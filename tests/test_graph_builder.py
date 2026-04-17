from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.graph_builder as graph_builder_module
from src.graph_builder import GraphBuildResult, GraphBuilder, GraphBuilderConfig, GraphTriple
from src.models.product import EnrichedProduct


class FakeSession:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.queries: list[tuple[str, dict]] = []

    def __enter__(self) -> "FakeSession":
        if self.fail:
            raise RuntimeError("Neo4j connection failed")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def run(self, query: str, **params) -> None:
        self.queries.append((query, params))


class FakeClient:
    def __init__(self, session: FakeSession) -> None:
        self._session = session

    def session(self, database: str | None = None) -> FakeSession:
        return self._session


class FakeGraphStore:
    def __init__(self, session: FakeSession) -> None:
        self.client = FakeClient(session)


def make_builder(session: FakeSession | None = None) -> GraphBuilder:
    config = GraphBuilderConfig(
        neo4j_uri="bolt://example:7687",
        neo4j_username="neo4j",
        neo4j_password="password",
        neo4j_database="neo4j",
    )
    return GraphBuilder(config=config, graph_store=FakeGraphStore(session or FakeSession()), embedder=lambda text: [1.0, 2.0])


def test_infer_triples_maps_known_corpus() -> None:
    builder = make_builder()
    products = [
        EnrichedProduct(
            sku="SKU-1",
            canonical_name="Magnesium Glycinate",
            active_ingredients=["Magnesium Glycinate"],
            target_biomarkers=["Sleep"],
            mechanisms_of_action=["GABA support"],
            contraindications=[],
        ),
        EnrichedProduct(
            sku="SKU-2",
            canonical_name="Ashwagandha KSM-66",
            active_ingredients=["Ashwagandha"],
            target_biomarkers=["Stress"],
            mechanisms_of_action=["Cortisol reduction"],
            contraindications=[],
        ),
    ]
    research_documents = [
        ("23853635.md", "Magnesium supplementation improves insomnia and sleep efficiency."),
        ("23439798.md", "Ashwagandha reduced serum cortisol and stress in adults."),
    ]

    triples = builder.infer_triples(products, research_documents)

    assert [triple.source_pmid for triple in triples] == ["23853635", "23439798"]
    assert triples[0].symptom_name == "Sleep"
    assert triples[1].mechanism_name == "Cortisol reduction"


def test_write_triples_uses_parameterized_merge() -> None:
    session = FakeSession()
    builder = make_builder(session)
    triple = GraphTriple(
        product_sku="SKU-1",
        product_name="Magnesium Glycinate",
        ingredient_name="Magnesium Glycinate",
        mechanism_name="GABA signaling support",
        symptom_name="Sleep",
        source_pmid="23853635",
    )

    builder.write_triples([triple])
    builder.write_triples([triple])

    assert len(session.queries) == 2
    assert all("MERGE" in query for query, _ in session.queries)
    assert all("CREATE" not in query for query, _ in session.queries)
    assert session.queries[0][1]["product_sku"] == "SKU-1"
    assert session.queries[0][1]["mechanism_embedding"] == [1.0, 2.0]
    assert session.queries[0][1]["source_pmid"] == "23853635"
    assert "SUPPORTED_BY" in session.queries[0][0]


