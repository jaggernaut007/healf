# Healf Architecture Document

## 1. System Design
Healf’s architecture consists of three decoupled components operating in a pipeline:
*   **Component 1 (Enrichment Client):** Scrapes product URLs (using Firecrawl/Jina fallback), extracts a strict `EnrichedProduct` schema via Instructor (LLM), and grounds the data using the NIH RxTerms API.
*   **Component 2 (Graph Builder):** Ingests the enriched product JSON and PubMed research markdown. It infers and writes `GraphTriple` elements into Neo4j using idempotent Cypher `MERGE` statements.
*   **Component 3 (Agent Orchestrator):** A LangGraph state machine (`AgentOrchestrator`) controlling intent classification, prompt rewriting, graph traversal, a pharmacovigilance critic, payload generation, and final heuristic quality gating.

**Contracts & Failure Modes:** 
Components interface via explicit JSON schemas and the Neo4j database. 
*   If the Enrichment pipeline fails, products lack mechanistic details, degrading graph connectivity but keeping the system online. 
*   If the Graph is unavailable, the `retriever` adapter raises an error, and the Orchestrator gracefully falls back to returning a "failed" state rather than hallucinating answers. 
*   If any internal LangGraph node fails (e.g., the safety gate or evaluator LLM), the system fails closed explicitly.

## 2. Knowledge Graph Schema
The Neo4j property graph encodes five primary entities:
*   `Product` (Contains SKU, canonical name)
*   `Ingredient` (Active compounds like "Magnesium Glycinate")
*   `Mechanism` (Biological pathways, e.g., "GABA signaling support")
*   `Symptom` / `Biomarker` (Health goals like "Sleep" or "Stress")
*   `Research` (Source PMIDs backing the claims)

**Why this structure?** To enable **topological reasoning**. Instead of a vector database loosely mapping "brain fog" to a random product, the graph enforces strict traversal: *Symptom (Brain Fog) → Mechanism (Neurotransmitter synthesis) → Ingredient (B-Vitamins) → Product.* 
**Inference Querying:** The LangGraph `specialist` node outputs a strict `GraphQueryPlan` (operation, domain, risk_level, and keywords). The retriever dynamically ranks these against graph nodes, returning precise `RetrievalChunk` objects with product contraindications attached.

## 3. Enrichment Design
**Schema:** The `EnrichedProduct` Pydantic schema acts as the backbone, defining `sku`, `canonical_name`, `active_ingredients`, `target_biomarkers`, `mechanisms_of_action`, and `contraindications`.

**Pipeline:** Raw HTML/Markdown is fetched, passed into an Instructor-wrapped LLM (`gpt-5.4-mini`) to force structural adherence, and then safety-checked via the `fetch_nih_dsld_data` method against the NIH API to append true clinical contraindications. 

**What is lost without it?** Marketing copy would dominate the knowledge base. Semantic dilution would occur, and safety validations would fail because product contraindications would not be machine-readable by the Critic node.

## 4. Context Assembly
**State Structure:** The LangGraph `OrchestrationState` (a TypedDict) serves as the context window.
**Assembly & Dropping:** Immutable user facts (the `user_profile` containing allergies, conditions, and medications) are explicitly separated from the transient `chat_history`. If the context window fills, older chat turns are summarized or truncated, but the `user_profile` and ongoing `validation_errors` from the critic are never dropped. This prevents "RAG amnesia".
**Retrieval Strategy:** The context window receives evidence only through the `specialist` node, which generates read-only `GraphQueryPlan`s. If evidence is overwhelming, the `retriever` limits chunks to the top 3-5 via term-scoring algorithms. 

## 5. Evaluation Framework
**Eval-Driven Development (EDD):** We adopt an EDD workflow for all agentic nodes. This means we use our evaluation results (from unit tests and DeepEval) to drive iterative improvements in fallback heuristics and LLM prompts. By reproducing failures (like missed allergy warnings) in dedicated tests, we ensure that every architectural hardening is grounded in empirical evidence rather than "prompt vibes".

**Offline Metrics:** We use DeepEval (`FaithfulnessMetric` and `AnswerRelevancyMetric`) in our offline evaluation suite (`tests/evals/`) to measure regression against a "Golden Dataset" of 10-20 high-signal health queries.
*   **Faithfulness:** Measures if the final payload hallucinates claims not present in the Neo4j `RetrievalChunk`s.
*   **Answer Relevancy:** Measures how well the response addresses the user's intent.

