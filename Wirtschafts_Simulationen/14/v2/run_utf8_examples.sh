#!/usr/bin/env bash
set -euo pipefail

# Ein normaler UTF-8-Art-Bericht
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario baseline \
  --ticks 120 \
  --seed 42 \
  --report-out tgw_utf8_report.txt

# Vergleich mehrerer Standard-Szenarien
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario-suite \
  --ticks 100 \
  --seed 42 \
  --suite-out tgw_utf8_suite_report.md \
  --quiet

# Kuratierte Beispiele neu erzeugen
python3 generate_tgw_utf8_examples.py
