# Mega-Wirtschaftssimulation mit zweiter Prädikat-Wahrheitswährung

Diese Erweiterung baut auf der vorhandenen Datei `mega_economy_sim.py` auf und ergänzt sie durch eine zweite handelbare Währung: `TCR`, eine rationalwertige Stapelung von Fuzzy-Wahrheitswerten aus n-stelligen Logikprädikaten.

Die alte Währung bleibt normales Zahlengeld (`ECU`). Die neue Währung misst nicht bloß Gewinn, sondern die **Korrektheit wirtschaftlicher Aktivität**: Ressourcendisziplin, Energiedisziplin, planetare Belastbarkeit, Bilanzwahrheit, Verifikation, Wissen, Bildung und langfristige Güte von Marktmodellen.

## Dateien

- `mega_economy_sim.py` – ursprüngliche große Wirtschafts-Simulation.
- `mega_economy_sim_truth_currency.py` – neue Erweiterung mit zweiter Währung und Wahrheits-/Ressourcenmarkt.
- `sample_truth_currency.csv` – Beispiel-Zeitreihe.
- `sample_truth_currency_summary.json` – Beispiel-Endauswertung.
- `sample_truth_currency_comparison.csv` – kleiner Szenariovergleich.
- `sample_truth_currency_comparison.json` – JSON-Version des Szenariovergleichs.

Beide Python-Dateien müssen im selben Ordner liegen, weil die Erweiterung die alte Simulation importiert.

## Grundidee der zweiten Währung

Jeder größere Geldfluss wird zusätzlich als Logikprädikat bewertet. Beispiel:

```text
credit_contract_predicate(borrower, bank, collateral, purpose, t)
```

Dieses Prädikat erhält mehrere Fuzzy-Wahrheitswerte im Bereich `[-1, 1]`:

- `-1` bedeutet: falsifiziert, falsch, Lüge, nicht korrekt.
- `0` bedeutet: unklar, neutral oder ambivalent.
- `1` bedeutet: verifiziert, wahr, korrekt.

Mehrere Wahrheitswerte werden gestapelt und mit `fractions.Fraction` als rationale Zahl gespeichert. Dadurch ist eine Zahl in dieser Simulation nicht nur ein Skalar, sondern ein Stapel geprüfter Aussagen.

Wenn ein Wahrheitswert geprüft wird, steigt die Prädikat-Arity. Wird die Prüfung selbst geprüft, steigt sie erneut. Das Modell bildet also ab:

```text
P(x1, x2, x3)                         # Ausgangsprädikat, arity 3
P(x1, x2, x3, verifier)               # Verifikation, arity 4
P(x1, x2, x3, verifier, metaVerifier) # Verifikation der Verifikation, arity 5
```

## Neue simulierte Mechanismen

Die Erweiterung enthält unter anderem:

- zweite handelbare Währung `TCR`;
- Wahrheitsguthaben und Wahrheitsschulden für Haushalte, Firmen, Banken und Staat;
- n-stellige Logikprädikate für Einkommen, Konsum, Kredite, Bilanzen, Marktumsätze, Steuern und Ressourcen;
- exakte rationale Darstellung gestapelter Fuzzy-Bits;
- Ressourcen- und Energie-Kontingente mit fuzzy erlaubten Bereichen;
- harte Folgewirkung bei Überschreitung: wenn ein Ressourcenkontingent überzogen wird, wird der Zugriff auf alle Ressourcen in späteren Perioden gedrosselt;
- Markt für Wahrheitswährung;
- Markt für Korrektheitsmodelle, also handelbare Modelle erfolgreichen und planetarisch korrekten Wirtschaftens;
- Verifikation, Falsifikation und Meta-Verifikation;
- handelbares Wissen und Bildung über Prädikate;
- Bilanzwahrheit für Banken und Firmen;
- Einfluss von TCR auf Kreditgenehmigung, Kreditpreis, Investitionsqualität, Ressourcen-Zugang und Reputation.

## Start

```bash
pypy3 mega_economy_sim_truth_currency.py --quiet \
  --out truth.csv \
  --json truth_summary.json
```

Falls PyPy3 nicht installiert ist, läuft es auch mit CPython:

```bash
python3 mega_economy_sim_truth_currency.py --quiet \
  --out truth.csv \
  --json truth_summary.json
```

## Größerer Lauf

```bash
pypy3 mega_economy_sim_truth_currency.py \
  --steps 120 \
  --households 800 \
  --firms 160 \
  --banks 8 \
  --scenario truth_currency_transition \
  --policy green \
  --out truth_transition.csv \
  --json truth_transition_summary.json
```

## Szenariovergleich

