#!/usr/bin/env bash
set -euo pipefail
PY=${PY:-pypy3}
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python3
fi
"$PY" planetary_effect_economy.py --steps 120 --scenario planetary_commons --out sample_output
"$PY" planetary_effect_economy.py --steps 120 --scenario ecological_crisis --out crisis_output
"$PY" planetary_effect_economy.py --steps 120 --scenario technocratic_control --out technocratic_output
