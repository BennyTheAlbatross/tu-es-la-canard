#!/usr/bin/env bash
set -euo pipefail
CANARD_REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CANARD_HOST="${1:-canard@canard-web}"
if [[ ! "$CANARD_HOST" =~ ^[A-Za-z0-9._@:-]+$ ]]; then
  echo 'Invalid SSH destination.' >&2; exit 1
fi
CANARD_BUILD="$CANARD_REPO/build/web"
if [[ ! -f "$CANARD_BUILD/index.html" || ! -f "$CANARD_BUILD/game/game.tar.gz" || ! -f "$CANARD_BUILD/runtime/0.9.3/cpython312/main.wasm" ]]; then
  echo 'Build the complete static site and verify it in browsers before deploying.' >&2; exit 1
fi
CANARD_STAMP="$(date -u +%Y%m%dT%H%M%S)-$$"
CANARD_RELEASE="/srv/canard/releases/$CANARD_STAMP"
ssh "$CANARD_HOST" "mkdir -p '$CANARD_RELEASE'"
tar -C "$CANARD_BUILD" -cf - . | ssh "$CANARD_HOST" "tar --no-same-owner -C '$CANARD_RELEASE' -xf -"
ssh "$CANARD_HOST" bash -s -- "$CANARD_RELEASE" <<'REMOTE'
set -euo pipefail
release="$1"
test -f "$release/index.html"
test -f "$release/game/game.tar.gz"
test -f "$release/runtime/0.9.3/cpython312/main.wasm"
if [[ -e /srv/canard/build && ! -L /srv/canard/build ]]; then
  echo '/srv/canard/build must be absent or a release symlink.' >&2
  exit 1
fi
find "$release" -type d -exec chmod 755 {} +
find "$release" -type f -exec chmod 644 {} +
previous="$(readlink /srv/canard/build || true)"
ln -s "$release" /srv/canard/build.next
mv -Tf /srv/canard/build.next /srv/canard/build
if ! curl -fsS http://127.0.0.1:8080/ >/dev/null; then
  if [[ -n "$previous" ]]; then
    ln -s "$previous" /srv/canard/build.rollback
    mv -Tf /srv/canard/build.rollback /srv/canard/build
  fi
  echo 'HTTP check failed; previous release restored where available.' >&2
  exit 1
fi
echo "Deployed $release"
REMOTE
