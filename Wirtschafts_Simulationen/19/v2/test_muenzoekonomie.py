#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""Kleine Standardbibliothek-Tests für muenzoekonomie.py.

Ausführen:
    pypy3 test_muenzoekonomie.py
oder:
    python3 test_muenzoekonomie.py
"""

import os
import tempfile

from muenzoekonomie import Economy, CATEGORY_INFO, category_markdown_table


def main():
    assert len(CATEGORY_INFO) == 19, "Es müssen genau 19 Kategorien vorhanden sein."
    assert "Ziel-Ergebnis" in CATEGORY_INFO[19]["short"], "Kategorie 19 fehlt oder ist falsch."
    assert "Fusion" in CATEGORY_INFO[14]["short"], "Kategorie 14 fehlt oder ist falsch."

    eco = Economy(seed=123, households=18, firms_per_category=1, banks=1, shock_frequency=0.0)
    eco.run(4, quiet=True)

    assert len(eco.metrics) == 4, "Es müssen vier Perioden simuliert worden sein."
    assert eco.metrics[-1]["coins_created"] > 0, "Es müssen Münzen erzeugt werden."
    assert eco.metrics[-1]["money_supply"] > 0, "Geldmenge muss positiv sein."
    assert 0 <= eco.metrics[-1]["unemployment"] <= 1, "Arbeitslosigkeit muss zwischen 0 und 1 liegen."
    assert 0 <= eco.metrics[-1]["nature_capital"] <= 1.15, "Naturkapital außerhalb des Modellbereichs."
    assert len(category_markdown_table().splitlines()) >= 21, "Kategorietabelle ist zu kurz."

    out = tempfile.mkdtemp(prefix="muenzoekonomie_test_")
    eco.export(out)
    for name in ["metrics.csv", "ledger.csv", "agents.json", "coins.json", "contracts.json", "summary.md"]:
        path = os.path.join(out, name)
        assert os.path.exists(path), "Export fehlt: %s" % name
        assert os.path.getsize(path) > 0, "Export ist leer: %s" % name

    print("OK: Münzökonomie-Simulation, Kategorien, Kennzahlen und Export funktionieren.")


if __name__ == "__main__":
    main()
