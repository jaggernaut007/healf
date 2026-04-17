# Research: Requests HTTP Client Library

**Library version:** requests 2.33.1
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Requests docs | https://requests.readthedocs.io/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/requests/ | 2026-04-17 |
| GitHub Repository | https://github.com/psf/requests | 2026-04-17 |

## The Correct Approach

Use `requests` for synchronous HTTP calls to external APIs (NIH DSLD, etc.). For async contexts, consider `httpx` or `aiohttp`, but use `requests` within thread executors if needed.

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up retries for robust API calls
def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session()

# Example: NIH DSLD API call
response = session.get(
    "https://dsld.od.nih.gov/dsld/api/v1/products",
    params={"ingredient": "magnesium"},
    timeout=10
)
response.raise_for_status()
data = response.json()
```

## Files This Affects

- `src/clients/enrichment_client.py` — NIH DSLD API calls
- `src/enrichment.py` — Product page fetching (fallback if Firecrawl unavailable)
- Tests: `tests/test_enrichment_client.py` — API mock/fixture tests

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| urllib | Standard library, but verbose; requests is cleaner for the majority of use cases |
| httpx | Good async support, but overkill for synchronous NIH API calls in phase 1 |
| aiohttp | Better for async pipelines; current enrichment flow is synchronous |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Mar 2026, actively maintained by Kenneth Reitz (core) and team
- [x] License compatibility: Apache-2.0, compatible with project
- [x] Dependency tree risk: Minimal dependencies; stable upstream (urllib3)
- [x] Download stats / popularity: 50M+ weekly downloads, de facto standard for HTTP in Python
- [x] Single-maintainer risk: Kenneth Reitz + team; large community support

## Known Gotchas / Edge Cases

- **Timeout**: Always set `timeout=` to avoid hanging connections (default is no timeout).
- **SSL Verification**: Use `verify=True` (default) in production; disable only for testing.
- **Retries**: Implement exponential backoff for transient errors (429, 5xx responses).
- **Session Reuse**: Reuse `Session` objects for connection pooling and performance.
- **API Rate Limits**: Monitor 429 responses; implement backoff and respect Retry-After headers.

## Integration Notes

- Create a reusable session factory with retry logic for all external API calls.
- Always catch `requests.RequestException` for network errors.
- Log request/response details for debugging (but avoid logging sensitive headers like Authorization).
- For NIH DSLD calls, parse JSON responses and validate against expected schema before storing.
- If async is needed in future, migrate to `httpx` with minimal changes.
