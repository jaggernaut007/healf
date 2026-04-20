# Usage Guide

The Healf Health Intelligence Engine is operated through the `healf` CLI. 

### 🎥 Video Walkthrough
Watch the system in action: **[Healf Operations Walkthrough (YouTube)](https://youtu.be/CFmVON-Xw0k)**

> [!IMPORTANT]
> **Prerequisite**: Ensure you have run `./scripts/init.sh` to initialize the environment and install dependencies before running any commands.

You can run individual components or the entire end-to-end pipeline.

## 0. Full Intelligence Pipeline (Recommended)

To build the entire system from scratch—including product enrichment, research fetching, and knowledge graph construction—run the unified pipeline command:

```bash
uv run healf run
```

This command executes `enrich`, `research`, and `sync-graph` in sequence, providing a fully grounded knowledge base ready for chat.

---

## 1. Data Enrichment Pipeline

If you only need to process new products, run the enrichment command. This scrapes raw product URLs and generates structured data.

```bash
uv run healf enrich
```

- **Input**: `data/raw_product_urls.json`
- **Output**: `data/enriched_products.json`
- **Hardening**: The pipeline automatically validates URLs and skips malformed links. It also enforces a minimum content length (100 characters) to ensure scrapers haven't been blocked by bot walls; failed pages are skipped and excluded from the knowledge graph.
- **Authentication**: Grounding against NIH DSLD is free (1,000 req/hr). For higher volume, obtain a key at [https://dsld.od.nih.gov/api-guide](https://dsld.od.nih.gov/api-guide) and set `NIH_DATA_API_KEY` in `.env`.

## 2. Knowledge Graph Build

Build the knowledge graph in Neo4j based on the enriched products and research documents.

```bash
# Standard build
uv run healf sync-graph

# Build with custom path
uv run healf sync-graph --products-path custom/path/enriched.json
```

- **Dependencies**: Requires `data/enriched_products.json` and documents in `data/research/`.

## 3. Conversational Chat (REPL)

Interact with the system using the Consultative Discovery REPL. This mode supports multi-turn conversations, personalization via user profiles, and safety-first responses grounded in the Knowledge Graph.

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
| `uv run invoke -r scripts test` | Run the full test suite. |
| `uv run invoke -r scripts lint` | Run the linter (ruff). |
| `uv run invoke -r scripts smoke` | Run a quick smoke test of the CLI. |
| `uv run invoke -r scripts check` | Combined lint and test pass. |

---

## Advanced Usage

### Customizing Inference Rules
You can modify the graph inference logic by editing `data/research/graph_inference_rules.json`. Each rule maps ingredient terms to specific mechanisms and symptoms supported by research (PMIDs).

### Safety Guardrails
The orchestration layer applies deterministic heuristic block lists. It then uses a Dynamic Cognitive Classification (Coordinator Node) via structured LLM outputs to evaluate safety intent and routing before further processing.

### Observability
If `enable_observability` is on (default), the system will attempt to export traces to a Phoenix collector. You can view these by running a Phoenix server locally.
