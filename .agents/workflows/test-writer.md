# Test Writer Workflow

Use this workflow for Wave 3 in Triple Agent Audit.

0. Read `SPEC.md` and derive tests from active phase/wave acceptance criteria.
0.1 If criteria are missing or ambiguous, return BLOCK until `SPEC.md` is updated.
1. Translate acceptance criteria into failing tests.
2. Add happy-path, boundary, and failure-path coverage.
3. Add resilience checks for 4xx/5xx and invalid input.
4. Keep tests deterministic and independent.
5. Run tests and report SHIP, ITERATE, or BLOCK.
6. Use `rg --files` and `rg -n` for test impact search; fallback to `find`/`grep` only if `rg` is unavailable.
