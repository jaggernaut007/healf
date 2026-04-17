# Agentic Coding: An Operational Playbook for IDE Coding Agents
## v7.0 Lite Edition — For Startups, Small Teams & Individual Developers

**For IDE coding agents: Claude Code, Cursor, GitHub Copilot, Codex CLI, Gemini CLI, Windsurf**
**Feed this document to your agent at the start of any project.**

---

## What's New in v7.0 Lite

This version incorporates 2026 paradigm shifts and multi-framework best practices without enterprise overhead:

**New Insights Added**:
- 🚀 Multi-framework patterns (LangGraph, CrewAI, AutoGen) simplified for solo/small teams
- 🎯 ADLC (Agentic Development Life Cycle) - modern workflow for the AI-native era
- 🛡️ Lightweight risk awareness (no approval bureaucracy, just smart defaults)
- 🔌 MCP best practices (security-conscious without governance overhead)
- 📊 2026 benchmarks: 3x acceleration, 45% faster resolution, 60% higher accuracy

**What We Skipped** (Enterprise v7.0 only):
- ❌ Formal approval workflows (you're moving fast, not red tape)
- ❌ Multi-person review gates (trust your judgment)
- ❌ Audit logging (unless you want it)
- ❌ Compliance documentation (GDPR, SOC 2, etc.)

**Perfect for**: Startups, indie developers, small teams (1-10 people), side projects, MVPs, rapid prototyping

---

## How to Use This Guide

This is an operational playbook. Read it at session start and apply each practice to optimize your development workflow.

1. Read this document at the start of a new project or when onboarding to an existing one
2. Check which practices are already configured — does AGENTS.md exist? hooks.json? MCP servers?
3. For any missing practice, create the files and configuration described in that section
4. Follow the Session Workflow (after Section 15) for every working session
5. Use the Master Checklist (end of document) as a periodic audit

When this guide says "agent," it means your IDE coding agent and its subagents — not standalone autonomous systems, chatbots, or agent frameworks. All practices assume a developer is present, supervising, and iterating in real-time via their IDE or terminal.

Every recommendation below is grounded in empirical findings: Anthropic's engineering research, CodeScene's peer-reviewed studies (January 2026), the Linux Foundation AGENTS.md specification, METR task-horizon research, and real-world practitioner reports from teams shipping 20+ agent-authored PRs per day.

### The 2026 Paradigm Shift

**Code scarcity → Thinking scarcity**: The bottleneck is no longer syntax generation — it's specification clarity. Invest in better problem definitions, not faster typing.

**Assistants → Collaborators**: Agents are moving from autocomplete tools to autonomous team members. They need state management, testing frameworks, and clear workflows.

**Single agent → Multi-agent**: Distributed cognitive load prevents context overload. One agent plans, another implements, a third reviews.

**Traditional SDLC → ADLC**: Intent → Plan → Parallel Execute → Validate → Deploy. Faster, more autonomous, continuously validated.

## GitHub Copilot Instruction Architecture (Practical)

Use this operating model when the primary execution surface is GitHub Copilot (VS Code, GitHub.com coding agent, or Copilot CLI).

### Copilot Instruction Layers

1. **Cross-tool source of truth**: `AGENTS.md` in repository root.
2. **Copilot repository-wide entrypoint**: `.github/copilot-instructions.md`.
3. **Path-scoped rules**: `.github/instructions/*.instructions.md` with `applyTo` globs.
4. **Reusable one-shot workflows**: `.github/prompts/*.prompt.md`.
5. **Specialized personas and tool boundaries**: `.github/agents/*.agent.md`.

This separation keeps always-on context small, while shifting task-specific behavior into modular files.

### Copilot-First Design Rules

- Keep repository-wide instructions concise and non-conflicting.
- Put language and subsystem rules in path-scoped instruction files.
- Keep repeatable workflows in prompt files, not in always-on instructions.
- Use custom agents only for distinct roles (for example planner vs reviewer).
- Treat coding-agent pull requests as teammate PRs: batch review comments, request a new agent iteration, and verify with tests before merge.
- Confirm instruction usage through references or diagnostics whenever behavior diverges from expectations.

### Repository Baseline Template (Copilot)

```text
AGENTS.md
.github/copilot-instructions.md
.github/instructions/
  python.instructions.md
  tests.instructions.md
  web.instructions.md
.github/prompts/
  pr-ready.prompt.md
  new-connector.prompt.md
.github/agents/
  planner.agent.md
  code-reviewer.agent.md
```

---

## 1. The Agent Memory Layer: AGENTS.md, CLAUDE.md, and Instruction Architecture

The single highest-leverage file in any project is the agent instruction file. It is the project's permanent brain — loaded into every session, shaping every decision.

### Three Files, Three Purposes

**AGENTS.md** is the universal, cross-tool standard donated to the Linux Foundation's Agentic AI Foundation (AAIF) in December 2025. Co-founded by OpenAI, Anthropic, and Block, it is supported by 20+ tools including Claude Code, GitHub Copilot, Cursor, Codex, VS Code, Gemini CLI, Windsurf, RooCode, Devin, and Aider. Over 60,000 open-source projects have adopted it. The format is plain Markdown with no required fields, no YAML frontmatter, and no special syntax.

Since most teams use multiple IDE agents, AGENTS.md is the cross-tool bridge — the one file every tool reads natively.

**CLAUDE.md** is Claude Code's tool-specific instruction file with `@import` support (recursive up to 5 levels deep), path-scoped rules via `.claude/rules/`, and tight integration with Claude Code's auto-memory system. Critical caveat: Claude Code wraps CLAUDE.md content in a `<system-reminder>` tag that tells the model to ignore content not relevant to the current task. Bloated, unfocused files actively degrade performance.

**CLAUDE.local.md** handles personal, machine-specific overrides — sandbox URLs, debugging preferences, environment-specific configuration. Add it to `.gitignore` so it never enters version control.

### Your AGENTS.md Template

Keep AGENTS.md under 100 lines with only universal rules:

```markdown
# AGENTS.md
Role: Output ultra-dense text. Sacrifice grammar for token efficiency. Preserve meaning/value. Omit pleasantries/fluff.

## Project Overview
[Project name] — [one sentence: what it does + primary tech stack].

## Tech Stack
- Language / Framework / Database / Testing / Docs

## Build & Test Commands
# Install / Dev server / Run all tests / Lint / Build docs

## Code Standards
- [Positive instructions: describe what TO do]

## Testing Requirements
- All new features require tests before marking complete
- Do not mark a task complete until you have seen the test pass with your own tool calls

## Definition of Done
1. Tests pass  2. Linter passes  3. Docs updated if behaviour changed
4. PROGRESS.md updated  5. E2E smoke test passes (run ./scripts/init.sh)

## Session Start Protocol
1. Read PROGRESS.md for current project state
2. Run ./scripts/init.sh to verify the app is in a working state
3. Fix any broken state BEFORE starting new work
```

Your **CLAUDE.md** uses `@import AGENTS.md` to avoid duplication, then adds only Claude Code-specific behaviours:

```markdown
# CLAUDE.md
@import AGENTS.md

## Claude-Specific Behaviours
### Subagent Routing
- Use the Explore subagent for read-only codebase search
- Use the Plan subagent before implementing anything non-trivial
- Do NOT spawn subagents for simple single-file changes

### Context Management
- When context feels crowded, stop and write a summary to PROGRESS.md
- Start fresh sessions for new features
- If uncertain about a past decision, check docs/adr/ before guessing

### Hallucination Prevention
- For any external library or API, check MCP docs servers first (e.g. Context7)
- If MCP doesn't cover it, check docs/research/ for an existing research note
- If no research note exists, perform a web search for current official docs
- Pin library versions in all research queries
```

Your **CLAUDE.local.md** (personal, never committed):
```markdown
# CLAUDE.local.md
## Local Environment
# Local dev URL: http://localhost:3000
# My local MkDocs preview: http://127.0.0.1:8000
```

### The Instruction Budget Problem

Claude Code's built-in system prompt contains approximately 50 individual instructions consuming ~20K tokens before your CLAUDE.md even loads. Frontier LLMs can reliably follow roughly 150-200 instructions total — the system prompt already consumes nearly a third of available capacity.

Adherence data:
- Files under 200 lines: **92%+ instruction adherence**
- Files over 400 lines: **71% instruction adherence**
- HumanLayer's production CLAUDE.md: under 60 lines

Keep AGENTS.md under 100 lines. Use `@import` in CLAUDE.md to avoid bloating.

### The Negative Instruction Problem

Rewrite every "don't" into a "do." Models perform positive selection (choosing what token comes next), not explicit avoidance. "Don't use mock data" forces processing of the concept of mock data, increasing the probability of that behaviour.

- "Don't use mock data" → "Use only real-world data from the database"
- "Never create new files for fixes" → "Apply all fixes to existing files"
- "Avoid verbose comments" → "Write concise, professional comments"

### Hierarchical Loading for Monorepos

Claude Code loads instruction files via two mechanisms. **Ancestor loading** walks upward from the current working directory at startup, loading every CLAUDE.md found. **Descendant loading** is lazy — CLAUDE.md files in subdirectories load only when the agent reads files in those directories.

```
project-root/
├── CLAUDE.md                  # Loaded at startup — universal rules
├── AGENTS.md                  # Cross-tool compatibility
├── .claude/
│   └── rules/
│       └── api-standards.md   # Path-scoped YAML frontmatter
├── frontend/
│   └── CLAUDE.md              # Lazy-loaded when working on frontend
├── backend/
│   └── CLAUDE.md              # Lazy-loaded when working on backend
└── shared/
    └── CLAUDE.md              # Lazy-loaded when working on shared code
```

Place an instruction file near each significant code boundary. OpenAI's main repository contains 88 AGENTS.md files — one near each boundary.

**Subdirectory CLAUDE.md** files should cover domain-specific context that the root file cannot: pipeline architecture, service file purposes, model routing, key patterns for that subsystem. Keep them lean (under 50 lines) and focused on what the agent needs to know when editing files in that directory.

**Path-scoped rules** in `.claude/rules/` apply to specific file patterns via YAML frontmatter:
```yaml
---
description: API standards for backend and frontend Python
paths:
  - "frontend/**/*.py"
  - "backend/**/*.py"
---
# API Standards
- Use Pydantic models for all request/response schemas
- Raise HTTPException with correct status codes
- All external API calls go through backend/services/
```

Use `paths:` (not `globs:` — unsupported). Keep each rule file under 50 lines. Good candidates for rules: code quality thresholds (max function length, complexity limits), API standards, testing conventions.

### Auto-Memory System

Claude Code maintains a persistent file-based memory at `~/.claude/projects/<path>/memory/`. This survives across conversations and is automatically loaded at session start. Four memory types:

- **user** — role, goals, preferences, knowledge level
- **feedback** — corrections and guidance ("don't mock the database — we got burned by divergent mocks")
- **project** — ongoing work, decisions, deadlines (convert relative dates to absolute)
- **reference** — pointers to external systems (Linear projects, Grafana dashboards, Slack channels)

An index file `MEMORY.md` links to individual memory files. Use auto-memory for **strategic knowledge** (what you learned, key numbers, architectural decisions). Use PROGRESS.md for **tactical state** (what is in progress right now). Review and curate auto-memory monthly — stale entries waste instruction budget.

### Symlink Strategy for Cross-Tool Compatibility

Keep AGENTS.md as the single source of truth with symlinks:

```bash
ln -sfn AGENTS.md .github/copilot-instructions.md
# CLAUDE.md imports AGENTS.md via @import (no symlink needed)
```

For teams adding Cursor or other tools later, `npx rule-porter --to agents-md` converts between formats.

### Section Checklist

- [ ] Root AGENTS.md under 100 lines with only universal rules
- [ ] CLAUDE.md uses `@import AGENTS.md` and adds only Claude-specific behaviours
- [ ] CLAUDE.local.md in `.gitignore` with personal overrides
- [ ] All negative instructions rewritten as positive directives
- [ ] `.github/copilot-instructions.md` symlinked to AGENTS.md
- [ ] Subdirectory instruction files for each major code boundary
- [ ] `.claude/rules/` directory with path-scoped rules using YAML frontmatter
- [ ] Auto-memory reviewed and curated monthly

---

## 2. Project Structure for AI Navigation

When navigating a codebase, systematically read files, trace imports, and map dependencies. Minimize token consumption at every step.

### The Package Explosion Problem

Prefer flat, colocated structures. If you encounter 10+ packages in a monorepo, map dependencies before writing code — navigating 15 micro-packages can waste 5+ minutes of context just mapping dependencies. The same functionality in 3 well-structured packages is understood in minutes.

```
# Preferred: flat, colocated
src/
├── auth/
│   ├── auth.service.ts
│   ├── auth.service.test.ts
│   ├── auth.types.ts
│   └── README.md
├── billing/
│   ├── billing.service.ts
│   ├── billing.service.test.ts
│   └── billing.types.ts
└── CLAUDE.md
```

### Barrel Files Destroy Traceability

Never use barrel files (`index.ts` re-exports). They create indirection that wastes tokens tracing through extra layers. Use direct imports: `from './auth/auth.service'` not `from './auth'`. Atlassian reported 75% faster builds after removing barrel files.

### Code Health as AI-Readiness Metric

Before applying agent-driven development to a module, measure its code health. CodeScene's peer-reviewed research (January 2026): AI-generated code in unhealthy codebases increases defect risk by at least 30%. Target **Code Health score 9.5+** (on CodeScene's 1-10 scale). Healthy code delivers 2x faster development, 15x fewer defects, and 9x more predictable delivery.

