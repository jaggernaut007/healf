from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from src.models.orchestration import EvaluationGate, RetrievalChunk, SafetyDecision


_BLOCKED_MEDICAL_PATTERNS = (
    "diagnose",
    "diagnosis",
    "infected",
    "severe chest pain",
    "heart attack",
    "stroke",
    "medical emergency",
)

_OBSERVABILITY_ACTIVE = False


def build_default_safety_check(
    guardrails_config_path: Path = Path("config/wellness_guard.co"),
) -> Callable[[str], SafetyDecision]:
    blocked_phrases = _load_blocked_phrases_from_guardrails(guardrails_config_path)
    rails = None
    rails_attempted = False

    def _check(query: str) -> SafetyDecision:
        nonlocal rails
        nonlocal rails_attempted

        phrase_decision = _phrase_safety_decision(query=query, blocked_phrases=blocked_phrases)
        if not phrase_decision.allowed:
            return phrase_decision
        if not rails_attempted:
            rails = _load_nemo_guardrails(guardrails_config_path)
            rails_attempted = True
        if rails is None:
            return SafetyDecision(allowed=True)
        return _nemo_safety_decision(query=query, rails=rails)

    return _check


def build_default_retriever(
    products_path: Path = Path("data/enriched_products.json"),
) -> Callable[[str], list[RetrievalChunk]]:
    products = _load_products(products_path)

    def _retrieve(query: str) -> list[RetrievalChunk]:
        ranked = sorted(
            products,
            key=lambda product: _score_product_for_query(query, product),
            reverse=True,
        )
        chunks: list[RetrievalChunk] = []
        for product in ranked[:3]:
            score = _score_product_for_query(query, product)
            if score <= 0:
                continue
            chunks.append(
                RetrievalChunk(
                    source_id=f"SKU:{product.get('sku', 'unknown')}",
                    content=_render_product_chunk(product),
                )
            )
        return chunks

    return _retrieve


def build_default_generator() -> Callable[[str, list[RetrievalChunk]], str]:
    def _generate(query: str, chunks: list[RetrievalChunk]) -> str:
        if not chunks:
            return "I don't have documented evidence for that request in the current graph."
        evidence = "; ".join(chunk.source_id for chunk in chunks[:2])
        return (
            "Based on available evidence, these products look relevant to your question. "
            f"Supporting records: {evidence}."
        )

    return _generate


def build_default_evaluator() -> Callable[[str, str, list[RetrievalChunk], float], EvaluationGate]:
    def _evaluate(
        query: str,
        draft: str,
        chunks: list[RetrievalChunk],
        threshold: float,
    ) -> EvaluationGate:
        deepeval_score = _try_deepeval_score(query=query, draft=draft, chunks=chunks)
        score = deepeval_score if deepeval_score is not None else _heuristic_score(draft, chunks)
        passed = score >= threshold
        reason = None
        if not passed:
            reason = f"Quality gate score {score:.2f} is below threshold {threshold:.2f}."
        return EvaluationGate(passed=passed, score=score, threshold=threshold, reason=reason)

    return _evaluate


def build_default_observability_activator() -> Callable[[], None]:
    def _activate() -> None:
        global _OBSERVABILITY_ACTIVE
        if _OBSERVABILITY_ACTIVE:
            return
        import phoenix as px
        from openinference.instrumentation.langchain import LangChainInstrumentor

        px.launch_app()
        LangChainInstrumentor().instrument()
        _OBSERVABILITY_ACTIVE = True

    return _activate


def _load_products(products_path: Path) -> list[dict]:
    if not products_path.exists():
        return []
    with products_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return [item for item in raw if isinstance(item, dict)]


def _score_product_for_query(query: str, product: dict) -> int:
    query_terms = {token for token in query.lower().split() if token}
    if not query_terms:
        return 0
    product_blob = " ".join(
        [
            str(product.get("canonical_name", "")).lower(),
            " ".join(value.lower() for value in product.get("active_ingredients", []) if value),
            " ".join(value.lower() for value in product.get("mechanisms_of_action", []) if value),
        ]
    )
    return sum(1 for term in query_terms if term in product_blob)


