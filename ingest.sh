#!/bin/sh
ROOT="$(cd "$(dirname "$0")" && pwd)"; export BLACKOUT_ROOT="$ROOT"
exec "$(command -v python3 || command -v python)" "$ROOT/app/ingest.py" "$@"
