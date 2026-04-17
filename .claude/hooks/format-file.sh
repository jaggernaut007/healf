#!/bin/bash
FILE_PATH=$1

if [[ -z "$FILE_PATH" ]]; then
  echo "Usage: $0 <file_path>"
  exit 1
fi

EXTENSION="${FILE_PATH##*.}"

case "$EXTENSION" in
  "py")
    if command -v black >/dev/null 2>&1; then
      black "$FILE_PATH"
    elif command -v ruff >/dev/null 2>&1; then
      ruff format "$FILE_PATH"
    fi
    ;;
  "ts"|"tsx"|"js"|"jsx"|"css"|"json"|"md")
    if command -v prettier >/dev/null 2>&1; then
      prettier --write "$FILE_PATH"
    fi
    ;;
  *)
    # Do nothing for other extensions
    ;;
esac
