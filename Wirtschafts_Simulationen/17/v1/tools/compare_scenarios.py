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
        print("%-20s BQP=%8.2f  Arbeitslosigkeit=%5.1f%%  Schulden=%9.2f" % (
            scenario, row["bqp"], row["unemployment_rate"] * 100.0, row["total_debt_value"]
        ))
    csv_path = os.path.join(args.out, "scenario_comparison.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fields = ["scenario", "periods", "bqp", "price_index", "inflation", "unemployment_rate", "total_positive_money_value", "total_debt_value", "loan_outstanding", "government_net_worth", "household_gini"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    md_path = os.path.join(args.out, "scenario_comparison.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Szenariovergleich\n\n")
        f.write("| Szenario | BQP | Arbeitslosigkeit | Inflation | Q-Schulden | Gini |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for r in rows:
            f.write("| %s | %.2f | %.2f %% | %.2f %% | %.2f | %.4f |\n" % (
                r["scenario"], r["bqp"], r["unemployment_rate"] * 100.0, r["inflation"] * 100.0, r["total_debt_value"], r["household_gini"]
            ))
    print("\nVergleich gespeichert:")
    print("  ", csv_path)
    print("  ", md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
