import logging
from src.enrichment import run_enrichment_pipeline
from src.research_enricher import enrich_research
from src.rule_generator import generate_missing_rules
from src.graph_builder import run_graph_build

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("full-pipeline")

def run_full_pipeline():
    """
    Executes the entire Healf Intelligence Pipeline:
    1. Product Enrichment (Scraping + NIH Grounding + PubMed Research Fetching)
    2. Research Enrichment (Structured Extraction from PubMed Abstracts)
    3. Autonomous Rule Generation (Grounding missing ingredients using research)
    4. Knowledge Graph Build (Syncing to Neo4j)
    """
    logger.info("=== Starting Healf Full Intelligence Pipeline ===")

    try:
        # Step 1: Product Enrichment
        logger.info("Step 1/4: Product Enrichment & Research Fetching...")
        run_enrichment_pipeline()
        logger.info("Step 1/4 Complete.")

        # Step 2: Research Enrichment
        logger.info("Step 2/4: Research Enrichment (Structured Extraction)...")
        enrich_research()
        logger.info("Step 2/4 Complete.")

        # Step 3: Autonomous Rule Generation
        logger.info("Step 3/4: Generating Missing Graph Inference Rules...")
        generate_missing_rules()
        logger.info("Step 3/4 Complete.")

        # Step 4: Knowledge Graph Build
        logger.info("Step 4/4: Syncing to Knowledge Graph (Neo4j)...")
        run_graph_build()
        logger.info("Step 4/4 Complete.")

        logger.info("=== Pipeline Execution Successful ===")
        print("\nPipeline finished! You can now start the chat REPL with: uv run healf chat")

    except Exception as e:
        logger.error(f"Pipeline failed at some step: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_full_pipeline()
