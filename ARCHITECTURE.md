# Architecture and Decisions Log

1. **System design**

how do the three components connect, what are their contracts with each other, and what is the failure mode if any one is unavailable or returns low-quality output?

The enrichment and graph components function in a synchronized pipeline. The enrichment engine consumes raw product URLs (via Firecrawl) and research papers (via PubMed and NIH DSLD) to extract structured USPs, ingredients, and clinical safety data. This grounded data is then persisted into a Neo4j Knowledge Graph, where robust relationships link studies, products, ingredients, mechanisms, and symptoms.

Once stored, the agentic system utilizes the graph to provide grounded responses. The orchestration layer, built on LangGraph, coordinates nine functional nodes: `SafetyCheck` (intent classification & clinical diagnosis block), `PromptRewriter` (normalizes intent), `IntakeRouter` (ambiguity detection), `DomainSpecialist` (graph query plan generation), `Retriever` (hybrid Cypher execution), `PharmacovigilanceCritic` (safety validation), `PayloadGenerator` (grounded response synthesis), `DiscoveryAgent`, and `Evaluator`. When the `IntakeRouter` detects ambiguous intent, it triggers the `DiscoveryAgent` to ask a targeted clarification question before retrieval. Every inter-node contract is validated via Pydantic models, ensuring system reliability. In cases where full research grounding is unavailable, the system falls back to enriched marketing data, explicitly reflecting this uncertainty in the final response.


2. **Knowledge graph schema** 

what entities and relationships does the graph encode, why, and how does the chatbot query it at inference time?

    Products -CONTAINS-> Ingredient
    Ingredient -TRIGGERS-> Mechanism
    Mechanism -ALLEVIATES-> Symptom
    Mechanism -SUPPORTED_BY-> Study
    Ingredient -EVALUATED_IN-> Study

The graph also has the complete study and description of the product (USP, usage, and contraindications) to enable robust semantic matching. 

This mapping is crucial because these relationships enable the agent to sequentially reason through the evidence before making a recommendation. By tracing cognitive and canonical connections—from symptoms to mechanisms to ingredients—the system can infer relevant products even for complex user queries. During inference, multiple nodes query this graph: `SafetyCheck` and `DiscoveryAgent` use it for domain-specific context, the `Retriever` executes hybrid search for grounded recommendations, and the `PharmacovigilanceCritic` checks for contraindications to ensure medical robustness.


3. **Enrichment design** 

what does the enrichment schema look like, what does the agent pipeline do, and what would be lost if enrichment were removed?

The enrichment design ensures that product information is prepared for Knowledge Graph ingestion and grounded in peer-reviewed studies. By mapping product USPs, usage instructions, and contraindications to a structured schema, we ensure downstream reliability. The agent pipeline utilizes this enriched data—including ingredients, research findings, and user biomarkers—to ensure recommendations are both effective and safe. Without this enrichment, the Knowledge Graph would lack the semantic depth required for high-confidence advisory, potentially leading to safety risks or irrelevant product matches.


4. **Context assembly** 

how do you construct the context window for a given customer turn? What is your retrieval strategy, what do you include, and what do you drop when the window is constrained?

We utilize a project-defined user profile for personalization, managed through a TypedDict to ensure consistent, modeled data across the orchestration state. Multi-turn context is preserved via chat_history injected through the system prompts. 

The retrieval strategy for the Knowledge Graph employs a hybrid approach, prioritizing results based on a combined term-relevance score and vector similarity. Specifically, the Discovery Agent identifies biological mechanisms semantically nearest to the user's ambiguous query and constructs a targeted multiple-choice question for clarification. This consultative sales process is designed to systematically narrow the user's intent until a clear, actionable question is formulated for the retrieval pipeline.

5. **Evaluation framework** 

what are your judges, what do they measure, what are their failure modes, and which one would you trust least in production?

The evaluation framework combines deterministic heuristic quality gates—using keyword-based blocks to refuse, clarify, or deny unsafe requests—with an LLM-based evaluation pipeline integrated into both real-time orchestration and automated quality gates. 

We utilize DeepEval as our primary 'LLM-as-a-judge' framework to ensure grounded results, specifically measuring Faithfulness and Answer Relevancy. A curated golden dataset is used to verify response accuracy and minimize hallucinations, while multi-turn test cases ensure conversational consistency is maintained. This 'Eval-driven development' approach was central to optimizing agent performance. While a full-scale production observability suite wasn't strictly required for this POC, Arize Phoenix was implemented as a dependency and instrumentation logic exists, though it remains inactive as the current validation pipeline provides sufficient coverage. 

6. **Safety model** 

how does the chatbot stay within wellness guidance? What does your guardrail catch and what does it miss?


The system ensures responses remain within the wellness and supplement advisory domain, strictly avoiding medical diagnosis or treatment advice.

What it catches:
- The SafetyCheck node performs immediate intent classification, filtering out queries that seek medical diagnoses or involve life-threatening conditions.
- A specialized PromptRewriter agent analyzes the query to detect hidden medical intent or "jailbreak" attempts disguised as wellness questions.

- The PharmacovigilanceCritic node serves as a final safety gate, verifying that recommendations do not contradict established research and are grounded in the clinical safety data stored in the Knowledge Graph.

- The enrichment pipeline uses NIH DSLD and PubMed grounding to verify product descriptions against credible sources, ensuring no misinformation enters the Knowledge Graph.

What it misses:

- Extremely sophisticated or multi-layered adversarial queries that appear as valid product requests might bypass the initial intent filters, though the PharmacovigilanceCritic still enforces grounding to known studies.

- The system's "ground-truth" is bounded by the studies ingested during the enrichment phase. Without a real-time, open-ended research retrieval engine (e.g., live PubMed search at inference), the system may produce a "false negative" for a product that has recent supporting research not yet present in the local graph.


7. **What you did not build** — honest scoping, what you would do differently with a full sprint, what you would not change with unlimited time

- Agent to scour the APIs / product scraping engine to ensure the best possible result for the user.
- Multi-turn safety engine, trying to find the intent of the user in the entire conversation rather than in the particular message.

- I would change the way that agents work where I would add more dexterity to what each agent is capable of; create more sub-agents for specific tasks.

- Build a more robust eval pipeline and enable tracing and observability to see the tools being called, the products being retrieved, and the user feedback to ensure the best version of the software is present.

- I want to build a reinforcement learning-based prompt recommendation engine to ensure real-time user queries are addressed more appropriately, and the prompts are optimised for the task.

- Make the responses more refined (product placement,research findings delivery etc.) while also making they cli Richer

- While going to production, architecting a modification to the graph such that retrieval of large products is easier/faster.
- The enrichment process to be more dynamic.

- What I wouldn't change: the baseline enrichment, agentic and graph architecture, and the Pydantic models.
-Ensure a robust system is setup for multi api providers to be used.
- Robust Security, like PII, Ratelimiting, prompt injeciton filter, guardrailing etc.

8. **Founding engineer decisions** — if you were starting day one at Healf, what are the two or three AI infrastructure decisions you would make in the first two weeks that would be hardest to reverse?

- Enforcing Pydantic models for every node input/output from day one.
- Choosing a Knowledge Graph (Neo4j) as the primary source of truth.
- Committing to LangGraph for dexterity.
- Building the Evaluation Pipeline (LLM-as-a-judge + NeMO guardrailing technologies) into the CI/CD loop.



