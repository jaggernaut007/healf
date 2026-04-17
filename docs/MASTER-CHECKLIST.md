# AI Package Master Checklist

Use this checklist to verify your agentic project setup is complete.

## Agent Instruction Files

- [ ] Root AGENTS.md under 100 lines, universal rules only
- [ ] CLAUDE.md uses `@import AGENTS.md`, adds only Claude-specific behaviours
- [ ] CLAUDE.local.md in `.gitignore` (or use CLAUDE.local.md.template)
- [ ] `.github/copilot-instructions.md` symlinked to AGENTS.md
- [ ] `.github/instructions/*.instructions.md` exists with focused applyTo globs
- [ ] `.github/prompts/*.prompt.md` exists for repeatable one-shot workflows
- [ ] `.github/agents/*.agent.md` exists for specialized Copilot personas
- [ ] All negative instructions rewritten as positive directives
- [ ] `.claude/rules/` directory exists with path-scoped rules
- [ ] Each rule file has YAML frontmatter with `paths:` (not `globs:`)
- [ ] Each rule file under 50 lines

### Path-Scoped Rules Checklist
- [ ] global.md (universal standards)
- [ ] Language-specific rules (python-standards.md, frontend-standards.md, etc.)
- [ ] testing-standards.md (test requirements)
- [ ] Rules apply automatically based on file patterns

## Project Structure

- [ ] Flat package structure navigable in under 2 minutes
- [ ] Tests, types, docs colocated with implementation
- [ ] No barrel files — direct import paths only
- [ ] README.md at root with project overview
- [ ] README.md at each significant directory
- [ ] CONTRIBUTING.md as pattern source of truth (if applicable)

## Specialized Agents

- [ ] `.claude/agents/` directory exists
- [ ] planner.agent.md (read-only, task decomposition, 50-min horizon)
- [ ] implementer.agent.md (write access, TDD workflow)
- [ ] reviewer.agent.md (high signal-to-noise, security focus)
- [ ] research-assistant.agent.md (dependency validation, read-only)
- [ ] test-writer.agent.md (comprehensive testing, failing tests first)
- [ ] docs-writer.agent.md (documentation sync, ADRs)
- [ ] security-auditor.agent.md (dependency/CVE and security regression checks)

### Agent Configuration Checklist
- [ ] Each agent has YAML frontmatter with name and description
- [ ] Descriptions are keyword-rich for activation
- [ ] Agent roles clearly defined (read-only vs write access)
- [ ] Tool lists appropriate for each agent's role

## Skills

- [ ] `.claude/skills/` directory exists
- [ ] session-handoff skill with dual mode (start/end session)
- [ ] ship-it skill with 7-step pipeline
- [ ] triple-agent-audit skill with test -> review -> docs waves
- [ ] ui-scaffolder skill for repeatable responsive UI scaffolding
- [ ] Each SKILL.md has keyword-rich description in YAML frontmatter
- [ ] SKILL.md bodies under 500 lines
- [ ] Skills verify prerequisites before running

### Skill Features Checklist
- [ ] session-handoff reads PROGRESS.md + auto-memory + git log
- [ ] session-handoff updates PROGRESS.md at session end
- [ ] ship-it runs pre-flight (init.sh) before proceeding
- [ ] ship-it enforces Definition of Done
- [ ] ship-it supports selective execution ("just commit", "commit and push")

## Context Management

- [ ] PROGRESS.md exists with current project state
- [ ] feature_list.json (or equivalent) for feature status
- [ ] Documentation instructs `/clear` after every commit
- [ ] Documentation instructs `/compact` at natural breakpoints
- [ ] Context budget documented (AGENTS.md <100 lines, rules <50 lines)
- [ ] Session-handoff skill installed and tested

### Context Management Practices
- [ ] Work in 30-minute sprints documented
- [ ] Loop intelligence pattern documented (PROGRESS + memory + git log)
- [ ] `/compact focus on X` pattern documented
- [ ] Context utilization target <85%

## Hallucination Prevention

