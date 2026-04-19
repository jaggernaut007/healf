from pathlib import Path
from src.agent.adapters import build_default_retriever, build_default_payload_generator
from src.models.orchestration import GraphQueryPlan, RetrievalChunk

def test_enhanced_recommendations_retrieves_research_and_products():
    retriever = build_default_retriever(
        products_path=Path("data/enriched_products.json"),
        research_path=Path("data/research"),
        rules_path=Path("data/research/graph_inference_rules.json"),
    )
    
    plan = GraphQueryPlan(
        operation="product_search",
        key_terms=["rhodiola", "fatigue"],
        domain="energy",
        risk_level="low",
        limit=5,
        read_only=True
    )
    
    chunks = retriever(plan)
    
    # Verify that research chunks are retrieved and have PMID
    has_research = any("PMID:" in chunk.source_id for chunk in chunks)
    assert has_research, "No research chunk found containing PMID."
    
    # Verify that product chunks have URL
    product_chunks = [c for c in chunks if "SKU:" in c.source_id]
    if product_chunks:
        has_url = any("https://healf.com/products/" in chunk.content for chunk in product_chunks)
        assert has_url, "No product chunk found containing product URL."

def test_enhanced_recommendations_payload_generator_prompt():
    payload_generator = build_default_payload_generator(model="gpt-5.4-mini")
    
    chunks = [
        RetrievalChunk(source_id="PMID:19016404", content="Research (PMID: 19016404): Rhodiola Rosea. Summary: Stress-adaptation and fatigue modulation."),
        RetrievalChunk(source_id="SKU:prod-1", content="Rhodiola Rosea (URL: https://healf.com/products/prod-1). Ingredients: Rhodiola. Mechanisms: adaptogen.")
    ]
    
    draft = payload_generator(
        query="I'm feeling fatigued and stressed, what can I take? Please explain why based on research.",
        chunks=chunks,
        profile={"name": "Test User"}
    )
    
    assert draft.uncertainty is False
    # Ensure it's not failing early and has citations
    assert len(draft.citations) > 0
    # Depending on model output, we might not strictly assert the exact string since it's an LLM,
    # but we can verify it ran successfully and the prompt changes didn't break the adapter interface.
