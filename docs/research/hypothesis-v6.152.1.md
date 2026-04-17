# Research: Hypothesis Property-Based Testing

**Library version:** hypothesis 6.152.1
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Hypothesis docs | https://hypothesis.readthedocs.io/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/hypothesis/ | 2026-04-17 |
| GitHub Repository | https://github.com/HypothesisWorks/hypothesis | 2026-04-17 |

## The Correct Approach

Use Hypothesis for property-based testing of deterministic functions. Generate edge cases automatically to uncover regressions.

```python
from hypothesis import given, strategies as st
from src.graph_builder import extract_triples_from_corpus

@given(corpus_text=st.text(min_size=1))
def test_extract_triples_returns_list(corpus_text):
    """Property: extract_triples always returns a list."""
    result = extract_triples_from_corpus(corpus_text)
    assert isinstance(result, list)

@given(
    product_names=st.lists(st.text(min_size=1), min_size=1),
    ingredients=st.lists(st.text(min_size=1), min_size=1),
)
def test_graph_merge_idempotency(product_names, ingredients):
    """Property: MERGE operations are idempotent."""
    # Run twice; results should be identical
    result1 = run_merge_batch(product_names, ingredients)
    result2 = run_merge_batch(product_names, ingredients)
    
    assert len(result1) == len(result2)
    assert result1 == result2
```

## Files This Affects

- `tests/test_enrichment.py` — Property-based edge case testing
- `tests/test_graph_builder.py` — Idempotency and determinism verification

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Manual edge case lists | Limited; Hypothesis generates far more combinations |
| Fuzzing alone | Overkill for deterministic function testing |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by HypothesisWorks
- [ ] License compatibility: Dual license (MPL-2.0 + commercial); verify compatibility for your use case
- [x] Dependency tree risk: Minimal dependencies; stable
- [x] Download stats / popularity: 5M+ weekly downloads, widely used in Python testing
- [x] Single-maintainer risk: David MacIver leads; distributed team

## Known Gotchas / Edge Cases

- **Determinism Required**: Functions being tested must be deterministic; randomness causes flaky tests.
- **Strategy Selection**: Use appropriate strategies (`st.text()`, `st.integers()`, `st.from_regex()`); wrong strategy reduces effectiveness.
- **Example Limits**: Hypothesis may generate thousands of examples; tune `max_examples` if tests run too long.
- **Seed for Reproducibility**: Use `@settings(derandomize=True)` for reproducible failures in CI/CD.
- **Stateful Testing**: Complex workflows can use `RuleBasedStateMachine` for multi-step scenarios; start simple.

## Integration Notes

- Use Hypothesis for deterministic, pure functions (no side effects).
- Pair with pytest for easy integration.
- Start with simple properties (return type, idempotency); don't over-engineer.
- Use `hypothesis.assume()` to filter invalid inputs gracefully.
- Run via: `PYTHONPATH=. uv run pytest tests/ -v`
