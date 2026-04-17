# NeMo Guardrails Integration Research

## Overview
NeMo Guardrails helps add programmable guardrails to LLM-based applications. For the `healf` engine, it acts as a semantic firewall to ensure the LLM strictly adheres to medical intent and avoids diagnosing conditions, offering prescriptive medical guidance, or outputting off-topic content.

## Configuration Structure
NeMo relies on YAML-based configurations (`config.yml`) and specialized format files (`.co` for Colang files) defining the specific rules.

- **Colang:** A specialized dialogue modeling language to define flows.
  - Define canonical user messages (e.g., `define user ask medical advice`).
  - Define bot responses (e.g., `define bot decline medical advice`).
  - Define rails mapping user intents to specific bot actions.

## Key Insights for `healf`
- The Guardrails runtime wraps standard LangChain models.
- Since we are using Instructor for `Pydantic` validation, we must strategically place our Guardrails. They are ideally invoked on user input/intent *before* the prompt is structured, to stop generation immediately on malicious input.
- **Initialization Cost:** Precomputing semantic indices can add slight latency on startup, so the Guardrails instance should be a singleton inside our FastAPI application.

## Example Colang (medical_safety.co)
```colang
define user ask generic medical advice
  "I have a headache, what should I take?"
  "Can this supplement cure diabetes?"

define bot decline medical advice
  "I am an AI health intelligence engine providing product insights, not a doctor. I cannot provide medical advice or diagnose conditions. Please consult a healthcare professional."

define flow
  user ask generic medical advice
  bot decline medical advice
```