# Bunte Terminal-Anzeige

Diese Version zeigt die Verträge und Wahrheitsdimensionen **farbig und stylisch** im Terminal an.

## Start

```bash
pypy3 planetary_effect_economy.py   --steps 120   --scenario planetary_commons   --out out_planetenwirtschaft   --show-trades 40   --show-trade-detail   --show-dimensions   --show-catalog   --show-stack-explanation
```

Ohne PyPy3:

```bash
python3 planetary_effect_economy.py   --steps 120   --scenario planetary_commons   --out out_planetenwirtschaft   --show-trades 40   --show-trade-detail   --show-dimensions   --show-catalog   --show-stack-explanation
```

## Farben

Jede Dimension hat jetzt eine eigene Farbe, ein Symbol und sichtbare Balken:

- Kausalität
- Zeit
- Intensität
- Existenz
- Potenzen
- Wirkungen
- Substanz
- Materie
- Differenz
- Bestimmung
- Phänomene
- Winkelrichtung

## Optional

Farben abschalten:

```bash
python3 planetary_effect_economy.py --no-color
```

## Extrem bunte UTF-8-Art-Galerie

Unterhalb der sichtbaren Wirkungsverträge wird jetzt zusätzlich eine große UTF-8/ANSI-Art-Galerie angezeigt.

```bash
python3 planetary_effect_economy.py --show-trades 40 --show-trade-detail --show-art 30
```

Farben beim Umleiten/Pipen erzwingen:

```bash
python3 planetary_effect_economy.py --show-art 30 --force-color > bunte_ausgabe.txt
```

Ausschalten:

```bash
python3 planetary_effect_economy.py --show-art 0
```


## Automatischer Bildschirmumbruch

Diese Version erkennt die Terminalbreite automatisch. UTF-8-Rahmen, Balken,
Panels und farbige Textzeilen werden an die gefundene Bildschirmbreite
angepasst. ANSI-Farbcodes werden beim Messen ignoriert, damit farbige Zeilen
nicht fälschlich zu breit berechnet werden.

Bei Weiterleitung/Pipe nutzt das Programm eine sichere Standardbreite. Viele
Terminals erlauben zusätzlich eine Vorgabe über `COLUMNS`, zum Beispiel:

```bash
COLUMNS=80 python3 planetary_effect_economy.py --show-art 30 --force-color
```
