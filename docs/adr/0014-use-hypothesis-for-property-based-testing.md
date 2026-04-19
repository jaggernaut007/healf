# ADR-0014: Use Hypothesis for Property-Based Testing

## Status
Accepted

## Context
Standard unit tests with manual edge cases are often insufficient for uncovering subtle bugs in data parsing, SKU extraction, and graph construction logic, where edge cases in strings, URLs, and large datasets can be difficult to predict. We need a more rigorous way to verify the correctness and robustness of our deterministic logic.

## Decision
We will use **Hypothesis** (v6.152.1) to implement property-based testing. Hypothesis automatically generates diverse and extreme inputs to test that specific properties (e.g., idempotency, type safety, non-empty outputs) hold true regardless of the input.

Specifically, we will apply Hypothesis to:
1. URL-based SKU extraction logic in `EnrichmentClient`.
2. Rule-driven graph inference in `GraphBuilder`.
3. String normalization and prompt rewriting helpers.

## Consequences
- **Easier**: Uncovers complex edge cases (e.g., Unicode characters in URLs, empty strings, extremely large inputs) that manual testing would likely miss. Improves confidence in the reliability of core data transformation logic.
- **Harder**: Requires writing tests in terms of "properties" rather than fixed inputs/outputs, which has a steeper learning curve. Tests can also run slower as they execute multiple generated examples (tunable via `max_examples`).
