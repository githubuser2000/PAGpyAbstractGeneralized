# Planetenwirtschaft PyPy3-Simulation

Dieses Projekt ist eine lauffähige, reine Python/PyPy3-Simulation des im Chat entwickelten Wirtschaftssystems:

> **Wirtschaft = koordinierte Veränderung realer Zustände**  
> statt Kauf/Verkauf von Dingen über Preis, Wert, Menge und Besitz.

Die Simulation ist absichtlich **keine Volkswirtschaft**. Sie hat keine Staaten als Hauptakteure, kein BIP, keine Währungen und keine Preise. Sie simuliert einen **gesamten Planeten** als Zusammenspiel von:

- planetaren Grenzen: Klima, Biosphäre, Süßwasser, Boden, Verschmutzung, Material- und Energiedurchsatz
- Bioregionen statt Nationalstaaten
- Kommunen als konkrete Orte von Bedarf, Substanz und Wirkung
- Bevölkerungs-Kohorten als Einzelpersonen-Ebene in aggregierter Form
- Gruppen/Fähigkeitsfelder: Wasser, Landwirtschaft, Energie, Wohnen, Gesundheit, Pflege, Bildung, Logistik, Reparatur, Ökologie
- gestapelten logischen Wahrheitswerten für jedes Handlungsfeld
- globaler Verteilung von Überschüssen nach realer Dringlichkeit statt Kaufkraft
- Rückkopplung über Vertrauen, Autonomie, Demokratiequalität und Wahrheitsfehler

## Schnellstart

```bash
pypy3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out_planetenwirtschaft
```

Falls PyPy3 nicht installiert ist, funktioniert es auch mit CPython:

```bash
python3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out_planetenwirtschaft
```

## Szenarien

```bash
pypy3 planetary_effect_economy.py --scenario planetary_commons
pypy3 planetary_effect_economy.py --scenario local_democracy
pypy3 planetary_effect_economy.py --scenario technocratic_control
pypy3 planetary_effect_economy.py --scenario ecological_crisis
pypy3 planetary_effect_economy.py --scenario scarcity_shock
```

Bedeutung:

| Szenario | Bedeutung |
|---|---|
| `planetary_commons` | Standard: demokratische planetare Commons-Logik |
| `local_democracy` | stärkere kommunale Demokratie, weniger Zentralisierung |
| `technocratic_control` | Kontrollsystem: hohe Zentralisierung, niedrige Privatsphäre, schwache Korrektur |
| `ecological_crisis` | Start mit überschrittenen planetaren Grenzen |
| `scarcity_shock` | Start mit Wasser-/Nahrungs-/Energieknappheit |

## Ausgabedateien

Nach einem Lauf erscheinen im Ausgabeordner:

| Datei | Inhalt |
|---|---|
| `summary.json` | Endzusammenfassung mit Anfang/Ende/Delta |
| `timeline.csv` | globale Monats-Zeitreihe |
| `communes_final.csv` | Endzustand aller Kommunen |
| `truth_audit.csv` | höchste Wahrheitswert-Prioritäten des letzten Schritts |
| `manifest.md` | menschenlesbare Interpretation des Laufs |

## Wichtige Modellidee

Jede Kommune berechnet für jedes Feld einen Wahrheitsvektor:

```text
Kausalität, Zeit, Intensität, Existenz, Potenzial, Wirkung,
Substanz, Materie, Differenz, Bestimmung, Phänomen, Winkelrichtung
```

Daraus entsteht **keine Zahl als Preis**, sondern eine **Priorität als Wirklichkeitskoordination**.

Beispiel:

```text
Wasserbedarf hoch + Zeitdringlichkeit hoch + lösbares Potenzial hoch
+ positive Wirkung hoch + planetare Richtung gut
→ Arbeit, Energie und Reparaturmaterial werden in Wasserwirkung gelenkt.
```

## Was planetar und nicht national ist

Die Simulation ist planetar, weil:

1. planetare Grenzen als harte Systembedingungen wirken,
2. globale Überschüsse nach Bedürfnisdifferenzen verteilt werden,
3. Regionen Bioregionen sind, keine Staaten,
4. die Erde nicht als Rohstofflager, sondern als Lebensbedingung modelliert wird,
5. Abfall, Boden, Wasser, Klima, Energie und Biosphäre zur Wirtschaft selbst gehören,
6. Wohlbefinden nicht gegen Planetenschutz ausgespielt wird, sondern beides gemeinsam bewertet wird.

## Kennzahlen

| Kennzahl | Bedeutung |
|---|---|
| `wellbeing` | gewichtetes Wohlbefinden aus Bedürfnisdeckung, Gesundheit, Autonomie, Vertrauen und planetarer Sicherheit |
| `unmet_basic` | unerfüllte Grundbedürfnisse |
| `overshoot` | Summe der Überschreitungen planetarer Grenzen über 1.0 |
| `avg_truth_error` | Fehler der gesellschaftlichen Wahrheits-/Rückkopplungslogik |
| `avg_autonomy` | Freiheit/Autonomie der Personen/Kohorten |
| `avg_trust` | Vertrauen in die Koordination |

## Interpretation

Ein gutes Ergebnis ist nicht einfach „mehr Produktion“, sondern:

```text
weniger unerfüllte Grundbedürfnisse
+ weniger planetare Überschreitung
+ sinkender Wahrheitsfehler
+ stabile oder steigende Autonomie
+ weniger Abfall und bessere Stoffkreisläufe
```

Ein schlechtes Ergebnis ist besonders dann gefährlich, wenn die Grundversorgung zwar scheinbar geplant wird, aber Autonomie, Vertrauen und Wahrheitskorrektur zusammenbrechen. Dann wird aus Wirkungswirtschaft eine Kontrollmaschine.

## Technische Hinweise

- Keine externen Bibliotheken.
- Kompatibel mit PyPy3 und CPython 3.
- Reproduzierbar über `--seed`.
- Standardgröße: 8,1 Milliarden synthetische Menschen, 12 Bioregionen, 96 Kommunen, 120 Monate.
- Das Modell ist synthetisch und nicht empirisch kalibriert. Es ist ein Simulationsbaukasten, kein Prognosemodell.

## Beispiele

Kleiner schneller Test:

```bash
python3 planetary_effect_economy.py --steps 12 --regions 4 --communes-per-region 3 --population 10000000 --out quick_test
```

Vollerer Planetentest:

```bash
pypy3 planetary_effect_economy.py --steps 240 --regions 16 --communes-per-region 10 --population 8100000000 --scenario ecological_crisis --out long_crisis
```

## Mitgelieferte Beispiel-Läufe

Im Ordner `example_runs/` liegen bereits erzeugte Beispielausgaben für alle fünf Szenarien. Der Vergleich steht in:

```text
example_runs/scenario_comparison.md
example_runs/scenario_comparison.csv
```

Diese Beispiel-Läufe wurden in der Erstellungsumgebung mit `python3` ausgeführt. Der Code selbst ist für `pypy3` geschrieben und nutzt keine externen Pakete.
