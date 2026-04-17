# The Healf Series B Health-Intelligence Engine: Master Execution Plan

## Core Architecture Summary
* **Database:** Neo4j AuraDB (Native GraphRAG + Vectors).
* **Ingestion:** Firecrawl (Scraping) + NIH DSLD API (Medical Grounding).
* **Orchestration:** LangGraph (Stateful Swarm with `TypedDict` Reducers).
* **Safety & Evals:** NeMo Guardrails (Firewall), DeepEval (CI/CD Quality Gates), Arize Phoenix (Tracing).
* **API:** FastAPI + SlowAPI (Rate Limiting).

---

## Phase 0: Project Scaffolding & Environment Setup
Initialize the absolute source of truth for the project.

### 1. Directory Structure
```text
healf-ai-engineer/
├── data/
│   ├── raw_product_urls.json      # Mock webhook payload of 3 Shopify URLs
│   ├── enriched_products.json     # Output of Component 1
│   ├── mock_users.json            # Static Healf Zone user profiles
│   └── research/                  # 3 PubMed abstracts (.txt)
├── src/
│   ├── enrichment.py              # Component 1 (Firecrawl + NIH DSLD)
│   ├── graph_builder.py           # Component 2 (Neo4j AuraDB Ingestion)
│   ├── chatbot.py                 # Component 3 (LangGraph Nodes & API)
│   └── state.py                   # Component 3 (LangGraph TypedDict schemas)
├── config/
│   └── wellness_guard.co          # NeMo Guardrails configuration
├── tests/
│   ├── test_cases.json            # 5 varied mock user queries
│   └── test_eval.py               # DeepEval pytest script
├── .env                           # API Keys
├── requirements.txt               # Pinned dependencies
├── README.md                      # Deployment instructions
└── ARCHITECTURE.md                # Strategic ADRs and defenses
```

### 2. Environment Variables (`.env`)
```env
OPENAI_API_KEY="sk-..."
NEO4J_URI="neo4j+s://<YOUR_INSTANCE>.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="<YOUR_PASSWORD>"
FIRECRAWL_API_KEY="fc-..."
```

### 3. Dependencies (`requirements.txt`)
```text
llama-index
llama-index-graph-stores-neo4j
langchain-openai
langgraph
instructor
pydantic
firecrawl-py
nemoguardrails
arize-phoenix
deepeval
fastapi
slowapi
uvicorn
requests
```

---

## Phase 1: Component 1 — Product Enrichment Pipeline
**Goal:** Ingest raw e-commerce data, bypass bot protections, and ground it in verified supplement data.

### 1. The Inputs
Create `data/raw_product_urls.json` with 3 target products:
* Atrantil Digestive Supplements (Gut Pillar)
* Magnesium Glycinate (Sleep Pillar)
* Ashwagandha KSM-66 (Mind/Stress Pillar)

### 2. The Pydantic Schema (`src/enrichment.py`)
```python
from pydantic import BaseModel
from typing import List

class EnrichedProduct(BaseModel):
    sku: str
    canonical_name: str # e.g., "Magnesium Glycinate" to prevent graph duplicates
    active_ingredients: List[str]
    target_biomarkers: List[str]
    mechanisms_of_action: List[str]
    contraindications: List[str] # Sourced strictly from NIH DSLD
```

### 3. The Execution Flow
1. **Scrape product pages:** Use the `FirecrawlApp` Python SDK to extract clean Markdown from the 3 URLs. Treat the scraper output as the canonical raw input for product names, ingredients, claims, and page context. *(Reasoning: Faster than Jina, handles Shopify JS, SOC 2 compliant).*
2. **Medical Grounding:** For each active ingredient, use Python `requests` to hit the **NIH Dietary Supplement Label Database (DSLD) API** to fetch known contraindications. *(Reasoning: Supplements are food, not drugs. OpenFDA returns null gaps; NIH DSLD is accurate).*
3. **Structurize:** Pass the Firecrawl Markdown + NIH Data through OpenAI via the `instructor` library, forcing the output to match the `EnrichedProduct` schema.
4. **Save:** Output the final array to `data/enriched_products.json`.

### 4. Product Scraping Rules
* Keep product scraping separate from schema extraction so a fetch failure does not blur the enrichment contract.
* Preserve the scraper snapshot when possible so enrichment and graph debugging can trace each canonical field back to a page capture.

---

## Phase 2: Component 2 — Knowledge Graph Construction
**Goal:** Build the Neo4j GraphRAG layer using idempotent writes to prevent write-lock deadlocks.

### 1. The Corpus
Fetch these specific PubMed abstracts into `data/research/` using a scraper-backed retrieval step, then store the resulting clear-text abstracts in the repository:
* **Sleep:** PMID 23853635 (Magnesium -> GABA -> Sleep)
* **Mind:** PMID 23439798 (Ashwagandha -> Cortisol reduction -> Stress)
* **Gut:** PMID 26365448 (Quebracho -> Methane reduction -> Bloating)

