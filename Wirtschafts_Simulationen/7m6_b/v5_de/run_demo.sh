#!/usr/bin/env bash
set -euo pipefail
python3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