```bash
pypy3 mega_economy_sim_truth_currency.py \
  --steps 40 \
  --households 300 \
  --firms 80 \
  --banks 5 \
  --compare baseline truth_currency_transition planetary_overshoot greenwashing_crackdown knowledge_commons climate_transition \
  --out truth_comparison.csv \
  --json truth_comparison.json
```

## Neue Wahrheitsszenarien

Zusätzlich zu den alten Szenarien der Basissimulation gibt es neue Truth-Currency-Szenarien:

```text
truth_currency_transition
planetary_overshoot
greenwashing_crackdown
knowledge_commons
```

Diese lassen sich auch mit alten Schocks kombinieren:

```bash
pypy3 mega_economy_sim_truth_currency.py \
  --scenario truth_currency_transition \
  --compound energy_shock,financial_crisis,climate_transition \
  --steps 100 \
  --out compound_truth.csv \
  --json compound_truth.json
```

## Wichtige neue Parameter

```text
--truth-currency-name              Name der zweiten Währung, Standard: TCR
--disable-truth-currency           Truth-Currency-Schicht deaktivieren
--truth-initial-price              Anfangspreis in ECU je TCR
--truth-market-intensity           Stärke, mit der Geldflüsse TCR erzeugen oder vernichten
--truth-verification-intensity     Stärke der Verifikation/Falsifikation
--truth-resource-strictness        Härte der Ressourcen-Drosselung bei Überschreitung
--truth-trade-fraction             Anteil des Truth-Guthabens, der handelbar wird
--truth-meta-verification-rate     Wahrscheinlichkeit einer Verifikation der Verifikation
--truth-min-credit-score           Mindest-Truth-Score für günstigere Kreditvergabe
--truth-quota-scale                Skalierung der Ressourcen-Kontingente
--truth-audit-sample               Anzahl geprüfter Agenten pro Periode
--truth-print-events               Ressourcen-/Truth-Events ausführlicher loggen
```

## Neue Metriken im CSV

Wichtige zusätzliche Spalten:

```text
truth_price_ecu
truth_currency_supply
truth_debt_total
truth_net_supply
truth_trade_volume
truth_trade_volume_ecu
truth_positive_issued_total
truth_negative_issued_total
truth_planetary_score
truth_resource_throttle
truth_max_resource_overshoot
truth_avg_firm_score
truth_avg_household_score
truth_avg_bank_score
truth_avg_predicate_arity
truth_avg_verification_depth
truth_verification_count
truth_falsification_count
truth_meta_verification_count
truth_model_count
truth_model_top_quality
truth_model_concentration
resource_use_<resource>
resource_truth_<resource>
resource_overshoot_<resource>
```

## Interpretationslogik

Ein Unternehmen kann in ECU profitabel sein, aber TCR verlieren, wenn es seine Gewinne durch Ressourcenübernutzung, schlechte Bilanzwahrheit, schlechte Löhne, emissionsintensive Produktion oder falsifizierte Korrektheitsbehauptungen erzielt.

Ein Unternehmen kann TCR gewinnen, wenn es profitabel und zugleich ressourcenschonend, bilanzklar, innovationsfähig, lohnfair und überprüfbar korrekt wirtschaftet.

Das ist der Kern der Simulation: Es gibt nicht nur Konkurrenz um Profit, sondern Konkurrenz um **verifizierte wirtschaftliche Richtigkeit**.

## Ressourcenlogik

Die Simulation verfolgt unter anderem:

```text
energy_total
fossil_energy
emissions
materials
water
land
waste
biodiversity_pressure
compute_energy
housing_land
```

Jede Ressource hat fuzzy erlaubte Bereiche. Wenn die Nutzung im idealen Bereich bleibt, ist der Ressourcen-Wahrheitswert nahe `1`. Bei Überschreitung fällt er Richtung `-1`. Wird eine Ressource zu stark überschritten, sinkt `truth_resource_throttle`. Dieser Faktor wirkt als Drosselung auf das gesamte System.

## Handelbare Korrektheitsmodelle

Firmen besitzen Korrektheitsmodelle. Diese Modelle haben:

- Qualität;
- Verifikationstiefe;
- Arity;
- Marktanteil;
- Preis in ECU;
- TCR-Vermögen.

Andere Firmen können bessere Modelle kaufen oder kopieren. Dadurch wird Korrektheit selbst wettbewerblich: Nicht nur Produkte konkurrieren, sondern auch Modelle, wie korrekt man produziert, bilanziert, lernt und Ressourcen nutzt.

## Grenzen

Das Modell ist bewusst stilisiert. Es ist kein empirisches Prognosemodell. Es ist ein Mechanismenlabor, um zu testen, wie eine zweite Währung für Wahrheit, Verifikation und planetare Ressourcenrichtigkeit mit klassischen Märkten interagieren könnte.
