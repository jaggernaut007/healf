# Docs Writer Workflow

Use this workflow for Wave 5 in Triple Agent Audit.

0. Read `SPEC.md` and documentation scope for active phase/wave.
0.1 If docs, ADRs, or research artifacts are not aligned with spec, return BLOCK.
1. Identify behavior, API, and architecture changes.
2. Sync docs, llms.txt references, and PROGRESS artifacts.
3. Ensure terminology and commands match implementation.
4. Flag stale docs and unresolved assumptions.
5. Return SHIP, ITERATE, or BLOCK.
6. Use `rg --files` and `rg -n` for documentation impact search; fallback to `find`/`grep` only if `rg` is unavailable.
