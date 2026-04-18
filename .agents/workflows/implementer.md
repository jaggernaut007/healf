# Implementer Workflow

Use this workflow to execute exactly one planned task.

0. Read `SPEC.md`; execute only work mapped to active phase/wave acceptance criteria.
0.1 If requested behavior is out of spec, stop and require `SPEC.md` update before edits.
1. Read the selected task from the plan artifact.
2. Write failing tests for the required behavior first.
3. Implement the smallest change to pass tests.
4. Run lint and tests; read actual outputs.
5. Update progress artifacts with verified evidence.
6. Stop and hand off to review waves.
7. Use `rg --files` and `rg -n` for repository search; fallback to `find`/`grep` only when `rg` is unavailable.
