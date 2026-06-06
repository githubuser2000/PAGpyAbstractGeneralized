#!/usr/bin/env bash
set -euo pipefail
python3 vector_currency_sim.py \
  --steps 8 \
  --countries 2 \
  --households 100 \
  --firms 30 \
  --banks 4 \
  --seed 99 \
  --out demo_art_metrics.csv \
  --summary demo_art_summary.json \
  --events demo_art_events.csv \
  --art \
  --art-every 4 \
  --art-width 120
