# Münzökonomie – ausschließlich bunte UTF-8-Art-Simulation

Dieses Paket enthält die PyPy3-kompatible Münzökonomie aus dem bisherigen Chat, aber mit neuem Standardlauf:
Die sichtbare Simulation zeigt ausschließlich bunte UTF-8-Art-Diagramme, Abbildungen und Darstellungen.

Der ökonomische Kern bleibt vollständig erhalten und liegt in `muenzoekonomie_core.py`. Das Hauptprogramm `muenzoekonomie.py` importiert diesen Kern, rechnet die Simulation und rendert danach nur den UTF-8-Art-Bericht.

## Erfüllte Ausgabe-Regeln

Jede einzelne UTF-8-Art hat:

- direkt darüber eine Erklärung, warum simuliert wird,
- direkt darüber eine Erklärung, was simuliert wird,
- direkt darüber nur die Abkürzungen, die in genau dieser UTF-8-Art vorkommen,
- direkt darunter eine eigene Auswertung des jeweiligen Simulationsergebnisses.

Im normalen Lauf erscheinen keine Fortschrittszeilen, keine CSV-/JSON-Tabellen und keine nüchterne Abschlussstatistik.

## Ausführen

```bash
pypy3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42
```

Oder mit CPython 3:

```bash
python3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42
```

## Ausgabe speichern

```bash
pypy3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42 --out ergebnis
```

Dann wird zusätzlich geschrieben:

```text
ergebnis/utf8_art_report.txt
```

Mit `--no-print` wird nur gespeichert und nichts ins Terminal geschrieben:

```bash
pypy3 muenzoekonomie.py --years 20 --out ergebnis --no-print
```

## Optionen

```text
--years                 Anzahl Jahre
--periods-per-year      Perioden pro Jahr
--households            Anzahl Haushalte
--firms-per-category    Unternehmen pro Kategorie
--banks                 Anzahl Banken
--seed                  Zufallsseed
--no-foreign            Außenhandel deaktivieren
--shock-frequency       Wahrscheinlichkeit eines Schocks je Periode
--out                   Ordner für utf8_art_report.txt
--no-print              Terminalausgabe abschalten, nur Datei schreiben
```

## Enthaltene Dateien

```text
muenzoekonomie.py                    Hauptprogramm mit Art-only-Ausgabe
muenzoekonomie_core.py               vollständiger Simulationskern
README_muenzoekonomie_utf8_art.md    diese Anleitung
test_muenzoekonomie.py               Basistest für Kern und Export
test_muenzoekonomie_utf8_art.py      Test für den UTF-8-Art-Bericht
beispiel_utf8_art.txt                Beispielbericht
```

## Hinweis

Die Art-Ausgabe nutzt Unicode-Zeichen, farbige Emoji-Blöcke und UTF-8-Symbole. Ein modernes Terminal mit UTF-8-Unterstützung ist sinnvoll.
