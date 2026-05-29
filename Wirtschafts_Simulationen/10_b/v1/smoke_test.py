#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal smoke test for planetary_effect_economy.py."""

from planetary_effect_economy import run_simulation


def main():
    regions, boundary, planner, timeline, last_truth = run_simulation(
        seed=7,
        steps=3,
        population=1_000_000,
        regions_count=2,
        communes_per_region=2,
        scenario="planetary_commons",
    )
    assert len(timeline) == 4
    assert sum(len(r.communes) for r in regions) == 4
    assert timeline[-1].population > 0
    assert last_truth
    assert all(0.0 <= p <= 2.2 for p in boundary.pressures.values())
    print("smoke_test: ok")


if __name__ == "__main__":
    main()
