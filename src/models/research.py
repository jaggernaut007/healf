from pydantic import BaseModel

class ResearchSummary(BaseModel):
    pmid: str
    study_type: str  # e.g., "Randomized Controlled Trial", "Meta-Analysis"
    sample_size: str  # e.g., "120 participants", "N=45"
    dosage_tested: str  # e.g., "5g daily", "400mg"
    key_finding: str  # One sentence summary of the primary outcome