**Runtime Quality Gating:** The orchestrator uses a **Heuristic Quality Gate** inside the LangGraph `evaluate` node. This uses keyword density, evidence mapping (ensuring at least one citation), and length constraints to score the response before emission.

**Failure Modes & Trust:** 
- **LLM-as-a-Judge Failure:** DeepEval can be non-deterministic or suffer from the same parametric memory biases as the generator. If the context is semantically complex, the judge might approve a "plausible but wrong" answer.
- **Heuristic Failure:** Heuristic gates can be too rigid, blocking high-quality but unconventional responses.
- **Trust Ranking:** In production, I would trust the **FaithfulnessMetric** (LLM-as-a-Judge) **least**. Its high latency and "recursive hallucination" risk (where the judge hallucinate that the generator didn't hallucinate) make it unsuitable for real-time safety. I trust our **Fail-Closed Safety Model** (Safety Node + Critic) most, as it is grounded in deterministic checks and strict schema enforcement.

## 6. Safety Model
The chatbot operates on a strict **Fail-Closed** philosophy.

**Safety Controls & Coverage:**
1.  **Intent Classification (Intake):** Uses a Coordinator LLM to catch diagnostic intent (`is_clinical_diagnosis_request`) and blocks literal blacklisted phrases (e.g., "cure", "heart attack").
2.  **Pharmacovigilance Critic (Supervisor):** Analyzes retrieved graph evidence against the `user_profile` (allergies, medications, conditions). It explicitly flags `ALLERGY_RECHECK`, `MEDICATION_CAUTION`, and `PREGNANCY_CAUTION`.
3.  **NIH Grounding:** The enrichment pipeline cross-references active ingredients with the NIH RxTerms API to fetch clinical contraindications, which are then encoded as hard edges in the graph.

**What it catches:** Direct medical advice, known supplement-medication interactions (e.g., St. John's Wort + SSRIs), and allergic conflicts based on the user's profile.
**What it misses:** 
- **Subtle Diagnostic Intent:** Phrasings like "My skin is peeling, which cream?" might bypass the "clinical diagnosis" check if phrased as a product inquiry.
- **Graph Gaps:** If an interaction is not in the Neo4j graph or the NIH database (e.g., a very new or obscure herbal supplement), the Critic will not flag it.
- **Non-Linear Polypharmacy:** Complex interactions involving 3+ medications are difficult to resolve via single-turn retrieval and may be missed by the current Critic logic.


## 7. What I Did Not Build
**Honest Scoping:** I did not build the frontend chat UI (React/Next.js), auth, or complex vector database replication (relying entirely on Neo4j for semantic/graph intersections).
**Full Sprint Additions:** Given another week, I would implement Language Agent Tree Search (LATS) for the Critic node. Simulating multi-branch medication interaction pathways allows for a much deeper understanding of complex polypharmacy constraints. I would also integrate **DSPy** to algorithmically compile and optimize prompt schemas based on our DeepEval suite.
**What I wouldn't change:** The core LangGraph state separation and Neo4j topological reasoning. These are foundational and scale infinitely.

## 8. Founding Engineer Decisions
If starting Day 1 at Healf, these are the irreversible AI architecture decisions I'd make:

1.  **Grammar-Level Enforcement over Prompt Engineering:** We use `instructor` and dynamic Pydantic Enums to strictly cast LLM outputs (like Discovery `AvailablePathwaysEnum`). Telling an LLM "IMPORTANT: ONLY USE THESE CATEGORIES" fails in production. Enforcing it at the JSON grammar level completely eliminates the hallucination surface.
2.  **Strictly Typed State over Chained Prompts:** Using LangGraph's `TypedDict` for the memory layer explicitly segregates user health profiles from conversational drift. Trying to manage this via massive array-concatenation in LangChain `LLMChain`s inevitably leads to token overflow and lost medical context. 
3.  **Graph Topology over Pure Vector DBs:** Vectors suffer from semantic dilution (e.g., matching "brain fog" to an irrelevant but semantically similar marketing string). Neo4j enforces hard edges. This provides the exact audit trail needed for clinical product recommendations: we know *exactly* which node led to which product, and we can prove it.
