# Testing Strategy

Tests are the source of truth for feature completion.

## Core Rules

- Write failing tests first for behavior changes.
- Implement minimal code to satisfy tests.
- Read actual test output before reporting completion.

## Testing Pyramid

- Unit tests: run continuously for fast feedback.
- Integration tests: run after meaningful changes.
- E2E tests: run for critical workflows and release checks.

## Eval-Driven Development (EDD)

We utilize **Eval-Driven Development** to iterate on non-deterministic LLM nodes and safety guardrails.

1.  **Baseline Failure**: Identify a scenario where the agent fails (e.g., missed interaction, weak reasoning).
2.  **Reproduction Case**: Create a surgical test case (unit or eval) that reproduces the failure state.
3.  **Heuristic/Prompt Hardening**: Update the adapter logic, prompt schemas, or fallback heuristics to address the failure.
4.  **Verification**: Run the full suite to ensure the fix holds without regressing existing quality scores.

## Coverage Targets
...

- 80%+ for business logic.
- 100% for critical paths.

## Completion Evidence

A task is complete only when:

1. Tests pass via tool execution.
2. Lint passes.
3. Behavior and docs are synchronized.
4. PROGRESS is updated from verified outputs.
