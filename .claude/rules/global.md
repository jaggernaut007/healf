---
description: Universal coding standards that apply to all code
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---

# Global Code Standards

## Positive Instructions Only
- Write concise, professional comments (not verbose explanations)
- Use only real-world data from the database (never mock data)
- Apply all fixes to existing files (create new files only when explicitly required)
- Write descriptive git commit messages that serve as session history

## File Organization
- Use direct import paths (never barrel files/index re-exports)
- Colocate tests with implementation (auth.ts → auth.test.ts)
- Keep functions under 50 lines; split larger ones into helpers

## Error Handling
- Raise specific exceptions with clear messages
- Include error context (what failed, expected vs actual)
- Never swallow exceptions without logging

## Verification Before Completion
- Run tests via tool call before marking complete
- Read test output to verify pass
- Update PROGRESS.md with what was done
