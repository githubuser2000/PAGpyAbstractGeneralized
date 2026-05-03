# Relational Currency Economy / Relationale Währungsökonomie

This package contains an expanded, very colorful PyPy3/Python-3 terminal simulation of a relational currency economy.
The currency is not a single number. It is modeled as a structured bundle of relations: claims, duties, risks, validity, labour safeguards, ecological burdens, credit quality, state gates and social protection.

Dieses Paket enthält eine erweiterte, sehr bunte PyPy3/Python-3-Terminalsimulation einer relationalen Währungsökonomie.
Die Währung ist keine einzelne Zahl. Sie wird als strukturiertes Bündel von Relationen modelliert: Ansprüche, Pflichten, Risiken, Gültigkeit, Arbeitsschutz, Umweltlasten, Kreditqualität, staatliche Grenzen und soziale Sicherung.

## Run / Ausführen

Default language is English:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py
```

German output:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py --lang de
```

Python 3 also works:

```bash
python3 rwoe_ultra_color_utf8_simulation.py --lang en
python3 rwoe_ultra_color_utf8_simulation.py --lang de
```

Run selected parts:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py --parts 1,4,7-9
pypy3 rwoe_ultra_color_utf8_simulation.py --teile 1,4,7-9 --lang de
```

Turn colors off:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py --no-color
```

Use another deterministic scenario seed:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py --seed 99
```

Change layout width:

```bash
pypy3 rwoe_ultra_color_utf8_simulation.py --width 120
```

## What is included / Inhalt

1. Anatomy of the relation currency / Anatomie der relationalen Währung
2. Market matching without a single price / Markt-Matching ohne einzelnen Preis
3. Production chain as relation flow / Produktionskette als Relationsfluss
4. Labour market with a worker shield / Arbeitsmarkt mit Arbeitsschutzschild
5. Credit as transformation of future relations / Kredit als Transformation von Zukunftsrelationen
6. The boom: hidden value becomes liquid / Der Boom: verborgener Wert wird liquide
7. The amoral dark side: trading domination / Die amoralische Schattenseite: Handel mit Herrschaft
8. Government gates and non-tradable rights / Regierungstore und nicht handelbare Rechte
9. Ecology attached to every traded bundle / Ökologie an jedem gehandelten Bündel
10. Central bank circuit and crisis handling / Zentralbankkreislauf und Krisenbehandlung
11. Social state as basic relation shield / Sozialstaat als Grundrelationsschild
12. Competition, platforms and monopoly pressure / Wettbewerb, Plattformen und Monopoldruck
13. Foreign trade and translation of standards / Außenhandel und Übersetzung von Standards
14. Full comparison with a plain market economy / Gesamtvergleich mit einer bloßen Marktwirtschaft

## Design rules implemented / Umgesetzte Gestaltungsregeln

- Output language parameter: `--lang en` or `--lang de`. Default is `en`.
- Every simulation part explains what is simulated and why it is simulated.
- Every simulation part explains only the abbreviations that occur in that specific part.
- Multi-letter abbreviations are colorized in the terminal.
- Units are colorized separately as unit pills.
- Each simulation part contains Unicode art, diagrams, tables, bars, heatmaps or flow illustrations.
- Each simulation part evaluates several possible starting scenarios: guarded, open, speculative and dark.
- The dark/amoral scenario is included only to expose the risk of domination markets, not to endorse it.
- No external packages are required.

## Files / Dateien

- `rwoe_ultra_color_utf8_simulation.py` — main script / Hauptskript
- `rwoe_sample_output_en_no_color.txt` — English sample output without color codes
- `rwoe_sample_output_de_no_color.txt` — German sample output without color codes
- `README_rwoe_ultra_color_utf8_simulation.md` — this file / diese Datei

