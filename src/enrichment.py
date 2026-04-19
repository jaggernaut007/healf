import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def process_single_url(url: str, client: EnrichmentClient, patch_client) -> tuple:
    """Helper to process a single URL: Scrape + Initial LLM Extraction."""
    logger.info(f"Processing URL: {url}")
    try:
        # 1. Fetch raw markdown
        logger.info(f"   [{url}] Scraping markup via Firecrawl...")
        markdown = client.fetch_product_page(url)
        
        # 2. Map and Extract Schema
        logger.info(f"   [{url}] Extracting structured data via LLM...")
        product = client.extract_product_data(markdown, url=url, instructor_client=patch_client)
        
        return product, None
    except Exception as e:
        logger.error(f"Failed processing {url} - {str(e)}")
        return None, url

def run_enrichment_pipeline():
    """
    Optimized Component 1 Orchestrator:
    1. Parallel URL Scraping & Extraction
    2. De-duplicated Ingredient Grounding (NIH + PubMed)
    3. Save results
    """
    input_file = "data/raw_product_urls.json"
    output_file = "data/enriched_products.json"
    
    urls = load_input_urls(input_file)
    if not urls:
        logger.error("No input URLs to process. Exiting.")
        return

    # API Key check
    fc_api_key = os.getenv("FIRECRAWL_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not fc_api_key or not openai_key:
        raise RuntimeError("Missing required API keys: FIRECRAWL_API_KEY or OPENAI_API_KEY")
    
    client = EnrichmentClient(api_key=fc_api_key)
    oai_client = OpenAI(api_key=openai_key)
    patch_client = instructor.from_openai(oai_client)

    enriched_results = []
    failed_urls = []

    # --- Phase 1: Parallel Extraction ---
    logger.info(f"Starting parallel extraction for {len(urls)} URLs...")
    with ThreadPoolExecutor(max_workers=int(os.getenv("MAX_WORKERS", 5))) as executor:
        futures = {executor.submit(process_single_url, url, client, patch_client): url for url in urls}
        for future in as_completed(futures):
            product, error_url = future.result()
            if product:
                enriched_results.append(product)
            if error_url:
                failed_urls.append(error_url)

    if not enriched_results:
        logger.error("No products were successfully extracted.")
        if failed_urls:
            raise RuntimeError(f"All extractions failed: {failed_urls}")
        return

    # --- Phase 2: De-duplicated Grounding ---
    unique_ingredients = {ing for prod in enriched_results for ing in prod.active_ingredients}
    logger.info(f"Starting grounding for {len(unique_ingredients)} unique ingredients...")
    
    ingredient_warnings = {}
    
    # Ground each unique ingredient once
    for ingredient in unique_ingredients:
        logger.info(f"   -> Grounding: {ingredient}")
        
        # 2a. NIH Grounding for warnings
        nih_data = client.fetch_nih_dsld_data(ingredient)
        if "warnings" in nih_data and nih_data["warnings"]:
            ingredient_warnings[ingredient] = nih_data["warnings"]
        
        # 2b. PubMed Research Fetching (saves to data/research/)
        client.fetch_pubmed_research(ingredient, limit=1)

    # --- Phase 3: Map Grounding back to Products ---
    for product in enriched_results:
        for ingredient in product.active_ingredients:
            if ingredient in ingredient_warnings:
                for warning in ingredient_warnings[ingredient]:
                    if warning not in product.contraindications:
                        product.contraindications.append(warning)
        logger.info(f"   -> EnrichedProduct finalized: {product.canonical_name}")

    if failed_urls:
        logger.warning(f"Enrichment partial success. Failed URLs: {', '.join(failed_urls)}")

    # --- Phase 4: Save Final State ---
    save_output_products(output_file, enriched_results)

if __name__ == "__main__":
    run_enrichment_pipeline()
