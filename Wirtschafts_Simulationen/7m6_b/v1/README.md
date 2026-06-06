# Vektorwährungs-Wirtschaftssimulation

Dies ist eine lauffähige **PyPy3-kompatible** Wirtschaftssimulation für die im Chat entwickelte Grundlage:

\[
M = (m, \theta, \rho, h)
\]

- `m`: Zahlenbetrag / Kaufkraft
- `theta`: Winkelrichtung aus Gut/Böse und Beliebt/Unbeliebt
- `rho`: Konfidenz / Sicherheit des Winkels
- `h`: begrenzte Herkunfts- und Transaktionshistorie

Die Simulation ist bewusst als **Forschungs- und Experimentiergerüst** gebaut. Sie ist nicht ökonometrisch kalibriert, enthält aber die relevanten Systemteile, damit sich Dynamiken wie Winkelhandel, Winkelwäsche, Legitimitätskrisen, Sanktionen, Medienereignisse, Kreditkrisen und internationale Winkelübersetzung beobachten lassen.

## Enthaltene Bausteine

### Politische Ebene

- mehrere Länder / Jurisdiktionen
- mehrere Regierungen als Gut/Böse-Orakel
- Regierungsparameter: Kompetenz, Korruption, Ideologie, Informationsqualität, Macht, Gerichtsunabhängigkeit, Propaganda
- Regierungsfehler und Unsicherheit
- Sanktionen gegen Firmen
- Steuern, Subventionen, öffentliche Beschaffung
- Wahlen, Legitimität, Proteste, Regierungswechsel

### Völker und Gesellschaft

- mehrere Völker mit mehreren Gruppen pro Land
- Gruppenparameter: Ideologie, Einkommen, Medienanfälligkeit, Aktivismus, Regierungsvertrauen, moralische Strenge
- Beliebt/Unbeliebt-Achse aus Präferenzen, Preisen, Qualität, Werbung, Skandalen, Jobs und Medien
- Polarisierung und Protestdynamik

### Akteure

- Haushalte / Individuen
- Firmen und Konzernähnliche Unternehmen
- Banken
- Zentralbanken
- Regierungen
- Zentralbankgeld und Kreditgeld

### Märkte

- Produktmärkte
- Dienstleistungsmärkte
- Arbeitsmarkt
- Kreditmarkt
- Winkelmarkt
- internationaler Handel
- Schwarzmarkt / Graumarkt
- öffentliche Beschaffung

### Güter und Sektoren

Enthaltene Sektoren:

- food
- energy
- housing
- health
- education
- transport
- clothing
- entertainment
- luxury
- data
- software
- raw_materials
- machinery
- finance
- security
- media

Jeder Sektor hat Preisbasis, Essenzialität, Einkommenselastizität, Winkelsensitivität, Arbeitsintensität, Energieintensität, Materialintensität, Umweltbelastung, sozialen Nutzen und Inputsektoren.

### Finanzsystem

- Banken mit Kapital, Reserven, Risikoneigung und Kreditbüchern
- Kredite mit Betrag, Zinssatz, Laufzeit, Winkel und Konfidenz
- Ausfallrisiko aus Verschuldung, Winkelrisiko, Fraud, Konfidenz
- Kreditausfälle
- Bankausfälle
- Zentralbankpolitik mit Basiszins, Inflationsziel, Arbeitslosenziel und Lender-of-last-resort

### Winkelwährung

- `VectorMoney`: Betrag + Winkel + Konfidenz + Herkunft
- Winkelkompatibilität über Kreisdistanz
- gewichtete Winkelverschmelzung
- Winkelrotation mit Kosten
- Winkelspread: Kaufwinkel vs Verkaufswinkel
- Winkelmarktgebühren
- Winkelwäscheindex
- Geldwinkelverteilung als Histogramm

### Informations- und Machtmodell

- Medienfreiheit
- Propaganda
- Werbung
- Skandale
- Leaks
- Boykottwellen
- Audit- und Gerichtssystem
- Lobbying
- Marktmacht
- Schattenwirtschaft

### Externe Effekte und Krisen

- Umweltverschmutzung
- Ressourcenverbrauch
- Produktivitäts- und Sentimentfolgen von Umweltbelastung
- Energieschocks
- Korruptionsleaks
- Cyberangriffe
- Naturkatastrophen
- Kriegsschreck
- Bank-Run-Angst
- Firmenbankrotte

## Installation

