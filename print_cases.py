import json
from src.agent.orchestrator import AgentOrchestrator
from src.models.orchestration import OrchestrationRequest
import nest_asyncio

nest_asyncio.apply()

data = json.load(open('evals/datasets/golden_dataset.json'))
orchestrator = AgentOrchestrator.build_default()

for i in [0, 4, 8]:
    case = data[i]
    print(f"\n--- CASE {i} ---")
    print(f"INPUT: {case['input']}")
    req = OrchestrationRequest(user_query=case['input'])
    res = orchestrator.run(req)
    print(f"STATUS: {res.status}")
    if res.status == 'ok':
        print(f"RESPONSE: {res.response_text}")
    elif res.status == 'discovery':
        print(f"DISCOVERY: {res.clarification_question}")
    else:
        print(f"ERROR: {res.error}")

