import json
import pytest
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import OrchestrationRequest

def load_eval_dataset():
    with open("evals/datasets/golden_dataset.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_eval_dataset())
def test_orchestration_quality(case):
    """
    Industrial Quality Gate: Measures Faithfulness and Relevance of the 5-agent pipeline.
    """
    # 1. Setup Orchestrator
    config = OrchestrationConfig(evaluation_threshold=0.7, enable_observability=False)
    orchestrator = AgentOrchestrator.build_default(config=config)
    
    # 2. Execute Pipeline
    request = OrchestrationRequest(user_query=case["input"])
    result = orchestrator.run(request)
    
    # 3. Handle failure cases (cannot evaluate if pipeline crashed)
    if result.status != "ok":
        pytest.fail(f"Pipeline failed for input '{case['input']}': {result.error}")

    # 4. DeepEval Test Case
    test_case = LLMTestCase(
        input=case["input"],
        actual_output=result.response_text,
        expected_output=case["expected_output"],
        retrieval_context=case["context"]
    )
    
    # 5. Metrics (Thresholds aligned with ADR-0007)
    # Thresholds are 0.7 to account for Gemini's variability in industrial settings.
    faithfulness_metric = FaithfulnessMetric(threshold=0.7)
    relevance_metric = AnswerRelevancyMetric(threshold=0.7)
    
    # 6. Evaluation
    faithfulness_metric.measure(test_case)
    relevance_metric.measure(test_case)
    
    # 7. Assertions
    assert faithfulness_metric.is_successful(), f"Faithfulness failed: {faithfulness_metric.score}"
    assert relevance_metric.is_successful(), f"Relevance failed: {relevance_metric.score}"

if __name__ == "__main__":
    # Allow manual execution via python script
    pytest.main([__file__])
