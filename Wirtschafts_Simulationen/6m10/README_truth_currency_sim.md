# Mega-Wirtschaftssimulation mit handelbarer Fuzzy-Wahrheitswährung

Diese Version erweitert die bisherige PyPy3-kompatible Wirtschaftssimulation um eine zweite Währung namens `LOGOS`. `LOGOS` ist keine normale Zahlgeld-Währung, sondern eine handelbare, rationale Wahrheits-/Richtigkeitswährung.

## Kernidee

Jeder relevante Geldfluss kann zusätzlich als n-stelliges Logikprädikat modelliert werden:

```text
P(element_1, element_2, ..., element_n) -> fuzzy truth in [-1, 1]
```

Dabei bedeutet:

- `-1`: Lüge, falsche oder planetarisch schädliche Wirtschaftsweise
- `0`: unklar, neutral oder nicht ausreichend verifiziert
- `1`: wahr, korrekt, ressourcenschonend, langfristig richtig

Die Simulation stapelt diese fuzzy Truth Bits als rationale Zahlen (`fractions.Fraction`). Dadurch entsteht eine zweite Währung, deren Einheiten nicht einfach „Geld“, sondern verifizierbare Richtigkeitsansprüche sind.

## Was wurde eingebaut?

### 1. Zweite Währung `LOGOS`

Alle großen Zahlgeldflüsse können zusätzlich Wahrheitseinheiten erzeugen oder zerstören:

- Konsum
- Löhne
- Steuern
- Transfers
- Renten
- Hypotheken
- Kredite
- Schuldendienst
- Kreditausfälle
- Investitionen
- Exporte und Importe
- Plattformgebühren
- Versicherungsprämien und Auszahlungen
- CO₂-/Carbon-Zahlungen
- Bank-Bailouts
- Firmeninsolvenzen

Ein Fiat-Geldfluss erzeugt ein Prädikat wie:

```text
MoneyFlowIsRight(subject, counterparty, amount, purpose, truth_price, planetary_stress, t)
```

Aus diesem Prädikat wird ein rationaler Truth-Stack berechnet:

```text
currency_value = fuzzy_truth * confidence * arity / (verification_depth + 1)
```

Die Fiat-Menge wird logarithmisch skaliert, damit große Geldflüsse nicht automatisch alle Wahrheitsmärkte dominieren.

### 2. Verifikation und Falsifikation

Ein Prädikat kann überprüft werden. Jede Überprüfung fügt ein weiteres Element hinzu. Dadurch wird aus einem n-stelligen Prädikat ein n+1-stelliges Prädikat.

Beispiel:

```text
MoneyFlowIsRight(firm:7, household:21, wage, amount, t)
```

wird nach Audit zu:

```text
MoneyFlowIsRight.verified(firm:7, household:21, wage, amount, t, verification_by=bank:2)
```

Eine weitere Prüfung der Prüfung erhöht die Arity erneut. Das entspricht deiner Idee: Verifikation/Falsifikation ist selbst wieder ein logisches Element und kann erneut überprüft werden.

### 3. Ressourcen- und Energie-Kontingente

Die Simulation verfolgt mehrere planetarische Ressourcen:

```text
fossil_energy
renewable_energy
carbon_budget
water
materials
land
biodiversity
waste_capacity
labor_attention
data_privacy
```

Für jede Ressource gibt es:

- aktuelle Nutzung
- erlaubtes Kontingent
- fuzzy truth range
- lokale Akteursbewertung
- globale Systembewertung

Wenn eine Ressource außerhalb ihres erlaubten fuzzy truth Bereichs liegt, wird nicht nur diese Ressource sanktioniert. Die Simulation aktiviert dann eine Cross-Resource-Sanktion:

```text
truth_cross_resource_throttle
```

Dieser Wert reduziert die erlaubte Nutzung aller Ressourcen und Energien pro Zeitschritt. Das modelliert die Idee: Wer eine planetarische Grenze reißt, darf von allem anderen sehr viel weniger verbrauchen.

