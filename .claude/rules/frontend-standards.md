---
description: Frontend code standards for React/Next.js
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.ts"
  - "**/*.js"
---

# Frontend Standards

## React Components
- Use functional components with hooks (not class components)
- Keep components under 200 lines; extract sub-components
- Use meaningful prop names and destructure in function signature

## TypeScript
- Strict mode enabled (no `any` types)
- Define interfaces for all component props
- Use `type` for unions, `interface` for objects

## Styling
- Use Tailwind CSS utility classes (not custom CSS)
- Follow mobile-first responsive design
- Keep inline styles to minimum; prefer Tailwind

## State Management
- Use React hooks for local state (useState, useReducer)
- Lift state only when needed by multiple components
- Document state flow for complex interactions

## Testing
- Write tests for user interactions (not implementation details)
- Use React Testing Library patterns
- Test accessibility (ARIA labels, keyboard navigation)
