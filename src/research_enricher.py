import os
import json
from pathlib import Path
from typing import List
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from src.models.research import ResearchSummary

load_dotenv()

def enrich_research():
    client = instructor.patch(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    research_dir = Path("data/research")
    output_path = Path("data/research_summaries.json")
    
    summaries: List[ResearchSummary] = []
    
    # Load existing summaries if they exist to avoid re-processing
    existing_summaries = {}
    if output_path.exists():
        with open(output_path, "r") as f:
            data = json.load(f)
            existing_summaries = {s["pmid"]: s for s in data}

    for file_path in research_dir.glob("*.md"):
        pmid = file_path.stem
        if pmid in existing_summaries:
            print(f"Skipping {pmid} (already enriched)")
            summaries.append(ResearchSummary.model_validate(existing_summaries[pmid]))
            continue
            
        print(f"Enriching {pmid}...")
        content = file_path.read_text()
        
        try:
            summary = client.chat.completions.create(
                model="gpt-5.4-mini",
                response_model=ResearchSummary,
                messages=[
                    {"role": "system", "content": "Extract structured clinical data from the research summary markdown. Be precise and concise."},
                    {"role": "user", "content": f"Extract details for PMID {pmid} from this summary:\n\n{content}"}
                ]
            )
            summary.pmid = pmid # Ensure PMID matches filename
            summaries.append(summary)
        except Exception as e:
            print(f"Failed to enrich {pmid}: {e}")

    with open(output_path, "w") as f:
        json.dump([s.model_dump() for s in summaries], f, indent=2)
    
    print(f"Saved {len(summaries)} research summaries to {output_path}")

if __name__ == "__main__":
    enrich_research()
