# Research: SlowAPI Rate Limiting

**Library version:** slowapi 0.1.9
**Status:** Current (with maintenance caution)
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| GitHub Repository | https://github.com/laurentS/slowapi | 2026-04-17 |
| PyPI Package | https://pypi.org/project/slowapi/ | 2026-04-17 |
| GitHub Issues | https://github.com/laurentS/slowapi/issues | 2026-04-17 |

## The Correct Approach

Use SlowAPI as a decorator-based rate limiter for FastAPI endpoints. Be aware of maintenance lag and consider contingency planning.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)

# Global error handler for rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Maximum 5 requests per minute."}
    )

# Apply rate limit decorator
@app.post("/api/chat")
@limiter.limit("5/minute")
async def chat(request: ChatRequest):
    return {"reply": "..."}

@app.get("/api/health")
@limiter.limit("100/minute")
async def health():
    return {"status": "ok"}
```

## Files This Affects

- `src/chatbot.py` — Rate limiter initialization and decorator application
- Tests: `tests/test_chatbot.py` — Rate limit boundary testing

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| No rate limiting | API would be vulnerable to abuse/DoS |
| Redis-based limiter | Adds operational complexity; SlowAPI in-memory is sufficient for MVP |
| Custom middleware | Reinventing wheel; SlowAPI is proven and simple |

## Security Assessment

- [ ] CVE check (Snyk): None known, but package is in maintenance mode
- [ ] Maintenance health: Last release Feb 2024 (8+ months old); slower update cadence than FastAPI/Starlette
- [x] License compatibility: MIT, compatible with project
- [ ] Dependency tree risk: Minimal dependencies; but watch for FastAPI/Starlette compatibility drift
- [x] Download stats / popularity: 1M+ weekly downloads, stable usage
- [x] Single-maintainer risk: Laurent Savaete is primary maintainer; community-supported

## Known Gotchas / Edge Cases

- **FastAPI/Starlette Compatibility**: SlowAPI is maintained at slower cadence; monitor for future incompatibilities.
- **In-Memory Storage**: Rate limit state is not shared across multiple Uvicorn workers; use Redis adaptor for multi-worker deployments.
- **Expiration**: Rate limit counters persist in memory; old entries can accumulate.
- **Granularity**: Limits are per IP by default; token-based or user-based limits require custom `key_func`.

## Integration Notes

- SlowAPI is designed specifically for FastAPI; use decorator pattern.
- For production with multiple workers, consider migrating to Redis-backed limiter (contingency plan).
- Monitor FastAPI/Starlette release notes for compatibility drift.
- Set reasonable defaults (e.g., 5/minute for chat endpoints, 100/minute for health checks).
- Pair with structured logging to track limit violations.
