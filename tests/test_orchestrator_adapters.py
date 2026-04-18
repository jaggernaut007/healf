from __future__ import annotations

import json
import sys
from types import ModuleType
from pathlib import Path

import pytest

from src.agent.adapters import (
    build_default_evaluator,
    build_default_generator,
    build_default_observability_activator,
    build_default_retriever,
    build_default_safety_check,
)
from src.models.orchestration import RetrievalChunk


def test_default_safety_check_blocks_high_risk_query(tmp_path: Path) -> None:
    check = build_default_safety_check(tmp_path / "missing.co")

    decision = check("Can you diagnose my severe chest pain?")

    assert decision.allowed is False
    assert decision.reason is not None


def test_default_safety_check_blocks_phrase_from_config(tmp_path: Path) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: rare symptom\n", encoding="utf-8")
    check = build_default_safety_check(policy_path)

    decision = check("Please diagnose this rare symptom")

    assert decision.allowed is False
    assert "rare symptom" in (decision.reason or "")


def test_default_safety_check_is_case_insensitive(tmp_path: Path) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: severe chest pain\n", encoding="utf-8")
    check = build_default_safety_check(policy_path)

    decision = check("Is this SEVERE CHEST PAIN dangerous?")

    assert decision.allowed is False
    assert "severe chest pain" in (decision.reason or "")


def test_default_safety_check_defaults_when_config_has_no_policy(tmp_path: Path) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")
    check = build_default_safety_check(policy_path)

    decision = check("Can you diagnose this issue?")

    assert decision.allowed is False
    assert "diagnose" in (decision.reason or "")


def test_phrase_block_happens_before_nemo_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: blocked phrase\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            raise RuntimeError("NeMo should not be called for blocked phrase")

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())
    check = build_default_safety_check(policy_path)

    decision = check("This contains blocked phrase")

    assert decision.allowed is False
    assert "blocked phrase" in (decision.reason or "")


def test_default_retriever_returns_ranked_chunks(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "prod-01",
                    "canonical_name": "Magnesium Glycinate",
                    "active_ingredients": ["Magnesium"],
                    "mechanisms_of_action": ["Supports sleep quality"],
                },
                {
                    "sku": "prod-02",
                    "canonical_name": "Ashwagandha",
                    "active_ingredients": ["Ashwagandha"],
                    "mechanisms_of_action": ["Supports stress"],
                },
            ]
        ),
        encoding="utf-8",
    )
    retrieve = build_default_retriever(products_path=products_path)

    chunks = retrieve("sleep magnesium support")

    assert chunks
    assert chunks[0].source_id == "SKU:prod-01"


def test_default_generator_and_evaluator_gate_fail_without_context() -> None:
    generate = build_default_generator()
    evaluate = build_default_evaluator()

    draft = generate("sleep", [])
    gate = evaluate("sleep", draft, [], 0.8)

    assert gate.passed is False
    assert gate.score == 0.0
    assert gate.reason is not None


def test_guardrails_config_defines_medical_intent_flow() -> None:
    guardrails = Path("config/wellness_guard.co").read_text(encoding="utf-8")

    assert "define user express medical diagnosis" in guardrails
    assert "define bot refuse medical diagnosis" in guardrails
    assert "define flow medical_intent_block" in guardrails


def test_guardrails_project_config_wires_medical_intent_flow() -> None:
    config = Path("config/config.yml").read_text(encoding="utf-8")

    assert "rails:" in config
    assert "input:" in config
    assert "medical_intent_block" in config


def test_default_evaluator_uses_deepeval_when_environment_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    deepeval_metrics = ModuleType("deepeval.metrics")
    deepeval_test_case = ModuleType("deepeval.test_case")

    class _FaithfulnessMetric:
        def __init__(self, threshold: float):
            self.threshold = threshold
            self.score = 0.8

        def measure(self, test_case) -> None:
            return None

    class _AnswerRelevanceMetric:
        def __init__(self, threshold: float):
            self.threshold = threshold
            self.score = 0.6

        def measure(self, test_case) -> None:
            return None

    class _LLMTestCase:
        def __init__(self, **kwargs):
            self.payload = kwargs

    deepeval_metrics.FaithfulnessMetric = _FaithfulnessMetric
    deepeval_metrics.AnswerRelevanceMetric = _AnswerRelevanceMetric
    deepeval_test_case.LLMTestCase = _LLMTestCase

    monkeypatch.setitem(sys.modules, "deepeval.metrics", deepeval_metrics)
    monkeypatch.setitem(sys.modules, "deepeval.test_case", deepeval_test_case)

    evaluate = build_default_evaluator()
    gate = evaluate(
        "sleep support",
        "Draft response with evidence",
        [
            RetrievalChunk(source_id="PMID:1", content="Magnesium supports sleep quality."),
        ],
        0.7,
    )

    assert gate.passed is True
    assert gate.score == pytest.approx(0.7)


def test_observability_activator_runs_once_when_modules_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counters = {"launch": 0, "instrument": 0}

    phoenix_module = ModuleType("phoenix")

    def _launch_app() -> None:
        counters["launch"] += 1

    phoenix_module.launch_app = _launch_app

    langchain_module = ModuleType("openinference.instrumentation.langchain")

    class _Instrumentor:
        def instrument(self) -> None:
            counters["instrument"] += 1

    langchain_module.LangChainInstrumentor = _Instrumentor

    monkeypatch.setitem(sys.modules, "phoenix", phoenix_module)
    monkeypatch.setitem(sys.modules, "openinference.instrumentation.langchain", langchain_module)
    monkeypatch.setattr("src.agent.adapters._OBSERVABILITY_ACTIVE", False)

    activate = build_default_observability_activator()

    activate()
    activate()

    assert counters["launch"] == 1
    assert counters["instrument"] == 1
