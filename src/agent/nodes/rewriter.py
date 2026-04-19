from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

from openai import OpenAI

from src.models.orchestration import RewrittenQuery

logger = logging.getLogger(__name__)


def build_default_prompt_rewriter(model: str = "gpt-5.4-mini") -> Callable[[str, dict[str, Any]], RewrittenQuery]:
    client = OpenAI()

    def _rewrite(query: str, profile: dict[str, Any] | None = None) -> RewrittenQuery:
        normalized = re.sub(r"\s+", " ", query.strip())
        profile = profile or {}
        
        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a search query optimizer for a health supplement engine. "
                            "Rewrite the user query for maximum retrieval precision. "
                            "1. Correct misspellings (e.g., 'Ashwaganda' -> 'Ashwagandha'). "
                            "2. Map slang/informal terms to clinical or scientific synonyms (e.g., 'pill for brain focus' -> 'cognitive enhancement', 'tired' -> 'fatigue'). "
                            "3. Preserve the core intent and any specific ingredients or products mentioned. "
                            "4. If profile context is provided, align the rewrite with user goals (e.g., if user wants 'recovery', mention 'muscle recovery' or 'nervous system recovery')."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\nProfile: {json.dumps(profile)}"
                    }
                ],
                response_format=RewrittenQuery,
                temperature=0.0,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.warning(f"LLM rewrite failed, falling back to heuristic: {e}")
            lowered = re.sub(r"[^a-z0-9\s]", "", normalized.lower())
            goals = profile.get("goals", [])
            if goals and "recommend" in lowered:
                 lowered += f" favoring goals like {', '.join(goals)}"
            preserved_terms = [term for term in normalized.split() if len(term) > 3][:5]
            return RewrittenQuery(normalized_text=lowered, preserved_terms=preserved_terms)

    return _rewrite
