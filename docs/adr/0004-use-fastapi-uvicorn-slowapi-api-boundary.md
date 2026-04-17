# 4. Use FastAPI + Uvicorn + SlowAPI for the API Boundary

## Status
Accepted

## Context
The system requires a production API surface for chat execution with strict schema contracts, predictable latency characteristics, and request-level abuse controls. The stack also needs straightforward Python-native integration with typed models and async execution.

Package and docs validation confirmed `fastapi`, `uvicorn`, and `slowapi` are suitable for the current architecture, with a known maintenance-risk note for `slowapi` cadence.

## Decision
Use:
- `FastAPI` as the HTTP framework.
- `uvicorn` as the ASGI runtime server.
- `slowapi` for baseline rate limiting at endpoint boundaries.

Apply rate limiting on external-facing chat endpoints and preserve typed request/response schemas through Pydantic.

## Consequences
- Positive: Fast development velocity with explicit schema enforcement.
- Positive: Clear runtime boundary for orchestration and safety middleware.
- Negative: `slowapi` release cadence is slower than adjacent frameworks and must be monitored.
- Negative: Future FastAPI/Starlette shifts may require limiter reassessment.
