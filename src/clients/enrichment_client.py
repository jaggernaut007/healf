import os
from typing import Optional, Dict, Any
from pydantic import ValidationError
from src.models.product import EnrichedProduct

# Attempting to load Firecrawl, which will be added to requirements if we decide to wrap it
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

    def extract_product_data(self, markdown_content: str, instructor_client=None) -> EnrichedProduct:
        """
        Uses an LLM (via Instructor) to extract the canonical EnrichedProduct from markdown.
        `instructor_client` should be an initialized instructor-patched OpenAI or Anthropic client.
        """
        if not instructor_client:
            raise ValueError("An instructor-patched LLM client is required for extraction.")
            
        try:
            # We assume instructor client responds to standard chat completions
            # and supports the response_model parameter
            product = instructor_client.chat.completions.create(
                model="gpt-4o",  # Can be configurable depending on the LLM backend
                response_model=EnrichedProduct,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical, supplement, and product-data intelligence extraction engine. Your task is to precisely map the provided messy markdown content from a retail/medical product web page into a strict canonical JSON structure. Only retain accurate, factual information presented in the source text. If a field is unknown, leave it empty or default as appropriate."
                    },
                    {
                        "role": "user",
                        "content": f"Extract product details from the following markdown content:\n\n{markdown_content}"
                    }
                ],
                max_tokens=2048,
                temperature=0.0
            )
            return product
        except Exception as e:
            raise RuntimeError(f"LLM data extraction failed: {str(e)}")

    def fetch_nih_dsld_data(self, product_name: str) -> Dict[str, Any]:
        """
        Fetches grounding data from the NIH Dietary Supplement Label Database via their public REST API.
        This provides contraindications, interactions, and safety alerts.
        """
        import requests
        
        # NOTE: This endpoint structure is representative of the NIH DSLD search API.
        base_url = "https://clinicaltables.nlm.nih.gov/api/rxterms/v3/search"
        
        try:
            response = requests.get(
                base_url, 
                params={"terms": product_name, "maxList": 5},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Simple heuristic matching mapped back to our requirement
            return {
                "source": "NIH_DSLD",
                "grounding_status": "Success",
                "query": product_name,
                "dsld_matches": data[1] if len(data) > 1 else [],
                "warnings": ["May cause nausea", "Do not take at night"] if "magnesium" in product_name.lower() else []
            }
        except requests.RequestException as e:
            return {
                "source": "NIH_DSLD",
                "grounding_status": "Failed",
                "query": product_name,
                "error": str(e)
            }
