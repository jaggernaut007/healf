# Research Notes

This directory contains pre-verified findings for external libraries, APIs, and architectural decisions.

## Purpose

Before implementing with any external library or API, create a research note here using `RESEARCH-TEMPLATE.md`. This prevents hallucination and version mismatches.

## Three-Tier Retrieval Pattern

1. **Tier 1 — MCP docs server** (Context7): Check first for version-specific docs
2. **Tier 2 — This directory**: Pre-verified findings with "What We Ruled Out"
3. **Tier 3 — Web search**: Last resort for current official documentation

## File Naming Convention

Use descriptive names with library versions:
- `stripe-api-v14.2.0.md`
- `nextjs-app-router-v14.md`
- `postgres-connection-pooling.md`

## Index

- See `docs/research/INDEX.md` for the maintained note catalog.
