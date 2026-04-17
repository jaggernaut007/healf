# Research: Instructor Structured LLM Outputs

**Library version:** instructor 1.15.1
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Instructor docs | https://jxnl.github.io/instructor/ | 2026-04-17 |
| GitHub Repository | https://github.com/jxnl/instructor | 2026-04-17 |
| PyPI Package | https://pypi.org/project/instructor/ | 2026-04-17 |

## The Correct Approach

Use Instructor to patch LLM clients (OpenAI, etc.) and enforce Pydantic schema compliance on model outputs without additional parsing overhead.

```python
import instructor
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class EnrichedProduct(BaseModel):
    sku: str
    canonical_name: str
    active_ingredients: list
    mechanisms_of_action: list
    contraindications: list

# Patch the OpenAI client with instructor
client = instructor.from_openai(ChatOpenAI(model="gpt-4", temperature=0))

# Call with response_model parameter; instructor handles schema enforcement
enriched = client.create(
    response_model=EnrichedProduct,
    messages=[
        {
            "role": "user",
            "content": f"Extract product info: {product_markdown}"
        }
    ]
)
# enriched is guaranteed to be an instance of EnrichedProduct
print(enriched.canonical_name)
```

## Files This Affects

- `src/enrichment.py` — Product extraction with schema enforcement
- `src/chatbot.py` — UI payload generation with type safety
- Tests: `tests/test_enrichment.py`, `tests/test_chatbot.py` — Schema compliance tests

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Manual JSON parsing | Error-prone; easy to miss validation, coercion issues |
| OpenAI's native JSON mode | Doesn't guarantee structural compliance; still requires parsing |
| LangChain output parsers | Heavier weight; Instructor is more direct and composable |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by Jason Liu
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Depends on Pydantic + OpenAI SDK (both stable)
- [x] Download stats / popularity: 1M+ weekly downloads, growing adoption
- [ ] Single-maintainer risk: Jason Liu is primary maintainer; community-supported

## Known Gotchas / Edge Cases

- **Model Availability**: Instructor works best with models supporting structured outputs (gpt-4, gpt-4-turbo); test with gpt-3.5-turbo.
- **Response Model Required**: Always pass `response_model=YourPydanticModel`; without it, response is not validated.
- **Retry on Failure**: Instructor can retry failed validations; tune `max_retries` parameter if needed.
- **Streaming**: Streaming responses with Instructor require special handling; test complex schemas before relying on streaming.
- **Cost**: Each retry incurs additional API calls; monitor usage for high-cardinality data.

## Integration Notes

- Instructor is a thin wrapper that doesn't change the underlying model behavior; it adds a validation layer.
- Combine with Pydantic for strict schema definitions; use `Field` for documentation and constraints.
- Use Instructor in all LLM extraction points (enrichment, payload generation).
- For multi-part extraction, consider breaking into sequential calls with separate Pydantic models.
- Monitor model outputs if schema changes; old model checkpoints may struggle with new field requirements.
