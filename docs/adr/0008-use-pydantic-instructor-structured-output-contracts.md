# 8. Use Pydantic + Instructor for Structured Output Contracts

## Status
Accepted

## Context
The pipeline depends on reliable structured extraction for enrichment outputs and UI payload generation. Unconstrained model output increases parsing failures, hidden schema drift, and downstream graph inconsistencies.

Research validation and current project patterns support combining Pydantic schema definitions with Instructor-constrained generation.

## Decision
Standardize structured output boundaries on:
- `Pydantic` models for explicit schema contracts.
- `instructor` for constrained model outputs that conform to those schemas.

Use this pattern for enrichment records, chat payloads, and other contract-critical boundaries.

## Consequences
- Positive: Stronger schema consistency and safer downstream processing.
- Positive: Better testability for contract compliance.
- Negative: Additional strictness may require schema/prompt iteration during development.
- Negative: Coupling to Instructor behavior/version semantics requires pinning discipline.
