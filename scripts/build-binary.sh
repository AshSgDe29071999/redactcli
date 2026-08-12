#!/usr/bin/env bash
# Build a one-file PyInstaller binary for the current platform.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "${VIRTUAL_ENV:-}" ] && [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
PY="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"
PY="${PY:-$ROOT/.venv/bin/python}"
"$PY" -m pip install --quiet --upgrade pip pyinstaller
"$PY" -m PyInstaller \
  --noconfirm \
  --onefile \
  --name redactcli \
  --paths src \
  --hidden-import redactcli \
  --hidden-import redactcli.cli \
  --hidden-import redactcli.engine \
  --hidden-import redactcli.patterns \
  src/redactcli/__main__.py

BIN="dist/redactcli"
if [ -f dist/redactcli.exe ]; then
  BIN="dist/redactcli.exe"
fi
echo "built $BIN"
"$BIN" --version
echo "token=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab" | "$BIN" | grep -q REDACTED
echo "smoke ok"
