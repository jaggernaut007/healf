from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    user_query: str
    user_id: str | None = None
    chat_history: list[str] = Field(default_factory=list)
    user_profile: dict[str, str] = Field(default_factory=dict)


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
    domain: str
    risk_level: str = "low"
    route_reason: str | None = None


class GraphQueryPlan(BaseModel):
    operation: str
    key_terms: list[str] = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict)
    limit: int = 3
    read_only: bool = True


class CriticFinding(BaseModel):
    code: str
    message: str
    severity: str = "high"


class CriticDecision(BaseModel):
    passed: bool
    findings: list[CriticFinding] = Field(default_factory=list)
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
    trace_enabled: bool = False