Keine externen Pakete nötig.

```bash
pypy3 vector_currency_sim.py --steps 120 --countries 3 --households 900 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Alternativ mit CPython:

```bash
python3 vector_currency_sim.py --steps 120 --countries 3 --households 900 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

In der Erstellungsumgebung war `pypy3` nicht installiert; der Code wurde dort mit `python3` kompiliert und mit einem Probelauf ausgeführt. Er verwendet nur die Standardbibliothek und vermeidet NumPy/Pandas, damit er unter PyPy3 laufen kann.

## Beispiel: kleiner schneller Lauf

```bash
python3 vector_currency_sim.py \
  --steps 24 \
  --countries 3 \
  --households 300 \
  --firms 64 \
  --banks 6 \
  --seed 11 \
  --out demo_metrics.csv \
  --summary demo_summary.json \
  --events demo_events.csv \
  --verbose
```

## Output-Dateien

### `metrics.csv`

Eine Zeile pro Simulationsmonat. Wichtige Spalten:

- `gdp`
- `consumer_sales`
- `b2b_sales`
- `wages`
- `taxes`
- `subsidies`
- `loans_issued`
- `loan_defaults`
- `black_market_volume`
- `angle_rotation_volume`
- `angle_rotation_cost`
- `laundering_index`
- `scandals`
- `strikes`
- `bank_failures`
- `firms_defaulted`
- `trade_volume`
- `money_supply`
- `household_gini`
- `firm_cash_gini`
- `unemployment`
- `avg_inflation`
- `avg_legitimacy`
- `avg_polarization`
- `legitimacy_gap`
- `world_money_theta_deg`
- `world_money_concentration`
- `avg_goodness_axis`
- `avg_popularity_axis`
- `angle_volatility`
- `avg_angle_spread`
- `mean_cash_confidence`

Zusätzlich gibt es länderspezifische Spalten:

- `country_0_gdp`
- `country_0_inflation`
- `country_0_unemployment`
- `country_0_legitimacy`
- `country_0_pollution`
- `country_0_exchange_rate`
- `country_0_protests`

usw. für jedes Land.

### `summary.json`

Enthält:

- letzte Metrikzeile
- Weltgeldwinkel
- Winkelhistogramm
- Ländersummary
- Top-Firmen nach Umsatz
- wichtige Ereignisse

### `events.csv`

Ereignislog mit:

- Skandalen
- Audits
- Bankrotten
- Schocks
- Boykotten
- Regierungswechseln

## Modellkern

Ein Handel transportiert nicht nur Betrag, sondern Winkel:

```text
payer.cash.theta + context_theta -> incoming.theta
```

Der Empfänger verschmilzt das eingehende Geld mit seiner bestehenden Geldposition. Die Winkelverschmelzung ist betrags- und konfidenzgewichtet.

Winkelkompatibilität wird über die Kreisdistanz berechnet:

```text
compatibility = cos(distance(theta_a, theta_b) / 2)
```

Winkelrotation kostet Betrag und senkt bei großen Sprüngen Konfidenz:

```text
keep = exp(-friction * distance^2)
```

Damit ist eine moralisch oder sozial große Umfärbung teuer. Wenn eine Firma viel Winkelrotation ohne echte Compliance/Transparenz/Fraud-Reduktion macht, steigt der `laundering_index`.

## Wichtige Designentscheidung

Der Winkel ist nicht objektive Wahrheit. Regierungen und Völker sind selbst fehlbar:

- Regierungen können korrupt, ideologisch, schlecht informiert oder manipuliert sein.
- Völker können durch Werbung, Medien, Preise, Arbeitsplätze, Skandale und Trends reagieren.
- Deshalb wird jeder Winkel mit Konfidenz und Gedächtnis geführt.

Das ist der entscheidende Schutz gegen eine naive „moralische Zahl“.

## Erweiterungspunkte

Die Datei ist monolithisch gehalten, damit sie direkt mit PyPy3 läuft. Sinnvolle nächste technische Schritte wären:

- Parametrisierung über JSON-Szenarien
- echte Konzern-Holdingstrukturen
- mehrstufigere Lieferketten
- getrennte nationale Währungen mit explizitem FX-Orderbuch
- Netzwerkgraph für Eigentum, Medienmacht und Lieferketten
- Kalibrierung von Nachfrage und Preisen
- Monte-Carlo-Läufe über viele Seeds
- Visualisierung der Winkelverteilung
