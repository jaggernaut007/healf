# System Architecture: Healf Health Intelligence Engine

Status: 2026-04-18

## Scope and Status Boundary
This document defines the implemented architecture for Phase 3 and the pending execution scope for Phase 4.

Implemented architecture:
- Prompt rewrite preprocessing plus a five-agent orchestration cycle:
  - Intake Router
  - Domain Specialist
  - Graph Retriever
  - Pharmacovigilance Critic
  - Payload Generator
- Bounded retry loop between Critic and Specialist.
- Graph-grounded conversational output constrained to retrieved evidence.
- Fail-closed safety behavior when NeMo guardrails are unavailable or execution fails.
- Dynamic NeMo safety decision contract parsing with explicit fields:
  - allowed
  - reason
  - reason_code
  - risk_level
- Unparseable NeMo decisions are treated as high-risk and fail closed.

Phase 4 pending architecture scope:
- CLI/task-runner operator surfaces for enrichment, graph build, and orchestration tasks.
- API ingress controls and operator ergonomics for repeatable local/CI usage.

## Architectural Principles
1. Safety-first execution: high-risk medical intent is blocked before specialist or generation nodes run.
2. Evidence-first generation: responses must be grounded in retrieved graph/product evidence.
3. Typed contracts over free text: node interfaces use strict structured outputs.
4. Bounded autonomy: retry loops are capped and fail closed on persistent errors.
5. Observable trajectories: node transitions and rejection reasons are traceable.

## End-to-End Flow (Implemented)
1. Safety node evaluates the raw user query and can terminate as blocked.
2. Prompt Rewrite normalizes the query for retrieval planning while preserving intent.
3. Intake Router chooses domain lane and risk route.
4. Domain Specialist drafts a structured, read-only graph query plan.
5. Graph Retriever executes validated query plans and normalizes evidence chunks.
6. Pharmacovigilance Critic evaluates candidate recommendation against profile constraints.
7. Critic pass routes to Payload Generator; critic fail routes back to Specialist with validation errors (bounded retry).
8. Evaluator gate validates output quality before final response is returned.

## State Contract (Implemented)
State must preserve both raw and transformed data:
- chat_history (append-only)
- user_profile (overwritable structured facts)
- rewritten_query (single normalized query)
- routing_intent (domain/risk classification)
- graph_query_plan (validated read-only plan)
- retrieved_evidence (appendable evidence paths/chunks)
- candidate_payload (overwritable draft)
- validation_errors (append-only critic findings)
- evaluation_result and terminal status

All agent node outputs are runtime-validated with Pydantic models before state updates.

## Graph Retrieval and Query Safety
The graph layer remains deterministic even when planned by LLM:
- LLM can propose plans but never executes direct arbitrary Cypher.
- Query boundary enforces read-only allowlist rules.
- Query boundary enforces parameterization, timeout, and row caps.
- Evidence objects are normalized into a shared schema before reranking/generation.

## LLM Output Validation
- Instructor extraction outputs are re-validated with Pydantic before use.
- Safety responses are parsed through the IntentClassification schema.
- Embeddings API responses are validated against a Pydantic response schema before vector usage.
- Any schema violation fails the current run instead of silently degrading.

## Pharmacovigilance Critic Responsibilities
The critic is the final safety net before output:
- Validates contraindications against profile facts (allergies, medications, known conditions).
- Emits structured validation errors when conflicts are found.
- Requests one bounded retry from Specialist with error context.
- Fails closed when retries are exhausted.

## Conversational Output Strategy
KG-RAG improves trust and specificity; user-friendliness is delivered by the Payload Generator:
- Response tone is conversational and direct.
- Claims are limited to supported evidence.
- Unknowns are stated explicitly when evidence is insufficient.
- Output includes machine-readable citations/recommendations for UI rendering.

## Evaluation and Observability
- Evaluation gate remains mandatory before final response release.
- Observability traces include node path, retry count, and critic outcomes.
- Test suite must cover control flow, fail-closed paths, and retry behavior.

## Failure Modes and Degradation
1. Safety block: return refusal with no downstream execution.
2. Graph query validation failure: return failed with explicit error reason.
3. Critic retry exhaustion: fail closed with validation context.
4. Low evaluation score: suppress final response and return failed status.
5. Empty evidence: return transparent uncertainty response.
