from __future__ import annotations
from typing import Any

from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import (
    CriticDecision,
    CriticFinding,
    EvaluationGate,
    GraphQueryPlan,
    OrchestrationRequest,
    PayloadDraft,
    RetrievalChunk,
    RewrittenQuery,
    RoutingIntent,
    IntentClassification,
)



def test_orchestrator_happy_path_runs_all_steps_in_order() -> None:
    calls: list[str] = []

    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        calls.append("safety")
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")


    def rewrite(query: str) -> RewrittenQuery:
        calls.append("rewrite")
        return RewrittenQuery(normalized_text="what helps with sleep")

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        calls.append("route")
        return RoutingIntent(domain="sleep", risk_level="low")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        calls.append("specialist")
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"], limit=2)

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return [RetrievalChunk(source_id="PMID:23853635", content="Magnesium and sleep")]

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        calls.append("critic")
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        calls.append("payload")
        return PayloadDraft(response_text="Magnesium may support sleep.", citations=["PMID:23853635"])

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=0.94, threshold=threshold)

    def activate_observability() -> None:
        calls.append("observability")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(evaluation_threshold=0.8, enable_observability=True),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
        activate_observability=activate_observability,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="What helps with sleep?"))

    assert result.status == "ok"
    assert result.response_text is not None
    assert result.evaluation is not None
    assert result.evaluation.passed is True
    assert result.citations == ["PMID:23853635"]
    assert result.trace_enabled is True
    assert calls == [
        "observability",
        "safety",
        "rewrite",
        "route",
        "specialist",
        "retrieve",
        "critic",
        "payload",
        "evaluate",
    ]


def test_orchestrator_blocks_when_safety_denies_query() -> None:
    calls: list[str] = []

    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        calls.append("safety")
        return IntentClassification(is_clinical_diagnosis_request=True, primary_domain="general", requires_discovery=False, reasoning="test block")


    def rewrite(query: str) -> RewrittenQuery:
        calls.append("rewrite")
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        calls.append("route")
        return RoutingIntent(domain="general")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        calls.append("specialist")
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return []

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        calls.append("critic")
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        calls.append("payload")
        return PayloadDraft(response_text="should not run")

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="Diagnose my chest pain"))

    assert result.status == "blocked"
    assert result.safety is not None
    assert result.safety.allowed is False
    assert calls == ["safety"]


def test_orchestrator_returns_failed_when_retrieval_raises() -> None:
    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")

    def rewrite(query: str) -> RewrittenQuery:
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        return RoutingIntent(domain="general")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        raise RuntimeError("retrieval unavailable")

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        return PayloadDraft(response_text="not used")

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "retrieval unavailable" in (result.error or "")


def test_orchestrator_fails_closed_when_critic_exhausts_retries() -> None:
    calls: list[str] = []

    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        calls.append("safety")
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")


    def rewrite(query: str) -> RewrittenQuery:
        calls.append("rewrite")
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        calls.append("route")
        return RoutingIntent(domain="general")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        calls.append("specialist")
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return [RetrievalChunk(source_id="PMID:1", content="evidence")]

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        calls.append(f"critic:{retry_count}")
        return CriticDecision(
            passed=False,
            findings=[CriticFinding(code="ALLERGY_RECHECK", message="retry needed")],
            retryable=True,
        )

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        calls.append("payload")
        return PayloadDraft(response_text="should not run")

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False, max_critic_retries=1),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert result.error == "Critic rejected recommendations after bounded retries."
    assert result.retry_count == 2
    assert len(result.validation_errors) == 2
    assert calls == [
        "safety",
        "rewrite",
        "route",
        "specialist",
        "retrieve",
        "critic:0",
        "specialist",
        "retrieve",
        "critic:1",
    ]


def test_orchestrator_fails_when_evaluation_gate_rejects_response() -> None:
    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")


    def rewrite(query: str) -> RewrittenQuery:
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        return RoutingIntent(domain="general")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        return [RetrievalChunk(source_id="PMID:1", content="evidence")]

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        return PayloadDraft(response_text="draft", citations=["PMID:1"])

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=False, score=0.51, threshold=threshold, reason="faithfulness below threshold")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert result.response_text is None
    assert result.evaluation is not None
    assert result.evaluation.passed is False
    assert result.error == "faithfulness below threshold"


