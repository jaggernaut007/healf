# 7. Use DeepEval as CI Quality Gates for LLM Outputs

## Status
Accepted

## Context
Traditional unit tests are insufficient to validate generated response quality and grounding behavior. The system needs repeatable evaluation gates for faithfulness and answer relevance as part of delivery readiness.

Research and package checks validate `deepeval` as an appropriate framework for test-based LLM quality assertions in this repository.

## Decision
Adopt `DeepEval` for evaluation tests in CI/CD simulation.

- Track at least faithfulness and relevance metrics for curated test cases.
- Run evaluation tests through pytest workflows.
- Treat failing evaluation thresholds as release blockers for relevant features.

## Consequences
- Positive: Objective quality gates for generative behaviors.
- Positive: Early detection of retrieval or prompt regressions.
- Negative: Metric tuning and test case maintenance overhead.
- Negative: Evaluations may require careful control of non-determinism.
