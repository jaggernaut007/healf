# Code Reviewer Workflow

Use this workflow after implementation and test updates.

0. Read `SPEC.md` and review changed behavior against phase/wave acceptance criteria.
0.1 If behavior deviates from spec, return BLOCK with required spec update.
1. Inspect changed files and expected behavior.
2. Validate bugs, regressions, security, and compatibility risks.
3. Verify caller/callee impact for changed symbols.
4. Confirm tests/lint were actually run and passed.
5. Return SHIP, ITERATE, or BLOCK with concrete findings.
6. Use `rg --files` and `rg -n` for impact discovery; fallback to `find`/`grep` only if `rg` is unavailable.