def test_orchestrator_fails_when_observability_activation_raises() -> None:
    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")


    def rewrite(query: str) -> RewrittenQuery:
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        return RoutingIntent(domain="general")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        return []

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        return PayloadDraft(response_text="draft")

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        return EvaluationGate(passed=True, score=1.0, threshold=threshold)

    def activate_observability() -> None:
        raise RuntimeError("phoenix unavailable")

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=True),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
        activate_observability=activate_observability,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "phoenix unavailable" in (result.error or "")


def test_orchestrator_retries_once_then_succeeds() -> None:
    calls: list[str] = []

    def safety_check(query: str, profile: dict[str, Any] = None) -> IntentClassification:
        calls.append("safety")
        return IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="test allow")


    def rewrite(query: str) -> RewrittenQuery:
        calls.append("rewrite")
        return RewrittenQuery(normalized_text=query)

    def route(rewritten: RewrittenQuery) -> RoutingIntent:
        calls.append("route")
        return RoutingIntent(domain="sleep", risk_level="high")

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ) -> GraphQueryPlan:
        calls.append("specialist")
        return GraphQueryPlan(operation="product_search", key_terms=["sleep"])

    def retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        calls.append("retrieve")
        return [RetrievalChunk(source_id="SKU:prod-1", content="Evidence")]

    def critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        calls.append(f"critic:{retry_count}")
        if retry_count == 0:
            return CriticDecision(
                passed=False,
                findings=[CriticFinding(code="ALLERGY_RECHECK", message="retry")],
                retryable=True,
            )
        return CriticDecision(passed=True, findings=[])

    def payload(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        calls.append("payload")
        return PayloadDraft(response_text="Grounded reply", citations=["SKU:prod-1"])

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float) -> EvaluationGate:
        calls.append("evaluate")
        return EvaluationGate(passed=True, score=0.9, threshold=threshold)

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False, max_critic_retries=1),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep with allergy concern"))

    assert result.status == "ok"
    assert result.retry_count == 1
    assert len(result.validation_errors) == 1
    assert result.response_text == "Grounded reply"
    assert result.citations == ["SKU:prod-1"]
    assert calls == [
        "safety",
        "rewrite",
        "route",
        "specialist",
        "retrieve",
        "critic:0",
        "specialist",
        "retrieve",
        "critic:1",
        "payload",
        "evaluate",
    ]


def test_orchestrator_fails_when_agent_output_violates_schema() -> None:
    def safety_check(query: str):
        return {"is_clinical_diagnosis_request": False, "primary_domain": "general", "requires_discovery": False, "reasoning": "test"}

    def rewrite(query: str):
        return {"normalized_text": "sleep"}

    def route(rewritten: RewrittenQuery):
        return {"domain": "sleep", "risk_level": "low"}

    def specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding],
    ):
        # Invalid schema: missing required `operation`.
        return {"key_terms": ["sleep"], "limit": 2, "read_only": True}

    def retrieve(plan: GraphQueryPlan):
        return [{"source_id": "SKU:1", "content": "evidence"}]

    def critic(query: str, routing: RoutingIntent, chunks: list[RetrievalChunk], retry_count: int):
        return {"passed": True, "findings": [], "retryable": False}

    def payload(query: str, chunks: list[RetrievalChunk]):
        return {"response_text": "ok", "citations": [], "uncertainty": False}

    def evaluate(query: str, draft: str, chunks: list[RetrievalChunk], threshold: float):
        return {"passed": True, "score": 1.0, "threshold": threshold, "reason": None}

    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(enable_observability=False),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=critic,
        generate_payload=payload,
        evaluate=evaluate,
    )

    result = orchestrator.run(OrchestrationRequest(user_query="sleep"))

    assert result.status == "failed"
    assert "operation" in (result.error or "")