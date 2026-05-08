#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mehrere Szenarien vergleichen.

Beispiel:
    pypy3 tools/compare_scenarios.py --periods 80 --households 250 --firms 70 --out scenario_runs
"""

from __future__ import print_function

import argparse
import csv
import os
import sys

# erlaubt Start aus tools/ heraus
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from qsim.simulation import EconomySimulation, SCENARIOS
from qsim.utf8art import build_scenario_comparison_art


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def main(argv=None):
    p = argparse.ArgumentParser(description="Vergleicht Q-Wirtschaftsszenarien.")
    p.add_argument("--periods", type=int, default=80)
    p.add_argument("--households", type=int, default=250)
    p.add_argument("--firms", type=int, default=70)
    p.add_argument("--banks", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="scenario_comparison_output")
    p.add_argument("--no-color", action="store_true", help="ANSI-Farben in der Konsolenausgabe deaktivieren")
    p.add_argument("--scenarios", nargs="*", default=["balanced", "code_bubble", "energy_crisis", "automation_wave", "public_investment", "austerity", "climate_shock", "architecture_crisis"])
    args = p.parse_args(argv)
    ensure_dir(args.out)
    rows = []
    for i, scenario in enumerate(args.scenarios):
        if scenario not in SCENARIOS:
            print("Überspringe unbekanntes Szenario:", scenario)
            continue
        out_dir = os.path.join(args.out, scenario)
        sim = EconomySimulation(seed=args.seed + i * 1000, households=args.households, firms=args.firms, banks=args.banks, scenario=scenario)
        sim.run(args.periods, progress=False)
        sim.save(out_dir)
        core = sim.final_summary()["core"]
        row = {
            "scenario": scenario,
            "periods": args.periods,
            "bqp": core["bqp"],
            "price_index": core["price_index"],
            "inflation": core["inflation"],
            "unemployment_rate": core["unemployment_rate"],
            "total_positive_money_value": core["total_positive_money_value"],
            "total_debt_value": core["total_debt_value"],
            "loan_outstanding": core["loan_outstanding"],
            "government_net_worth": core["government_net_worth"],
            "household_gini": core["household_gini"],
        }
        rows.append(row)
        # Keine trockene Zahlenzeile mehr: der eigentliche Vergleich wird als UTF-8-Art-Bericht erzeugt.
        print("✅ Szenario %-20s simuliert" % scenario)
    csv_path = os.path.join(args.out, "scenario_comparison.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fields = ["scenario", "periods", "bqp", "price_index", "inflation", "unemployment_rate", "total_positive_money_value", "total_debt_value", "loan_outstanding", "government_net_worth", "household_gini"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    md_path = os.path.join(args.out, "scenario_comparison.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_scenario_comparison_art(rows, markdown=True, ansi=False))
    ansi_path = os.path.join(args.out, "scenario_comparison_ansi.txt")
    with open(ansi_path, "w", encoding="utf-8") as f:
        f.write(build_scenario_comparison_art(rows, markdown=False, ansi=True))
    plain_path = os.path.join(args.out, "scenario_comparison_utf8.txt")
    with open(plain_path, "w", encoding="utf-8") as f:
        f.write(build_scenario_comparison_art(rows, markdown=False, ansi=False))
    print("\n" + build_scenario_comparison_art(rows, markdown=False, ansi=not args.no_color))
    print("\nVergleich gespeichert:")
    print("  ", csv_path)
    print("  ", md_path)
    print("  ", plain_path)
    print("  ", ansi_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
