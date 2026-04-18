from __future__ import annotations

from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import (
    EvaluationGate,
    OrchestrationRequest,
    RetrievalChunk,
    SafetyDecision,
)


def test_orchestrator_happy_path_runs_all_steps_in_order() -> None:
    calls: list[str] = []

    def safety_check(query: str) -> SafetyDecision:
        calls.append("safety")
        return SafetyDecision(allowed=True)

    def retrieve(query: str) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return [RetrievalChunk(source_id="PMID:23853635", content="Magnesium and sleep")]

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        calls.append("generate")
        return "Magnesium glycinate may support sleep quality."

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=0.94, threshold=threshold)

    def activate_observability() -> None:
        calls.append("observability")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(evaluation_threshold=0.8, enable_observability=True),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
        activate_observability=activate_observability,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="What helps with sleep?"))

    assert result.status == "ok"
    assert result.response_text is not None
    assert result.evaluation is not None
    assert result.evaluation.passed is True
    assert result.trace_enabled is True
    assert calls == ["observability", "safety", "retrieve", "generate", "evaluate"]


def test_orchestrator_blocks_when_safety_denies_query() -> None:
    calls: list[str] = []

    def safety_check(query: str) -> SafetyDecision:
        calls.append("safety")
        return SafetyDecision(allowed=False, reason="medical diagnosis request")

    def retrieve(query: str) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return []

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        calls.append("generate")
        return "should not run"

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="Diagnose my chest pain"))

    assert result.status == "blocked"
    assert result.safety is not None
    assert result.safety.allowed is False
    assert calls == ["safety"]


def test_orchestrator_returns_failed_when_retrieval_raises() -> None:
    def safety_check(query: str) -> SafetyDecision:
        return SafetyDecision(allowed=True)

    def retrieve(query: str) -> list[RetrievalChunk]:
        raise RuntimeError("retrieval unavailable")

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        return "not used"

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "retrieval unavailable" in (result.error or "")


def test_orchestrator_returns_failed_when_generation_raises() -> None:
    calls: list[str] = []

    def safety_check(query: str) -> SafetyDecision:
        calls.append("safety")
        return SafetyDecision(allowed=True)

    def retrieve(query: str) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return [RetrievalChunk(source_id="PMID:1", content="evidence")]

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        calls.append("generate")
        raise RuntimeError("generation failure")

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "generation failure" in (result.error or "")
    assert calls == ["safety", "retrieve", "generate"]


def test_orchestrator_fails_when_evaluation_gate_rejects_response() -> None:
    def safety_check(query: str) -> SafetyDecision:
        return SafetyDecision(allowed=True)

    def retrieve(query: str) -> list[RetrievalChunk]:
        return [RetrievalChunk(source_id="PMID:1", content="evidence")]

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        return "draft"

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=False, score=0.51, threshold=threshold, reason="faithfulness below threshold")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert result.response_text is None
    assert result.evaluation is not None
    assert result.evaluation.passed is False
    assert result.error == "faithfulness below threshold"


def test_orchestrator_fails_when_observability_activation_raises() -> None:
    def safety_check(query: str) -> SafetyDecision:
        return SafetyDecision(allowed=True)

    def retrieve(query: str) -> list[RetrievalChunk]:
        return []

    def generate(query: str, chunks: list[RetrievalChunk]) -> str:
        return "draft"

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    def activate_observability() -> None:
        raise RuntimeError("phoenix unavailable")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=True),
        safety_check=safety_check,
        retrieve=retrieve,
        generate=generate,
        evaluate=evaluate,
        activate_observability=activate_observability,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "phoenix unavailable" in (result.error or "")
