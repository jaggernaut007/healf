from typing import List
from pydantic import BaseModel

class EnrichedProduct(BaseModel):
    sku: str
    canonical_name: str  # e.g., "Magnesium Glycinate" to prevent graph duplicates
    active_ingredients: List[str]
    target_biomarkers: List[str]
    mechanisms_of_action: List[str]
    contraindications: List[str]  # Sourced from NIH RxTerms grounding
    usp: str = ""  # Unique Selling Points (e.g. "Third-party tested", "Vegan")
    usage_instructions: str = ""  # e.g. "Take 2 capsules daily with food"
