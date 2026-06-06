#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-pypy3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python3
fi
"$PYTHON_BIN" vector_currency_sim.py \
  --steps 60 \
  --countries 3 \
  --households 600 \
  --firms 120 \
  --banks 9 \
  --seed 42 \
  --out demo_metrics.csv \
  --summary demo_summary.json \
  --events demo_events.csv \
  --verbose
