That is a fantastic addition. If you are going to build an internal CLI for operations (like triggering the enrichment pipeline or running a local graph sync), it shouldn't just dump raw JSON logs. It should look and feel like a premium developer tool.

Adding rich (the standard Python library for beautiful terminal formatting) perfectly bridges the gap between backend logic and a great developer experience. We will use rich.console, rich.table, and rich.progress to make the CLI readable and professional.

Here is the finalized Phase 4 execution plan, now incorporating the rich CLI upgrade while keeping the FastAPI boundary as the ultimate production target.

Finalized Phase 4 Execution Plan: API, Rich CLI & Release
Objective: Secure the system boundary for production via FastAPI, build a premium operational CLI using rich, and finalize all release-readiness documentation.

Phase A: Baseline Lock & Dependency Update
Scope Alignment: The primary product deliverable is the FastAPI boundary. The secondary operational deliverable is the Rich CLI.

Dependency Addition: Add rich to requirements.txt (or via uv add rich).

Record Non-Goals: No new agent nodes. No database schema changes.

Phase B: The API Boundary (Primary Focus)
FastAPI Implementation (api.py): Wrap the orchestrator.py logic in a robust FastAPI endpoint (POST /api/chat).

SlowAPI Rate Limiting: Implement strict rate limiting (e.g., 5/minute) to prevent abuse.

Payload Validation: Enforce strict Pydantic validation on incoming requests to prevent malicious input.

Phase C: The "Rich" Operator CLI (Secondary Focus)
CLI Entrypoint (cli.py): Create a unified CLI using argparse or typer linked to a rich.console.Console.

Enrichment Command (healf-cli enrich): Wrap the Firecrawl/NIH DSLD scraping logic in a rich.progress bar so operators can see exact real-time progress across products.

Graph Sync Command (healf-cli sync-graph): Upon completing the Neo4j ingestion, output a rich.table summarizing the database state (e.g., Nodes Created, Edges Formed, Duplicate Skips).

Local Chat Command (healf-cli chat): Use rich.markdown to render the agent's Markdown and citations beautifully in the terminal for rapid local testing without hitting the FastAPI endpoint.

Phase D: Task-Runner & CI/CD Parity
Task Automation: Finalize a simple task runner (e.g., a Makefile) for make test, make lint, and make run-api.

Deterministic CI Parity: Ensure the local test commands exactly match what would run in a GitHub Actions pipeline.

Phase E: The Test Wave (DeepEval & Trajectory)
API Tests: Write pytest assertions for the FastAPI boundary (HTTP 429, HTTP 422).

Trajectory Evaluation (DeepEval): Execute the "Harm of Omission" test. Assert that complex queries successfully hit the Pharmacovigilance Critic node.

Regression Suite: Run PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q.

Phase F: Release Hardening & "Fail-Closed" Audit
Security Audit: Verify the "deny, not warn" philosophy is active in the Critic node.

Lint & Formatting: Run ruff or black to ensure code quality meets Series B standards.

Smoke Verification: Run a full end-to-end test (CLI Enrichment -> CLI Graph Sync -> API Request).

Phase G: Documentation Synchronization
ARCHITECTURE.md Update: Ensure the language reflects the Healf mindset.

Explicitly mention the "Fail-Closed Safety Gate".

Highlight the "Typed Memory Layer".

Detail the roadmap toward LATS and DSPy.

Note the use of rich for premium operational tooling.

Tracker Updates: Sync PROGRESS.md, feature_list.json, and todo.md.

Readiness Summary: Generate a final pass/fail summary mapping evidence to all Phase 4 criteria in SPEC.md.