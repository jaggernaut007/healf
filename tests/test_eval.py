import pytest
from unittest.mock import MagicMock, patch
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import (
    OrchestrationRequest, 
    IntentClassification, 
    RewrittenQuery, 
    RoutingIntent, 
    GraphQueryPlan, 
    RetrievalChunk, 
    CriticDecision, 
    CriticFinding,
    PayloadDraft,
    EvaluationGate
)

def test_harm_of_omission_ssri_contraindication():
    """
    Test Case: User is on SSRIs; asks for a stress supplement.
    Assertion: Must flag SSRI contraindication in Critic node.
    """
    safety_check = MagicMock(return_value=IntentClassification(is_clinical_diagnosis_request=False, primary_domain="general", requires_discovery=False, reasoning="safe"))
    rewrite = MagicMock(return_value=RewrittenQuery(normalized_text="stress supplement", preserved_terms=["stress"]))
    route = MagicMock(return_value=RoutingIntent(domain="stress", risk_level="high"))
    specialize = MagicMock(return_value=GraphQueryPlan(operation="search", key_terms=["stress"], domain="stress", risk_level="high", retry_codes="", limit=3, read_only=True))
    retrieve = MagicMock(return_value=[RetrievalChunk(source_id="PROD-1", content="St. John's Wort")])
    
    def mock_critic(query, routing, chunks, retry_count, profile):
        if "SSRI" in profile.get("medications", []):
            return CriticDecision(
                passed=False,
                findings=[CriticFinding(code="MEDICATION_CAUTION", message="SSRI Contraindication detected for St. John's Wort", severity="high")],
                retryable=False
            )
        return CriticDecision(passed=True, findings=[])

    payload = MagicMock(return_value=PayloadDraft(response_text="Blocked recommendation"))
    evaluate = MagicMock(return_value=EvaluationGate(passed=True, score=1.0, threshold=0.7))
    
    orchestrator = AgentOrchestrator(
        config=OrchestrationConfig(),
        safety_check=safety_check,
        rewrite=rewrite,
        route=route,
        specialize=specialize,
        retrieve=retrieve,
        critic=mock_critic,
        generate_payload=payload,
        evaluate=evaluate
    )
    
    user_profile = {"medications": ["SSRI"]}
    request = OrchestrationRequest(
        user_query="Can I take St. John's Wort?",
        user_profile=user_profile
    )
    
    result = orchestrator.run(request)
    
    assert result.status == "ok"
    assert "Blocked recommendation" in result.response_text
    assert any(f.code == "MEDICATION_CAUTION" for f in result.validation_errors)

def test_critic_node_trajectory_invocation():
    pass
