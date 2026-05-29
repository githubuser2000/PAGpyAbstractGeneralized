# Erweiterung: Was aus der Volkswirtschaft übernommen wurde — aber ohne Geldlogik

Diese Datei beschreibt die Erweiterung der Simulation nach deiner Vorgabe:

> Handeln ist anders: kaufen/verkaufen = Kausalität, Zeit, Intensität, Existenz, Potenzen, Wirkungen, Substanz, Materie, Differenz, Bestimmung, Phänomene, Winkelrichtung statt Wert, Menge, Wert, Dinge.

## Übersetzungstabelle

| Alte Volkswirtschaft | Neue Planetenwirtschaft |
|---|---|
| Haushalt | Einzelpersonen/Kohorten in Kommunen: Bedürfnisse, Fähigkeiten, Gesundheit, Autonomie |
| Firma | Wirkungsgruppe: Fähigkeit, Substanz, Zeit und Kausalität |
| Markt | Rückkopplungs- und Prioritätssystem aus Wahrheitsvektoren |
| Preis | keine Entsprechung; ersetzt durch Dringlichkeit, Differenz, Richtung, Wirkung |
| Einkommen | Zugang zu Bedürfniswirkungen + reale Entfaltungsmöglichkeiten |
| Lohn | entfällt; Zeitbeitrag wird nicht gekauft |
| Profit | entfällt; Erfolg = gelöste Differenz + positive Wirkung |
| Kapital | Kapazität: Infrastruktur, Wissen, Lagerung, Resilienz, Gesundheit, Wohnen |
| Investition | Kapazitätsaufbau / Potenzenerhöhung |
| Konsum | Bedürfniswirkung annehmen |
| Sparen | Puffer, Lagerung, Resilienz, Substanzerhalt |
| Steuer | gemeinschaftliche Koordinations-/Zeit-/Substanzbindung |
| Staatsausgaben | Governance, Infrastruktur, Pflege, Bildung, Schutz, Korrektur |
| Außenhandel | innerplanetare Wirkungsflüsse zwischen Bioregionen |
| BIP | planetarer Reproduktionsindex |
| Inflation | nicht modelliert; Preisniveau existiert nicht |
| Arbeitslosigkeit | blockierte oder nicht aktivierte Fähigkeits-/Zeitpotenz |
| Ungleichheit | ungleiche Bedürfnisdeckung, Autonomie, Resilienz, Gesundheit |
| Wachstum | erhöhte Reproduktionsfähigkeit innerhalb planetarer Grenzen |
| Krise | starke Differenz: Bedarf hoch, Potenz/Substanz/Richtung unzureichend |

## Die neue Transaktion

Klassisch:

```text
Ware + Menge + Preis + Eigentumswechsel = Handel
```

In der Simulation:

```text
Phänomen + Differenz + Potenzen + Substanz + Zeit + Winkelrichtung
→ Wirkungsfluss
→ neuer Zustand
```

Eine Transaktion ist daher kein Eigentumswechsel, sondern ein **Wirklichkeitswechsel**.

## Die drei Flow-Typen

### 1. `contribution_offer`

Ersetzt:

```text
verkaufen
Arbeitskraft anbieten
Dienstleistung verkaufen
```

Neue Bedeutung:

```text
Fähigkeit/Zeit/Substanz wird in eine kausale Wirkung eingebracht.
```

### 2. `need_acceptance`

Ersetzt:

```text
kaufen
konsumieren
mieten
Dienstleistung erwerben
```

Neue Bedeutung:

```text
Ein realer Bedarf nimmt eine passende Wirkung an.
```

### 3. `planetary_transfer`

Ersetzt:

```text
Handel
Import
Export
Lieferung nach Kaufkraft
```

Neue Bedeutung:

```text
Überschuss und Mangel werden nach Differenz, Dringlichkeit und Logistik verbunden.
```

## Neue Auswertung

Die Erweiterung erzeugt zusätzlich:

```text
macro_accounts.csv
```

Darin stehen Makrokonten pro Domain und Zeitschritt:

```text
need
available
gap
satisfaction
priority
labor_share
contribution_time
stock_or_capacity
boundary_penalty
truth_error
democratic_quality
activated_flows
```

Und:

```text
effect_flow_audit.csv
```

Darin stehen die Wirkungsflüsse mit Wahrheitswerten. Diese Datei ist die wichtigste Prüfung der neuen Handelslogik.

## Zentrale Formel

```text
Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen
+ Substanz + Materie + Differenz + Bestimmung + Phänomene + Winkelrichtung
→ Priorität
→ Beitrag / Annahme / Transfer
→ neue Wirklichkeit
```

## Zusatzerweiterung: sichtbares Handeln in Dimensionen

Die neuere Fassung schreibt nicht nur einen Wirkungsfluss, sondern auch die ganze Handelssemantik:

```text
Was wird gehandelt?        → trade_object
Was ist damit gemeint?     → meant_as
Welche Produktträger?      → product_examples
Welche Arbeitsplätze?      → workplace_examples
Welche Dienstleistungen?   → service_examples
Welche Ökologiebedingung?  → ecological_clause
Welche Klimabedingung?     → climate_clause
Welche Vertragsgültigkeit? → contract_validity
Welche Bedingungen?        → contract_conditions
Welcher Wahrheitsstapel?   → truth_stack_base5 / truth_stack_score_0_4
```

Damit wird klar: Ein Produkt ist nicht verschwunden. Brot, Wohnung, Werkzeug, Energie, Pflege und Transport existieren weiter. Aber sie werden nicht als Wertding gekauft/verkauft, sondern als **Träger einer kausalen Wirkung** behandelt.

Beispiel:

```text
Brot klassisch:
  Ware Brot + Menge + Preis → Eigentumswechsel

Brot in der Planetenwirtschaft:
  Hunger + Nährstoffbedarf + verfügbare Nahrung + Zeitdringlichkeit
  + Verteilung + Boden-/Klimabedingungen
  → Nahrungswirkung wird angenommen
```

Die Vertragsgültigkeit wird aus den Dimensionen abgeleitet:

```text
Kausalität niedrig    → experimentell / Ursachenprüfung
Zeit hoch             → Notfallpfad
Intensität hoch       → stärkere Einsatzbindung
Existenz unsicher     → Messung und Betroffenenrückmeldung
Potenzen niedrig      → Fähigkeit/Material zuerst aufbauen
Substanz niedrig      → Stofffreigabe bedingt
Materie niedrig       → Logistik/Ort klären
Differenz hoch        → Handlung legitimiert
Bestimmung niedrig    → demokratische Rückkopplung nötig
Phänomene schwach     → Beobachtung/Audit nötig
Winkelrichtung niedrig→ blockieren oder neu entwerfen
```

