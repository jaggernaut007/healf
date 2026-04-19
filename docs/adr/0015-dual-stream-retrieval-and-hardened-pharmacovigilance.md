# ADR-0015: Dual-Stream Retrieval and Hardened Pharmacovigilance

## Status
Accepted

## Context
As the Healf engine moved into Phase 7 (Advanced Enrichment), the requirements for retrieval and safety became more stringent. Users need recommendations grounded not only in product marketing data but also in scientific research (mechanisms of action, study findings). Furthermore, the conversational agent must handle high-risk health scenarios (medication interactions, pregnancy, allergies) with extreme caution to maintain trust and safety.

## Decision
We have implemented a **Dual-Stream Retrieval** architecture and a **Hardened Pharmacovigilance Critic**:

1.  **Dual-Stream Retrieval**: The `RetrieverAdapter` (via `build_default_retriever`) now performs two parallel hybrid searches (Vector + Graph) in Neo4j:
    *   **Product Stream**: Retrieves product entities, their ingredients, mechanisms, and USPs based on semantic similarity to the query.
    *   **Research Stream**: Retrieves scientific study entities (PMIDs) and their full summaries/key findings, linked through mechanisms of action.
2.  **Hardened Pharmacovigilance Critic**: The `CriticAdapter` (via `build_default_critic`) implements a multi-layered safety check:
    *   **LLM-Based Review**: A strict system prompt specifically flags Direct Conflicts (contraindications), Irrelevant Evidence, and High-Risk Intents (medication, pregnancy, allergies, diagnostic intent).
    *   **Heuristic Fallback**: A robust fallback mechanism that triggers conversational refusals or redirects if specific high-risk tokens are detected in the query or user profile, ensuring safety even if the LLM call fails.

## Consequences
- **Easier**: Provides significantly more grounded and scientifically backed responses by combining product data with clinical research. Centralizes safety logic into a dedicated, testable "Pharmacovigilance" layer.
- **Harder**: Increases the complexity of the retrieval logic and the Neo4j schema (requiring `Study` nodes and `SUPPORTED_BY` relationships). Higher token usage due to the dual-stream retrieval context being passed to the generator.
