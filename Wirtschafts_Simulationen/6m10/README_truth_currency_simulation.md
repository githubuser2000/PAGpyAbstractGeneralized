# Mega-Wirtschaftssimulation mit zweiter Wahrheitswährung `LOGOS`

Diese Datei beschreibt die Erweiterung von `mega_economy_sim.py` zu `mega_economy_truth_currency_sim.py`.

Die neue Simulation bleibt PyPy3-kompatibel und nutzt nur die Python-Standardbibliothek. Sie ergänzt das normale Zahlengeld `ECU` um eine zweite handelbare Währung: `LOGOS`.

## Grundidee

`LOGOS` ist kein normales Geld. Es ist eine Währung aus gestapelten Fuzzy-Wahrheitswerten.

Jede wichtige wirtschaftliche Handlung wird als logisches Prädikat interpretiert:

```text
predicate(subject, object, amount, sector, resource, time, ...)
```

Dieses Prädikat bekommt einen Fuzzy-Wahrheitswert:

```text
-1 = Lüge / falsch / zerstörerisch / nicht korrekt
 0 = unklar / neutral / ambivalent
+1 = wahr / korrekt / nachhaltig / richtig
```

Mehrere solcher Wahrheitswerte werden gestapelt. Der Stapel ist in der Simulation eine rationale Zahl (`fractions.Fraction`). Dadurch ist `LOGOS` ein alternatives Zahlenverständnis: nicht nur Menge, sondern bewertete Korrektheit.

## Was wurde eingebaut?

### 1. Zweite Währung neben ECU

Jeder Haushalt, jede Firma, jede Bank, der Staat und sogar Versicherungs-/Marktobjekte erhalten zusätzliche Konten:

- `truth_balance`
- `truth_debt`
- `truth_assets`
- `truth_reputation`
- `knowledge_balance`
- `correctness_model_quality`

Fiat-Geld bleibt erhalten. Aber Einkommen, Konsum, Kredit, Löhne, Investitionen, Steuern, Ressourcenverbrauch und Bilanzqualität erzeugen parallel eine `LOGOS`-Bewertung.

### 2. N-stellige Logikprädikate als Token

Die Klasse `LogicPredicateToken` modelliert handelbare Wahrheitstoken.

Ein Token enthält:

- `predicate`: Name des logischen Prädikats
- `terms`: beliebig viele Prädikatselemente
- `truth_value`: rationaler Fuzzy-Wahrheitswert
- `quantity`: rationale Menge
- `stack_depth`: Tiefe der gestapelten Prüfung
- `price_ecu`: Preis in ECU
- `parent_id`: Ursprungstoken bei Verifikation/Falsifikation

Verifikation fügt ein weiteres Element hinzu:

```text
correct_resource_use(firm, sector, t)
```

wird zu:

```text
correct_resource_use(firm, sector, t, verified_by=auditor:123)
```

Meta-Verifikation fügt wieder ein Element hinzu:

```text
correct_resource_use(firm, sector, t, verified_by=auditor:123, verified_by=meta_auditor:77)
```

Damit steigt die Arity des Prädikats. Genau das entspricht der Idee: Jede Überprüfung erzeugt ein logisch reichhaltigeres Prädikat.

### 3. Ressourcen- und Energie-Kontingente

Die Simulation enthält planetare Kontingente für:

```text
fossil_energy
renewable_energy
emissions
water
land
minerals
biomass
waste
```

Jedes Kontingent hat eine Fuzzy-Bewertung. Innerhalb des sicheren Bereichs ist der Wahrheitswert positiv. Bei Überschreitung fällt er bis auf `-1`.

Wenn ein Kontingent überschritten wird, sinkt der globale `resource_quota_multiplier`. Das bedeutet: Überschreitet die Wirtschaft eine Ressource stark, dann dürfen alle Akteure in der nächsten Periode auch von anderen Ressourcen deutlich weniger verbrauchen.

Das entspricht deiner Regel:

> Überschreitet man eine Energie- oder Ressourcengrenze, darf man von allen anderen Energien und Ressourcen pro Zeit nur noch sehr viel weniger verbrauchen.

### 4. Markt für Korrektheit und Richtigkeit

Firms mit hoher `truth_reputation`, positiven `truth_balance`-Werten und guter `correctness_model_quality` können Korrektheitsmodelle verkaufen.

Firms mit schlechter Ressourcenbilanz, geringer Reputation oder niedrigem Permit-Faktor kaufen diese Modelle.

Ein Handel bewirkt real:

- Käufer zahlt ECU.
- Verkäufer erhält ECU.
- Käufer erhält `LOGOS`.
- Verkäufer verliert nur einen Teil davon, weil es eher eine Lizenzierung von Wissen ist als Verbrauch eines Tokens.
- Käufer verbessert Innovation, Energieintensität, Emissionsintensität und `correctness_model_quality`.

Damit entsteht ein Markt der Richtigkeit: Wer besser wirtschaftet, kann sein Modell verkaufen. Wer schlechter wirtschaftet, muss bessere Modelle kaufen oder wird durch Ressourcenlimits, höhere Wahrheitsschulden und schlechteren Kreditzugang bestraft.

