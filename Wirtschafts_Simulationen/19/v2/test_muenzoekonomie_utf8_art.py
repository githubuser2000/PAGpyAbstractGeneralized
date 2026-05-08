#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""Tests für die Art-only-Ausgabe der Münzökonomie."""

from __future__ import print_function

import argparse
import os
import tempfile

from muenzoekonomie import run_art_simulation


def main():
    args = argparse.Namespace(
        years=1,
        periods_per_year=1,
        households=10,
        firms_per_category=1,
        banks=1,
        seed=99,
        no_foreign=False,
        shock_frequency=0.0,
        out="",
        no_print=True,
    )
    report = run_art_simulation(args)
    assert "UTF-8-Art 01" in report
    assert "Warum:" in report
    assert "Was:" in report
    assert "Abkürzungen:" in report
    assert "Auswertung:" in report
    assert "metrics.csv" not in report
    assert "ledger.csv" not in report
    assert "Fertig nach" not in report
    assert len(report.splitlines()) > 150

    out = tempfile.mkdtemp(prefix="muenzoekonomie_art_test_")
    args.out = out
    # run_art_simulation schreibt nicht; Datei-Schreiben passiert nur im CLI.
    report2 = run_art_simulation(args)
    assert report2

    print("OK: UTF-8-Art-Bericht enthält Erklärung, Abkürzungen, Auswertung und keine Normalausgabe.")


if __name__ == "__main__":
    main()
