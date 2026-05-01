# 🌌 TGW UTF‑8 Szenario-Suite: verschiedene Ausgänge

Diese Auswertung vergleicht mehrere Läufe derselben Wirtschaftslogik. Jeder Lauf verwendet dieselbe
einzige Währung LZ,
dieselbe additive Gruppenbuchhaltung und dieselbe topologische Problem-/Lösungsstruktur. Die
Szenarien verändern nur die
Rahmenbedingungen: Konfliktwahrscheinlichkeit, Betrugsdruck, intergalaktische Remote-Projekte oder
Anfangsknappheit.

🔤 Abkürzungen dieser UTF‑8‑Art:
  SOL     = kumulierte Problemlösung
  DMG     = kumulierte formalisierte Schäden/Probleme
  OP      = offene Problemschwere am Ende
  REP     = Reparaturquote SOL/DMG
  BKL     = Backlogquote OP/DMG
  FRD     = entdeckte Betrugsfälle
  WAR     = heiße Konflikte
  maxT    = höchste politische Spannung
  Σbal    = Gesamtsumme aller Konten; soll nahe 0 bleiben

## 🧾 Vergleichstabelle

| Szenario | Ausgang | SOL | DMG | OP | REP | BKL | FRD | WAR | maxT | Σbal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stable_repair | 🟢 Stabiler Lösungsaufbau | +47.51k LZ | -51.09k LZ | -3.54k LZ | 93.0% | 6.9% | 0 | 0 | 1.351 | -0.000000 |
| conflict_spiral | 🔴 Konfliktlastiger Ausgang | +109.84k LZ | -128.05k LZ | -17.97k LZ | 85.8% | 14.0% | 2 | 1 | 1.933 | -0.000000 |
| fraud_stress | 🟠 Audit-/Betrugsstress | +114.38k LZ | -179.23k LZ | -64.61k LZ | 63.8% | 36.1% | 927 | 0 | 1.628 | -0.000000 |
| scarcity_backlog | 🟡 Reparaturrückstand | +66.29k LZ | -407.03k LZ | -340.74k LZ | 16.3% | 83.7% | 0 | 0 | 2.072 | 0.000000 |
| intergalactic_latency | 🟡 Kaltkonflikt-Druck | +165.45k LZ | -344.51k LZ | -179.06k LZ | 48.0% | 52.0% | 2 | 0 | 2.167 | 0.000000 |

## 📊 Vergleichsdiagramme

🔤 Abkürzungen dieser UTF‑8‑Art:
  SOL     = positive Problemlösung; höher ist besser
  DMG     = formalisierter Schaden; höher bedeutet mehr negative Stack-Erzeugung
  OP      = offene Problemschwere am Ende; niedriger ist besser
  FRP     = Fraud Penalty; Korrekturzahlungen wegen Betrug/Unterleistung
  WDMG    = Kriegsschaden
  │█░│    = Balken relativ zum größten Wert in diesem Vergleich

### stable_repair
  SOL   │██████████░░░░░░░░░░░░░░░░░░░░░░░░│ 47.51k
  DMG   │████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 51.09k
  OP    │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 3.54k
  FRP   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 0
  WDMG  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 0

### conflict_spiral
  SOL   │███████████████████████░░░░░░░░░░░│ 109.84k
  DMG   │███████████░░░░░░░░░░░░░░░░░░░░░░░│ 128.05k
  OP    │██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 17.97k
  FRP   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 792.90
  WDMG  │██████████████████████████████████│ 16.93k

### fraud_stress
  SOL   │████████████████████████░░░░░░░░░░│ 114.38k
  DMG   │███████████████░░░░░░░░░░░░░░░░░░░│ 179.23k
  OP    │██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 64.61k
  FRP   │██████████████████████████████████│ 182.37k
  WDMG  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 0

### scarcity_backlog
  SOL   │██████████████░░░░░░░░░░░░░░░░░░░░│ 66.29k
  DMG   │██████████████████████████████████│ 407.03k
  OP    │██████████████████████████████████│ 340.74k
  FRP   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 66.19
  WDMG  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 0

### intergalactic_latency
  SOL   │██████████████████████████████████│ 165.45k
  DMG   │█████████████████████████████░░░░░│ 344.51k
  OP    │██████████████████░░░░░░░░░░░░░░░░│ 179.06k
  FRP   │█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 4.73k
  WDMG  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ 0


## 🧠 Auswertung der verschiedenen Ausgänge

### stable_repair — 🟢 Stabiler Lösungsaufbau
stable_repair Reparaturquote: 93.0%. Backlogquote: 6.9%. Betrugsfälle: 0. Kriegsevents: 0.
Maximalspannung: 1.351.
Daraus folgt: Die Solver-Kapazität hält mit Schäden und öffentlichen Problemen mit; das System wird
tendenziell stabiler.

### conflict_spiral — 🔴 Konfliktlastiger Ausgang
conflict_spiral Reparaturquote: 85.8%. Backlogquote: 14.0%. Betrugsfälle: 2. Kriegsevents: 1.
Maximalspannung: 1.933.
Daraus folgt: Konflikt- und Sicherheitsprobleme dominieren; LZ wird stark in Reparatur und
Schadensausgleich gebunden.

### fraud_stress — 🟠 Audit-/Betrugsstress
fraud_stress Reparaturquote: 63.8%. Backlogquote: 36.1%. Betrugsfälle: 927. Kriegsevents: 0.
Maximalspannung: 1.628.
Daraus folgt: Viele behauptete Lösungen werden korrigiert; die inverse Gruppenbuchung arbeitet, aber
Vertrauen und Effizienz leiden.

### scarcity_backlog — 🟡 Reparaturrückstand
scarcity_backlog Reparaturquote: 16.3%. Backlogquote: 83.7%. Betrugsfälle: 0. Kriegsevents: 0.
Maximalspannung: 2.072.
Daraus folgt: Die Wirtschaft löst Probleme, aber neue oder wachsende Probleme laufen schneller auf
als die Solver-Kapazität.

### intergalactic_latency — 🟡 Kaltkonflikt-Druck
intergalactic_latency Reparaturquote: 48.0%. Backlogquote: 52.0%. Betrugsfälle: 2. Kriegsevents: 0.
Maximalspannung: 2.167.
Daraus folgt: Es gibt keine dominierende heiße Eskalation, aber hohe Spannungen erzeugen
Sicherheits-, Vertrauens- und Governance-Kosten.


Gesamtlesart: Die TGW-Simulation belohnt nicht einfach Aktivität, sondern prüfbare Problemreduktion.
In ruhigen Szenarien kann
Solver-Kapazität offene Probleme abbauen. In Konflikt- oder Betrugsdruck-Szenarien wird die gleiche
Währung durch negative Stacks,
Audits und Reparaturfonds belastet. Dass Σbal nahe Null bleibt, ist wichtig: Die Simulation erzeugt
keine zweite verdeckte Währung,
sondern verschiebt und korrigiert LZ innerhalb der additiven Gruppe.
