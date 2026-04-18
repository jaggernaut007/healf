---
applyTo: "**/*.{py,ts,tsx,js,jsx,md}"
---

# Spec-Driven Instructions

- Read `SPEC.md` before planning, implementation, testing, review, or release actions.
- Map requested work to a phase and acceptance criteria in `SPEC.md` before editing files.
- If work conflicts with `SPEC.md` or has no acceptance criteria, block execution until `SPEC.md` is updated.
- Require tool-verified evidence before claiming completion against `SPEC.md` criteria.
- For architecture, dependency, or API contract changes, require ADR and research updates first.
- Use `rg --files` for file discovery and `rg -n` for content search by default.
- If `rg` is unavailable, use `find . -type f` and `grep -RIn --exclude-dir=.git`, and log `rg unavailable, using grep/find fallback`.
