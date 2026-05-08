# -*- coding: utf-8 -*-
"""Command line interface for the Q economy simulation."""

from __future__ import print_function

import argparse
import sys

from .simulation import EconomySimulation, SCENARIOS
from .utf8art import build_terminal_dashboard, normalize_width
from .i18n import normalize_language, t, scenario_description, PUBLIC_LANGUAGE_NAMES


def build_parser():
    p = argparse.ArgumentParser(
        description="Q economy simulation: semantic coins, markets, all forms of work, state, banks, debt and production.",
    )
    p.add_argument("--periods", type=int, default=120, help="number of periods/cycles, default: 120")
    p.add_argument("--seed", type=int, default=42, help="random seed, default: 42")
    p.add_argument("--households", type=int, default=300, help="number of households, default: 300")
    p.add_argument("--firms", type=int, default=80, help="number of firms, default: 80")
    p.add_argument("--banks", type=int, default=4, help="number of banks, default: 4")
    p.add_argument("--scenario", choices=sorted(SCENARIOS.keys()), default="balanced", help="scenario")
    p.add_argument("--out", default="qsim_output", help="output folder")
    p.add_argument("--progress", action="store_true", help="print localized colorful UTF-8 progress lines")
    p.add_argument("--no-dashboard", action="store_true", help="do not print the large UTF-8 art dashboard at the end")
    p.add_argument("--no-color", action="store_true", help="disable ANSI terminal colors; UTF-8/emoji remain")
    p.add_argument("--language", default="english", help="report language; default: english; also: %s" % ", ".join(PUBLIC_LANGUAGE_NAMES[1:]))
    p.add_argument("--width", default="auto", help="window width: auto detects terminal columns and subtracts 5; or pass an integer")
    p.add_argument("--list-scenarios", action="store_true", help="list scenarios and exit")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        language = normalize_language(args.language)
    except ValueError as exc:
        parser.error(str(exc))
    width = normalize_width(args.width)
    if args.list_scenarios:
        for key in sorted(SCENARIOS):
            print("%-20s %s" % (key, scenario_description(key, language)))
        return 0
    sim = EconomySimulation(
        seed=args.seed,
        households=args.households,
        firms=args.firms,
        banks=args.banks,
        scenario=args.scenario,
    )
    sim.run(args.periods, progress=args.progress, color=not args.no_color, language=language, width=width)
    paths = sim.save(args.out, language=language, width=width)
    if not args.no_dashboard:
        print("\n" + build_terminal_dashboard(sim, ansi=not args.no_color, language=language, width=width))
    print("\n✅ %s" % t(language, "done"))
    print("📁 %s: %s" % (t(language, "output_folder"), args.out))
    print("🎨 %s:" % t(language, "important_files"))
    for key in ("summary", "visual_report", "dashboard_utf8", "visual_report_ansi"):
        if key in paths:
            print("  %-20s %s" % (key + ":", paths[key]))
    print("📊 %s:" % t(language, "raw_data"))
    for name in sorted(paths):
        if name not in ("summary", "visual_report", "dashboard_utf8", "visual_report_ansi"):
            print("  %-20s %s" % (name + ":", paths[name]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