- [ ] `docs/research/` directory exists
- [ ] RESEARCH-TEMPLATE.md in docs/research/
- [ ] Three-tier retrieval pattern documented (MCP → research → web)
- [ ] Package verification workflow documented
- [ ] Research template includes security assessment
- [ ] research-assistant agent configured

### Research Workflow Checklist
- [ ] External library usage triggers research-assistant
- [ ] Research notes include "What We Ruled Out"
- [ ] Package registry verification documented
- [ ] Version pinning enforced in research notes
- [ ] CVE checks included in research template

## MCP Server Integration

- [ ] `.claude/mcp.json` exists
- [ ] context7 configured (version-specific library docs)
- [ ] nexus-mcp configured (hybrid code intelligence)
- [ ] playwright configured (browser automation)
- [ ] chrome-devtools configured (live browser debugging)
- [ ] memstate-ai configured (persistent memory MCP)
- [ ] sequential-thinking configured (structured reasoning)
- [ ] fetch configured (web content retrieval)
- [ ] All MCP servers have descriptions

## Antigravity Compliance

- [ ] Artifact-first workflow documented (plan/research before implementation)
- [ ] `.agents/workflows/` contains planner, implementer, code-reviewer, test-writer, docs-writer, research-assistant, security-auditor, and ship-it workflows
- [ ] Planner -> Implementer -> Triple Agent Audit pipeline documented
- [ ] Significant changes require Triple Agent Audit before release
- [ ] Task decomposition enforced for 30-50 minute horizons

### MCP Usage Checklist
- [ ] Agents configured to use appropriate MCP tools
- [ ] Three-tier retrieval uses context7 as Tier 1
- [ ] research-assistant uses MCP docs servers
- [ ] E2E tests can use playwright
- [ ] Code search uses nexus-mcp

## Testing Strategy

- [ ] Testing tools installed (pytest, jest, etc.)
- [ ] test-writer agent configured
- [ ] TDD workflow documented (failing tests first)
- [ ] Definition of Done includes test verification
- [ ] Coverage targets documented (80%+ business logic, 100% critical paths)
- [ ] init.sh runs test suite

### Testing Practices Checklist
- [ ] Tests written BEFORE implementation
- [ ] Tests run via tool call (never self-report)
- [ ] Test output read to verify pass
- [ ] Unit tests <5s feedback
- [ ] E2E tests in CI before merge
- [ ] Testing standards in path-scoped rules

## Hooks and Automation

- [ ] `.claude/hooks.json` exists
- [ ] `.claude/hooks/` directory exists
- [ ] format-file.sh (PostToolUse hook)
- [ ] pre-commit.sh (PreToolUse hook)
- [ ] Stop hook runs init.sh before completion
- [ ] All hook scripts executable (`chmod +x`)

### Hooks Configuration Checklist
- [ ] PostToolUse: Auto-format files after Edit|Write
- [ ] PreToolUse: Pre-commit validation for git commits
- [ ] Stop hook: Runs init.sh before task completion
- [ ] Hooks fail gracefully for optional checks
- [ ] Hook scripts tested and working

## Documentation Architecture

- [ ] `docs/` directory exists
- [ ] `docs/adr/` directory for Architecture Decision Records
- [ ] ADR template file (see docs/adr/template.md or guide)
- [ ] llms.txt at documentation root
- [ ] docs-writer agent configured
- [ ] QUICK-REFERENCE.md created

### Documentation Standards Checklist
- [ ] ADRs created for architectural decisions
- [ ] ADRs sequentially numbered (ADR-001, ADR-002, etc.)
- [ ] llms.txt organized with links
- [ ] READMEs at significant directories
- [ ] Documentation updates in Definition of Done

## Initialization Script

- [ ] `scripts/init.sh` exists
- [ ] init.sh executable (`chmod +x`)
- [ ] Environment checks (Python, Node, etc.)
- [ ] Dependency checks
- [ ] Linter check
- [ ] Test suite run
- [ ] Clear pass/warn/fail indicators
- [ ] Graceful degradation for optional checks

