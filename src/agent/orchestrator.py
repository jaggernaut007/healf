from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from src.models.orchestration import (
    EvaluationGate,
    OrchestrationRequest,
    OrchestrationResult,
    RetrievalChunk,
    SafetyDecision,
)


class OrchestrationConfig(BaseModel):
    evaluation_threshold: float = 0.8
    enable_observability: bool = True


class OrchestrationState(TypedDict, total=False):
    request: OrchestrationRequest
    safety: SafetyDecision
    retrieved_chunks: list[RetrievalChunk]
    drafted_response: str
    evaluation: EvaluationGate
    result: OrchestrationResult
    trace_enabled: bool


class AgentOrchestrator:
    def __init__(
        self,
        config: OrchestrationConfig,
        safety_check: Callable[[str], SafetyDecision],
        retrieve: Callable[[str], list[RetrievalChunk]],
        generate: Callable[[str, list[RetrievalChunk]], str],
        evaluate: Callable[[str, str, list[RetrievalChunk], float], EvaluationGate],
        activate_observability: Callable[[], None] | None = None,
    ) -> None:
        self.config = config
        self.safety_check = safety_check
        self.retrieve = retrieve
        self.generate = generate
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
            build_default_evaluator,
            build_default_generator,
            build_default_observability_activator,
            build_default_retriever,
            build_default_safety_check,
        )

        return cls(
            config=config or OrchestrationConfig(),
            safety_check=build_default_safety_check(guardrails_config_path=guardrails_config_path),
            retrieve=build_default_retriever(products_path=products_path),
            generate=build_default_generator(),
            evaluate=build_default_evaluator(),
            activate_observability=build_default_observability_activator(),
        )

    def build_graph(self) -> Any:
        graph = StateGraph(OrchestrationState)
        graph.add_node("safety", self._safety_node)
        graph.add_node("blocked", self._blocked_node)
        graph.add_node("retrieve", self._retrieve_node)
        graph.add_node("generate", self._generate_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("finalize_success", self._finalize_success_node)
        graph.add_node("finalize_failed_gate", self._finalize_failed_gate_node)

        graph.add_edge(START, "safety")
        graph.add_conditional_edges(
            "safety",
            self._route_after_safety,
            {"blocked": "blocked", "retrieve": "retrieve"},
        )
        graph.add_edge("blocked", END)
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            self._route_after_evaluation,
            {"finalize_success": "finalize_success", "finalize_failed_gate": "finalize_failed_gate"},
        )
        graph.add_edge("finalize_success", END)
        graph.add_edge("finalize_failed_gate", END)

        return graph.compile()

    def run(self, request: OrchestrationRequest) -> OrchestrationResult:
        trace_enabled = False
        try:
            trace_enabled = self._activate_observability_if_enabled()
            final_state = self._graph.invoke({"request": request, "trace_enabled": trace_enabled})
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
        decision = self.safety_check(state["request"].user_query)
        return {"safety": decision}

    def _blocked_node(self, state: OrchestrationState) -> OrchestrationState:
        return {
            "result": OrchestrationResult(
                status="blocked",
                safety=state["safety"],
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _retrieve_node(self, state: OrchestrationState) -> OrchestrationState:
        chunks = self.retrieve(state["request"].user_query)
        return {"retrieved_chunks": chunks}

    def _generate_node(self, state: OrchestrationState) -> OrchestrationState:
        drafted = self.generate(state["request"].user_query, state.get("retrieved_chunks", []))
        return {"drafted_response": drafted}

    def _evaluate_node(self, state: OrchestrationState) -> OrchestrationState:
        gate = self.evaluate(
            state["request"].user_query,
            state["drafted_response"],
            state.get("retrieved_chunks", []),
            self.config.evaluation_threshold,
        )
        return {"evaluation": gate}

    def _finalize_success_node(self, state: OrchestrationState) -> OrchestrationState:
        return {
            "result": OrchestrationResult(
                status="ok",
                response_text=state["drafted_response"],
                safety=state.get("safety"),
                retrieved_chunks=state.get("retrieved_chunks", []),
                evaluation=state["evaluation"],
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _finalize_failed_gate_node(self, state: OrchestrationState) -> OrchestrationState:
        reason = state["evaluation"].reason or "Evaluation quality gate failed."
        return {
            "result": OrchestrationResult(
                status="failed",
                safety=state.get("safety"),
                retrieved_chunks=state.get("retrieved_chunks", []),
                evaluation=state["evaluation"],
                error=reason,
                trace_enabled=state.get("trace_enabled", False),
            )
        }

    def _route_after_safety(self, state: OrchestrationState) -> str:
        return "retrieve" if state["safety"].allowed else "blocked"

    def _route_after_evaluation(self, state: OrchestrationState) -> str:
        return "finalize_success" if state["evaluation"].passed else "finalize_failed_gate"


def run_orchestration(
    request: OrchestrationRequest,
    orchestrator: AgentOrchestrator,
) -> OrchestrationResult:
    return orchestrator.run(request)
