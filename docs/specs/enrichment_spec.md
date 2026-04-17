# Enrichment Pipeline Specification

## 1. Overview
The Enrichment Pipeline is responsible for taking raw e-commerce product URLs, extracting their medical/supplemental data, grounding this data against verified government databases (NIH DSLD), and returning a strictly typed JSON output suitable for ingestion into the Knowledge Graph and Chatbot modules.

## 2. Inputs
- Target: `data/raw_product_urls.json`
- Content: An array of Shopify or direct-to-consumer product URLs.

## 3. Core Processing Steps
### 3.1. Scraping (Firecrawl)
- Tool: `firecrawl-py` SDK.
- Action: Scrape raw HTML/JS into clean markdown to bypass bot protections and capture unstructured product context.
- Output: Raw Markdown string.

### 3.2. Medical Grounding (NIH DSLD)
- Tool: `requests` package targeting the NIH Dietary Supplement Label Database API.
- Action: Query the API using active ingredients extracted from the product.
- Output: A list of medically verified contraindications.

### 3.3 Structuring (Instructor + OpenAI)
- Tool: `instructor` patched OpenAI client.
- Action: Pass the Firecrawl Markdown + NIH Data into the LLM with a strict prompt forcing output into the `EnrichedProduct` schema.

## 4. Schemas
The extracted data MUST conform to the following Pydantic model (`src/models/product.py`):
```python
class EnrichedProduct(BaseModel):
    sku: str
    canonical_name: str
    active_ingredients: List[str]
    target_biomarkers: List[str]
    mechanisms_of_action: List[str]
    contraindications: List[str]
```

## 5. Outputs
- Target: `data/enriched_products.json`
- Content: JSON array of serialized `EnrichedProduct` objects.