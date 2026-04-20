# Triple Agent Audit — Full Project (Post-Architecture Hardening)

**Date**: 2026-04-20
**Auditor**: Antigravity
**Commit Baseline**: HEAD
**Scope**: All Phases 0–7 + Architecture documentation quality
**Trigger**: Manual request post-ARCHITECTURE.md finalisation

---

## Wave 1 — Planner Review

### Scope Mapping Against SPEC.md

| Phase | SPEC Criteria | Status |
|---|---|---|
| 0: Setup & Governance | Structure, env, test scaffold, GFM docs | ✅ PASS |
| 1: Enrichment Pipeline | EnrichmentClient, Pydantic schemas, NIH grounding | ✅ PASS |
| 2: Knowledge Graph Builder | Deterministic Cypher MERGE, inference rules | ✅ PASS |
| 3: Agentic Orchestration | 5-agent LangGraph, safety gate, critic loop, eval gate | ✅ PASS |
| 4: CLI & UX | Typer CLI, rich output, invoke tasks | ✅ PASS |
| 5: Compliance & Hardening | MCP config, EDD golden dataset, TTL caching | ✅ PASS |
| 6: Consultative Discovery | Discovery node, REPL, multi-turn clarification | ✅ PASS |
| 7: Advanced Enrichment | Research summaries, dual-stream retrieval, Critic hardening | ✅ PASS |

### New Since Last Audit (2026-04-19)

- `ARCHITECTURE.md` added: Production-quality engineering narrative covering all 7 system design decisions, known gaps, and founding engineer constraints.
- `SPEC.md` documentation quality criteria added (Phase 0).
- `docs/task.md` standardised to GFM.

---

## Wave 2 — Implementer Review

### Critical Path Nodes

#### Safety Node (`src/agent/nodes/safety.py`)
- ✅ Heuristic hard-block fires before any LLM call (pattern list: `diagnose`, `cancer`, `heart attack`, etc.)
- ✅ Cognitive Classification via `instructor` + `IntentClassification` Pydantic schema enforced at decode layer.
- ✅ KG-grounded context injected into classifier prompt via `Neo4jPropertyGraphStore` vector query.
- ⚠️ `build_default_safety_check()` eagerly constructs `Neo4jPropertyGraphStore` at factory time. Empty URI raised `ConfigurationError` in unit tests. **FIXED in this audit** (see Wave 3).

#### Retrieval Node (`src/agent/nodes/retrieval.py`)
- ✅ Hybrid search: keyword union + vector ANN via `db.index.vector.queryNodes` on both `Product` and `Study` node types.
- ✅ `_validate_read_only_plan()` enforces operation whitelist, limit bounds `[1,5]`, and non-empty key_terms.
- ✅ Dual-stream (product + research) returned as typed `RetrievalChunk` list.
- ℹ️ `final_score` formula uses `coalesce(vector_score, 0.5)` as base. This means keyword-only matches get a static 0.5 bias. Acceptable for current scale; revisit when corpus grows to >100 products.

#### Critic Node (`src/agent/nodes/critic.py`)
- ✅ LLM-as-judge via `client.beta.chat.completions.parse` with `response_format=CriticDecision`.
- ✅ Nuanced prompt prevents over-blocking: general wellness ≠ high-risk by default.
- ✅ Deterministic heuristic fallback if LLM fails: keyword scan for `allergy/medication/pregnant/diagnose`.
- ✅ Empty-chunk short-circuit returns `passed=True` (no evidence = no risk to flag).

#### Orchestrator (`src/agent/orchestrator.py`)
- ✅ LangGraph `StateGraph` with 11 nodes, typed `OrchestrationState`.
- ✅ `_safe_call()` introspects function signatures to prevent passing unsupported kwargs across adapter boundaries.
- ✅ Fail-closed paths: `finalize_fail_closed` (critic retry exhausted), `finalize_failed_gate` (eval gate), `blocked` (safety).
- ✅ Discovery fork: `_route_after_router` gates retrieval until intent is resolved.
- ✅ All inter-node outputs runtime-validated via `Model.model_validate()`.
- ✅ Top-level `run()` catches uncaught exceptions → `OrchestrationResult(status="failed")`, never propagates.

#### Evaluation Node (`src/agent/nodes/evaluation.py`)
- ✅ Heuristic gate: `0.4 + 0.2 * min(chunks, 3)` — deterministic, zero LLM dependency.
- ✅ Optional DeepEval path gated by `HEALF_USE_DEEPEVAL_GATE=true` env var.
- ✅ No-chunk path returns `score=0.0`, `passed=False` (correct fail-closed for empty retrieval).

#### Graph Builder (`src/graph_builder.py`)
- ✅ Idempotent `MERGE` statements throughout — safe to re-run.
- ✅ `ensure_ready()` guards against missing Neo4j config before any network call.
- ✅ Research summaries dual-ingested: `.md` corpus files + `research_summaries.json` structured metadata.
- ✅ Vector indices created `IF NOT EXISTS` for all four node types.
- ✅ `preflight()` mode available for dry-run validation without Neo4j writes.