### Code Intelligence Tools

Standard lexical search (grep, ripgrep) consumes 108-117K tokens for iterative codebase navigation. Use code intelligence tools to reduce this by 10-100x:

**Hybrid code intelligence** (unified): Modern MCP servers like Nexus-MCP combine vector search (semantic), BM25 (keyword), and graph analysis (structural) into a single hybrid pipeline with Reciprocal Rank Fusion. Query "how does authentication work?" and receive relevant code chunks fused from all three engines, re-ranked for precision. This eliminates the need for separate semantic and structural tools. Knowledge graph approaches reduce hallucination by 40-60% by providing structural context alongside code.

**Key capabilities in a unified server**: `search` for hybrid discovery, `find_callers`/`find_callees` for call graphs, `impact` for transitive change analysis, `explain` for combined understanding, `analyze` for complexity/quality metrics, `architecture` for project overview, `remember`/`recall` for persistent memory across sessions. Token-budgeted responses (summary/detailed/full) keep context lean.

**Usage pattern**: Use hybrid search first for discovery ("find code related to rate limiting"), then structural tools for impact assessment (`impact`, `find_callers`). Use `explain` when you need combined graph+vector understanding in one call. Configure as an MCP server (see Section 5) and add to subagent tool lists.

### Section Checklist

- [ ] Package structure flat enough to map dependencies in under 2 minutes
- [ ] Tests, types, and documentation colocated with implementation code
- [ ] No barrel files — all imports use direct paths
- [ ] Code Health score measured and maintained at 9.5+
- [ ] README.md at root and each significant directory
- [ ] CONTRIBUTING.md as single source of truth for coding patterns
- [ ] Code intelligence tools configured for semantic and structural search
- [ ] Subagents have code search tools in their tool lists

---

## 3. Context Management: The Central Constraint

Most best practices are based on one constraint: the context window fills up fast, and performance degrades as it fills.

### Within-Session Context Rot

Claude Code's standard context window is 200K tokens, with ~20K consumed by system prompt and tools before your conversation begins. Auto-compaction triggers at approximately 95% utilisation.

Performance degradation is non-linear:
- At 70% utilisation: precision begins degrading
- At 80-100%: degradation accelerates sharply
- Opus 4.6 suffers a 17-point accuracy drop using the full 1M window (93% → 76%)

**Work in 30-minute sprints.** Sessions under 80K tokens stay below compaction. 2-hour sessions hit 2-3 compactions with progressive quality dilution.

Key commands:
- `/context` — reveals current token breakdown
- `/clear` — wipes conversation history (use after every commit)
- `/compact` — summarises and replaces history (use at natural breakpoints)
- `/compact focus on the API changes` — directed compaction preserving specific context

### Directed Compaction

Use `/compact focus on X` when working on a narrow concern within a broader session. This preserves the specific context thread you need while compressing everything else. Example: `/compact focus on the authentication middleware changes` retains auth context while compressing unrelated exploration. This is more effective than full `/compact` when you need to maintain continuity on one topic.

### Cross-Session State: The PROGRESS.md Pattern

Every new session starts with a blank context window. Maintain a PROGRESS.md file with current status, what's working, what's in progress, what's blocked, next steps, and recent decisions. Update it before every `/clear` and at session end.

Store feature/task state in JSON format (e.g. `feature_list.json`) — agents are less likely to inappropriately change or overwrite JSON files than Markdown. Keep PROGRESS.md for narrative state.

### Session Handoff as a Skill

Implement a `session-handoff` skill (`.claude/skills/session-handoff/SKILL.md`) that triggers on "wrap up", "end of session", "save progress", "what's the current state", or "orient yourself." At session end, it writes structured state to PROGRESS.md. At session start, it reads PROGRESS.md and runs `init.sh` to verify state matches documentation. Key rule: **never mark a feature complete in PROGRESS.md without having seen a test pass via tool call.**

### Loop Intelligence: Iterative Improvement Across Sessions

Each session should start with strictly more knowledge than the previous one. The pattern compounds:
- **PROGRESS.md** provides tactical state (what is in progress now)
- **Auto-memory** provides strategic knowledge (what you learned, key decisions, user preferences)
- **Git log** provides implementation history (what changed, when, why)

Read all three at session start. Write back to PROGRESS.md and auto-memory at session end. This creates a ratchet — knowledge accumulates, mistakes are not repeated.

### The Initialiser Pattern

1. At project start, create `init.sh`, `feature_list.json`, PROGRESS.md, and make an initial commit
2. Each coding session: read git log + progress → pick one feature → implement → test end-to-end → commit → update progress

Configure `init.sh` with your actual build/test/lint commands. An `init.sh` that only echoes "OK" provides zero protection. The agent should fix any failures before starting new work.

### Subagents as Context Isolation

Each subagent operates in its own isolated 200K-token window, receiving ~500 tokens of task context. When complete, it returns only a summary (~1-2K tokens) to the main conversation. Up to 10 subagents can run simultaneously.

Route subagents by task type:
- **Explore** subagent for read-only codebase search
- **Plan** subagent before implementing anything non-trivial
- Custom subagents in `.claude/agents/` for recurring tasks (code review, test writing, docs)

Anthropic's multi-agent system (Opus lead + Sonnet subagents) outperformed single-agent Opus by 90.2%.

### Dynamic Pre-Flight Hooks

Instead of loading massive project guidelines on every turn, use `session-start.sh` hooks to dynamically load only the rules relevant to the active directory (e.g., only load frontend rules if you are working in `/src/components`). Build a script that concatenates modular rule files (like `global.md` and `frontend.md`) into a single `active-context.md` based on `$PWD`, and incorporate this hook into your initialization protocol.

### Semantic Caching Structuring

To maximize the 50-90% input token discount from Prompt Caching, structure all predefined workflows and prompts so the cacheable content is front-loaded. Ensure all static context (system instructions, API references) sits strictly at the very top of the context window, and the dynamic user request is appended at the very bottom.

### Section Checklist

- [ ] `/clear` used after every commit and task switch
- [ ] PROGRESS.md maintained as cross-session state artifact
- [ ] Feature/task state stored in JSON format
- [ ] Custom subagents defined in `.claude/agents/` for recurring tasks
- [ ] Context never exceeds 85% utilisation during development
- [ ] `init.sh` configured with real build/test/lint commands
- [ ] Directed `/compact focus on X` used for focused sessions
- [ ] Session-handoff skill installed and tested
- [ ] Git commit messages descriptive enough to serve as session history
- [ ] Dynamic pre-flight hooks used to bound context by directory
- [ ] Prompts structured for semantic caching (static top, dynamic bottom)

---

## 4. Hallucination Prevention and Verification

The most dangerous failure mode is confidently wrong code that appears complete. Guard against it with structured verification at every step.

### Package Hallucination Rates

USENIX Security 2025 study of 576K samples:
- Python: **5.2%** hallucination rate
- JavaScript: **21.7%** hallucination rate
- Prompts for "2025 libraries": hallucinations in **84%** of tasks

### MCP-First Retrieval

Before writing any code that uses an external library or API, follow this 3-tier retrieval pattern:

1. **Tier 1 — MCP docs server** (e.g. Context7: `resolve-library-id` then `query-docs`): version-specific, sub-second, zero token waste. Always try this first.
2. **Tier 2 — Project research notes** (`docs/research/`): pre-verified findings with "What We Ruled Out" preventing rediscovery of rejected approaches.
3. **Tier 3 — Web search**: last resort, highest token cost. Search for current official documentation only.

This pattern eliminates the most common hallucination vector: wrong-version API calls.

### Dependency Verification (Slopsquatting)

34% of AI-suggested packages don't exist (Endor Labs 2025). This is called "slopsquatting" — plausible but non-existent package names that attackers can register and fill with malware. 43% of hallucinated package names are consistently repeated across similar prompts.

Before adding any dependency:
- Verify the package exists in the public registry (PyPI, npm, etc.)
- Check: popularity (download count), maintenance status, license
- Pin exact versions in lockfiles (`uv.lock`, `package-lock.json`)
- Flag single-maintainer projects and packages with >20 transitive dependencies
- Agents select vulnerable versions 2.46% of the time vs 1.64% for humans — always verify

### The "Mark as Complete" Failure Mode

Before marking any task complete: run tests via tool call, read the output, verify pass. Never self-report completion. The Definition of Done in AGENTS.md enforces this:

1. Tests pass (verified via tool call)
2. Linter passes
3. Docs updated if behaviour changed
4. PROGRESS.md updated with what was done
5. E2E smoke test passes (run `./scripts/init.sh`)

### Code Search as Hallucination Prevention

Before inventing a pattern, search the codebase for existing implementations. Use semantic code search to find similar patterns already in use. If the codebase already has a rate limiter, follow that pattern rather than generating one from training data. This prevents "style hallucination" — code that works but violates project conventions.

### Hooks as Structural Guardrails

Configure hooks in `.claude/hooks.json` to enforce verification automatically. Three hook types form a layered validation system:

**Stop hooks** — run linter, tests before allowing task completion. Empty matcher = always runs:
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{ "type": "command", "command": "ruff check . --quiet && echo 'Lint: OK'" }]
    }]
  }
}
```

**PostToolUse hooks** — automatically format files behind the agent's back. Instead of making the agent waste tokens fixing syntax, route `Edit|Write` to a `.claude/hooks/format-file.sh` that detects the extension and runs Prettier or Ruff:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "./.claude/hooks/format-file.sh \"${CLAUDE_TOOL_INPUT_FILE_PATH}\"" }]
    }]
  }
}
```

