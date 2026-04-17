# Research: LangGraph Orchestration Runtime

**Library version:** langgraph 1.1.8
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official LangGraph docs | https://langchain-ai.github.io/langgraph/ | 2026-04-17 |
| LangGraph Python guide | https://langchain-ai.github.io/langgraph/how-tos/create-graph-agent/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/langgraph/ | 2026-04-17 |
| GitHub Repository | https://github.com/langchain-ai/langgraph | 2026-04-17 |

## The Correct Approach

Use LangGraph to define multi-node orchestration with explicit state management via `TypedDict` and accumulator semantics.

```python
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
import operator

class HealfGraphState(TypedDict):
    # Accumulator: messages persist across turns
    messages: Annotated[List[dict], operator.add]
    
    # Immutable user context
    user_biomarkers: dict
    
    # Accumulating reasoning
    inferred_deficiencies: Annotated[List[str], operator.add]
    retrieved_graph_paths: Annotated[List[str], operator.add]
    
    # Outputs
    is_medical_intent: bool
    ui_payload: dict

def context_extractor(state: HealfGraphState):
    # Load user biomarkers from data
    return {"user_biomarkers": {...}}

def clinical_inferencer(state: HealfGraphState):
    # Infer deficiencies from biomarkers
    return {"inferred_deficiencies": [...]}

def graph_retriever(state: HealfGraphState):
    # Query Neo4j and accumulate paths
    return {"retrieved_graph_paths": [...]}

def payload_generator(state: HealfGraphState):
    # Generate UI payload
    return {"ui_payload": {...}}

# Build graph
graph = StateGraph(HealfGraphState)
graph.add_node("extract", context_extractor)
graph.add_node("infer", clinical_inferencer)
graph.add_node("retrieve", graph_retriever)
graph.add_node("generate", payload_generator)

graph.add_edge("extract", "infer")
graph.add_edge("infer", "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

graph.set_entry_point("extract")
compiled = graph.compile()
result = compiled.invoke(initial_state)
```

## Files This Affects

- `src/chatbot.py` — Graph definition and node implementations
- `src/state.py` — TypedDict state schema definitions
- `tests/test_chatbot.py` — Node behavior and state accumulation tests

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Simple sequential chains | Cannot handle cyclical reasoning or multi-turn context accumulation |
| Manual state threading | Error-prone, verbose, hard to debug agent decisions |
| Async callbacks alone | Insufficient for stateful multi-agent orchestration |
| Custom graph implementation | Reinventing wheel; LangGraph provides proven abstractions |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by LangChain team
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Depends on langchain core; actively maintained
- [x] Download stats / popularity: 5M+ weekly downloads, growing adoption
- [ ] Single-maintainer risk assessment: Part of LangChain team; distributed ownership

## Known Gotchas / Edge Cases

- **State Accumulation**: Use `operator.add` for fields that should append, not replace.
- **Node Return Format**: Each node must return a dict matching state keys; missing keys are ignored.
- **Cyclical Graphs**: Ensure termination conditions are explicit (use conditional edges or END).
- **Debugging State**: Use `.get_graph().draw_ascii()` or `.get_graph().draw_mermaid_png()` for visualization.
- **Serialization**: State must be JSON-serializable for persistence; avoid complex objects.

## Integration Notes

- Define all state fields upfront in `src/state.py` as a single `TypedDict`.
- Each node is a pure function that reads state and returns updated fields.
- Use `Annotated[Type, reducer_fn]` for fields that need custom merge behavior.
- Pair with `arize-phoenix` instrumentation for full observability across node transitions.
- Test nodes independently before wiring into the full graph.
