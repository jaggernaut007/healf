from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Callable

from src.models.orchestration import (
    CriticDecision,
    CriticFinding,
    EvaluationGate,
    GraphQueryPlan,
    PayloadDraft,
    RetrievalChunk,
    RewrittenQuery,
    RoutingIntent,
    SafetyDecision,
)


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
            return SafetyDecision(
                allowed=False,
                reason="Blocked: safety guardrails unavailable",
                reason_code="GUARDRAILS_UNAVAILABLE",
                risk_level="high",
                source="system",
            )
        return _nemo_safety_decision(query=query, rails=rails)

    return _check


def build_default_prompt_rewriter() -> Callable[[str], RewrittenQuery]:
    def _rewrite(query: str) -> RewrittenQuery:
        normalized = re.sub(r"\s+", " ", query.strip())
        lowered = re.sub(r"[^a-z0-9\s]", "", normalized.lower())
        preserved_terms = [term for term in normalized.split() if len(term) > 3][:5]
        return RewrittenQuery(normalized_text=lowered, preserved_terms=preserved_terms)

    return _rewrite


def build_default_intake_router() -> Callable[[RewrittenQuery], RoutingIntent]:
    def _route(rewritten: RewrittenQuery) -> RoutingIntent:
        text = rewritten.normalized_text
        domain = "general"
        if any(token in text for token in ("sleep", "insomnia", "bedtime")):
            domain = "sleep"
        elif any(token in text for token in ("stress", "anxiety", "calm")):
            domain = "stress"
        elif any(token in text for token in ("gut", "digestion", "bloating")):
            domain = "gut"
        elif any(token in text for token in ("energy", "fatigue", "ferritin")):
            domain = "energy"

        risk_level = "high" if any(
            token in text for token in ("medication", "pregnant", "allergy", "diagnose")
        ) else "low"
        return RoutingIntent(domain=domain, risk_level=risk_level, route_reason=f"domain={domain}")

    return _route


def build_default_specialist() -> Callable[[RewrittenQuery, RoutingIntent, list[CriticFinding]], GraphQueryPlan]:
    def _specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding] | None = None,
    ) -> GraphQueryPlan:
        terms = [term for term in rewritten.normalized_text.split() if len(term) > 2][:8]
        retry_codes = [finding.code for finding in (findings or [])]
        return GraphQueryPlan(
            operation="product_search",
            key_terms=terms,
            filters={
                "domain": routing.domain,
                "risk_level": routing.risk_level,
                "retry_codes": ",".join(retry_codes),
            },
            limit=3,
            read_only=True,
        )

    return _specialize


def build_default_retriever(
    products_path: Path = Path("data/enriched_products.json"),
) -> Callable[[GraphQueryPlan], list[RetrievalChunk]]:
    products = _load_products(products_path)

    def _retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        _validate_read_only_plan(plan)
        query_terms = set(plan.key_terms)
        eligible_products = [
            product for product in products if _product_matches_plan_filters(product, plan.filters)
        ]
        ranked = sorted(
            eligible_products,
            key=lambda product: _score_product_for_terms(query_terms, product),
            reverse=True,
        )
        chunks: list[RetrievalChunk] = []
        for product in ranked[: plan.limit]:
            score = _score_product_for_terms(query_terms, product)
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


def build_default_critic() -> Callable[[str, RoutingIntent, list[RetrievalChunk], int], CriticDecision]:
    def _critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
    ) -> CriticDecision:
        normalized = query.lower()
        findings: list[CriticFinding] = []

        if "allergy" in normalized and chunks:
            findings.append(
                CriticFinding(
                    code="ALLERGY_RECHECK",
                    message="Potential allergy sensitivity requires stricter evidence filtering.",
                )
            )

        if routing.risk_level == "high" and "medication" in normalized:
            findings.append(
                CriticFinding(
                    code="MEDICATION_CAUTION",
                    message="Medication context requires conservative recommendation behavior.",
                )
            )
        if routing.risk_level == "high" and "pregnant" in normalized:
            findings.append(
                CriticFinding(
                    code="PREGNANCY_CAUTION",
                    message="Pregnancy context requires conservative recommendation behavior.",
                )
            )
        if routing.risk_level == "high" and "diagnose" in normalized:
            findings.append(
                CriticFinding(
                    code="DIAGNOSIS_REDIRECT",
                    message="Diagnostic intent requires refusal and clinical redirection.",
                )
            )

        if not findings:
            return CriticDecision(passed=True)

        retryable = retry_count == 0
        return CriticDecision(passed=False, findings=findings, retryable=retryable)

    return _critic


