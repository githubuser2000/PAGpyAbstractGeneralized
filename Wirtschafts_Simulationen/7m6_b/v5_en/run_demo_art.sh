#!/usr/bin/env bash
set -euo pipefail
python3 vector_currency_sim.py --steps 12 --countries 3 --households 300 --firms 80 --banks 6 --seed 42 --out art_metrics.csv --summary art_summary.json --events art_events.csv --art --art-every 4
