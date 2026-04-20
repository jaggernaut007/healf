from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

from openai import OpenAI

from src.models.orchestration import PayloadDraft, RetrievalChunk

logger = logging.getLogger(__name__)


def build_default_payload_generator(model: str = "gpt-5.4") -> Callable[[str, list[RetrievalChunk], dict[str, Any], list[dict[str, str]]], PayloadDraft]:
    client = OpenAI()

    def _generate(
        query: str,
        chunks: list[RetrievalChunk],
        profile: dict[str, Any] | None = None,
        chat_history: list[dict[str, str]] | None = None,
        safety_findings: list[str] | None = None,
    ) -> PayloadDraft:
        profile = profile or {}
        chat_history = chat_history or []
        safety_findings = safety_findings or []
        
        if not chunks and not safety_findings:
            return PayloadDraft(
                response_text=(
                    f"Hi {profile.get('name', 'there')}, I couldn't find enough specific evidence in our catalog to make a grounded recommendation for your request. "
                    "I can discuss general wellness principles related to your goals if you'd like."
                ),
                citations=[],
                uncertainty=True,
            )

        context_lines = [f"- {chunk.source_id}: {chunk.content}" for chunk in chunks]
        context_blob = "\n".join(context_lines)
        user_context_str = json.dumps(profile, indent=2)

        system_prompt = (
            "You are a Healf Health Intelligence Assistant. "
            "Generate a helpful, conversational, and strictly grounded response based on the provided evidence. "
            "1. GROUNDING: Only mention benefits, ingredients, or mechanisms explicitly supported by the evidence. "
            "2. CITATIONS: Use [Source ID] (e.g., [SKU:xxx] or [PMID:xxx]) for every claim. "
            "3. URLS: ALWAYS include the product URL from the evidence if you recommend a product. "
            "4. PERSONALIZATION: Address the user by name if available and link the recommendation to their goals/biomarkers. "
            "5. SAFETY: If safety concerns were flagged, explain them clearly and refuse the recommendation."
        )
        
        if safety_findings:
            system_prompt += (
                "\nSAFETY ALERT: The following concerns were identified:\n"
                + "\n".join([f"- {f}" for f in safety_findings])
                + "\nYou MUST respectfully refuse to recommend the specific product and explain why based on these findings."
            )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *chat_history[-20:],
                    {
                        "role": "user",
                        "content": f"User Profile:\n{user_context_str}\n\nQuery: {query}\n\nEvidence:\n{context_blob}",
                    },
                ],
                temperature=0.0,
            )
            text = response.choices[0].message.content or ""
            # Extract citations from text or use chunks
            citations = list(set(re.findall(r"\[(SKU:\S+|PMID:\d+)\]", text)))
            if not citations:
                citations = [chunk.source_id for chunk in chunks[:3]]
                
            return PayloadDraft(
                response_text=text,
                citations=citations,
                uncertainty=False,
            )
        except Exception as e:
            logger.error(f"Payload generation failed: {e}")
            return PayloadDraft(
                response_text="I encountered an error generating your response. Please try again.",
                citations=[],
                uncertainty=True,
            )

    return _generate


def build_default_generator() -> Callable[[str, list[RetrievalChunk], dict[str, Any]], str]:
    payload_generator = build_default_payload_generator()

    def _generate(query: str, chunks: list[RetrievalChunk], profile: dict[str, Any] | None = None) -> str:
        return payload_generator(query, chunks, profile).response_text

    return _generate
