# Mega-Wirtschaftssimulation mit drei Währungen: Fiat, LOGOS und ARETE

Diese Version erweitert die vorherige `LOGOS`-Simulation um eine dritte handelbare Währung: **ARETE**, eine Winkel-/Moral-Währung.

Die Simulation bleibt Standard-Library-only und ist für **PyPy3** ausgelegt.

## Download-Dateien im Paket

- `mega_economy_angle_truth_currency_sim.py`  
  Die erweiterte PyPy3-kompatible Simulation.
- `sample_angle_truth_baseline.csv`  
  Beispiel-Zeitreihe eines Baseline-Laufs.
- `sample_angle_truth_baseline_summary.json`  
  Zusammenfassung des Beispiel-Baseline-Laufs.
- `sample_angle_truth_comparison.csv`  
  Beispiel-Szenariovergleich.
- `sample_angle_truth_comparison.json`  
  Zusammenfassung des Beispiel-Szenariovergleichs.

## Die drei Währungen

### 1. Fiat

Die bisherige normale Geldwährung bleibt erhalten:

- Haushalte besitzen `cash`, Schulden, Hypotheken, Portfolios.
- Firmen besitzen `cash`, Kapital, Schulden, Umsätze, Kosten.
- Banken besitzen Reserven, Einlagen, Eigenkapital und Kreditbücher.
- Staat besitzt Einnahmen, Ausgaben, Defizite und Schulden.

Fiat misst weiterhin Liquidität, Kaufkraft, Preise, Löhne, Gewinne und Zahlungsfähigkeit.

### 2. LOGOS

`LOGOS` ist die bereits eingeführte Wahrheits-/Richtigkeitswährung.

Jeder relevante Geldfluss kann als n-stelliges Fuzzy-Logikprädikat dargestellt werden:

```text
MoneyFlowIsRight(subject, counterparty, amount, purpose, resource_state, time, ...)
```

Der Wahrheitswert liegt zwischen:

```text
-1 = Lüge / falsch / schädlich
 0 = unbestimmt / ambivalent
 1 = wahr / richtig / korrekt
```

Die gestapelten Wahrheitswerte werden mit `fractions.Fraction` als rationale Zahlen gespeichert.

Verifikation/Falsifikation erhöht die Prädikat-Arity:

```text
n -> n+1 -> n+2 -> ...
```

Dadurch werden Wissen, Audits, Bildung, Bilanzprüfung, Ressourcenrichtigkeit und Markterfolgsmodelle handelbar.

### 3. ARETE

`ARETE` ist die neue Winkelwährung.

Sie modelliert nicht nur Wahrheit, sondern eine geometrische Marktethik.

Zwei Volkswirtschaften/Länder setzen unterschiedliche Güte-Referenzen:

```text
Land A: gutmütig bei 0°
Land B: gutmütig bei 90°
gemeinsames synthetisches Gutes: 45°
Böse, als Gegenseite des Guten: 225°
Beliebt: 135°
Unbeliebt: 315°
```

Damit entstehen zwei Achsen:

```text
Gut/Böse:           45° <-> 225°
Beliebt/Unbeliebt: 135° <-> 315°
```

Ein Marktgegenstand erhält einen Winkel. Beispiele:

- Arbeit / Löhne liegen nahe am gemeinsamen Guten.
- Bildung, Gesundheit, Wissen und Audits liegen nahe am Guten.
- Fossile Energie, Emissionen und Defaults werden Richtung Böse gezogen.
- Plattform-/Datenrenten können Richtung beliebt, aber nicht notwendigerweise gut kippen.
- Renten und Immobilien können gut oder schlecht werden, je nach Erschwinglichkeit.
- Ressourcenverbrauch wird über Ressourcenwinkel und planetare Stresswerte bewertet.

## Gute als Zahl

Die Simulation rechnet das Gute als Teil des Halbkreisumfangs zwischen Böse und Gut.

Bei Radius 1 gilt:

```text
maximaler Halbkreisumfang = pi
```

In der Simulation:

```python
good_fraction = 1 - angular_distance(angle, 45°) / 180
good_circumference = pi * good_fraction
```

Das heißt:

```text
45°   -> maximal gut, voller Halbkreisumfang
225°  -> böse, 0 guter Halbkreisumfang
135°  -> orthogonal, beliebt/unbeliebt-Achse
315°  -> orthogonal, Gegenpol beliebt/unbeliebt
```

## Wie ARETE entsteht

Fiat-Geldflüsse erzeugen zusätzlich ARETE-Ereignisse.

LOGOS-Ausgaben und LOGOS-Transfers erzeugen ebenfalls ARETE-Ereignisse.

Ressourcenverbrauch erzeugt ebenfalls ARETE-Ereignisse.

Ein Ereignis speichert unter anderem:

```text
subject
counterparty
amount
currency_context
purpose
object_angle
subject_angle
counterparty_angle
state_a_good
state_b_good
objective_good
evil_angle
popular_axis
unpopular_axis
good_circumference
good_evil_coordinate
popularity_coordinate
truth_hint
units
```

Damit ist jeder Geldfluss auch ein Winkelobjekt.

## Was ARETE ökonomisch beeinflusst

