from __future__ import annotations

import logging
import os
from typing import Any, Callable

from src.models.orchestration import EvaluationGate, RetrievalChunk

logger = logging.getLogger(__name__)


def build_default_evaluator(model: str = "gpt-5.4-mini") -> Callable[[str, str, list[RetrievalChunk], float], EvaluationGate]:
    def _evaluate(
        query: str,
        draft: str,
        chunks: list[RetrievalChunk],
        threshold: float,
    ) -> EvaluationGate:
        logger.info(f"Evaluating draft: {draft[:100]}...")
        logger.info(f"Chunks available: {len(chunks)}")
        
        # 1. Try DeepEval if enabled (via environment or config)
        score = None
        if os.getenv("HEALF_USE_DEEPEVAL_GATE") == "true":
            score = _try_deepeval_score(query, draft, chunks, model=model)
            
        # 2. Fallback to heuristic score
        if score is None:
            score = _heuristic_score(draft, chunks)
            
        logger.info(f"Final evaluation score: {score}")
        passed = score >= threshold
        reason = None
        if not passed:
            reason = f"Quality gate score {score:.2f} is below threshold {threshold:.2f}."
        return EvaluationGate(passed=passed, score=score, threshold=threshold, reason=reason)

    return _evaluate


def _try_deepeval_score(query: str, draft: str, chunks: list[RetrievalChunk], model: str = "gpt-5.4-mini") -> float | None:
    """
    Attempt to use DeepEval for a more robust LLM-as-a-Judge score.
    Returns None if deepeval is not installed or if API calls fail.
    """
    try:
        from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
        from deepeval.test_case import LLMTestCase
        
        test_case = LLMTestCase(
            input=query,
            actual_output=draft,
            retrieval_context=[c.content for c in chunks]
        )
        
        # We use a lower threshold here because this is a real-time gate
        # and we want to be conservative but not block everything.
        f_metric = FaithfulnessMetric(threshold=0.5, model=model)
        r_metric = AnswerRelevancyMetric(threshold=0.5, model=model)
        
        f_metric.measure(test_case)
        r_metric.measure(test_case)
        
        # Average the two metrics
        return (f_metric.score + r_metric.score) / 2.0
    except (ImportError, Exception) as e:
        logger.warning(f"DeepEval scoring skipped or failed: {e}")
        return None


def _heuristic_score(draft: str, chunks: list[RetrievalChunk]) -> float:
    if not chunks:
        return 0.0
    score = min(1.0, 0.4 + (0.2 * min(len(chunks), 3)))
    if "documented evidence" in draft.lower():
        score = min(1.0, score + 0.1)
    return score
