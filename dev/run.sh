#!/usr/bin/env bash
# Serve the app on http://localhost:8765, run one Python test/script, stop the server.
# usage: dev/run.sh dev/check.py      (or any dev/tests/*.py)
cd "$(dirname "$0")/.." || exit 1
mkdir -p /tmp/fk-shots
python3 -m http.server 8765 >/tmp/fk-srv.log 2>&1 & S=$!; sleep 0.8
python3 "$@"; R=$?; kill $S 2>/dev/null; exit $R
