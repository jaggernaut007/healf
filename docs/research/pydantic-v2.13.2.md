# Research: Pydantic v2 Schema Validation

**Library version:** pydantic 2.13.2
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Pydantic v2 docs | https://docs.pydantic.dev/latest/ | 2026-04-17 |
| Migration guide (v1→v2) | https://docs.pydantic.dev/latest/migration/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/pydantic/ | 2026-04-17 |
| GitHub Repository | https://github.com/pydantic/pydantic | 2026-04-17 |

## The Correct Approach

Use Pydantic v2 for all schema definitions. Avoid v1 patterns; v2 has breaking changes but superior performance and clarity.

```python
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional

class EnrichedProduct(BaseModel):
    """Pydantic v2 schema with strict validation."""
    
    model_config = ConfigDict(strict=True)  # Enforce type strictness
    
    sku: str = Field(..., min_length=1)
    canonical_name: str = Field(..., description="Ingredient name from NIH RxTerms")
    active_ingredients: List[str]
    target_biomarkers: List[str] = Field(default_factory=list)
    mechanisms_of_action: List[str]
    contraindications: List[str]
    source_url: Optional[str] = None

class ChatRequest(BaseModel):
    user_id: str
    message: str
    biomarkers: dict = Field(default_factory=dict)

# Validation happens automatically
product = EnrichedProduct(
    sku="SKU-001",
    canonical_name="Magnesium Glycinate",
    active_ingredients=["Magnesium"],
    mechanisms_of_action=["GABA synthesis"],
    contraindications=[]
)

# Serialize to dict/JSON
product.model_dump()
product.model_dump_json()
```

## Files This Affects

- `src/models/product.py` — Product schema definitions
- `src/chatbot.py` — Chat request/response schemas
- `src/enrichment.py` — EnrichedProduct validation
- `tests/` — Schema validation tests

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Pydantic v1 | End-of-life; v2 has performance improvements and cleaner syntax |
| dataclasses | No built-in validation; Pydantic provides type coercion and error messages |
| Protocol/TypedDict | No runtime validation; Pydantic enforces contracts at runtime |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by the Pydantic team
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Minimal core dependencies; pydantic-core is well-maintained
- [x] Download stats / popularity: 50M+ weekly downloads, de facto Python validation standard
- [x] Single-maintainer risk: Samuel Colvin leads Pydantic; distributed team

## Known Gotchas / Edge Cases

- **v1 vs v2 Breaking Changes**: Do not import from `pydantic.v1` unless bridging legacy code; use only v2 patterns.
- **Strict Mode**: Use `ConfigDict(strict=True)` for contract boundaries (API inputs, LLM outputs).
- **Custom Validators**: Use `field_validator` (v2) not `validator` decorator; apply per-field or model-level.
- **Serialization**: Use `.model_dump()` (dict) or `.model_dump_json()` (JSON string); `dict()` is deprecated.
- **Serialization Aliases**: Use `Field(alias="...")` for API input aliases; separate from model field names.

## Integration Notes

- Always use Pydantic v2 syntax; never import `pydantic.v1`.
- Define schemas in `src/models/` for reuse across modules.
- Pair with `instructor` for LLM-enforced schema compliance.
- FastAPI automatically validates path/query/body params against Pydantic models.
- Use `model_dump(mode="json")` for JSON serialization to avoid datetime/UUID issues.
