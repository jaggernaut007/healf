#!/usr/bin/env bash
set -e

echo "=== Healf AI Initialization ==="
if [ ! -d ".venv" ]; then uv venv; fi
source .venv/bin/activate
uv pip install -r requirements.txt
export PYTHONPATH=.
pytest tests/
echo "=== Environment verified successfully ==="
