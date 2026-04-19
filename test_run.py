from src.agent.orchestrator import AgentOrchestrator
from src.models.orchestration import OrchestrationRequest
import nest_asyncio

nest_asyncio.apply()

orchestrator = AgentOrchestrator.build_default()
req = OrchestrationRequest(user_query="I'm feeling fatigued and stressed, what can I take? Please explain why based on research.")
res = orchestrator.run(req)
print("--- RESPONSE ---")
print(res.response_text)
print("--- CITATIONS ---")
print(res.citations)
