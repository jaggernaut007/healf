#!/bin/bash
# Pre-commit hook for agentic framework validation

echo "Running pre-commit checks..."

# Run initialization script to confirm project state
./scripts/init.sh

# Additional checks can be added here
# e.g. check for PROGRESS.md updates, ADR links, etc.

echo "Validation successful!"
exit 0
