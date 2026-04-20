from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from src.cli import app
from src.models.orchestration import OrchestrationResult, SafetyDecision, IntentClassification

runner = CliRunner()

@patch("src.cli.AgentOrchestrator")
@patch("src.cli.typer.prompt")
def test_chat_history_includes_options(mock_prompt, mock_orchestrator_cls):
    # Setup mock orchestrator
    mock_orchestrator = MagicMock()
    mock_orchestrator_cls.build_default.return_value = mock_orchestrator
    
    # First turn: returns discovery with options
    result1 = OrchestrationResult(
        status="ok",
        response_text="What is your goal?",
        requires_clarification=True,
        options=["A: Energy", "B: Focus"],
        safety=SafetyDecision(allowed=True),
        intent_classification=IntentClassification(
            is_clinical_diagnosis_request=False,
            primary_domain="general",
            requires_discovery=True,
            reasoning="Broad query"
        )
    )
    
    # Second turn: returns success
    result2 = OrchestrationResult(
        status="ok",
        response_text="Here is a recommendation.",
        requires_clarification=False,
        safety=SafetyDecision(allowed=True)
    )
    
    mock_orchestrator.run.side_effect = [result1, result2]
    
    # Mock inputs: first query, second query, then exit
    mock_prompt.side_effect = ["I need help", "A", "exit"]
    
    result = runner.invoke(app, ["chat"])
    
    assert result.exit_code == 0
    
    # Check that the second call to orchestrator.run included history with options
    assert mock_orchestrator.run.call_count == 2
    
    second_request = mock_orchestrator.run.call_args_list[1][0][0]
    history = second_request.chat_history
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "I need help"
    assert history[1]["role"] == "assistant"
    assert "Options:" in history[1]["content"]
    assert "- A: Energy" in history[1]["content"]
    assert "- B: Focus" in history[1]["content"]
