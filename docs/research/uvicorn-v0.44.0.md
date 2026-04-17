# Research: Uvicorn ASGI Server

**Library version:** uvicorn 0.44.0
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Uvicorn docs | https://www.uvicorn.org/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/uvicorn/ | 2026-04-17 |
| GitHub Repository | https://github.com/encode/uvicorn | 2026-04-17 |

## The Correct Approach

Use Uvicorn to serve FastAPI applications in development and production with explicit configuration tuning.

```python
# Production run command
# uvicorn src.chatbot:app --host 0.0.0.0 --port 8000 --workers 4 --access-log

# Or programmatically
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.chatbot:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Match CPU cores for production
        reload=False,  # Disable in production
        access_log=True,
        log_level="info",
        env_file=".env",
    )
```

## Files This Affects

- `src/chatbot.py` — FastAPI app definition (referenced by Uvicorn)
- `scripts/init.sh` — (potential startup orchestration)

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Gunicorn + Uvicorn workers | Gunicorn is for WSGI; Uvicorn manages its own worker pool for ASGI |
| Single-threaded dev server | Insufficient concurrency for production; Uvicorn with workers required |
| Docker without worker tuning | Will bottleneck; explicit worker count essential |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by Encode
- [x] License compatibility: BSD-3-Clause, compatible with project
- [x] Dependency tree risk: Minimal dependencies; stable upstream
- [x] Download stats / popularity: 10M+ weekly downloads, industry standard
- [x] Single-maintainer risk: Tom Christie leads Encode; distributed team

## Known Gotchas / Edge Cases

- **Worker Count**: Use `workers = CPU_CORES` for production; default is 1 (single-process mode).
- **Graceful Shutdown**: Uvicorn handles SIGTERM; running requests complete before shutdown.
- **Port Binding**: Ensure port 8000 (or chosen port) is not already in use.
- **Reload in Production**: NEVER use `--reload` in production; it causes worker crashes and state loss.
- **Logging**: Enable `--access-log` for HTTP request monitoring; pair with structured logging for application events.

## Integration Notes

- For local development: `uvicorn src.chatbot:app --reload`
- For production: Specify explicit workers, disable reload, enable logging.
- Pair with Nginx or similar reverse proxy for SSL termination and load balancing.
- Use environment-based configuration (via `.env` or env vars) for port/workers/log-level.
- Monitor Uvicorn startup time; if workers take >10s to start, investigate blocking initialization.
