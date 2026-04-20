from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    user_query: str
    user_id: str | None = None
    chat_history: list[dict[str, str]] = Field(default_factory=list)
    user_profile: dict[str, Any] = Field(default_factory=dict)


class IntentClassification(BaseModel):
    is_clinical_diagnosis_request: bool = Field(description="True if the query describes symptoms, asks for a diagnosis, or seeks medical treatment.")
    primary_domain: str = Field(description="The primary health domain: sleep, stress, gut, energy, or general.")
    requires_discovery: bool = Field(description="True if the query is ambiguous or broad and requires a discovery question.")
    reasoning: str = Field(description="Explanation for the classification and safety decision.")



class SafetyDecision(BaseModel):
    allowed: bool
    reason: str | None = None
    reason_code: str = "UNSPECIFIED"
    risk_level: str = "unknown"
    source: str = "policy"


class RewrittenQuery(BaseModel):
    normalized_text: str
    preserved_terms: list[str] = Field(default_factory=list)


class RoutingIntent(BaseModel):
    domain: str = "general"
    risk_level: str = "low"
    route_reason: str | None = None
    requires_clarification: bool = False


class GraphQueryPlan(BaseModel):
    operation: str
    key_terms: list[str] = Field(default_factory=list)
    domain: str = "general"
    risk_level: str = "low"
    retry_codes: str = ""
    limit: int = 3
    read_only: bool = True


class CriticFinding(BaseModel):
    code: str
    message: str
    severity: str = "high"


class CriticDecision(BaseModel):
    passed: bool
    findings: list[CriticFinding]
    retryable: bool = False


class RetrievalChunk(BaseModel):
    source_id: str
    content: str


class PayloadDraft(BaseModel):
    response_text: str
    citations: list[str] = Field(default_factory=list)
    uncertainty: bool = False


class EvaluationGate(BaseModel):
    passed: bool
    score: float
    threshold: float
    reason: str | None = None


class DiscoveryDecision(BaseModel):
    requires_clarification: bool
    clarification_question: str | None = None
    options: list[str] = Field(default_factory=list, description="A list of specific options for the user to choose from (e.g. ['A: Physical Energy', 'B: Mental Focus']).")
    reasoning: str | None = None
    resolved_query: RewrittenQuery | None = None


class OrchestrationResult(BaseModel):
    status: str
    response_text: str | None = None
    safety: SafetyDecision | None = None
    rewritten_query: RewrittenQuery | None = None
    routing_intent: RoutingIntent | None = None
    retrieved_chunks: list[RetrievalChunk] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    uncertainty: bool = False
    evaluation: EvaluationGate | None = None
    validation_errors: list[CriticFinding] = Field(default_factory=list)
    retry_count: int = 0
    error: str | None = None
    requires_clarification: bool = False
    clarification_question: str | None = None
    options: list[str] = Field(default_factory=list)
    intent_classification: IntentClassification | None = None
    trace_enabled: bool = False