def build_default_payload_generator() -> Callable[[str, list[RetrievalChunk]], PayloadDraft]:
    def _generate(query: str, chunks: list[RetrievalChunk]) -> PayloadDraft:
        if not chunks:
            return PayloadDraft(
                response_text=(
                    "I do not have enough retrieved evidence to make a confident recommendation. "
                    "I can share general wellness guidance if you want."
                ),
                citations=[],
                uncertainty=True,
            )

        citations = [chunk.source_id for chunk in chunks[:3]]
        return PayloadDraft(
            response_text=(
                "Based on the retrieved evidence, these options may be relevant to your question: "
                f"{', '.join(citations)}."
            ),
            citations=citations,
            uncertainty=False,
        )

    return _generate


def build_default_generator() -> Callable[[str, list[RetrievalChunk]], str]:
    payload_generator = build_default_payload_generator()

    def _generate(query: str, chunks: list[RetrievalChunk]) -> str:
        return payload_generator(query, chunks).response_text

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
    return _score_product_for_terms(query_terms, product)


def _score_product_for_terms(query_terms: set[str], product: dict) -> int:
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
    contraindications = ", ".join(product.get("contraindications", []))
    return (
        f"{name}. Ingredients: {ingredients}. Mechanisms: {mechanisms}. "
        f"Contraindications: {contraindications}."
    )


def _product_matches_plan_filters(product: dict, filters: dict[str, str]) -> bool:
    domain = filters.get("domain", "general").strip().lower()
    risk_level = filters.get("risk_level", "low").strip().lower()

    product_blob = " ".join(
        [
            str(product.get("canonical_name", "")).lower(),
            " ".join(value.lower() for value in product.get("mechanisms_of_action", []) if value),
            " ".join(value.lower() for value in product.get("health_goals", []) if value),
        ]
    )

    if domain and domain != "general" and domain not in product_blob:
        return False

    contraindications = [value for value in product.get("contraindications", []) if value]
    if risk_level == "high" and not contraindications:
        return False

    return True


def _validate_read_only_plan(plan: GraphQueryPlan) -> None:
    if not plan.read_only:
        raise ValueError("Graph query plan must be read-only.")
    if plan.operation not in {"product_search"}:
        raise ValueError("Unsupported graph query operation.")
    if plan.limit < 1 or plan.limit > 5:
        raise ValueError("Graph query plan limit must be between 1 and 5.")
    if not plan.key_terms:
        raise ValueError("Graph query plan must include key terms.")


def _keyword_safety_decision(query: str) -> SafetyDecision:
    normalized = query.lower()
    for pattern in _BLOCKED_MEDICAL_PATTERNS:
        if pattern in normalized:
            return SafetyDecision(
                allowed=False,
                reason=f"Blocked by safety policy: {pattern}",
                reason_code="POLICY_PHRASE_BLOCK",
                risk_level="high",
                source="policy",
            )
    return SafetyDecision(
        allowed=True,
        reason="Allowed by deterministic safety policy",
        reason_code="POLICY_ALLOW",
        risk_level="low",
        source="policy",
    )


