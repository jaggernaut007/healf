# Research: pytest Testing Framework

**Library version:** pytest 9.0.3
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official pytest docs | https://docs.pytest.org/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/pytest/ | 2026-04-17 |
| GitHub Repository | https://github.com/pytest-dev/pytest | 2026-04-17 |

## The Correct Approach

Use pytest as the primary test runner for unit, integration, and evaluation tests. Leverage fixtures for setup/teardown and parameterization for edge cases.

```python
import pytest
from src.enrichment import EnrichedProduct

@pytest.fixture
def sample_markdown():
    return "Magnesium Glycinate: Pure elemental magnesium bound to glycine..."

def test_enrichment_schema(sample_markdown):
    """Test that enriched product matches schema."""
    product = EnrichedProduct(
        sku="SKU-001",
        canonical_name="Magnesium Glycinate",
        active_ingredients=["Magnesium"],
        mechanisms_of_action=["GABA synthesis"],
        contraindications=[]
    )
    assert product.sku == "SKU-001"
    assert isinstance(product.active_ingredients, list)

@pytest.mark.parametrize("sku,expected_valid", [
    ("", False),
    ("SKU-001", True),
    (None, False),
])
def test_sku_validation(sku, expected_valid):
    """Test SKU validation edge cases."""
    if expected_valid:
        product = EnrichedProduct(sku=sku, ...)
    else:
        with pytest.raises(ValueError):
            EnrichedProduct(sku=sku, ...)
```

## Files This Affects

- `tests/test_*.py` — All test files
- `pytest.ini` — pytest configuration
- `scripts/init.sh` — Test execution commands

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| unittest (stdlib) | More verbose; pytest fixtures are superior to setUp/tearDown |
| nose | Legacy; pytest has replaced it as de facto standard |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by pytest team
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Minimal dependencies; stable ecosystem
- [x] Download stats / popularity: 20M+ weekly downloads, de facto standard for Python testing
- [x] Single-maintainer risk: Holger Krekel leads; large community support

## Known Gotchas / Edge Cases

- **Fixture Scope**: Use `scope="function"` (default, isolated tests), `scope="module"` (shared setup), or `scope="session"` carefully.
- **Markers**: Use `@pytest.mark.slow` or `@pytest.mark.integration` to skip/filter tests.
- **Async Tests**: Use `@pytest.mark.asyncio` for async test functions.
- **Temporary Files**: Use `tmp_path` fixture for file I/O tests instead of creating files manually.
- **Mocking**: Use `unittest.mock` or `pytest-mock` plugin; avoid mocking external APIs when possible in integration tests.

## Integration Notes

- All tests must pass before marking features complete (Definition of Done).
- Run via: `PYTHONPATH=. uv run pytest tests/`
- Use `pytest.ini` to configure test discovery, markers, and coverage thresholds.
- Aim for 80%+ coverage on business logic, 100% on critical paths (auth, data validation).
- Integrate DeepEval tests in `tests/test_eval.py` for LLM output quality gates.
