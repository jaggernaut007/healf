---
name: triple-agent-audit
description: >
  Run Wave 3-5 quality gates: test, review, and documentation passes.
  Use when user asks for audit, hardening, PR readiness, or production quality check.
---

# Triple Agent Audit

Run three distinct passes after implementation.

## Spec Conformance Gate

- All three waves must validate against `SPEC.md` acceptance criteria.
- Any wave finding that indicates out-of-spec behavior is a BLOCK until `SPEC.md` or implementation is corrected.

## Wave 3: Tester
- Validate happy path, edge cases, and resilience failures.
- Verify test commands and read actual output.
- Verdict: SHIP | ITERATE | BLOCK

## Wave 4: Reviewer
- Validate logic, regressions, architecture consistency, and security-sensitive paths.
- Verify impacted callers/callees where applicable.
- Verdict: SHIP | ITERATE | BLOCK

## Wave 5: Docs Writer
- Sync behavior changes to docs, llms.txt, and PROGRESS.md.
- Ensure docs reflect current implementation.
- Verdict: SHIP | ITERATE | BLOCK

## Completion Rule
A feature is release-ready only when all three waves produce SHIP.