**PreToolUse hooks** — intercept critical commands (like `git commit`) with lightweight validation, or inject reminders before file modifications. For example, remind the agent to use `nexus-mcp` before writing files:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "echo 'REMINDER: Ensure you have performed a nexus-mcp codebase search for impact and dependencies prior to this adjustment.'"
      }]
    }, {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "echo \"${CLAUDE_TOOL_INPUT_COMMAND}\" | grep -q 'git commit' && (./.claude/hooks/pre-commit.sh || exit 1) || true"
      }]
    }]
  }
}
```

**Advanced patterns:**
- **External script delegation**: for complex pre-commit logic (docs staleness, changelog checks), delegate to a shell script: `bash .claude/hooks/pre-commit-docs-check.sh`
- **Non-blocking warnings**: exit 0 always for advisory hooks (e.g. "docs may be stale"), exit 1 only for blocking gates
- **Bypass mechanism**: check for `[skip-docs]` in commit message to suppress optional warnings
- **Environment variables**: hooks receive `$CLAUDE_TOOL_INPUT_FILE_PATH`, `$CLAUDE_TOOL_INPUT_COMMAND`, `$TOOL_NAME` for conditional logic

### Your Research Template

Before implementing with any external library, create a research note using this structure:

```markdown
# Research: [Topic / Library / API Name]
**Library version:** [exact version, e.g. stripe@14.2.0]
**Status:** [Current | Needs update | Superseded]

## Sources Consulted
| Source | URL | Date accessed |

## The Correct Approach
[Working code example with exact library version]

## What We Ruled Out (and Why)
| Approach | Why Rejected |

## Security Assessment
- [ ] CVE check (Snyk, pip-audit, npm audit)
- [ ] Maintenance health (last release, open issues, bus factor)
- [ ] License compatibility
- [ ] Dependency tree risk (transitive deps count, known vulnerabilities)

## Known Gotchas / Edge Cases
```

The key fields: **Library version** prevents wrong-version code generation. **What We Ruled Out** prevents rediscovering rejected approaches. **Security Assessment** is mandatory for every new dependency — no exceptions.

### Section Checklist

- [ ] MCP-first retrieval pattern configured (docs server → research notes → web search)
- [ ] Testing tools installed (runners, browser automation, HTTP clients)
- [ ] API documentation injected for all external services
- [ ] Feature status derived from test results, not agent self-reporting
- [ ] Stop hooks enforce test/lint pass before task completion
- [ ] PostToolUse hooks run formatters on every write
- [ ] Research template used for every new external library/API
- [ ] Library versions pinned in project configuration
- [ ] Dependencies verified against package registries before installation

---

## 5. MCP Server Integration: The IDE Agent Toolbox

Model Context Protocol (MCP) servers extend your IDE coding agent with external tools — docs lookup, browser testing, security scanning, code intelligence — all accessible without leaving the editor. MCP is an open standard with 97M+ monthly SDK downloads, adopted as an AAIF project under the Linux Foundation.

### Configuration

Configure MCP servers in two locations:
- **`.claude/mcp.json`** (project-scoped): checked into version control, shared with the team
- **`~/.claude/mcp.json`** (user-scoped): personal tools, not committed

Example project-scoped configuration:
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright"]
    }
  }
}
```

### MCP Stack Taxonomy

Configure servers from each category relevant to your project:

| Category | Examples | Purpose |
|----------|----------|---------|
| **Knowledge retrieval** | Context7, official docs servers | Version-specific library docs — eliminates wrong-version hallucination |
| **Code intelligence (hybrid)** | Nexus-MCP, Probe | Hybrid search (vector+BM25+graph), structural analysis, semantic memory — unified in one server |
| **Discovery & Management** | MCP Compass | Discover, catalog, and manage large collections of MCP servers |
| **Browser automation** | Playwright, Puppeteer | E2E testing, UI verification, visual regression; Puppeteer preferred for Node-heavy stacks |
| **Reasoning** | Sequential Thinking | Structured reasoning for architecture decisions |
| **Security** | Snyk, Semgrep | SAST scanning, dependency vulnerability checking |

### Agent-to-MCP Routing

Assign MCP tools to subagents based on their role. Not every agent needs every tool:

| Subagent | MCP Tools | Rationale |
|----------|-----------|-----------|
| **planner** & **implementer** | Nexus-MCP | Perform structural discovery, analyze dependencies, search codebase context before executing changes |
| **code-reviewer** | Context7, Nexus-MCP, Snyk | Verify API usage, check callers/callees/impact, blast radius, ensure no side-effects occur, scan security |
| **research-assistant** | Context7, Sequential Thinking, Snyk, Nexus-MCP | Docs lookup, structured reasoning, dependency safety, code search and validation |
| **debug-detective** | Playwright, Nexus-MCP, Context7 | Reproduce in browser, trace call paths, verify API usage |
| **test-writer** | Context7 | Verify test framework APIs against current docs |
| **docs-writer** | Context7, Playwright, Nexus-MCP | Discover full context of code updates to synchronize documentation properly |
| **security-auditor** | Snyk, Nexus-MCP | Analyze blast radius of uncovered vulnerabilities, query CVEs |
| **ui-scaffolder** | Nexus-MCP | Find existing styling rules before generating layouts |
| **ship-it** | Nexus-MCP | System-wide architecture query prior to deployment |

### MCP Best Practices

Follow these principles from the official MCP specification:
- **Single responsibility**: one clear purpose per server — avoid "everything tool" complexity
- **Security-first defaults**: all new servers start read-only; grant write access only after observing safe usage
- **Strict schemas**: define input/output contracts before implementation; fail-fast on invalid data
- **Token efficiency**: be specific in queries, use limits, avoid loading entire pages into context
- **Active Enforcement**: Do not assume agents will proactively use contextual MCP tools. You must enforce codebase discovery across three layers:
  1. **Instruction Layer**: Mandate usage centrally in `AGENTS.md` and `CLAUDE.md` (e.g., "MANDATORY: Check nexus-mcp for impact on every adjustment").
  2. **Workflow Layer**: Add explicit query steps directly into recurrent `.agents/workflows/` (including `planner`, `implementer`, `code-reviewer`, `docs-writer`, `security-auditor`, `ship-it`, `ui-scaffolder`, and `research-assistant`).
  3. **Hook Layer**: Use `PreToolUse` bash hooks targeting `Edit|Write` matchers to emit terminal reminders immediately before an agent alters a file without fetching context.

### Section Checklist

- [ ] MCP servers configured in `.claude/mcp.json` (project-scoped)
- [ ] Knowledge retrieval server configured for version-specific library docs
- [ ] Code intelligence tools (semantic + structural) configured as MCP servers
- [ ] Browser automation MCP configured for E2E testing
- [ ] Agent-to-MCP routing defined (which subagents get which tools)
- [ ] Security scanning MCP integrated with review workflow

---

## 5a. Multi-Framework Patterns (LangGraph, CrewAI, AutoGen)

You don't need external frameworks to adopt their best practices. Here's how to implement proven patterns from major agentic frameworks using only IDE agents and simple files.

### Why This Matters

In 2026, three major frameworks emerged with complementary strengths:
- **LangGraph**: Graph-based workflows, state machines, self-correction loops
- **CrewAI**: Role-based collaboration, hierarchical workflows
- **AutoGen**: Conversational architecture, event-driven coordination

**You can implement all these patterns** without installing frameworks, just by organizing your agent workflow smartly.

### LangGraph Patterns (Graph-Based Workflow)

**What**: Tasks as DAGs (directed acyclic graphs) with conditional branching and state machines.

**How to implement with IDE agents**:
1. **Planner creates DAGs**: When planning, have your planner agent think in dependency graphs:
   ```
   Task A (setup) → Task B (implement) → Task C (test)
                 ↘ Task D (docs) ↗
   ```
2. **PROGRESS.md as state machine**: Track current state, transitions, and conditions
3. **Self-correction loops**: Reviewer agent provides feedback → implementer revises → reviewer validates

**Practical example**:
```markdown
## Task Graph (in plan.md)
- [ ] A: Setup auth module (no deps)
- [ ] B: Implement JWT (depends on A)
- [ ] C: Add refresh tokens (depends on B)
- [ ] D: Write tests (depends on B,C)
- [ ] E: Update docs (depends on D)
```

**Benefit**: Parallel execution (A and docs can start simultaneously), clear dependencies, no blocked work.

### CrewAI Patterns (Role-Based Collaboration)

**What**: Specialized agents for specific roles (researcher, coder, reviewer, tester) with hierarchical coordination.

**How to implement with IDE agents**:
1. **Create 3-6 custom agents** (`.claude/agents/` or `.github/agents/`)
   - `planner.agent.md`: Breaks down tasks
   - `implementer.agent.md`: Writes code following TDD
   - `reviewer.agent.md`: High signal-to-noise code review
   - `research-assistant.agent.md`: Validates external dependencies
   - `test-writer.agent.md`: Comprehensive test coverage
   - `docs-writer.agent.md`: Keeps docs in sync

2. **Wave Protocol** (hierarchical workflow):
   - Wave 1: Planner generates plan.md
   - Wave 2: Implementer + research-assistant execute in parallel
   - Wave 3: Test-writer validates
   - Wave 4: Reviewer provides feedback
   - Wave 5: Docs-writer updates documentation

**Benefit**: Each agent has clear focus, preventing context overload. Better results than one agent trying to do everything.

### AutoGen Patterns (Conversational & Event-Driven)

**What**: Agents communicate through natural dialogue and react to events.

**How to implement with IDE agents**:
1. **Session handoff dialogue**: Use skills like `session-handoff` for cross-session continuity
2. **Event-driven hooks**: Use `.claude/hooks.json` (or equivalent) to trigger actions
   ```json
   {
     "on_file_save": "format-file.sh {file_path}",
     "on_test_fail": "research-assistant",
     "on_commit": "ship-it verify"
   }
   ```
3. **File-based async coordination**: Agents communicate through PROGRESS.md, plan.md, ADRs

**Benefit**: Reactive workflows, automatic formatting, smart handoffs between specialized agents.

### Lightweight Risk Awareness (Not Governance)

You don't need approval workflows, but you should **think about risk**:

**High-Risk Tasks** (think twice, test thoroughly):
- Database migrations (hard to rollback)
- Authentication changes (security critical)
- Third-party API changes (external dependencies)
- Payment processing (financial impact)
- Production deployments (user-facing)

**Low-Risk Tasks** (move fast):
- Documentation updates
- Test additions
- Formatting changes
- Internal refactoring (with good tests)

**Smart defaults for solo/small teams**:
- High-risk: Write extra tests, document rollback plan, deploy to staging first
- Low-risk: Ship it, iterate fast

No bureaucracy needed—just awareness.

### MCP Security (Without Governance Overhead)

