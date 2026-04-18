> Archived note: This file is legacy planning context and is not the canonical execution contract.
> Use SPEC.md, docs/pm-docs/architecture.md, and docs/pm-docs/plan_4.md as the authoritative sources.

## The Founding Engineer Execution Plan

### Phase 0: Environment & Cloud Setup (Timebox: 1 Hour)
Your goal here is a clean repository that a reviewer can run instantly without debugging local infrastructure.

1.  **Repository Structure:**
    * Create standard directories: `data/`, `src/`, `tests/`, and `config/`.
2.  **Neo4j AuraDB Provisioning:**
    * Create a free Neo4j AuraDB instance. 
    * Save the connection URI, username, and password.
3.  **Environment Variables:**
    * Create a `.env.example` file:
        ```env
        OPENAI_API_KEY="sk-proj-..."
        NEO4J_URI="neo4j+s://<YOUR_INSTANCE>.databases.neo4j.io"
        NEO4J_USERNAME="neo4j"
        NEO4J_PASSWORD="<YOUR_PASSWORD>"
        ```
4.  **Dependencies:**
    * Initialize `requirements.txt` with: `llama-index`, `llama-index-graph-stores-neo4j`, `arize-phoenix`, `deepeval`, `nemoguardrails`, `pydantic`, `python-dotenv`.

---

### Phase 1: Product Enrichment Pipeline (Component 1) (Timebox: 2 Hours)
Do not build a live web scraper or complex database for this step. Build a data pipeline that outputs a static, reasoning-ready artifact.

1.  **Mock Raw Data:** * Create `data/raw_products.json` with 5–10 Healf-style products (e.g., Magnesium Glycinate, Ashwagandha).
2.  **Define Schema:**
    * In `src/enrichment.py`, write a strict Pydantic model (`EnrichedProduct`) requiring `active_ingredients`, `mechanisms_of_action`, `target_biomarkers`, and `contraindications`.
3.  **Execute Pipeline:**
    * Use LlamaIndex's `StructuredLLM` to process the raw JSON through your LLM, forcing the output to match your Pydantic schema.
    * Save the output to `data/enriched_products.json`. Your chatbot will read from this static file.

---

### Phase 2: Knowledge Graph Construction (Component 2) (Timebox: 2.5 Hours)
Focus entirely on the quality of the schema and relationships, not the volume of data.

1.  **The Corpus:**
    * Download 3–5 short PubMed abstracts linking common ingredients to Healf goals (e.g., Magnesium for Sleep) and save them in `data/research/`.
2.  **Graph Extraction:**
    * Write `src/graph_builder.py`.
    * Connect to AuraDB using `Neo4jPropertyGraphStore`.
    * Use LlamaIndex’s `PropertyGraphIndex.from_documents()` to process the abstracts.
3.  **Prompt Engineering:**
    * Customize the LlamaIndex extraction prompt to strictly map entities relevant to Healf: `HealthGoal`, `Symptom`, `Biomarker`, `Ingredient`, and `Mechanism`.
4.  **Verification:**
    * Open the Neo4j Aura Console. Visually confirm the nodes and edges were created correctly. Take a screenshot for your documentation.

---

### Phase 3: Health Chatbot Orchestration (Component 3) (Timebox: 4 Hours)
This is the core agentic workflow.

1.  **Initialize Observability:**
    * At the top of `src/chatbot.py`, initialize Arize Phoenix (`px.launch_app()`) to trace all LLM calls locally.
2.  **Build LlamaIndex Tools:**
    * `get_user_context()`: Returns a hardcoded Python dictionary of mock user data (e.g., "User has low ferritin, viewed sleep aids today").
    * `query_product_catalog()`: Searches your `data/enriched_products.json` file.
    * `query_knowledge_graph()`: Executes a retrieval query against the Neo4j `PropertyGraphIndex` (connected to AuraDB).
3.  **Agent Assembly:**
    * Wrap these tools in a `FunctionCallingAgentWorker`. 
4.  **Implement the Safety Guardrail:**
    * Create `config/wellness_guard.co` (NeMo Guardrails format).
    * Define medical intents (e.g., "diagnose me", "chest pain") and route them to a hardcoded string: *"I am a wellness assistant, not a doctor. Please consult a medical professional."*
    * Wrap the LlamaIndex agent execution within the NeMo safety check.

---

### Phase 4: Evaluation via CI/CD Simulation (Timebox: 1.5 Hours)
Prove that your code is production-ready and measurable.

1.  **Test Cases:**
    * Create `tests/test_cases.json` containing 5 varied prompts (e.g., standard wellness question, multi-hop reasoning question, medical injection attempt).
2.  **DeepEval Script:**
    * Write `tests/test_eval.py`.
    * Import DeepEval's `FaithfulnessMetric` (to check against hallucinations) and `AnswerRelevanceMetric`.
3.  **Run the Evals:**
    * Execute `pytest tests/test_eval.py`. Save the terminal output logs to prove the pipeline passes its own quality gates.

---

### Phase 5: Documentation & Submission (Timebox: 1 Hour)
This is where Sr. Staff candidates win the offer.

1.  **Write `ARCHITECTURE.md`:**
    * Use the exact rationale matrix we developed earlier. Highlight the decisions to use LlamaIndex (determinism), AuraDB (frictionless scale), Phoenix (privacy), DeepEval (CI/CD integration), and NeMo (semantic firewall).
2.  **Write `README.md`:**
    * Include the "Drop-the-Mic" note: *"The Knowledge Graph is hosted on a live Neo4j AuraDB instance. You do not need to run extraction pipelines or Docker containers. Add your API key and run the chatbot."*
3.  **Record the Loom Video (Max 8 Mins):**
    * *0:00 - 1:30:* Demo a successful multi-hop query (Symptom -> Graph -> Product).
    * *1:30 - 2:30:* Demo NeMo instantly blocking a medical query.
    * *2:30 - 4:30:* Open Arize Phoenix on localhost to show the exact tool calls and Cypher queries the agent generated.
    * *4:30 - 6:00:* Show the DeepEval `pytest` script to prove your commitment to quality gates.
    * *6:00 - 8:00:* Discuss trade-offs (e.g., what you would do with a 2-week sprint).