#### Rule Generator (`src/rule_generator.py`)
- ✅ LLM-synthesised rules grounded against existing PubMed research summaries.
- ✅ Duplicate-check by ingredient term set intersection before append.
- ✅ Clinical safety enforced in system prompt: "NEVER use clinical diseases" in `symptom_name`.
- ⚠️ Still uses `instructor.patch()` (deprecated API) instead of `instructor.from_openai()`. Non-blocking; add to backlog.

---

## Wave 3 — Tester Report

### Test Execution Results

**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ src/ -q --tb=short`

**Result**: `68 passed, 0 failed, 1 warning` ✅

**Failures found and fixed in this audit**:

| Test | Root Cause | Fix Applied |
|---|---|---|
| `test_safety_check_blocks_clinical_diagnosis` | `build_default_safety_check()` eagerly instantiates `Neo4jPropertyGraphStore` with empty URI | Added `autouse` fixture in `test_safety.py` that patches `Neo4jPropertyGraphStore` before factory call |
| `test_safety_check_passes_wellness_query` | Same eager Neo4j construction | Same fixture |
| `test_safety_check_triggers_discovery` | Same eager Neo4j construction | Same fixture |

### Lint Results

**Command**: `uv run ruff check src/`

**Pre-audit**: 5 F401 unused-import errors
**Post-audit**: `All checks passed!` ✅

| File | Removed Import | Reason |
|---|---|---|
| `src/agent/nodes/evaluation.py` | `typing.Any` | Unused |
| `src/agent/orchestrator.py` | `pathlib.Path` | Unused after node modularisation |
| `src/agent/test_adapters.py` | `src.agent.nodes.observability` | Module imported but no direct reference |
| `src/rule_generator.py` | `typing.List` | Legacy Python 3.8 compat import |
| `src/rule_generator.py` | `src.models.research.ResearchSummary` | Unused after refactor |

### Warning (Non-Blocking)

`UserWarning: Client should be an instance of openai.OpenAI or openai.AsyncOpenAI` from `instructor.from_openai()` when called with a mock client in `test_adapters.py`. This is expected in test context; no production impact.

---

## Wave 4 — Reviewer Report

### Security Checklist

| Check | Status | Notes |
|---|---|---|
| No credentials in source | ✅ | All secrets via `os.getenv()` / `.env` |
| No raw SQL/Cypher injection | ✅ | All Cypher parameterised |
| Read-only enforced on retrieval path | ✅ | `_validate_read_only_plan()` whitelist |
| Medical diagnosis requests blocked | ✅ | Two-layer: heuristic + cognitive classifier |
| Fail-closed on LLM errors | ✅ | All nodes have deterministic fallback paths |
| Pydantic validation on all boundaries | ✅ | `model_validate()` before state mutation |

### Architectural Risks

| Risk | Severity | Status |
|---|---|---|
| `build_default_safety_check()` / `build_default_discovery()` eager Neo4j init | Medium | Mitigated in tests; acceptable in prod (fail-fast at startup if misconfigured) |
| `rule_generator.py` uses deprecated `instructor.patch()` | Low | Backlog item; no production regression |
| Heuristic eval score formula is static | Low | Suitable for current corpus scale |
| Single-turn adversarial safety evasion | High (known gap) | Documented in ARCHITECTURE.md §6; multi-turn detection deferred |

---

## Wave 5 — Docs Writer Report

### Documentation Status

| Artefact | Status |
|---|---|
| `ARCHITECTURE.md` | ✅ Complete, production-quality narrative |
| `SPEC.md` | ✅ All phases defined with acceptance criteria |
| `PROGRESS.md` | ✅ Reflects all completed phases |
| `docs/task.md` | ✅ GFM compliant |
| `docs/audits/` | ✅ Audit history preserved |
| `docs/research/INDEX.md` | ✅ Research notes indexed |
| `docs/adr/` | ✅ ADR baseline present |
| `docs/MCP-ROUTING.md` | ✅ MCP config documented |

### PROGRESS.md Update Required

`PROGRESS.md` to be updated post-audit to reflect:
- 3 test failures resolved (test isolation regression fixed).
- 5 lint violations cleared.
- ARCHITECTURE.md finalised as production-grade engineering narrative.

---

## Final Verdicts

| Phase | Verdict |
|---|---|
| 0: Setup & Governance | ✅ SHIP |
| 1: Enrichment Pipeline | ✅ SHIP |
| 2: Knowledge Graph | ✅ SHIP |
| 3: Agentic Orchestration | ✅ SHIP |
| 4: CLI & UX | ✅ SHIP |
| 5: Compliance & Hardening | ✅ SHIP |
| 6: Consultative Discovery | ✅ SHIP |
| 7: Advanced Enrichment | ✅ SHIP |

## **Overall Project Verdict: SHIP ✅**

**Test Evidence**: `68 passed, 0 failed` (post-fix)
**Lint Evidence**: `All checks passed!`

### Backlog Items (Non-Blocking)

1. Migrate `rule_generator.py` from deprecated `instructor.patch()` to `instructor.from_openai()`.
2. Revisit retrieval `coalesce(vector_score, 0.5)` floor when product corpus exceeds ~100 SKUs.
3. Implement multi-turn adversarial intent accumulation (documented known gap).
4. Production deployment config (Terraform/Docker).
5. Public API rate-limiting if external ingress is opened.