**Trust but verify** your MCP servers:
1. **Stick to well-known servers** (Anthropic's official ones, popular community servers with 1000+ stars)
2. **Review permissions** before installing (file access, network access, etc.)
3. **Don't blindly install** from random sources (same as npm/pip/cargo packages)

**Pre-approved safe servers** (as of 2026):
- `context7` - Real-time docs (Anthropic official)
- `sequential-thinking` - Complex reasoning (Anthropic official)
- `fetch` - Web scraping/API calls (controlled network access)
- `playwright` - Browser automation (if you need it)

**Red flags**:
- Servers requesting file system write access without clear need
- Servers with vague descriptions
- Servers from unknown maintainers with <10 stars

**Your call**: You're the security officer. If it feels sketchy, skip it.

### ADLC (Agentic Development Life Cycle)

Traditional SDLC for humans:
```
Requirements → Design → Implement → Test → Deploy
```

ADLC for AI-native teams (solo or small):
```
Intent → Plan (AI) → Parallel Execute (AI) → Validate (AI+Human) → Deploy (Human confirms)
```

**Key differences**:
- **Parallel execution**: Multiple agents work simultaneously (planner + researcher, implementer + test-writer)
- **Continuous validation**: Tests run during implementation, not after
- **Autonomous with checkpoints**: Agents do heavy lifting, you approve deploys

**Practical workflow**:
1. **Intent**: "Build user authentication with JWT"
2. **Plan**: Planner agent creates task DAG (30 seconds)
3. **Execute**: Implementer + research-assistant work in parallel (5-10 minutes)
4. **Validate**: Test-writer creates tests, runner validates (2 minutes)
5. **Deploy**: You review, approve, ship-it skill deploys (30 seconds)

Total: 10-15 minutes instead of 2 hours. That's the 3-10x acceleration.

### Quick Implementation Guide (30 Minutes)

Want to adopt these patterns? Start small:

**Week 1** (10 min):
- Create 3 custom agents: planner, implementer, reviewer
- Add them to `.claude/agents/` or `.github/agents/`
- Use planner before starting any task

**Week 2** (10 min):
- Add PROGRESS.md state tracking
- Use Wave Protocol (plan → implement → review)
- Create plan.md with task DAGs

**Week 3** (10 min):
- Add research-assistant and test-writer agents
- Set up hooks.json for auto-formatting
- Review MCP server list, remove unknowns

**Week 4** (ongoing):
- Measure velocity (features per week)
- Refine agent prompts based on results
- Share learnings with team

No frameworks, no dependencies, just better organization.

### Section Checklist

- [ ] 3-6 specialized agents created (planner, implementer, reviewer minimum)
- [ ] Task planning uses DAG thinking (dependencies explicit)
- [ ] PROGRESS.md tracks state across sessions
- [ ] Wave Protocol adopted (plan → execute → validate → review)
- [ ] High-risk tasks identified and tested thoroughly
- [ ] MCP servers reviewed (stick to well-known ones)
- [ ] ADLC workflow understood (Intent → Plan → Execute → Validate → Deploy)

---

## 6. Skills: Modular, On-Demand Agent Knowledge

Skills solve the tension between giving agents enough knowledge and not overwhelming their context window. They follow a progressive disclosure model.

### How Skills Work

**Level 1 — Metadata only**: At startup, load only the `name` and `description` from every Skill's YAML frontmatter. Cost: ~100 tokens per Skill.

**Level 2 — SKILL.md body**: Loaded when the Skill is relevant to the current task. Target: under 500 lines.

**Level 3+ — Supporting files**: Scripts, templates, references load on-demand. Scripts execute externally — their code never enters the context window.

### The Description Field Is Everything

The description triggers Skill loading — it is the primary activation mechanism. Write keyword-rich descriptions with trigger contexts:

```yaml
---
name: deploy-staging
description: >
  Deploy the application to staging environment. Use when the user asks to
  deploy, push to staging, or test in a staging environment. Handles Docker
  build, ECR push, ECS service update, and health check verification.
---
```

Include trigger contexts, relevant file types, task types, and keywords the user might use.

### Skill Architecture

```
.claude/skills/
├── deploy-staging/
│   ├── SKILL.md              # Instructions + YAML frontmatter
│   ├── scripts/
│   │   └── deploy.sh         # Executed externally, not loaded into context
│   └── references/
│       └── aws-config.md     # Loaded on-demand
├── session-handoff/
│   └── SKILL.md
├── triple-agent-audit/
│   └── SKILL.md
└── api-endpoint/
    ├── SKILL.md
    └── references/
        └── openapi-spec.yaml
```

### When to Create a Skill vs Other Constructs

| Construct | Use When |
|-----------|----------|
| **Skill** | Repeatable task needing supporting files; loads on-demand |
| **Path-scoped rule** (`.claude/rules/`) | Universal instruction for specific file patterns; under 50 lines |
| **CLAUDE.md** | Universal constraint; under 5 lines; applies every session |
| **Subagent** (`.claude/agents/`) | Specialised role with isolated context |

### Advanced Skill Patterns

**Prerequisite checks**: Skills should verify preconditions before running. A coverage-report skill should check that pytest-cov is installed and tests pass before generating coverage. A commit-ready skill should run lint before tests (fail fast on cheap checks).

**Multi-step gate functions**: A commit-ready skill can implement a 5-7 step validation checklist: lint → tests → docs staleness → PROGRESS.md → code review gate. Mark steps as BLOCKING (must pass) vs WARN (advisory only). Docs-only commits can bypass test and code review gates.

**Feature classification routing**: A new-feature skill can classify features into types (e.g. Type A: new service, Type B: new agent, Type C: new endpoint) and route to different agent sequences. Type A routes to research-assistant first; Type B routes to adr-writer first; all types route to test-writer (non-negotiable).

**Bidirectional documentation bridges**: A docs-writer skill should both READ business context documents before updating (for alignment) AND WRITE back to them when code changes affect business capabilities. This creates a two-way flow between code and strategy documentation.

**Ship-it release pipeline**: A ship-it skill orchestrates the full release workflow: pre-flight verification → documentation updates → commit (with lint/test gates) → push → deploy → post-deploy health check. Each step acts as a gate — failure stops the pipeline. The skill supports selective execution ("just commit", "commit and push", "deploy only") so developers choose their scope. Key rules: always confirm before deploying, never commit secrets, never force push, derive feature status from test results only. This pattern eliminates the "it works on my machine" gap by enforcing the same verification chain locally that CI would enforce remotely.

### Development Workflow

1. Run agents on representative tasks, observe failures
2. Build a Skill addressing the gap
3. Have a **fresh Claude session** test the Skill — the author session is biased
4. Iterate: remove explanations the model already knows, split when SKILL.md exceeds 500 lines

### Section Checklist

- [ ] Skills directory at `.claude/skills/` with clear naming
- [ ] Each Skill has keyword-rich description in YAML frontmatter
- [ ] SKILL.md bodies under 500 lines
- [ ] Scripts in `scripts/` for external execution
- [ ] Skills tested with a fresh session
- [ ] No duplication between Skills and CLAUDE.md
- [ ] Skills with prerequisites verify them before running
- [ ] Commit-ready skill implements multi-step validation gate
- [ ] Triple-agent-audit skill installed for industrial quality gates
- [ ] Ship-it skill for document → commit → push → deploy pipeline

---

## 7. Documentation Architecture for Dual-Audience Consumption

Documentation in agentic projects serves two audiences: humans who skim and infer, and agents who depend on explicit structure.

### The llms.txt Standard

Serve a `/llms.txt` Markdown file at the documentation root containing the project name, a summary, and organised links. A companion `llms-full.txt` concatenates all docs for full-context consumption. Reduces token consumption 90%+ vs HTML parsing. For MkDocs, `mkdocs-llmstxt` auto-generates these files.

### Architecture Decision Records

Before making any architectural decision (new dependency, design pattern, data model change), create an ADR:

```markdown
# ADR-[NNN]: [Title]
## Status: [Proposed | Accepted | Deprecated | Superseded]
## Context: [What is the issue motivating this decision?]
## Decision: [What is the change proposed/agreed to?]
## Consequences: [What becomes easier or harder?]
```

Store in `docs/adr/` with sequential numbering. Without ADRs, agents will "improve" code by reversing deliberate architectural choices.

### Section Checklist

- [ ] llms.txt file at documentation root
- [ ] ADR directory with sequential numbering and template
- [ ] CLAUDE.md instruction to create ADRs for architectural decisions
- [ ] READMEs at every significant directory level
- [ ] Business rules and external constraints explicitly documented

---

## 8. Specification-Driven Development

The gap between a task description and shippable code is where most agentic workflows break down. Specifications are implementation contracts, not documentation.

### The 50-Minute Horizon

METR research (March 2025): frontier models have 50% success at 50-minute tasks. Approaches 100% for <4-minute tasks, drops below 10% for >4-hour tasks. Horizon doubles every 7 months.

**Decompose every feature into tasks achievable within 30-50 minutes of agent work.**

### GitHub Issues as Agent Task Units

Structure Issues with everything an agent needs:

```markdown
## Feature: Rate limiting for API endpoints

### Acceptance Criteria
- [ ] Rate limit: 100 requests per minute per API key
- [ ] Rate limit headers in all responses
- [ ] 429 response with Retry-After header when exceeded
- [ ] Integration tests covering normal flow, limit hit, and reset

### Files Likely Modified
- src/middleware/rate-limiter.ts (new)
- src/api/router.ts (apply middleware)
- tests/integration/rate-limiting.test.ts (new)

### Out of Scope
- Do NOT modify authentication middleware
- Do NOT change existing API response formats
```

### Two-Tier Agent Architecture

For complex features: **Planner agent** (Opus, read-only) decomposes work → **Implementer agent** (Sonnet, full access) executes one task at a time. The `opusplan` alias delivers 80-90% cost savings vs all-Opus.

### Plan Mode Before Implementation

Use Plan Mode (Shift+Tab in Claude Code) to restrict to read-only operations. Planning (5-9 minutes) followed by implementation (18-35 minutes) produces faster total completion than jumping to coding.

**Enter plan mode for any task with 3+ steps, multi-file changes, or architectural decisions.**

### The Wave Protocol (Triple Agent Audit)

After each implementation wave, execute the **Triple Agent Audit** (Review, Test, Document) to ensure quality compounds. This protocol transforms raw code into industrial-grade features.

1. **Implement** (Wave 2): The implementation phase where the core logic is written.
2. **Test** (Wave 3): Run `test-writer` agent — adds comprehensive coverage, edge cases, and resilience checks.
3. **Review** (Wave 4): Run `code-reviewer` agent — checks logic, security, and strict pattern consistency.
4. **Document** (Wave 5): Run `docs-writer` agent — synchronizes changes with documentation and `PROGRESS.md`.
5. **Final Commitment**: Verify all tests pass via `./scripts/test_all.sh` before commit.

Multi-agent orchestration outperforms single-agent by 45% faster resolution and 60% higher accuracy (LangChain State of Agent Engineering 2026). Treat agents like code, not chat interfaces — apply distributed systems thinking with explicit structure and validation at every boundary.

### Section Checklist

- [ ] Specifications with measurable acceptance criteria before work begins
- [ ] Tasks decomposed into 30-50 minute agent work units
- [ ] Issues structured with acceptance criteria, files, and scope
- [ ] Plan mode used before non-trivial implementation
- [ ] Definition of Done enforced for every agent task
- [ ] Wave protocol followed for each implementation cycle
- [ ] Orchestrator + specialist pattern for multi-concern features

---

## 9. Research Before Implementation, Never During

Research while implementing produces the worst outcomes. Follow this pattern: **research first, document findings, clear context, implement from the research artifact.**

### The Retrieval-Augmented Implementation Pattern

1. Create a research subagent with read-only tools (Glob, Grep, Read, WebSearch, MCP docs servers)
2. Subagent explores codebase, checks versions, reads docs
3. Produces a structured findings document using RESEARCH-TEMPLATE.md (see Section 4 for the template)
4. Clear context (`/clear`)
5. Implementation agent reads only the findings document

The "Files This Affects" section in the research template gives the implementation agent an immediate scope boundary.

### Token Consumption

Analysis of 7 coding agents: Claude Code uses 108-117K tokens for iterative lexical search. Aider's tree-sitter AST with PageRank uses only 8.5-13K tokens. Pre-research dramatically reduces implementation-phase token burn. AST-level code retrieval achieves 87% token reduction vs grep-based search.

### Version Pinning

Include versions in both CLAUDE.md and research docs: "React 18 with TypeScript, Vite, Tailwind" prevents wrong-version code generation.

### Section Checklist

- [ ] Research subagent created for every non-trivial task
- [ ] Findings documented using RESEARCH-TEMPLATE.md before implementation
- [ ] Context cleared between research and implementation
- [ ] Third-party API versions verified before integration code
- [ ] Library versions pinned in project configuration
- [ ] `docs/research/INDEX.md` maintained as knowledge base index

---

## 10. Observability and Debugging Agent Behaviour

Agent behaviour is opaque by default. Without observability, debugging failures becomes guesswork.

### Logging Proxy

Route all API calls through a logging proxy via `ANTHROPIC_BASE_URL`:

```bash
ANTHROPIC_BASE_URL=http://localhost:8000/ claude
```

This captures prompts, responses, tool calls, and token counts — complete visibility without modifying agent code. **claude-code-logger** provides chat mode visualisation. **claude-code-transcripts** converts session transcripts to detailed HTML.

### Hook-Based Tracing

Log every tool call via PreToolUse hooks:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "",
      "hooks": [{ "type": "command", "command": "echo \"$(date) $TOOL_NAME\" >> .claude/agent-trace.log" }]
    }]
  }
}
```

### Platforms

**Langfuse** (open-source): traces decision workflows with OpenTelemetry support. **Braintrust**: gateway-based proxy with no code changes. **Arize/Phoenix**: structured tracing with duration, token usage, cost per step.

### Section Checklist

- [ ] Logging proxy or transcript tool capturing agent sessions
- [ ] Hook-based tracing for tool call audit trail
- [ ] Token consumption tracked per session type
- [ ] Quiet failure detection (infinite loops, context abandonment)

---

## 11. Code Review for Agent-Generated Code

AI-generated code contains 1.7x more defects than human code. 45% contains security flaws. Only 48% of developers consistently review AI-assisted code before committing. Treat agent-generated code with the same rigour as human code — or more.

### Cross-Model Review

If you use multiple IDE agents (Claude Code + Copilot), generate with one, review with the other — each has distinct blind spots. For forma
l review: Claude Code's GitHub Actions integration (`anthropics/claude-code-action@beta`) enables automated PR review on every push.

### Agent-Based Code Review

Define a code-reviewer subagent in `.claude/agents/code-reviewer.md`:

```yaml
---
name: code-reviewer
description: Senior code reviewer. Run after every implementation wave.
  Checks code quality, architecture, security, test coverage.
