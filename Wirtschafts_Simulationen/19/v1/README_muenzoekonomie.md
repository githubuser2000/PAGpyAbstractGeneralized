# Münzökonomie – Wirtschaftssystem in PyPy3

Dieses Paket enthält ein ausführbares Wirtschaftssystem aus dem im Chat entwickelten Münzmodell.

Eine **Münze** ist im Programm eine Optimierungseinheit:

```text
M = (Hauptfunktion, Nebenbedingung, Kategorie)
```

Die 19 Kategorien werden als Wirtschaftssektoren modelliert. Das System simuliert Haushalte, Unternehmen, Banken, Staat, Zentralbank, Märkte, Außenhandel, Umwelt, Verträge, Steuern, Geld, Kredit, Subventionen, Innovation, Bildung, Gesundheit, Kultur, Solidarität und Zielnutzen.

## Dateien

| Datei | Inhalt |
|---|---|
| `muenzoekonomie.py` | Hauptprogramm der Simulation |
| `test_muenzoekonomie.py` | Kleine Selbsttests ohne externe Bibliotheken |
| `README_muenzoekonomie.md` | Diese Anleitung |
| `beispiel_ergebnis/` | Beispielausgabe eines kurzen Testlaufs |

## Ausführen

Mit PyPy3:

```bash
pypy3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42 --out ergebnis
```

Oder mit normalem Python 3:

```bash
python3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42 --out ergebnis
```

## Tests ausführen

```bash
pypy3 test_muenzoekonomie.py
```

oder:

```bash
python3 test_muenzoekonomie.py
```

## Wichtige Optionen

| Option | Bedeutung |
|---|---|
| `--years 20` | Anzahl simulierter Jahre |
| `--periods-per-year 4` | Perioden pro Jahr, standardmäßig Quartale |
| `--households 120` | Anzahl Haushalte |
| `--firms-per-category 2` | Unternehmen je Münz-Kategorie |
| `--banks 2` | Anzahl Geschäftsbanken |
| `--seed 42` | Zufallsseed für reproduzierbare Läufe |
| `--out ergebnis` | Ausgabeordner |
| `--no-foreign` | Außenhandel deaktivieren |
| `--shock-frequency 0.06` | Wahrscheinlichkeit eines Schocks pro Periode |
| `--list-categories` | Die 19 Kategorien anzeigen |

## Ausgabedateien

Nach einem Lauf stehen im Ausgabeordner:

| Datei | Bedeutung |
|---|---|
| `metrics.csv` | Kennzahlen pro Periode: BMP, Münzwohlstand, Inflation, Arbeitslosigkeit, Naturkapital usw. |
| `ledger.csv` | Zahlungs- und Ereignisjournal: Löhne, Käufe, Steuern, Kredite, Schocks, Innovationen |
| `agents.json` | Endzustand von Haushalten, Firmen, Banken, Staat, Zentralbank, Umwelt, Außenwirtschaft |
| `coins.json` | Alle erzeugten Münzen mit Hauptfunktion, Nebenbedingung, Kategorie, Qualität, Preis, Score |
| `contracts.json` | Arbeits-, Kredit- und weitere Verträge |
| `summary.md` | Lesbare Zusammenfassung des Simulationslaufs |

## Modellkern

Das Programm enthält:

- 19 Kategorien als ökonomische Sektoren.
- Münzen als Optimierungsobjekte mit `main_function`, `constraint`, `category`, `inputs`, `outputs`, `quality`, `externality`, `risk`, `score`.
- Haushalte mit Geld, Bildung, Gesundheit, Vertrauen, Fähigkeit, Aufmerksamkeit, Konsumnutzen.
- Firmen mit Kategorie, Kapital, Technologie, Produktivität, Reputation, Inventar, Schulden.
- Banken mit Kreditvergabe, Zinsen, Tilgung und Ausfällen.
- Staat mit Steuern, Transfers, öffentlicher Investition, Mindestlohn, Subventionen und Schuld.
- Zentralbank mit Geldmenge, Zinsregel, Inflationsziel und Glaubwürdigkeit.
- Märkte mit Preisen, Angebot, Nachfrage, Umsatzsteuer, Importen und Exporten.
- Umwelt mit Naturkapital, Biodiversität, Emissionen, Ressourcenstress und Regeneration.
- Krisen/Schocks: Energie, Vertrauen, Innovation, Gesundheit, Umwelt, Nachfrage, Finanzen.
- Kennzahlen: Brutto-Münzprodukt, Münzwohlstand, Inflation, Arbeitslosigkeit, Ungleichheit, systemisches Risiko.

## Die 19 Kategorien

| Nr. | Kurzname | Wirtschaftssektor |
|---:|---|---|
| 1 | Expression extrahieren | Forschung, Rohideen, Diagnose, Datengewinnung |
| 2 | Drücken / Ausdrücken | Arbeit, Aufwand, Leistung, Produktionsdruck |
| 3 | Extrahiertes Ausgedrücktes | Vorprodukte, Entwürfe, Demos, frühe Versionen |
| 4 | Materielle Produktion | Industrie, Handwerk, Bau, Landwirtschaft, Herstellung |
| 5 | Rahmen / Werkzeug | Maschinen, Werkzeuge, Plattformen, Institutionen |
| 6 | Expressivität / Intensität | Marken, Signalstärke, Qualität, Aufmerksamkeit |
| 7 | Kreative Formung | Kunst, Design, Architektur, Mode, Mediengestaltung |
| 8 | Bild / fertiges Objekt | Endprodukt, Medienobjekt, fertige Ware |
| 9 | Typen des Ausdrucks | Normen, Labels, Produktarten, Branchenlogik |
| 10 | Galerie / Markt | Märkte, Plattformen, Börsen, Museen, Kataloge |
| 11 | Stilbruch / Disruption | Innovation, Disruption, radikale Experimente |
| 12 | Bewertung / Kritik | Zertifizierung, Rezension, Qualitätskontrolle, Risikoanalyse |
| 13 | Spektrum / Infrastruktur | Energie, Datenströme, Verkehrsflüsse, Kommunikationsnetze |
| 14 | Fusion von Ideen | Kooperation, Forschungskonsortien, neue Industrien |
| 15 | Rhythmus / Serie | Serienproduktion, Routinen, Prozesse, Abonnements |
| 16 | Transformation | Reparatur, Recycling, Übersetzung, Datenkonvertierung, Logistik |
| 17 | Meta-Intelligenz | Bildung, KI, Beratung, Psychologie, Strategie |
| 18 | Wertschätzung / Solidarität | Pflege, Geschenke, Hilfe, soziale Arbeit, Solidarität |
| 19 | Ziel-Ergebnis / Hot Dog | Konsum, Grundversorgung, Bedürfnisbefriedigung |

## Einordnung

Das ist ein Simulations- und Experimentiermodell. Es ist nicht als reale volkswirtschaftliche Prognosemaschine gedacht, sondern als programmierbarer Kern für dein Münzökonomie-Konzept: Man kann Kategorien, Regeln, Steuern, Schocks, Preise, Agentenzahlen und Politikparameter verändern und dann beobachten, wie sich das System entwickelt.
