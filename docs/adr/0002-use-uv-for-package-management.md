# 2. Use uv for Python Package Management

## Status
Accepted

## Context
Standard Python packaging tools (`pip`, `venv`, `virtualenv`) often lead to slow dependency resolution, bloated virtual environments, and inconsistent states across developer machines. Initial attempts to pin dependencies for `langchain`, `arize-phoenix`, and `nemoguardrails` using standard `pip` resulted in complex dependency conflicts that delayed the setup phase. 

## Decision
We will exclusively use `uv` for all Python package management, virtual environment creation, and dependency resolution. All commands across the project (including `scripts/init.sh` and agentic workflows) must use `uv pip install` and `uv venv`.

## Consequences
- **Positive:** Drastically faster package installation and dependency resolution.
- **Positive:** Single tool for both virtual environment management and package installation.
- **Positive:** Better cross-platform consistency for reproducible builds.
- **Negative:** Requires team members and CI pipelines to install a new tool before bootstrapping the project.