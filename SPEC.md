# Healf Spec-Driven Development Contract

Status: Active
Last Updated: 2026-04-18

## Purpose

This file is the canonical product and execution contract for all coding agents in this repository. Agents must ground planning, implementation, testing, review, and release activities in this specification.

## Mandatory Agent Rules

1. Agents must read this file before planning or implementation.
2. Every task must be mapped to a phase and acceptance criteria in this file.
3. If requested work is out of scope, ambiguous, or conflicts with this file, implementation is blocked until this file is updated.
4. Completion claims are invalid without tool-verified evidence against acceptance criteria.
5. Architecture, dependency, and API contract changes must be reflected in ADRs and research notes before implementation.

## Phases

### Phase 0: Setup and Governance

Acceptance criteria:
- Project structure, environment, and test scaffolding are in place.
- Research notes are indexed in `docs/research/INDEX.md`.
- ADR baseline exists in `docs/adr/`.

### Phase 1: Enrichment Pipeline

Acceptance criteria:
- `src/clients/enrichment_client.py` supports external enrichment data retrieval.
- `src/enrichment.py` orchestrates enrichment flow and persists outputs.
- Product schema is validated with Pydantic models in `src/models/`.
- Tests for enrichment and client flows pass.

### Phase 2: Knowledge Graph Builder

Acceptance criteria:
- `src/graph_builder.py` builds graph entities and relationships from enriched data.
- Rule-based inference uses `data/research/graph_inference_rules.json`.
- Graph build path is test-covered and deterministic for repeated runs.

### Phase 3: Agentic Orchestration

Acceptance criteria:
- Orchestration workflow coordinates a five-agent path: intake router, domain specialist, graph retriever, pharmacovigilance critic, and payload generator.
- Prompt rewriting runs before intake routing and preserves original user intent semantics.
- Guardrails are applied before specialist, retrieval, and generation execution.
- Graph retrieval runs through validated read-only query plans and deterministic execution boundaries.
- Critic loop supports bounded retry behavior and fail-closed escalation when safety or data constraints are violated.
- Payload output is conversational, grounded strictly in retrieved evidence, and degrades gracefully when evidence is insufficient.
- Observability instrumentation is active for orchestration runs.
- Evaluation quality gates run before final response is returned.
- Integration tests validate orchestration control flow, critic retry behavior, and failure paths.

### Phase 4: CLI and UX

Acceptance criteria:
- CLI entrypoint provides operator commands for enrichment, graph build, and orchestration tasks.
- CLI output is structured and human-readable.
- Task runner commands support repeatable local and CI operations.
- CLI and task-runner behavior is covered by tests.

### Phase 5: Compliance and Industrial Hardening

Acceptance criteria:
- Industrial MCP stack (context7, nexus-mcp, sequential-thinking, playwright, chrome-devtools, memstate-ai, fetch) is configured and routed.
- Triple Agent Audit is performed for Phase 4 CLI/UX and documented in `docs/audits/`.
- Eval-Driven Development (EDD) suite is scaffolded in `evals/` with a golden dataset covering: positive, dangerous (diagnosis/interaction), edge cases (misspellings), and persona-based queries (athlete vs. illiterate).
- Industrial performance patterns (TTL L1 Caching) implemented in the enrichment pipeline.

## Wave Contract

All work must follow this wave sequence unless explicitly waived in this file:

1. Plan wave: scoped, verifiable tasks with dependencies.
2. Implement wave: smallest change to satisfy acceptance criteria.
3. Test wave: failing tests first, then passing verification.
4. Review wave: bug, security, regression, and compatibility checks.
5. Docs wave: synchronize ADRs, research notes, and progress artifacts.

## Allowed Evidence for Completion

- Test outputs from tool calls.
- Lint outputs from tool calls.
- File diffs matching requested acceptance criteria.
- Updated docs (`PROGRESS.md`, `feature_list.json`, ADRs/research as needed).

## Change Control

When this spec changes, update:

1. Relevant ADR in `docs/adr/`.
2. Research note in `docs/research/` when dependencies or APIs change.
3. Tracking artifacts: `todo.md`, `PROGRESS.md`, and `feature_list.json`.
