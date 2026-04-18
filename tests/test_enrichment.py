import pytest
from pydantic import ValidationError
from hypothesis import given, strategies as st
from src.models.product import EnrichedProduct

import src.enrichment as enrichment_module

# Hypothesis property-based testing strategy for EnrichedProduct
@given(
    sku=st.text(min_size=1),
    canonical_name=st.text(min_size=1),
    active_ingredients=st.lists(st.text(min_size=1), min_size=1),
    target_biomarkers=st.lists(st.text()),
    mechanisms=st.lists(st.text()),
    contraindications=st.lists(st.text())
)
def test_enriched_product_schema(sku, canonical_name, active_ingredients, target_biomarkers, mechanisms, contraindications):
    product = EnrichedProduct(
        sku=sku,
        canonical_name=canonical_name,
        active_ingredients=active_ingredients,
        target_biomarkers=target_biomarkers,
        mechanisms_of_action=mechanisms,
        contraindications=contraindications
    )
    
    assert product.sku == sku
    assert product.canonical_name == canonical_name
    assert isinstance(product.active_ingredients, list)

def test_enriched_product_validation_failure():
    # Test strict typing failure (missing required fields)
    with pytest.raises(ValidationError):
        EnrichedProduct(sku="123") # Missing canonical_name, etc.

def test_run_enrichment_pipeline_fails_fast_without_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(enrichment_module, "load_input_urls", lambda *_: ["https://healf.com/products/test"])

    with pytest.raises(RuntimeError, match="Missing required API keys"):
        enrichment_module.run_enrichment_pipeline()


def test_run_enrichment_pipeline_fails_when_all_urls_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(enrichment_module, "load_input_urls", lambda *_: ["https://healf.com/products/test"])

    class FailingClient:
        def fetch_product_page(self, url: str) -> str:
            raise RuntimeError("scrape failure")

        def extract_product_data(self, markdown_content: str, url: str, instructor_client=None):
            raise RuntimeError("should not reach")

        def fetch_nih_dsld_data(self, product_name: str):
            return {}

    monkeypatch.setattr(enrichment_module, "EnrichmentClient", lambda api_key=None: FailingClient())

    class FakeOpenAI:
        def __init__(self, api_key: str):
            self.api_key = api_key

    monkeypatch.setattr(enrichment_module, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(enrichment_module.instructor, "from_openai", lambda *_: object())

    with pytest.raises(RuntimeError, match=r"Enrichment failed for 1 URL\(s\)"):
        enrichment_module.run_enrichment_pipeline()


def test_run_enrichment_pipeline_fails_on_partial_url_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(
        enrichment_module,
        "load_input_urls",
        lambda *_: ["https://healf.com/products/good", "https://healf.com/products/bad"],
    )

    class MixedClient:
        def fetch_product_page(self, url: str) -> str:
            if url.endswith("bad"):
                raise RuntimeError("scrape failure")
            return "# markdown"

        def extract_product_data(self, markdown_content: str, url: str, instructor_client=None):
            return EnrichedProduct(
                sku="sku-1",
                canonical_name="Good Product",
                active_ingredients=["Magnesium"],
                target_biomarkers=[],
                mechanisms_of_action=[],
                contraindications=[],
            )

        def fetch_nih_dsld_data(self, product_name: str):
            return {"warnings": []}

    monkeypatch.setattr(enrichment_module, "EnrichmentClient", lambda api_key=None: MixedClient())

    class FakeOpenAI:
        def __init__(self, api_key: str):
            self.api_key = api_key

    monkeypatch.setattr(enrichment_module, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(enrichment_module.instructor, "from_openai", lambda *_: object())

    with pytest.raises(RuntimeError, match=r"Enrichment failed for 1 URL\(s\)"):
        enrichment_module.run_enrichment_pipeline()
