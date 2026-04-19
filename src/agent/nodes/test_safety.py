from __future__ import annotations

import pytest
from src.agent.nodes import build_default_safety_check
from src.models.orchestration import IntentClassification

def test_safety_check_blocks_clinical_diagnosis() -> None:
    check = build_default_safety_check()
    
    # "diagnose" matches first heuristic
    classification = check("Can you diagnose my severe chest pain?")
    
    assert classification.is_clinical_diagnosis_request is True
    assert "diagnose" in classification.reasoning.lower()

def test_safety_check_passes_wellness_query(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockCompletions:
        def create(self, **kwargs):
            return IntentClassification(
                is_clinical_diagnosis_request=False,
                primary_domain="sleep",
                requires_discovery=False,
                reasoning="Wellness query about sleep."
            )

    class MockChat:
        @property
        def completions(self):
            return MockCompletions()

    class MockEmbeddings:
        def create(self, **kwargs):
            class MockData:
                def __init__(self):
                    self.embedding = [0.1] * 1536
            class MockResponse:
                def __init__(self):
                    self.data = [MockData()]
            return MockResponse()

    class MockClient:
        @property
        def chat(self):
            return MockChat()
            
        @property
        def embeddings(self):
            return MockEmbeddings()

    monkeypatch.setattr("instructor.from_openai", lambda *_: MockClient())
    
    check = build_default_safety_check()
    classification = check("What is good for sleep?")
    
    assert classification.is_clinical_diagnosis_request is False
    assert classification.primary_domain == "sleep"
    assert classification.requires_discovery is False

def test_safety_check_triggers_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockCompletions:
        def create(self, **kwargs):
            return IntentClassification(
                is_clinical_diagnosis_request=False,
                primary_domain="general",
                requires_discovery=True,
                reasoning="Ambiguous query."
            )

    class MockChat:
        @property
        def completions(self):
            return MockCompletions()

    class MockEmbeddings:
        def create(self, **kwargs):
            class MockData:
                def __init__(self):
                    self.embedding = [0.1] * 1536
            class MockResponse:
                def __init__(self):
                    self.data = [MockData()]
            return MockResponse()

    class MockClient:
        @property
        def chat(self):
            return MockChat()
            
        @property
        def embeddings(self):
            return MockEmbeddings()

    monkeypatch.setattr("instructor.from_openai", lambda *_: MockClient())
    
    check = build_default_safety_check()
    classification = check("I want to feel better")
    
    assert classification.requires_discovery is True
