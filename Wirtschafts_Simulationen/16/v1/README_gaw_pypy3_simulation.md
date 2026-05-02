# Gestapelte Arbeitsblock-Wirtschaft – PyPy3-Simulation

Diese Datei ist eine umfangreiche, farbige Terminal-Simulation des Arbeitswährungs-Systems.
Sie läuft ohne externe Bibliotheken und ist für `pypy3` geschrieben.

## Start

```bash
pypy3 gaw_pypy3_simulation.py
```

Auch möglich, falls PyPy3 nicht installiert ist:

```bash
python3 gaw_pypy3_simulation.py
```

## Beispiele

```bash
pypy3 gaw_pypy3_simulation.py --szenario krise --perioden 8
pypy3 gaw_pypy3_simulation.py --szenario forschung --perioden 12 --seed 7
pypy3 gaw_pypy3_simulation.py --teile faktoren,arbeit,markt,schluss
pypy3 gaw_pypy3_simulation.py --no-color
```

## Optionen

- `--szenario normal|krise|forschung|hausbau` verändert Knappheit, öffentliche Belastung, Kreditrisiko und Ressourcenentnahme.
- `--perioden N` bestimmt die Länge der Mehrperioden- und Ressourcensimulation.
- `--seed N` macht Zufall reproduzierbar.
- `--teile ...` startet nur ausgewählte Simulationsteile.
- `--breite N` verändert die Tabellenbreite.
- `--no-color` schaltet Farben aus.

## Enthaltene Simulationsteile

1. Wertskala der Arbeitsarten
2. Einzelne Arbeitsblöcke
3. Projektstapel am Beispiel eines Hauses
4. Marktpreise mit Knappheit
5. Gemeinfonds und öffentliche Geldsteuerung
6. Produktionskredit und Lagerware
7. Ressourcenbestand und ökologische Rückkopplung
8. Negative Arbeit und Schadensabzug
9. Mehrperioden-Wirtschaft mit Sektoren
10. Prüfung gegen Faktorbetrug
11. Schlussübersicht der Simulation

Jeder Simulationsteil erklärt direkt in der Ausgabe, was simuliert wird. Danach werden nur die Kürzel erklärt, die in diesem Teil wirklich vorkommen.
