# Research: FastAPI HTTP Framework

**Library version:** fastapi 0.136.0
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official FastAPI docs | https://fastapi.tiangolo.com/ | 2026-04-17 |
| FastAPI async guide | https://fastapi.tiangolo.com/async-concurrency/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/fastapi/ | 2026-04-17 |
| GitHub Repository | https://github.com/tiangolo/fastapi | 2026-04-17 |

## The Correct Approach

Use FastAPI for type-safe API endpoints with automatic validation and OpenAPI schema generation.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor

# Init observability
px.launch_app()
LangChainInstrumentor().instrument()

app = FastAPI(title="Healf API", version="1.0.0")
limiter = Limiter(key_func=get_remote_address)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    biomarkers: dict = {}

class ChatResponse(BaseModel):
    reply_text: str
    user_context_acknowledged: list
    citations: list
    recommended_products: list

@app.post("/api/chat")
@limiter.limit("5/minute")
async def chat(request: ChatRequest) -> ChatResponse:
    # Evaluate guardrails first
    if is_protected_intent(request.message):
        raise HTTPException(
            status_code=403,
            detail="Medical diagnosis not supported. Please consult a healthcare professional."
        )
    
    # Execute graph and return payload
    result = compiled_graph.invoke({
        "messages": [{"role": "user", "content": request.message}],
        "user_id": request.user_id,
        "user_biomarkers": request.biomarkers,
    })
    
    return ChatResponse(**result["ui_payload"])

@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Files This Affects

- `src/chatbot.py` — FastAPI app definition and endpoints
- `src/state.py` — Pydantic request/response schemas
- Tests: `tests/test_chatbot.py` — Endpoint integration tests

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Flask | Simpler, but lacks native async/await and auto-validation |
| Django | Overkill for a single microservice; includes ORM/admin overhead |
| Starlette directly | Lower-level; FastAPI provides helpful validation/OpenAPI layers |
| Sync-only views | Would block on long-running orchestration; async is required |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, maintained by Sebastián Ramírez (core dev)
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Depends on Starlette, Pydantic (both actively maintained)
- [x] Download stats / popularity: 10M+ weekly downloads, industry standard for Python APIs
- [x] Single-maintainer risk: Sebastián Ramírez is primary maintainer, but large community support

## Known Gotchas / Edge Cases

- **Async Context**: All database calls (Neo4j, LLM) must be truly async or use thread pools.
- **Request Validation**: Pydantic validates on route entry; invalid requests fail with 422 before reaching handler.
- **CORS**: If frontend is on different origin, enable CORS with `CORSMiddleware`.
- **Uvicorn Configuration**: Ensure `workers` and `threads` are tuned for your workload.
- **Exception Handling**: Use `HTTPException` for API-level errors; log and monitor uncaught exceptions.

## Integration Notes

- FastAPI auto-generates OpenAPI (Swagger) at `/docs` and ReDoc at `/redoc`.
- Combine with `slowapi` for rate limiting per route.
- Use Pydantic models for all request/response contracts.
- Pair with Uvicorn for production serving.
- Integrate NeMo Guardrails before LangGraph invocation in each endpoint handler.
