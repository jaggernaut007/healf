#!/usr/bin/env bash
set -e

echo "=== Healf AI Initialization ==="
if [ ! -d ".venv" ]; then uv venv; fi
source .venv/bin/activate
uv pip install -r requirements.txt
export PYTHONPATH=.
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv run pytest tests/ -q
echo "=== Environment verified successfully ==="
