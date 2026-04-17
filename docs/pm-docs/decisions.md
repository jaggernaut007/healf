Here is the definitive **Architectural Decision Record (ADR)** for your Healf take-home task. This is exactly what you should use as a cheat sheet during your live 60-minute technical debrief. It proves that every choice you made was deliberate, balancing the 12-hour constraint with a Series B production vision.

### 1. Decisions We Took (The "Series B" Flexes)

* **GraphRAG natively inside Neo4j (over separate databases):** We decided to store vector embeddings directly on the `Mechanism` and `Product` nodes inside Neo4j. This allows us to use semantic search to enter the graph, and strict directional relationships (edges) to traverse it, preventing "semantic dilution."
* **LangGraph with `TypedDict` Reducers (over LlamaIndex):** We shifted from linear RAG to a stateful LangGraph swarm. Crucially, we used `TypedDict` and `operator.add` to create an "Isolate and Distill" memory state. This prevents "context rot" and KV Cache penalties as conversations get longer.
* **Idempotent Ingestion (`MERGE` statements):** We enforced parameterized `MERGE` Cypher queries for Graph construction. This prevents database deadlocks and duplicate node creation when webhooks asynchronously push new products into the system.
* **Strict UI-Ready JSON Payloads:** We decided the backend will not return raw markdown text. It returns a Pydantic-enforced JSON object containing `reply_text`, `citations` (linked to PubMed), and `recommended_products`. This shows high product empathy for the frontend team.
* **A "Safety Cascade" (NeMo Guardrails):** We chose to implement a deterministic semantic firewall in front of the LLM. If a user asks for medical advice, NeMo catches the intent and blocks it instantly, ensuring a 0% hallucination rate on high-risk medical queries.
* **Evaluation as a CI/CD Quality Gate (DeepEval):** We decided to use `pytest` with DeepEval (`Faithfulness` and `AnswerRelevance`) rather than just logging outputs. This treats AI evaluation like traditional software unit testing.

---

### 2. Decisions We Went Against (The Contrarian/Expert Choices)

* **We went against multi-agent debate swarms (e.g., AutoGen, CrewAI):** "Agent debate" introduces high latency, massive token costs, and unpredictability. In health-tech, we need deterministic workflows, which is why we chose LangGraph's predictable, graph-based routing instead.
* **We went against standard Vector RAG (e.g., Pinecone/Milvus):** Standard RAG pulls text chunks based on "similarity," which is dangerous in healthcare (e.g., a drug that *treats* a disease is semantically similar to a drug that *causes* it). We opted for a strict Knowledge Graph to enforce logical boundaries.
* **We went against OpenFDA for Grounding:** OpenFDA is built for pharmaceutical drugs. Because Healf's catalog is wellness and supplement-heavy, we pivoted to the **NIH Dietary Supplement Label Database (DSLD)**, which is legally and scientifically relevant to the products Healf actually sells.
* **We went against Jina Reader and Shopify `.json` scraping:** Jina proved too slow (nearly 8 seconds of latency), and Shopify native endpoints are often bot-protected. We pivoted to **Firecrawl** because of its speed, JS-rendering capabilities, and enterprise SOC 2 compliance.

---

### 3. Decisions We Skipped / Scoped Out (The Pragmatic Compromises)

* **We skipped building a Frontend UI:** The prompt asks for an AI infrastructure prototype. Wasting 4 hours building a React or Streamlit app detracts from the core backend logic. We prove UI awareness by returning the `UIReadyPayload` JSON instead.
* **We skipped live Webhook integration:** In production, Component 1 would be triggered by Shopify webhooks. Given the constraints, we skipped the webhook listener and opted to read from a local `data/raw_product_urls.json` file to mock the ingestion trigger.
* **We skipped deploying CI/CD Pipelines (GitHub Actions):** While we wrote the DeepEval `pytest` script, we scoped out actually configuring the cloud CI/CD YAML files. We run the tests locally to prove the *concept* of the quality gate without wasting time on dev-ops pipelines.
* **We skipped putting volatile user data in the Graph:** We actively decided *not* to store live user chat states or transient Oura ring data in Neo4j. Highly transactional data ruins graph caching. We keep the Graph for "immutable medical facts" and keep the user state entirely within the LangGraph session memory.