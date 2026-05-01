#!/usr/bin/env bash
set -euo pipefail

# TGW / Topologische Gruppenwirtschaft - Beispielbefehle

pypy3 tgw_pypy3_simulation.py --ticks 80 --seed 23 --report-every 20 \
  --csv-out tgw_sample_timeseries.csv \
  --json-out tgw_sample_final.json

pypy3 tgw_pypy3_simulation.py --scenario conflict --ticks 120 --seed 8 \
  --war-probability 0.03 --report-every 20 \
  > tgw_conflict_report.txt

pypy3 tgw_pypy3_simulation.py --scenario intergalactic --galaxies 5 --ticks 180 --seed 11 \
  --remote-project-probability 0.25 --intergalactic-delay 25 \
  --json-out tgw_intergalactic_final.json
