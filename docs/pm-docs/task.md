# Phase 3 Task Brief: Conversational 5-Agent KG-RAG Chatbot

Status: Active
Last Updated: 2026-04-18

## Goal
Deliver Component 3 as a grounded conversational system that uses knowledge graph reasoning, enriched product context, and user safety constraints.

## Must-Have Architecture Elements
1. Typed state
2. Prompt rewrite
3. Intake router
4. Graph retrieval
5. Pharmacovigilance critic
6. Structured output
7. Bounded retries

## Rate Limiting Requirement
Rate limiting is required at the API boundary and is included as a deployment control for chat endpoints.
- If orchestration is exposed through an API in this phase, apply request throttling immediately.
- If API exposure remains deferred, keep rate limiting as a mandatory Phase 4 implementation gate.

## Required Behaviors
1. Conversational response quality (no static templates).
2. Knowledge graph-backed reasoning for retrieval and recommendation context.
3. Safety boundaries that refuse medical diagnosis and treatment requests.
4. Graceful uncertainty when evidence is insufficient.
5. Evaluation gate before final response emission.

## Approved Agent Architecture
- Prompt Rewrite (preprocessing)
- Intake Router
- Domain Specialist
- Graph Retriever
- Pharmacovigilance Critic
- Payload Generator

Execution constraints:
- Safety check runs before specialist, retriever, and generator.
- Critic-to-specialist loop is bounded.
- Graph query execution is read-only and validated.

## Deliverables
1. Typed orchestration state and model contracts.
2. Adapter implementations for each agent role.
3. Orchestrator flow rewired to the approved topology.
4. Unit and integration tests for pass, fail, and retry control paths.
5. Updated docs and progress evidence.

## Done Criteria
- Tests pass with tool output evidence.
- Docs reflect implemented state versus target state accurately.
- Tracker files remain phase-consistent.
- Rate limiting requirement is either implemented at the API boundary or explicitly tracked as a blocking Phase 4 gate.
