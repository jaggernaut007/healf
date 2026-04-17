# Research: Arize Phoenix Observability Platform

**Library version:** arize-phoenix 14.8.0
**Status:** Current (with licensing caveat)
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official Phoenix docs | https://docs.arize.com/phoenix | 2026-04-17 |
| GitHub Repository | https://github.com/Arize-ai/phoenix | 2026-04-17 |
| PyPI Package | https://pypi.org/project/arize-phoenix/ | 2026-04-17 |

## The Correct Approach

Use Arize Phoenix for trace-level observability and debugging of LLM/agent workflows. Pair with OpenInference instrumentation.

```python
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor

# Start Phoenix at app initialization
px.launch_app()  # Boots local trace server on localhost:6006

# Instrument LangGraph/LangChain for automatic span capture
LangChainInstrumentor().instrument()

# Traces are automatically collected
# Access traces at http://localhost:6006
```

## Files This Affects

- `src/chatbot.py` — Phoenix initialization at app startup
- `src/state.py` — (reference only; LangGraph spans captured automatically)
- `scripts/init.sh` — (optional; can verify Phoenix availability)

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| No observability | Blind debugging; difficult to diagnose retrieval/latency issues |
| Splunk/Datadog | Overkill for MVP; expensive and complex to configure |
| Langsmith only | Limited to LangChain integration; Phoenix offers broader instrumentation |

## Security Assessment

- [ ] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by Arize team
- [ ] License compatibility: Elastic-2.0 (non-OSI license); requires policy review for commercial use
- [x] Dependency tree risk: Minimal dependencies; stable upstream
- [x] Download stats / popularity: 500K+ weekly downloads in ecosystem
- [x] Single-maintainer risk: Arize team; distributed ownership

## Known Gotchas / Edge Cases

- **License**: Elastic-2.0 is not OSI-compliant; review your distribution/commercial policy before production deployment.
- **Local Storage**: Default tracing writes to local SQLite; no remote backend needed for development.
- **Startup Cost**: Initial Phoenix startup can take 5-10s; lazy-load in production if acceptable latency.
- **Memory**: In-memory trace buffer can grow; configure trace size limits or use persistent backend.
- **Port Conflict**: Phoenix UI runs on localhost:6006 by default; adjust if port is taken.

## Integration Notes

- Initialize Phoenix at the very top of `src/chatbot.py` before any LangGraph/LLM calls.
- Use with OpenInference instrumentation for comprehensive span capture.
- Access UI at `http://localhost:6006` during development for debugging.
- For production: either disable Phoenix or configure persistent backend (e.g., Elasticsearch).
- Pair with structured logging (e.g., JSON logs) for correlated tracing.
