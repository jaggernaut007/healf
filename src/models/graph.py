from __future__ import annotations

from pydantic import BaseModel, Field


class GraphTriple(BaseModel):
    product_sku: str
    product_name: str
    ingredient_name: str
    mechanism_name: str
    symptom_name: str
    source_pmid: str | None = None


class GraphInferenceRule(BaseModel):
    ingredient_terms: list[str]
    mechanism_name: str
    symptom_name: str
    source_pmid: str | None = None
    corpus_terms: list[str] = Field(default_factory=list)


class GraphBuildResult(BaseModel):
    products_loaded: int
    research_documents_loaded: int
    triples_written: int


class GraphPreflightResult(BaseModel):
    products_loaded: int
    research_documents_loaded: int
    rules_loaded: int
    triples_inferred: int
    missing_rule_pmids: list[str]
    unmatched_ingredients: list[str]
    triples_preview: list[GraphTriple]
