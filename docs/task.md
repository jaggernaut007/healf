# Healf — Founding AI Engineer Take-Home Task

**[🎥 Completed Task Video Walkthrough](https://youtu.be/CFmVON-Xw0k)**

**Role:** Founding AI Engineer (Sr. Staff)

> [!IMPORTANT]
> **Time expectation:** 8–12 hours across a week
> 
> **Submission deadline:** 7 days from receipt
> 
> **Questions?** Email [manilyn@healf.com](mailto:manilyn@healf.com)

---

# About This Task

This task is intentionally open-ended. There is no single correct architecture. We are evaluating how you think.

---

# Context — What Healf Does

Healf is the UK’s leading health and nutrition platform. We sell 4,000+ curated wellness products across four pillars: Eat, Move, Mind, and Sleep. We also run Healf Zone, a subscription health testing service where members receive blood panel results and track their health over time.

Our customers are trying to make real decisions about their health — which supplements to take, what their blood results mean, whether a product is right for their specific goals. These are not trivial questions. A customer with low ferritin, disrupted sleep, and a goal of improving energy needs a different answer than a customer with the same goal but no nutritional deficiencies. Getting this wrong is not just a bad experience — it erodes trust in a category where trust is everything.

We have a growing body of knowledge that should be informing these conversations: product information, ingredient science, research literature, and content from our health editorial team. Right now, this knowledge is fragmented — sitting in product descriptions, PDFs, and articles — and none of it is connected in a way that allows an AI system to reason across it coherently.

You can explore the live product at [healf.com](http://healf.com).

---

# The Problem

Customers come to Healf with health questions that deserve grounded, personalised answers — not generic supplement advice, and not hallucinated claims dressed up as health guidance.

Building a system that can do this well requires three things working together. First, a knowledge foundation: health research, ingredient science, and product information structured in a way that supports reasoning, not just retrieval. Second, a product understanding layer: product descriptions that go beyond marketing copy to capture the clinical context, ingredient interactions, and goal-specific relevance of each product. Third, a conversational layer: a chatbot that draws on both, while also knowing who it is talking to — their goals, their health data, their past purchases, and what they have been looking at in this session.

These three components are not independent. The chatbot is only as good as the knowledge it can retrieve. The knowledge is only as useful as the structure that connects it. The product context is only as valuable as the enrichment that makes it machine-readable for reasoning.

The system you build should demonstrate all three — and demonstrate that they work together in a way that is reliable, grounded, and measurable.

---

# The Task

This task has three interconnected components. The architecture connecting them is as important as any individual component.

## Component 1 — Product Enrichment Agent

Build an agent that takes raw product information — descriptions, ingredient lists, and images — and enriches it into a structured, reasoning-ready representation.

The enrichment should go beyond paraphrasing the existing description. Think about what a knowledgeable health advisor would want to know about a product that is not in the marketing copy: what the active ingredients actually do at a mechanistic level, which health goals and biomarker patterns this product is relevant to, what the evidence quality looks like, what interactions or contraindications exist, and how this product relates to others in the catalogue.

You decide what the enrichment schema looks like and what the agent pipeline that produces it looks like. The output of this component feeds directly into the chatbot — so design it with that consumer in mind.

## Component 2 — Knowledge Graph Construction

Build a pipeline that ingests health research documents — use publicly available papers, systematic reviews, or any suitable source — and constructs a knowledge graph that connects health goals, symptoms, biomarkers, ingredients, and mechanisms of action.

The purpose of this graph is to enable the chatbot to reason across knowledge, not just retrieve it. A customer asking about brain fog in the afternoon should be connectable to magnesium, B vitamins, and iron through the graph — not because those words appeared in a search result, but because the graph encodes the relationships.

You decide the graph schema, the extraction pipeline, and how the graph is queried at inference time. The graph does not need to be large — it needs to be coherently designed and actually used by the chatbot.

## Component 3 — Health Chatbot

Build the conversational layer that brings the above together. The chatbot should be able to hold a grounded, personalised health conversation with a Healf customer — drawing on:

- The knowledge graph for health and ingredient reasoning
- Enriched product information for specific product recommendations
- Customer context: their stated preferences and goals, their Healf Zone health data if available, their past orders, and what they have been browsing in the current session

The chatbot must not cross from wellness guidance into medical diagnosis or treatment. It must ground its responses in the knowledge it has access to — not in the model’s parametric memory. When it does not know something, it should say so.

You decide the orchestration architecture: how context is assembled, what gets retrieved and when, how multi-turn conversation is handled, and how the system degrades gracefully when retrieval returns nothing useful.

---

# Architecture Document (Required)

Include an `ARCHITECTURE.md` in your repo. This is the primary artefact we evaluate. Address:

1. **System design** — how do the three components connect, what are their contracts with each other, and what is the failure mode if any one is unavailable or returns low-quality output?
2. **Knowledge graph schema** — what entities and relationships does the graph encode, why, and how does the chatbot query it at inference time?
3. **Enrichment design** — what does the enrichment schema look like, what does the agent pipeline do, and what would be lost if enrichment were removed?
4. **Context assembly** — how do you construct the context window for a given customer turn? What is your retrieval strategy, what do you include, and what do you drop when the window is constrained?
5. **Evaluation framework** — what are your judges, what do they measure, what are their failure modes, and which one would you trust least in production?
6. **Safety model** — how does the chatbot stay within wellness guidance? What does your guardrail catch and what does it miss?
7. **What you did not build** — honest scoping, what you would do differently with a full sprint, what you would not change with unlimited time
8. **Founding engineer decisions** — if you were starting day one at Healf, what are the two or three AI infrastructure decisions you would make in the first two weeks that would be hardest to reverse?

Target: 700–1200 words. Prose or structured bullets, your call.

---

# Technical Constraints

- **LLM provider:** Any — use what you know best; abstract it behind an interface so it is swap-able
- **Knowledge graph:** Any approach — a property graph, a triple store, or a structured in-memory representation. It must be genuinely queryable for reasoning, not just retrievable by similarity
- **Research documents:** Use publicly available sources — PubMed abstracts, systematic reviews, NHS guidance, or similar. A small, well-chosen corpus is better than a large, loosely structured one
- **Mock customer data:** Use realistic but invented customer profiles, order histories, and browsing sessions — keep it minimal but sufficient to demonstrate personalisation
- **No production infrastructure required** — local setup is fine; your design must make clear where real infrastructure would sit
- **AI coding tools:** Use freely. The design decisions, evaluation framework, and written reasoning must be yours and must hold up under live questioning

---

# Submission

**What to send:**

- GitHub repo — public, or private with [sam.p@healf.com](mailto:sam.p@healf.com) added
- Loom video, 8 min max — demo the working system end to end, walk through one orchestration decision you are proud of and one you are uncertain about
- README — setup instructions that work on a clean machine in under 10 minutes; required API keys and environment variables clearly listed

**Evaluation process:** Three people review independently: one AI infrastructure engineer, one product-minded engineer, and a product manager. We then run a 60-minute technical debrief. Expect to be asked to extend the system live — add a new knowledge source, change the safety policy, or handle a retrieval failure you did not anticipate.

> [!TIP]
> **On the Loom:** Do not over-polish. We want a peer-level conversation, not a demo. The debrief is specifically designed to separate engineers who understand what they built from those who assembled a pipeline. Come ready to discuss your eval design, your context assembly decisions, and the one thing you would change if you had another week.

