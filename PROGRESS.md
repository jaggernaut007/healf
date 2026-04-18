# Project Progress

## Current Status
Phase 3 is implemented and verified with the 5-agent KG-RAG conversational workflow now active in orchestration.

## Phase Completion Snapshot
- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete with post-audit hardening.
- Phase 3: Complete.
- Phase 4: Complete (Typer CLI, Rich formatting, Invoke task runner, and integration tests).

## Verified Working
- Core framework research notes in `docs/research/INDEX.md` were re-verified against Context7 sources on 2026-04-18 and status stamps were refreshed.
- Enrichment now fails fast when required API keys are missing.
- URL-based SKU extraction is deterministic and resilient to query/hash URL variants.
- NIH grounding path no longer fabricates warning strings.
- Graph inference now emits multiple triples for a single ingredient when multiple rules apply.
- Rule-driven graph build and preflight modes remain functional.
- LangGraph orchestration flow now routes safety -> rewrite -> intake router -> specialist -> read-only retrieval -> critic -> payload -> evaluation with terminal blocked/failed/ok outcomes.
- Safety-denied medical-intent requests stop before retrieval and generation.
- Evaluation gate failure prevents final response emission.
- Orchestration failures from observability, retrieval, and generation are surfaced as explicit failed results.
- Default orchestration constructor now wires concrete adapter boundaries from repository data and config.
- Safety adapter applies deterministic medical-intent blocking and optionally attempts NeMo rails loading when available.
- Evaluator adapter applies a quality gate score with optional DeepEval metric execution when configured.
- Observability adapter activates Phoenix and OpenInference instrumentation once per process.
- Safety adapter now reads block phrases from `config/wellness_guard.co` and applies phrase-first blocking before optional NeMo checks.
- Safety adapter now parses a dynamic structured NeMo decision contract (`allowed`, `reason`, `reason_code`, `risk_level`) when available.
- Safety decision path now emits normalized decision metadata (`reason_code`, `risk_level`, `source`) for deterministic downstream handling.
- NeMo rails loading is now lazy, so blocked queries avoid unnecessary runtime overhead and warnings.
- Guardrails project config exists at `config/config.yml` and is validated by adapter tests.
- Prompt rewrite adapter normalizes query text with deterministic term preservation before routing.
- Intake router assigns deterministic domain and risk routes.
- Domain specialist emits structured read-only graph query plans.
- Retrieval boundary enforces read-only plan validation and bounded limits before evidence retrieval.
- Pharmacovigilance critic supports bounded retry and fail-closed outcomes with structured validation findings.
- Payload generator emits conversational responses constrained to retrieved evidence citations and transparent uncertainty for no-evidence scenarios.
- All agent node outputs are runtime-validated via Pydantic before state mutation.
- All LLM call boundaries (Instructor extraction, NeMo safety decisions, embeddings API responses) are schema-validated before downstream use.

## Test Evidence
- Latest run: `70 passed` via `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q`.
- Init verification run passes deterministically via `./scripts/init.sh` with plugin autoload disabled.
- New coverage added for:
  - SKU extraction edge cases.
  - Firecrawl fallback/error branches.
  - NIH warning grounding behavior.
  - Enrichment fail-fast credential behavior.
  - Multi-rule/multi-triple graph inference behavior.
  - Committed inference-rules contract loading path.
  - Orchestration full Phase 3 node-order happy path.
  - Safety block behavior that short-circuits downstream nodes.
- Adapter-level rewrite/router/specialist/retrieval-boundary/critic/payload/evaluation deterministic behavior.
- Config-driven safety phrase parsing, case-insensitive blocking, and phrase-first precedence over NeMo path.
- Guardrails config presence and configured-path adapter behavior checks.
- Critic retry-success flow and bounded retry fail-closed flow.

- Phase 4 CLI entrypoint provides `enrichment`, `graph`, and `orchestration` subcommands with `rich` terminal formatting.
- `invoke` tasks implemented for `test`, `lint`, `smoke`, and `check` workflows.
- CLI integration tests verify help output, subcommand execution with mocks, and safety block handling.
- Task runner tests verify task logic and command composition.
- Smoke test confirms CLI help availability across all namespaces.
- Dependency fix: `tasks.py` function names decoupled from `pytest` collection patterns to avoid test discovery conflicts.
- Environment fix: `invoke` tasks use `in_stream=False` to avoid TTY-related OSErrors in restricted environments.

## Phase 5: Compliance & Hardening [COMPLETE]
- Industrial MCP configuration implemented and routed via `docs/MCP-ROUTING.md`.
- Agent personas updated with advanced memory and testing tools in `.claude/agents/`.
- Triple Agent Audit performed and documented in `docs/audits/phase-5-audit.md`.
- TTL L1 Caching and Golden Dataset (10 cases) implemented.

## Test Evidence
- Latest run: `81 passed` via `uv run invoke test`.
- Smoke test passes via `uv run invoke smoke`.
- Init verification run passes via `./scripts/init.sh`.

## Remaining Pending Items
1. Final production deployment configuration.
2. API ingress rate-limiting implementation (if exposing as public API).

## Next Steps
1. Finalize documentation and repository release state.
2. Prepare for Phase 5 or production transition if requested.
