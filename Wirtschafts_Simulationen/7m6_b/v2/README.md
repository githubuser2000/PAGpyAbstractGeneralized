# Vector Currency Economy Simulation V2

PyPy3-kompatible, reine-Standardbibliothek-Simulation für die Zahlen-Winkel-Währung:

```text
M = (amount, theta, confidence, origin, history)
```

- `amount`: normaler Zahlenbetrag / Kaufkraft
- `theta`: Winkel aus Gut/Böse-Achse und Beliebt/Unbeliebt-Achse
- `confidence`: Sicherheit des Winkels
- `origin` und `history`: Herkunft, Provenienz, Winkelwäsche-Risiko

V2 erweitert die erste Version stark. Sie ist weiterhin kein kalibriertes Realweltmodell, sondern ein lauffähiges Forschungsgerüst für Experimente mit einer politisch-ökonomischen Vektorwährung.

## Ausführen

Empfohlen mit PyPy3:

```bash
pypy3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Oder mit CPython:

```bash
python3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Größerer Lauf:

```bash
pypy3 vector_currency_sim.py --steps 120 --countries 4 --households 1200 --firms 180 --banks 12 --seed 123 --out metrics_big.csv --summary summary_big.json --events events_big.csv
```

Die V2 hat deutlich mehr Mechaniken als V1. Unter CPython sind 60 Schritte mit 600 Haushalten ein guter Standardtest; PyPy3 sollte für längere Läufe besser geeignet sein.

## Dateien

- `vector_currency_sim.py`: Hauptdatei, direkt ausführbar.
- `vector_currency_sim_v2.py`: identische V2-Kopie mit explizitem Namen.
- `demo_metrics.csv`: Beispielausgabe eines 60-Schritte-Laufs.
- `demo_summary.json`: Zusammenfassung des Beispiel-Laufs.
- `demo_events.csv`: Ereignislog des Beispiel-Laufs.
- `COVERAGE.md`: Abdeckung der eingebauten Mechaniken.
- `CHANGELOG_V2.md`: Was gegenüber V1 ergänzt wurde.

## Große eingebaute Blöcke

### 1. Kernwährung

- Vektorgeld mit Betrag, Winkel, Konfidenz, Herkunft und Historie
- Winkelverschmelzung nach Betrag mal Konfidenz
- Kaufwinkel und Verkaufswinkel je Akteur
- Winkelrotation mit Kosten, Konfidenzverlust und Winkelwäscheindex
- internationale Winkelübersetzung zwischen Ländern

### 2. Länder, Regierungen, Völker

- mehrere Länder mit eigenen Währungen, Wechselkursen, Medienfreiheit, Rechtssystem, Ressourcen, Umweltzustand, Infrastruktur und politischer Stabilität
- Regierungen als unvollkommene Gut/Böse-Orakel mit Kompetenz, Korruption, Ideologie, Informationsqualität, Macht, Gerichten und Propaganda
- Völker als Gruppen mit Ideologie, Einkommen, Aktivismus, Medienanfälligkeit, Moralstrenge und Sektorpräferenzen
- Beliebt/Unbeliebt-Bewertung durch Gruppenpräferenzen, Preis, Qualität, Arbeitsplätze, Werbung, Skandale und Medien

### 3. Märkte

- Produktmärkte
- Dienstleistungsmärkte
- Arbeitsmarkt
- Kreditmarkt
- Winkelmarkt
- FX-/Kapitalfluss-Orderbuchapproximation
- Bondmarkt
- Aktien-/Equitymarkt
- Immobilienmarkt
- Mietmarkt
- Hypothekenmarkt
- Versicherungsmarkt
- internationale Lieferketten und B2B-Inputs

### 4. Firmen, Konzerne, Holdings

- Firmen mit Sektor, Preis, Qualität, Inventar, Arbeit, Technologie, Produktivität, Lohnangebot, Schulden, Marktmacht, Lobbying, Werbung, Betrug, Transparenz und Compliance
- explizite Corporate Groups mit Parent-Firma, Tochterfirmen, Tax-Haven-Land, Kontrollmacht, Opazität und konsolidiertem Winkel
- Transfer Pricing, Steuervermeidung, konzerninterne Dividenden
- börsennotierte Firmen mit Aktienpreis, Shares Outstanding und Free Float
- Corporate Bonds
- R&D, Patente, Technologie-Spillover

### 5. Finanzsystem

- Banken mit Kapital, Reserven, Kreditbuch, Hypothekenbuch, Bond- und Equity-Beständen, Schattenexposure und Liquiditätsstress
- Zentralbanken mit Zinspolitik, Geldemission, FX-Reserven, Reservewährungsgewicht und Lender-of-last-resort-Funktion
- Investment-/Pensionsfonds mit AUM, Mandatswinkel, Aktien- und Bondbeständen
- Ratingagenturen als alternative Orakel mit Genauigkeit, Bias, Korruption und Einfluss

### 6. Politik, Recht, Medien

- politische Parteien mit Ideologie, Wirtschaftspolitik, Autoritarismus, Unterstützung und Firmenspendern
- Verfassungs-/Gerichtsebene mit Overrides gegen willkürliche Sanktionen
- Minderheitenschutz und Minority-Harm-Index
- Medien, Propaganda, Werbung, Boykottwellen, Skandale, Leaks und zivilgesellschaftliche Untersuchungen
- Audits, Strafen, Rehabilitation, Vertragsstreitigkeiten

### 7. Umwelt, Gesellschaft, externe Effekte

- Pollution, CO₂-/Carbon-Stock, Biodiversity, Health Burden, Crime Index, Data Privacy Damage
- Infrastrukturqualität nach Sektor
- Human Capital, Gesundheit, Alterung, Renteneintritt, Sterblichkeit, Migration
- Ressourcenverbrauch, Energie- und Materialintensität

## Wichtige Metriken in `metrics.csv`

Neben klassischen Größen wie GDP, Inflation, Arbeitslosigkeit, Gini, Löhnen und Profit gibt es V2-Metriken wie:

- `fx_orderbook_volume`
- `capital_flow_volume`
- `reserve_intervention`
- `bond_issuance`
- `bond_defaults`
- `equity_issuance`
- `equity_trading_volume`
- `dividends`
- `transfer_pricing_volume`
- `tax_avoided`
- `real_estate_rents`
- `mortgages_issued`
- `insurance_premiums`
- `insurance_claims`
- `r_and_d_spend`
- `patent_events`
- `rating_actions`
- `constitutional_overrides`
- `minority_harm_index`
- `migration_count`
- `infrastructure_spending`
- `privacy_damage`
- `health_damage`
- `biodiversity_loss`
- `crime_delta`
- `contract_disputes`
- `world_money_theta_deg`
- `world_money_concentration`
- `avg_goodness_axis`
- `avg_popularity_axis`
- `angle_volatility`
- `avg_angle_spread`
- `mean_cash_confidence`

## Architektur

Die Simulation ist hybrid:

- agentenbasiert für Haushalte, Firmen, Banken, Fonds, Regierungen und Zentralbanken
- stock-flow-artig für Geld, Kredite, Bonds, Steuern, Dividenden und Zahlungsflüsse
- netzwerkartig für Holdings, Lieferketten, Eigentum und internationale Winkelübersetzung
- ereignisbasiert für Krisen, Skandale, Boykotte, Patente, Gesundheitswarnungen und politische Eingriffe

## Hinweis

`pypy3` war in der Erstellungsumgebung nicht installiert. Der Code wurde mit CPython kompiliert und mit Demo-Läufen getestet. Er nutzt nur Python-Standardbibliothek und sollte deshalb unter PyPy3 laufen.
