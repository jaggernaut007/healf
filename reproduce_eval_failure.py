
import os
import json
from src.agent.orchestrator import AgentOrchestrator, OrchestrationConfig
from src.models.orchestration import OrchestrationRequest

def reproduce():
    config = OrchestrationConfig(evaluation_threshold=0.7, enable_observability=False)
    orchestrator = AgentOrchestrator.build_default(config=config)
    
    cases = [
        "What are the benefits of Magnesium Glycinate for sleep?",
        "Optimize Rhodiola Rosea for increasing power output and endurance in a high-intensity session.",
        "Wut pill for brain focus? am tired and cant think good.",
        "Tell me about 'Ashwaganda' for stress.",
        "How should I stack L-Tyrosine and Magnesium for recovery after 5am training?"
    ]
    
    for query in cases:
        print(f"\n--- Testing Query: {query} ---")
        request = OrchestrationRequest(user_query=query)
        
        # Manually run parts to debug
        rewritten = orchestrator.rewrite(query)
        print(f"Rewritten: {rewritten.normalized_text}")
        
        routing = orchestrator.route(rewritten)
        print(f"Routing: {routing.domain}, {routing.risk_level}")
        
        plan = orchestrator.specialize(rewritten, routing)
        print(f"Plan Terms: {plan.key_terms}")
        
        result = orchestrator.run(request)
        print(f"Status: {result.status}")
        if result.status == "failed":
            print(f"Error: {result.error}")
        if result.validation_errors:
            print("Validation Errors:")
            for err in result.validation_errors:
                print(f"  - {err.code}: {err.message}")
        if result.response_text:
            print(f"Response: {result.response_text[:200]}...")

if __name__ == "__main__":
    reproduce()
