import os
import json
import logging
from pathlib import Path
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from src.graph_builder import GraphBuilder, GraphBuilderConfig
from src.models.graph import GraphInferenceRule

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rule-generator")

def generate_missing_rules():
    """
    Autonomous Rule Generation:
    1. Identifies ingredients in the product catalog that have no matching inference rules.
    2. Uses structured PubMed research summaries to ground new rules.
    3. Synthesizes GraphInferenceRule objects using an LLM.
    """
    logger.info("Checking for missing graph inference rules...")
    
    # Initialize GraphBuilder to use its preflight logic for finding unmatched ingredients
    builder = GraphBuilder(config=GraphBuilderConfig())
    try:
        preflight = builder.preflight()
    except Exception as e:
        logger.error(f"Preflight failed, cannot determine missing rules: {e}")
        return

    unmatched_ingredients = preflight.unmatched_ingredients
    
    if not unmatched_ingredients:
        logger.info("No missing rules detected. All ingredients are mapped.")
        return

    logger.info(f"Found {len(unmatched_ingredients)} unmatched ingredients: {', '.join(unmatched_ingredients)}")

    # Load existing rules to append to them
    rules_path = Path("data/research/graph_inference_rules.json")
    if not rules_path.exists():
        existing_rules = []
    else:
        with open(rules_path, "r") as f:
            existing_rules = json.load(f)

    # Load research summaries for grounding
    summaries_path = Path("data/research_summaries.json")
    if not summaries_path.exists():
        logger.warning("No research summaries found. Grounding will be limited to parametric memory.")
        summaries = []
    else:
        with open(summaries_path, "r") as f:
            summaries = json.load(f)

    # Setup Instructor for structured extraction
    client = instructor.patch(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    
    new_rules_count = 0
    for ingredient in unmatched_ingredients:
        logger.info(f"Generating grounded rule for: {ingredient}...")
        
        # Filter summaries relevant to this ingredient to keep context window small
        relevant_summaries = [
            s for s in summaries 
            if ingredient.lower() in str(s).lower()
        ]
        
        try:
            # The prompt strictly enforces grounding in the provided research data
            rule = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=GraphInferenceRule,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Clinical Knowledge Graph Engineer. Your task is to generate a deterministic "
                            "GraphInferenceRule for a health ingredient based ON THE PROVIDED RESEARCH SUMMARIES. "
                            "\n\nGUIDELINES:"
                            "\n1. ingredient_terms: List variations of the name (e.g., ['magnesium', 'magnesium glycinate'])."
                            "\n2. mechanism_name: The biological pathway involved (e.g., 'GABA signaling support')."
                            "\n3. symptom_name: The WELLNESS benefit (e.g., 'Sleep', 'Focus', 'Energy'). NEVER use clinical diseases."
                            "\n4. source_pmid: Use the PMID from the provided research summary that supports this claim."
                            "\n5. corpus_terms: 3-5 keywords found in the research that link the ingredient to the symptom."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Target Ingredient: {ingredient}\n\n"
                            f"Available Grounding Research:\n{json.dumps(relevant_summaries[:3], indent=2)}\n\n"
                            "Generate a rule that safely connects this ingredient to a health outcome."
                        )
                    }
                ]
            )
            
            # Check for duplicates before appending
            if not any(set(rule.ingredient_terms) & set(r.get("ingredient_terms", [])) for r in existing_rules):
                existing_rules.append(rule.model_dump())
                new_rules_count += 1
                logger.info(f"   -> Successfully generated rule: {rule.ingredient_terms} -> {rule.symptom_name}")
            else:
                logger.info(f"   -> Rule already exists for {ingredient}, skipping.")

        except Exception as e:
            logger.error(f"Failed to generate rule for {ingredient}: {e}")

    # Save the updated rules file
    if new_rules_count > 0:
        with open(rules_path, "w") as f:
            json.dump(existing_rules, f, indent=2)
        logger.info(f"Saved {new_rules_count} new rules to {rules_path}")
    else:
        logger.info("No new rules were added.")

if __name__ == "__main__":
    generate_missing_rules()
