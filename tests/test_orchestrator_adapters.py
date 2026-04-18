from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from src.agent.adapters import (
    build_default_critic,
    build_default_evaluator,
    build_default_intake_router,
    build_default_observability_activator,
    build_default_payload_generator,
    build_default_prompt_rewriter,
    build_default_retriever,
    build_default_safety_check,
    build_default_specialist,
)
from src.models.orchestration import GraphQueryPlan, RetrievalChunk, RewrittenQuery, RoutingIntent


def test_default_safety_check_blocks_high_risk_query(tmp_path: Path) -> None:
    check = build_default_safety_check(tmp_path / "missing.co")

    decision = check("Can you diagnose my severe chest pain?")

    assert decision.allowed is False
    assert decision.reason_code == "POLICY_PHRASE_BLOCK"
    assert decision.risk_level == "high"
    assert decision.source == "policy"
    assert decision.reason is not None


def test_default_safety_check_blocks_phrase_from_config(tmp_path: Path) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: rare symptom\n", encoding="utf-8")
    check = build_default_safety_check(policy_path)

    decision = check("Please help with this rare symptom")

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


def test_default_safety_check_blocks_when_nemo_returns_refusal_signal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return "You should consult a medical professional"

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what helps sleep")

    assert decision.allowed is False
    assert decision.reason_code == "NEMO_DENY_FALLBACK"
    assert decision.source == "nemo"


def test_default_safety_check_falls_back_when_nemo_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            raise RuntimeError("nemo unavailable")

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is False
    assert decision.reason == "Blocked: safety guardrails execution failure"
    assert decision.reason_code == "GUARDRAILS_EXECUTION_FAILURE"
    assert decision.source == "system"


def test_default_safety_check_fails_closed_when_nemo_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: None)

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is False
    assert decision.reason == "Blocked: safety guardrails unavailable"
    assert decision.reason_code == "GUARDRAILS_UNAVAILABLE"
    assert decision.source == "system"


def test_default_safety_check_merges_custom_and_default_phrases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# healf_block_phrase: rare symptom\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return "allowed"

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)

    default_phrase_decision = check("can you diagnose this issue")
    custom_phrase_decision = check("this is a rare symptom")

    assert default_phrase_decision.allowed is False
    assert "diagnose" in (default_phrase_decision.reason or "")
    assert custom_phrase_decision.allowed is False
    assert "rare symptom" in (custom_phrase_decision.reason or "")


def test_default_safety_check_fails_closed_on_unparseable_nemo_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return "uncertain safety response"

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is False
    assert decision.reason == "Blocked: unparseable safety decision"
    assert decision.reason_code == "NEMO_UNPARSEABLE"
    assert decision.source == "nemo"


def test_default_safety_check_denies_not_allowed_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return "This request is not allowed under safety policy"

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is False
    assert decision.reason_code == "NEMO_DENY_FALLBACK"


