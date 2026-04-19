# ADR-0013: Use Firecrawl for Advanced Enrichment Data Extraction

## Status
Accepted

## Context
Raw product pages on wellness sites (like healf.com) are often cluttered with marketing banners, navigation links, and tracking scripts, which add noise to LLM context windows and increase extraction costs. We need a reliable way to convert these complex HTML structures into clean, reasoning-ready Markdown.

## Decision
We will use the **Firecrawl API** (via the `firecrawl-py` client) for high-quality web-to-markdown conversion. Firecrawl handles JS-heavy pages and dynamically renders content that traditional scrapers (like `BeautifulSoup` or `requests-html`) often miss. 

We will fetch the raw Markdown from Firecrawl and perform structured extraction locally using `Instructor` and Pydantic models. This ensures data sovereignty and allows us to use specific models (e.g., `gpt-5.4-mini`) optimized for our custom schemas.

## Consequences
- **Easier**: Handles complex JavaScript rendering and bypasses basic anti-bot measures, providing clean Markdown inputs for our `EnrichedProduct` extraction pipeline.
- **Harder**: Introduces an external API dependency and associated costs per page scrape. Requires robust error handling for API outages and rate limits.
