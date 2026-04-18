# Planner Workflow

Use this workflow for read-only planning before implementation.

0. Read `SPEC.md` and map requested work to phase/wave acceptance criteria.
0.1 If no matching criteria exist, return BLOCK and request `SPEC.md` update.
1. Read the request, acceptance criteria, and any ADR constraints.
2. Search the codebase for existing patterns and impacted boundaries.
3. Decompose work into verifiable 30-50 minute tasks.
4. Produce a task DAG with dependencies and risks.
5. Define files likely modified and out-of-scope areas.
6. Hand off one task at a time to implementer.
7. Use `rg --files` and `rg -n` by default; use `find`/`grep` only if `rg` is unavailable.
