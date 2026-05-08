# -*- coding: utf-8 -*-
"""Minimaler Smoke-Test ohne pytest.

Start:
    pypy3 tests/test_smoke.py
"""
from __future__ import print_function

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from qsim.simulation import EconomySimulation


def main():
    sim = EconomySimulation(seed=7, households=40, firms=16, banks=2, scenario="balanced")
    hist = sim.run(6)
    assert len(hist) == 6
    last = hist[-1]
    assert last["bqp"] >= 0.0
    assert 0.0 <= last["unemployment_rate"] <= 1.0
    assert last["total_positive_money_value"] > 0.0
    assert len(sim.firms) > 0
    print("Smoke-Test bestanden. Letztes BQP: %.2f ZW" % last["bqp"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
