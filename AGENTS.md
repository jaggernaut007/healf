# AGENTS.md
Role: Output ultra-dense text. Sacrifice grammar for token efficiency. Preserve meaning/value. Omit pleasantries/fluff.

## Project Overview
AI Package Template — A production-ready agentic development framework for IDE coding agents.

## Tech Stack
- Python (FastAPI, LlamaIndex, LangGraph)
- uv (Python Package Manager - ALWAYS use `uv` instead of `pip` or `python -m venv`)
- Neo4j AuraDB (Knowledge Graph)
- Claude Code / GitHub Copilot (Primary agents)

## Build & Test Commands
# Run `./scripts/init.sh` to initialize and verify environment
# Run `uv pip install -r requirements.txt` to install dependencies
# Run `PYTHONPATH=. pytest tests/` to manually test

## Code Standards
- Write concise, professional comments (not verbose explanations)
- Use only real-world data from the database (never mock data)
- Apply all fixes to existing files (create new files only when explicitly required)
- Use direct import paths (never barrel files/index re-exports)
- Use Pydantic models for all Python request/response schemas
- Raise HTTPException with correct status codes in API code
- Keep functions under 50 lines; split larger ones into helpers

## Before Using External Libraries
1. Check MCP docs server (Context7) for version-specific docs
2. Check `docs/research/` for existing research notes
3. If neither covers it, create research note using `docs/research/RESEARCH-TEMPLATE.md`
4. Verify package exists in registry (npm, PyPI) to prevent slopsquatting
5. Pin exact versions in all research and dependencies

## Testing Requirements
- All new features require tests BEFORE marking complete
- Write failing tests first, then implement until they pass
- Run tests via tool call and read output to verify pass (never self-report)
- Unit tests for business logic; Integration tests for API endpoints; E2E for critical workflows
- Aim for 80%+ coverage on business logic, 100% on critical paths

## Definition of Done
1. Tests pass (verified via tool call)  2. Linter passes  3. Docs updated if behavior changed
4. PROGRESS.md updated with what was done  5. E2E smoke test passes (./scripts/init.sh)

## Antigravity Operating Rules
1. Artifact-first execution: produce plan/research artifacts before multi-file implementation
2. Use role-isolated agents: planner -> implementer -> test/review/docs waves
3. Keep tasks in the 30-50 minute horizon with explicit dependencies
4. Run Triple Agent Audit for significant changes before release
5. Treat skills and agents as code: versioned, concise, and tool-verified

## Workflow and Policy Sources
- Antigravity workflows live in `.agents/workflows/`
- MCP routing policy: `docs/MCP-ROUTING.md`
- Security guardrails: `docs/SECURITY-CONFIG.md`
- Testing policy: `docs/TESTING-STRATEGY.md`

## Session Start Protocol
1. Read PROGRESS.md for current project state
2. Run ./scripts/init.sh to verify the app is in a working state
3. Fix any broken state BEFORE starting new work
4. Check `docs/adr/` for relevant architectural decisions
