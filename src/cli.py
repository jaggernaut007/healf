import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import sys

from src.enrichment import run_enrichment_pipeline
from src.graph_builder import run_graph_build
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import OrchestrationRequest

app = typer.Typer(help="Healf CLI for enrichment, graph building, and orchestration.")
console = Console()

enrichment_app = typer.Typer(help="Manage product enrichment.")
app.add_typer(enrichment_app, name="enrichment")

graph_app = typer.Typer(help="Manage knowledge graph.")
app.add_typer(graph_app, name="graph")

orchestration_app = typer.Typer(help="Manage agentic orchestration.")
app.add_typer(orchestration_app, name="orchestration")

@enrichment_app.command("run")
def enrichment_run():
    """Execute the enrichment pipeline."""
    console.print(Panel("[bold green]Starting Enrichment Pipeline...[/bold green]"))
    try:
        run_enrichment_pipeline()
        console.print("[bold green]Enrichment completed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Enrichment failed:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)

@graph_app.command("build")
def graph_build(
    products_path: Path = typer.Option(Path("data/enriched_products.json"), help="Path to enriched products."),
    research_dir: Path = typer.Option(Path("data/research"), help="Path to research documents."),
    rules_path: Path = typer.Option(Path("data/research/graph_inference_rules.json"), help="Path to inference rules."),
):
    """Execute the knowledge graph build process."""
    console.print(Panel("[bold green]Starting Graph Build...[/bold green]"))
    try:
        result = run_graph_build(
            enriched_products_path=products_path,
            research_dir=research_dir,
            inference_rules_path=rules_path
        )
        console.print(f"Products loaded: {result.products_loaded}")
        console.print(f"Research docs loaded: {result.research_documents_loaded}")
        console.print(f"Triples written: {result.triples_written}")
        console.print("[bold green]Graph build completed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Graph build failed:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)

@orchestration_app.command("run")
def orchestration_run(
    query: str = typer.Argument(..., help="User query for the orchestrator."),
    threshold: float = typer.Option(0.8, help="Evaluation threshold."),
    no_obs: bool = typer.Option(False, "--no-obs", help="Disable observability."),
):
    """Run the 5-agent conversational flow."""
    console.print(Panel(f"[bold green]Running Orchestration for query:[/bold green] {query}"))
    try:
        config = OrchestrationConfig(
            evaluation_threshold=threshold,
            enable_observability=not no_obs
        )
        orchestrator = AgentOrchestrator.build_default(config=config)
        request = OrchestrationRequest(user_query=query)
        result = orchestrator.run(request)
        
        if result.status == "ok":
            console.print(Panel(f"[bold cyan]Response:[/bold cyan]\n{result.response_text or ''}"))
            if result.citations:
                console.print(f"[bold]Citations:[/bold] {', '.join(result.citations)}")
        elif result.status == "blocked":
            reason = result.safety.reason if result.safety else "Unknown safety reason"
            console.print(f"[bold yellow]Blocked:[/bold yellow] {reason}", style="yellow")
        else:
            console.print(f"[bold red]Failed:[/bold red] {result.error}", style="red")
            
    except Exception as e:
        console.print(f"[bold red]Orchestration failed:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
