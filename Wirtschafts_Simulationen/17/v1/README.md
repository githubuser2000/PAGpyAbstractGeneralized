# Q-Wirtschaftssimulation für PyPy3

Dies ist eine ausführbare Wirtschaftssimulation auf Basis der Q-Münzenwährung.

Die Simulation behandelt die Q-Münzen nicht als normale Zahlwährung, sondern als **semantische Wert- und Schuldenvektoren**:

- `Q1` bis `Q4` haben Münzwert 1.
- `Q5` bis `Q9` haben Münzwert 2.
- `Q10` bis `Q16` haben Münzwert 3.
- `Q17` bis `Q20` haben Münzwert 4.
- Positive Bestände sind Vermögen.
- Negative Bestände sind Schulden.
- Gleicher Nominalwert heißt nicht gleiche Funktion: `4 × Q1` und `1 × Q20` sind nominal gleich, aber semantisch verschieden.

Das Modell bildet nicht nur KI-, Software- oder Intelligenzarbeit ab, sondern eine ganze Volkswirtschaft mit Landwirtschaft, Rohstoffen, Energie, Industrie, Bau, Gesundheit, Bildung, Logistik, Handel, Finanzwesen, öffentlichem Dienst, Kultur, Gastgewerbe, Wartung, Software/KI, Forschung, Umwelt und Sicherheit.

## Schnellstart

```bash
cd q_economy_sim_pypy3
pypy3 run_simulation.py --periods 120 --scenario balanced --out output_balanced --progress
```

Falls `pypy3` nicht installiert ist, läuft das Projekt auch mit normalem Python 3:

```bash
python3 run_simulation.py --periods 120 --scenario balanced --out output_balanced --progress
```

## Beispiel: Szenariovergleich

```bash
pypy3 tools/compare_scenarios.py --periods 80 --households 250 --firms 70 --banks 4 --out scenario_runs
```

## Ausgabeberichte

Ein Simulationslauf erzeugt im Ausgabeordner:

| Datei | Inhalt |
|---|---|
| `summary.md` | lesbarer Ergebnisbericht |
| `time_series.csv` | alle Periodenkennzahlen |
| `q_balances.csv` | positive Q-Bestände, Q-Schulden und Knappheit je Münze |
| `sector_report.csv` | Sektoren, Produktion, Preise, Kapital, Schulden |
| `labor_report.csv` | Arbeitstypen, Beschäftigung, Löhne |
| `agents_snapshot.csv` | Haushalte, Firmen, Banken, Staat, Außenwelt am Ende |
| `final_state.json` | kompakte Endauswertung |
| `events.json` | Ereignisprotokoll: Krisen, Defaults, öffentliche Jobs usw. |
| `run_config.json` | verwendete Parameter |

## Szenarien

```bash
pypy3 run_simulation.py --list-scenarios
```

Vorhandene Szenarien:

- `balanced` – ausgewogene Startwirtschaft.
- `code_bubble` – Software/KI boomt, aber Q10/Q16/Q18-Schulden entstehen.
- `energy_crisis` – Energieproduktion ist gedrückt.
- `food_crisis` – Nahrungsschock.
- `architecture_crisis` – Q18-Architektur ist knapp.
- `automation_wave` – Automatisierung wächst stark, Arbeitsmarkt wird verdrängt.
- `public_investment` – Staat erhöht Bildung, Infrastruktur, Gesundheit und Gemeingüter.
- `austerity` – Sparpolitik.
- `climate_shock` – Klima-/Resilienzschock.

## Wichtige Kommandozeilenparameter

```bash
pypy3 run_simulation.py \
  --periods 120 \
  --seed 42 \
  --households 300 \
  --firms 80 \
  --banks 4 \
  --scenario balanced \
  --out output_balanced \
  --progress
```

Parameter:

| Parameter | Bedeutung |
|---|---|
| `--periods` | Anzahl Simulationsperioden |
| `--seed` | Zufalls-Seed für reproduzierbare Läufe |
| `--households` | Anzahl Haushalte |
| `--firms` | Anzahl Firmen |
| `--banks` | Anzahl Banken |
| `--scenario` | Szenarioauswahl |
| `--out` | Ausgabeordner |
| `--progress` | Fortschritt auf der Konsole anzeigen |

