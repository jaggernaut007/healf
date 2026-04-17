# Firecrawl API Research Note

## Overview
Firecrawl provides capabilities to convert single websites or entire domains into markdown or structured data. This makes it an ideal fit for health intelligence parsing, particularly for converting disorganized product pages into LLM-ready inputs for `EnrichedProduct` extraction.

## Features Investigated
- **Endpoints:** `scrape` (single URL to markdown) and `crawl` (recursive domain discovery).
- **Structure Response:** Capability to pass an LLM extraction prompt natively, returning structured JSON JSON schemas without needing to chain a secondary LLM internally.
- **Concurrency & Limits:** Rate limits are dependent on the API key tier. Concurrent crawls are supported but need reasonable backoff/retries.

## Key Insights for `healf`
- We primarily need to use the `scrape` endpoint since we are targeting specific product URLs.
- While Firecrawl `extract` exists, it inherently uses an older OpenAI integration in some versions. We should stick to fetching Markdown, then passing the markdown to our strictly typed `Instructor` via local/hosted models for data sovereignty and exact property testing compatilibity.
- **Python Client:** `firecrawl-py`

## Example Usage
```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-xxxx")

# Get markdown from a product page
scrape_result = app.scrape_url('https://example.com/product/omega-3', params={'formats': ['markdown']})
product_markdown = scrape_result.get('markdown')
```