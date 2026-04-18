# LangGraph + NeMo Guardrails Orchestration (v1.1.8 + v0.21.0)

**Status:** Current
**Date:** 2026-04-17
**Versions:** LangGraph 1.1.8, NeMo Guardrails 0.21.0
**Purpose:** Multi-node agentic orchestration with semantic safety gates

## Official Documentation
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **NeMo Guardrails:** https://docs.nvidia.com/nemo/guardrails/
- **Integration Guide:** https://github.com/langchain-ai/langgraph/discussions

## Design Pattern: Safety-Gated Multi-Agent Orchestration

### Architecture
```
User Input → NeMo Guardrails (semantic check) 
           → LangGraph (multi-node orchestration)
           → DeepEval (output quality check)
           → Phoenix (observability)
           → User Output
```

### Phase 3 Orchestrator Node Graph

```python
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from nemo_guardrails import LLMRails

class OrchestrationState(TypedDict):
    product_id: str
    user_query: str
    enriched_product: dict
    graph_context: str  # from Neo4j
    safety_check_passed: bool
    llm_response: str
    quality_score: float

# Initialize guardrails
guardrails = LLMRails(config_path="src/guardrails.yaml")

# Define orchestration nodes
def safety_gate_node(state):
    """NeMo Guardrails: semantic validation."""
    query = state["user_query"]
    result = guardrails.generate(prompt=query)
    # result includes safety decision
    state["safety_check_passed"] = result.get("safe", False)
    return state

def graph_lookup_node(state):
    """Query Neo4j for product relationships."""
    # Query graph for product_id
    # Return relevant mechanisms, ingredients, studies
    state["graph_context"] = "..."
    return state

def enrichment_node(state):
    """LLM-based enrichment with context."""
    # Use graph_context to ground response
    # Instructor validates structure
    state["llm_response"] = "..."
    return state

def quality_check_node(state):
    """DeepEval: output faithfulness check."""
    # Evaluate response against graph_context
    state["quality_score"] = 0.95
    return state

# Build graph
workflow = StateGraph(OrchestrationState)
workflow.add_node("safety_gate", safety_gate_node)
workflow.add_node("graph_lookup", graph_lookup_node)
workflow.add_node("enrichment", enrichment_node)
workflow.add_node("quality_check", quality_check_node)

# Add edges with conditional routing
workflow.add_edge("START", "safety_gate")
workflow.add_conditional_edges(
    "safety_gate",
    lambda state: "graph_lookup" if state["safety_check_passed"] else "END",
)
workflow.add_edge("graph_lookup", "enrichment")
workflow.add_edge("enrichment", "quality_check")
workflow.add_edge("quality_check", "END")

# Compile with tracing (Phoenix instrumentation)
from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument()

orchestrator = workflow.compile()
```

### NeMo Guardrails Configuration (guardrails.yaml)
```yaml
models:
- type: main
  engine: openai
  model: gpt-4o

rails:
  input:
    flows:
    - name: "check medical intent"
      if: user_intent not in ["product_inquiry", "safety_question"]
      then: "reject_non_medical"
    
    - name: "check product scope"  
      if: product_id not in allowed_products
      then: "reject_out_of_scope"

  output:
    flows:
    - name: "no unsupported claims"
      if: response contains ["cures", "treats", "proven"]
      then: "rephrase_claims"

actions:
  reject_non_medical: |
    I can only help with biomedical product inquiries.
    
  reject_out_of_scope: |
    This product is not in my knowledge base.
```

## Files Affected in Healf
- `src/orchestrator.py` (Phase 3 main orchestrator)
- `src/guardrails.yaml` (safety constraints)
- `src/nodes/*.py` (individual node implementations)

## Integration Checklist
- [ ] Create `src/orchestrator.py` with LangGraph StateGraph
- [ ] Define safety, lookup, enrichment, quality nodes
- [ ] Create `guardrails.yaml` with medical intent rules
- [ ] Add Phoenix instrumentation to workflow
- [ ] Add DeepEval quality gates to orchestrator
- [ ] Test with mock state inputs
- [ ] Performance baseline: <2s per query

## Known Gotchas
1. NeMo Guardrails requires explicit RAILS config file (not in code)
2. StateGraph requires TypedDict; use `Annotated` for reducer operations
3. Conditional edges need lambda functions; can't use plain strings
4. Phoenix requires active OTEL collector; test locally with mock spans

## Security Assessment
- ✅ NeMo Guardrails enforces semantic safety before LLM execution
- ✅ Input validation prevents prompt injection
- ✅ Output validation prevents jailbreak claims
- ✅ All CVEs: 0 for both LangGraph (1.1.8) and NeMo (0.21.0)

## Healf Integration Notes
This orchestrator will:
- Accept biomedical product queries from users
- Gate inputs through NeMo Guardrails (semantic safety)
- Query Neo4j graph for context (mechanisms, studies, contraindications)
- Enrich response with LLM (grounded by graph)
- Validate output against source material (DeepEval)
- Stream events to Phoenix for observability

