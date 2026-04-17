# 5. Use NeMo Guardrails as a Pre-Execution Safety Gateway

## Status
Accepted

## Context
This system handles wellness and medical-adjacent user prompts. Safety policy must be enforced before any model orchestration to prevent diagnosis-like responses, unsafe medical guidance, or policy bypass attempts.

Existing research notes and package validation confirm `nemoguardrails` supports intent-based gating via policy definitions and can be integrated as a pre-LangGraph control point.

## Decision
Adopt `NeMo Guardrails` as a pre-execution semantic safety layer.

- Evaluate user prompts against guardrail policy first.
- If a protected intent triggers, return a safe refusal/redirect response.
- Only invoke graph orchestration when guardrail checks pass.

## Consequences
- Positive: Fail-closed behavior for high-risk medical intents.
- Positive: Clear separation between safety policy and orchestration logic.
- Negative: Additional startup/runtime complexity and policy maintenance overhead.
- Negative: Requires ongoing tuning to reduce false positives/false negatives.
