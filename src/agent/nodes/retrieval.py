from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable

from openai import OpenAI

from src.models.orchestration import (
    CriticFinding,
    GraphQueryPlan,
    RetrievalChunk,
    RewrittenQuery,
    RoutingIntent,
)

logger = logging.getLogger(__name__)


def build_default_specialist(model: str = "gpt-5.4-mini") -> Callable[..., GraphQueryPlan]:
    client = OpenAI()

    def _specialize(
        rewritten: RewrittenQuery,
        routing: RoutingIntent,
        findings: list[CriticFinding] | None = None,
        profile: dict[str, Any] | None = None,
    ) -> GraphQueryPlan:
        profile = profile or {}
        
        try:
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate a high-precision GraphQueryPlan to find relevant products. "
                            "Operation MUST be 'product_search'. "
                            "read_only MUST be true. "
                            "1. EXTRACT SEARCH TERMS: Choose 2-4 highly specific terms (ingredients, specific symptoms, or clinical goals). Avoid broad words like 'supplement' or 'pill'. "
                            "2. PERSONALIZATION: Include biomarker names if they are 'low' or 'high' in the profile. "
                            "3. ADAPTATION: If 'findings' are provided, it means previous search results were rejected. "
                            "If the error was 'IRRELEVANT_EVIDENCE', use more specific ingredient names or exclude ambiguous terms. "
                            "If the error was 'SAFETY_WARNING_PRESENT', DO NOT try to avoid it; instead, ensure the terms are precise so the correct product info is found for the generator to handle."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Query: {rewritten.normalized_text}\nRouting: {routing.domain}\nProfile: {json.dumps(profile)}\nFindings: {json.dumps([f.model_dump() for f in (findings or [])])}"
                    }
                ],
                response_format=GraphQueryPlan,
                temperature=0.0,
            )
            plan = response.choices[0].message.parsed
            plan.operation = "product_search"
            plan.read_only = True
            if plan.limit < 1:
                plan.limit = 1
            if plan.limit > 5:
                plan.limit = 5
            return plan
        except Exception as e:
            logger.warning(f"LLM specialization failed, falling back to heuristic: {e}")
            terms = [term for term in rewritten.normalized_text.split() if len(term) > 2][:8]
            biomarkers = profile.get("health_data", {}).get("biomarkers", {})
            for biomarker, level in biomarkers.items():
                if level in ("low", "high"):
                    terms.append(biomarker)
            
            retry_codes = [finding.code for finding in (findings or [])]
            return GraphQueryPlan(
                operation="product_search",
                key_terms=list(set(terms)),
                domain=routing.domain,
                risk_level=routing.risk_level,
                retry_codes=",".join(retry_codes),
                limit=3,
                read_only=True,
            )

    return _specialize


