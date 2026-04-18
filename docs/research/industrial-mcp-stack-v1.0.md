# Research: Industrial MCP Stack (Antigravity/Gemini)

**Stack Version:** v1.0.0
**Status:** Current
**Model Target:** Gemini 3.1 Pro / Flash

## Sources Consulted
| Source | URL | Date accessed |
|--------|-----|---------------|
| Industrial Agentic Guide v7.2 | docs/agentic-guide-v7.2-industrial.md | 2026-04-18 |
| Nexus-MCP Docs | https://github.com/mcp-server/nexus-mcp | 2026-04-18 |
| Memstate Docs | https://github.com/memstate/mcp | 2026-04-18 |

## The Correct Approach (Industrial Patterns)

### 1. Nexus-MCP (Hybrid Intelligence)
- **Search**: Use for hybrid (vector + BM25) codebase discovery.
- **Remember/Recall**: Use to store architectural invariants that Gemini should not violate during long-running orchestration sessions.
- **Impact**: Mandatory pre-flight check before any file modification in `src/agent/`.

### 2. Memstate-AI (Persistent Context)
- **Architecture**: Store the "State Machine Definition" from `orchestrator.py` in Memstate to ensure cross-session continuity when debugging agent loops.
- **Handoff**: Use in the `session-handoff` skill to checkpoint the current "KG-RAG" graph state.

### 3. Playwright & Chrome-DevTools
- **Verification**: Use for E2E testing of the API layer if it were to have a UI, or for visual verification of graph generated artifacts.
- **Debugging**: Use `chrome-devtools` to inspect local browser-based testing sessions.

## What We Ruled Out (and Why)
| Approach | Why Rejected |
|----------|--------------|
| Broad Shell Access | Violates Antigravity Rule 69 (Security Guardrails). Restricted to whitelisted `uv run` commands. |
| Global Web Search | Replaced by Context7 (Tier 1) and Fetch (Tier 2) to reduce token waste and hallucination. |

## Security Assessment
- [x] CVE check: All @modelcontextprotocol and official Anthropic servers are verified.
- [x] Maintenance health: Primary servers (fetch, playwright, thinking) are actively maintained.
- [x] License compatibility: MIT/Apache 2.0.
- [x] Dependency tree risk: Minimal; using `npx` with pinned versions prevents slopsquatting.

## Implementation Roadmap (Phase 5)
1. **Meta-Tools**: Consolidate `search` + `impact` into a single "Pre-Flight Check" meta-tool.
2. **Persistence**: Wire `memstate-ai` into the `init.sh` and `session-handoff` hooks.
3. **Auditing**: Use `chrome-devtools` during the Triple Agent Audit of Phase 4 CLI features.
