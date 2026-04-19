# 11. Use Coordinator Node for Dynamic Cognitive Classification

## Status
Accepted

## Context
The previous safety strategy relied on `nemoguardrails` (ADR-0005) for semantic checking before routing into the primary orchestration pipeline. However, NeMo added significant complexity, dependency issues, and required a separate definition format (`.co` files). We need a unified mechanism to determine both safety (is this a clinical request?) and routing intent (which domain, and is discovery required?). Pydantic structured output models via `instructor` are a proven method within our stack to enforce schemas.

## Decision
Replace NeMo Guardrails with a purely model-parametric "Coordinator Node" (Strategy 1).

- Use `instructor` against the LLM to populate a predefined Pydantic schema (`IntentClassification`).
- The schema will explicitly capture boolean safety flags (`is_clinical_diagnosis_request`) alongside routing hints (`primary_domain`, `requires_discovery`) and `reasoning`.
- Run this as the very first node in orchestration.
- If `is_clinical_diagnosis_request` is True, fail the query and return a deterministic safety block.
- Otherwise, pass the classification context downstream to the router to avoid redundant LLM calls.

## Consequences
- Positive: Eliminates the `nemoguardrails` dependency, simplifying packaging and reducing load times.
- Positive: Unifies safety and routing into a single intelligent node, improving efficiency.
- Positive: Structured outputs provide precise, predictable control over failure conditions.
- Negative: Relies entirely on the LLM's parametric capabilities for semantic safety checks, though backed up by explicit heuristic block phrases.
