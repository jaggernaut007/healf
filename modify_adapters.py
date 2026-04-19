from pathlib import Path

content = Path('src/agent/adapters.py').read_text()

# 1. Update _try_deepeval_score default model
content = content.replace(
    'def _try_deepeval_score(query: str, draft: str, chunks: list[RetrievalChunk], model: str = "gpt-5.4") -> float | None:',
    'def _try_deepeval_score(query: str, draft: str, chunks: list[RetrievalChunk], model: str = "gpt-5.4-mini") -> float | None:'
)

# 2. Update _render_product_chunk to include URL
old_render_product = """def _render_product_chunk(product: dict) -> str:
    name = product.get("canonical_name", "Unknown product")
    ingredients = ", ".join(product.get("active_ingredients", []))
    mechanisms = "; ".join(product.get("mechanisms_of_action", []))
    contraindications = ", ".join(product.get("contraindications", []))
    return (
        f"{name}. Ingredients: {ingredients}. Mechanisms: {mechanisms}. "
        f"Contraindications: {contraindications}."
    )"""

new_render_product = """def _render_product_chunk(product: dict) -> str:
    name = product.get("canonical_name", "Unknown product")
    ingredients = ", ".join(product.get("active_ingredients", []))
    mechanisms = "; ".join(product.get("mechanisms_of_action", []))
    contraindications = ", ".join(product.get("contraindications", []))
    sku = product.get("sku", "unknown")
    url = f"https://healf.com/products/{sku}"
    return (
        f"{name} (URL: {url}). Ingredients: {ingredients}. Mechanisms: {mechanisms}. "
        f"Contraindications: {contraindications}."
    )"""

content = content.replace(old_render_product, new_render_product)

# 3. Update build_default_retriever
old_retriever = """def build_default_retriever(
    products_path: Path = Path("data/enriched_products.json"),
) -> Callable[[GraphQueryPlan], list[RetrievalChunk]]:
    products = _load_products(products_path)

    def _retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        _validate_read_only_plan(plan)
        logger.info(f"Retrieval plan: {plan.model_dump()}")
        query_terms = set(plan.key_terms)
        filters = {
            "domain": plan.domain,
            "risk_level": plan.risk_level,
            "retry_codes": plan.retry_codes,
        }
        eligible_products = [
            product for product in products if _product_matches_plan_filters(product, filters)
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

    return _retrieve"""

new_retriever = """def build_default_retriever(
    products_path: Path = Path("data/enriched_products.json"),
    research_path: Path = Path("data/research"),
    rules_path: Path = Path("data/research/graph_inference_rules.json"),
) -> Callable[[GraphQueryPlan], list[RetrievalChunk]]:
    products = _load_products(products_path)
    research_docs = _load_research(research_path)
    inference_rules = _load_inference_rules(rules_path)

    def _retrieve(plan: GraphQueryPlan) -> list[RetrievalChunk]:
        _validate_read_only_plan(plan)
        logger.info(f"Retrieval plan: {plan.model_dump()}")
        query_terms = set(plan.key_terms)
        filters = {
            "domain": plan.domain,
            "risk_level": plan.risk_level,
            "retry_codes": plan.retry_codes,
        }
        eligible_products = [
            product for product in products if _product_matches_plan_filters(product, filters)
        ]
        
        eligible_research = []
        for doc in research_docs:
            score = _score_research_for_terms(query_terms, doc)
            if score > 0:
                eligible_research.append((score, doc))
        
        # Apply inference rules
        for score, doc in eligible_research:
            for rule in inference_rules:
                if rule.get("mechanism_name") and rule.get("mechanism_name").lower() in doc.get("summary", "").lower():
                    pass # Placeholder for more complex inference logic

        ranked_products = sorted(
            eligible_products,
            key=lambda product: _score_product_for_terms(query_terms, product),
            reverse=True,
        )
        ranked_research = sorted(eligible_research, key=lambda x: x[0], reverse=True)
        
        chunks: list[RetrievalChunk] = []
        
        for product in ranked_products[: plan.limit]:
            score = _score_product_for_terms(query_terms, product)
            if score <= 0:
                continue
            chunks.append(
                RetrievalChunk(
                    source_id=f"SKU:{product.get('sku', 'unknown')}",
                    content=_render_product_chunk(product),
                )
            )
            
        for score, doc in ranked_research[: plan.limit]:
            chunks.append(
                RetrievalChunk(
                    source_id=f"PMID:{doc.get('pmid', 'unknown')}",
                    content=_render_research_chunk(doc),
                )
            )

        return chunks

    return _retrieve"""

content = content.replace(old_retriever, new_retriever)

# 4. Append new functions at the end
new_functions = """

def _load_research(research_path: Path) -> list[dict]:
    if not research_path.exists() or not research_path.is_dir():
        return []
    docs = []
    for file_path in research_path.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        pmid = file_path.stem
        lines = content.split('\\n')
        title = lines[0].replace('#', '').strip() if lines else "Unknown Title"
        docs.append({"pmid": pmid, "title": title, "summary": content})
    return docs

def _load_inference_rules(rules_path: Path) -> list[dict]:
    if not rules_path.exists():
        return []
    with rules_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def _score_research_for_terms(query_terms: set[str], doc: dict) -> int:
    content = f"{doc.get('title', '')} {doc.get('summary', '')}".lower()
    score = 0
    for term in query_terms:
        if term.lower() in content:
            score += 1
    return score

def _render_research_chunk(doc: dict) -> str:
    summary = doc.get('summary', '')
    if len(summary) > 500:
        summary = summary[:500] + '...'
    return f"Research (PMID: {doc.get('pmid')}): {doc.get('title')}. Summary: {summary}"
"""

content += new_functions

Path('src/agent/adapters.py').write_text(content)
