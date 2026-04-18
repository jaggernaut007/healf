# Typer CLI Framework (v0.12.3)

**Status:** Current
**Date:** 2026-04-17
**Version:** 0.12.3
**Purpose:** Modern Python CLI framework with automatic help generation and rich integration

## Official Documentation
- **Docs:** https://typer.tiangolo.com/
- **GitHub:** https://github.com/tiangolo/typer
- **PyPI:** https://pypi.org/project/typer/

## Core Capabilities
Typer is built on Click but adds automatic validation, help text generation, and tight Rich integration.

1. **Commands with Type Hints**
   ```python
   import typer
   
   app = typer.Typer()
   
   @app.command()
   def enrich(url: str = typer.Argument(...), 
              api_key: str = typer.Option(..., "--api-key")):
       """Enrich a product from URL."""
       print(f"Enriching {url}")
   
   if __name__ == "__main__":
       app()
   ```

2. **Built-in Validation**
   ```python
   @app.command()
   def process(
       product_id: str = typer.Argument(...),
       batch_size: int = typer.Option(10, "--batch-size", min=1, max=100)
   ):
       """Process products."""
   ```

3. **Rich Output Integration (automatic)**
   - Rich formatting is built-in
   - Error messages automatically styled
   - Progress bars work seamlessly

## Healf Phases
- **Phase 3:** Internal task runner for orchestration
- **Phase 4:** Public CLI for end users

## Phase 4 CLI Command Structure
```python
app = typer.Typer()

@app.command()
def enrich(input_json: str = typer.Argument(...)):
    """Phase 1: Scrape and extract products."""
    
@app.command()
def build_graph(products_json: str = typer.Argument(...)):
    """Phase 2: Build knowledge graph in Neo4j."""
    
@app.command()
def orchestrate(product_id: str = typer.Argument(...)):
    """Phase 3: Run agentic enrichment workflow."""

@app.command()
def preflight(component: str = typer.Option("all", "--component")):
    """Validate inputs and configuration."""

if __name__ == "__main__":
    app()
```

## Files Affected in Healf
- `src/cli.py` (Phase 4 CLI entrypoint)
- `src/main.py` (orchestration entry point)
- `scripts/healf.py` (user-facing CLI)

## Rejected Alternatives
- **Click:** Lower-level, requires manual validation
- **ArgumentParser:** Standard library but verbose
- **Fire:** Too implicit, harder to document

## Known Gotchas
1. Typer uses Click under the hood; some edge cases require Click knowledge
2. Async support requires `typer.run()` with async functions
3. Multi-level subcommands can become verbose

## Security Assessment
- ✅ No CVEs (as of 2026-04-17)
- ✅ Active maintenance (latest commit 2026-04-16)
- ✅ GitHub stargazers: 16K+
- ✅ Used by: Arize, Weights & Biases, etc.

## Healf Integration Plan
- Phase 4: Create `src/cli.py` with Typer commands for each phase
- Each command wraps existing Python APIs (enrichment_client, graph_builder)
- Rich output for progress, tables, and validation messages
- Environment variables via `typer.Option(..., envvar="VAR_NAME")`

