 # Phase 4 Execution Plan: CLI and UX

Status: Active
Last Updated: 2026-04-18

## Objective
Deliver operator-facing CLI/task-runner workflows for enrichment, graph build, and orchestration with repeatable local/CI execution and test coverage.

## Scope
1. Unified CLI entrypoint for core operations.
2. Task-runner commands for repeatable workflows.
3. Structured human-readable outputs for operators.
4. CLI/task-runner tests and smoke verification.

## Deliverables
1. CLI entrypoint with subcommands:
- enrichment run
- graph build
- orchestration run
2. Task-runner definitions for:
- test
- lint/check
- smoke flow
3. CLI integration tests covering success and failure paths.
4. Documentation updates in README/PROGRESS/tracking artifacts.

## Acceptance Checks
1. Commands execute successfully with expected structured output.
2. Invalid command inputs fail with clear errors and non-zero exit status.
3. Task-runner commands are deterministic in local and CI-like environments.
4. Tests pass with tool-verified evidence.

## Verification Commands
- ./scripts/init.sh
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q
- CLI integration test command (to be added with implementation)

## Evidence Updates Required
- PROGRESS.md
- feature_list.json
- todo.md

## Non-Goals
- Orchestrator control-flow redesign (completed in Phase 3).
- New external dependency additions outside approved ADR scope.