def test_build_raises_when_products_missing(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    products_path = tmp_path / "enriched_products.json"
    research_dir.mkdir()
    (research_dir / "23853635.md").write_text("magnesium", encoding="utf-8")
    products_path.write_text("[]", encoding="utf-8")

    config = GraphBuilderConfig(
        neo4j_uri="bolt://example:7687",
        neo4j_username="neo4j",
        neo4j_password="password",
        neo4j_database="neo4j",
        research_dir=research_dir,
        enriched_products_path=products_path,
    )
    session = FakeSession()
    builder = GraphBuilder(config=config, graph_store=FakeGraphStore(session))

    with pytest.raises(RuntimeError, match="No enriched products found"):
        builder.build()


def test_build_raises_when_research_missing(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    products_path = tmp_path / "enriched_products.json"
    research_dir.mkdir()
    products_path.write_text(
        """[
  {
    \"sku\": \"SKU-1\",
    \"canonical_name\": \"Magnesium Glycinate\",
    \"active_ingredients\": [\"Magnesium Glycinate\"],
    \"target_biomarkers\": [\"Sleep\"],
    \"mechanisms_of_action\": [\"GABA support\"],
    \"contraindications\": []
  }
]""",
        encoding="utf-8",
    )

    config = GraphBuilderConfig(
        neo4j_uri="bolt://example:7687",
        neo4j_username="neo4j",
        neo4j_password="password",
        neo4j_database="neo4j",
        research_dir=research_dir,
        enriched_products_path=products_path,
    )
    builder = GraphBuilder(config=config, graph_store=FakeGraphStore(FakeSession()))

    with pytest.raises(RuntimeError, match="No research documents found"):
        builder.build()


def test_write_triples_raises_on_connection_failure() -> None:
    builder = make_builder(FakeSession(fail=True))
    triple = GraphTriple(
        product_sku="SKU-1",
        product_name="Magnesium Glycinate",
        ingredient_name="Magnesium Glycinate",
        mechanism_name="GABA signaling support",
        symptom_name="Sleep",
    )

    with pytest.raises(RuntimeError, match="Neo4j connection failed"):
        builder.write_triples([triple])


def test_build_raises_when_inference_rules_missing(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    products_path = tmp_path / "enriched_products.json"
    rules_path = research_dir / "graph_inference_rules.json"
    research_dir.mkdir()
    (research_dir / "23853635.md").write_text("magnesium sleep", encoding="utf-8")
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "SKU-1",
                    "canonical_name": "Magnesium Glycinate",
                    "active_ingredients": ["Magnesium Glycinate"],
                    "target_biomarkers": ["Sleep"],
                    "mechanisms_of_action": ["GABA support"],
                    "contraindications": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    config = GraphBuilderConfig(
        neo4j_uri="bolt://example:7687",
        neo4j_username="neo4j",
        neo4j_password="password",
        neo4j_database="neo4j",
        research_dir=research_dir,
        enriched_products_path=products_path,
        inference_rules_path=rules_path,
    )
    builder = GraphBuilder(config=config, graph_store=FakeGraphStore(FakeSession()))

    with pytest.raises(RuntimeError, match="No inference rules found"):
        builder.build()


def test_build_raises_when_no_triples_inferred(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    products_path = tmp_path / "enriched_products.json"
    rules_path = research_dir / "graph_inference_rules.json"
    research_dir.mkdir()
    (research_dir / "23853635.md").write_text("magnesium sleep", encoding="utf-8")
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "SKU-1",
                    "canonical_name": "Magnesium Glycinate",
                    "active_ingredients": ["Magnesium Glycinate"],
                    "target_biomarkers": ["Sleep"],
                    "mechanisms_of_action": ["GABA support"],
                    "contraindications": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    rules_path.write_text(
        json.dumps(
            [
                {
                    "ingredient_terms": ["ashwagandha"],
                    "mechanism_name": "Cortisol reduction",
                    "symptom_name": "Stress",
                    "source_pmid": "23439798",
                    "corpus_terms": ["ashwagandha", "cortisol", "stress"],
                }
            ]
        ),
        encoding="utf-8",
    )

    config = GraphBuilderConfig(
        neo4j_uri="bolt://example:7687",
        neo4j_username="neo4j",
        neo4j_password="password",
        neo4j_database="neo4j",
        research_dir=research_dir,
        enriched_products_path=products_path,
        inference_rules_path=rules_path,
    )
    builder = GraphBuilder(config=config, graph_store=FakeGraphStore(FakeSession()))

    with pytest.raises(RuntimeError, match="No graph triples inferred"):
        builder.build()


def test_run_graph_build_accepts_inference_rule_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Path | None] = {}

    def fake_build(self: GraphBuilder) -> GraphBuildResult:
        captured["enriched_products_path"] = self.config.enriched_products_path
        captured["research_dir"] = self.config.research_dir
        captured["inference_rules_path"] = self.config.inference_rules_path
        return GraphBuildResult(products_loaded=1, research_documents_loaded=1, triples_written=1)

    monkeypatch.setattr(GraphBuilder, "build", fake_build)
    enriched_path = Path("/tmp/enriched_products.json")
    research_dir = Path("/tmp/research")
    rules_path = Path("/tmp/rules.json")

    result = graph_builder_module.run_graph_build(
        enriched_products_path=enriched_path,
        research_dir=research_dir,
        inference_rules_path=rules_path,
    )

    assert result.triples_written == 1
    assert captured["enriched_products_path"] == enriched_path
    assert captured["research_dir"] == research_dir
    assert captured["inference_rules_path"] == rules_path


def test_main_returns_zero_on_success(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fake_run_graph_build(**kwargs) -> GraphBuildResult:
        return GraphBuildResult(products_loaded=2, research_documents_loaded=3, triples_written=4)

    monkeypatch.setattr(graph_builder_module, "run_graph_build", fake_run_graph_build)

    exit_code = graph_builder_module.main([])
    output = capsys.readouterr()

    assert exit_code == 0
    assert '"triples_written": 4' in output.out


def test_main_returns_one_on_failure(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fake_run_graph_build(**kwargs) -> GraphBuildResult:
        raise RuntimeError("boom")

    monkeypatch.setattr(graph_builder_module, "run_graph_build", fake_run_graph_build)

    exit_code = graph_builder_module.main([])
    output = capsys.readouterr()

    assert exit_code == 1
    assert "graph_builder failed: boom" in output.err


def test_preflight_reports_diagnostics(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    products_path = tmp_path / "enriched_products.json"
    rules_path = research_dir / "graph_inference_rules.json"
    research_dir.mkdir()

    (research_dir / "23853635.md").write_text(
        "magnesium supplementation improves sleep",
        encoding="utf-8",
    )
    products_path.write_text(
        json.dumps(
            [
                {
                    "sku": "SKU-1",
                    "canonical_name": "Focus Stack",
                    "active_ingredients": ["Magnesium Glycinate", "Unknown Ingredient"],
                    "target_biomarkers": ["Sleep"],
                    "mechanisms_of_action": ["GABA support"],
                    "contraindications": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    rules_path.write_text(
        json.dumps(
            [
                {
                    "ingredient_terms": ["magnesium"],
                    "mechanism_name": "GABA signaling support",
                    "symptom_name": "Sleep",
                    "source_pmid": "23853635",
                    "corpus_terms": ["magnesium", "sleep"],
                },
                {
                    "ingredient_terms": ["ashwagandha"],
                    "mechanism_name": "Cortisol reduction",
                    "symptom_name": "Stress",
                    "source_pmid": "23439798",
                    "corpus_terms": ["ashwagandha", "stress"],
                },
            ]
        ),
        encoding="utf-8",
    )

    config = GraphBuilderConfig(
        research_dir=research_dir,
        enriched_products_path=products_path,
        inference_rules_path=rules_path,
    )

    result = GraphBuilder(config=config, graph_store=FakeGraphStore(FakeSession())).preflight(preview_limit=2)

    assert result.triples_inferred == 1
    assert result.missing_rule_pmids == ["23439798"]
    assert result.unmatched_ingredients == ["unknown ingredient"]
    assert len(result.triples_preview) == 1


def test_main_preflight_returns_zero(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fake_preflight(self: GraphBuilder, preview_limit: int = 5):
        return graph_builder_module.GraphPreflightResult(
            products_loaded=1,
            research_documents_loaded=1,
            rules_loaded=1,
            triples_inferred=1,
            missing_rule_pmids=[],
            unmatched_ingredients=[],
            triples_preview=[],
        )

    monkeypatch.setattr(GraphBuilder, "preflight", fake_preflight)

    exit_code = graph_builder_module.main(["--preflight"])
    output = capsys.readouterr()

    assert exit_code == 0
    assert '"triples_inferred": 1' in output.out