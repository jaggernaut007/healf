# CLAUDE.md
@import AGENTS.md

## Claude-Specific Behaviours

### Subagent Routing
- **Explore subagent**: Read-only codebase search and Q&A
- **Plan subagent**: Before implementing tasks with 2+ steps or multi-file changes
- **research-assistant**: Before using external libraries (creates research notes)
- **test-writer**: Writes comprehensive failing tests before implementation
- **code-reviewer**: Post-implementation QA (linting, security, patterns)
- **docs-writer**: Updates documentation when code changes affect architecture
- Do NOT spawn subagents for simple single-file changes

### Specialized Agent Sequence (The Wave Protocol)
After each implementation wave, run agents in sequence:
1. Implement the feature
2. Run test-writer agent → adds coverage
3. Run code-reviewer agent → checks quality/security
4. Fix any issues found
5. Run docs-writer agent → updates docs
6. Commit

### Workflow Sources
- Use `.agents/workflows/` as the workflow mirror for planner, implementer, test-writer, code-reviewer, docs-writer, research-assistant, security-auditor, and ship-it.
- Keep workflow docs synchronized with `.claude/agents/` and skills.

### Context Management
- Work in 30-minute sprints; use `/compact` at natural breakpoints
- Use `/clear` after every commit and task switch
- Use `/compact focus on X` when working on a narrow concern within broader session
- Keep context under 85% utilisation (check with `/context`)
- When context feels crowded, update PROGRESS.md before clearing
- Start fresh sessions for new features

### Hallucination Prevention
- For external libraries: check MCP docs servers first (Context7)
- Check `docs/research/` for existing research notes
- If neither covers it, spawn research-assistant agent
- Pin library versions in all research queries
- Search codebase for existing patterns before inventing new ones
- Verify packages exist in registries before adding dependencies

### Policy References
- MCP routing matrix: `docs/MCP-ROUTING.md`
- Security controls and supply-chain checks: `docs/SECURITY-CONFIG.md`
- Testing gates and completion evidence: `docs/TESTING-STRATEGY.md`

### Path-Scoped Rules
Rules in `.claude/rules/` apply automatically based on file patterns:
- `global.md` → all code files
- `python-standards.md` → Python files only
- `frontend-standards.md` → React/Next.js files only
- `testing-standards.md` → test files only

### Before Making Architectural Decisions
1. Check `docs/adr/` for existing decisions
2. If decision is new, create ADR in `docs/adr/` with sequential numbering
3. Use ADR template: Status, Context, Decision, Consequences
