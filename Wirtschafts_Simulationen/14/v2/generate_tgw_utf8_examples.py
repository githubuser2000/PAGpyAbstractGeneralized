#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate curated TGW UTF-8 example reports."""
from __future__ import print_function
import tgw_pypy3_simulation as core
import tgw_pypy3_utf8_art_simulation as rich

CASES = [
    ("stable_repair", core.Config(
        scenario="baseline", seed=111, ticks=80, galaxies=2, planets_per_galaxy=2, states_per_planet=2,
        households=250, firms=100, initial_problems_per_state=2, max_projects_started_per_tick=50,
        max_active_projects=200, fraud_pressure=0.12, externality_rate=0.10, war_probability=0.0, quiet=True
    ), "/mnt/data/tgw_utf8_stable_repair_report.txt"),
    ("conflict_spiral", core.Config(
        scenario="conflict", seed=222, ticks=100, galaxies=3, planets_per_galaxy=2, states_per_planet=2,
        households=180, firms=45, initial_problems_per_state=3, max_projects_started_per_tick=20,
        max_active_projects=80, fraud_pressure=0.30, externality_rate=0.60, war_probability=0.02, quiet=True
    ), "/mnt/data/tgw_utf8_conflict_spiral_report.txt"),
    ("fraud_stress", core.Config(
        scenario="fraud", seed=333, ticks=90, galaxies=3, planets_per_galaxy=2, states_per_planet=2,
        households=180, firms=55, initial_problems_per_state=3, max_projects_started_per_tick=24,
        max_active_projects=100, fraud_pressure=3.0, externality_rate=1.0, war_probability=0.0, quiet=True
    ), "/mnt/data/tgw_utf8_fraud_stress_report.txt"),
    ("scarcity_backlog", core.Config(
        scenario="scarcity", seed=444, ticks=80, galaxies=3, planets_per_galaxy=2, states_per_planet=2,
        households=120, firms=25, initial_problems_per_state=9, max_projects_started_per_tick=8,
        max_active_projects=40, fraud_pressure=0.30, externality_rate=1.40, war_probability=0.0, quiet=True
    ), "/mnt/data/tgw_utf8_scarcity_backlog_report.txt"),
    ("intergalactic_latency", core.Config(
        scenario="intergalactic", seed=555, ticks=110, galaxies=5, planets_per_galaxy=2, states_per_planet=2,
        households=120, firms=15, initial_problems_per_state=5, max_projects_started_per_tick=12,
        max_active_projects=80, remote_project_probability=1.0, intergalactic_delay=40,
        fraud_pressure=0.40, externality_rate=0.50, war_probability=0.0, quiet=True
    ), "/mnt/data/tgw_utf8_intergalactic_latency_report.txt"),
]

results = []
for name, cfg, path in CASES:
    print("running", name)
    sim = rich.run_simulation(cfg, progress=False)
    report = rich.build_utf8_report(sim)
    rich.write_text(path, report)
    results.append((name, sim))

suite = rich.build_suite_report(results)
rich.write_text("/mnt/data/tgw_utf8_outcome_gallery_report.md", suite)
print("done")
