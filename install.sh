#!/usr/bin/env bash
set -e
echo "Installing FreeStream..."
if command -v uv >/dev/null 2>&1; then
    uv tool install freestream
elif command -v pipx >/dev/null 2>&1; then
    pipx install freestream
elif command -v pip3 >/dev/null 2>&1; then
    pip3 install --user freestream
elif command -v pip >/dev/null 2>&1; then
    pip install --user freestream
else
    echo "error: no pip/uv/pipx found. Install Python 3.10+ first." >&2
    exit 1
fi
echo "Done. Run: freestream"