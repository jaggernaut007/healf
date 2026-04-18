# Phase 3 Execution Plan: 5-Agent KG-RAG Orchestration

Status: Active
Last Updated: 2026-04-18

## Objective
Implement a conversational, graph-grounded health chatbot using a five-agent LangGraph topology with bounded safety and validation loops.

## Approved Agent Topology
1. Intake Router
2. Domain Specialist
3. Graph Retriever
4. Pharmacovigilance Critic
5. Payload Generator

Preprocessing node:
- Prompt Rewrite (before routing)

Cross-cutting gates:
- Safety guardrails before specialist/retriever/generation
- Evaluation gate before final response
- Rate limiting at API boundary when orchestration endpoint is exposed

## Work Breakdown

### Slice A: State and Contracts
Deliverables:
- Extend orchestration models with typed contracts for rewritten query, routing intent, graph query plan, critic findings, and payload metadata.
- Keep backward compatibility for existing request fields.

Acceptance checks:
- Model validation tests pass for valid/invalid payloads.

### Slice B: Prompt Rewrite + Router
Deliverables:
- Prompt rewrite adapter that preserves intent semantics while improving retrieval readiness.
- Router adapter for domain and risk routing.

Acceptance checks:
- Rewrite tests assert normalized entity extraction and meaning preservation.
- Router tests assert expected specialist lane for representative query types.

### Slice C: Specialist + Graph Retrieval Boundary
Deliverables:
- Specialist agent emits structured read-only graph query plans.
- Query boundary validates allowed schema usage and executes parameterized read-only queries.
- Retriever normalizes graph results into evidence chunks.

Acceptance checks:
- Tests reject non-read-only plans.
- Tests verify valid plans execute and normalize as expected.

### Slice D: Pharmacovigilance Critic Loop
Deliverables:
- Critic adapter checks conflicts against user profile and evidence.
- Bounded retry from critic -> specialist with structured validation errors.

Acceptance checks:
- Critic fail routes back to specialist once (bounded).
- Retry exhaustion fails closed with explicit status.

### Slice E: Conversational Payload + Evaluation
Deliverables:
- Payload generator produces conversational grounded responses and UI-ready metadata.
- Evaluation gate remains mandatory before final emit.

Acceptance checks:
- No-evidence case returns transparent uncertainty response.
- Low-quality outputs are blocked by evaluation gate.

## Node Flow (Target)
- safety -> prompt_rewrite -> intake_router -> domain_specialist -> graph_retriever -> critic
- critic_pass -> payload_generator -> evaluate -> finalize_ok
- critic_fail -> domain_specialist (bounded retry)
- any_error -> finalize_failed
- safety_block -> finalize_blocked

## Test Plan
Targeted:
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/test_orchestrator_adapters.py -q
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/test_orchestrator.py -q

Regression:
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q

## Evidence and Tracking
Update after each slice:
- PROGRESS.md
- todo.md
- feature_list.json

## Non-Goals for Phase 3
- CLI/task-runner expansion (Phase 4).
- API surface redesign beyond orchestration needs.

## API Boundary Control
When a chat endpoint is exposed, apply rate limiting at ingress as a mandatory control.
If endpoint exposure is deferred, keep rate limiting as a tracked Phase 4 blocker.