### 4. Markt für Richtigkeit und Korrektheit

`LOGOS` ist handelbar. Firmen mit hoher Richtigkeitsbilanz und guten Modellen können Truth-Stacks verkaufen. Firmen mit schlechter Ressourcenbilanz kaufen Truth-Einheiten, bessere Modelle oder Wissen.

Der Markt handelt nicht nur Tokens, sondern auch:

- Korrektheitsmodelle
- Ressourcen-Effizienzmodelle
- Bildungs-/Wissensansprüche
- Verifikationsleistungen
- Bilanz-Audits
- reputationsbasierte Kreditwürdigkeit

Dadurch entsteht Konkurrenz um korrektes Wirtschaften. Nicht nur maximaler Gewinn zählt, sondern auch die Frage, ob ein Akteur glaubwürdig, ressourcenschonend, überprüfbar und langfristig planetarisch tragfähig wirtschaftet.

## Neue Metriken

Die CSV-Ausgabe enthält zusätzlich unter anderem:

```text
truth_price
truth_correctness_index
truth_planetary_stress
truth_cross_resource_throttle
truth_trade_volume
truth_fiat_volume
truth_model_trade_volume
truth_knowledge_trade_volume
truth_verifications
truth_predicates_created
truth_total_predicates
truth_total_verifications
truth_household_mean
truth_firm_mean
truth_bank_mean
truth_government_balance
truth_model_competition
truth_audit_pressure
truth_adjusted_welfare
truth_resource_use_<resource>
truth_resource_truth_<resource>
truth_resource_limit_<resource>
```

## Start

```bash
pypy3 mega_economy_truth_currency_sim.py --quiet --out truth_baseline.csv --json truth_baseline.json
```

Falls PyPy3 nicht installiert ist, läuft der Code auch mit CPython:

```bash
python3 mega_economy_truth_currency_sim.py --quiet --out truth_baseline.csv --json truth_baseline.json
```

## Größerer Lauf

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 120 \
  --households 800 \
  --firms 160 \
  --banks 8 \
  --scenario climate_transition \
  --policy green \
  --out climate_truth.csv \
  --json climate_truth_summary.json
```

## Strenger planetarischer Ressourcenmodus

Je höher `--truth-resource-strictness`, desto enger die Ressourcen-Kontingente:

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 80 \
  --households 500 \
  --firms 120 \
  --scenario energy_shock \
  --truth-resource-strictness 1.8 \
  --out strict_energy_truth.csv \
  --json strict_energy_truth.json
```

Wenn Kontingente verletzt werden, fällt `truth_cross_resource_throttle` stark. Dann sinkt die zulässige Nutzung aller Ressourcen pro Zeitschritt.

## Szenariovergleich

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 60 \
  --households 300 \
  --firms 80 \
  --banks 5 \
  --compare baseline energy_shock climate_transition ai_automation financial_crisis \
  --out truth_comparison.csv \
  --json truth_comparison.json
```

## Neue CLI-Parameter

```text
--truth-currency-name LOGOS
--disable-truth-market
--truth-money-scale 80.0
--truth-resource-strictness 1.0
--truth-verification-depth 3
--truth-public-audit-rate 0.055
--truth-trade-intensity 0.18
--truth-cross-resource-penalty 0.78
--truth-to-fiat-fx 1.0
```

## Interpretation

Diese Simulation ist kein empirisches Prognosemodell. Sie ist ein Mechanik-Labor. Der entscheidende Unterschied zur ursprünglichen Version ist:

```text
Altes Modell:
    Wer profitabel ist, kann wachsen.

Erweitertes Modell:
    Wer profitabel, ressourcenschonend, überprüfbar, wissensstark und planetarisch korrekt wirtschaftet, erhält zusätzlich LOGOS-Reputation, bessere Kreditbedingungen, handelbare Modellwerte und langfristige Marktvorteile.
```

Das Modell schafft damit einen Markt, in dem Korrektheit selbst zur knappen, handelbaren und überprüfbaren ökonomischen Ressource wird.
