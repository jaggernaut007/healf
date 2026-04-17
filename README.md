# AI Package (v7 Lite)

A lean, production-ready starter for agentic coding workflows in small teams.

## What This Package Includes

- `AGENTS.md`: cross-tool instruction source of truth
- `CLAUDE.md`: tool-specific behavior via `@import AGENTS.md`
- `.github/copilot-instructions.md`: symlink to `AGENTS.md`
- `.github/instructions/`: Copilot path-scoped instruction files
- `.github/prompts/`: Copilot reusable one-shot workflows
- `.github/agents/`: Copilot specialized personas
- `.claude/rules/`: path-scoped standards
- `.claude/agents/`: planner, implementer, reviewer, research-assistant, test-writer, docs-writer
- `.claude/skills/`: `session-handoff`, `ship-it`, `triple-agent-audit`, `ui-scaffolder`
- `.claude/hooks.json` and `.claude/hooks/`: formatting and pre-commit safeguards
- `.claude/mcp.json`: MCP server baseline
- `.agents/workflows/`: Antigravity-compatible workflow docs for planner/implementer/review cycle
- `docs/`: checklist, quick reference, ADR and research templates
- `docs/`: checklist, quick reference, ADR/research templates, and strict policy docs
- `scripts/init.sh`: startup health checks with auto-detected commands

## Lite Compliance Goals

This package is optimized for startup/small-team velocity:

- Keep always-on instructions small (`AGENTS.md` < 100 lines)
- Prefer practical validation over enterprise approval bureaucracy
- Use planner for tasks with 2+ steps
- Use three-tier retrieval for external libraries: MCP docs -> research notes -> web
- Require tool-verified test outcomes before marking work complete
- Use artifact-driven execution (plan/research docs first, implementation second)

## Quick Start

1. Update project summary and stack in `AGENTS.md`.
2. Confirm `scripts/init.sh` auto-detection matches your stack.
3. Run:
   ```bash
   chmod +x scripts/init.sh .claude/hooks/*.sh
   ./scripts/init.sh
   ```
4. Start work using Wave Protocol:
   implement -> test-writer -> reviewer -> fix -> docs-writer -> commit

## Keep It Lean

Remove or archive generated summaries and one-off analysis artifacts once decisions are captured in:

- `PROGRESS.md` for tactical status
- `feature_list.json` for machine-readable state
- `docs/adr/` for architecture decisions
- `docs/research/` for external dependency decisions

## Strict Compliance Docs

- `docs/MCP-ROUTING.md`
- `docs/SECURITY-CONFIG.md`
- `docs/TESTING-STRATEGY.md`
- `docs/SPEC-DRIVEN.md`
- `docs/TASK-TEMPLATE.md`
- `docs/CODE-HEALTH.md`
- `docs/OBSERVABILITY.md`
- `docs/REVIEW-SETUP.md`
- `docs/MODEL-ROUTING.md`
- `docs/AUTO-MEMORY.md`
- `CONTRIBUTING.md`
