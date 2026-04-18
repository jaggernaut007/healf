from typer.testing import CliRunner
from src.cli import app
from unittest.mock import MagicMock, patch

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "enrichment" in result.stdout
    assert "graph" in result.stdout
    assert "orchestration" in result.stdout

@patch("src.cli.run_enrichment_pipeline")
def test_enrichment_run_success(mock_run):
    result = runner.invoke(app, ["enrichment", "run"])
    assert result.exit_code == 0
    assert "Starting Enrichment Pipeline" in result.stdout
    mock_run.assert_called_once()

@patch("src.cli.run_graph_build")
def test_graph_build_success(mock_run):
    mock_run.return_value = MagicMock(products_loaded=1, research_documents_loaded=1, triples_written=1)
    result = runner.invoke(app, ["graph", "build"])
    assert result.exit_code == 0
    assert "Starting Graph Build" in result.stdout
    assert "Products loaded: 1" in result.stdout
    mock_run.assert_called_once()

@patch("src.cli.AgentOrchestrator.build_default")
def test_orchestration_run_success(mock_build):
    mock_orchestrator = MagicMock()
    mock_orchestrator.run.return_value = MagicMock(status="ok", response_text="Test response", citations=["SKU:1"])
    mock_build.return_value = mock_orchestrator
    
    result = runner.invoke(app, ["orchestration", "run", "what helps sleep"])
    assert result.exit_code == 0
    assert "Running Orchestration for query: what helps sleep" in result.stdout
    assert "Test response" in result.stdout
    assert "SKU:1" in result.stdout

def test_orchestration_run_blocked():
    with patch("src.cli.AgentOrchestrator.build_default") as mock_build:
        mock_orchestrator = MagicMock()
        mock_orchestrator.run.return_value = MagicMock(status="blocked", safety=MagicMock(reason="Safety reason"))
        mock_build.return_value = mock_orchestrator
        
        result = runner.invoke(app, ["orchestration", "run", "diagnose me"])
        assert result.exit_code == 0
        assert "Blocked: Safety reason" in result.stdout
