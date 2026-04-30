# Delta-Norm-Wirtschaftssimulation

Dieses Paket enthält eine umfangreiche, eigenständige Wirtschaftssimulation in Python/PyPy3. Sie modelliert ein Wirtschaftssystem, in dem Geld als **Delta zwischen zwei mathematischen Normen** entsteht:

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Ein Verhalten `e` wird als Merkmalsvektor beschrieben. Die Plusnorm bewertet Beitrag/Nutzen, die Minusnorm bewertet Belastung/Risiko/Schaden. Die Differenz wird als Delta-Geld gebucht.

## Enthaltene Datei

- `delta_norm_economy_sim.py` – lauffähige Simulation, nur Standardbibliothek, PyPy3-tauglich.
- `delta_norm_sample_run/` – Beispielausgabe eines 30-Tage-Laufs mit Orbit-Notfall-Szenario.

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
--out        Ausgabeordner
--quiet      Keine Tagesausgaben in der Konsole
--self-test  Kurzer interner Funktionstest
```

## Ausgaben

Nach einem Lauf entstehen im Ausgabeordner:

- `report.md` – lesbarer Bericht mit Kennzahlen, Domänen, Top-Handlungen und Zusammenfassung.
- `daily_metrics.csv` – Zeitreihe der Makrokennzahlen.
- `events.csv` – alle Verhaltensereignisse mit Plusnorm, Minusnorm und Delta.
- `transactions.csv` – vollständiges Buchungsjournal.
- `actors.csv` – Endzustand aller Akteure.
- `final_state.json` – kompakter maschinenlesbarer Endzustand.

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
