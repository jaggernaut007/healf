# Research: NIH DSLD (Dietary Supplement Label Database) API

**API Version:** DSLD REST API v9.4.0 (current, tested 2026-04-18)
**Status:** Current (free public access; optional paid API key available)
**Date:** 2026-04-18

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| DSLD Official Portal | https://dsld.od.nih.gov/ | 2026-04-18 |
| DSLD API Guide | https://dsld.od.nih.gov/api-guide | 2026-04-18 |
| DSLD SwaggerHub (v9.4.0) | https://app.swaggerhub.com/apis/ODSDSLD/DSLD/9.4.0 | 2026-04-18 |
| Test: Ingredient Group Search | https://api.ods.od.nih.gov/dsld/v9/ingredient-groups | 2026-04-18 |

## The Correct Approach

DSLD provides a **free, public REST API** — no authentication required for standard 1,000 req/hour. For higher limits (10,000 req/hour), obtain an API key from data.gov.

**Base URL:** `https://api.ods.od.nih.gov/dsld/v9/`

**Key Endpoints:**
- `GET /ingredient-groups` — Query ingredient groups with synonyms and factsheets
- `GET /search-filter` — Complex search for products/ingredients
- `GET /label/{dsldId}` — Fetch individual product label data
- `GET /browse-products` — Browse by keyword or letter

```python
import requests

DSLD_BASE_URL = "https://api.ods.od.nih.gov/dsld/v9"

def query_dsld_ingredient_group(ingredient_name: str) -> dict:
    """
    Query DSLD for supplement forms, synonyms, and related factsheets.
    
    Returns ingredient groups matching the query, including all synonym forms
    and links to PubMed, MedlinePlus, and clinical trial data.
    """
    params = {
        "method": "by_keyword",
        "term": ingredient_name
    }
    response = requests.get(
        f"{DSLD_BASE_URL}/ingredient-groups",
        params=params,
        timeout=15  # NLM endpoints can be slow
    )
    response.raise_for_status()
    return response.json()

def search_dsld_products(query: str) -> dict:
    """Search DSLD for products matching ingredient, brand, or claim."""
    params = {"q": query}
    response = requests.get(
        f"{DSLD_BASE_URL}/search-filter",
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()

# Example: Query magnesium (tested 2026-04-18)
result = query_dsld_ingredient_group("magnesium")
print(f"✓ Found {result['total']['value']} magnesium ingredient groups")

# Sample output: 37 results including multiple forms
for hit in result['hits'][:2]:
    group = hit['_source']
    print(f"\n{group['groupName']} (ID: {group['groupId']})")
    print(f"  Category: {group['category']}")
    print(f"  Synonyms: {len(group['synonyms'])} forms")
    print(f"  First 3: {group['synonyms'][:3]}")
    print(f"  Factsheets: {len(group['factsheets'])} links")
```

**Live Test Output (Magnesium search, 2026-04-18):**
```
✓ Found 37 magnesium ingredient groups

Magnesium (ID: 82)
  Category: ['mineral', None]
  Synonyms: 285 forms (including glycinate, aspartate, citrate, oxide, etc.)
  First 3: ['100% pure (food grade) magnesium chloride', '12.6 mg of mg citrate', '350 mg from magnesium oxide']
  Factsheets: 11 links
    - Magnesium Supplement (ClinicalTrials.gov)
    - Magnesium — Health Professional Fact Sheet (ODS)
    - Magnesium - Adverse effects (PubMed)
    - Magnesium - Contraindications (PubMed)  ← Safety data
    - Magnesium - Kinetics (PubMed)
```

## Files This Affects (Phase 3-4)

- `src/clients/enrichment_client.py` — Add `fetch_dsld_data()` as fallback/primary grounding source
- `src/models/product.py` — Tag products with `grounding_source: "NIH_DSLD"` or `"NIH_RXTERMS"`
- `tests/test_enrichment_client.py` — Add mock-based integration tests for DSLD
- `.env` — Already has `NIH_DATA_API_KEY` (for future higher rate limits if needed)

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Pharma-only endpoints (OpenFDA, RxTerms) | Insufficient supplement form coverage; DSLD is supplement-native |
| Manual label parsing | Not scalable; DSLD automates OCR/extraction |
| No grounding at all | Hallucination risk; medical data requires sourcing |

