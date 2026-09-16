#!/usr/bin/env bash
# For a fresh Replit import. Keep existing working Replit projects separate.
set -euo pipefail
cd "$(dirname "$0")/.."

note2flash_python=""
for candidate in python3.12 python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(not ((3, 11) <= sys.version_info[:2] < (3, 13)))'; then
        note2flash_python="$candidate"
        break
    fi
done
if [[ -z "$note2flash_python" ]]; then
    echo 'Note2Flash needs Python 3.11 or 3.12. Enable a supported Python runtime in this new Replit project.' >&2
    exit 1
fi
"$note2flash_python" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export HOST=0.0.0.0
exec .venv/bin/python app.py
