---
description: Python-specific code standards
paths:
  - "**/*.py"
---

# Python Standards

## Type Hints
- Use type hints for all function signatures
- Import from `typing` for complex types (List, Dict, Optional, Union)
- Use Pydantic models for all request/response schemas

## API Standards
- Raise HTTPException with correct status codes
- All external API calls go through designated service layer
- Validate inputs with Pydantic before processing

## Testing
- Use pytest for all tests
- Prefer real integrations in controlled test environments; use minimal test doubles only for unstable external systems
- Aim for 80%+ coverage on business logic

## Code Quality
- Follow PEP 8 (enforced by Ruff)
- Max line length: 100 characters
- Use f-strings for string formatting (not %)
