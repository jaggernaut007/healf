# Ship-It Workflow

Use this workflow to release safely.

0. Read `SPEC.md` and verify release scope satisfies phase/wave acceptance criteria.
0.1 If implementation or docs diverge from `SPEC.md`, return BLOCK and do not release.
1. Run preflight checks with scripts/init.sh.
2. Verify Definition of Done with real test/lint evidence.
3. Confirm docs and progress artifacts are synchronized.
4. Commit with a clear message.
5. Push only with explicit confirmation.
6. Deploy only with explicit confirmation and health checks.
7. Use `rg --files` and `rg -n` for release-impact search; fallback to `find`/`grep` only if `rg` is unavailable.
