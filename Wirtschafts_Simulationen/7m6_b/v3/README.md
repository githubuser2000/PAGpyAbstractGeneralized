# Vector Currency Economy Simulation V3

PyPy3-kompatible, reine-Standardbibliothek-Simulation für eine Zahlen-Winkel-Währung:

```text
M = (amount, theta, confidence, origin, history)
```

- `amount`: normaler Zahlenbetrag / Kaufkraft / Wertgewicht des Winkels
- `theta`: Winkel aus Gut/Böse-Achse und Beliebt/Unbeliebt-Achse
- `confidence`: Sicherheit des Winkels, also Konfidenz der Bewertung
- `origin` und `history`: Herkunft, Provenienz und Winkelwäsche-Risiko

V3 erweitert V2 um zwei Dinge:

1. einen expliziten Dreifachmarkt `Wert ↔ Gutartigkeit ↔ Beliebtheit`, inklusive Metriken für „Wert kauft Gutartigkeit“, „Wert kauft Beliebtheit“, „Beliebtheit kauft Gutartigkeit“ und „Gutartigkeit kauft Beliebtheit“;
2. ein großes buntes UTF‑8/ANSI-Terminaldashboard mit Kompass, Kreis-Orderbuch, Buy-/Sell-Winkeln, Länderpanels, Firmenquadranten, Makroflüssen und Ereignisband.

Die Simulation ist kein kalibriertes Realweltmodell. Sie ist ein lauffähiges Forschungsgerüst für Experimente mit einer politisch-ökonomischen Vektorwährung.

## Ausführen

Empfohlen mit PyPy3:

```bash
pypy3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Oder mit CPython:

```bash
python3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Mit buntem UTF‑8-Dashboard:

```bash
pypy3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --art --art-every 6 --art-width 120
```

Ohne ANSI-Farben, aber weiterhin mit UTF‑8-Art:

```bash
pypy3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --art --art-every 6 --no-color
```

## Neue V3-Flags

- `--art`: gibt das große UTF‑8/ANSI-Dashboard während des Simulationslaufs aus.
- `--art-every N`: druckt das Dashboard alle `N` Schritte. Der erste und letzte Schritt werden immer gezeigt.
- `--art-width N`: Zielbreite für die Dashboard-Trennlinien.
- `--no-color`: deaktiviert ANSI-Farben, lässt aber die UTF‑8-Diagramme stehen.

## Dateien

- `vector_currency_sim.py`: Hauptdatei, direkt ausführbar.
- `vector_currency_sim_v3.py`: identische V3-Kopie mit explizitem Namen.
- `demo_metrics.csv`: Beispielausgabe eines 24-Schritte-Laufs.
- `demo_summary.json`: Zusammenfassung des Beispiel-Laufs.
- `demo_events.csv`: Ereignislog des Beispiel-Laufs.
- `demo_art_ansi.txt`: Beispielausgabe des bunten Dashboards mit ANSI-Farben.
- `demo_art_plain.txt`: dieselbe Dashboard-Art ohne ANSI-Farben.
- `demo_art_metrics.csv`, `demo_art_summary.json`, `demo_art_events.csv`: Metriken des Dashboard-Demolaufs.
- `COVERAGE.md`: Abdeckung der eingebauten Mechaniken.
- `CHANGELOG_V2.md`: Was in V2 ergänzt wurde.
- `CHANGELOG_V3.md`: Was in V3 ergänzt wurde.
- `ART_DASHBOARD.md`: Erklärung der UTF‑8-Diagramme.
- `run_demo.sh`: normaler Demolauf.
- `run_demo_art.sh`: Demolauf mit Dashboard.

## Währungskern

```text
M = m · e^(iθ)
θ = atan2(Beliebtheit, Gutartigkeit)
effektive Kaufkraft ≈ m · ρ · cos(Δθ/2)
```

Jeder wichtige Akteur besitzt jetzt sichtbar:

```text
Kaufwinkel    θ_K  = welche Winkelqualität er akzeptiert
Verkaufswinkel θ_V = welche Winkelqualität er verlangt
Spread        Δθ   = Distanz zwischen Kaufen und Verkaufen
```

Der Betrag `m` ist weiterhin Kaufkraft, aber zugleich Gewicht des Winkels im Markt. Ein großer Akteur mit viel Geld zieht das Winkelorderbuch stärker als ein kleiner Akteur.

## V3-Dreifachmarkt

V3 macht den Handel der drei Größen sichtbar und teilweise explizit dynamisch:

```text
Wert         → Gutartigkeit    durch Compliance, Audits, Umweltinvestitionen, Arbeitsschutz
Wert         → Beliebtheit     durch Werbung, Service, Community, Medien
Beliebtheit  → Gutartigkeit    durch soziales Mandat, Kundenvertrauen, Akzeptanz realer Reformkosten
Gutartigkeit → Beliebtheit     durch glaubwürdiges Verhalten, Medienfreiheit, Gerichte, Zivilgesellschaft
```

Das ist absichtlich nicht als magische moralische Geldwäsche implementiert. Betrug, geringe Medienfreiheit, geringe Transparenz und schwache Gerichte erzeugen Reibung, Gebühren, Konfidenzverlust und Winkelwäscheindex.

Neue Metriken:

- `value_buy_goodness_volume`
- `value_buy_popularity_volume`
- `popularity_buy_goodness_volume`
- `goodness_buy_popularity_volume`
- `value_good_pop_exchange_fees`
- `triadic_exchange_count`

## Dashboard-Diagramme

Das Dashboard enthält unter anderem:

