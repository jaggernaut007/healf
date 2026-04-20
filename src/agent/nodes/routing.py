from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

import instructor
from openai import OpenAI

from src.models.orchestration import DiscoveryDecision, RewrittenQuery, RoutingIntent

logger = logging.getLogger(__name__)


def build_default_intake_router(model: str = "gpt-5.4-mini") -> Callable[[RewrittenQuery, dict[str, Any]], RoutingIntent]:
    client = OpenAI()

    def _route(rewritten: RewrittenQuery, profile: dict[str, Any] | None = None, chat_history: list[dict[str, str]] | None = None) -> RoutingIntent:
        profile = profile or {}
        chat_history = chat_history or []
        
        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify the query domain (sleep, stress, gut, energy, or general) and risk_level (low or high). "
                            "High risk includes medication interactions, pregnancy, breastfeeding, allergies, or diagnostic intent. "
                            "AMBIGUITY DETECTION: A query requires clarification if it is broad, conceptual, or lacking constraints. "
                            "Use the provided chat history to determine if the user has already provided enough detail to skip discovery. "
                            "If the user is answering a discovery question, and the combination of history + current answer provides a specific goal and constraint, set requires_clarification=False."
                        )
                    },
                    *chat_history[-20:],
                    {
                        "role": "user",
                        "content": f"Rewritten Query: {rewritten.normalized_text}\nProfile: {json.dumps(profile)}"
                    }
                ],
                response_format=RoutingIntent,
                temperature=0.0,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.warning(f"LLM routing failed, falling back to heuristic: {e}")
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
            return RoutingIntent(domain=domain, risk_level=risk_level, route_reason="fallback_heuristic")

    return _route


def build_default_discovery(
    model: str = "gpt-5.4",
    neo4j_uri: str = os.getenv("NEO4J_URI", ""),
    neo4j_username: str = os.getenv("NEO4J_USERNAME", ""),
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", ""),
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j"),
) -> Callable[[str, list[dict[str, str]], dict[str, Any]], DiscoveryDecision]:
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    
    client = OpenAI()
    
    # Initialize Neo4j client to fetch dynamic context
    store = Neo4jPropertyGraphStore(
        username=neo4j_username,
        password=neo4j_password,
        url=neo4j_uri,
        database=neo4j_database,
    )

    def _get_kg_context(query_text: str, chat_history: list[dict[str, str]] | None = None):
        # Combine chat history and current query for better context in short responses
        context_parts = []
        if chat_history:
            for msg in chat_history[-20:]:  # Last 10 turns for context
                context_parts.append(f"{msg['role']}: {msg['content']}")
        context_parts.append(f"user: {query_text}")
        embedding_input = "\n".join(context_parts)

        # Semantic search for relevant mechanisms and symptoms
        embedding_response = client.embeddings.create(model="text-embedding-3-small", input=embedding_input)
        query_embedding = embedding_response.data[0].embedding
        
        with store.client.session(database=neo4j_database) as session:
            result = session.run(
                "CALL db.index.vector.queryNodes('mechanism_embeddings', 10, $embedding) YIELD node RETURN node.name AS name",
                embedding=query_embedding
            )
            mechanisms = [record["name"] for record in result]
            
            result = session.run(
                "CALL db.index.vector.queryNodes('symptom_embeddings', 10, $embedding) YIELD node RETURN node.name AS name",
                embedding=query_embedding
            )
            symptoms = [record["name"] for record in result]
            
            return mechanisms, symptoms

    def _discover(
        query: str,
        rewritten: RewrittenQuery | None = None,
        routing: RoutingIntent | None = None,
        profile: dict[str, Any] | None = None,
        chat_history: list[dict[str, str]] | None = None,
    ) -> DiscoveryDecision:
        profile = profile or {}
        chat_history = chat_history or []
        
        mechanisms, symptoms = _get_kg_context(query, chat_history)
        kg_context = f"\n\nRelevant Health Goals: {', '.join(symptoms)}.\nRelevant Biological Pathways: {', '.join(mechanisms)}."

        try:
            ic_client = instructor.from_openai(OpenAI())
            
            discovery = ic_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an elite sports dietitian and sales consultant at Healf. The user has an ambiguous intent. "
                            "You must not recommend a product yet. "
                            "1. Briefly validate their goal and educate them on the 2 or 3 biological pathways that support this. "
                            "2. Ask a single, highly targeted multiple-choice question to uncover their specific constraint. Provide these as a structured list of 'options'. "
                            "3. If the user has already provided enough detail in the history + current query to make a recommendation, set requires_clarification=False and provide a 'resolved_query' that captures the full user intent for search (e.g. 'Magnesium glycinate for afternoon energy crash'). "
                            "Keep it professional, consultative, and concise. "
                            f"{kg_context}"
                        )
                    },
                    *chat_history[-20:],
                    {
                        "role": "user",
                        "content": f"User Query: {query}\nUser Profile: {json.dumps(profile, default=str)}"
                    }
                ],
                response_model=DiscoveryDecision,
                max_retries=3,
            )
            return discovery
        except Exception as e:
            logger.error(f"Discovery LLM failed: {e}")
            return DiscoveryDecision(
                requires_clarification=True,
                clarification_question="I'd love to help you with that. Could you tell me a bit more about what you're looking for specifically so I can find the right supplement for you?",
                reasoning=f"Error in discovery: {e}"
            )

    return _discover