### 5. Wahrheit beeinflusst Kredit

Kreditvergabe berücksichtigt jetzt zusätzlich:

- `truth_reputation`
- `truth_debt`
- `resource_permit_factor`
- Green-Investment-Bonus

Eine Firma mit schlechter Wahrheitshistorie bekommt schwerer Kredit. Grüne Investitionen und positive Korrektheitsmodelle erhöhen die Chance.

### 6. Wissen und Bildung sind handelbar

Haushalte und Firmen besitzen `knowledge_balance`. Bildung erzeugt Wahrheitstoken. Bildungsgewinne werden als verifizierbare Wissenswerte gebucht.

Das bedeutet: Wissen ist nicht nur Humankapital im Hintergrund, sondern ein handelbarer und bilanziell sichtbarer Wahrheitsbestand.

### 7. Bilanzen besitzen Wahrheit

Banken, Haushalte, Firmen und Staat haben neben Geldbilanzen auch Wahrheitsbilanzen.

Beispiele:

- Eine Bank mit schlechter Kreditqualität erhält negative Wahrheit.
- Ein Kreditdefault falsifiziert frühere Kreditprädikate.
- Eine nachhaltige Investition mintet positive Wahrheit.
- Eine Insolvenz erzeugt Wahrheitsschuld.
- Der Staat bekommt Wahrheit für planetare Stewardship und verliert Wahrheit bei Ressourcenüberschreitungen.

## Neue CLI-Parameter

```bash
--truth-currency-name LOGOS
--no-truth-market
--truth-initial-price 1.0
--truth-verification-rate 0.18
--truth-meta-verification-rate 0.045
--truth-max-predicates 8000
--truth-resource-strictness 1.0
--truth-lockdown-strength 0.72
--truth-credit-weight 0.32
--truth-tax-rate 0.035
--truth-wage-share 0.020
--truth-trade-intensity 1.0
```

## Beispielstart

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 60 --households 300 --firms 80 --banks 5 \
  --scenario baseline \
  --out truth_baseline.csv \
  --json truth_baseline_summary.json
```

## Strengere planetare Regeln

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 80 --households 400 --firms 120 --banks 6 \
  --scenario climate_transition \
  --policy green \
  --truth-resource-strictness 1.6 \
  --truth-lockdown-strength 0.9 \
  --out strict_green.csv \
  --json strict_green_summary.json
```

## Markt für Korrektheitsmodelle stärker machen

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 80 --households 400 --firms 120 --banks 6 \
  --truth-trade-intensity 2.5 \
  --truth-credit-weight 0.5 \
  --out correctness_market.csv \
  --json correctness_market_summary.json
```

## Szenariovergleich

```bash
pypy3 mega_economy_truth_currency_sim.py \
  --steps 50 --households 250 --firms 80 --banks 5 \
  --compare baseline energy_shock climate_transition financial_crisis ai_automation \
  --out truth_scenario_comparison.csv \
  --json truth_scenario_comparison.json
```

## Wichtige neue Output-Metriken

```text
truth_price_ecu
truth_supply
truth_last_issued
truth_last_destroyed
truth_trade_volume
truth_trade_volume_ecu
truth_model_trade_volume_ecu
truth_verifications
truth_falsifications
truth_predicates_created
truth_token_count
truth_avg_predicate_arity
truth_market_correctness_index
planet_integrity
resource_quota_multiplier
resource_breach_count
resource_worst_excess
resource_avg_truth
truth_household_avg_balance
truth_household_gini
truth_firm_avg_balance
truth_firm_gini
truth_bank_avg_balance
truth_government_balance
truth_firm_avg_reputation
truth_household_avg_reputation
knowledge_household_avg
correctness_model_quality_avg
resource_usage_<resource>
resource_allowance_<resource>
resource_ratio_<resource>
resource_truth_<resource>
```

## Eingebaute Szenarien

```text
baseline
energy_shock
supply_chain_break
financial_crisis
housing_boom_bust
climate_transition
protectionism
ai_automation
austerity
stimulus
pandemic_like
stagflation_combo
```

## Wichtige Designentscheidung

Die Simulation behandelt Wahrheit nicht als Moralpredigt, sondern als ökonomisch wirksame Bilanzgröße.

Wer korrekt, ressourcenschonend, stabil und wissensproduktiv wirtschaftet, kann daraus ein handelbares Modell machen. Wer Ressourcen überschreitet oder falsche Bilanzmodelle produziert, erzeugt Wahrheitsschuld. Dadurch entsteht Konkurrenz um Korrektheit statt nur Konkurrenz um Gewinn.

## Einschränkung

Alle Zahlen sind stilisiert. Das Modell ist ein kausales Forschungslabor, keine empirisch kalibrierte Vorhersagemaschine. Für echte Politik- oder Unternehmensentscheidungen müssten Ressourcenintensitäten, Quoten, Kreditparameter und Verifikation aus Daten kalibriert werden.
