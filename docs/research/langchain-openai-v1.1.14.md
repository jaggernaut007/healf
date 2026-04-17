# Research: LangChain OpenAI Provider Adapter

**Library version:** langchain-openai 1.1.14
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official LangChain docs | https://python.langchain.com/docs/integrations/llms/openai/ | 2026-04-17 |
| PyPI Package | https://pypi.org/project/langchain-openai/ | 2026-04-17 |
| GitHub Repository | https://github.com/langchain-ai/langchain | 2026-04-17 |

## The Correct Approach

Use `langchain-openai` as a narrowly-scoped provider adapter for model instantiation. Avoid coupling to broader LangChain abstractions unless strictly needed.

```python
from langchain_openai import ChatOpenAI

# Use with instructor for structured outputs
chat_model = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key="sk-...",  # or use OPENAI_API_KEY env var
)

# Do not rely on LangChain chains; use direct model calls
# Pass model to instructor for strict schema enforcement
import instructor
from pydantic import BaseModel

class EnrichedProduct(BaseModel):
    sku: str
    canonical_name: str

client = instructor.from_openai(ChatOpenAI)
# Extract with enforced schema
```

## Files This Affects

- `src/enrichment.py` — LLM extraction for product schema structuring
- `src/chatbot.py` — LLM calls within LangGraph nodes for chat responses
- `src/state.py` — (reference only, model creation happens at runtime)

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Broader LangChain chains | Tight coupling to chain patterns; brittle for multi-step agentic flows |
| Direct OpenAI SDK | Loses LangGraph/LangChain integration points and callback hooks |
| Multiple LLM providers | Scope creep; stick to single provider (OpenAI) for now |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by LangChain team
- [x] License compatibility: MIT, compatible with project
- [x] Dependency tree risk: Depends on openai SDK (actively maintained); transitive depth moderate
- [x] Download stats / popularity: 10M+ weekly downloads, widely used
- [ ] Single-maintainer risk assessment: Part of larger LangChain org; distributed team

## Known Gotchas / Edge Cases

- **API Key Management**: Ensure OPENAI_API_KEY is set or passed explicitly; do not hardcode.
- **Rate Limiting**: OpenAI enforces per-minute token limits; consider retry logic with exponential backoff.
- **Model Availability**: Verify model name (e.g., "gpt-4") is available in your OpenAI account tier.
- **Structured Output Breaking Changes**: `langchain-openai` 1.x doesn't natively enforce JSON schema; use `instructor` as the validation layer.

## Integration Notes

- Keep `langchain-openai` usage isolated to model instantiation.
- Pass the resulting `ChatOpenAI` instance to `instructor` for structured outputs.
- Do not use LangChain `LLMChain` or similar abstractions; orchestrate via LangGraph instead.
- Instructor + Pydantic provide the contract enforcement that LangChain chains would normally handle.