### 1.1 PubMed Scraping Rules
* Use a deterministic scraper or document fetcher for PubMed so the corpus is reproducible.
* Keep one file per PMID so graph inference rules can map directly from document provenance to graph evidence.
* Prefer source-captured abstracts over hand-written summaries when the full abstract is available.

### 2. The Extraction & Schema (`src/graph_builder.py`)
Prompt the LLM to extract relationships fitting this strict directional schema:
`(Symptom) <-[:ALLEVIATES]- (Mechanism) <-[:TRIGGERS]- (Ingredient) <-[:CONTAINS]- (Product)`

### 3. The Database Write (Idempotency)
* Connect to AuraDB using `Neo4jPropertyGraphStore`.
* You **MUST** use parameterized Cypher `MERGE` statements (not `CREATE`).
  * *Example:* `MERGE (i:Ingredient {name: $canonical_name})`
  * *(Reasoning: This handles our "Mix and Batch" deduplication strategy, ensuring that multiple webhooks updating the same ingredient don't spawn duplicate nodes or cause DB deadlocks).*
* **Vectorization:** Configure the LlamaIndex property graph to natively generate embeddings for the text descriptions of the `Mechanism` and `Product` nodes, storing them as properties within AuraDB.

---

## Phase 3: Component 3 — LangGraph Orchestration
**Goal:** Stateful multi-agent routing that eliminates context rot and outputs frontend-ready payloads.

### 1. The Isolated Memory State (`src/state.py`)
```python
from typing import Annotated, List, TypedDict
import operator

class HealfGraphState(TypedDict):
    # Operator.add ensures messages accumulate, preventing KV cache overwrite rot
    messages: Annotated[List[dict], operator.add]
    
    # Immutable user facts (isolated from chat history)
    user_biomarkers: dict 
    
    # Accumulating reasoning trails
    inferred_deficiencies: Annotated[List[str], operator.add]
    retrieved_graph_paths: Annotated[List[str], operator.add]
    
    # Flags and outputs
    is_medical_intent: bool
    ui_payload: dict
```

### 2. The Agent Nodes (`src/chatbot.py`)
* **Node A (Context Extractor):** Loads `data/mock_users.json` (e.g., `user_101` with low ferritin). Parses the latest chat message and updates `user_biomarkers` if new facts are stated.
* **Node B (Clinical Inferencer):** Reads `user_biomarkers` and infers gaps (e.g., "User is an endurance athlete and has twitching -> Needs Magnesium"). Outputs to `inferred_deficiencies`.
* **Node C (Graph Retriever):** Performs Vector Search against Neo4j to find the closest `Mechanism` node, then executes a Cypher traversal to pull the linked `Ingredients` and `Products`. Updates `retrieved_graph_paths`.
* **Node D (Payload Generator):** Uses `instructor` to enforce the final output into the `UIReadyPayload`.

### 3. The UI-Ready Payload Schema
```python
from pydantic import BaseModel

class UIReadyPayload(BaseModel):
    reply_text: str # Must include the "I don't have documented evidence" fallback if graph is empty.
    user_context_acknowledged: List[str]
    citations: List[dict] # Format: {"source": "PMID: 23853635", "finding": "..."}
    recommended_products: List[dict] # Format: {"sku": "...", "name": "..."}
```

---

## Phase 4: API Wrapper & Enterprise Safety
**Goal:** Secure the backend for production API consumption.

### 1. Observability Initialization
At the very top of `src/chatbot.py`, add:
```python
import phoenix as px
px.launch_app() # Boots local trace server on localhost:6006
from openinference.instrumentation.langchain import LangChainInstrumentor
LangChainInstrumentor().instrument()
```

### 2. The FastAPI Server (`src/chatbot.py`)
* Wrap the LangGraph execution block in a FastAPI POST endpoint (`/api/chat`).
* Apply `slowapi` decorator: `@limiter.limit("5/minute")`.

### 3. The NeMo Guardrails Semantic Firewall
* Create `config/wellness_guard.co`.
* Define an intent `define user express medical diagnosis` containing phrases like "diagnose me," "does this look infected," "I have severe chest pain."
* Wrap the FastAPI logic so NeMo evaluates the prompt *first*. If triggered, return: *"I am a wellness assistant, not a doctor. Please consult a medical professional."* (Do not invoke LangGraph).

---

## Phase 5: Evaluation via CI/CD Simulation
**Goal:** Objectively prove the system does not hallucinate.

### 1. The DeepEval Script (`tests/test_eval.py`)
* Import `FaithfulnessMetric` and `AnswerRelevanceMetric` from `deepeval`.
* Write 5 test queries in `tests/test_cases.json`:
  1. Standard recommendation (e.g., "What helps with sleep?")
  2. Context-dependent (e.g., "Based on my biomarkers, what should I take?")
  3. Multi-hop (e.g., "I run marathons and have brain fog.")
  4. Medical Jailbreak (e.g., "Diagnose my irregular heartbeat.")
  5. Out-of-bounds (e.g., "What is the capital of France?")
* Execute the script via `pytest tests/test_eval.py`. Save the passing terminal output logs to include in your README.
