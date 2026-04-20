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

    def _rewrite(query: str, profile: dict[str, Any] | None = None, chat_history: list[dict[str, str]] | None = None) -> RewrittenQuery:
        normalized = re.sub(r"\s+", " ", query.strip())
        profile = profile or {}
        chat_history = chat_history or []
        
        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a search query optimizer for a health supplement engine. "
                            "Rewrite the user query for maximum retrieval precision. "
                            "CONTEXT AWARENESS: Use the provided chat history to resolve pronouns and short answers (e.g., 'A', 'yes', 'that one'). "
                            "1. Correct misspellings. "
                            "2. Map slang/informal terms to clinical synonyms. "
                            "3. Preserve core intent and specific ingredients. "
                            "4. If profile context is provided, align the rewrite with user goals."
                        )
                    },
                    *chat_history[-20:],
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
