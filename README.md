# Healf Health Intelligence Engine

This repository implements a spec-driven health-tech assistant composed of:
1. Product enrichment pipeline
2. Knowledge graph builder
3. Agentic orchestration layer

Current orchestration implements the 5-agent KG-RAG conversational topology and is tested in the repository suite.

## Current Status
- Phase 1: Complete
- Phase 2: Complete
- Phase 3: Complete
- Phase 4: In progress

## Architecture Snapshot
Active flow:
- safety -> prompt rewrite -> intake router -> domain specialist -> graph retriever -> critic
- critic pass -> payload generator -> evaluation -> finalize
- critic fail -> specialist retry (bounded)

Phase 4 pending scope:
- CLI/task-runner operator surface and associated tests

## Safety and Quality Controls
- NeMo and policy phrase safety checks before specialist/retrieval/generation
- Dynamic structured safety decisions from NeMo (`allowed`, `reason`, `reason_code`, `risk_level`)
- Fail-closed behavior for unavailable, failed, or unparseable NeMo safety decisions
- Runtime schema validation for agent-node outputs and LLM-call boundaries
- Evaluation gate before final response
- Optional observability instrumentation
- Deterministic fallback behavior for unavailable external integrations

## Local Setup
1. Activate environment
- source .venv/bin/activate

2. Install dependencies (if needed)
- uv pip install -r requirements.txt

3. Run tests
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q

## Required Environment Variables
- OPENAI_API_KEY
- NEO4J_URI
- NEO4J_USERNAME
- NEO4J_PASSWORD
- FIRECRAWL_API_KEY

## Key Paths
- Enrichment: src/enrichment.py
- Graph builder: src/graph_builder.py
- Orchestrator: src/agent/orchestrator.py
- Adapters: src/agent/adapters.py
- Phase 3 plan: docs/pm-docs/plan_3.md
- Architecture doc: docs/pm-docs/architecture.md

## Submission Note
The architecture narrative is maintained at docs/pm-docs/architecture.md and should clearly separate implemented behavior from pending scope.
