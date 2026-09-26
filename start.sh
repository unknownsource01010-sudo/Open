#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 -m venv .venv 2>/dev/null || true
. .venv/bin/activate
pip -q install -r requirements.txt
exec python server.py