ARETE ist nicht nur Berichtswert, sondern wirkt zurück auf die Simulation:

- Firmen mit besserem ARETE-Ruf bekommen produktivere Ressourcenbedingungen.
- Banken berücksichtigen ARETE beim Kreditrating.
- Haushalte mit besserem ARETE-Ruf bekommen bessere Kreditwahrscheinlichkeiten.
- Schlechte Winkelpositionen erzeugen `angle_debt`.
- Firmen können ARETE handeln.
- Firmen können Winkel-Korrektheitsmodelle kaufen.
- Winkelmodelle können Firmen näher an das gemeinsame 45°-Gute bewegen.
- Ressourcenübernutzung verschiebt Akteure Richtung Böse und senkt ihre langfristige Wettbewerbsfähigkeit.

## Neue zentrale Metriken

Die Simulation schreibt zusätzlich unter anderem:

```text
angle_price
angle_market_alignment
angle_popularity_index
angle_polarization_index
angle_trade_volume
angle_fiat_volume
angle_model_trade_volume
angle_events_created
angle_total_events
angle_units_issued_step
angle_units_destroyed_step
angle_total_units_issued
angle_total_units_destroyed
angle_moral_arbitrage_volume
angle_household_mean
angle_firm_mean
angle_bank_mean
angle_government_balance
angle_mean_actor_goodness
angle_objective_good_deg
angle_evil_deg
angle_popular_axis_deg
angle_unpopular_axis_deg
angle_model_competition
truth_angle_adjusted_welfare
```

Besonders wichtig:

```text
angle_market_alignment
```

misst, wie nah die jüngsten Marktgegenstände am gemeinsamen Guten liegen.

```text
angle_polarization_index
```

misst, wie weit Märkte vom gemeinsamen Guten wegdriften.

```text
angle_popularity_index
```

misst die Position auf der beliebt/unbeliebt-Achse.

## Start

```bash
pypy3 mega_economy_angle_truth_currency_sim.py \
  --quiet \
  --out angle_baseline.csv \
  --json angle_baseline_summary.json
```

## Größerer Lauf

```bash
pypy3 mega_economy_angle_truth_currency_sim.py \
  --steps 120 \
  --households 800 \
  --firms 160 \
  --banks 8 \
  --scenario climate_transition \
  --policy green \
  --out angle_climate.csv \
  --json angle_climate_summary.json
```

## Szenariovergleich

```bash
pypy3 mega_economy_angle_truth_currency_sim.py \
  --steps 50 \
  --households 300 \
  --firms 80 \
  --banks 5 \
  --compare baseline energy_shock financial_crisis climate_transition ai_automation \
  --out angle_comparison.csv \
  --json angle_comparison.json
```

## Schocks kombinieren

```bash
pypy3 mega_economy_angle_truth_currency_sim.py \
  --scenario baseline \
  --compound energy_shock,financial_crisis,supply_chain_break
```

## Neue CLI-Parameter für ARETE

```text
--angle-currency-name ARETE
--disable-angle-market
--angle-money-scale 42.0
--angle-trade-intensity 0.14
--angle-to-fiat-fx 1.0
--angle-state-a-good 0.0
--angle-state-b-good 90.0
--angle-objective-good 45.0
--angle-popularity-weight 0.22
--angle-truth-weight 0.42
--angle-resource-weight 0.35
--angle-moral-credit-bonus 0.020
```

## Interpretation

Diese dritte Währung macht aus Märkten keine reine Gewinnkonkurrenz mehr.

Es gibt jetzt drei unterschiedliche Rechenebenen:

```text
Fiat  = Zahlungsfähigkeit und Preis
LOGOS = Wahrheit, Richtigkeit, Verifizierbarkeit
ARETE = Winkelposition des Marktgegenstands im Raum Gut/Böse und Beliebt/Unbeliebt
```

Ein Unternehmen kann also:

- Fiat-reich, aber LOGOS-arm sein.
- LOGOS-reich, aber ARETE-verschuldet sein.
- ARETE-reich, aber kurzfristig Fiat-arm sein.
- beliebt, aber nicht gut sein.
- gut, aber unbeliebt sein.
- nahe an 45° liegen und dadurch langfristig bessere systemische Bedingungen erhalten.

Der Markt der Richtigkeit wird dadurch nicht nur ein Wahrheitsmarkt, sondern ein **geometrischer Korrektheitsmarkt**.

## Technischer Hinweis

Die Simulation ist absichtlich groß und mechanistisch breit. Sie ist kein empirisch kalibriertes Prognosemodell.

Sie ist ein Experimentierlabor für Fragen wie:

- Welche Marktgegenstände bewegen eine Wirtschaft vom Guten weg?
- Was passiert, wenn zwei Länder unterschiedliche Gütereferenzsysteme haben?
- Kann ein handelbarer Richtigkeits-/Winkelmarkt Ressourcenverbrauch langfristig senken?
- Wann wird Beliebtheit zur Konkurrenz des Guten?
- Welche Firmen werden reich in Fiat, LOGOS und ARETE gleichzeitig?
- Wie verändern Wahrheit, Wissen, Audits, Bildung und Ressourcenrechte die Kredit- und Produktionsdynamik?