def test_default_safety_check_fails_closed_for_invalid_contract_risk_level(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return {
                "allowed": True,
                "reason": "safe",
                "reason_code": "SAFE",
                "risk_level": "critical",
            }

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is False
    assert decision.reason_code == "NEMO_UNPARSEABLE"


def test_default_safety_check_uses_structured_nemo_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return {
                "allowed": False,
                "reason": "Medical diagnosis intent detected",
                "reason_code": "MEDICAL_DIAGNOSIS",
                "risk_level": "high",
            }

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("please review this wellness question")

    assert decision.allowed is False
    assert decision.reason == "Medical diagnosis intent detected"
    assert decision.reason_code == "MEDICAL_DIAGNOSIS"
    assert decision.risk_level == "high"
    assert decision.source == "nemo_contract"


def test_default_safety_check_parses_structured_contract_from_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy_path = tmp_path / "wellness_guard.co"
    policy_path.write_text("# no policy lines here\n", encoding="utf-8")

    class FakeRails:
        def generate(self, messages):
            return (
                "Here is the decision:\n"
                '{"allowed": true, "reason": "Wellness-safe request", '
                '"reason_code": "WELLNESS_SAFE", "risk_level": "low"}'
            )

    monkeypatch.setattr("src.agent.adapters._load_nemo_guardrails", lambda *_: FakeRails())

    check = build_default_safety_check(policy_path)
    decision = check("what supports sleep quality")

    assert decision.allowed is True
    assert decision.reason == "Wellness-safe request"
    assert decision.reason_code == "WELLNESS_SAFE"
    assert decision.risk_level == "low"
    assert decision.source == "nemo_contract"


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
                    "health_goals": ["sleep"],
                    "contraindications": ["pregnancy"],
                },
                {
                    "sku": "prod-02",
                    "canonical_name": "Ashwagandha",
                    "active_ingredients": ["Ashwagandha"],
                    "mechanisms_of_action": ["Supports stress"],
                    "health_goals": ["stress"],
                    "contraindications": [],
                },
            ]
        ),
        encoding="utf-8",
    )
    retrieve = build_default_retriever(products_path=products_path)

    plan = GraphQueryPlan(operation="product_search", key_terms=["sleep", "magnesium"], limit=3)
    chunks = retrieve(plan)

    assert chunks
    assert chunks[0].source_id == "SKU:prod-01"


def test_retriever_applies_domain_and_risk_filters(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "prod-01",
                    "canonical_name": "Magnesium Glycinate",
                    "active_ingredients": ["Magnesium"],
                    "mechanisms_of_action": ["Supports sleep quality"],
                    "health_goals": ["sleep"],
                    "contraindications": ["medication review"],
                },
                {
                    "sku": "prod-02",
                    "canonical_name": "Calm Blend",
                    "active_ingredients": ["L-theanine"],
                    "mechanisms_of_action": ["Supports stress"],
                    "health_goals": ["stress"],
                    "contraindications": [],
                },
            ]
        ),
        encoding="utf-8",
    )
    retrieve = build_default_retriever(products_path=products_path)

    plan = GraphQueryPlan(
        operation="product_search",
        key_terms=["support"],
        filters={"domain": "sleep", "risk_level": "high"},
        limit=3,
    )
    chunks = retrieve(plan)

    assert [chunk.source_id for chunk in chunks] == ["SKU:prod-01"]


def test_retriever_rejects_non_read_only_plan(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text("[]", encoding="utf-8")
    retrieve = build_default_retriever(products_path=products_path)

    with pytest.raises(ValueError, match="read-only"):
        retrieve(
            GraphQueryPlan(
                operation="product_search",
                key_terms=["sleep"],
                read_only=False,
            )
        )


def test_retriever_rejects_unsupported_operation(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text("[]", encoding="utf-8")
    retrieve = build_default_retriever(products_path=products_path)

    with pytest.raises(ValueError, match="Unsupported graph query operation"):
        retrieve(GraphQueryPlan(operation="write", key_terms=["sleep"]))


@pytest.mark.parametrize("limit", [0, 6])
def test_retriever_rejects_out_of_range_limit(tmp_path: Path, limit: int) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text("[]", encoding="utf-8")
    retrieve = build_default_retriever(products_path=products_path)

    with pytest.raises(ValueError, match="limit must be between 1 and 5"):
        retrieve(GraphQueryPlan(operation="product_search", key_terms=["sleep"], limit=limit))


def test_retriever_rejects_empty_terms(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text("[]", encoding="utf-8")
    retrieve = build_default_retriever(products_path=products_path)

    with pytest.raises(ValueError, match="must include key terms"):
        retrieve(GraphQueryPlan(operation="product_search", key_terms=[]))


def test_retriever_is_deterministic_for_same_plan(tmp_path: Path) -> None:
    products_path = tmp_path / "enriched_products.json"
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "prod-01",
                    "canonical_name": "Magnesium Glycinate",
                    "active_ingredients": ["Magnesium"],
                    "mechanisms_of_action": ["Supports sleep quality"],
                    "health_goals": ["sleep"],
                    "contraindications": ["pregnancy"],
                },
                {
                    "sku": "prod-02",
                    "canonical_name": "Magnesium Taurate",
                    "active_ingredients": ["Magnesium"],
                    "mechanisms_of_action": ["Supports sleep"],
                    "health_goals": ["sleep"],
                    "contraindications": ["medication"],
                },
            ]
        ),
        encoding="utf-8",
    )
    retrieve = build_default_retriever(products_path=products_path)
    plan = GraphQueryPlan(operation="product_search", key_terms=["sleep", "magnesium"], limit=2)

    first = retrieve(plan)
    second = retrieve(plan)

    assert [chunk.source_id for chunk in first] == [chunk.source_id for chunk in second]


