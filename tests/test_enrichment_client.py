import pytest
from unittest.mock import MagicMock, patch
from src.clients.enrichment_client import EnrichmentClient
from src.models.product import EnrichedProduct

def test_is_valid_url():
    """Test URL validation logic."""
    assert EnrichmentClient.is_valid_url("https://healf.com/products/test") is True
    assert EnrichmentClient.is_valid_url("http://example.com") is True
    assert EnrichmentClient.is_valid_url("ftp://server.com") is True
    assert EnrichmentClient.is_valid_url("invalid-url") is False
    assert EnrichmentClient.is_valid_url("http://") is False
    assert EnrichmentClient.is_valid_url("") is False

def test_fetch_product_page_validates_url():
    client = EnrichmentClient(api_key="fake-key")
    with pytest.raises(ValueError, match="Invalid URL format"):
        client.fetch_product_page("not-a-url")

def test_fetch_product_page_rejects_short_markdown():
    mock_app = MagicMock()
    mock_document = MagicMock()
    mock_document.markdown = "Too short" # Less than 100 chars
    mock_app.scrape.return_value = mock_document
    
    client = EnrichmentClient(api_key="fake-key")
    client.app = mock_app

    with pytest.raises(RuntimeError, match="Scrape result is empty or too short"):
        client.fetch_product_page("https://healf.com/products/test")

def test_extract_sku_from_url():
    """Test that SKUs are correctly extracted from product URLs."""
    assert EnrichmentClient.extract_sku_from_url(
        "https://healf.com/products/bare-biology-ready-and-rested-magnesium-glycinate"
    ) == "bare-biology-ready-and-rested-magnesium-glycinate"
    
    assert EnrichmentClient.extract_sku_from_url(
        "https://healf.com/products/love-life-supplements-organic-ksm-66-r-ashwagandha/"
    ) == "love-life-supplements-organic-ksm-66-r-ashwagandha"

    assert EnrichmentClient.extract_sku_from_url(
        "https://healf.com/products/momentous-l-theanine?variant=123#details"
    ) == "momentous-l-theanine"

    fallback = EnrichmentClient.extract_sku_from_url("https://healf.com/")
    assert fallback.startswith("url-")
    assert len(fallback) == len("url-") + 12

    non_product = EnrichmentClient.extract_sku_from_url("https://healf.com/collections/sleep")
    assert non_product.startswith("url-")

def test_enrichment_client_missing_api_key():
    with patch.dict('os.environ', clear=True):
        client = EnrichmentClient(api_key=None)
        # Even if firecrawl is installed, without API key or env var, it will not instantiate app
        with pytest.raises(RuntimeError):
            client.fetch_product_page("http://example.com")

def test_enrichment_client_mock_fetch():
    mock_app = MagicMock()
    mock_document = MagicMock()
    mock_document.markdown = "# Test Product\nIt's great. " * 10 # Ensure it's over 100 chars
    mock_app.scrape.return_value = mock_document
    
    with patch('src.clients.enrichment_client.FirecrawlApp', mock_app):
        # We manually inject the mock app
        client = EnrichmentClient(api_key="fake-key")
        client.app = mock_app

        markdown = client.fetch_product_page("http://example.com/test")
        assert markdown.startswith("# Test Product")
        assert len(markdown) > 100


def test_enrichment_client_fetch_fallback_scrape_url() -> None:
    mock_app = MagicMock()
    del mock_app.scrape
    mock_app.scrape_url.return_value = {"markdown": "# Legacy scrape_url response " * 10}

    client = EnrichmentClient(api_key="fake-key")
    client.app = mock_app

    markdown = client.fetch_product_page("http://example.com/test")

    assert markdown.startswith("# Legacy scrape_url response")
    assert len(markdown) > 100


def test_enrichment_client_fetch_raises_without_supported_methods() -> None:
    class AppWithoutScrapers:
        pass

    client = EnrichmentClient(api_key="fake-key")
    client.app = AppWithoutScrapers()

    with pytest.raises(RuntimeError, match="does not expose scrape or scrape_url"):
        client.fetch_product_page("http://example.com/test")

def test_extract_product_data_mock_llm():
    mock_llm_client = MagicMock()
    mock_response = EnrichedProduct(
        sku="ignored-sku-will-be-overridden",
        canonical_name="Test Product",
        active_ingredients=["Test Ingredient"],
        target_biomarkers=["Test Marker"],
        mechanisms_of_action=["Does test"],
        contraindications=["Do not test"]
    )
    mock_llm_client.chat.completions.create.return_value = mock_response

    client = EnrichmentClient(api_key="fake-key")
    url = "https://healf.com/products/test-product-sku"
    product = client.extract_product_data(
        "# Test Product Markdown", 
        url=url,
        instructor_client=mock_llm_client
    )

    assert isinstance(product, EnrichedProduct)
    assert product.canonical_name == "Test Product"
    assert product.sku == "test-product-sku"  # URL-derived SKU overrides LLM extraction
    assert "Do not test" in product.contraindications


def test_extract_product_data_rejects_invalid_schema() -> None:
    mock_llm_client = MagicMock()
    # Missing required canonical fields for EnrichedProduct.
    mock_llm_client.chat.completions.create.return_value = {"sku": "bad"}

    client = EnrichmentClient(api_key="fake-key")

    with pytest.raises(RuntimeError, match="LLM data extraction failed"):
        client.extract_product_data(
            "# invalid",
            url="https://healf.com/products/invalid",
            instructor_client=mock_llm_client,
        )


def test_fetch_nih_dsld_data_does_not_fabricate_warnings() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [0, ["rxterm-match"]]
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        data = EnrichmentClient(api_key="fake-key").fetch_nih_dsld_data("magnesium")

    assert data["grounding_status"] == "Success"
    assert data["dsld_matches"] == ["rxterm-match"]
    assert data["warnings"] == []


def test_fetch_nih_dsld_data_handles_malformed_payload() -> None:
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("invalid json")
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        data = EnrichmentClient(api_key="fake-key").fetch_nih_dsld_data("magnesium")

    assert data["grounding_status"] == "Failed"
    assert "invalid json" in data["error"]

def test_fetch_nih_dsld_v9_success() -> None:
    """Test successful DSLD v9 lookup without fallback."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hits": [{"id": "dsld-123", "name": "Magnesium"}]}
    
    with patch("requests.get", return_value=mock_response):
        data = EnrichmentClient(api_key="fake-key").fetch_nih_dsld_data("magnesium")

    assert data["source"] == "NIH_DSLD"
    assert data["grounding_status"] == "Success"
    assert data["dsld_matches"][0]["id"] == "dsld-123"
