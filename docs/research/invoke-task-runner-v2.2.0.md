# Invoke Task Runner (v2.2.0)

**Status:** Current
**Date:** 2026-04-17
**Version:** 2.2.0
**Purpose:** Python-based task runner (make-like) with shell integration

## Official Documentation
- **Docs:** https://docs.pyinvoke.org/
- **GitHub:** https://github.com/pyinvoke/invoke
- **PyPI:** https://pypi.org/project/invoke/

## Core Capabilities
Invoke is a Python task execution library that replaces shell scripts and Makefiles with Python code.

1. **Task Definition**
   ```python
   from invoke import task, run
   
   @task
   def init(c):
       """Initialize environment."""
       c.run("uv venv")
       c.run("uv pip install -r requirements.txt")
   
   @task
   def test(c):
       """Run all tests."""
       c.run("pytest tests/ -v")
   
   @task
   def enrich(c, input_file="data/raw_product_urls.json"):
       """Run enrichment pipeline."""
       c.run(f"python src/enrichment.py --input {input_file}")
   ```

2. **Task Dependencies**
   ```python
   @task
   def build(c):
       """Build graph."""
       c.run("...")
   
   @task(pre=[init], post=[test])
   def full_pipeline(c):
       """Run full pipeline with setup and tests."""
   ```

3. **Namespacing**
   ```python
   from invoke import Collection, task
   
   @task
   def preflight(c): ...
   
   @task
   def build(c): ...
   
   graph = Collection('graph', preflight=preflight, build=build)
   
   # Usage: invoke graph.preflight, invoke graph.build
   ```

## Healf Phase 3-4 Tasks
```python
# tasks.py (or invoke.py)
from invoke import task, Collection

# Phase 1: Enrichment
@task
def enrich(c, input_json="data/raw_product_urls.json"):
    """Scrape and enrich products."""
    c.run(f"python src/enrichment.py --input {input_json}")

# Phase 2: Graph
@task
def graph_preflight(c):
    """Validate graph inputs."""
    c.run("python -m src.graph_builder --preflight")

@task
def graph_build(c):
    """Ingest into Neo4j."""
    c.run("python -m src.graph_builder")

# Phase 3: Orchestration
@task
def orchestrate(c, product_id):
    """Run agentic workflow for product."""
    c.run(f"python src/orchestrator.py --product {product_id}")

# Development
@task
def test(c):
    """Run all tests."""
    c.run("pytest tests/ -v --cov=src")

@task
def lint(c):
    """Run linting."""
    c.run("ruff check src/ tests/")

@task
def format_code(c):
    """Format code."""
    c.run("ruff format src/ tests/")

# Namespacing
graph_ns = Collection('graph', preflight=graph_preflight, build=graph_build)
dev_ns = Collection('dev', test=test, lint=lint, format=format_code)

ns = Collection(graph=graph_ns, dev=dev_ns, 
                enrich=enrich, orchestrate=orchestrate)

# Usage:
# invoke graph.preflight
# invoke graph.build
# invoke dev.test
# invoke orchestrate --product-id prod-01
```

## Files Affected in Healf
- `tasks.py` or `invoke.py` (Phase 3-4 task definitions)
- `Makefile` (optional; can be replaced by invoke)
- `scripts/init.sh` (can call `invoke init`)

## Rejected Alternatives
- **Makefile:** Shell-based, harder to maintain for Python projects
- **Shell scripts:** No dependency tracking, manual ordering
- **Just:** Too minimal for complex workflows

## Known Gotchas
1. Tasks run in shell context; environment variables don't automatically propagate
2. Working directory matters; use `c.cd()` for nested paths
3. `c.run()` returns stdout; capture with `result = c.run(..., hide=True)`

## Security Assessment
- ✅ No CVEs (as of 2026-04-17)
- ✅ Active maintenance (latest commit 2026-04-10)
- ✅ GitHub stargazers: 4.2K+
- ✅ Used by major Python projects

## Healf Integration Plan
- Create `tasks.py` with Invoke tasks for all phases
- Replace `scripts/init.sh` logic with `invoke init`
- Provide `invoke full_pipeline` for end-to-end runs
- Easy local testing: `invoke test`, `invoke lint`

