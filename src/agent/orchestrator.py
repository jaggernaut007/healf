from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from src.models.orchestration import (
    CriticDecision,
    CriticFinding,
    EvaluationGate,
    GraphQueryPlan,
    OrchestrationRequest,
    OrchestrationResult,
    PayloadDraft,
    RetrievalChunk,
    RewrittenQuery,
    RoutingIntent,
    SafetyDecision,
)


class OrchestrationConfig(BaseModel):
    evaluation_threshold: float = 0.8
    enable_observability: bool = True
    max_critic_retries: int = 1


class OrchestrationState(TypedDict, total=False):
    request: OrchestrationRequest
    safety: SafetyDecision
    rewritten_query: RewrittenQuery
    routing_intent: RoutingIntent
    graph_query_plan: GraphQueryPlan
    retrieved_chunks: list[RetrievalChunk]
    critic_decision: CriticDecision
    payload: PayloadDraft
    evaluation: EvaluationGate
    retry_count: int
    validation_errors: list[CriticFinding]
    result: OrchestrationResult
    trace_enabled: bool


class AgentOrchestrator:
    def __init__(
        self,
        config: OrchestrationConfig,
        safety_check: Callable[[str], SafetyDecision],
        rewrite: Callable[[str], RewrittenQuery],
        route: Callable[[RewrittenQuery], RoutingIntent],
        specialize: Callable[..., GraphQueryPlan],
        retrieve: Callable[[GraphQueryPlan], list[RetrievalChunk]],
        critic: Callable[[str, RoutingIntent, list[RetrievalChunk], int], CriticDecision],
        generate_payload: Callable[[str, list[RetrievalChunk]], PayloadDraft],
        evaluate: Callable[[str, str, list[RetrievalChunk], float], EvaluationGate],
        activate_observability: Callable[[], None] | None = None,
    ) -> None:
        self.config = config
        self.safety_check = safety_check
        self.rewrite = rewrite
        self.route = route
        self.specialize = specialize
        self.retrieve = retrieve
        self.critic = critic
        self.generate_payload = generate_payload
        self.evaluate = evaluate
        self.activate_observability = activate_observability
        self._graph = self.build_graph()

    @classmethod
    def build_default(
        cls,
        config: OrchestrationConfig | None = None,
        guardrails_config_path: Path = Path("config/wellness_guard.co"),
        products_path: Path = Path("data/enriched_products.json"),
    ) -> "AgentOrchestrator":
        from src.agent.adapters import (
            build_default_critic,
            build_default_evaluator,
            build_default_intake_router,
            build_default_observability_activator,
            build_default_payload_generator,
            build_default_prompt_rewriter,
            build_default_retriever,
            build_default_safety_check,
            build_default_specialist,
        )

        return cls(
            config=config or OrchestrationConfig(),
            safety_check=build_default_safety_check(guardrails_config_path=guardrails_config_path),
            rewrite=build_default_prompt_rewriter(),
            route=build_default_intake_router(),
            specialize=build_default_specialist(),
            retrieve=build_default_retriever(products_path=products_path),
            critic=build_default_critic(),
            generate_payload=build_default_payload_generator(),
            evaluate=build_default_evaluator(),
            activate_observability=build_default_observability_activator(),
        )

    def build_graph(self) -> Any:
        graph = StateGraph(OrchestrationState)
        graph.add_node("safety", self._safety_node)
        graph.add_node("blocked", self._blocked_node)
        graph.add_node("rewrite", self._rewrite_node)
        graph.add_node("intake_router", self._router_node)
        graph.add_node("specialist", self._specialist_node)
        graph.add_node("retrieve", self._retrieve_node)
        graph.add_node("critic", self._critic_node)
        graph.add_node("payload", self._payload_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("finalize_success", self._finalize_success_node)
        graph.add_node("finalize_failed_gate", self._finalize_failed_gate_node)
        graph.add_node("finalize_fail_closed", self._finalize_fail_closed_node)

        graph.add_edge(START, "safety")
        graph.add_conditional_edges(
            "safety",
            self._route_after_safety,
            {"blocked": "blocked", "rewrite": "rewrite"},
        )
        graph.add_edge("blocked", END)
        graph.add_edge("rewrite", "intake_router")
        graph.add_edge("intake_router", "specialist")
        graph.add_edge("specialist", "retrieve")
        graph.add_edge("retrieve", "critic")
        graph.add_conditional_edges(
            "critic",
            self._route_after_critic,
            {
                "payload": "payload",
                "specialist": "specialist",
                "finalize_fail_closed": "finalize_fail_closed",
            },
        )
        graph.add_edge("payload", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            self._route_after_evaluation,
            {"finalize_success": "finalize_success", "finalize_failed_gate": "finalize_failed_gate"},
        )
        graph.add_edge("finalize_success", END)
        graph.add_edge("finalize_failed_gate", END)
        graph.add_edge("finalize_fail_closed", END)

        return graph.compile()

    def run(self, request: OrchestrationRequest) -> OrchestrationResult:
        trace_enabled = False
        try:
            trace_enabled = self._activate_observability_if_enabled()
            final_state = self._graph.invoke(
                {
                    "request": request,
                    "trace_enabled": trace_enabled,
                    "retry_count": 0,
                    "validation_errors": [],
                }
            )
        except Exception as exc:
            return OrchestrationResult(
                status="failed",
                error=str(exc),
                trace_enabled=trace_enabled,
            )

        result = final_state.get("result")
        if result is None:
            return OrchestrationResult(
                status="failed",
                error="Orchestration finished without a result.",
                trace_enabled=trace_enabled,
            )
        return result

    def _activate_observability_if_enabled(self) -> bool:
        if not self.config.enable_observability or self.activate_observability is None:
            return False
        self.activate_observability()
        return True

    def _safety_node(self, state: OrchestrationState) -> OrchestrationState:
        decision = SafetyDecision.model_validate(self.safety_check(state["request"].user_query))
        return {"safety": decision}

    def _rewrite_node(self, state: OrchestrationState) -> OrchestrationState:
        rewritten = RewrittenQuery.model_validate(self.rewrite(state["request"].user_query))
        return {"rewritten_query": rewritten}

    def _router_node(self, state: OrchestrationState) -> OrchestrationState:
        rewritten = state.get("rewritten_query") or RewrittenQuery(
            normalized_text=state["request"].user_query.lower()
        )
        intent = RoutingIntent.model_validate(self.route(rewritten))
        return {"routing_intent": intent}

    def _specialist_node(self, state: OrchestrationState) -> OrchestrationState:
        rewritten = state.get("rewritten_query") or RewrittenQuery(
            normalized_text=state["request"].user_query.lower()
        )
        routing = state.get("routing_intent") or RoutingIntent(domain="general")
        findings = state.get("validation_errors", [])
        plan = GraphQueryPlan.model_validate(self.specialize(rewritten, routing, findings))
        return {"graph_query_plan": plan}

    def _blocked_node(self, state: OrchestrationState) -> OrchestrationState:
        return {
            "result": OrchestrationResult(
                status="blocked",
                safety=state["safety"],
                retry_count=state.get("retry_count", 0),
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _retrieve_node(self, state: OrchestrationState) -> OrchestrationState:
        raw_chunks = self.retrieve(state["graph_query_plan"])
        chunks = [RetrievalChunk.model_validate(chunk) for chunk in raw_chunks]
        return {"retrieved_chunks": chunks}

    def _critic_node(self, state: OrchestrationState) -> OrchestrationState:
        retry_count = state.get("retry_count", 0)
        decision = CriticDecision.model_validate(
            self.critic(
            state["request"].user_query,
            state.get("routing_intent") or RoutingIntent(domain="general"),
            state.get("retrieved_chunks", []),
            retry_count,
            )
        )
        if decision.passed:
            return {"critic_decision": decision}

        current_errors = list(state.get("validation_errors", []))
        current_errors.extend(decision.findings)
        next_retry = retry_count + 1
        return {
            "critic_decision": decision,
            "validation_errors": current_errors,
            "retry_count": next_retry,
        }

    def _payload_node(self, state: OrchestrationState) -> OrchestrationState:
        payload = PayloadDraft.model_validate(
            self.generate_payload(state["request"].user_query, state.get("retrieved_chunks", []))
        )
        return {"payload": payload}

    def _evaluate_node(self, state: OrchestrationState) -> OrchestrationState:
        gate = EvaluationGate.model_validate(
            self.evaluate(
                state["request"].user_query,
                state["payload"].response_text,
                state.get("retrieved_chunks", []),
                self.config.evaluation_threshold,
            )
        )
        return {"evaluation": gate}

    def _finalize_success_node(self, state: OrchestrationState) -> OrchestrationState:
        return {
            "result": OrchestrationResult(
                status="ok",
                response_text=state["payload"].response_text,
                safety=state.get("safety"),
                rewritten_query=state.get("rewritten_query"),
                routing_intent=state.get("routing_intent"),
                retrieved_chunks=state.get("retrieved_chunks", []),
                citations=state["payload"].citations,
                uncertainty=state["payload"].uncertainty,
                evaluation=state["evaluation"],
                validation_errors=state.get("validation_errors", []),
                retry_count=state.get("retry_count", 0),
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _finalize_failed_gate_node(self, state: OrchestrationState) -> OrchestrationState:
        reason = state["evaluation"].reason or "Evaluation quality gate failed."
        return {
            "result": OrchestrationResult(
                status="failed",
                safety=state.get("safety"),
                rewritten_query=state.get("rewritten_query"),
                routing_intent=state.get("routing_intent"),
                retrieved_chunks=state.get("retrieved_chunks", []),
                evaluation=state["evaluation"],
                validation_errors=state.get("validation_errors", []),
                retry_count=state.get("retry_count", 0),
                error=reason,
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _finalize_fail_closed_node(self, state: OrchestrationState) -> OrchestrationState:
        return {
            "result": OrchestrationResult(
                status="failed",
                safety=state.get("safety"),
                rewritten_query=state.get("rewritten_query"),
                routing_intent=state.get("routing_intent"),
                retrieved_chunks=state.get("retrieved_chunks", []),
                validation_errors=state.get("validation_errors", []),
                retry_count=state.get("retry_count", 0),
                error="Critic rejected recommendations after bounded retries.",
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _route_after_safety(self, state: OrchestrationState) -> str:
        return "rewrite" if state["safety"].allowed else "blocked"

    def _route_after_critic(self, state: OrchestrationState) -> str:
        decision = state.get("critic_decision") or CriticDecision(passed=True)
        if decision.passed:
            return "payload"
        if decision.retryable and state.get("retry_count", 0) <= self.config.max_critic_retries:
            return "specialist"
        return "finalize_fail_closed"

    def _route_after_evaluation(self, state: OrchestrationState) -> str:
        return "finalize_success" if state["evaluation"].passed else "finalize_failed_gate"


def run_orchestration(
    request: OrchestrationRequest,
    orchestrator: AgentOrchestrator,
) -> OrchestrationResult:
    return orchestrator.run(request)
