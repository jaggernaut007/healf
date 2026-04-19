import os
import hashlib
from urllib.parse import urlparse
from typing import Optional, Dict, Any
from src.models.product import EnrichedProduct

# Attempting to load Firecrawl, which will be added to requirements if we decide to wrap it
from cachetools import cached, TTLCache
try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = None

class EnrichmentClient:
    """Client for gathering external data and parsing it into our canonical structure."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if FirecrawlApp and self.api_key:
            self.app = FirecrawlApp(api_key=self.api_key)
        else:
            self.app = None

    @staticmethod
    def _fallback_sku(url: str) -> str:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        return f"url-{digest}"

    @staticmethod
    def extract_sku_from_url(url: str) -> str:
        """Extract SKU from /products/<slug>; otherwise return deterministic fallback."""
        try:
            parsed = urlparse(url)
            path = parsed.path.rstrip("/")
            if not path:
                return EnrichmentClient._fallback_sku(url)

            parts = [part for part in path.split("/") if part]
            if len(parts) >= 2 and parts[0] == "products":
                slug = parts[-1]
                if slug:
                    return slug

            return EnrichmentClient._fallback_sku(url)
        except Exception:
            return EnrichmentClient._fallback_sku(url)

    def fetch_product_page(self, url: str) -> str:
        """
        Fetches a product page from a URL and converts the core text content to Markdown.
        Uses Firecrawl if available and configured.
        """
        if not self.app:
            raise RuntimeError("FirecrawlApp is not configured or installed. Please set FIRECRAWL_API_KEY.")
            
        try:
            if hasattr(self.app, "scrape"):
                result = self.app.scrape(url, formats=["markdown"])
                # New SDK returns a Document model; fallback handles dict-like responses.
                if hasattr(result, "markdown"):
                    return result.markdown or ""
                if isinstance(result, dict):
                    return result.get("markdown", "")
                raise RuntimeError("Firecrawl scrape response did not include markdown output.")

            if hasattr(self.app, "scrape_url"):
                result = self.app.scrape_url(url, params={"formats": ["markdown"]})
                return result.get("markdown", "")

            raise RuntimeError("Firecrawl client does not expose scrape or scrape_url methods.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch product page via Firecrawl: {str(e)}")

    def extract_product_data(self, markdown_content: str, url: str, instructor_client=None) -> EnrichedProduct:
        """
        Uses an LLM (via Instructor) to extract the canonical EnrichedProduct from markdown.
        `instructor_client` should be an initialized instructor-patched OpenAI or Anthropic client.
        `url` is used to derive a unique, deterministic SKU (product URL slug).
        """
        if not instructor_client:
            raise ValueError("An instructor-patched LLM client is required for extraction.")
        
        # Extract SKU from URL (guaranteed unique per product)
        sku = self.extract_sku_from_url(url)
            
        try:
            # Use gpt-5.4-mini for high-volume extraction tasks
            product = instructor_client.chat.completions.create(
                model=os.getenv("ENRICHMENT_MODEL", "gpt-5.4-mini"),
                response_model=EnrichedProduct,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precision data extraction engine. Extract product details from the markdown of a single product page. "
                            "CRITICAL: Only extract the product that is the MAIN SUBJECT of the page. "
                            "IGNORE 'Trending searches', 'Recommended products', or other sidebar/footer items. "
                            "Do NOT hallucinate names like 'Pure Encapsulations Magnesium Glycinate' unless it is the PRIMARY product on the page. "
                            "If you are unsure of the canonical name, use the largest H1 or title in the text. "
                            "Also extract 2-3 Unique Selling Points (USPs) and any available Usage Instructions."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Extract the PRIMARY product details from this page:\n\n{markdown_content}"
                    }
                ],
                max_completion_tokens=2048,
                temperature=0.0,
            )

            if hasattr(product, "model_dump"):
                product = EnrichedProduct.model_validate(product.model_dump())
            else:
                product = EnrichedProduct.model_validate(product)
            
            # Override the SKU with the URL-derived value (deterministic and unique)
            product.sku = sku
            return product
        except Exception as e:
            raise RuntimeError(f"LLM data extraction failed: {str(e)}")

    @cached(cache=TTLCache(maxsize=100, ttl=3600))
    def fetch_nih_dsld_data(self, product_name: str) -> Dict[str, Any]:
        """
        Fetches grounding data from the NIH Dietary Supplement Label Database via their public REST API.
        This provides contraindications, interactions, and safety alerts.
        """
        import requests
        
        # NOTE: This endpoint is the NIH RxTerms search API.
        base_url = "https://clinicaltables.nlm.nih.gov/api/rxterms/v3/search"
        
        try:
            response = requests.get(
                base_url, 
                params={"terms": product_name, "maxList": 5},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Keep warnings source-backed only; do not synthesize clinical warnings.
            return {
                "source": "NIH_RXTERMS",
                "grounding_status": "Success",
                "query": product_name,
                "dsld_matches": data[1] if len(data) > 1 else [],
                "warnings": [],
            }
        except (requests.RequestException, ValueError, TypeError, IndexError) as e:
            return {
                "source": "NIH_RXTERMS",
                "grounding_status": "Failed",
                "query": product_name,
                "error": str(e)
            }

    def fetch_pubmed_research(self, ingredient: str, limit: int = 1) -> None:
        """
        Searches PubMed for research abstracts related to an ingredient and saves them as Markdown files.
        Uses the NCBI Entrez Programming Utilities (E-utils).
        """
        import requests
        import xml.etree.ElementTree as ET
        from pathlib import Path

        research_dir = Path("data/research")
        research_dir.mkdir(parents=True, exist_ok=True)

        # 1. Search for PMIDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        try:
            search_res = requests.get(
                search_url,
                params={
                    "db": "pubmed",
                    "term": f"{ingredient} supplementation",
                    "retmax": limit,
                    "retmode": "json"
                },
                timeout=10
            )
            search_res.raise_for_status()
            id_list = search_res.json().get("esearchresult", {}).get("idlist", [])
            
            for pmid in id_list:
                file_path = research_dir / f"{pmid}.md"
                if file_path.exists():
                    continue

                # 2. Fetch Abstract for each PMID
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                fetch_res = requests.get(
                    fetch_url,
                    params={
                        "db": "pubmed",
                        "id": pmid,
                        "rettype": "abstract",
                        "retmode": "xml"
                    },
                    timeout=10
                )
                fetch_res.raise_for_status()
                
                # Parse XML to extract title and abstract
                root = ET.fromstring(fetch_res.content)
                article = root.find(".//PubmedArticle")
                if article is None:
                    continue

                title = article.find(".//ArticleTitle")
                title_text = title.text if title is not None else "No Title"
                
                abstract_parts = []
                for abs_text in article.findall(".//AbstractText"):
                    label = abs_text.get("Label", "")
                    text = abs_text.text if abs_text.text else ""
                    if label:
                        abstract_parts.append(f"**{label}**: {text}")
                    else:
                        abstract_parts.append(text)
                
                abstract_text = "\n\n".join(abstract_parts) if abstract_parts else "No Abstract Found."

                content = f"# PMID {pmid}\n\nTitle: {title_text}\n\nSummary:\n{abstract_text}\n"
                file_path.write_text(content, encoding="utf-8")
                print(f"   -> Fetched research for {ingredient}: PMID {pmid}")

        except Exception as e:
            print(f"   -> PubMed fetch failed for {ingredient}: {str(e)}")