## Modellbestandteile

### Agenten

- Haushalte mit Gesundheit, Bildung, Zufriedenheit, Fähigkeiten, Arbeitsangebot, Konsum und Q-Wallet.
- Firmen mit Sektor, Preisen, Kapitalstock, Automatisierung, Inputs, Produktion, Inventar, Q-Schulden und Reputation.
- Banken mit Kreditbuch, Risikoprüfung, Zinsen, Kreditausfällen und Kapitalpuffer.
- Staat mit Steuern, Transfers, öffentlichem Einkauf, Gemeingüterbestand, Jobprogramm und automatischer Stabilisierung.
- Rest der Welt mit Exportnachfrage und begrenztem Importpuffer.
- Münzamt mit Validierung und Q-Münzprägung.

### Märkte

- Arbeitsmarkt für alle Arbeitstypen.
- Gütermarkt für Konsum, Inputs, öffentliche Nachfrage und Exporte.
- Kreditmarkt mit Banken, Zinsen, Laufzeiten, Ausfällen und Restrukturierung.
- Q-Markt mit Knappheit, semantischen Ersatzbeziehungen und Schuldreparatur.

### Arbeitstypen

Die Simulation umfasst unter anderem:

- einfache körperliche Arbeit
- Landwirtschaft
- Rohstoffarbeit
- Energiearbeit
- Industriearbeit
- Handwerk
- Bauarbeit
- Logistik
- Handel
- Gastgewerbe
- Pflege
- Gesundheit
- Bildung
- Forschung
- Software/KI/Automatisierung
- Ingenieurwesen
- Wartung
- Finanzwesen
- Recht/Verträge
- kreative Arbeit
- öffentlicher Dienst
- Sicherheit
- Umweltarbeit
- Management/Organisation

### Güter und Sektoren

Die Sektoren erzeugen Güter und Dienste wie Nahrung, Rohstoffe, Energie, Industriegüter, Wohnraum, Gesundheit, Bildung, Transport, Handel, Finanzdienste, öffentliche Leistungen, Kultur, Gastgewerbe, Wartung, Automatisierung, Wissen, Umweltleistung und Sicherheit.

## Q-Logik im Code

Die wichtigsten Klassen:

| Datei | Inhalt |
|---|---|
| `qsim/money.py` | Q-Münzen, Wallets, Schulden, Münzamt |
| `qsim/sectors.py` | Arbeitstypen, Güter, Sektoren, Produktionsrezepte |
| `qsim/agents.py` | Haushalte, Firmen, Banken, Staat |
| `qsim/markets.py` | Arbeitsmarkt, Gütermarkt, Q-Markt |
| `qsim/finance.py` | Kredite, Zinsen, Defaults |
| `qsim/simulation.py` | Hauptablauf der Volkswirtschaft |
| `qsim/reporting.py` | CSV/JSON/Markdown-Berichte |
| `qsim/cli.py` | Kommandozeile |

## Smoke-Test

```bash
pypy3 tests/test_smoke.py
```

## Hinweise zur Interpretation

Die Simulation ist kein Prognosemodell für reale Volkswirtschaften. Sie ist ein exploratives, agentenbasiertes Modell der Q-Währungsidee.

Besonders wichtig sind diese Kennzahlen:

- `total_positive_money_value`: positiver Q-Bestand.
- `total_debt_value`: gesamte Q-Schuld.
- `q16_debt_value`: Betriebsschuld.
- `q18_debt_value`: Architekturschuld.
- `q20_debt_value`: Modul-/Maschinenschuld.
- `unemployment_rate`: Arbeitslosigkeit.
- `price_index` und `inflation`: Preisentwicklung.
- `shortage_*`: ungedeckte Güternachfrage.
- `sector_*_profit`: Sektorprofitabilität.

Eine Wirtschaft kann nominal reich sein und trotzdem semantisch krank: zum Beispiel viel `Q5` besitzen, aber `Q18` schulden. Das bedeutet viel Code, aber zu wenig Architektur.
