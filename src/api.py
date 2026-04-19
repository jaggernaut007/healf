from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.agent.orchestrator import AgentOrchestrator
from src.models.orchestration import OrchestrationRequest

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Healf Series B API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initializing orchestrator - will use env keys
orchestrator = AgentOrchestrator.build_default()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: ChatRequest, http_request: Request):
    try:
        orch_request = OrchestrationRequest(
            user_query=request.message,
            user_id=request.user_id
        )
        result = orchestrator.run(orch_request)
        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
