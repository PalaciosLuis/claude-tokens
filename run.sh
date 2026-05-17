#!/usr/bin/env bash
set -e

# Build candidate list: pyenv versions first, then system
CANDIDATES=()

# Add pyenv versions if pyenv is installed
if [ -d "$HOME/.pyenv/versions" ]; then
  for v in "$HOME/.pyenv/versions"/*/bin/python3; do
    [ -x "$v" ] && CANDIDATES+=("$v")
  done
fi

# Add system Python fallbacks
CANDIDATES+=(python3 python)

# Find first candidate that has pip
PYTHON=""
for candidate in "${CANDIDATES[@]}"; do
  if command -v "$candidate" &>/dev/null || [ -x "$candidate" ]; then
    if "$candidate" -m pip --version &>/dev/null 2>&1; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "No Python 3 with pip found."
  echo "Install Python from https://python.org"
  read -r -p "Press Enter to exit..."
  exit 1
fi

echo "Using: $($PYTHON --version)"

# Install rich if missing
"$PYTHON" -c "import rich" 2>/dev/null || "$PYTHON" -m pip install rich --quiet

"$PYTHON" "$(dirname "$(realpath "$0")")/claude-tokens.py"
