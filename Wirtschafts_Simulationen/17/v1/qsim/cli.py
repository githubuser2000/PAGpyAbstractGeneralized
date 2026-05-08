# -*- coding: utf-8 -*-
"""CLI für die Q-Wirtschaftssimulation."""

from __future__ import print_function

import argparse
import os
import sys

from .simulation import EconomySimulation, SCENARIOS


def build_parser():
    p = argparse.ArgumentParser(
        description="Q-Wirtschaftssimulation: semantische Münzen, Märkte, Arbeit, Staat, Banken, Schulden und Produktion.",
    )
    p.add_argument("--periods", type=int, default=120, help="Anzahl Perioden/Zyklen, Standard: 120")
    p.add_argument("--seed", type=int, default=42, help="Zufalls-Seed, Standard: 42")
    p.add_argument("--households", type=int, default=300, help="Anzahl Haushalte, Standard: 300")
    p.add_argument("--firms", type=int, default=80, help="Anzahl Firmen, Standard: 80")
    p.add_argument("--banks", type=int, default=4, help="Anzahl Banken, Standard: 4")
    p.add_argument("--scenario", choices=sorted(SCENARIOS.keys()), default="balanced", help="Szenario")
    p.add_argument("--out", default="qsim_output", help="Ausgabeordner")
    p.add_argument("--progress", action="store_true", help="Fortschritt auf der Konsole ausgeben")
    p.add_argument("--list-scenarios", action="store_true", help="Szenarien anzeigen und beenden")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_scenarios:
        for key in sorted(SCENARIOS):
            print("%-20s %s" % (key, SCENARIOS[key]))
        return 0
    sim = EconomySimulation(
        seed=args.seed,
        households=args.households,
        firms=args.firms,
        banks=args.banks,
        scenario=args.scenario,
    )
    sim.run(args.periods, progress=args.progress)
    paths = sim.save(args.out)
    summary = sim.final_summary()
    core = summary["core"]
    print("\nFertig.")
    print("Szenario: %s" % args.scenario)
    print("Perioden: %d" % args.periods)
    print("BQP: %.2f ZW" % core["bqp"])
    print("Arbeitslosigkeit: %.2f %%" % (core["unemployment_rate"] * 100.0))
    print("Inflation letzte Periode: %.2f %%" % (core["inflation"] * 100.0))
    print("Q-Schulden: %.2f ZW" % core["total_debt_value"])
    print("Berichte:")
    for name in sorted(paths):
        print("  %-14s %s" % (name + ":", paths[name]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
