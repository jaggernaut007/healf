***

# System Architecture: Healf Health-Intelligence Engine

## Core Philosophy
This architecture was designed entirely around the mandate that health-tech AI must be **reliable, grounded, and measurable**. As Healf transitions into a diagnostics-led platform (Healf Zone), standard probabilistic RAG systems are insufficient and medically risky. 

I rejected standard RAG in favor of a stateful LangGraph agent swarm backed by a Neo4j ontology. This ensures that every recommendation is *grounded* in strict graph traversal, *reliable* through Pydantic data contracts and NeMo safety routing, and objectively *measurable* via CI/CD evaluation integration.

---

## 1. System Design & Orchestration (Component 3)

The core orchestrator is not a linear pipeline, but a **stateful multi-agent swarm** built with LangGraph. 

**The Context Rot Problem:** Standard chatbots suffer from "context rot" as conversations grow, passing giant transcripts to the LLM and causing hallucination. 
**The Solution:** I implemented an "Isolate and Distill" architecture using Python `TypedDict` with `operator.add` reducers. The LangGraph state separates immutable facts (biomarkers, known conditions) from the transient chat history.

**The Routing Flow:**
1. **Node A (Context Extractor):** Reads the chat and updates immutable facts in the `user_biomarkers` state.
2. **Node B (Clinical Inferencer):** Infers latent deficiencies (e.g., *Endurance Athlete + Twitching = Magnesium Gaps*) based on the isolated facts.
3. **Node C (Graph Retriever):** Uses inferred gaps to traverse the Neo4j Knowledge Graph.
4. **Node D (Payload Generator):** Drafts the final response and forces it into a `UIReadyPayload` JSON schema. 

**UI/Frontend Empathy:** The backend does not return raw Markdown strings. It returns a strict JSON object containing `reply_text`, `citations`, and `recommended_products`. This allows the frontend team to natively render 'Source' badges and clickable 'Add to Cart' UI cards directly in the chat interface.

---

## 2. Knowledge Graph Schema & Vectorization (Component 2)

I explicitly avoided introducing a standalone Vector DB (like Pinecone). Introducing disjointed databases creates synchronization issues. Instead, I built a hybrid **GraphRAG** system utilizing Neo4j AuraDB.

**The Schema Pattern:**
We use clinically directional edges:
`(Symptom) <-[:ALLEVIATES]- (Mechanism) <-[:TRIGGERS]- (Ingredient) <-[:CONTAINS]- (Product)`

**Vector Integration:**
Text embeddings are stored directly as properties on the `Mechanism` and `Product` nodes inside Neo4j. 
* *Inference Strategy:* We use semantic vector search to find the correct entry node (e.g., vector-matching the user's query to a specific `Mechanism`), and then switch to **deterministic graph traversal** to find the connected ingredients and safe SKUs. This prevents the "semantic dilution" that plagues standard Vector DBs.

**PubMed Corpus Intake:**
The knowledge graph corpus is built from scraper-backed PubMed abstract captures saved under `data/research/`. Each abstract file stays tied to a PMID so the extraction step can cite the exact evidence source used for each relationship.

---

## 3. Product Enrichment & Canonicalization (Component 1)

This pipeline extracts raw product data and standardizes it into reasoning-ready JSON.

**The Tech Stack:**
* **Firecrawl:** Used over traditional scrapers for its speed, JS-rendering, and SOC 2 compliance.
* **NIH DSLD API:** Rather than using OpenFDA (which is tuned for pharmaceutical drugs), I grounded the enrichment step using the NIH Dietary Supplement Label Database. Because Healf's catalog is wellness-heavy, this ensures our extracted contraindications are accurate for food-grade supplements.
* **Instructor (Pydantic):** Forces the LLM to output structured data.

**Scraper-First Product Intake:**
Product descriptions, ingredient lists, and visible claims should come from scraper output, not hand-entered catalog notes. The scrape is the primary raw input; the enrichment model only standardizes and grounds what the scraper captured.

**Idempotent Ingestion & Deduplication:**
To prevent database deadlocks and node duplication when e-commerce data updates asynchronously, the Cypher extraction pipeline utilizes parameterized `MERGE` operations. The LLM is instructed to map all ingredients to a `canonical_name` (e.g., merging "Mag. Glycinate" and "Magnesium Bisglycinate" into one node).

---

## 4. Safety Model & Medical Guardrails

"You are a helpful wellness assistant" is not a security boundary. I implemented a **Safety Cascade**:

1. **The Semantic Firewall (NeMo Guardrails):** Sitting at the API gateway level before LangGraph is even invoked. If a user asks a high-risk medical question (e.g., "diagnose my chest pain"), NeMo identifies the intent via fast embeddings and deterministically returns a hardcoded disclaimer.
2. **Closed-Book Grounding:** The LangGraph Response Agent operates on a strict "I don't know" policy. If the Neo4j graph returns an empty traversal path, the agent is programmatically forbidden from answering using its parametric memory.

---

## 5. Evaluation Framework & Observability

You cannot improve what you cannot measure. 
* **Observability (Arize Phoenix):** Phoenix traces every LangGraph node transition and Cypher query locally, ensuring deep visibility into the swarm's logic without leaking Healf Zone health data to a third-party cloud provider.
* **CI/CD Quality Gates (DeepEval):** I integrated `deepeval` natively into `pytest`. We score `Faithfulness` (Did it cite the Neo4j graph?) and `AnswerRelevance`. In production, this script blocks pull requests if a prompt tweak causes the `Faithfulness` metric to drop below 95%.

---

## 6. Scoping: What I Did Not Build

Given the time constraints, I made strict, pragmatic scoping decisions to focus on core AI infrastructure:
* **No Frontend:** I did not build a React/Streamlit app. The final deliverable is the API payload ready for frontend consumption.
* **No Live Webhooks:** In production, Component 1 would trigger via a Shopify webhook when the curation team adds a SKU. Here, I mocked the webhook payload via local JSON reading.
* **No Highly-Transactional Graph Data:** I did not map individual user sessions as nodes in Neo4j. Mixing volatile user chat state with immutable medical facts destroys database caching strategies. User state lives strictly in LangGraph memory.

---

## 7. Founding Engineer Decisions (First 14 Days)

If starting on Day 1 at Healf, here are the AI infrastructure decisions I would make that are hardest to reverse:

1. **Enforcing "Mix and Batch" Graph Ingestion:** As we scale, naive `MERGE` queries during concurrent product updates will cause Neo4j write-lock deadlocks. I would immediately implement a Celery/Redis queue to partition incoming webhook data by Node ID, eliminating lock contention.
2. **Treating Evals as Code:** Establishing the DeepEval CI/CD pipeline on week one. If we wait until we have 10,000 users to start evaluating hallucination rates, we are already liable. AI evaluations must be blocking quality gates, not just dashboard metrics.