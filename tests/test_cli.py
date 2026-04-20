from typer.testing import CliRunner
from src.cli import app
from unittest.mock import MagicMock, patch

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "enrich" in result.stdout
    assert "sync-graph" in result.stdout
    assert "chat" in result.stdout

@patch("src.cli.run_enrichment_pipeline")
def test_enrichment_run_success(mock_run):
    result = runner.invoke(app, ["enrich"])
    assert result.exit_code == 0
    assert "Starting Data Enrichment Pipeline" in result.stdout
    mock_run.assert_called_once()

@patch("src.cli.run_graph_build")
def test_graph_build_success(mock_run):
    mock_run.return_value = MagicMock(products_loaded=1, research_documents_loaded=1, triples_written=1)
    result = runner.invoke(app, ["sync-graph"])
    assert result.exit_code == 0
    assert "Syncing Knowledge Graph to Neo4j" in result.stdout
    assert "Nodes Added/Updated" in result.stdout
    mock_run.assert_called_once()



