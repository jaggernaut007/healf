---
description: Testing standards and requirements
paths:
  - "**/*.test.ts"
  - "**/*.test.py"
  - "**/*.spec.ts"
  - "**/*.spec.py"
---

# Testing Standards

## General Principles
- Write failing tests before implementation (TDD)
- Tests define the specification (not documentation)
- One assertion per test when possible
- Test behavior, not implementation details

## Test Organization
- Arrange-Act-Assert pattern
- Clear test names describing behavior
- Group related tests with describe/context blocks
- Independent tests (no shared state)

## Coverage Requirements
- All new features require tests before marking complete
- Aim for 80%+ coverage on business logic
- 100% coverage on critical paths (auth, payments, data validation)

## Test Types
- **Unit tests**: Run continuously (<5s feedback)
- **Integration tests**: Run after each commit
- **E2E tests**: Run in CI before merge

## Verification Protocol
- Run tests via tool call before marking task complete
- Read test output to verify pass (never self-report)
- Commit failing tests as checkpoint before implementation
