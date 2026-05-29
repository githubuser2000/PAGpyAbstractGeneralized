# Planet Truth Paradigm Architecture — PyPy3 Process Edition

Diese Version simuliert eine planetare Wirtschaft mit nationalen Fiat-Währungen und einer globalen gestapelten Wahrheitswert-Währung `WK = Wahrheitskapital`.

## Änderungen in dieser Version

- Die Dokumentation steht am Anfang jeder Ausgabe.
- Die Beschreibung der Simulation und die Abkürzungen stehen weiterhin im Quelltext.
- Der UTF-8-Art-Report beginnt ebenfalls mit der Dokumentation.
- Vor jedem einzelnen UTF-8-Art-Diagramm steht eine eigene Erklärung, was das folgende Bild zeigt.
- UTF-8-Art-Ausgabe auf stdout ist Standard.
- Mit `--no-print-art` kann die lange Konsolenausgabe abgeschaltet werden; die Report-Dateien werden trotzdem geschrieben.
- Die automatische Terminal-Breitenerkennung zieht rechts jetzt 5 Zeichen Sicherheitsreserve ab.
- Prozessparallelisierung läuft über `multiprocessing` / `ProcessPoolExecutor`, bevorzugt für PyPy3, ohne Threads.

## Start

```bash
python planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24
```

Mit PyPy3 und automatischer Prozesszahl:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset standard --months 120 --workers auto --out run_standard
```

Ohne lange UTF-8-Ausgabe auf stdout:

```bash
python planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24 --no-print-art
```

## Ausgabe-Dateien

```text
history.csv
agents.csv
morphisms.csv
events.json
summary.json
summary.txt
utf8_paradigm_architecture_report.txt
```

`summary.txt` beginnt mit der Dokumentation und enthält danach Summary + alle UTF-8-Diagramme mit Erklärungen.
`utf8_paradigm_architecture_report.txt` beginnt ebenfalls mit der Dokumentation und enthält alle Diagramm-Erklärungen.

## Wichtige Optionen

```text
--preset tiny|standard|large|epic
--months N
--seed N
--out ORDNER
--workers auto|N
--mp-start-method auto|fork|spawn|forkserver
--parallel-min-items N
--print-art
--no-print-art
```
