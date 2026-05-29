# Planetare WK-Wirtschaftssimulation — OOP/UTF-8 Edition

Diese Version ist eine stark objektorientierte Variante der planetaren Wirtschaftssimulation mit gestapelter Wahrheitswert-Währung (`WK`).

## Start

```bash
python planet_truth_economy_oop_utf8_sim.py --preset tiny --months 24 --verbose --print-art
```

Größer:

```bash
python planet_truth_economy_oop_utf8_sim.py --preset standard --months 120 --seed 7 --out sim_output
python planet_truth_economy_oop_utf8_sim.py --preset large --months 360 --out large_world
python planet_truth_economy_oop_utf8_sim.py --preset epic --months 720 --seed 42 --out epic_world
```

## Wichtige Dateien nach einem Lauf

- `summary.txt`: Zusammenfassung plus großer UTF-8-Art-Anhang
- `utf8_art_report.txt`: reine Unicode-Diagramme/Grafiken
- `history.csv`: Zeitreihen
- `countries.csv`: Länderzustände
- `companies.csv`: Firmenzustände
- `banks.csv`: Bankzustände
- `events.json`: Ereignisse
- `transactions.json`: letzte Transaktionen

## Modellidee

Ein Kauf ist in dieser Simulation eine Kombination aus Fiat-Zahlung, Wahrheitswert-Transfer und Realitätsänderung. WK ist kein Skalar, sondern ein Vektor aus Wahrheitsdimensionen wie Legalität, Kausalität, Existenz, Epistemik, Sicherheit, Zeitbindung, Potenzial, Wahrnehmung, Gesundheit, Infrastruktur, Souveränität usw. Negative Komponenten modellieren Schulden, Lügenlasten, nicht eingelöste Kausalversprechen und Zukunftsverpflichtungen.
