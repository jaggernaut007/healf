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

## Coverage Targets

- 80%+ for business logic.
- 100% for critical paths.

## Completion Evidence

A task is complete only when:

1. Tests pass via tool execution.
2. Lint passes.
3. Behavior and docs are synchronized.
4. PROGRESS and feature status are updated from verified outputs.
