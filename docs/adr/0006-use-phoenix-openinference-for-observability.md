# 6. Use Arize Phoenix + OpenInference Instrumentation for Observability

## Status
Accepted

## Context
The orchestration pipeline needs trace-level visibility for debugging retrieval quality, latency outliers, and response faithfulness regressions. Observability must capture spans/events across model calls and orchestration nodes.

Research and package validation support `arize-phoenix` with `openinference-instrumentation-langchain` for this stack.

## Decision
Use:
- `arize-phoenix` as the primary tracing and inspection UI.
- `openinference-instrumentation-langchain` for model/orchestration instrumentation hooks.

Enable tracing in development and controlled environments, and keep observability dependencies configurable for lean runtime profiles.

## Consequences
- Positive: Better debugging and faster root-cause analysis for agent behavior.
- Positive: Consistent trace data across orchestration and model boundaries.
- Negative: Additional dependency/runtime overhead if always enabled.
- Negative: `arize-phoenix` uses Elastic-2.0 licensing, which requires policy review for some distribution contexts.
