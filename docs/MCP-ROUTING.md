# MCP Routing Policy

This repository uses role-specific MCP routing to reduce context waste and improve correctness.

## Routing Matrix

- planner: nexus-mcp, sequential-thinking
- implementer: nexus-mcp, context7
- research-assistant: context7, fetch, sequential-thinking, nexus-mcp
- test-writer: context7
- code-reviewer: nexus-mcp, context7
- security-auditor: nexus-mcp
- docs-writer: nexus-mcp, context7

## Mandatory Sequence

1. Discovery: use nexus-mcp search to find existing patterns.
2. Verification: use context7 for version-specific external API usage.
3. Impact: use caller/callee analysis before changing shared symbols.
4. Security: for dependency changes, run security checks before merge.

## Rules

- Use MCP-first retrieval before web search.
- Keep queries specific and token-efficient.
- Document key findings in docs/research notes.
- Do not perform broad edits without impact analysis.
