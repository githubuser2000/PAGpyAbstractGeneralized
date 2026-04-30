# Delta-Norm Economy Simulation / Delta-Norm-Wirtschaftssimulation

Dieses Paket enthält eine eigenständige Wirtschaftssimulation in Python/PyPy3. Sie modelliert ein Wirtschaftssystem, in dem Geld als **Delta zwischen zwei mathematischen Normen** entsteht:

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Ein Verhalten `e` wird als Merkmalsvektor beschrieben. Die Plusnorm bewertet Beitrag/Nutzen, die Minusnorm bewertet Belastung/Risiko/Schaden. Die Differenz wird als Delta-Geld gebucht.

## Sprache / Language

Die Simulation ist jetzt per Programmparameter auf Deutsch oder Englisch einstellbar. **Standard ist Englisch.**

```bash
pypy3 delta_norm_economy_sim.py --days 365 --persons 700 --scenario baseline --out run_en
pypy3 delta_norm_economy_sim.py --days 365 --persons 700 --scenario baseline --out run_de --lang de
```

Unterstützte Werte:

```text
--lang en   English output, default
--lang de   Deutsche Ausgabe
```

Der Sprachparameter betrifft die Konsolenausgabe, `report.md`, `utf8_dashboard.md` und `utf8_dashboard_ansi.txt`. CSV/JSON-Schlüssel bleiben stabil, damit Auswertungen und Skripte nicht brechen.

## Enthaltene Dateien

- `delta_norm_economy_sim.py` – lauffähige Simulation, nur Standardbibliothek, PyPy3-tauglich.
- `delta_norm_sample_run_en/` – Beispielausgabe eines englischen Laufs.
- `delta_norm_sample_run_de/` – Beispielausgabe eines deutschen Laufs.

## Start

```bash
pypy3 delta_norm_economy_sim.py --days 365 --persons 700 --scenario baseline --out run_baseline
```

Alternativ mit CPython:

```bash
python3 delta_norm_economy_sim.py --days 365 --persons 700 --scenario baseline --out run_baseline
```

## Szenarien

```bash
pypy3 delta_norm_economy_sim.py --scenario baseline
pypy3 delta_norm_economy_sim.py --scenario media_crisis
pypy3 delta_norm_economy_sim.py --scenario orbit_emergency
pypy3 delta_norm_economy_sim.py --scenario lunar_expansion
pypy3 delta_norm_economy_sim.py --scenario scarcity
pypy3 delta_norm_economy_sim.py --scenario boom
```

## Wichtige Parameter

```text
--days       Anzahl der Simulationstage, Standard: 180
--persons    Anzahl natürlicher Personen, Standard: 300
--seed       Zufalls-Seed für reproduzierbare Läufe
--scenario   baseline, media_crisis, orbit_emergency, lunar_expansion, scarcity, boom
--lang       en oder de; Standard: en
--out        Ausgabeordner
--quiet      Keine bzw. weniger Konsolenausgabe; Dateien werden weiterhin geschrieben
--self-test  Kurzer interner Funktionstest
```

## Ausgaben

Nach einem Lauf entstehen im Ausgabeordner:

- `report.md` – lesbarer Bericht mit Kennzahlen, Domänen, Top-Handlungen und Zusammenfassung.
- `utf8_dashboard.md` – umfangreiche UTF8-Art-Auswertung mit Erklärungen, Diagrammen und Interpretationen.
- `utf8_dashboard_ansi.txt` – farbige Terminalversion der UTF8-Dashboard-Auswertung mit ANSI-Farben.
- `daily_metrics.csv` – Zeitreihe der Makrokennzahlen.
- `events.csv` – alle Verhaltensereignisse mit Plusnorm, Minusnorm und Delta.
- `transactions.csv` – vollständiges Buchungsjournal.
- `actors.csv` – Endzustand aller Akteure.
- `final_state.json` – kompakter maschinenlesbarer Endzustand.

## Farbiges UTF8-Dashboard

Die Simulation erzeugt eine große visuelle Text-Auswertung. Zu jedem Abschnitt gibt es immer:

- eine Erklärung **oberhalb** der Grafik, was simuliert wird und warum,
- eine **UTF8-Art-Grafik / ein Diagramm / eine Abbildung**,
- eine **Auswertung darunter**, die den Zustand interpretiert.

Enthalten sind unter anderem Makrotrendlinien, Geldschöpfung und Haftung, Grundversorgung, Preise nach Ort, Beschäftigung, Sektoren, Delta nach Domänen, häufige Handlungen, Medien- und Nachrichtenökologie, Wohlfahrt, Ungleichheit, Raumwirtschaft sowie Finanz- und Governance-Panels.

## Simulierte Bereiche

Die Simulation enthält unter anderem:

- Zentralbank/ZEMO-ähnliches Clearing für Erde, Mond, Orbit und Raumstation.
- Personen mit Gesundheit, Stress, Vertrauen, Fähigkeiten, Konsumverhalten und Medienverhalten.
- Firmen in Landwirtschaft, Wasser, Energie, Bau, Fertigung, Logistik, Gesundheit, Bildung, Forschung, Medien, Finanzen, Raumfahrt, Bergbau und Datennetzen.
- Märkte mit Preisen, Lagerbeständen, Knappheit, Qualitätsfaktoren und Standorteffekten.
- Arbeit, Löhne, Produktivität, Arbeitslosigkeit und Fähigkeiten.
- Nahrung, Wasser, Energie, Wohnen, Gesundheit, Bildung, Transport, Konsumgüter, Medien, Ersatzteile, Sauerstoff, Rohstoffe, Datenbandbreite und Forschung.
- Medien- und Nachrichtenzyklus mit Wahrheit, Relevanz, Quellenqualität, Aufmerksamkeit, Manipulation, Panik, Korrekturen und öffentlicher Nachrichtenfinanzierung.
- Satelliten, Raumstation, Mondhabitat, Lebenserhaltung, Trümmerrisiko und Infrastrukturwartung.
- Kredite, Zinsen, Versicherungen, Schadensfälle und öffentliche Fonds.
- demokratische Normanpassung, Einsprüche, Grundrechte, Grundversorgungsschutz, Anti-Gaming- und Anti-Manipulations-Audits.

## Selbsttest

```bash
pypy3 delta_norm_economy_sim.py --self-test
```

Der Selbsttest führt einen kurzen Lauf aus, prüft zentrale Ereignisse, Transaktionen und Ausgabedateien und meldet bei Erfolg `Self-test OK`.

## Hinweis

Das Modell ist absichtlich als Simulation und nicht als politischer Vorschlag implementiert. Es enthält Schutzmechanismen gegen eine naive Sozialkredit-Logik: begrenzte negative Buchungen, Grundversorgungsschutz, Einsprüche, Transparenzereignisse, Anti-Manipulationskontrollen und getrennte Konten.
