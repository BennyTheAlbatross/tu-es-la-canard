#!/usr/bin/env bash
set -euo pipefail
CANARD_REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CANARD_PYTHON="${CANARD_PYTHON:-$CANARD_REPO/.venv/bin/python}"
if [[ ! -x "$CANARD_PYTHON" ]]; then
  echo 'Create .venv and install requirements-web.txt first, or set CANARD_PYTHON.' >&2
  exit 1
fi
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
exec "$CANARD_PYTHON" "$CANARD_REPO/scripts/build_web.py"
