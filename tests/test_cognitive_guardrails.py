from __future__ import annotations

import pytest
from pathlib import Path
from src.agent.adapters import build_default_safety_check
from src.models.orchestration import IntentClassification

def test_safety_check_blocks_clinical_diagnosis(tmp_path: Path) -> None:
    check = build_default_safety_check(tmp_path / "missing.co")
    
    # "diagnose" matches first
    classification = check("Can you diagnose my severe chest pain?")
    
    assert classification.is_clinical_diagnosis_request is True
    assert "diagnose" in classification.reasoning.lower()

def test_safety_check_blocks_custom_phrase(tmp_path: Path) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: custom bad thing\n", encoding="utf-8")
    check = build_default_safety_check(policy_path)
    
    classification = check("Tell me about custom bad thing")
    
    assert classification.is_clinical_diagnosis_request is True
    assert "custom bad thing" in classification.reasoning.lower()

def test_safety_check_passes_wellness_query(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
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

    class MockClient:
        @property
        def chat(self):
            return MockChat()

    monkeypatch.setattr("instructor.from_openai", lambda *_: MockClient())
    
    check = build_default_safety_check(tmp_path / "missing.co")
    classification = check("What is good for sleep?")
    
    assert classification.is_clinical_diagnosis_request is False
    assert classification.primary_domain == "sleep"
    assert classification.requires_discovery is False

def test_safety_check_triggers_discovery(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
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

    class MockClient:
        @property
        def chat(self):
            return MockChat()

    monkeypatch.setattr("instructor.from_openai", lambda *_: MockClient())
    
    check = build_default_safety_check(tmp_path / "missing.co")
    classification = check("I want to feel better")
    
    assert classification.requires_discovery is True