def _load_blocked_phrases_from_guardrails(guardrails_config_path: Path) -> tuple[str, ...]:
    if not guardrails_config_path.exists():
        return _BLOCKED_MEDICAL_PATTERNS

    try:
        raw = guardrails_config_path.read_text(encoding="utf-8")
    except OSError:
        return _BLOCKED_MEDICAL_PATTERNS

    from_file = _extract_blocked_phrases(raw)
    merged = set(_BLOCKED_MEDICAL_PATTERNS)
    merged.update(from_file)
    return tuple(sorted(merged))


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
            return SafetyDecision(
                allowed=False,
                reason=f"Blocked by safety policy: {phrase}",
                reason_code="POLICY_PHRASE_BLOCK",
                risk_level="high",
                source="policy",
            )
    return SafetyDecision(
        allowed=True,
        reason="Allowed by deterministic safety policy",
        reason_code="POLICY_ALLOW",
        risk_level="low",
        source="policy",
    )


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
        response = rails.generate(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY a JSON object with keys: "
                        "allowed (boolean), reason (string), reason_code (string), risk_level (low|medium|high)."
                    ),
                },
                {"role": "user", "content": query},
            ]
        )
        contract_decision = _parse_nemo_safety_contract(response)
        if contract_decision is not None:
            return contract_decision

        if isinstance(response, dict):
            return SafetyDecision(
                allowed=False,
                reason="Blocked: unparseable safety decision",
                reason_code="NEMO_UNPARSEABLE",
                risk_level="high",
                source="nemo",
            )

        text = str(response).lower()
        deny_tokens = (
            "consult",
            "medical professional",
            "cannot",
            "can't",
            "not allowed",
            "disallowed",
            "unable",
            "not able",
            "refuse",
            "decline",
            "emergency",
        )
        allow_tokens = (
            "allowed",
            "safe to proceed",
            "approved",
        )
        if any(pattern in text for pattern in deny_tokens):
            return SafetyDecision(
                allowed=False,
                reason="Blocked by NeMo guardrails",
                reason_code="NEMO_DENY_FALLBACK",
                risk_level="high",
                source="nemo",
            )
        if any(pattern in text for pattern in allow_tokens) and "not allowed" not in text:
            return SafetyDecision(
                allowed=True,
                reason="Allowed by NeMo guardrails fallback",
                reason_code="NEMO_ALLOW_FALLBACK",
                risk_level="low",
                source="nemo",
            )
        return SafetyDecision(
            allowed=False,
            reason="Blocked: unparseable safety decision",
            reason_code="NEMO_UNPARSEABLE",
            risk_level="high",
            source="nemo",
        )
    except Exception:
        return SafetyDecision(
            allowed=False,
            reason="Blocked: safety guardrails execution failure",
            reason_code="GUARDRAILS_EXECUTION_FAILURE",
            risk_level="high",
            source="system",
        )


def _parse_nemo_safety_contract(response: object) -> SafetyDecision | None:
    payload: dict[str, object] | None = None
    if isinstance(response, dict):
        payload = response
    elif isinstance(response, str):
        response_text = response.strip()
        try:
            maybe_dict = json.loads(response_text)
            if isinstance(maybe_dict, dict):
                payload = maybe_dict
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", response_text)
            if match:
                try:
                    maybe_dict = json.loads(match.group(0))
                    if isinstance(maybe_dict, dict):
                        payload = maybe_dict
                except json.JSONDecodeError:
                    payload = None

    if payload is None:
        return None

    allowed_value = payload.get("allowed")
    if isinstance(allowed_value, bool):
        allowed = allowed_value
    else:
        decision_value = str(payload.get("decision", "")).strip().lower()
        if decision_value in {"allow", "allowed", "pass"}:
            allowed = True
        elif decision_value in {"deny", "block", "blocked", "reject"}:
            allowed = False
        else:
            return None

    reason = str(payload.get("reason", "")).strip() or None
    reason_code = str(payload.get("reason_code", "")).strip().upper() or "NEMO_DECISION"
    risk_level = str(payload.get("risk_level", "unknown")).strip().lower()
    if risk_level not in {"low", "medium", "high"}:
        return None

    return SafetyDecision(
        allowed=allowed,
        reason=reason,
        reason_code=reason_code,
        risk_level=risk_level,
        source="nemo_contract",
    )


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
        from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
        from deepeval.test_case import LLMTestCase

        test_case = LLMTestCase(
            input=query,
            actual_output=draft,
            expected_output=draft,
            retrieval_context=[chunk.content for chunk in chunks],
        )
        faithfulness = FaithfulnessMetric(threshold=0.0)
        relevance = AnswerRelevancyMetric(threshold=0.0)
        faithfulness.measure(test_case)
        relevance.measure(test_case)
        faithfulness_score = float(getattr(faithfulness, "score", 0.0))
        relevance_score = float(getattr(relevance, "score", 0.0))
        return max(0.0, min(1.0, (faithfulness_score + relevance_score) / 2))
    except Exception:
        return None
