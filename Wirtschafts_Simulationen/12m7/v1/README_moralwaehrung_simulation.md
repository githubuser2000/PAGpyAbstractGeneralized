# Radial-hierarchische Moralwährungs-Simulation

Dieses Paket enthält eine umfangreiche, sehr farbige Terminalsimulation in reinem Python, lauffähig mit `pypy3` oder `python3`.

## Start

```bash
pypy3 moralwaehrung_simulation_pypy3.py
```

Falls PyPy3 nicht installiert ist:

```bash
python3 moralwaehrung_simulation_pypy3.py
```

## Nützliche Varianten

```bash
pypy3 moralwaehrung_simulation_pypy3.py --seed 17 --ticks 8 --color always
pypy3 moralwaehrung_simulation_pypy3.py --compact --no-animation
pypy3 moralwaehrung_simulation_pypy3.py --color never > bericht.txt
```

## Was simuliert wird

Die Simulation modelliert eine mehrdimensionale Wertwährung mit radialer Achsenlogik:

- Gutartigkeit gegen Schädlichkeit
- Beliebtheit gegen Unbeliebtheit
- veränderliche Hierarchie
- Produktmarkt
- Arbeitsmarkt
- Aktienmarkt
- Währungsmarkt
- Versicherungsmarkt
- Karriere und Abstieg
- Manipulations-Stresstest
- Anspruchsverteilung knapper Güter
- Marktsegment-Matrix
- finale Diagnose

Jeder Simulationsteil erklärt direkt über der Ausgabe nur die Kürzel, die in diesem Teil vorkommen. Mehrbuchstabige Kürzel und Einheiten werden in der Terminalausgabe farbig dargestellt.

## Dateien

- `moralwaehrung_simulation_pypy3.py` — Hauptsimulation
- `moralwaehrung_simulation_beispiel_farbig.ansi` — Beispielausgabe mit ANSI-Farbcodes
- `moralwaehrung_simulation_beispiel_text.txt` — dieselbe Beispielausgabe ohne Farbcodes
