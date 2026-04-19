from __future__ import annotations

import json
import logging
from typing import Any, Callable

from openai import OpenAI

from src.models.orchestration import CriticDecision, CriticFinding, RetrievalChunk, RoutingIntent

logger = logging.getLogger(__name__)


def build_default_critic(model: str = "gpt-5.4") -> Callable[[str, RoutingIntent, list[RetrievalChunk], int, dict[str, Any]], CriticDecision]:
    client = OpenAI()

    def _critic(
        query: str,
        routing: RoutingIntent,
        chunks: list[RetrievalChunk],
        retry_count: int,
        profile: dict[str, Any] | None = None,
    ) -> CriticDecision:
        if not chunks:
            return CriticDecision(passed=True, findings=[], retryable=False)

        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a nuanced pharmacovigilance critic for Healf. "
                            "Critique the retrieved evidence against the user query and profile. "
                            "Flag findings ONLY if: "
                            "1. DIRECT CONFLICT: Product contraindications specifically conflict with user's conditions/history. "
                            "2. IRRELEVANT: The evidence does not address the core subject or ingredients of the query at all. "
                            "3. SAFETY RISK: The query involves high-risk factors (medication interactions, pregnancy, breastfeeding, severe allergies, or diagnostic intent) AND there are relevant warnings in the evidence. "
                            "NUANCE RULES: "
                            "- General wellness queries (sleep, stress, energy, gut health) are NOT high-risk unless medical conditions/medications are involved. "
                            "- Do NOT flag a safety risk just because a product has a generic 'consult a doctor' warning unless point 3 is met. "
                            "- STACK QUERIES: If the query asks for a 'stack' or 'combination', and you have evidence for the individual components that address the goals, set passed=True. You do NOT need evidence for the specific combination/synergy unless safety interactions are suspected. "
                            "- If the evidence is relevant but unsafe for this specific user, set passed=False and retryable=False."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\nRouting: {routing.domain}, {routing.risk_level}\nProfile: {json.dumps(profile)}\nEvidence: {json.dumps([c.content for c in chunks])}"
                    }
                ],
                response_format=CriticDecision,
                temperature=0.0,
            )
            decision = response.choices[0].message.parsed
            if not hasattr(decision, "retryable"):
                decision.retryable = False
            return decision
        except Exception as e:
            logger.warning(f"LLM critic failed, falling back to heuristic: {e}")
            # Basic safety heuristic: if the query or evidence contains high-risk keywords, block it.
            text = (query + " " + " ".join([c.content for c in chunks])).lower()
            if any(token in text for token in ("allergy", "medication", "pregnant", "breastfeeding", "diagnose")):
                return CriticDecision(
                    passed=False, 
                    findings=[CriticFinding(code="HEURISTIC_BLOCK", message="Potential safety risk detected in query or evidence during fallback.", severity="high")],
                    retryable=False
                )
            return CriticDecision(passed=True, findings=[], retryable=False)

    return _critic
