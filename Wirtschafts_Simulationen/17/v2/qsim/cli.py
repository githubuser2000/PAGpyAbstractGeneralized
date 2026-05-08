# -*- coding: utf-8 -*-
"""CLI für die Q-Wirtschaftssimulation."""

from __future__ import print_function

import argparse
import os
import sys

from .simulation import EconomySimulation, SCENARIOS
from .utf8art import build_terminal_dashboard


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
    p.add_argument("--progress", action="store_true", help="Fortschritt auf der Konsole als farbige UTF-8-Art-Zeile ausgeben")
    p.add_argument("--no-dashboard", action="store_true", help="Am Ende keinen großen farbigen UTF-8-Art-Bericht auf der Konsole drucken")
    p.add_argument("--no-color", action="store_true", help="ANSI-Farben in der Konsole deaktivieren; Emoji/UTF-8 bleiben erhalten")
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
    sim.run(args.periods, progress=args.progress, color=not args.no_color)
    paths = sim.save(args.out)
    if not args.no_dashboard:
        print("\n" + build_terminal_dashboard(sim, ansi=not args.no_color))
    print("\n✅ Fertig. Die Hauptausgaben sind jetzt farbige UTF-8-Art-Berichte mit Beschreibung über jeder Abbildung und Auswertung darunter.")
    print("📁 Ausgabeordner: %s" % args.out)
    print("🎨 Wichtigste Dateien:")
    for key in ("summary", "visual_report", "dashboard_utf8", "visual_report_ansi"):
        if key in paths:
            print("  %-20s %s" % (key + ":", paths[key]))
    print("📊 Rohdaten bleiben zusätzlich für eigene Analysen erhalten:")
    for name in sorted(paths):
        if name not in ("summary", "visual_report", "dashboard_utf8", "visual_report_ansi"):
            print("  %-20s %s" % (name + ":", paths[name]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
