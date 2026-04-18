---
applyTo: "**/*.{test,spec}.{py,ts,tsx,js,jsx}"
---

# Testing Instructions

- Derive test cases from `SPEC.md` acceptance criteria for the active phase/wave.
- If acceptance criteria are missing or contradictory, block test authoring until `SPEC.md` is updated.
- Write failing tests first for behavior changes.
- Cover success, failure, and boundary conditions.
- Keep tests deterministic and independent.
- Verify test output from tool runs before claiming completion.
- Do not weaken assertions to make tests pass.
