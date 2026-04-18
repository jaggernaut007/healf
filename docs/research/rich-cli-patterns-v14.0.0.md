# Rich CLI Patterns (v14.0.0)

**Status:** Current
**Date:** 2026-04-17
**Version:** 14.0.0
**Purpose:** Rich text formatting and progress visualization for CLI applications

## Official Documentation
- **Docs:** https://rich.readthedocs.io/en/latest/
- **GitHub:** https://github.com/Textualize/rich
- **PyPI:** https://pypi.org/project/rich/

## Core Capabilities
Rich is a Python library for rendering rich text and beautiful formatting in the terminal. Key features for CLI applications:

1. **Progress Bars & Live Displays**
   ```python
   from rich.progress import track
   from rich.live import Live
   from rich.table import Table
   
   for item in track(items, description="Processing..."):
       # process item
   ```

2. **Tables & Structured Output**
   ```python
   from rich.table import Table
   table = Table(title="Results")
   table.add_column("Name", style="cyan")
   table.add_row("Magnesium", "42.5 mg")
   console.print(table)
   ```

3. **Status & Spinners**
   ```python
   with console.status("[bold green]Processing..."):
       # long running operation
   ```

## Integration with Typer
Rich integrates seamlessly with Typer for CLI argument parsing + rich output:

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def main(product_name: str = typer.Argument(...)):
    with console.status(f"[bold green]Enriching {product_name}..."):
        # enrichment logic
    console.print("[green]✓ Complete[/green]")

if __name__ == "__main__":
    app()
```

## Files Affected in Healf
- `src/api/main.py` (future API logging/formatting)
- `src/cli.py` (Phase 4 CLI entrypoint)
- `scripts/init.sh` (progress visualization)

## Rejected Alternatives
- **Colorama:** Simpler but lacks tables, progress tracking
- **Click alone:** No rich formatting without additional setup

## Known Gotchas
1. Console output can be captured in tests; use `rich.get_console()` for testing
2. Progress bars don't work well with logging; use `Live` + custom handlers instead
3. Terminal width detection may fail in CI; set `Console(width=80)` explicitly

## Security Assessment
- ✅ No CVEs (as of 2026-04-17)
- ✅ Active maintenance (latest commit 2026-04-16)
- ✅ GitHub stargazers: 48K+
- ✅ Used by major projects (Apache Airflow, Typer, etc.)

## Healf Integration Notes
Use Rich for Phase 4 CLI to:
- Display enrichment progress as products are scraped/extracted
- Show graph builder ingestion stats in formatted tables
- Display preflight validation results with colored status indicators
- Stream real-time LangGraph orchestration state in Phase 3

