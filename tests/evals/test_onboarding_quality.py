import os
import pytest
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, TurnRelevancyMetric
from deepeval.test_case import LLMTestCase, ConversationalTestCase, Turn
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import OrchestrationRequest
import json

def load_onboarding_dataset():
    with open("evals/datasets/onboarding_golden.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("scenario", load_onboarding_dataset())
def test_onboarding_conversation(scenario):
    """
    Multi-turn evaluation for Conversational Onboarding.
    Ensures the agent maintains persona and steers correctly across turns.
    """
    config = OrchestrationConfig(evaluation_threshold=0.7, enable_observability=False)
    orchestrator = AgentOrchestrator.build_default(config=config)
    
    chat_history = []
    test_cases = []

    for turn_data in scenario["turns"]:
        user_input = turn_data["input"]
        
        # 1. Run Orchestrator with history
        request = OrchestrationRequest(user_query=user_input, chat_history=chat_history)
        result = orchestrator.run(request)
        actual_output = result.response_text or result.clarification_question or ""
        
        # 2. Track for DeepEval as a sequence of Turns
        user_turn = Turn(role="user", content=user_input)
        assistant_turn = Turn(
            role="assistant", 
            content=actual_output,
            retrieval_context=[c.content for c in result.retrieved_chunks] if result.retrieved_chunks else []
        )
        test_cases.extend([user_turn, assistant_turn])
        
        # 3. Update history for next turn
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": actual_output})

    # 4. Evaluate the entire conversation
    conversational_test_case = ConversationalTestCase(turns=test_cases)
    
    # We use TurnRelevancyMetric to ensure the agent stayed on topic across the session
    metric = TurnRelevancyMetric(threshold=0.7)
    metric.measure(conversational_test_case)
    
    assert metric.is_successful(), f"Conversation flow failed: {metric.score}. Reason: {metric.reason}"
