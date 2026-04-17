# Code Health

## Goal

Maintain high-readability, low-risk modules suitable for agentic iteration.

## Practical Quality Signals

- Small functions and clear boundaries.
- Low duplication and explicit ownership.
- Co-located tests with behavior coverage.
- Stable public interfaces with ADR-backed decisions.

## Monitoring

- Track quality regressions during review cycles.
- Use lint/test failures as immediate gates.
- Log recurring hotspots in PROGRESS for follow-up refactors.