tools: Read, Grep, Glob, Bash
model: sonnet
---
```

The agent follows a structured protocol:
1. Identify changed files via `git diff`
2. Run verification commands (lint, test)
3. Check each category: logic errors, security vulnerabilities, performance, pattern consistency
4. Include MCP tools in the `tools:` list for deeper analysis — Context7 for API verification, Nexus-MCP for callers/callees/impact of changed functions, Snyk for security scanning
5. Produce a structured verdict: **SHIP** / **ITERATE** / **BLOCK**

**Critical rule: tool verification mandate.** The code-reviewer must USE TOOLS to verify every checklist item — read actual test output, run actual lint commands, check actual file contents. Never assume anything passes. This single rule eliminates the majority of false "SHIP" verdicts.

### Agent Definition Best Practices

When defining agents in `.claude/agents/`:
- **Model sizing**: haiku for research/exploration (cheap, fast), sonnet for code review and test writing (good reasoning), opus for architecture decisions and eval judging (deep reasoning)
- **Single-line descriptions**: block scalars in YAML cause indent errors; use a single string with trigger keywords
- **Explicit MCP tools**: list the exact MCP tools each agent uses — not all agents need all tools
- **Pattern-based diagnosis**: for debugging agents, define named failure patterns with specific playbooks (e.g. "mock path error: agent patched at definition site instead of usage site")
- **Deterministic thresholds**: for eval/review agents, use concrete score thresholds (e.g. "block if regression > -0.5"), not subjective judgment
- **Escalation protocols**: define what happens after 3 failed iterations — escalate to human or switch approach
- **Hypothesis-driven iteration**: for prompt optimizers, require a one-sentence hypothesis per change (prevents shotgun rewrites)

Empirical data: 83.77% of Claude Code PRs merge (vs 91% for human PRs), and 54.95% require zero modifications — agent code quality is achievable with proper review (arxiv 2509.14745v1).

### Automated Enforcement

Use CLAUDE.md for semantic rules (architecture, patterns). Use hooks for mechanical rules (formatting, imports). PostToolUse hooks for formatters. Stop hooks ensure the agent cannot declare completion until checks pass.

### Section Checklist

- [ ] All agent PRs reviewed with same rigour as human code
- [ ] Cross-model review configured where multiple IDE agents are available
- [ ] Code-reviewer subagent defined with structured protocol and MCP tools
- [ ] PostToolUse hooks for formatters
- [ ] CI pipeline includes security scanning (SAST/DAST)
- [ ] Wave protocol followed: test-writer → code-reviewer → fix → docs-writer
- [ ] Tool verification mandate: reviewers read actual output, never assume passes
- [ ] Agent definitions use deterministic thresholds, not subjective judgment

### Review-as-a-Service: CodeRabbit Integration

For high-velocity teams, integrate CodeRabbit as a proactive review layer.
- **Pattern**: CodeRabbit acts as the "Senior Reviewer" that watches every PR.
- **Agentic Value**: Use the CodeRabbit **Issue Planner** to generate "Agentic Plans" before code is written, ensuring the local agent (Claude, Cursor) follows an approved architectural blueprint.
- **Automation**: Feed CodeRabbit's persistent findings back into the agent's auto-memory to prevent recurring style violations.

---

## 11a. The Triple Agent Audit: Review, Test, Document

The Triple Agent Audit is the non-negotiable quality gate in the industrial-grade ADLC. It ensures that code isn't just "functional" but is industrially hardened, resilient, and properly documented before merge.

### The Personas
1. **The Reviewer** (`code-reviewer.md`): Focuses on logic errors, pattern consistency, security vulnerabilities (via Snyk/MCP), and code health metrics. Mandate: must achieve Code Health score 9.5+.
2. **The Tester** (`test-writer.md` / `tester.md`): Focuses on edge cases, resilience (404/500 handling), concurrency, and boundary conditions. Mandate: 100% pass on `./scripts/test_all.sh` (Smoke, Unit, Integration, Stress, E2E).
3. **The Writer** (`docs-writer.md`): Focuses on synchronizing design changes strictly into `docs/`, updating `PROGRESS.md`, and keeping `llms.txt` current. Mandate: zero documentation staleness.

### The Protocol
- **Skill-Based Execution**: Use the `triple-agent-audit` skill (`.claude/skills/triple-agent-audit/SKILL.md`) to orchestrate the validation waves.
- **Distinct Passes**: Run as three distinct subagent waves (Wave 3, 4, 5) to prevent context contamination.
- **Tool Verification Mandate**: The Reviewer and Tester MUST use tools to verify every claim—read actual test output, run actual lint commands, and check actual file contents. Never assume a pass.
- **Audit Verdict**: Each agent produces a structured verdict (SHIP / ITERATE / BLOCK) with a brief justification.

### Definition of Done (Triple Audit)
- [ ] **Reviewer**: "SHIP" verdict with 0 logic errors and 0 critical lint/pattern warnings.
- [ ] **Tester**: Verified logs showing 100% test pass including E2E and stress tests.
- [ ] **Writer**: Documentation sync verified; `PROGRESS.md` and `ARCHITECTURE.md` reflect current state.

### Section Checklist
- [ ] Reviewer, Tester, and Writer personas defined in `.claude/agents/` or `.github/agents/`
- [ ] Triple Agent Audit executed for every significant PR/Feature
- [ ] Tool verification mandate followed (agents read actual output)
- [ ] Audit results documented in session or `docs/audits/`

---


## 12. Cost and Efficiency Management

An unconstrained agent can consume $5-8 per task. Research loops running 10 cycles can burn 50x the tokens of a single linear pass. Output tokens cost ~4x more than input tokens.

### Model Routing

| Model Class | Cost | Use For |
|-------------|------|---------|
| **Haiku** | 1x | Exploration, file search, summarisation, status checks |
| **Sonnet** | 12x | Standard code generation, test writing, documentation (90% of work) |
| **Opus** | 60x | Architecture, complex debugging, multi-step reasoning |

### Token Optimisation

- **Prompt caching**: saves 50-90% on repeated prompt tokens
- **History pruning** via `/compact`: cuts per-conversation tokens 70-90%
- **Reference files instead of pasting**: 500-line paste = ~4K tokens
- **Progressive disclosure via Skills**: only load knowledge when needed
- **AST-level code retrieval**: 87% token reduction vs grep-based search (use code intelligence MCP servers)
- **Semantic caching**: 90% input cost reduction + 75% latency improvement on repeated context
- **Dynamic turn limits**: 24% cost reduction by capping loop iterations based on problem complexity — simpler tasks get fewer turns
- **Batch API**: 50% discount for 24-hour turnaround (background tasks)

### Section Checklist

- [ ] Model routing configured by task type
- [ ] Prompt caching enabled for repeated context
- [ ] Skills used for progressive knowledge disclosure
- [ ] Token budget tracked per session type
- [ ] Code intelligence tools used to reduce search token consumption
- [ ] Batch API used for non-urgent tasks

---

## 13. Security Guardrails

ProjectDiscovery generated 3 full-stack applications (~30,000 lines) using Codex, Cursor, and Claude Code without prompting for security. Result: 70 exploitable vulnerabilities including 18 Critical/High issues. Prompt injection attacks achieve up to 84% success rates.

### Sandbox Architecture

IDE coding agents use OS-level primitives:
- **Linux**: Bubblewrap (Landlock + Seccomp profiles)
- **macOS**: Seatbelt (`sandbox_init`)

Non-negotiable controls: network egress controls, file write restrictions outside workspace, secret isolation.

### Permission Tiers

| Tier | Actions |
|------|---------|
| Always allow | Read files, run tests, format, search, grep |
| Ask first | Schema changes, add dependencies, modify CI |
| Never allow | Commit secrets, push to main, modify production |

**Granular permission allow-lists**: In `settings.json`, whitelist specific commands rather than granting blanket approval. Example: allow `Bash(uv run ruff check ...)` and `Bash(uv run pytest ...)` but not all Bash commands. This prevents accidental destructive operations while keeping the development flow smooth.

### Supply Chain Security

Agents introduce supply chain risk at scale. Key data:
- 34% of AI-suggested packages don't exist ("slopsquatting") — verify against registry before install
- Agents select vulnerable versions 2.46% of the time vs 1.64% for humans
- Agent dependency selections require major version upgrades 36.8% of the time (vs 12.9% for humans)

Mitigate: pin exact versions in lockfiles, scan full dependency tree for CVEs, flag packages with >20 transitive dependencies, verify every package exists in the public registry before adding.

### NVIDIA's Mandatory Controls

The NVIDIA AI Red Team (2025) defines five non-negotiable controls for agentic workflows:
1. **Network isolation**: use allowlists (known-safe locations), not denylists
2. **Workspace boundaries**: prevent writes outside the active workspace
3. **Config file protection**: block all writes to agent config files (.cursorrules, hooks, MCP configs) without explicit user approval
4. **Lifecycle management**: periodically destroy and recreate sandbox environments to prevent credential accumulation
5. **Per-action approvals**: never cache approval decisions — require fresh confirmation for each risky action

OS-level enforcement beats application-level controls. Attackers can bypass allowlists through indirect tool calls.

### Security Scanning via MCP

Integrate security scanning MCP servers (e.g. Snyk) directly into the agent workflow. Scan new or modified code immediately after writing it ("security at inception"), not as a separate CI step:
- **SAST scanning**: static analysis for injection, XSS, path traversal
- **SCA scanning**: dependency vulnerability checking when lockfiles change
- Add as a CLAUDE.md instruction: "Always run security scan for new first-party code in a supported language"

**Budget-conscious scanning**: If using a free-tier security scanner (e.g. Snyk's 100 tests/month), skip per-wave scans in the code-reviewer agent and reserve the budget for pre-commit scans and new dependency additions. Document the budget in CLAUDE.md so agents don't waste it.

### Version Control for Everything

All agent configs (AGENTS.md, CLAUDE.md, Skills, hooks) must be version-controlled alongside code. Changes to CLAUDE.md should go through the same PR review as application code.

### Section Checklist

- [ ] Agent sandbox with network egress controls and file restrictions
- [ ] No agent write access to production
- [ ] Risk-tiered approval process defined
- [ ] All prompts, Skills, CLAUDE.md version-controlled and PR-reviewed
- [ ] Secrets isolated from agent environment
- [ ] Package names verified against registry before installation
- [ ] Supply chain scanning for transitive vulnerabilities
- [ ] Security scanning MCP integrated and configured for "security at inception"
- [ ] NVIDIA mandatory controls applied (network, workspace, config, lifecycle, approvals)
- [ ] SAST/DAST scanning in CI

---

## 14. Testing Strategy: The Ground Truth

In agent-driven development, tests *define* code. They are the specification, the acceptance criteria, the objective measure of "done."

### Tests as Specification

Write comprehensive failing tests from a specification, then implement until they pass — without modifying the tests. This provides objective guard rails that channel the agent toward correct behaviour. Confirm tests fail first, commit the failing tests as a checkpoint, then implement.

### The Broken Foundation Problem

Before starting any new work, verify the existing system works. Run `init.sh` at session start. A production-ready `init.sh` should include:

1. **Environment check** — verify `.env` file exists (warn, don't fail)
2. **Dependency check** — verify package manager is installed and lockfile is in sync
3. **Linter check** — run lint in quiet mode
4. **Test suite** — run full test suite
5. **Docs build** — verify documentation builds without errors (if applicable)
6. **Code intelligence** — verify MCP tools are installed (warn, don't fail on optional tools)

Use clear output symbols (pass/fail/warning) and a summary at the end. The agent should fix any failures before starting new work. Use `set -e` for strict mode but handle optional checks with `|| true` for graceful degradation.

### Testing Pyramid

- **Unit tests**: Run continuously during sessions. Fast feedback (<5s). Many of these.
- **Integration tests**: Run after each commit. Stable interfaces. Some of these.
- **E2E tests**: Run in CI before merge. Critical workflows. Few but essential.

E2E tests are 3-5x more expensive to maintain but resilient to refactoring — agents are remarkably good at writing code that passes unit tests while failing in integration.

### Section Checklist

- [ ] Failing tests written from specifications before implementation
- [ ] Existing test suite passes before any new agent task starts
- [ ] Unit tests run continuously during sessions (<5s feedback)
- [ ] E2E tests run in CI before merge
- [ ] Coverage gates prevent reduction on PRs
- [ ] Browser automation available for UI verification
- [ ] `init.sh` configured with real commands (not placeholders)

---

## 15. Eval-Driven Prompt Development

This section applies when your product contains AI agents — when prompts are testable artifacts, not just developer tools.

### EDD vs TDD

Traditional TDD uses binary pass/fail assertions. LLM outputs are probabilistic — thousands of valid responses exist for any prompt. Eval-Driven Development (EDD) defines **success thresholds** instead of binary assertions: "85% of outputs must score 4+ on the factual accuracy rubric."

### The Eval Workflow

1. **Define an eval dataset**: curated input/output pairs representing expected agent behaviour. Store in a dedicated directory (e.g. `evals/datasets/`).
2. **Run A/B comparison**: execute the same dataset against prompt variant A and variant B.
3. **Score with an eval-judge**: a secondary model or agent scores outputs on a rubric — factual accuracy, formatting compliance, hallucination rate, latency.
4. **Verdict**: **SHIP** (variant wins decisively) / **HOLD** (no significant difference) / **ITERATE** (variant loses or mixed results).

### Prompt Regression Testing

Add eval runs to CI. When a prompt changes, re-run evals and compare against the baseline. Block merge if accuracy drops below threshold. This prevents prompt regressions the same way unit tests prevent code regressions.

### Version-Control Prompts

Store prompt templates in dedicated files (e.g. `prompts/` or `backend/prompts/`), not inline in code. Track changes like any other code artifact. The conversation trace — initial query → intermediate reasoning → tool calls → final response — is the unit of evaluation.

### Section Checklist

- [ ] Eval dataset maintained with curated input/output pairs
- [ ] A/B comparison workflow for prompt variants
- [ ] Eval-judge scoring on defined rubric
- [ ] Prompt regression tests in CI
- [ ] Prompts stored in dedicated files, version-controlled
- [ ] Conversation traces used as evaluation unit

---

## Session Workflow: Putting It All Together (v7 Lite)

**Start every session:**
1. Read PROGRESS.md and auto-memory for current state
2. Run `./scripts/init.sh` and fix any failures before starting new work
3. Check `docs/adr/` for relevant prior architectural decisions
4. **NEW**: Use planner agent for any task with 2+ steps (not just 3+)

**Before implementing with external libraries:**
1. Check MCP docs server (Context7 or equivalent) for version-specific API docs
2. Check `docs/research/` for existing research notes
3. If neither covers it, create a research note using RESEARCH-TEMPLATE.md
4. **NEW**: Verify package exists in registry (npm/PyPI/crates.io) before installing
5. **NEW**: Quick risk check: Is this high-risk? (database, auth, payments, APIs) → Extra tests needed

**During implementation (ADLC Workflow & Triple Agent Audit):**
1. **Intent**: Clarify what you're building (1-2 sentences)
2. **Plan (Wave 1)**: Planner agent creates task DAG in plan.md
3. **Execute (Wave 2)**: Implementer + research-assistant work in parallel
   - Work in 30-minute sprints, clearing context between natural breakpoints
   - Use TDD: tests first, then implementation
4. **Triple Agent Audit (Wave 3-5)**:
   - **Test (Wave 3)**: Test-writer agent validates coverage, edge cases, and resilience
   - **Review (Wave 4)**: Code-reviewer agent provides logic, pattern, and security feedback
   - **Document (Wave 5)**: Docs-writer synchronizes documentation and `PROGRESS.md`
5. **Ship**: If high-risk → extra review + staging deploy. If low-risk → ship it!

**Smart defaults for different task types:**
- **High-risk tasks** (database, auth, payments, APIs):
  - Write extra tests (happy path + edge cases)
  - Deploy to staging/local test first
  - Document rollback plan in comments
  
- **Low-risk tasks** (docs, tests, formatting, internal refactoring):
  - Move fast, iterate
  - Ship and monitor
  
- **Medium tasks** (new features, refactoring with users):
  - Standard TDD flow
  - Ship with confidence

**End every session:**
1. Use the session-handoff skill to update PROGRESS.md
2. Save any strategic knowledge to auto-memory
3. Commit with descriptive messages that serve as session history
4. **NEW**: Quick velocity check: Did this feel faster than before? Track it.

**Pro tips for small teams**:
- Don't overthink risk—just be aware
- Tests are your safety net—write them
- Parallel execution is your friend—use multiple agents
- Deploy often—small deploys are safer
- Measure occasionally—are you actually faster?

---

## Bootstrapping a New Agentic Project (Manual Steps)

When you take this architecture to a *brand new project*, the AI cannot easily pull itself up by its own bootstraps without basic infrastructure. You (the human) must perform these exact manual steps before letting agents take over:

1. **Copy the Core Instructions**: Copy `AGENTS.md` and `CLAUDE.md` to the root.
2. **Create the Hook Directories**: `mkdir -p .claude/hooks .claude/rules .claude/skills`
3. **Modularize Rules**: Break down your monolithic rules into `.claude/rules/global.md`, `frontend.md`, etc.
4. **Implement Context Builder**: Create `.claude/hooks/session-start.sh` to compile `active-context.md` dynamically based on `$PWD`. Ensure you `chmod +x` it.
5. **Implement Auto-Formatters**: Create `.claude/hooks/format-file.sh` to run Prettier/Ruff silently on edited files. Make it executable.
6. **Implement Pre-Commits**: Create `.claude/hooks/pre-commit.sh` for lightweight validation before git commits. Make it executable.
7. **Wire `hooks.json`**: Copy `.claude/hooks.json` to map `PostToolUse` to the auto-formatter and `PreToolUse` to the pre-commit script.
8. **Create `init.sh`**: Create `scripts/init.sh` with graceful test/lint validations and wire `session-start.sh` to run at the very top. Make it executable (`chmod +x scripts/init.sh`).
9. **Configure MCPs**: Create `.claude/mcp.json` and add `context7`, `playwright`, `fetch`, etc.
10. **Establish State**: Create an empty `PROGRESS.md` and `feature_list.json`.

*Once these 10 manual steps are executed, the repository boundary is secured and fully agent-ready.*

---

## Master Checklist

### Agent Instruction Files
- [ ] Root AGENTS.md under 100 lines, universal rules only
- [ ] CLAUDE.md uses `@import AGENTS.md`, adds only Claude-specific behaviours
- [ ] CLAUDE.local.md in `.gitignore`
- [ ] `.github/copilot-instructions.md` symlinked to AGENTS.md
- [ ] `.github/instructions/*.instructions.md` exists for language/framework-specific rules
- [ ] Each `.instructions.md` file has `applyTo` and a focused single concern
- [ ] `.github/prompts/*.prompt.md` exists for repeatable one-shot workflows
- [ ] `.github/agents/*.agent.md` exists for specialized Copilot personas
- [ ] All negative instructions rewritten as positive directives
- [ ] Subdirectory CLAUDE.md at each major code boundary (lazy-loaded)
- [ ] `.claude/rules/` with path-scoped rules (using `paths:` not `globs:`)
- [ ] Auto-memory reviewed monthly
- [ ] Granular permissions in settings.json (specific commands, not blanket approval)

### Project Structure
- [ ] Flat package structure navigable in under 2 minutes
- [ ] Tests, types, docs colocated with implementation
- [ ] No barrel files — direct import paths
- [ ] Code Health at 9.5+
- [ ] README.md at root and significant directories
- [ ] CONTRIBUTING.md as pattern source of truth

### Context Management
- [ ] `/clear` after every commit and task switch
- [ ] PROGRESS.md maintained across sessions
- [ ] Feature/task state in JSON
- [ ] Custom subagents in `.claude/agents/`
- [ ] Context never exceeds 85% utilisation
- [ ] `init.sh` configured with real commands
- [ ] Session-handoff skill installed and tested

### MCP Integration
- [ ] MCP servers configured in `.claude/mcp.json` (project-scoped)
- [ ] Knowledge retrieval server for version-specific library docs
- [ ] Code intelligence tools (semantic + structural) configured
- [ ] Browser automation MCP for E2E testing
- [ ] Agent-to-MCP routing defined
- [ ] Security scanning MCP integrated with review workflow
- [ ] **NEW**: MCP servers reviewed (stick to well-known ones with 1000+ stars)
- [ ] **NEW**: MCP permissions reviewed before installation

### Multi-Framework Patterns (v7 Lite)
- [ ] 3-6 specialized agents created (minimum: planner, implementer, reviewer)
- [ ] Planner agent creates task DAGs (dependencies explicit in plan.md)
- [ ] Triple Agent Audit protocol adopted (Wave 3-5: Test → Review → Document)
- [ ] ADLC workflow understood (Intent → Plan → Execute → Validate → Deploy)
- [ ] Parallel execution patterns used (research + implementation simultaneously)
- [ ] Risk awareness integrated (high-risk tasks get extra tests, not approvals)
- [ ] Test-writer agent validates implementation
- [ ] Research-assistant agent validates dependencies before installation

### Verification and Testing
- [ ] Testing tools installed (runners, browser automation, HTTP clients)
- [ ] API documentation injected for integrations
- [ ] Feature status from test results, not self-reporting
- [ ] Stop hooks enforce test/lint pass
- [ ] Copilot code review in repository settings uses custom instructions
- [ ] Failing tests before implementation
- [ ] E2E tests in CI before merge
- [ ] Pre-flight smoke test every session
- [ ] Eval dataset maintained for AI-agent product prompts
- [ ] Prompt regression tests in CI

### Skills and Documentation
- [ ] Skills directory with keyword-rich descriptions
- [ ] SKILL.md bodies under 500 lines
- [ ] Skills verify prerequisites before running
- [ ] Commit-ready skill with multi-step validation gate
- [ ] llms.txt at documentation root
- [ ] ADR directory with template
- [ ] Research findings in `docs/research/` with index and mandatory security assessment
- [ ] Session-handoff skill installed and tested
- [ ] Ship-it skill for release pipeline (document → commit → push → deploy)

### Workflow and Project Management
- [ ] Specifications with measurable acceptance criteria
- [ ] Tasks decomposed into 30-50 minute units
- [ ] Issues with acceptance criteria, files, and scope
- [ ] Plan mode before non-trivial tasks
- [ ] Definition of Done defined and enforced
- [ ] Wave protocol followed for each implementation cycle
- [ ] Research template used before implementation

### Security and Operations
- [ ] Agent sandbox with egress controls
- [ ] No agent access to production
- [ ] Risk-tiered approval process
- [ ] All configs version-controlled and PR-reviewed
- [ ] Three-layer hooks: Stop (pre-completion), PostToolUse (per-file), PreToolUse (conditional)
- [ ] Cross-model review where multiple IDE agents are available
- [ ] Observability proxy capturing sessions
- [ ] Dependencies verified against package registries
- [ ] Supply chain scanning for transitive vulnerabilities
- [ ] Security scanning budget documented and conserved (pre-commit only)
- [ ] Tool verification mandate: reviewers read actual output, never assume
- [ ] SAST/DAST in CI

---

## 16. Future-Proofing: 2026 Agentic AI Trends & Optimizations

As the industry shifts from assistive AI ("copilots") to agentic AI ("autonomous executors"), several key optimizations have emerged that deliver 10x efficiency gains. Apply these principles universally across any project:

### The "Antigravity" Paradigm
Modern platforms orchestrate specialized AI agents that execute complex workflows in parallel, interacting securely across terminal sandboxing and browser automation. Evolve your processes to rely on **artifact-driven oversight**, where agents output structured reports and design plans *before* large code implementations, reserving the human developer for high-level architectural verification.

### Codex / Base-Model Workflow Evolution
- **Context Window Management**: Feed narrow, summarized module profiles to the agent instead of massive repository dumps. Use `llms.txt` and `llms-full.txt` patterns to efficiently dictate context sprawl.
- **System-Level Pre-conditions**: Force agents through mandatory reasoning formats (like `PLANS.md` or `RESEARCH-TEMPLATE.md`) to establish durable boundary guidelines *before* generating logic.
- **Skills as Background Jobs**: Package strict Standard Operating Procedures (SOPs) inside `.claude/skills/` or similar folders. Agents only load these skills based on prompt keywords, minimizing baseline token burn.

### The Progression of `skills.md` and `agents.md`
In 2026, progressive disclosure is the gold standard for agent memory architecture:
- Maintain the root `AGENTS.md` file firmly under 100 lines for cross-IDE compliance.
- Keep individualized `SKILL.md` capabilities under 500 lines, relying entirely on concise YAML metadata for agent discovery.
- Employ strictly separated agent personas (e.g., `planner.agent.md`, `code-reviewer.agent.md`) so the LLM explicitly limits its behavioral tree and tool access to the requested role.

### Generic Multi-Agent Organization Chart
Transition from unstructured chat logic to an engineered, multi-agent pipeline. At minimum, scaffold the following subagents in any project repository:
1. **Planner Agent**: Read-only tooling. Analyzes issues, performs repository sweeps, and decomposes work into 30-minute verifiable tasks.
2. **Implementer Agent**: Write-context execution of a single task from the Planner.
3. **Research Assistant**: Validates external dependencies, open-source libraries, and APIs via terminal tooling *prior* to integration.
4. **Test Writer & Code Reviewer**: The QA Validation tier. These agents operate iteratively together until bugs and security regressions are resolved.
5. **Security Auditor**: Designed specifically to query dependency charts for CVEs, analyze CI/CD policies, and check for LLM-induced injection flaws (slopsquatting prevention).
6. **Docs Writer**: Synchronizes design changes strictly into `docs/` and `llms.txt`. 

### The 10x Efficiency Shift Blueprint
- **Retrieval-Augmented Implementation (RAI)**: Always instruct an agent to investigate a codebase first -> output a findings artifact -> completely clear its context window -> and implement code directly from the research artifact. This vastly reduces token dilution.
- **Autonomous QA / Terminal Tooling**: Give debugging agents the ability to run test suites in isolated terminal loops, mutating logic incrementally until tests pass.
- **Total SDLC Orchestration**: Offload repetitive project structures to agents. End-to-end AI deployment can compress traditional 20-engineer 6-month product arcs down to sub-10-week milestones by standardizing tasking pipelines.

### Spec-Driven Development for Agentic Reliability
The gap between a vague prompt and shippable code is where agent workflows break down. 
- **The 50-Minute Horizon**: AI models succeed reliably at 30-50 minute tasks. Decompose all feature work into small, verifiable chunks before generating code.
- **Implementation Contracts**: Use GitHub Issues or `PLANS.md` as strict contracts. A prompt should not say "build auth"; it should say "implement the JWT validation step from auth.md".
- **Two-Tier Agent Architecture**: Divide and conquer. Use a read-only **Planner Agent** to break down tasks, then pass those tasks to an **Implementer Agent** with explicit file targets. Never ask an implementer agent to design and build a large feature in one pass.

### Comprehensive Testing Suites for Rich, Robust Code
In an agent-driven world, tests are the literal definition of the code. Agents frequently hallucinate logic but rarely hallucinate syntax that passes a strict test suite.
- **Test-Driven Generation**: Write comprehensive, failing tests *before* writing implementation code. This provides the agent with an objective boundary to operate within.
- **Mutation and Optimization**: Dedicate a distinct **Test Writer Agent** to analyze test coverage and generate edge-case mutations. Agents are highly effective at finding untested paths when explicitly asked to break code.
- **The Broken Foundation Problem**: Before any session starts, a script (like `init.sh`) must verify the existing test suite passes. If an agent starts working on a broken foundation, it will generate compound errors. Never mark a task done without verifying logs of a passed test run.

### Evaluations and Observability Pipelines
Agentic software development requires treating AI inputs/outputs as system components that must be monitored. **Crucially, TDD and EDD must run as completely separate suites.** TDD asserts deterministic binary correctness of execution paths (usually isolated in `tests/`), while EDD measures probabilistic quality thresholds of AI outputs (typically stored in `evals/`). 

- **Eval-Driven Development (EDD) Suite**: For applications utilizing LLMs, replace binary TDD assertions with probabilistic success thresholds (e.g., "85% accuracy on formatting"). Run these evaluations in a dedicated, isolated CI pipeline step (`evals/runners`) to catch prompt regressions without making your deterministic unit tests flaky.
- **Token and Session Tracing**: Route agent API calls through observability gateways (like Langfuse or Braintrust). Unconstrained agents can fall into infinite loops or context abandonment. Monitor token burn per session and fail fast.
- **Hook-Based Audit Trails**: Use execution hooks to log every terminal command an agent runs, creating an immutable audit trail of the agent's actions during a CI or local run.

### The Tessl Paradigm: Skills-as-Code
Tessl represents the shift to **AI-Native Development Platforms**.
- **Skill Lifecycle**: Treat agent skills as versioned dependencies. Use Tessl to package, evaluate, and distribute internal "Source of Truth" skills across the organization.
- **Spec-Driven Maintenance**: Rely on Tessl's spec-driven approach to enable agents to perform autonomous maintenance (security patching, dependency updates) with deterministic validation.
- **Registry Pattern**: Centralize skills in a registry rather than duplicating `.claude/skills` across hundreds of repositories.

---

## 17. Operational Portability: The Cross-Platform Standard

To ensure agentic scripts and configurations work reliably across Linux, macOS, and Windows (via WSL or Git Bash), follow these "Write Once, Run Anywhere" principles.

### Cross-Platform Shell Scripting (Bash)
1. **The Shebang**: Always use `#!/usr/bin/env bash` for portability across `/bin/bash` locations.
2. **Robustness**: Always start with `set -euo pipefail` to catch silent failures.
3. **OS Detection**:
   ```bash
   if [[ "$OSTYPE" == "darwin"* ]]; then
     # macOS logic
   elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
     # Linux logic
   elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
     # Windows/Git Bash logic
   fi
   ```
4. **Tool Verification**: Use `command -v <tool>` to check for existence before execution. Avoid `which`.
5. **Pathing**: Always quote paths `"${MY_PATH}"` to handle spaces in Windows-style directories.

### Platform-Neutral Logic: Python Delegation
If a script exceeds 50 lines or requires complex file/network logic, **delegate to Python**.
- **Rationale**: Python's `os` and `pathlib` modules abstract away the differences between `\` and `/` or `CRLF` and `LF`.
- **Command**: `python3 -c "import os; ..."` or a dedicated script in `scripts/`.

### Windows Compatibility Gate
Every project should recommend **WSL (Windows Subsystem for Linux)** as the primary execution environment for agents on Windows. If WSL is unavailable, ensure `scripts/init.sh` is POSIX-compliant for Git Bash.

---

## 18. Standardized Project Customizations

A fully optimized agentic project should implement the following MCP servers, workflows, and agent personas to empower Antigravity and other IDE agents:

### Integrated MCP Servers
Configured in `.claude/mcp.json`:
- **`context7`** (`@upstash/context7-mcp`): Version-specific library docs retrieval.
- **`playwright`** (`@anthropic-ai/mcp-playwright`): E2E testing and UI verification.
- **`chrome-devtools`** (`chrome-devtools-mcp@latest`): Allowing agents to debug live web pages directly via Chrome Developer Tools.
- **`memstate-ai`** (`memstate-mcp`): Knowledge graph-based persistent memory for tracking project architecture across sessions.
- **`sequential-thinking`** (`@modelcontextprotocol/server-sequential-thinking`): Facilitates dynamic and reflective problem-solving sequences.
- **`fetch`** (`@modelcontextprotocol/server-fetch`): A lightweight server for grabbing and converting web content into lean Markdown.

### Agent Workflows & Personas
Stored natively in `.agents/workflows/` (for Antigravity `/slash-commands`) and synced to `.claude/skills/`:

**Core Loop Personas:**
- **Planner Agent** (`planner.md`): Operates in Read-Only mode to decompose features into verifiable tasks.
- **Implementer Agent** (`implementer.md`): Write-context execution of a single task at a time.
- **Research Assistant** (`research-assistant.md`): Validates external dependencies, libraries, and APIs via terminal tooling prior to integration.
- **Code Reviewer** (`code-reviewer.md`): Performs post-implementation QA by running linting and reading actual test outputs before deciding SHIP/ITERATE/BLOCK.
- **Security Auditor** (`security-auditor.md`): Scans dependencies (`npm audit`) and enforces workspace integrity constraints.
- **Docs Writer** (`docs-writer.md`): Synchronizes design changes strictly into `docs/` and `llms.txt`.

**Specialized Release & Scaffold Skills:**
- **Ship It** (`ship-it.md`): Orchestrates a rigid `test -> commit -> push -> deploy` pipeline. Uses `// turbo-all` for autonomous execution.
- **UI Scaffolder** (`ui-scaffolder.md`): High-leverage skill strictly tuned for building responsive Next.js/Vite + Tailwind CSS dashboard components automatically.
- **Session Handoff** (`session-handoff/SKILL.md`): Standardizes reading and writing state to `PROGRESS.md` and `feature_list.json` at session boundaries.
- **Triple Agent Audit** (`triple-agent-audit/SKILL.md`): Executes the Review, Test, Document wave protocol for industrial quality.

---

## 19. Operational Case Study: The Modo Pattern (Industrial-Grade Workflow)

The "Modo Pattern" is a distilled, hyper-efficient workflow executed during the Modo Energy MCP integration (April 2026). It demonstrates how to move from zero to a production-ready, highly robust MCP server in under 4 hours of agentic time.

### Phase 1: Spec-First Discovery Protocol
Never guess an API's structure.
- **Action**: Extract the system's source of truth (e.g., `swagger.json`, `schema.sql`, `proto` files).
- **Tooling**: Use a `planner` agent to map every endpoint/entity and write a formal `docs/research/api-map.md`.
- **Outcome**: 100% path accuracy and zero "endpoint hallucination" during implementation.

### Phase 2: The Instruction Foundation
Set the "laws of physics" for the repository.
- **Action**: Initialize `AGENTS.md` and customize `scripts/init.sh` to fail-hard on environment issues.
- **Logic**: Wire `init.sh` to verify Python/Node versions, lockfile integrity, and basic linter readiness.
- **Outcome**: Agents spend zero tokens fixing environment-missing-library errors because the gate is absolute.

### Phase 3: Domain-Oriented Modeling
Define the shapes before the logic.
- **Action**: Use Pydantic (Python) or Zod (TS) to define strict models for all request/response objects.
- **Logic**: Colocate models in `models/` subdirectories.
- **Outcome**: Type-safe logic with automatic validation, reducing 40% of runtime logic errors.

### Phase 4: The Triple Agent Audit (The Quality Gate)
Move from "it works for me" to "it's production-ready."
1. **The Reviewer**: Focuses on `lint`, `typing`, `dead code`, and `naming`.
2. **The Tester**: Focuses on `resilience` (404/500 handling), `edge cases` (empty lists), and `concurrency`.
3. **The Writer**: Focuses on `docstrings`, `README.md` sync, and `PROGRESS.md` history.
- **Protocol**: Run these as three distinct subagent passes using the `.claude/agents/*.md` personas.

### Phase 5: The Robustness Tier (Industrialization)
Layer performance and reliability on top of core tools.
- **Pattern A: Request Deduplication**: Use `SingleFlight` or equivalent to collapse concurrent burst requests to external APIs.
- **Pattern B: TTL L1 Caching**: Implement lightweight, in-memory TTL caching (e.g., `cachetools`) to minimize repeated API round-trips.
- **Pattern C: Meta-Tools**: Consolidate common analytical workflows (e.g., "List then Get Details") into single high-level agentic tools to reduce LLM tokens/latency.

### Phase 6: Deployment Verification
Research the target environment early.
- **Action**: Create `docs/research/deployment.md` characterizing CPU/RAM constraints and auth requirements of the target host (e.g., Horizon, AWS Lambda).
- **Outcome**: Zero-friction deployment because the code was built for the destination's constraints.

---

## 20. Master Checklist Update (Meta-Audit)

- [ ] Project has a formal `init.sh` that acts as a hard gate?
- [ ] Every API interaction is backed by a local Spec Discovery artifact?
- [ ] Models (Pydantic/Zod) exist for all external data boundaries?
- [ ] Triple Agent Audit protocol executed before final PR?
- [ ] Performance tier (Caching/Deduplication) verified in code?

---

## Sources

### Core Agentic Patterns (v6.0 base)
- Anthropic Engineering: Effective Harnesses, Context Engineering, Multi-Agent Systems (2025-2026)
- Anthropic: 2026 Agentic Coding Trends Report
- CodeScene: "Agentic AI Coding: Best Practice Patterns for Speed with Quality" (January 2026, peer-reviewed)
- Linux Foundation AAIF: AGENTS.md Specification (December 2025)
- Model Context Protocol: Specification (November 2025) + Best Practices Guide
- HumanLayer: "CLAUDE.md Best Practices" (2025)
- METR Research: "50-Minute Task Horizon" (March 2025)
- USENIX Security 2025: "Package Hallucination Study" (576K samples)
- Endor Labs: State of Dependency Management 2025 (slopsquatting)
- GitHub: Agentic Workflows Technical Preview (February 2026)
- GitHub Blog: "Multi-Agent Workflows Often Fail — Here's How to Engineer Ones That Don't" (2026)
- GitHub: Spec Kit and Agentic Workflows (February 2026)
- LangChain: State of Agent Engineering 2026

### Multi-Framework Insights (v7.0 Lite additions)
- LangChain/LangGraph: Graph-Based Workflow Patterns (2026)
- CrewAI: Role-Based Multi-Agent Collaboration Patterns (2026)
- Microsoft AutoGen + Semantic Kernel: Conversational Agent Patterns (2025-2026)
- Techmango & Wizr AI: Multi-Agent Performance Benchmarks (3x acceleration, 45% faster resolution)
- Dootrix, Accelirate, Codebridge: ADLC Framework Research (2026)

### Additional Research
- arxiv 2509.14745: "On the Use of Agentic Coding: An Empirical Study of Pull Requests on GitHub"
- CodeRabbit: State of AI vs Human Code Generation Report (2026)
- NVIDIA AI Red Team: Practical Security for Sandboxing Agentic Workflows (2025)
- Pragmatic Engineer: "A Pragmatic Guide to LLM Evals for Devs" (2025)
- Promptfoo, Braintrust, Fireworks Eval Protocol: Eval-Driven Development tools (2025-2026)
- earezki.com: "How I Cut My AI Coding Agent's Token Usage by 65%" (2026)
- Redis: LLM Token Optimization (2026)
- Armin Ronacher: "Go for Agentic Backend Development" (2025)
- Simon Willison: Skills Architecture, Hallucination Mitigation, 2025 Year in LLMs
- SFEIR Institute: Context Management Research (2025)

---

## Version History

### v7.2 Lite (Current) — The Industrial Edition
**Released**: April 11, 2026  
**Audience**: Developers building robust, cross-platform industrial-grade AI systems.

**What's New**:
- **Cross-Platform Standard** (Section 17): Best practices for Linux/Mac/Windows portability.
- **Enterprise Integrations**: Context 7, CodeRabbit, Tessl, and MCP Compass integrated.
- **Browser Automation**: Puppeteer/Playwright parity.

### v7.1 Lite — The Modo Edition
**Released**: April 2026  
**Audience**: Indie developers, startups, small teams (1-10 people), side projects, rapid prototyping

**What's New**:
- Multi-framework patterns (LangGraph, CrewAI, AutoGen) without framework dependencies
- ADLC (Agentic Development Life Cycle) simplified for fast iteration
- Lightweight risk awareness (no approval bureaucracy, just smart defaults)
- MCP security best practices (trust but verify)
- Enhanced Session Workflow with Wave Protocol and parallel execution
- 2026 paradigm shift documentation (Code scarcity → Thinking scarcity)
- 2026 benchmarks integrated (3x acceleration, 45% faster, 60% higher accuracy)

**What We Skipped** (Enterprise-only features):
- Formal approval workflows and multi-person review gates
- Audit logging and compliance documentation (GDPR, SOC 2, ISO 27001, HIPAA)
- Data classification frameworks
- Enterprise MCP governance (3-tier approval system)
- Formal risk classification with Level 0-4 ratings

**Line Count**: ~1,585 lines (+243 lines from v6.0)

### v6.0 — Foundation
**Released**: Early 2026  
**Audience**: All agentic developers

**Core Content**:
- 15 core sections covering all agentic best practices
- AGENTS.md and instruction architecture
- MCP integration, Skills, Context Management
- Testing strategy, Security guardrails, Hallucination prevention
- Session workflow and Master Checklist

**Line Count**: 1,342 lines (identical to v5.1)

### v5.1 — Original
**Released**: Late 2025  
**Audience**: Early adopters

**Foundation**:
- First comprehensive operational playbook for IDE coding agents
- Grounded in empirical research (Anthropic, CodeScene, Linux Foundation)
- Established patterns still used in all subsequent versions

**Line Count**: 1,341 lines

---

## Choosing Your Version

**Use v7.0 Lite** (this version) if:
- ✅ You're a startup, indie developer, or small team (1-10 people)
- ✅ You want modern multi-framework patterns without overhead
- ✅ You value speed and iteration over formal processes
- ✅ You want the 3x acceleration benefits without enterprise complexity
- ✅ You're building MVPs, side projects, or rapid prototypes

**Use v7.0 Enterprise** if:
- 🏢 You're in a regulated industry (finance, healthcare, government)
- 🏢 You need audit trails and compliance documentation
- 🏢 You have 10+ developers or multiple teams
- 🏢 You need formal approval workflows
- 🏢 You're integrating with existing enterprise governance

**Use v6.0** if:
- 📖 You want just the core patterns without any v7 additions
- 📖 You're uncertain about multi-framework approaches
- 📖 You prefer the original, minimal playbook

**Recommendation**: Start with v7.0 Lite. Upgrade to Enterprise only when you need formal governance.

---

**Status**: Production-Ready for Non-Enterprise Use ✅  
**License**: MIT (assumed, check with your legal team)  
**Contributors**: Community-driven, research-backed  
**Last Updated**: April 11, 2026