def _render_product_chunk(product: dict) -> str:
    name = product.get("canonical_name", "Unknown product")
    ingredients = ", ".join(product.get("active_ingredients", []))
    mechanisms = "; ".join(product.get("mechanisms_of_action", []))
    return f"{name}. Ingredients: {ingredients}. Mechanisms: {mechanisms}."


def _keyword_safety_decision(query: str) -> SafetyDecision:
    normalized = query.lower()
    for pattern in _BLOCKED_MEDICAL_PATTERNS:
        if pattern in normalized:
            return SafetyDecision(allowed=False, reason=f"Blocked by safety policy: {pattern}")
    return SafetyDecision(allowed=True)


def _load_blocked_phrases_from_guardrails(guardrails_config_path: Path) -> tuple[str, ...]:
    if not guardrails_config_path.exists():
        return _BLOCKED_MEDICAL_PATTERNS

    try:
        raw = guardrails_config_path.read_text(encoding="utf-8")
    except OSError:
        return _BLOCKED_MEDICAL_PATTERNS

    from_file = _extract_blocked_phrases(raw)
    if from_file:
        return from_file
    return _BLOCKED_MEDICAL_PATTERNS


def _extract_blocked_phrases(raw_text: str) -> tuple[str, ...]:
    phrases: list[str] = []
    for line in raw_text.splitlines():
        normalized = line.strip()
        if not normalized.startswith("# healf_block_phrase:"):
            continue
        value = normalized.split(":", maxsplit=1)[1].strip().lower()
        if value:
            phrases.append(value)
    return tuple(phrases)


def _phrase_safety_decision(query: str, blocked_phrases: tuple[str, ...]) -> SafetyDecision:
    normalized = query.lower()
    for phrase in blocked_phrases:
        if phrase in normalized:
            return SafetyDecision(allowed=False, reason=f"Blocked by safety policy: {phrase}")
    return SafetyDecision(allowed=True)


def _load_nemo_guardrails(guardrails_config_path: Path):
    if not guardrails_config_path.exists():
        return None
    try:
        from nemoguardrails import LLMRails, RailsConfig

        config = RailsConfig.from_path(str(guardrails_config_path.parent))
        return LLMRails(config=config)
    except Exception:
        return None


def _nemo_safety_decision(query: str, rails) -> SafetyDecision:
    try:
        response = rails.generate(messages=[{"role": "user", "content": query}])
        text = str(response).lower()
        if any(pattern in text for pattern in ("consult", "medical professional", "cannot")):
            return SafetyDecision(allowed=False, reason="Blocked by NeMo guardrails")
    except Exception:
        return _keyword_safety_decision(query)
    return SafetyDecision(allowed=True)


def _heuristic_score(draft: str, chunks: list[RetrievalChunk]) -> float:
    if not chunks:
        return 0.0
    score = min(1.0, 0.4 + (0.2 * min(len(chunks), 3)))
    if "documented evidence" in draft.lower():
        score = min(1.0, score + 0.1)
    return score


def _try_deepeval_score(query: str, draft: str, chunks: list[RetrievalChunk]) -> float | None:
    if not chunks or not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from deepeval.metrics import AnswerRelevanceMetric, FaithfulnessMetric
        from deepeval.test_case import LLMTestCase

        test_case = LLMTestCase(
            input=query,
            actual_output=draft,
            expected_output=draft,
            retrieval_context=[chunk.content for chunk in chunks],
        )
        faithfulness = FaithfulnessMetric(threshold=0.0)
        relevance = AnswerRelevanceMetric(threshold=0.0)
        faithfulness.measure(test_case)
        relevance.measure(test_case)
        faithfulness_score = float(getattr(faithfulness, "score", 0.0))
        relevance_score = float(getattr(relevance, "score", 0.0))
        return max(0.0, min(1.0, (faithfulness_score + relevance_score) / 2))
    except Exception:
        return None
