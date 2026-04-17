import pytest
from unittest.mock import MagicMock, patch
from src.clients.enrichment_client import EnrichmentClient
from src.models.product import EnrichedProduct

def test_enrichment_client_missing_api_key():
    with patch.dict('os.environ', clear=True):
        client = EnrichmentClient(api_key=None)
        # Even if firecrawl is installed, without API key or env var, it will not instantiate app
        with pytest.raises(RuntimeError):
            client.fetch_product_page("http://example.com")

def test_enrichment_client_mock_fetch():
    mock_app = MagicMock()
    mock_document = MagicMock()
    mock_document.markdown = "# Test Product\nIt's great."
    mock_app.scrape.return_value = mock_document
    
    with patch('src.clients.enrichment_client.FirecrawlApp', mock_app):
        # We manually inject the mock app
        client = EnrichmentClient(api_key="fake-key")
        client.app = mock_app

        markdown = client.fetch_product_page("http://example.com/test")
        assert markdown == "# Test Product\nIt's great."

def test_extract_product_data_mock_llm():
    mock_llm_client = MagicMock()
    mock_response = EnrichedProduct(
        sku="TEST-SKU",
        canonical_name="Test Product",
        active_ingredients=["Test Ingredient"],
        target_biomarkers=["Test Marker"],
        mechanisms_of_action=["Does test"],
        contraindications=["Do not test"]
    )
    mock_llm_client.chat.completions.create.return_value = mock_response

    client = EnrichmentClient(api_key="fake-key")
    product = client.extract_product_data("# Test Product Markdown", instructor_client=mock_llm_client)

    assert isinstance(product, EnrichedProduct)
    assert product.canonical_name == "Test Product"
    assert "Do not test" in product.contraindications
