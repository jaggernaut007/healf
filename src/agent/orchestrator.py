from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, TypedDict
import nest_asyncio

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
    DiscoveryDecision,
    IntentClassification,
)

nest_asyncio.apply()


class OrchestrationConfig(BaseModel):
    evaluation_threshold: float = 0.7
    enable_observability: bool = Field(
        default_factory=lambda: (
            os.getenv("HEALF_ENABLE_OBSERVABILITY", "false").lower() == "true"
        )
    )
    max_critic_retries: int = 3
    main_model: str = Field(default_factory=lambda: os.getenv("ORCHESTRATOR_MAIN_MODEL", "gpt-5.4"))
    lite_model: str = Field(default_factory=lambda: os.getenv("ORCHESTRATOR_LITE_MODEL", "gpt-5.4-mini"))


class OrchestrationState(TypedDict, total=False):
    request: OrchestrationRequest
    safety: SafetyDecision
    intent_classification: IntentClassification
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
    requires_clarification: bool
    clarification_question: str | None
    trace_enabled: bool


class AgentOrchestrator:
    def __init__(
        self,
        config: OrchestrationConfig,
        safety_check: Callable[[str, dict[str, Any]], IntentClassification],

        rewrite: Callable[[str], RewrittenQuery],
        route: Callable[[RewrittenQuery], RoutingIntent],
        specialize: Callable[..., GraphQueryPlan],
        retrieve: Callable[[GraphQueryPlan], list[RetrievalChunk]],
        critic: Callable[[str, RoutingIntent, list[RetrievalChunk], int, dict[str, Any]], CriticDecision],
        generate_payload: Callable[[str, list[RetrievalChunk], dict[str, Any], list[dict[str, str]]], PayloadDraft],
        evaluate: Callable[[str, str, list[RetrievalChunk], float], EvaluationGate],
        discover: Callable[[str, list[dict[str, str]], dict[str, Any]], str] | None = None,
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
        self.discover = discover
        self.activate_observability = activate_observability
        self._graph = self.build_graph()

    @classmethod
    def build_default(
        cls,
        config: OrchestrationConfig | None = None,
        neo4j_uri: str = os.getenv("NEO4J_URI", ""),
        neo4j_username: str = os.getenv("NEO4J_USERNAME", ""),
        neo4j_password: str = os.getenv("NEO4J_PASSWORD", ""),
        neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j"),
    ) -> "AgentOrchestrator":
        from src.agent.nodes import (
            build_default_critic,
            build_default_evaluator,
            build_default_intake_router,
            build_default_observability_activator,
            build_default_payload_generator,
            build_default_prompt_rewriter,
            build_default_retriever,
            build_default_safety_check,
            build_default_specialist,
            build_default_discovery,
        )

        config = config or OrchestrationConfig()
        return cls(
            config=config,
            safety_check=build_default_safety_check(
                model=config.main_model,
                neo4j_uri=neo4j_uri, 
                neo4j_username=neo4j_username, 
                neo4j_password=neo4j_password, 
                neo4j_database=neo4j_database
            ),
            rewrite=build_default_prompt_rewriter(model=config.lite_model),
            route=build_default_intake_router(model=config.lite_model),
            specialize=build_default_specialist(model=config.lite_model),
            retrieve=build_default_retriever(
                neo4j_uri=neo4j_uri, 
                neo4j_username=neo4j_username, 
                neo4j_password=neo4j_password, 
                neo4j_database=neo4j_database
            ),
            critic=build_default_critic(model=config.main_model),
            generate_payload=build_default_payload_generator(model=config.main_model),
            evaluate=build_default_evaluator(model=config.main_model),
            discover=build_default_discovery(
                model=config.main_model,
                neo4j_uri=neo4j_uri, 
                neo4j_username=neo4j_username, 
                neo4j_password=neo4j_password, 
                neo4j_database=neo4j_database
            ),
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
        graph.add_node("discovery", self._discovery_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("finalize_success", self._finalize_success_node)
        graph.add_node("finalize_discovery", self._finalize_discovery_node)
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
        graph.add_conditional_edges(
            "intake_router",
            self._route_after_router,
            {"specialist": "specialist", "discovery": "discovery"},
        )
        graph.add_edge("discovery", "finalize_discovery")
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
        graph.add_edge("finalize_discovery", END)
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
                    "requires_clarification": False,
                    "validation_errors": [],
                }
            )
        except Exception as exc:
            print(f"ORCHESTRATION EXCEPTION: {exc}")
            import traceback
            traceback.print_exc()
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

    def _safe_call(self, func: Callable, *args, **kwargs) -> Any:
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        # Filter kwargs based on function signature
        valid_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in sig.parameters or any(p.kind == p.VAR_KEYWORD for p in params)
        }
        
        # Filter positional args based on function signature
        max_pos = len([p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)])
        if any(p.kind == p.VAR_POSITIONAL for p in params):
            max_pos = len(args)
            
        return func(*args[:max_pos], **valid_kwargs)

    def _safety_node(self, state: OrchestrationState) -> OrchestrationState:
        request = state["request"]
        classification = IntentClassification.model_validate(
            self._safe_call(self.safety_check, request.user_query, profile=request.user_profile)
        )
        
        # Derive safety decision
        allowed = not classification.is_clinical_diagnosis_request
        safety = SafetyDecision(
            allowed=allowed,
            reason=classification.reasoning if not allowed else "Allowed",
            reason_code="CLINICAL_DIAGNOSIS_BLOCK" if not allowed else "OK",
            risk_level="high" if not allowed else "low",
            source="cognitive_guardrails"
        )
        
        return {"safety": safety, "intent_classification": classification}


    def _rewrite_node(self, state: OrchestrationState) -> OrchestrationState:
        request = state["request"]
        rewritten = RewrittenQuery.model_validate(
            self._safe_call(self.rewrite, request.user_query, profile=request.user_profile)
        )
        return {"rewritten_query": rewritten}

    def _router_node(self, state: OrchestrationState) -> OrchestrationState:
        request = state["request"]
        rewritten = state.get("rewritten_query") or RewrittenQuery(
            normalized_text=request.user_query.lower()
        )
        
        intent = RoutingIntent.model_validate(
            self._safe_call(self.route, rewritten, profile=request.user_profile)
        )
        return {"routing_intent": intent}



    def _specialist_node(self, state: OrchestrationState) -> OrchestrationState:
        request = state["request"]
        rewritten = state.get("rewritten_query") or RewrittenQuery(
            normalized_text=request.user_query.lower()
        )
        routing = state.get("routing_intent") or RoutingIntent(domain="general")
        findings = state.get("validation_errors", [])
        plan = GraphQueryPlan.model_validate(
            self._safe_call(self.specialize, rewritten, routing, findings, profile=request.user_profile)
        )
        return {"graph_query_plan": plan}

    def _blocked_node(self, state: OrchestrationState) -> OrchestrationState:
        reason = state["safety"].reason if "safety" in state else "Blocked by safety policy."
        return {
            "result": OrchestrationResult(
                status="blocked",
                safety=state["safety"],
                error=reason,
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
        request = state["request"]
        decision = CriticDecision.model_validate(
            self._safe_call(
                self.critic,
                request.user_query,
                state.get("routing_intent") or RoutingIntent(domain="general"),
                state.get("retrieved_chunks", []),
                retry_count,
                profile=request.user_profile,
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
        request = state["request"]
        decision = state.get("critic_decision")
        safety_findings = decision.findings if decision and not decision.passed else []
        
        payload = PayloadDraft.model_validate(
            self._safe_call(
                self.generate_payload,
                request.user_query,
                state.get("retrieved_chunks", []),
                profile=request.user_profile,
                chat_history=request.chat_history,
                safety_findings=safety_findings,
            )
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
                intent_classification=state.get("intent_classification"),
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
                intent_classification=state.get("intent_classification"),
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
                intent_classification=state.get("intent_classification"),
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
        decision = state.get("critic_decision") or CriticDecision(passed=True, findings=[])
        if decision.passed:
            return "payload"
        
        if decision.retryable:
            if state.get("retry_count", 0) <= self.config.max_critic_retries:
                return "specialist"
            return "finalize_fail_closed"
        
        # If not retryable, go to payload for conversational refusal
        return "payload"

    def _route_after_evaluation(self, state: OrchestrationState) -> str:
        return "finalize_success" if state["evaluation"].passed else "finalize_failed_gate"

    def _route_after_router(self, state: OrchestrationState) -> str:
        intent = state.get("routing_intent")
        if intent and intent.requires_clarification:
            return "discovery"
        return "specialist"

    def _discovery_node(self, state: OrchestrationState) -> OrchestrationState:
        request = state["request"]
        if not self.discover:
            return {
                "requires_clarification": False,
                "clarification_question": None,
            }

        discovery = DiscoveryDecision.model_validate(
            self._safe_call(
                self.discover,
                request.user_query,
                state.get("rewritten_query"),
                state.get("routing_intent"),
                profile=request.user_profile,
                chat_history=request.chat_history,
            )
        )
        return {
            "requires_clarification": discovery.requires_clarification,
            "clarification_question": discovery.clarification_question,
        }

    def _finalize_discovery_node(self, state: OrchestrationState) -> OrchestrationState:
        question = state.get("clarification_question")
        return {
            "result": OrchestrationResult(
                status="ok",
                response_text=question,
                safety=state.get("safety"),
                intent_classification=state.get("intent_classification"),
                rewritten_query=state.get("rewritten_query"),
                routing_intent=state.get("routing_intent"),
                requires_clarification=True,
                clarification_question=question,
                retry_count=state.get("retry_count", 0),
                trace_enabled=state.get("trace_enabled", False),
            )
        }


def run_orchestration(
    request: OrchestrationRequest,
    orchestrator: AgentOrchestrator,
) -> OrchestrationResult:
    return orchestrator.run(request)
