# 9. Use Typer + Rich + Invoke for CLI and Task Execution

## Status
Accepted

## Context
Phase 4 requires a user-facing CLI and internal task execution workflow for enrichment runs, graph preflight/build, and orchestration flows. Existing shell scripts are functional but do not provide typed argument validation, rich terminal UX, or composable task namespaces.

Research notes were prepared for `typer`, `rich`, and `invoke`:
- `docs/research/typer-cli-framework-v0.12.3.md`
- `docs/research/rich-cli-patterns-v14.0.0.md`
- `docs/research/invoke-task-runner-v2.2.0.md`

## Decision
Adopt the following split:
- `typer` for public CLI command parsing and typed input validation.
- `rich` for terminal formatting, progress indicators, and diagnostic tables.
- `invoke` for developer task orchestration (`test`, `lint`, `preflight`, `pipeline` commands).

Implementation scope:
- Add `src/cli.py` for user-facing commands.
- Add `tasks.py` for developer workflow tasks.
- Keep `scripts/init.sh` temporarily, but allow migration to `invoke init`.

## Consequences
- Positive: Better developer and operator ergonomics with typed commands and clearer diagnostics.
- Positive: Cleaner maintenance versus ad-hoc shell command collections.
- Positive: Consistent UX for preflight/build/orchestrate operations.
- Negative: Adds three dependencies that require version pinning and periodic maintenance.
- Negative: Requires writing CLI and task-runner tests to avoid regressions.
