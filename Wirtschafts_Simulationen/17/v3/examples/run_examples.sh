#!/usr/bin/env sh
set -eu

# Aus dem Projektwurzelordner starten:
#   sh examples/run_examples.sh

pypy3 run_simulation.py --periods 80 --households 250 --firms 70 --banks 4 --scenario balanced --out output_balanced --progress
pypy3 run_simulation.py --periods 80 --households 250 --firms 70 --banks 4 --scenario code_bubble --out output_code_bubble --progress
pypy3 tools/compare_scenarios.py --periods 60 --households 200 --firms 60 --banks 3 --out output_scenario_comparison
