# Usage Guide

The Healf Health Intelligence Engine is operated through a multi-phase pipeline. This guide covers how to run each phase using the CLI and task runner.

## Core Pipeline Overview

1.  **Enrichment**: Scrapes product web pages and grounds active ingredients against the NIH database.
2.  **Graph Build**: Infers relationships between products, ingredients, mechanisms, and symptoms to build a Knowledge Graph.
3.  **Orchestration**: A 5-agent conversational flow that answers user queries using the Knowledge Graph.

---

## 1. Enrichment Pipeline

Run the enrichment pipeline to process raw product URLs and generate structured product data.

```bash
uv run healf enrich
```

- **Input**: `data/raw_product_urls.json`
- **Output**: `data/enriched_products.json`

## 2. Knowledge Graph Build

Build the knowledge graph in Neo4j based on the enriched products and research documents.

```bash
# Standard build
uv run healf sync-graph

# Build with custom path
uv run healf sync-graph --products-path custom/path/enriched.json
```

- **Dependencies**: Requires `data/enriched_products.json` and documents in `data/research/`.

## 3. Agentic Orchestration (Discovery REPL)

Interact with the system using the stateful Consultative Discovery REPL. This mode supports multi-turn conversations and asks clarifying questions for ambiguous intents.

```bash
# Start an interactive session (no user profile by default)
uv run healf chat

# Run for a specific user to test personalization
uv run healf chat --user-id user_001

# Run in silent mode for a clean chat experience (suppresses background logs)
uv run healf chat -s
```

- **Options**:
  - `--silent` / `-s`: Suppress background logs and developer warnings for a clean conversational experience.
  - `--user-id` / `-u`: Simulate chat for a specific user ID from `data/user_profiles.json`.

#### Mock User Profiles
You can simulate different customer scenarios using the `--user-id` flag:

| User ID | Name | Focus | Key Context |
| :--- | :--- | :--- | :--- |
| `user_001` | Sarah | Energy & Sleep | Low Ferritin, seasonal allergies. |
| `user_002` | Mark | Recovery & Joints | Elevated CRP, knee inflammation. |
| `user_003` | Elena | Gut Health | IBS-C, low B12. |


---

## Task Automation (Invoke)

We use `invoke` to simplify common developer tasks.

| Command | Description |
| :--- | :--- |
| `uv run invoke test` | Run the full test suite. |
| `uv run invoke lint` | Run the linter (ruff). |
| `uv run invoke smoke` | Run a quick smoke test of the CLI. |
| `uv run invoke check` | Combined lint and test pass. |

---

## Advanced Usage

### Customizing Inference Rules
You can modify the graph inference logic by editing `data/research/graph_inference_rules.json`. Each rule maps ingredient terms to specific mechanisms and symptoms supported by research (PMIDs).

### Safety Guardrails
The orchestration layer applies deterministic heuristic block lists. It then uses a Dynamic Cognitive Classification (Coordinator Node) via structured LLM outputs to evaluate safety intent and routing before further processing.

### Observability
If `enable_observability` is on (default), the system will attempt to export traces to a Phoenix collector. You can view these by running a Phoenix server locally.
