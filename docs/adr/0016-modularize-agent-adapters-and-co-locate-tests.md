# ADR 0016: Modularize Agent Adapters and Co-locate Tests

**Status**: Proposed
**Date**: 2026-04-19
**Deciders**: Gemini CLI, Shreyas

## Context

The `src/agent/adapters.py` file had grown into a 900-line "god file" containing all factory functions for LangGraph nodes. This violated the "clear boundaries" and "small functions" principles defined in `docs/CODE-HEALTH.md`. Additionally, tests were centralized in a root `tests/` directory, while `CODE-HEALTH.md` mandated co-located tests.

## Decision

We will:
1.  **Modularize Adapters**: Decompose `src/agent/adapters.py` into a specialized package `src/agent/nodes/`, with separate modules for each domain (safety, routing, rewriter, retrieval, critic, generation, evaluation, observability).
2.  **Consolidate Models**: Move Pydantic models out of logic files (like `src/graph_builder.py`) into `src/models/graph.py`.
3.  **Co-locate Tests**: Move tests from `tests/` to live alongside the source code in `src/`.

## Consequences

### Positive
- **Improved Maintainability**: Smaller, single-purpose modules are easier to reason about and modify.
- **Architectural Alignment**: Aligns the codebase with the project's own health and quality standards.
- **Faster Discovery**: Co-located tests make it immediately clear what behavior is covered for a given module.

### Negative
- **Import Changes**: Requires updating imports across the project.
- **Test Discovery Complexity**: Requires configuring `pytest` to look into `src/`.

### Neutral
- **Structural Shift**: Significant file movements may cause merge conflicts with other long-lived branches.