def build_default_retriever(
    neo4j_uri: str = os.getenv("NEO4J_URI", ""),
    neo4j_username: str = os.getenv("NEO4J_USERNAME", ""),
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", ""),
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j"),
) -> Callable[[GraphQueryPlan], list[RetrievalChunk]]:
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    
    # Initialize Neo4j client
    store = Neo4jPropertyGraphStore(
        username=neo4j_username,
        password=neo4j_password,
        url=neo4j_uri,
        database=neo4j_database,
    )
    
    openai_client = OpenAI()

    def _retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        _validate_read_only_plan(plan)
        query_text = " ".join(plan.key_terms)
        
        # 1. Generate Query Embedding
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_embedding = embedding_response.data[0].embedding

        chunks: list[RetrievalChunk] = []
        
        with store.client.session(database=neo4j_database) as session:
            # 2. Robust Hybrid Search for Products
            product_results = session.run(
                """
                // 1. Fetch by Keyword (High priority)
                MATCH (p:Product)-[:CONTAINS]->(i:Ingredient)
                WHERE any(term IN $terms WHERE toLower(p.name) CONTAINS toLower(term) OR toLower(i.name) CONTAINS toLower(term))
                WITH collect(DISTINCT p) AS keyword_products
                
                // 2. Fetch by Vector
                CALL db.index.vector.queryNodes('product_embeddings', 50, $embedding)
                YIELD node, score
                
                // 3. Combine and deduplicate
                WITH keyword_products, collect({node: node, score: score}) AS vector_results
                WITH keyword_products + [v IN vector_results | v.node] AS all_nodes, vector_results
                UNWIND all_nodes AS node
                WITH DISTINCT node, vector_results
                
                // 4. Score and enrich
                MATCH (node)-[:CONTAINS]->(i:Ingredient)
                OPTIONAL MATCH (i)-[:TRIGGERS]->(m:Mechanism)-[:ALLEVIATES]->(s:Symptom)
                
                WITH node, collect(DISTINCT i.name) AS ingredients, 
                     collect(DISTINCT m.name) AS mechanisms,
                     [v IN vector_results WHERE v.node = node | v.score][0] AS vector_score
                WITH node, ingredients, mechanisms, vector_score,
                     [term IN $terms WHERE toLower(node.name) CONTAINS toLower(term) OR any(ing IN ingredients WHERE toLower(ing) CONTAINS toLower(term)) | 1] AS term_matches
                
                WITH node, ingredients, mechanisms,
                     coalesce(vector_score, 0.5) AS base_score,
                     size(term_matches) AS keyword_boost
                
                RETURN node.sku AS sku, node.name AS name, node.usp AS usp, node.usage AS usage,
                       node.contraindications AS contraindications,
                       ingredients, mechanisms,
                       (base_score + (0.5 * keyword_boost)) AS final_score
                ORDER BY final_score DESC
                LIMIT $limit
                """,
                embedding=query_embedding,
                terms=plan.key_terms,
                limit=plan.limit
            )
            
            for record in product_results:
                chunk_content = (
                    f"Product: {record['name']} (SKU: {record['sku']}). "
                    f"Ingredients: {', '.join(record['ingredients'])}. "
                    f"Mechanisms: {', '.join(record['mechanisms'])}. "
                    f"USPs: {record['usp']}. Usage: {record['usage']}. "
                    f"Contraindications: {record['contraindications']}. "
                    f"URL: https://healf.com/products/{record['sku']}"
                )
                chunks.append(RetrievalChunk(
                    source_id=f"SKU:{record['sku']}",
                    content=chunk_content
                ))

            # 3. Robust Hybrid Search for Research
            research_results = session.run(
                """
                // 1. Fetch by Keyword
                MATCH (s:Study)
                WHERE any(term IN $terms WHERE toLower(s.key_finding) CONTAINS toLower(term) OR toLower(s.full_summary) CONTAINS toLower(term))
                WITH collect(DISTINCT s) AS keyword_studies
                
                // 2. Fetch by Vector
                CALL db.index.vector.queryNodes('study_embeddings', 50, $embedding)
                YIELD node, score
                
                // 3. Combine
                WITH keyword_studies, collect({node: node, score: score}) AS vector_results
                WITH keyword_studies + [v IN vector_results | v.node] AS all_nodes, vector_results
                UNWIND all_nodes AS node
                WITH DISTINCT node, vector_results
                
                // 4. Score and enrich
                OPTIONAL MATCH (m:Mechanism)-[:SUPPORTED_BY]->(node)
                WITH node, m, 
                     [v IN vector_results WHERE v.node = node | v.score][0] AS vector_score,
                     [term IN $terms WHERE toLower(node.key_finding) CONTAINS toLower(term) OR (m IS NOT NULL AND toLower(m.name) CONTAINS toLower(term)) | 1] AS term_matches
                
                RETURN node.pmid AS pmid, node.study_type AS study_type, 
                       node.key_finding AS key_finding, node.sample_size AS sample_size,
                       node.full_summary AS full_summary,
                       coalesce(m.name, "General health") AS mechanism, 
                       (coalesce(vector_score, 0.5) + (0.5 * size(term_matches))) AS final_score
                ORDER BY final_score DESC
                LIMIT $limit
                """,
                embedding=query_embedding,
                terms=plan.key_terms,
                limit=plan.limit
            )

            for record in research_results:
                chunk_content = (
                    f"Research (PMID:{record['pmid']}): {record['key_finding']}. "
                    f"Mechanism: {record['mechanism']}. Study Type: {record['study_type']}. "
                    f"Sample Size: {record['sample_size']}. "
                    f"Full Summary: {record['full_summary']}"
                )
                chunks.append(RetrievalChunk(
                    source_id=f"PMID:{record['pmid']}",
                    content=chunk_content
                ))

        return chunks

    return _retrieve


def _validate_read_only_plan(plan: GraphQueryPlan) -> None:
    if not plan.read_only:
        raise ValueError("Graph query plan must be read-only.")
    if plan.operation not in {"product_search"}:
        raise ValueError("Unsupported graph query operation.")
    if plan.limit < 1 or plan.limit > 5:
        raise ValueError("Graph query plan limit must be between 1 and 5.")
    if not plan.key_terms:
        raise ValueError("Graph query plan must include key terms.")
