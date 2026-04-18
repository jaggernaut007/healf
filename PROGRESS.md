# Project Progress

## Current Status
Phase 3 is in migration from baseline safety-retrieval-generation-evaluation orchestration to a 5-agent KG-RAG conversational workflow with prompt rewriting, specialist routing, graph retrieval planning, critic retry loop, and grounded payload generation.

## Phase Completion Snapshot
- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete with post-audit hardening.
- Phase 3: In progress (baseline orchestration implemented; 5-agent KG-RAG upgrade now scoped and documented).
- Phase 4: In progress (planning and ADR prepared).

## Verified Working
- Enrichment now fails fast when required API keys are missing.
- URL-based SKU extraction is deterministic and resilient to query/hash URL variants.
- NIH grounding path no longer fabricates warning strings.
- Graph inference now emits multiple triples for a single ingredient when multiple rules apply.
- Rule-driven graph build and preflight modes remain functional.
- LangGraph orchestration flow now routes safety -> retrieval -> generation -> evaluation with terminal blocked/failed/ok outcomes.
- Safety-denied medical-intent requests stop before retrieval and generation.
- Evaluation gate failure prevents final response emission.
- Orchestration failures from observability, retrieval, and generation are surfaced as explicit failed results.
- Default orchestration constructor now wires concrete adapter boundaries from repository data and config.
- Safety adapter applies deterministic medical-intent blocking and optionally attempts NeMo rails loading when available.
- Evaluator adapter applies a quality gate score with optional DeepEval metric execution when configured.
- Observability adapter activates Phoenix and OpenInference instrumentation once per process.
- Safety adapter now reads block phrases from `config/wellness_guard.co` and applies phrase-first blocking before optional NeMo checks.
- NeMo rails loading is now lazy, so blocked queries avoid unnecessary runtime overhead and warnings.
- Guardrails project config exists at `config/config.yml` and is validated by adapter tests.

## Test Evidence
- Latest run: `45 passed` via `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q`.
- New coverage added for:
  - SKU extraction edge cases.
  - Firecrawl fallback/error branches.
  - NIH warning grounding behavior.
  - Enrichment fail-fast credential behavior.
  - Multi-rule/multi-triple graph inference behavior.
  - Committed inference-rules contract loading path.
  - Orchestration happy-path and failure-path integration routing.
  - Safety block behavior that short-circuits downstream nodes.
  - Evaluation gate rejection behavior and observability activation failure handling.
  - Adapter-level safety/retrieval/generation/evaluation deterministic behavior.
  - Config-driven safety phrase parsing, case-insensitive blocking, and phrase-first precedence over NeMo path.
  - Guardrails config presence and configured-path adapter behavior checks.

## Remaining Pending Items
1. Implement prompt rewrite node and typed query-normalization contract in orchestration state.
2. Implement intake router and domain specialist decision nodes using OpenAI-backed structured outputs.
3. Add validated read-only graph query planner/executor boundary and integrate graph evidence retrieval.
4. Implement pharmacovigilance critic with bounded retry loop and explicit validation errors.
5. Replace template generation path with conversational evidence-grounded payload generation.
6. Add integration tests for full 5-agent flow, critic retry behavior, and fail-closed routing.
7. Implement Phase 4 CLI entrypoint and task runner.
8. Add CLI integration tests.

## Next Steps
1. Deliver Phase 3 5-agent KG-RAG workflow in bounded slices (rewrite/router -> specialist/retriever -> critic -> payload).
2. Validate each orchestration slice with deterministic unit/integration tests before moving to the next node.
3. Expose orchestration entrypoint via CLI/tasks aligned with ADR-0009 once Phase 3 migration is stable.
