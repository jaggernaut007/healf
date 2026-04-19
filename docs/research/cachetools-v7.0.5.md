# Research: cachetools (TTL L1 Caching)

**Library version:** cachetools@7.0.5
**Status:** Current
**Date:** 2026-04-19

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| PyPI | https://pypi.org/project/cachetools/ | 2026-04-19 |
| Official Docs | https://cachetools.readthedocs.io/ | 2026-04-19 |
| Snyk Security | https://snyk.io/advisor/python/cachetools | 2026-04-19 |

## The Correct Approach

Use `@cached` with `TTLCache` for in-memory L1 caching of expensive API calls or idempotent computations.

```python
from cachetools import cached, TTLCache

# Cache up to 100 items with a 1-hour (3600s) TTL
@cached(cache=TTLCache(maxsize=100, ttl=3600))
def fetch_external_data(query: str):
    # Expensive API call here
    return result
```

## Files This Affects

- `src/clients/enrichment_client.py` — Implements `TTLCache` on `fetch_nih_dsld_data` to reduce NIH API load.
- `pyproject.toml` — Pinned to `7.0.5`.

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| `functools.lru_cache` | Missing native TTL (Time-To-Live) support; only supports size-based eviction. |
| Redis (L2 Cache) | Overkill for the current Phase 5/7 local-first architecture; added unnecessary network latency and infrastructure complexity. |
| `dogpile.cache` | More complex configuration; `cachetools` is lighter for simple L1 patterns. |

## Security Assessment

- [x] CVE check: No known CVEs for v7.0.5 as of April 2026.
- [x] Maintenance health: Active (latest release March 2026), high community trust (>300M monthly downloads).
- [x] License compatibility: MIT (Compatible).
- [x] Dependency tree risk: 0 dependencies (Pure Python).
- [x] Download stats / popularity: Extremely high (Key Ecosystem Project).
- [x] Single-maintainer risk assessment: Maintained by Thomas Kemmer; high bus factor due to massive ecosystem integration.

## Known Gotchas / Edge Cases

- **Thread Safety**: `cachetools` classes are NOT thread-safe by default. In multi-threaded environments, a lock must be passed: `@cached(cache=TTLCache(...), lock=threading.Lock())`.
- **Mutable Arguments**: Cache keys are generated from function arguments. If arguments are mutable (like lists/dicts), hashing will fail unless a custom `key` function is provided.
- **Memory Growth**: While `maxsize` limits items, large cached objects can still impact memory if not monitored.

## Integration Notes

`cachetools` is integrated into the `EnrichmentClient` as a "Pattern B (TTL L1 Cache)" industrial performance control. It ensures that repeated requests for the same product safety data do not hit external rate limits and provide sub-millisecond response times for cached entries.