## Security Assessment

- [x] CVE check: No known CVEs for DSLD endpoint usage
- [x] Maintenance health: NIH/ODS actively maintains; well-funded, institutional backing
- [x] License compatibility: US government data; public domain (CC0 1.0 Universal)
- [x] Dependency tree risk: HTTP-only, minimal dependencies (requests only)
- [x] Download stats / popularity: Official NIH source; widely trusted by researchers
- [x] Single-maintainer risk: NIH/Office of Dietary Supplements team; no single-person risk

## Known Gotchas / Edge Cases

- **Rate Limits (Free)**: 1,000 requests/hour per IP address; blocks for 1 hour if exceeded
- **Rate Limits (Paid)**: 10,000 requests/hour with data.gov API key (not needed for Phase 2-3)
- **Slow Endpoints**: Set timeout=15s minimum; some requests may take 5-10s on first call
- **Form Recognition**: DSLD recognizes specific forms ("Magnesium Glycinate") with 285+ synonyms per ingredient
- **Sparse Niche Supplements**: Some new/trending supplements may not have DSLD entries; graceful fallback to RxTerms recommended
- **API Key in .env**: `NIH_DATA_API_KEY` exists but NOT required for free tier; only use if bumping to 10k req/hr in Phase 4

## Integration Notes (Phase 3-4)

**Decision: Keep RxTerms for Phase 2 (SHIP), migrate to DSLD in Phase 3-4**

**Why DSLD is "better" but not urgent:**
- DSLD: Supplement-native, form-specific, 285+ synonyms per ingredient, built-in safety/contraindication links
- RxTerms: Generic/pharma-first, basic ingredient recognition, free, already tested and passing 28 tests

**Migration Path (Phase 3):**
```python
# Proposed dual-grounding strategy:
async def get_grounding(ingredient: str) -> dict:
    """Try DSLD first (supplement-native), fall back to RxTerms (broad coverage)."""
    try:
        dsld_result = await fetch_dsld_data(ingredient)
        if dsld_result.get("hits"):
            return {"source": "NIH_DSLD", **dsld_result}
    except requests.RequestException:
        pass  # Silently fall back
    
    # Fallback: broad pharmaceutical grounding
    rxterms_result = await fetch_nih_rxterms_data(ingredient)
    return {"source": "NIH_RXTERMS", **rxterms_result}
```

**Test Plan for DSLD Integration:**
- Unit test: Verify DSLD endpoint returns 200 for known ingredient (mock)
- Unit test: Verify fallback to RxTerms if DSLD times out
- Integration test: Call live DSLD with "magnesium"; validate schema match
- Regression test: Ensure Phase 2 RxTerms tests still pass (no breaking changes)

**CI/CD Gate:**
- If DSLD request times out >5%, log warning but don't fail build
- Ensure fallback to RxTerms keeps enrichment pipeline resilient

**Cost:** $0 (free public API; optional $$ for 10k req/hr in future)

## Why We Tested DSLD Now (April 2026)

User had existing `NIH_DATA_API_KEY` in .env suggesting prior exploration. Testing confirms:
1. ✅ API is publicly accessible (no authentication required)
2. ✅ Responses are well-structured (Elasticsearch-based, v9.4.0 stable)
3. ✅ Form recognition is excellent (37 magnesium entries, 285 synonyms per form)
4. ✅ Safety data links work (PubMed contraindications, adverse effects, dosage)
5. ⚠️ Rate limits are generous (1,000 req/hr free) for Healf's Phase 2-3 volume

## References

- DSLD Full Database Downloads: https://api.ods.od.nih.gov/dsld/s3/data/ (Excel, CSV, JSON)
- DSLD FAQ: https://dsld.od.nih.gov/faq
- Contact: ODSComments@mail.nih.gov (for rate limit increases)
