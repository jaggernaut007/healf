from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

import instructor
from openai import OpenAI

from src.models.orchestration import IntentClassification

logger = logging.getLogger(__name__)

_BLOCKED_MEDICAL_PATTERNS = (
    "diagnose",
    "diagnosis",
    "infected",
    "severe chest pain",
    "heart attack",
    "stroke",
    "medical emergency",
    "cure",
    "curing",
    "cancer",
)


def build_default_safety_check(
    model: str = "gpt-5.4-mini",
    neo4j_uri: str = os.getenv("NEO4J_URI", ""),
    neo4j_username: str = os.getenv("NEO4J_USERNAME", ""),
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", ""),
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j"),
) -> Callable[[str, dict[str, Any]], IntentClassification]:
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    client = instructor.from_openai(OpenAI())
    
    # Initialize Neo4j client to fetch dynamic context
    store = Neo4jPropertyGraphStore(
        username=neo4j_username,
        password=neo4j_password,
        url=neo4j_uri,
        database=neo4j_database,
    )

    def _get_known_symptoms(query_text: str):
        # Semantic search for relevant symptoms
        embedding_response = client.embeddings.create(model="text-embedding-3-small", input=query_text)
        query_embedding = embedding_response.data[0].embedding
        
        with store.client.session(database=neo4j_database) as session:
            result = session.run(
                "CALL db.index.vector.queryNodes('symptom_embeddings', 10, $embedding) YIELD node RETURN node.name AS name",
                embedding=query_embedding
            )
            return [record["name"] for record in result]

    def _check(query: str, profile: dict[str, Any] | None = None, chat_history: list[dict[str, str]] | None = None) -> IntentClassification:
        lowered_query = query.lower()
        profile = profile or {}
        chat_history = chat_history or []
        
        # 1. Heuristic medical block (Phase 1)
        for pattern in _BLOCKED_MEDICAL_PATTERNS:
            if pattern in lowered_query:
                return IntentClassification(
                    is_clinical_diagnosis_request=True,
                    primary_domain="general",
                    requires_discovery=False,
                    reasoning=f"The query involves a potential medical concern ('{pattern}') which requires clinical attention rather than supplement advice."
                )
        
        known_symptoms = _get_known_symptoms(query)
        kg_context = f"Relevant health domains and symptoms in our knowledge graph for this query: {', '.join(known_symptoms)}."

        try:
            # 3. Cognitive Classification (Phase 3 - Coordinator Node)
            classification = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the Healf Coordinator Node. Your job is to classify user intent for safety and routing. "
                            "SAFETY RULES: "
                            "1. If the user describes symptoms and asks for a diagnosis ('What is this rash?'), seeks medical treatment, "
                            "or asks for a cure for a disease, set is_clinical_diagnosis_request=True. "
                            "2. If the user asks for general wellness advice or supplement recommendations ('What is good for sleep?'), "
                            "set is_clinical_diagnosis_request=False. "
                            "ROUTING RULES: "
                            "1. Identify the primary health domain. "
                            f"{kg_context} "
                            "2. Determine if the query is a 'Direct Request' vs a 'Consultative Request'. "
                            "   - DIRECT: Specific product, ingredient, or narrow question (e.g., 'Magnesium for sleep', 'Best fish oil', 'How much protein?'). Set requires_discovery=False. "
                            "   - CONSULTATIVE: Broad, goal-oriented, or ambiguous (e.g., 'I want to feel better', 'mindful movement', 'optimize my brain', 'better recovery'). Set requires_discovery=True. "
                            "3. If the query lacks enough context to provide a personalized recommendation, set requires_discovery=True. "
                            "Use the provided user profile to ground your reasoning."
                        )
                    },
                    *chat_history,
                    {
                        "role": "user",
                        "content": f"Query: {query}\nProfile: {json.dumps(profile)}"
                    }
                ],
                response_model=IntentClassification,
                temperature=0.0,
            )
            return classification
            
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return IntentClassification(
                is_clinical_diagnosis_request=False,
                primary_domain="general",
                requires_discovery=True,
                reasoning=f"Fallback due to classification error: {e}"
            )

    return _check
