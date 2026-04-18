from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    user_query: str
    user_id: str | None = None


class SafetyDecision(BaseModel):
    allowed: bool
    reason: str | None = None


class RetrievalChunk(BaseModel):
    source_id: str
    content: str


class EvaluationGate(BaseModel):
    passed: bool
    score: float
    threshold: float
    reason: str | None = None


class OrchestrationResult(BaseModel):
    status: str
    response_text: str | None = None
    safety: SafetyDecision | None = None
    retrieved_chunks: list[RetrievalChunk] = Field(default_factory=list)
    evaluation: EvaluationGate | None = None
    error: str | None = None
    trace_enabled: bool = False
