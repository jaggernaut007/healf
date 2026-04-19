# Healf Health Intelligence Engine

Healf is a production-ready agentic framework for health-tech intelligence. It transforms raw product data and medical research into an actionable Knowledge Graph, orchestrated by a 5-agent conversational pipeline.

## 🚀 Quick Start

1.  **Setup**: Follow the [Setup Guide](docs/SETUP.md) to configure your environment and Neo4j instance.
2.  **Usage**: See the [Usage Guide](docs/USAGE.md) for CLI commands and task automation.

## 🏗️ Architecture

Healf implements an industrial-grade **KG-RAG (Knowledge Graph Retrieval-Augmented Generation)** topology:

- **Phase 1: Enrichment**: Scrapes and grounds product data against NIH databases.
- **Phase 2: Graph Builder**: Builds a Neo4j property graph with rule-based inference.
- **Phase 3: Orchestration**: A multi-agent LangGraph workflow:
    - `Safety` -> `Rewrite` -> `Router` -> `Specialist` -> `Retrieval` -> `Critic` -> `Payload` -> `Evaluate`.
- **Phase 4: CLI/UX**: Structured operator surface via Typer and Rich.
- **Phase 5: Compliance**: Industrial-grade hardening, TTL caching, and EDD (Eval-Driven Development).

## 🛡️ Safety & Quality

- **Fail-Closed Safety**: Deterministic and LLM-based guardrails protect against medical misadvice.
- **Critic Loop**: Bounded retries ensure retrieval plans satisfy domain specialists.
- **Quality Gates**: DeepEval-ready evaluation metrics run before final response emission.
- **Observability**: Built-in OpenInference instrumentation for tracing and debugging.

## 🛠️ Developer Workflow

We use `uv` and `invoke` for environment management and task automation.

- **Init**: `./scripts/init.sh`
- **Test**: `uv run invoke test`
- **Smoke Test**: `uv run invoke smoke`

---

*For detailed technical specifications, see [SPEC.md](SPEC.md).*
