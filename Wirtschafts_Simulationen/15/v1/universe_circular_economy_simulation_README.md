# Universum-Kreislaufwirtschaft — PyPy3 Simulation

Diese Simulation modelliert ein kosmisches Wirtschaftssystem auf Basis der gestapelten `for`-Schleifen-Währung.

## Kernformel

```text
SG_roh = (r - 1) * N + e - s
N(EarthType) = 20
N(VulcanType) = 22
SG_stack = Σ SG_roh_i * M_i * Q_i * U_i * G_i
UKE = SG_roh / N
```

Beispiele:

```text
EarthType:  start=4, end=17, repetition=4 => 73 SG
VulcanType: start=4, end=17, repetition=4 => 79 SG
```

## Enthaltene Simulationsschichten

- Kosmos mit einem oder mehreren Universen
- Universen mit Sternsystemen
- Sternsysteme mit Erde-Typ- und Vulkan-Typ-Planeten
- 20er- und 22er-Kreislaufalphabet
- Identitäten mit Kreislaufpass
- Agentenrollen: Bauer, Müller, Bäcker, Händler, Koch, Pfleger, Sanitärarbeiter, Kompostmeister, Chemiker, Geologe/Vulkanarbeiter, Validator, Banker
- Verifizierte und unverifizierte Geldschöpfung
- Gestapelte Schleifenwerte mit Material-, Qualitäts-, Nutzen- und Gerechtigkeitsfaktoren
- Kreislaufschuld für offene Abfall-, Schadstoff- und Hungerprozesse
- Staatliche Politik: Steuern, Reparatursubventionen, Kompostbonus, Sozialbonus, Prüfung
- Kreislaufbanken und Kredite auf erwartete Rückführung
- Interplanetarer Handel mit UKE-Normalisierung zwischen N=20 und N=22
- Kosmische Ereignisse: Signale, Strahlung, Kammerharmonisierung
- Lokale Ereignisse: Dürre, Mikrobenblüte, Schadstoffe, Technologie, Vulkaneruption
- Reports: Markdown, JSON, CSV-Ledger, Snapshots, Agenten, Identitätsproben

## Ausführen

```bash
pypy3 universe_circular_economy_simulation.py --seed 73 --ticks 60 --systems 2 --planets-per-system 3 --agents-per-planet 45 --report-dir uce_report
```

Alternativ mit CPython:

```bash
python3 universe_circular_economy_simulation.py --seed 73 --ticks 60 --systems 2 --planets-per-system 3 --agents-per-planet 45 --report-dir uce_report
```

## Größerer Lauf

```bash
pypy3 universe_circular_economy_simulation.py \
  --seed 7331 \
  --ticks 240 \
  --universes 2 \
  --systems 4 \
  --planets-per-system 5 \
  --agents-per-planet 80 \
  --report-dir uce_large_report \
  --progress
```

## Ausgabedateien

Im Report-Ordner entstehen:

- `final_report.md` — menschenlesbarer Markdown-Bericht
- `final_state.json` — vollständiger Endzustand
- `snapshots.csv` — Zeitreihe aller Planeten
- `ledger.csv` — Buchhaltung aller Schleifen-Transformationen
- `agents.csv` — Agentenbilanz
- `identity_samples.csv` — Stichprobe großer Identitäten mit Kreislaufpässen

## Hinweis

Die Simulation verwendet ausschließlich die Python-Standardbibliothek und ist für PyPy3 ausgelegt. In der aktuellen Umgebung wurde sie mit `python3` syntaxgeprüft und testweise ausgeführt; `pypy3` war hier nicht installiert.
