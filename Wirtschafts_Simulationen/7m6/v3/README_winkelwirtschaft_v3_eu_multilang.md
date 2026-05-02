# Winkelwährungswirtschaft Simulation v3 — EU-Länderwahl und Mehrsprachigkeit

Diese Version simuliert die Winkelwährungswirtschaft mit drei zufällig ausgewählten EU-Staaten. Die drei Währungen bleiben **gleich lange Euro-Vektoren**: `|€⃗| = 1 VE`. Die Konkurrenz entsteht nicht durch Zahlen-Wechselkurse und nicht durch Förder-/Strafmechanik, sondern durch Winkel, Richtung, Resonanz, Machtbindung, Wohlbefinden und Spannung.

## Start

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py
```

Standard ist Englisch. Ohne `--seed` wird bei jedem Start automatisch ein frischer Seed erzeugt. Dadurch werden normalerweise andere drei EU-Staaten gewählt.

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --seed 42
```

Mit demselben Seed werden dieselben drei EU-Staaten und derselbe Simulationslauf reproduziert.

## Sprache wählen

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang de
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang ru
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang es
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang it
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang zh
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang ja
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang ko
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang hi
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang he
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang fa
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang ar
```

Unterstützte Sprachcodes und Aliase:

- `en` Englisch, Standard
- `de` Deutsch, auch `--deutsch`
- `ru` Russisch
- `es` Spanisch
- `it` Italienisch
- `zh` Chinesisch
- `ja` Japanisch
- `ko` Koreanisch
- `hi` Hindi; Alias: `indisch`
- `he` Hebräisch
- `fa` Persisch/Farsi
- `ar` Arabisch

## EU-Länderwahl

Automatische Auswahl:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --seed 123
```

Manuelle Vorgabe von drei EU-Staaten:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --countries DE,FR,IT
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --countries DEU,FRA,ITA
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --countries Deutschland,Frankreich,Italien --lang de
```

Wenn weniger als drei gültige Länder angegeben werden, füllt das Skript die restlichen Plätze seed-stabil auf.

## Breite und Farben

Die automatische Bildschirmbreitenerkennung rendert rechts **5 Zeichen kürzer**. Das verhindert, dass Tabellen, Kreise und UTF-8-Art zu hart an den rechten Terminalrand laufen.

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --width 100
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --no-color
```

`--width 100` bedeutet: 100 Zeichen Basisbreite, intern mit 5 Zeichen Sicherheitsrand.

## Kurzer Lauf

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --lang de --ticks 2 --detail kurz --seed 42
```

## Nur Handbuch anzeigen

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --only-manual --lang de --seed 42
```

## Szenarien

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario resonance
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario power
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario wellbeing
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario fragmented
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario scarcity
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --scenario tradeboom
```

## UTF-8-Art-Galerie

Die große bunte UTF-8-Galerie erscheint am Ende standardmäßig. Abschalten:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py --no-utf8-gallery
```

## Exporte

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v3_eu_multilang.py \
  --lang de \
  --seed 42 \
  --ticks 6 \
  --export-csv verlauf.csv \
  --export-currencies-csv waehrungen.csv \
  --export-md bericht.md
```

## Technische Hinweise

Das Skript nutzt nur Python-Standardbibliothek und ist für `pypy3` ausgelegt. Es läuft auch mit normalem `python3`.
