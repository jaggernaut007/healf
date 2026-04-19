# Quick Reference: Healf Health Intelligence Engine

## Session Commands

| Command | When to Use |
|---------|-------------|
| `./scripts/init.sh` | Session start, before new work |
| `/clear` | After commits, task switches |
| `/compact` | At natural breakpoints (30-min sprints) |
| `/compact focus on X` | Narrow concern within broader session |
| `/context` | Check token utilization |

## Agent Routing

| Task | Agent | Access |
|------|-------|--------|
| Decompose complex feature | planner | Read-only |
| Implement one task | implementer | Write |
| Validate dependencies | research-assistant | Read-only |
| Write comprehensive tests | test-writer | Write |
| Review code quality | reviewer | Read-only |
| Update documentation | docs-writer | Write |

## The Wave Protocol

```
1. Implement → 2. Test (test-writer) → 3. Review (reviewer) →
4. Fix → 5. Document (docs-writer) → 6. Commit (ship-it)
```

## External Library Workflow

```
1. Check Context7 MCP (Tier 1)
     ↓ not found
2. Check docs/research/ (Tier 2)
     ↓ not found
3. Spawn research-assistant (Tier 3)
     ↓ creates
4. Research note in docs/research/
     ↓
5. Implementer uses research note
```

## Skills

| Skill | Triggers |
|-------|----------|
| session-handoff | "wrap up", "end of session", "orient yourself" |
| ship-it | "ship it", "deploy", "commit and push" |

## Definition of Done

- [ ] Tests pass (verified via tool call)
- [ ] Linter passes
- [ ] Docs updated if behavior changed
- [ ] PROGRESS.md updated
- [ ] E2E smoke test passes (init.sh)

## File Locations

| What | Where |
|------|-------|
| Universal rules | AGENTS.md |
| Claude-specific | CLAUDE.md |
| Path-scoped rules | .claude/rules/*.md |
| Specialized agents | .claude/agents/*.agent.md |
| Antigravity workflows | .agents/workflows/*.md |
| Skills | .claude/skills/*/SKILL.md |
| Research notes | docs/research/*.md |
| Architecture decisions | docs/adr/*.md |
| Cross-session state | PROGRESS.md |
| Init script | scripts/init.sh |

## Policy Docs

| Policy | File |
|--------|------|
| MCP routing | docs/MCP-ROUTING.md |
| Security controls | docs/SECURITY-CONFIG.md |
| Testing gates | docs/TESTING-STRATEGY.md |

## Context Budget

- AGENTS.md: <100 lines
- CLAUDE.md: Minimal (imports AGENTS.md)
- Path-scoped rules: <50 lines each
- Skills: <500 lines per SKILL.md
- Keep total context <85% utilization

## Best Practices

✅ **DO**:
- Write failing tests FIRST
- Run tests via tool call, read output
- Verify packages in registries
- Pin exact versions
- Update PROGRESS.md before `/clear`
- Check ADRs before architectural changes
- Work in 30-minute sprints

❌ **DON'T**:
- Self-report test results
- Skip package verification
- Use mock data (use real data)
- Create barrel files (use direct imports)
- Mark complete without test evidence
- Start new work on broken foundation

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Init.sh fails | Fix failures before new work |
| Tests fail | Debug, don't modify tests |
| Context >85% | Use `/compact` or `/clear` |
| Unknown library | Spawn research-assistant |
| Unclear architecture | Check docs/adr/ |
| Session continuity lost | Read PROGRESS.md + git log |

## Security Checklist

Before adding dependencies:
- [ ] Package exists in registry (prevent slopsquatting)
- [ ] CVE check (Snyk or equivalent)
- [ ] No secrets in code
- [ ] Maintenance health verified
- [ ] Transitive dependencies <20
- [ ] License compatible

## MCP Servers

| Server | Purpose |
|--------|---------|
| context7 | Version-specific library docs |
| nexus-mcp | Hybrid code intelligence |
| playwright | Browser automation, E2E tests |
| sequential-thinking | Structured problem-solving |
| fetch | Web content retrieval |

## Quick Start Checklist

New project setup:
- [ ] Copy AI Package directory
- [ ] Customize AGENTS.md (project, tech stack)
- [ ] Configure init.sh (build/test/lint)
- [ ] Add path-scoped rules (.claude/rules/)
- [ ] Make scripts executable (`chmod +x`)
- [ ] Create symlink (.github/copilot-instructions.md)
- [ ] Run init.sh to verify
- [ ] Update PROGRESS.md with current state
