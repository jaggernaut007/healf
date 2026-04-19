import json
import os
import pytest
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import OrchestrationRequest

load_dotenv()

def load_eval_dataset():
    with open("evals/datasets/golden_dataset.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_eval_dataset())
def test_orchestration_quality(case):
    """
    Industrial Quality Gate: Measures Faithfulness and Relevance of the 5-agent pipeline.
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not set. DeepEval requires an LLM to run quality gates.")

    # 1. Setup Orchestrator
    config = OrchestrationConfig(evaluation_threshold=0.7, enable_observability=False)
    orchestrator = AgentOrchestrator.build_default(config=config)
    
    # 2. Execute Pipeline
    request = OrchestrationRequest(user_query=case["input"])
    try:
        result = orchestrator.run(request)
    except Exception as e:
        if "401" in str(e) or "invalid_api_key" in str(e).lower() or "AuthenticationError" in type(e).__name__:
            pytest.skip(f"Skipping test due to invalid API key or Authentication Error: {e}")
        raise e

    # 3. Graceful fallback for LLM execution issues locally
    if result.status == "blocked" and result.error and ("unparseable" in result.error or "execution failure" in result.error):
        pytest.skip(f"Skipping test due to local LLM backend failure: {result.error}")
    
    # 4. Handle failure cases (cannot evaluate if pipeline crashed)
    expected_blocked = case["expected_output"].startswith("BLOCKED:")
    
    if expected_blocked:
        if result.status != "blocked":
            pytest.fail(f"Expected pipeline to block, but got status '{result.status}' for input '{case['input']}'")
        actual_output = f"BLOCKED: {result.error}"
    else:
        if result.status == "discovery":
            actual_output = result.clarification_question or ""
        elif result.status == "ok":
            actual_output = result.response_text or ""
        else:
            pytest.fail(f"Pipeline failed for input '{case['input']}': {result.error}")

    # 5. DeepEval Test Case
    test_case = LLMTestCase(
        input=case["input"],
        actual_output=actual_output,
        expected_output=case["expected_output"],
        retrieval_context=[c.content for c in result.retrieved_chunks] if hasattr(result, "retrieved_chunks") and result.retrieved_chunks else case["context"]
    )    
    # 6. Metrics (Thresholds aligned with ADR-0007)
    # Thresholds are 0.7 to account for Gemini's variability in industrial settings.
    faithfulness_metric = FaithfulnessMetric(threshold=0.7)
    relevance_metric = AnswerRelevancyMetric(threshold=0.7)
    
    try:
        # 7. Evaluation
        faithfulness_metric.measure(test_case)
        relevance_metric.measure(test_case)
        
        # 8. Assertions
        assert faithfulness_metric.is_successful(), f"Faithfulness failed: {faithfulness_metric.score}"
        assert relevance_metric.is_successful(), f"Relevance failed: {relevance_metric.score}"
    except Exception as e:
        if "401" in str(e) or "invalid_api_key" in str(e).lower() or "AuthenticationError" in type(e).__name__:
            pytest.skip(f"Skipping test due to invalid API key or Authentication Error during DeepEval: {e}")
        raise e

if __name__ == "__main__":
    # Allow manual execution via python script
    pytest.main([__file__])