### init.sh Features Checklist
- [ ] Returns exit code 0 for success
- [ ] Returns exit code 1 for failures
- [ ] Warns for optional missing components
- [ ] Runs at session start (documented)
- [ ] Runs in ship-it pre-flight
- [ ] Runs in Stop hook before completion

## Session Workflow

- [ ] Session start protocol documented
- [ ] Session end protocol documented
- [ ] Definition of Done clearly defined
- [ ] Wave Protocol documented (implement → test → review → fix → docs → commit)
- [ ] Three-tier retrieval pattern documented
- [ ] Agent routing guidelines documented

### Workflow Practices Checklist
- [ ] Read PROGRESS.md at session start
- [ ] Run init.sh before new work
- [ ] Check docs/adr/ before architectural decisions
- [ ] Use session-handoff at session end
- [ ] Update PROGRESS.md before /clear
- [ ] Descriptive git commit messages

## Security

- [ ] Package verification workflow documented
- [ ] Security assessment in research template
- [ ] No secrets in AGENTS.md or CLAUDE.md
- [ ] CLAUDE.local.md in .gitignore
- [ ] Security checklist in code-reviewer agent
- [ ] Slopsquatting prevention documented

### Security Practices Checklist
- [ ] CVE checks for new dependencies
- [ ] Package registry verification
- [ ] Transitive dependency limits (<20)
- [ ] No secrets in code (enforced)
- [ ] Security scan budget documented (if using free tier)
- [ ] Input validation standards in path-scoped rules

## Git Integration

- [ ] .gitignore includes CLAUDE.local.md
- [ ] .gitignore includes sensitive files
- [ ] Copilot commit trailer configured
- [ ] Git commit message standards documented
- [ ] pre-commit hook configured
- [ ] All agent configs version-controlled

### Git Practices Checklist
- [ ] Descriptive commit messages
- [ ] Commit messages serve as session history
- [ ] Co-authored-by trailer for agent commits
- [ ] /clear after every commit
- [ ] Git log read at session start

## Cross-Tool Compatibility

- [ ] AGENTS.md as cross-tool source of truth
- [ ] .github/copilot-instructions.md symlink to AGENTS.md
- [ ] CLAUDE.md imports AGENTS.md
- [ ] Universal rules in AGENTS.md (<100 lines)
- [ ] Tool-specific rules in respective files

### Compatibility Checklist
- [ ] Works with Claude Code
- [ ] Works with GitHub Copilot
- [ ] Works with Cursor (via AGENTS.md)
- [ ] No tool-specific syntax in AGENTS.md
- [ ] Plain Markdown only in AGENTS.md

## Final Verification

- [ ] Run `./scripts/init.sh` — should pass
- [ ] AGENTS.md word count <100 lines
- [ ] All hook scripts executable
- [ ] All symlinks working
- [ ] PROGRESS.md reflects current state
- [ ] README.md complete and accurate
- [ ] QUICK-REFERENCE.md available
- [ ] All agents tested in fresh session

## Optional Enhancements

- [ ] Custom agents for project-specific workflows
- [ ] Additional skills for common tasks
- [ ] Project-specific path-scoped rules
- [ ] MkDocs for documentation site
- [ ] CI/CD integration
- [ ] Observability proxy (Langfuse, Braintrust)
- [ ] Additional MCP servers for project needs

---

## Scoring

Count your checkmarks:

- **90-100% complete**: Production-ready ✅
- **70-89% complete**: Good foundation, continue hardening 🔄
- **50-69% complete**: Core elements present, needs work ⚠️
- **<50% complete**: Start with Quick Start section in README 🚀

## Quick Fixes

If you're missing critical items:

1. **No AGENTS.md**: Copy from template, customize for your project
2. **No init.sh**: Copy from template, add your build/test commands
3. **No path-scoped rules**: Start with global.md, add language-specific later
4. **No agents**: Use default agents (explore, plan, code-review) until custom ones needed
5. **No skills**: session-handoff and ship-it are highest priority

## Resources

- Quick reference: `docs/QUICK-REFERENCE.md`
- Research workflow: `docs/research/README.md`
- Research template: `docs/research/RESEARCH-TEMPLATE.md`
- README: `README.md`
