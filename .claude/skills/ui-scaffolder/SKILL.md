---
name: ui-scaffolder
description: >
  Scaffold responsive UI slices using existing project patterns.
  Use when user asks to create dashboard pages, admin views, or production-ready UI components.
---

# UI Scaffolder

## Purpose
Generate maintainable UI aligned with existing component and style conventions.

## Spec Conformance Gate
- Read `SPEC.md` before scaffolding UI.
- Ensure UI/API payload assumptions match active phase acceptance criteria.
- Block scaffolding if requested behavior changes contracts not present in `SPEC.md`.

## Workflow
1. Read existing UI patterns and shared components first.
2. Propose component tree and data flow before coding.
3. Build mobile-first layouts with accessible semantics.
4. Add interaction tests for critical user journeys.
5. Document introduced components and usage.

## Guardrails
- Preserve established design system.
- Avoid introducing new UI frameworks unless explicitly requested.
- Keep components focused and composable.
