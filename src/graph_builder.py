from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, Sequence

from dotenv import load_dotenv
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from openai import OpenAI
from pydantic import BaseModel, Field

from src.models.graph import (
    GraphBuildResult,
    GraphInferenceRule,
    GraphPreflightResult,
    GraphTriple,
)
from src.models.product import EnrichedProduct

load_dotenv()
class GraphBuilderConfig(BaseModel):
    neo4j_uri: str = Field(default_factory=lambda: os.getenv("NEO4J_URI", ""))
    neo4j_username: str = Field(default_factory=lambda: os.getenv("NEO4J_USERNAME", ""))
    neo4j_password: str = Field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", ""))
    neo4j_database: str = Field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    research_dir: Path = Path("data/research")
    enriched_products_path: Path = Path("data/enriched_products.json")
    inference_rules_path: Path = Path("data/research/graph_inference_rules.json")

    def ensure_ready(self) -> None:
        missing = [
            name
            for name, value in (
                ("NEO4J_URI", self.neo4j_uri),
                ("NEO4J_USERNAME", self.neo4j_username),
                ("NEO4J_PASSWORD", self.neo4j_password),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing Neo4j configuration: {', '.join(missing)}")


class OpenAIEmbeddingItem(BaseModel):
    embedding: list[float]


class OpenAIEmbeddingResponse(BaseModel):
    data: list[OpenAIEmbeddingItem]


class GraphBuilder:
    def __init__(
        self,
        config: GraphBuilderConfig | None = None,
        graph_store: Neo4jPropertyGraphStore | None = None,
        embedder: Callable[[str], list[float]] | None = None,
    ) -> None:
        self.config = config or GraphBuilderConfig()
        self.graph_store = graph_store
        self.embedder = embedder or self._build_default_embedder()

    def load_enriched_products(self, path: Path | None = None) -> list[EnrichedProduct]:
        product_path = path or self.config.enriched_products_path
        if not product_path.exists():
            return []

        with product_path.open("r", encoding="utf-8") as handle:
            raw_items = json.load(handle)

        return [EnrichedProduct.model_validate(item) for item in raw_items]

    def load_research_documents(self, research_dir: Path | None = None) -> list[tuple[str, str]]:
        directory = research_dir or self.config.research_dir
        if not directory.exists():
            return []

        documents: list[tuple[str, str]] = []
        for file_path in sorted(directory.glob("*.md")) + sorted(directory.glob("*.txt")):
            documents.append((file_path.name, file_path.read_text(encoding="utf-8")))
        return documents

    def load_inference_rules(
        self,
        rules_path: Path | None = None,
    ) -> list[GraphInferenceRule]:
        path = rules_path or self.config.inference_rules_path
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as handle:
            raw_rules = json.load(handle)

        return [GraphInferenceRule.model_validate(item) for item in raw_rules]

    def infer_triples(
        self,
        products: Sequence[EnrichedProduct],
        research_documents: Sequence[tuple[str, str]],
        inference_rules: Sequence[GraphInferenceRule] | None = None,
    ) -> list[GraphTriple]:
        pmid_corpus_map = {
            Path(filename).stem: content.lower() for filename, content in research_documents
        }
        full_corpus = "\n".join(pmid_corpus_map.values())
        rules = list(inference_rules) if inference_rules is not None else self.load_inference_rules()
        triples: list[GraphTriple] = []

        for product in products:
            for ingredient in product.active_ingredients:
                ingredient_triples = self._infer_triples_for_ingredient(
                    product=product,
                    ingredient=ingredient,
                    full_corpus=full_corpus,
                    pmid_corpus_map=pmid_corpus_map,
                    rules=rules,
                )
                triples.extend(ingredient_triples)

        return triples

    def build(self) -> GraphBuildResult:
        self.config.ensure_ready()
        products = self.load_enriched_products()
        research_documents = self.load_research_documents()
        inference_rules = self.load_inference_rules()
        
        # Load structured research summaries
        research_summaries_path = Path("data/research_summaries.json")
        research_summaries = {}
        if research_summaries_path.exists():
            with research_summaries_path.open("r", encoding="utf-8") as handle:
                raw_summaries = json.load(handle)
                research_summaries = {s["pmid"]: s for s in raw_summaries}

        if not products:
            raise RuntimeError(f"No enriched products found at {self.config.enriched_products_path}")
        if not research_documents:
            raise RuntimeError(f"No research documents found in {self.config.research_dir}")
        if not inference_rules:
            raise RuntimeError(f"No inference rules found at {self.config.inference_rules_path}")

        triples = self.infer_triples(products, research_documents, inference_rules=inference_rules)
        if not triples:
            raise RuntimeError("No graph triples inferred from current corpus and rules")
            
        self.write_triples(triples, products, research_summaries)
        active_products = [p for p in products if p.active_ingredients]
        return GraphBuildResult(
            products_loaded=len(products),
            active_products_loaded=len(active_products),
            research_documents_loaded=len(research_documents),
            triples_written=len(triples),
        )

    def preflight(self, preview_limit: int = 5) -> GraphPreflightResult:
        products = self.load_enriched_products()
        research_documents = self.load_research_documents()
        inference_rules = self.load_inference_rules()

        if not products:
            raise RuntimeError(f"No enriched products found at {self.config.enriched_products_path}")
        if not research_documents:
            raise RuntimeError(f"No research documents found in {self.config.research_dir}")
        if not inference_rules:
            raise RuntimeError(f"No inference rules found at {self.config.inference_rules_path}")

        triples = self.infer_triples(products, research_documents, inference_rules=inference_rules)
        if not triples:
            raise RuntimeError("No graph triples inferred from current corpus and rules")

        missing_rule_pmids = self._missing_rule_pmids(research_documents, inference_rules)
        unmatched_ingredients = self._unmatched_ingredients(products, triples)

        return GraphPreflightResult(
            products_loaded=len(products),
            research_documents_loaded=len(research_documents),
            rules_loaded=len(inference_rules),
            triples_inferred=len(triples),
            missing_rule_pmids=missing_rule_pmids,
            unmatched_ingredients=unmatched_ingredients,
            triples_preview=triples[:max(preview_limit, 0)],
        )

    def write_triples(
        self, 
        triples: Sequence[GraphTriple], 
        products: Sequence[EnrichedProduct],
        research_summaries: dict[str, dict]
    ) -> None:
        if not triples:
            return

        # Map SKUs to products for quick lookup
        product_map = {p.sku: p for p in products}
        
        # Build a map of PMIDs to full research content
        research_docs = self.load_research_documents()
        pmid_to_content = {Path(name).stem: content for name, content in research_docs}

        self.setup_vector_indices()

        store = self._ensure_graph_store()
        with store.client.session(database=self.config.neo4j_database) as session:
            for triple in triples:
                product_data = product_map.get(triple.product_sku)
                research_data = research_summaries.get(triple.source_pmid, {}) if triple.source_pmid else {}
                full_research_text = pmid_to_content.get(triple.source_pmid, "")
                
                # Generate a richer study context for embedding
                study_text = f"{research_data.get('key_finding', '')} {research_data.get('study_type', '')}"
                study_embedding = self._embed_text(study_text) if triple.source_pmid else None

                session.run(
                    """
                    MERGE (product:Product {sku: $product_sku})
                    SET product.name = $product_name,
                        product.usp = $product_usp,
                        product.usage = $product_usage,
                        product.contraindications = $contraindications,
                        product.embedding = coalesce($product_embedding, product.embedding)
                    MERGE (ingredient:Ingredient {name: $ingredient_name})
                    MERGE (mechanism:Mechanism {name: $mechanism_name})
                    SET mechanism.embedding = coalesce($mechanism_embedding, mechanism.embedding)
                    MERGE (symptom:Symptom {name: $symptom_name})
                    SET symptom.embedding = coalesce($symptom_embedding, symptom.embedding)
                    MERGE (product)-[:CONTAINS]->(ingredient)
                    MERGE (ingredient)-[:TRIGGERS]->(mechanism)
                    MERGE (mechanism)-[:ALLEVIATES]->(symptom)
                    FOREACH (_ IN CASE WHEN $source_pmid IS NULL THEN [] ELSE [1] END |
                        MERGE (study:Study {pmid: $source_pmid})
                        SET study.study_type = $study_type,
                            study.sample_size = $sample_size,
                            study.dosage_tested = $dosage_tested,
                            study.key_finding = $key_finding,
                            study.full_summary = $full_summary,
                            study.embedding = coalesce($study_embedding, study.embedding)
                        MERGE (mechanism)-[:SUPPORTED_BY]->(study)
                        MERGE (ingredient)-[:EVALUATED_IN]->(study)
                    )
                    """,
                    product_sku=triple.product_sku,
                    product_name=triple.product_name,
                    product_usp=getattr(product_data, "usp", ""),
                    product_usage=getattr(product_data, "usage_instructions", ""),
                    contraindications=", ".join(getattr(product_data, "contraindications", [])),
                    ingredient_name=triple.ingredient_name,
                    mechanism_name=triple.mechanism_name,
                    symptom_name=triple.symptom_name,
                    source_pmid=triple.source_pmid,
                    study_type=research_data.get("study_type", ""),
                    sample_size=research_data.get("sample_size", ""),
                    dosage_tested=research_data.get("dosage_tested", ""),
                    key_finding=research_data.get("key_finding", ""),
                    full_summary=full_research_text,
                    product_embedding=self._embed_text(f"{triple.product_name} {triple.ingredient_name}"),
                    mechanism_embedding=self._embed_text(triple.mechanism_name),
                    symptom_embedding=self._embed_text(triple.symptom_name),
                    study_embedding=study_embedding,
                )

    def setup_vector_indices(self) -> None:
        """Create vector indices in Neo4j for semantic KG-RAG search."""
        store = self._ensure_graph_store()
        with store.client.session(database=self.config.neo4j_database) as session:
            # Drop existing if needed or just CREATE IF NOT EXISTS (supported in Neo4j 5+)
            session.run(
                "CREATE VECTOR INDEX product_embeddings IF NOT EXISTS "
                "FOR (n:Product) ON (n.embedding) "
                "OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
            )
            session.run(
                "CREATE VECTOR INDEX mechanism_embeddings IF NOT EXISTS "
                "FOR (n:Mechanism) ON (n.embedding) "
                "OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
            )
            session.run(
                "CREATE VECTOR INDEX study_embeddings IF NOT EXISTS "
                "FOR (n:Study) ON (n.embedding) "
                "OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
            )
            session.run(
                "CREATE VECTOR INDEX symptom_embeddings IF NOT EXISTS "
                "FOR (n:Symptom) ON (n.embedding) "
                "OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
            )

    def _ensure_graph_store(self) -> Neo4jPropertyGraphStore:
        if self.graph_store is not None:
            return self.graph_store

        self.config.ensure_ready()
        self.graph_store = Neo4jPropertyGraphStore(
            username=self.config.neo4j_username,
            password=self.config.neo4j_password,
            url=self.config.neo4j_uri,
            database=self.config.neo4j_database,
            refresh_schema=False,
            create_indexes=False,
        )
        return self.graph_store

    def _embed_text(self, text: str) -> list[float] | None:
        if not self.embedder:
            return None
        return self.embedder(text)

    def _build_default_embedder(self) -> Callable[[str], list[float]] | None:
        if not self.config.openai_api_key:
            return None

        client = OpenAI(api_key=self.config.openai_api_key)

        def _embed(text: str) -> list[float]:
            response = client.embeddings.create(model=self.config.embedding_model, input=text)
            payload = response.model_dump() if hasattr(response, "model_dump") else response
            parsed = OpenAIEmbeddingResponse.model_validate(payload)
            if not parsed.data:
                raise RuntimeError("Embedding API returned no vectors")
            return parsed.data[0].embedding

        return _embed

    def _missing_rule_pmids(
        self,
        research_documents: Sequence[tuple[str, str]],
        rules: Sequence[GraphInferenceRule],
    ) -> list[str]:
        available_pmids = {Path(filename).stem for filename, _ in research_documents}
        missing_pmids = {
            rule.source_pmid
            for rule in rules
            if rule.source_pmid and rule.source_pmid not in available_pmids
        }
        return sorted(missing_pmids)

    def _unmatched_ingredients(
        self,
        products: Sequence[EnrichedProduct],
        triples: Sequence[GraphTriple],
    ) -> list[str]:
        matched = {triple.ingredient_name.lower() for triple in triples}
        all_ingredients = {
            ingredient.strip().lower()
            for product in products
            for ingredient in product.active_ingredients
            if ingredient.strip()
        }
        return sorted(all_ingredients - matched)

    def _infer_triples_for_ingredient(
        self,
        product: EnrichedProduct,
        ingredient: str,
        full_corpus: str,
        pmid_corpus_map: dict[str, str],
        rules: Sequence[GraphInferenceRule],
    ) -> list[GraphTriple]:
        normalized = ingredient.lower()
        matches: list[GraphTriple] = []

        for rule in rules:
            if not any(term.lower() in normalized for term in rule.ingredient_terms):
                continue

            scoped_corpus = full_corpus
            if rule.source_pmid:
                scoped_corpus = pmid_corpus_map.get(rule.source_pmid, "")
                if not scoped_corpus:
                    continue

            if rule.corpus_terms and not any(
                term.lower() in scoped_corpus for term in rule.corpus_terms
            ):
                continue

            matches.append(
                GraphTriple(
                    product_sku=product.sku,
                    product_name=product.canonical_name,
                    ingredient_name=ingredient,
                    mechanism_name=rule.mechanism_name,
                    symptom_name=rule.symptom_name,
                    source_pmid=rule.source_pmid,
                )
            )

        return matches


def run_graph_build(
    enriched_products_path: Path | None = None,
    research_dir: Path | None = None,
    inference_rules_path: Path | None = None,
) -> GraphBuildResult:
    config = GraphBuilderConfig()
    if enriched_products_path is not None:
        config.enriched_products_path = enriched_products_path
    if research_dir is not None:
        config.research_dir = research_dir
    if inference_rules_path is not None:
        config.inference_rules_path = inference_rules_path

    builder = GraphBuilder(config=config)
    return builder.build()


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Phase 2 knowledge graph in Neo4j.")
    parser.add_argument(
        "--enriched-products-path",
        type=Path,
        default=None,
        help="Path to enriched products JSON.",
    )
    parser.add_argument(
        "--research-dir",
        type=Path,
        default=None,
        help="Path to research corpus directory.",
    )
    parser.add_argument(
        "--inference-rules-path",
        type=Path,
        default=None,
        help="Path to graph inference rules JSON.",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Validate inputs and inference without writing to Neo4j.",
    )
    parser.add_argument(
        "--preview-limit",
        type=int,
        default=5,
        help="Number of inferred triples to include in preflight preview.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_cli_parser()
    args = parser.parse_args(argv)
    try:
        if args.preflight:
            config = GraphBuilderConfig()
            if args.enriched_products_path is not None:
                config.enriched_products_path = args.enriched_products_path
            if args.research_dir is not None:
                config.research_dir = args.research_dir
            if args.inference_rules_path is not None:
                config.inference_rules_path = args.inference_rules_path

            preflight_result = GraphBuilder(config=config).preflight(
                preview_limit=args.preview_limit,
            )
            print(json.dumps(preflight_result.model_dump(), indent=2))
        else:
            result = run_graph_build(
                enriched_products_path=args.enriched_products_path,
                research_dir=args.research_dir,
                inference_rules_path=args.inference_rules_path,
            )
            print(json.dumps(result.model_dump(), indent=2))
        return 0
    except Exception as exc:
        print(f"graph_builder failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())