from pathlib import Path
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown
from src.enrichment import run_enrichment_pipeline
from src.graph_builder import run_graph_build
from src.agent.orchestrator import AgentOrchestrator
from src.models.orchestration import OrchestrationRequest

# Load env immediately
load_dotenv()

app = typer.Typer(help="Healf Rich Operator CLI")
console = Console()

@app.command()
def enrich():
    """Trigger the data/enrichment pipeline with progress bar."""
    console.print(Panel("[bold green]Starting Data Enrichment Pipeline[/bold green]"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Enriching products...", total=100)
        try:
            run_enrichment_pipeline()
            progress.update(task, completed=100)
            console.print("[bold green]Enrichment complete![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Enrichment failed:[/bold red] {e}")
            raise typer.Exit(1)

@app.command(name="sync-graph")
def sync_graph(
    products_path: Path = typer.Option(Path("data/enriched_products.json"), help="Path to enriched products."),
):
    """Trigger Neo4j ingestion and output final state table."""
    console.print(Panel("[bold cyan]Syncing Knowledge Graph to Neo4j[/bold cyan]"))
    
    try:
        result = run_graph_build(enriched_products_path=products_path)
        
        table = Table(title="Neo4j Sync Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Nodes Added/Updated", str(result.products_loaded + result.research_documents_loaded))
        table.add_row("Edges Merged", str(result.triples_written))
        table.add_row("Database Status", "ONLINE")
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Sync failed:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def chat(
    silent: bool = typer.Option(False, "--silent", "-s", help="Suppress background logs and developer warnings for a clean conversational experience.")
):
    """Local REPL for testing the LangGraph agent."""
    console.print(Panel("[bold magenta]Healf Operator Chat REPL[/bold magenta]"))
    
    if silent:
        import logging
        logging.getLogger().setLevel(logging.ERROR)
        
    # Initialize after env load
    orchestrator = AgentOrchestrator.build_default()
    chat_history = []
    
    while True:
        query = typer.prompt("Operator")
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        request = OrchestrationRequest(user_query=query, chat_history=chat_history)
        
        with console.status("[bold yellow]Agent Thinking...", spinner="dots"):
            result = orchestrator.run(request)
            
        if result.status == "ok":
            console.print(Markdown(result.response_text or "No response"))
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": result.response_text or ""})
        elif result.status == "blocked":
            console.print(f"[bold yellow]Blocked:[/bold yellow] {result.safety.reason if result.safety else 'Safety violation'}")
        else:
            console.print(f"[bold red]Error:[/bold red] {result.error}")

if __name__ == "__main__":
    app()
