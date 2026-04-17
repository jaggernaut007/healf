# Research: DeepEval LLM Evaluation Framework

**Library version:** deepeval 3.9.7
**Status:** Current
**Date:** 2026-04-17

## Sources Consulted

| Source | URL | Date accessed |
|--------|-----|---------------|
| Official DeepEval docs | https://docs.confident-ai.com/ | 2026-04-17 |
| GitHub Repository | https://github.com/confident-ai/deepeval | 2026-04-17 |
| PyPI Package | https://pypi.org/project/deepeval/ | 2026-04-17 |

## The Correct Approach

Use DeepEval to test LLM output quality with objective metrics (faithfulness, relevance, hallucination). Integrate into pytest workflow for CI/CD gates.

```python
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevanceMetric
from deepeval.test_case import LLMTestCase

# Define test cases
test_cases = [
    LLMTestCase(
        input="What helps with sleep?",
        actual_output="Magnesium Glycinate supports sleep through GABA synthesis.",
        expected_output="Magnesium is known to support sleep quality.",
        retrieval_context=["PMID 23853635: Magnesium enhances GABA..."]
    ),
]

# Metrics
faithfulness = FaithfulnessMetric(threshold=0.8)
relevance = AnswerRelevanceMetric(threshold=0.7)

# Evaluate
for test_case in test_cases:
    faithfulness.measure(test_case)
    relevance.measure(test_case)
    
    assert faithfulness.is_successful()
    assert relevance.is_successful()
```

## Files This Affects

- `tests/test_eval.py` — DeepEval-based evaluation tests
- `tests/test_cases.json` — Test case definitions (input/output/context)
- CI/CD pipeline — (future integration point)

## What We Ruled Out (and Why)

| Approach | Why Rejected |
|----------|--------------|
| Manual human evaluation | Non-scalable; too slow for CI feedback loops |
| BLEU/ROUGE scores | Insufficient for semantic quality; designed for translation not grounding |
| Traditional unit tests | Cannot verify faithfulness or relevance of generated text |

## Security Assessment

- [x] CVE check (Snyk): No active CVEs as of 2026-04-17
- [x] Maintenance health: Last release Apr 2026, actively maintained by Confident AI
- [x] License compatibility: Apache-2.0, compatible with project
- [x] Dependency tree risk: Depends on OpenAI/Cohere APIs; added network dependency
- [x] Download stats / popularity: 500K+ weekly downloads, growing adoption
- [ ] Single-maintainer risk: Confident AI team; distributed ownership

## Known Gotchas / Edge Cases

- **Model Dependency**: DeepEval metrics use LLMs (OpenAI, Cohere) for evaluation; requires valid API keys.
- **Cost**: Each metric evaluation incurs API calls; budget accordingly for CI/CD.
- **Non-Determinism**: LLM-based evaluation can have variance; use reasonable thresholds (not 99%+).
- **Context Required**: Provide `retrieval_context` for faithfulness checks; improves accuracy.
- **Metric Selection**: Not all metrics apply to all use cases; choose based on what you want to measure.

## Integration Notes

- Use DeepEval for phase 5 evaluation gates in CI/CD simulation.
- Start with FaithfulnessMetric (does output match grounding evidence?) and AnswerRelevanceMetric (is output relevant to user query?).
- Define 5+ diverse test cases covering normal, edge, and adversarial prompts.
- Integrate with pytest for easy reporting and CI/CD integration.
- Monitor DeepEval cost; batch evaluations or sample tests if API spend becomes prohibitive.
