# Research Assistant Workflow

Use this workflow before adding dependencies or external APIs.

0. Read `SPEC.md` and confirm dependency/API work is in active phase/wave scope.
0.1 If out of scope, return BLOCK pending `SPEC.md` update.
1. Query MCP docs first for version-specific guidance.
2. Check docs/research for an existing note.
3. Verify package existence in public registry.
4. Record the chosen version, approach, and rejected options.
5. Produce a research artifact before implementation begins.
6. Use `rg --files` and `rg -n` for codebase search; fallback to `find`/`grep` only if `rg` is unavailable.
