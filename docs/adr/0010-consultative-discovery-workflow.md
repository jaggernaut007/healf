# ADR 0010: Consultative Discovery Workflow

## Status
Accepted

## Context
Initial user queries are often ambiguous (e.g., "mindful exercise") or lack specific parameters needed for accurate product recommendations. Prior to this ADR, the system would attempt to force a specialist retrieval based on ambiguous terms, often leading to irrelevant or medically risky suggestions.

## Decision
We will implement a "Discovery" node in the orchestration LangGraph. This node triggers when the `IntakeRouter` detects that a query `requires_clarification`. 

Key components of this decision:
1.  **Orchestration Branching**: The graph now branches after the router: `IntakeRouter` -> `Discovery` (if ambiguous) or `Specialist` (if clear).
2.  **Stateful Clarification**: The Discovery node uses an LLM to generate a conversational clarification question, preserving the `chat_history` to allow for multi-turn intent resolution.
3.  **Blocking Retrieval**: Product retrieval is blocked until the intent is clarified to prevent "hallucinated" or irrelevant recommendations.
4.  **Schema Standardization**: The `OrchestrationResult` and `RoutingIntent` models were updated to include `requires_clarification` and `clarification_question` fields.
5.  **Knowledge Graph Integration**: The discovery agent's prompt dynamically loads `symptom_name` and `mechanism_name` entities from the graph, ensuring clarification questions map perfectly to fulfilling products.
6.  **High Reasoning Budget**: The discovery API call utilizes `reasoning_effort="high"` to grant the LLM maximum hidden reasoning tokens, increasing fidelity when diagnosing ambiguous intents.

## Consequences
- **Positive**: Improved user experience through consultative guidance; reduced risk of irrelevant recommendations.
- **Negative**: Increased latency for ambiguous queries (requires an extra LLM turn); increased complexity in the orchestration graph.
- **Neutral**: Requires persistent session state (chat history) to be passed through all nodes.
