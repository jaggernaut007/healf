# Setup Guide

This guide will walk you through setting up the Healf Health Intelligence Engine for local development and production use.

## Prerequisites

- **Python 3.12+**: The core logic uses modern Python features.
- **uv**: The project uses `uv` for lightning-fast package management. [Install uv](https://github.com/astral-sh/uv).
- **Neo4j**: A Neo4j instance is required for the Knowledge Graph. We recommend [Neo4j AuraDB](https://neo4j.com/cloud/aura/) for a managed cloud instance, or you can run it locally via Docker.

## 1. Clone the Repository

```bash
git clone <repository-url>
cd healf
```

## 2. Environment Configuration

Create a `.env` file in the root directory and populate it with your credentials:

```bash
# LLM & Extraction
OPENAI_API_KEY=sk-...

# Web Scraping
FIRECRAWL_API_KEY=fc-...

# Knowledge Graph (Neo4j)
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j  # Default is 'neo4j'

# Optional: Observability
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
```

## 3. Initialize the Environment

Run the initialization script. This will create a virtual environment, install dependencies, and install the project in editable mode.

```bash
chmod +x scripts/init.sh
./scripts/init.sh
```

## 4. Verify Installation

Run the smoke test to ensure all CLI components are properly wired:

```bash
uv run invoke smoke
```

If you see the tests pass successfully, you are ready to go!

## Troubleshooting

- **Missing API Keys**: The pipeline will "fail-fast" if `FIRECRAWL_API_KEY` or `OPENAI_API_KEY` are missing.
- **Neo4j Connection**: Ensure your Neo4j instance is reachable and the credentials in `.env` match.
- **Python Version**: If `uv` fails to find Python 3.12, install it via your OS package manager or `pyenv`.
