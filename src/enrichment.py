import json
import logging
import os
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from src.clients.enrichment_client import EnrichmentClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("product-enricher")

def load_input_urls(filepath: str) -> list:
    """Load raw URLs from input JSON."""
    if not os.path.exists(filepath):
        logger.error(f"Input file not found: {filepath}")
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_output_products(filepath: str, products: list):
    """Save enriched products to JSON."""
    # Serialize Pydantic objects fully 
    serialized = [prod.model_dump() for prod in products]
    with open(filepath, 'w') as f:
        json.dump(serialized, f, indent=2)
    logger.info(f"Saved {len(products)} enriched products to {filepath}")

def run_enrichment_pipeline():
    """Component 1 Orchestrator: Scrapes Web -> NIH Facts -> Model Extract -> Save."""
    input_file = "data/raw_product_urls.json"
    output_file = "data/enriched_products.json"
    
    urls = load_input_urls(input_file)
    if not urls:
        logger.error("No input URLs to process. Exiting.")
        return

    # Fail fast when credentials are missing so runs cannot silently degrade.
    fc_api_key = os.getenv("FIRECRAWL_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not fc_api_key or not openai_key:
        missing = []
        if not fc_api_key:
            missing.append("FIRECRAWL_API_KEY")
        if not openai_key:
            missing.append("OPENAI_API_KEY")
        raise RuntimeError(f"Missing required API keys: {', '.join(missing)}")
    
    client = EnrichmentClient(api_key=fc_api_key)
    
    # Let instructor wrap openai
    oai_client = OpenAI(api_key=openai_key)
    patch_client = instructor.from_openai(oai_client)

    enriched_results = []
    failed_urls = []
    for url in urls:
        logger.info(f"Processing URL: {url}")
        
        try:
            # 1. Fetch raw markdown
            logger.info("   -> Scraping markup via Firecrawl...")
            markdown = client.fetch_product_page(url)
            logger.info(f"   -> Markdown fetched. Length: {len(markdown)}. Preview: {markdown[:50].strip()}...")

            # 2. Map and Extract Schema (pass URL for deterministic SKU extraction)
            logger.info("   -> Extracting structured data via LLM...")
            product = client.extract_product_data(markdown, url=url, instructor_client=patch_client)

            # 3. Grounding against NIH RxTerms 
            logger.info(f"   -> Grounding active ingredients for {product.canonical_name}...")
            # For each active ingredient, verify safety gaps
            for ingredient in product.active_ingredients:
                nih_data = client.fetch_nih_dsld_data(ingredient)
                # Overwrite contraindications based on NIH authoritative results
                if "warnings" in nih_data and nih_data["warnings"]:
                    # Ensure no duplicates
                    for warning in nih_data["warnings"]:
                        if warning not in product.contraindications:
                            product.contraindications.append(warning)

            enriched_results.append(product)
            logger.info(f"   -> EnrichedProduct ready for {product.canonical_name}")

        except Exception as e:
            logger.error(f"Failed processing {url} - {str(e)}")
            failed_urls.append(url)

    if failed_urls:
        raise RuntimeError(
            f"Enrichment failed for {len(failed_urls)} URL(s): {', '.join(failed_urls)}"
        )

    # 4. Save Final State
    if enriched_results:
        save_output_products(output_file, enriched_results)
    else:
        raise RuntimeError("No products were successfully extracted.")

if __name__ == "__main__":
    run_enrichment_pipeline()