def test_default_payload_generator_and_evaluator_gate_fail_without_context() -> None:
    payload = build_default_payload_generator()
    evaluate = build_default_evaluator()

    draft = payload("sleep", [])
    gate = evaluate("sleep", draft.response_text, [], 0.8)

    assert draft.uncertainty is True
    assert gate.passed is False
    assert gate.score == 0.0
    assert gate.reason is not None


def test_prompt_rewriter_is_deterministic_and_preserves_terms() -> None:
    rewrite = build_default_prompt_rewriter()

    first = rewrite("What helps with Sleep Quality?")
    second = rewrite("What helps with Sleep Quality?")

    assert first == second
    assert first.normalized_text == "what helps with sleep quality"
    assert "helps" in first.preserved_terms


def test_router_assigns_domain_and_risk() -> None:
    route = build_default_intake_router()

    routed = route(RewrittenQuery(normalized_text="sleep support with medication"))

    assert routed.domain == "sleep"
    assert routed.risk_level == "high"


def test_specialist_emits_read_only_plan() -> None:
    specialist = build_default_specialist()

    plan = specialist(
        RewrittenQuery(normalized_text="sleep magnesium support"),
        RoutingIntent(domain="sleep", risk_level="low"),
    )

    assert plan.operation == "product_search"
    assert plan.read_only is True
    assert plan.limit == 3


def test_critic_requests_retry_on_allergy_query() -> None:
    critic = build_default_critic()

    decision = critic(
        "sleep support with allergy concern",
        RoutingIntent(domain="sleep", risk_level="low"),
        [RetrievalChunk(source_id="SKU:1", content="contraindications: pollen")],
        retry_count=0,
    )

    assert decision.passed is False
    assert decision.retryable is True
    assert decision.findings


@pytest.mark.parametrize(
    ("query", "expected_code"),
    [
        ("sleep support while on medication", "MEDICATION_CAUTION"),
        ("sleep support while pregnant", "PREGNANCY_CAUTION"),
        ("can you diagnose this issue", "DIAGNOSIS_REDIRECT"),
    ],
)
def test_critic_flags_additional_high_risk_intents(query: str, expected_code: str) -> None:
    critic = build_default_critic()

    decision = critic(
        query,
        RoutingIntent(domain="sleep", risk_level="high"),
        [RetrievalChunk(source_id="SKU:1", content="evidence")],
        retry_count=0,
    )

    assert decision.passed is False
    assert any(finding.code == expected_code for finding in decision.findings)


def test_payload_generator_returns_citations_when_evidence_exists() -> None:
    payload = build_default_payload_generator()

    draft = payload(
        "sleep support",
        [
            RetrievalChunk(source_id="SKU:prod-1", content="Evidence one"),
            RetrievalChunk(source_id="SKU:prod-2", content="Evidence two"),
        ],
    )

    assert draft.uncertainty is False
    assert draft.citations == ["SKU:prod-1", "SKU:prod-2"]
    assert "SKU:prod-1" in draft.response_text


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