- Makro-Cockpit für BIP, Geldmenge, Inflation, Arbeitslosigkeit, Konfidenz, Gutartigkeit, Beliebtheit, Legitimität und Ungleichheit
- Vektor-Kompass mit Weltgeldwinkel, Cashwinkel, Kaufwinkel und Verkaufswinkel
- Dreifachhandel-Diagramm `Wert ↔ Gutartigkeit ↔ Beliebtheit`
- Marktfluss-Diagramm für Konsum, B2B, Arbeit, Steuern, Subventionen, Kredite, Handel, Winkelrotation, Schwarzmarkt und Kapitalflüsse
- Kreis-Orderbuch für Kauf- und Verkaufswinkel in 12 Winkelzonen
- Tabelle der größten Akteure mit Cashwinkel, Kaufwinkel, Verkaufswinkel, Spread und Konfidenz
- Länderpanels mit BIP, Inflation, Arbeitslosigkeit, Legitimität, FX, Protesten, Infrastruktur, Biodiversität, Kriminalität und Gerichten
- Firmenkarte `Gutartigkeit × Beliebtheit`, gewichtet durch Unternehmenswert
- externe Effekte und politische Sicherheitsventile
- Ereignisband für Skandale, Gerichte, Schocks, Patente, Proteste und politische Eingriffe

## Große eingebaute Blöcke

### 1. Länder, Regierungen, Völker

- mehrere Länder mit Währungen, Wechselkursen, Medienfreiheit, Rechtssystem, Ressourcen, Umweltzustand, Infrastruktur und politischer Stabilität
- Regierungen als unvollkommene Gut/Böse-Orakel mit Kompetenz, Korruption, Ideologie, Informationsqualität, Macht, Gerichten und Propaganda
- Völker als Gruppen mit Ideologie, Einkommen, Aktivismus, Medienanfälligkeit, Moralstrenge und Sektorpräferenzen
- Beliebt/Unbeliebt-Bewertung durch Gruppenpräferenzen, Preis, Qualität, Arbeitsplätze, Werbung, Skandale und Medien

### 2. Märkte

- Produkt- und Dienstleistungsmärkte
- Arbeitsmarkt
- Kreditmarkt
- Winkelmarkt
- Dreifachmarkt Wert/Gutartigkeit/Beliebtheit
- FX-/Kapitalfluss-Orderbuchapproximation
- Bondmarkt
- Aktien-/Equitymarkt
- Immobilienmarkt
- Mietmarkt
- Hypothekenmarkt
- Versicherungsmarkt
- internationale Lieferketten und B2B-Inputs

### 3. Firmen, Konzerne, Holdings

- Firmen mit Sektor, Preis, Qualität, Inventar, Arbeit, Technologie, Produktivität, Lohnangebot, Schulden, Marktmacht, Lobbying, Werbung, Betrug, Transparenz und Compliance
- Corporate Groups mit Parent-Firma, Tochterfirmen, Tax-Haven-Land, Kontrollmacht, Opazität und konsolidiertem Winkel
- Transfer Pricing, Steuervermeidung, konzerninterne Dividenden
- börsennotierte Firmen mit Aktienpreis, Shares Outstanding und Free Float
- Corporate Bonds
- R&D, Patente, Technologie-Spillover

### 4. Finanzsystem

- Banken mit Kapital, Reserven, Kreditbuch, Hypothekenbuch, Bond- und Equity-Beständen, Schattenexposure und Liquiditätsstress
- Zentralbanken mit Zinspolitik, Geldemission, FX-Reserven, Reservewährungsgewicht und Lender-of-last-resort-Funktion
- Investment-/Pensionsfonds mit AUM, Mandatswinkel, Aktien- und Bondbeständen
- Ratingagenturen als alternative Orakel mit Genauigkeit, Bias, Korruption und Einfluss

### 5. Politik, Recht, Medien

- politische Parteien mit Ideologie, Wirtschaftspolitik, Autoritarismus, Unterstützung und Firmenspendern
- Verfassungs-/Gerichtsebene mit Overrides gegen willkürliche Sanktionen
- Minderheitenschutz und Minority-Harm-Index
- Medien, Propaganda, Werbung, Boykottwellen, Skandale, Leaks und zivilgesellschaftliche Untersuchungen
- Audits, Strafen, Rehabilitation, Vertragsstreitigkeiten

### 6. Umwelt, Gesellschaft, externe Effekte

- Pollution, CO₂-/Carbon-Stock, Biodiversity, Health Burden, Crime Index, Data Privacy Damage
- Infrastrukturqualität nach Sektor
- Human Capital, Gesundheit, Alterung, Renteneintritt, Sterblichkeit, Migration
- Ressourcenverbrauch, Energie- und Materialintensität

## Architektur

Die Simulation ist hybrid:

- agentenbasiert für Haushalte, Firmen, Banken, Fonds, Regierungen und Zentralbanken
- stock-flow-artig für Geld, Kredite, Bonds, Steuern, Dividenden und Zahlungsflüsse
- netzwerkartig für Holdings, Lieferketten, Eigentum und internationale Winkelübersetzung
- orderbuchartig für Winkelzonen, FX und Kapitalflüsse
- ereignisbasiert für Krisen, Skandale, Boykotte, Patente, Gesundheitswarnungen und politische Eingriffe

## Hinweis

`pypy3` war in der Erstellungsumgebung nicht installiert. Der Code wurde mit CPython kompiliert und mit Demo-Läufen getestet. Er nutzt nur die Python-Standardbibliothek und sollte deshalb unter PyPy3 laufen.
