# Project Progress

## Current Status
**Phase 2: Component 2 — Knowledge Graph Construction** has started, with scraper-backed PubMed intake and scraper-first product enrichment now explicitly in scope.

## What's Working
- **Phase 0: Initialization & Setup** is fully complete.
- **Phase 0.1: Initial Architectural Docs** is complete.
  - `docs/adr/0001-use-langgraph-for-orchestration.md` and `docs/adr/0002-use-uv-for-package-management.md` created.
  - `docs/research/firecrawl-api.md` and `docs/research/nemo-guardrails.md` created.
- **Phase 1: Enrichment Scaffolding & Client** is complete.
  - `data/raw_product_urls.json` input payload generated.
  - Mocked out `EnrichmentClient.fetch_nih_dsld_data` replaced with actual `requests` call that targets the NIH RxTerms/DSLD pattern.
  - Orchestration pipeline `src/enrichment.py` built to scrape Firecrawl, align `instructor` LLM extractions, and synthesize NIH contraindications.
  - Property-based tests (`pytest` & `hypothesis`) pass locally.

## What's In Progress
- Phase 2 inference mapping in `src/graph_builder.py` was migrated from hardcoded `if` branches to external rules loaded from `data/research/graph_inference_rules.json`.
- Phase 2 builder now fails fast if inference rules are missing/empty or if no graph triples can be inferred from current inputs.
- Phase 2 graph builder now has a CLI entrypoint (`python -m src.graph_builder`) with optional path overrides for products, research corpus, and inference rules.
- Phase 2 now includes a no-write preflight mode (`python -m src.graph_builder --preflight`) that validates inputs/rules and reports inferred triple diagnostics before AuraDB writes.
- Generated `data/enriched_products.json` via live enrichment run and verified preflight now passes (`products_loaded=3`, `triples_inferred=3`).
- Completed live AuraDB ingestion smoke test successfully using detected database name (`NEO4J_DATABASE=234c64b6`).
- Product scraping remains Firecrawl-first in Phase 1, and PubMed abstracts will be captured via scraper-backed artifacts in Phase 2 instead of manual notes.
- Added focus/performance corpus context for caffeine + L-theanine, citicoline (CDP-choline), L-tyrosine, Bacopa monnieri, and Rhodiola rosea with corresponding PMID files and deterministic inference rules.

## Blocked / Pending
- Keep graph inference behavior data-driven so adding new ingredient/mechanism/symptom relationships does not require Python code edits.
1. Align `.env` naming and defaults: persist `NEO4J_USERNAME` and `NEO4J_DATABASE` to avoid manual export mapping.
2. Decide whether to reconcile the phase 1 NIH grounding mismatch or amend the spec note.
3. Expand enrichment input set beyond magnesium-heavy outputs and rerun graph ingestion.

## Next Steps
1. Set up Neo4j AuraDB integration for GraphRAG construction.
2. Scrape PubMed literature into `data/research` and keep one clear file per PMID.
3. Ingest `data/enriched_products.json` nodes and relationships into Python.

## Recent Decisions
- We wrapped the NIH DSLD API in a secure try/except struct inside the enrichment pipeline and built out the top-level executor script (`src/enrichment.py`) as mandated by the take-home `plan_3.md` definition.
- Phase 2 now uses a deterministic corpus-to-triple mapper as the first implementation slice, with idempotent `MERGE` Cypher and mocked Neo4j writes in tests.
- `uv` is now the active workflow for environment and test execution (`uv venv`, `uv pip install`, `uv run pytest`).
- Firecrawl client integration was updated to use current SDK scrape API compatibility (`scrape`) with fallback support.
