#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
	echo "python3 is required" >&2
	exit 1
fi
if ! command -v pip3 >/dev/null 2>&1; then
	echo "pip3 is required" >&2
	exit 1
fi

# Install deps (user site)
pip3 install --user -r requirements.txt

# Run
exec python3 -m bot