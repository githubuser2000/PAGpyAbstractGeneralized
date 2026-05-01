# TGW UTF‑8 Art Simulation — erweiterte PyPy3-Simulation

Diese Version erweitert die vorhandene TGW-Simulation um umfangreiche UTF‑8-Grafiken, Diagramme, Legenden und Ergebnisdiagnosen. Der Simulationskern bleibt gleich:

- genau eine Währung: **LZ / Lösungszahl**
- additive Gruppe: Konten können positiv und negativ sein
- Topologie: Problem- und Lösungsbereiche als offene Mengen
- Stack: `(offene Menge U, Gruppenwert g)`
- positive LZ durch Problemlösung
- negative LZ durch Schaden, Betrug, Krieg, Problemwachstum, Kreditlast oder Externalitäten

Die neue Datei `tgw_pypy3_utf8_art_simulation.py` ist ein reichhaltiger Frontend-Runner. Sie importiert den ursprünglichen Kern `tgw_pypy3_simulation.py`, führt die Simulation aus und erzeugt danach einen stark bebilderten UTF‑8-Bericht.

## Enthaltene UTF‑8 Arts

Jede Grafik hat direkt darüber eine eigene Legende. Die Abkürzungen werden also nicht global erklärt, sondern passend zur jeweiligen Grafik.

1. **Mathematischer Stack-Kern** — Topologie + Gruppe + Stack + Fusion
2. **Markt- und Zahlungsfluss** — Haushalte, Firmen, Banken, Staaten, Fonds, Auditoren, Escrow
3. **Intergalaktische Kausalzellen-Karte** — Galaxien, Planeten, Staaten und Problemschwere
4. **Bilanz-Skyline der Akteure** — positive und negative Top-Konten
5. **Zeitreihen-Sparklines** — offene Probleme, Lösung, Schaden, negative Akteure, Spannung, Betrug
6. **Topologische Problem-Heatmap** — Domänen wie Energie, Wasser, Governance, Sicherheit, Forschung
7. **Topologie-Fit und Adapterarbeit** — Kompatibilität zwischen Solver und Problemraum
8. **Intergalaktischer Escrow-Kanal** — Lock, Verzögerung, Release, Remote-Projekte
9. **Konfliktleiter** — Frieden, kalter Druck, heiße Gefahr, Kriegsspirale
10. **Betrug, Audit und inverse Buchung** — Promise, Actual, Penalty, Audit-Korrektur
11. **Institutionen-Bilanz** — Haushalte, Firmen, Banken, Staaten, Fonds, Prüfer
12. **Ergebnis-Scorecard** — Reparaturquote, Backlog, Betrugsstress, Konfliktstress, Arbeitslosigkeit
13. **Ereignisleiste** — letzte wichtige Simulationsereignisse

## Einzelszenario ausführen

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario baseline \
  --ticks 120 \
  --seed 42 \
  --report-out mein_utf8_report.txt
```

Mit normalem Python 3 geht es ebenfalls:

```bash
python3 tgw_pypy3_utf8_art_simulation.py --ticks 120 --report-out mein_utf8_report.txt
```

## Szenario-Suite ausführen

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario-suite \
  --ticks 120 \
  --seed 42 \
  --suite-out suite_report.md \
  --quiet
```

Die Suite vergleicht mehrere Ausgänge: Baseline, Konflikt, Betrug, Intergalaktik und Knappheit.

## Kuratierte Beispielausgänge

Die Beispielberichte im Paket zeigen bewusst verschiedene Endzustände:

- `tgw_utf8_stable_repair_report.txt` — stabiler Lösungsaufbau
- `tgw_utf8_conflict_spiral_report.txt` — konfliktlastiger Ausgang
- `tgw_utf8_fraud_stress_report.txt` — Audit-/Betrugsstress
- `tgw_utf8_scarcity_backlog_report.txt` — Reparaturrückstand
- `tgw_utf8_intergalactic_latency_report.txt` — intergalaktische Verzögerung mit Escrow-Locks
- `tgw_utf8_outcome_gallery_report.md` — Vergleich dieser verschiedenen Ausgänge

Diese Beispielberichte sind keine Prognosen. Sie sind Simulationsläufe mit bestimmten Seeds und Parametern, damit die Mechaniken sichtbar werden.

## Beispiel: stabiler Lösungsaufbau

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario baseline \
  --ticks 80 \
  --seed 111 \
  --households 250 \
  --firms 100 \
  --galaxies 2 \
  --planets-per-galaxy 2 \
  --states-per-planet 2 \
  --initial-problems-per-state 2 \
  --max-projects-started-per-tick 50 \
  --max-active-projects 200 \
  --fraud-pressure 0.12 \
  --externality-rate 0.10 \
  --war-probability 0 \
  --report-out tgw_utf8_stable_repair_report.txt
```

## Beispiel: Konfliktspirale

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario conflict \
  --ticks 100 \
  --seed 222 \
  --households 180 \
  --firms 45 \
  --galaxies 3 \
  --planets-per-galaxy 2 \
  --states-per-planet 2 \
  --war-probability 0.02 \
  --report-out tgw_utf8_conflict_spiral_report.txt
```

## Beispiel: Betrugsstress

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario fraud \
  --ticks 90 \
  --seed 333 \
  --fraud-pressure 3.0 \
  --report-out tgw_utf8_fraud_stress_report.txt
```

## Beispiel: Intergalaktische Latenz

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --scenario intergalactic \
  --ticks 110 \
  --seed 555 \
  --galaxies 5 \
  --firms 15 \
  --remote-project-probability 1.0 \
  --intergalactic-delay 40 \
  --report-out tgw_utf8_intergalactic_latency_report.txt
```

## CSV und JSON

Auch die neue Frontend-Datei kann CSV- und JSON-Ausgaben erzeugen:

```bash
pypy3 tgw_pypy3_utf8_art_simulation.py \
  --ticks 150 \
  --csv-out tgw_timeseries.csv \
  --json-out tgw_final.json \
  --report-out tgw_report.txt
```

## Grenzen

Die UTF‑8-Grafiken sind bewusst Textgrafiken. Sie sind copy-paste-freundlich und laufen ohne externe Bibliotheken. Sie ersetzen keine mathematisch perfekte Visualisierung, sondern machen die Mechanik im Terminal sichtbar.

Wichtig bleibt: Das Modell ist ein Simulationslabor, keine reale Wirtschaftsprognose. Es zeigt, wie ein Ein-Währungs-System mit Topologie, additiver Gruppe, positiven/negativen LZ, Problemlösungsmärkten und Reparaturbuchungen funktionieren könnte.
