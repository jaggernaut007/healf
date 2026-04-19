from __future__ import annotations

import logging
import os
from typing import Callable

logger = logging.getLogger(__name__)

_OBSERVABILITY_ACTIVE = False


def build_default_observability_activator() -> Callable[[], None]:
    def _activate() -> None:
        global _OBSERVABILITY_ACTIVE
        if _OBSERVABILITY_ACTIVE:
            return
        
        import phoenix as px
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor

        # If a collector endpoint is already set, we assume an external server is running.
        # Otherwise, we launch a local one.
        if not os.getenv("PHOENIX_COLLECTOR_ENDPOINT"):
            try:
                px.launch_app()
            except Exception as e:
                logger.warning(f"Failed to launch local Phoenix server: {e}")

        # Instrument everything we have
        LangChainInstrumentor().instrument()
        OpenAIInstrumentor().instrument()
        
        # Try to instrument LangGraph if available (requires openinference-instrumentation-langgraph)
        try:
            from openinference.instrumentation.langgraph import LangGraphInstrumentor
            LangGraphInstrumentor().instrument()
        except ImportError:
            logger.debug("LangGraph instrumentation not available (package missing).")
        except Exception as e:
            logger.warning(f"Failed to instrument LangGraph: {e}")

        _OBSERVABILITY_ACTIVE = True

    return _activate
