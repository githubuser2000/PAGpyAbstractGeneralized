#!/usr/bin/env bash
set -euo pipefail
python3 vector_currency_sim.py \
  --steps 24 \
  --countries 3 \
  --households 300 \
  --firms 75 \
  --banks 6 \
  --seed 42 \
  --out demo_metrics.csv \
  --summary demo_summary.json \
  --events demo_events.csv \
  --verbose
