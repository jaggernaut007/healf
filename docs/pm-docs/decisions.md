# Implementation Decisions

Status: 2026-04-18

## Current State
- Phase 3 orchestration is implemented and test-verified in this repository.
- Phase 4 remains in progress and is now the active delivery scope.

## Runtime Decisions
- Use LangGraph for deterministic node-level orchestration with bounded retries.
- Enforce safety checks before rewrite, routing, retrieval, and payload generation.
- Enforce read-only query planning and bounded retrieval constraints.
- Require evaluation gate pass before final successful response emission.
- Validate every agent output and every LLM-call output with Pydantic schemas at runtime.

## Safety Decisions
- Apply phrase-first blocking from config/wellness_guard.co.
- Use NeMo guardrails as semantic safety control when available.
- Fail closed when NeMo guardrails are unavailable.
- Fail closed when NeMo execution errors occur.
- Parse dynamic structured NeMo safety decisions when provided.
- Structured contract fields:
	- allowed
	- reason
	- reason_code
	- risk_level
- If the NeMo response cannot be parsed as a safety contract, fail closed.
- Require critic validation for high-risk contexts (medication, pregnancy, diagnosis, allergy) before payload output.

## Tracking Decisions
- SPEC.md is canonical for acceptance criteria.
- PROGRESS.md, feature_list.json, and todo.md should only be updated with tool-verified evidence.
- PM docs must explicitly distinguish implemented behavior from pending Phase 4 scope.
