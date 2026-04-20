from __future__ import annotations

import pytest
from src.agent.nodes import build_default_safety_check
from src.models.orchestration import IntentClassification


@pytest.fixture(autouse=True)
def _mock_neo4j_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent Neo4jPropertyGraphStore from requiring a live URI in unit tests."""
    class _MockSession:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def run(self, *a, **kw): return [{"name": "fatigue"}]

    class _MockClient:
        def session(self, **kw): return _MockSession()

    class _MockStore:
        @property
        def client(self): return _MockClient()

    monkeypatch.setattr(
        "llama_index.graph_stores.neo4j.Neo4jPropertyGraphStore",
        lambda **kw: _MockStore(),
    )


def test_safety_check_blocks_clinical_diagnosis() -> None:
    check = build_default_safety_check()

    # "diagnose" matches first heuristic — no LLM call needed
    classification = check("Can you diagnose my severe chest pain?")

    assert classification.is_clinical_diagnosis_request is True
    assert "diagnose" in classification.reasoning.lower()

def test_safety_check_passes_wellness_query(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Completions:
        def create(self, **kw):
            return IntentClassification(
                is_clinical_diagnosis_request=False,
                primary_domain="sleep",
                requires_discovery=False,
                reasoning="Wellness query about sleep.",
            )

    class _Chat:
        @property
        def completions(self): return _Completions()

    class _Embeddings:
        def create(self, **kw):
            class _D:
                embedding = [0.1] * 1536
            class _R:
                data = [_D()]
            return _R()

    class _Client:
        chat = _Chat()
        embeddings = _Embeddings()

    monkeypatch.setattr("instructor.from_openai", lambda *_: _Client())

    check = build_default_safety_check()
    classification = check("What is good for sleep?")

    assert classification.is_clinical_diagnosis_request is False
    assert classification.primary_domain == "sleep"
    assert classification.requires_discovery is False

def test_safety_check_triggers_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Completions:
        def create(self, **kw):
            return IntentClassification(
                is_clinical_diagnosis_request=False,
                primary_domain="general",
                requires_discovery=True,
                reasoning="Ambiguous query.",
            )

    class _Chat:
        @property
        def completions(self): return _Completions()

    class _Embeddings:
        def create(self, **kw):
            class _D:
                embedding = [0.1] * 1536
            class _R:
                data = [_D()]
            return _R()

    class _Client:
        chat = _Chat()
        embeddings = _Embeddings()

    monkeypatch.setattr("instructor.from_openai", lambda *_: _Client())

    check = build_default_safety_check()
    classification = check("I want to feel better")

    assert classification.requires_discovery is True
