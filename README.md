# Healf Health Intelligence Engine

Healf is a production-ready agentic framework for health-tech intelligence. It transforms raw product data and medical research into an actionable Knowledge Graph, orchestrated by a 5-agent conversational pipeline.

> **Note to Reviewers:** The **[ARCHITECTURE.md](ARCHITECTURE.md)** file is the primary artifact for evaluation, covering system design, safety models, and founding engineer decisions as requested in the task.

## 🚀 Quick Start & Setup

These setup instructions will get the system running on a clean machine in under 10 minutes.

### Prerequisites
- **Python 3.12+**: The core logic uses modern Python features.
- **uv**: The project uses `uv` for lightning-fast package management. [Install uv](https://github.com/astral-sh/uv).
- **Neo4j**: A Neo4j instance is required for the Knowledge Graph. We recommend [Neo4j AuraDB](https://neo4j.com/cloud/aura/) for a managed cloud instance, or you can run it locally via Docker.

### 1. Environment Configuration

Create a `.env` file in the root directory and populate it with your credentials:

```bash
# Required: LLM & Extraction
OPENAI_API_KEY=sk-...

# Required: Web Scraping
FIRECRAWL_API_KEY=fc-...

# Required: Knowledge Graph (Neo4j)
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j  # Default is 'neo4j'

# Optional: Observability
HEALF_ENABLE_OBSERVABILITY=false
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
```

### 2. Install & Initialize the Environment

Install the project dependencies and the `healf` CLI script using `uv sync`. This ensures the project is properly installed as an editable package in a dedicated virtual environment.

```bash
# Install dependencies and the 'healf' CLI
uv sync

# Run the initialization script for comprehensive environment verification
chmod +x scripts/init.sh
./scripts/init.sh
```

### 3. Verify Installation & Build Knowledge Base

1. **Verify CLI**: Run the smoke test to ensure the `healf` command is correctly installed and functional:
   ```bash
   uv run invoke smoke
   ```

2. **Build Knowledge Base**: Run the full intelligence pipeline to scrape products, fetch research from PubMed, and build the Neo4j graph:
   ```bash
   uv run healf run
   ```

3. **Start Chat**: Interact with the system:
   ```bash
   uv run healf chat
   ```

## 🏗️ Architecture

Healf implements an industrial-grade **KG-RAG (Knowledge Graph Retrieval-Augmented Generation)** topology:

- **Component 1: Enrichment**: Scrapes and grounds product data against NIH databases with premium clinical metadata extraction.
- **Component 2: Graph Builder**: Builds a Neo4j property graph with rule-based topological reasoning.
- **Component 3: Orchestration**: A multi-agent LangGraph workflow featuring Consultative Discovery and a Pharmacovigilance Critic.

## 🛡️ Safety & Quality

- **Fail-Closed Safety**: Safety controls block clinical diagnosis and dangerous intents.
- **Pharmacovigilance Critic**: Cross-references product evidence against user profiles (allergies, meds).
- **Quality Gates**: Heuristic and DeepEval-based metrics ensure faithfulness and relevancy.
- **Observability**: Built-in OpenInference instrumentation for tracing.

## 🛠️ Developer Workflow

We use `uv` and `invoke` for environment management and task automation.

- **Test**: `uv run invoke test` (core unit & integration suite)
- **Eval**: `uv run invoke eval` (DeepEval LLM-as-a-judge suite)

---

*For detailed technical specifications, see [SPEC.md](SPEC.md).*
