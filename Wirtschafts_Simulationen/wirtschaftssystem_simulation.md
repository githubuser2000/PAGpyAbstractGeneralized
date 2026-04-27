# Wirtschaftssysteme simulieren: Warum, wozu, was?

> Ein Wirtschaftssystem simuliert man nicht, um „die Wirtschaft nachzubauen“. Das wäre unmöglich und meistens nutzlos. Man simuliert es, um **kausale Mechanismen unter kontrollierten Bedingungen zu testen**.

Die zentrale Regel lautet:

> **Simuliere nicht alles, was existiert. Simuliere nur das, was für die Frage kausal relevant ist.**

## Inhaltsverzeichnis

1. [Warum überhaupt ein Wirtschaftssystem simulieren?](#1-warum-überhaupt-ein-wirtschaftssystem-simulieren)
2. [Mit welchen Zielen simuliert man?](#2-mit-welchen-zielen-simuliert-man)
3. [Was will man herausfinden?](#3-was-will-man-herausfinden)
4. [Welche Märkte sollte man simulieren?](#4-welche-märkte-sollte-man-simulieren)
5. [Der minimale Kern einer Wirtschaftssimulation](#5-der-minimale-kern-einer-wirtschaftssimulation)
6. [Die wichtigsten Märkte und warum man sie simulieren sollte](#6-die-wichtigsten-märkte-und-warum-man-sie-simulieren-sollte)
7. [Welche Märkte sollte man zuerst simulieren?](#7-welche-märkte-sollte-man-zuerst-simulieren)
8. [Welche Dinge außer Märkten muss man simulieren?](#8-welche-dinge-außer-märkten-muss-man-simulieren)
9. [Welche Modelltypen passen zu welchen Zielen?](#9-welche-modelltypen-passen-zu-welchen-zielen)
10. [Der wichtigste Designgrundsatz](#10-der-wichtigste-designgrundsatz)
11. [Eine sinnvolle allgemeine Architektur](#11-eine-sinnvolle-allgemeine-architektur)
12. [Was eine gute Simulation leisten sollte](#12-was-eine-gute-simulation-leisten-sollte)
13. [Klare Empfehlung](#13-klare-empfehlung)
14. [Praktische Start-Checkliste](#14-praktische-start-checkliste)

## 1. Warum überhaupt ein Wirtschaftssystem simulieren?

Weil reale Wirtschaftssysteme vier Eigenschaften haben, die reine Intuition schnell überfordern.

Erstens gibt es **Rückkopplungen**. Höhere Zinsen senken vielleicht Investitionen, senken dadurch Einkommen, senken Konsum, senken Firmenumsätze, erhöhen Ausfallrisiken, verschärfen Kreditbedingungen — und das wirkt wieder zurück auf Investitionen.

Zweitens gibt es **Heterogenität**. „Der Haushalt“, „die Firma“ oder „der Investor“ existieren in der Realität nicht. Arme Haushalte reagieren anders als reiche. Verschuldete Firmen anders als Cash-reiche. Große Banken anders als kleine.

Drittens gibt es **Nichtlinearitäten**. Ein kleiner Schock kann harmlos sein, aber ab einer Schwelle eine Kaskade auslösen: Bank Runs, Lieferkettenausfälle, Immobiliencrashs, Energiepreisschocks, Liquiditätskrisen.

Viertens gibt es **Institutionen und Friktionen**. Märkte sind nicht einfach freie Preisfindung. Es gibt Kreditlimits, Löhne, Verträge, Regulierung, Monopole, Suchkosten, Informationsasymmetrien, Insolvenzen, Steuern, Zentralbanken und Netzwerkeffekte.

Eine Simulation ist also besonders nützlich, wenn du wissen willst:

> **Welche Dynamik entsteht aus lokalen Entscheidungen vieler Akteure?**

## 2. Mit welchen Zielen simuliert man?

Es gibt unterschiedliche gute Ziele. Schlechte Simulationen vermischen sie. Gute Simulationen wählen eines oder wenige davon klar aus.

### A. Erklärung

Du willst verstehen, warum ein Phänomen entsteht.

Beispiele:

- Warum gibt es Konjunkturzyklen?
- Warum bleiben manche Regionen arm?
- Warum führen Immobilienbooms oft zu Bankenproblemen?
- Warum erzeugen manche Märkte Konzentration und Monopole?

Hier geht es nicht primär um Prognose, sondern um Mechanismen.

### B. Prognose unter Szenarien

Nicht: „Was wird exakt passieren?“

Sondern: „Was passiert wahrscheinlich unter Szenario A, B oder C?“

Beispiele:

- Was passiert mit Inflation, Arbeitslosigkeit und Firmeninsolvenzen, wenn Energiepreise um 40 Prozent steigen?
- Was passiert mit Wohnungsmieten, wenn Zuwanderung steigt, aber Baukapazität begrenzt bleibt?
- Was passiert mit Kreditvergabe, wenn Eigenkapitalanforderungen für Banken erhöht werden?

### C. Politik- und Regulierungsanalyse

Hier fragt man: Welche Maßnahme ist besser, wenn man Nebenwirkungen einbezieht?

Beispiele:

- Mietpreisbremse vs. Wohnungsbauzuschüsse
- CO₂-Steuer vs. Subventionen
- Mindestlohn
- Vermögenssteuer
- Bankenregulierung
- Industriepolitik
- Arbeitslosenversicherung
- Zölle
- Transferprogramme

Das Ziel ist nicht nur Effizienz, sondern auch Verteilung, Stabilität und politische Robustheit.

### D. Krisen- und Stabilitätsanalyse

Hier willst du wissen, wo das System bricht.

Beispiele:

- Wann wird ein Bankenproblem systemisch?
- Welche Firmen sind in einer Lieferkette kritische Knoten?
- Wann wird aus einem Immobilienpreisrückgang eine Kreditkrise?
- Wie viel Energiepreisvolatilität hält eine Industrie aus?

Das ist oft der wichtigste praktische Nutzen von Simulationen: **Stress Tests**.

### E. Marktdesign

Hier simulierst du nicht „die Wirtschaft“, sondern konkrete Regeln eines Marktes.

Beispiele:

- Auktionen für Strom, Frequenzen oder Werbung
- Matching-Märkte für Arbeitsplätze, Schulen oder Organspenden
- Plattformmärkte
- CO₂-Zertifikate
- Strombörsen
- Ride-sharing
- Lieferdienst-Plattformen

Das Ziel: Welche Regeln erzeugen effiziente, faire oder manipulationsresistente Ergebnisse?

### F. Unternehmensstrategie

Eine Firma kann simulieren, wie Preise, Nachfrage, Wettbewerber, Lieferketten und Finanzierung zusammenwirken.

Beispiele:

- Was passiert, wenn wir Preise erhöhen?
- Wie reagiert der Wettbewerb?
- Wie robust ist unsere Lieferkette?
- Wo entstehen Engpässe?
- Wie viel Lagerbestand ist optimal?
- Welche Kundengruppe reagiert am stärksten auf Rabatte?

## 3. Was will man herausfinden?

Eine gute ökonomische Simulation sollte mindestens eine dieser Fragen beantworten.

### 1. Welche Gleichgewichte entstehen?

Wo stabilisieren sich Preise, Löhne, Produktion, Mieten, Zinsen oder Beschäftigung?

Aber Vorsicht: Viele reale Systeme sind nicht ständig im Gleichgewicht. Daher ist die dynamische Frage oft wichtiger.

### 2. Welche Übergangsdynamik entsteht?

Wie kommt das System von Zustand A nach Zustand B?

Das ist zentral, weil kurzfristige Anpassungskosten politisch und wirtschaftlich oft wichtiger sind als ein schöner langfristiger Endzustand.

Beispiel: Eine CO₂-Steuer kann langfristig effizient sein, aber kurzfristig bestimmte Branchen, Haushalte oder Regionen hart treffen.

### 3. Wer trägt Kosten und wer erhält Gewinne?

Eine Simulation, die nur aggregiertes BIP, Durchschnittseinkommen oder Gesamtwohlfahrt betrachtet, ist oft blind.

Wichtiger ist:

- Wer verliert Einkommen?
- Wer verliert Vermögen?
- Wer bekommt Zugang zu Kredit?
- Wer wird aus dem Wohnungsmarkt gedrängt?
- Welche Firmen überleben?
- Welche Regionen profitieren?

### 4. Wo liegen Schwellenwerte?

Viele Systeme kippen nicht linear.

Beispiele:

- Bei 5 Prozent Kreditausfällen bleibt das Bankensystem stabil.
- Bei 8 Prozent ziehen Banken Kreditlinien zurück.
- Bei 12 Prozent kommt es zu Fire Sales.
- Bei 15 Prozent entsteht eine systemische Krise.

Solche Kipppunkte erkennt man durch Simulation oft besser als durch statische Analyse.

### 5. Welche Rückkopplungen dominieren?

In komplexen Systemen sind nicht alle Mechanismen gleich wichtig.

Eine gute Simulation hilft zu erkennen:

- Ist das Problem Nachfrage?
- Angebot?
- Kredit?
- Erwartungen?
- Marktmacht?
- Energie?
- Arbeitskräfte?
- Regulierung?
- Liquidität?
- Vertrauen?

### 6. Welche Politik ist robust?

Eine Maßnahme, die in einem Modell gut aussieht, aber bei kleinen Parameteränderungen kollabiert, ist gefährlich.

Deshalb testet man Szenarien:

- Was, wenn Haushalte anders sparen?
- Was, wenn Banken risikoscheuer sind?
- Was, wenn Produktivität niedriger ist?
- Was, wenn Energiepreise stärker schwanken?
- Was, wenn Firmen Marktmacht haben?

Robustheit ist oft wichtiger als theoretische Optimalität.

## 4. Welche Märkte sollte man simulieren?

Das hängt vom Erkenntnisziel ab. Trotzdem gibt es einige zentrale Märkte, weil sie in fast jedem Wirtschaftssystem starke Rückkopplungen erzeugen.

Die erste Frage ist nicht: „Welche Märkte existieren?“

Die bessere Frage ist:

> **Welche Märkte übertragen, verstärken oder dämpfen genau den Mechanismus, den ich untersuchen will?**

## 5. Der minimale Kern einer Wirtschaftssimulation

Für eine allgemeine Wirtschaftssimulation würde ich mindestens diese Bestandteile modellieren:

| Bestandteil | Warum er wichtig ist |
|---|---|
| Haushalte | Konsum, Arbeit, Sparen, Verschuldung, Verteilung |
| Firmen | Produktion, Preise, Löhne, Investitionen, Gewinne, Insolvenzen |
| Arbeitsmarkt | Einkommen, Beschäftigung, Lohnbildung, Ungleichheit |
| Gütermarkt | Nachfrage, Angebot, Preise, Inflation |
| Kredit-/Bankensystem | Geldschöpfung, Investition, Hebel, Krisen |
| Staat | Steuern, Ausgaben, Transfers, Schulden, Regulierung |
| Zentralbank/Geldpolitik | Zinsen, Liquidität, Inflation, Kreditbedingungen |
| Kapital/Investitionen | Produktivität, Kapazität, Wachstum |
| Vermögensmärkte | Immobilien, Aktien, Anleihen, Sicherheiten, Vermögenseffekte |
| Außenhandel, falls offene Volkswirtschaft | Wechselkurse, Importe, Exporte, externe Schocks |

Wenn du nur „Güterangebot und Güternachfrage“ simulierst, hast du ein Spielzeug. Sobald du Kredit, Vermögen, Erwartungen und Bilanzen hinzufügst, wird es ökonomisch ernst.

## 6. Die wichtigsten Märkte und warum man sie simulieren sollte

### 1. Güter- und Konsummärkte

Hier entstehen Preise, Umsätze, Produktionsentscheidungen und Inflation.

Diese Märkte solltest du simulieren, wenn du Fragen hast wie:

- Warum steigen Preise?
- Wie reagieren Konsumenten auf Einkommensschocks?
- Wie geben Firmen Kostensteigerungen weiter?
- Wie wirken Steuern oder Subventionen auf Nachfrage und Produktion?

Wichtig sind hier:

- Preissetzung
- Nachfrageelastizität
- Lagerbestände
- Wettbewerb
- Marktmacht
- Lieferengpässe
- Konsumentenheterogenität

Ohne Gütermärkte fehlt der direkte Ort, an dem reale Produktion und Konsum zusammenkommen.

### 2. Arbeitsmarkt

Der Arbeitsmarkt ist zentral, weil er Einkommen, Produktion, soziale Stabilität und politische Konflikte verbindet.

Man simuliert ihn, um herauszufinden:

- Wie entsteht Arbeitslosigkeit?
- Wie wirken Mindestlöhne?
- Wie schnell finden Menschen neue Jobs?
- Wie beeinflussen Löhne Inflation?
- Wie verändern Automatisierung oder Migration Beschäftigung und Lohnstruktur?

Wichtige Mechanismen:

- Matching
- Suchkosten
- Qualifikation
- regionale Mobilität
- Gewerkschaften
- Lohnstarrheit
- Verhandlungsmacht
- informelle Arbeit

Ein perfekter Arbeitsmarkt mit sofortiger Anpassung ist für viele reale Fragen nutzlos. Gerade die Friktionen sind interessant.

### 3. Kredit- und Bankenmarkt

Das ist einer der wichtigsten Märkte überhaupt, weil Kredit Investitionen, Konsum, Immobilien, Firmenwachstum und Krisen ermöglicht.

Man simuliert Kreditmärkte, wenn man wissen will:

- Wann wird Verschuldung gefährlich?
- Wie entstehen Finanzkrisen?
- Wie wirken Zinsen?
- Warum brechen Investitionen plötzlich ein?
- Wie übertragen sich Ausfälle von Firmen auf Banken und zurück auf Firmen?

Wichtige Variablen:

- Bankbilanzen
- Eigenkapital
- Sicherheiten
- Ausfallraten
- Risikoprämien
- Kreditrationierung
- Liquidität
- Interbankenverflechtung
- Zentralbankpolitik

Viele Wirtschaftssimulationen sind schwach, weil sie Geld und Kredit zu harmlos behandeln. In der Realität ist Kredit nicht nur ein Schleier über der Realwirtschaft. Er ist ein Verstärker.

### 4. Kapital- und Investitionsgütermärkte

Hier entscheidet sich, wie viel zukünftige Produktionskapazität entsteht.

Man simuliert sie, wenn man Wachstum, Produktivität, Strukturwandel oder Industriepolitik verstehen will.

Fragen:

- Wann investieren Firmen?
- Wie wirken Zinssätze?
- Wie schnell kann eine Wirtschaft neue Kapazitäten aufbauen?
- Welche Branchen schrumpfen oder expandieren?
- Wie wirken Unsicherheit und erwartete Nachfrage?

Wichtig sind:

- Kapitalstock
- Abschreibungen
- Kapazitätsauslastung
- Investitionskosten
- Finanzierung
- Technologie
- Erwartungen

Ohne Investitionen bleibt die Simulation statisch.

### 5. Immobilien- und Bodenmärkte

Immobilien sind besonders wichtig, weil sie Konsumgut, Vermögenswert und Kreditsicherheit zugleich sind.

Man simuliert sie, wenn man wissen will:

- Warum steigen Mieten?
- Wie entstehen Immobilienblasen?
- Warum ist Wohnraum knapp?
- Wie wirken Bauvorschriften, Zinsen, Migration, Einkommen oder Spekulation?
- Wie treffen Immobilienpreise das Bankensystem?

Wichtige Mechanismen:

- Bodenknappheit
- Bauverzögerungen
- Regulierung
- Hypotheken
- Mieten
- Leerstand
- Eigentum vs. Miete
- regionale Nachfrage
- Beleihungswerte

Der Immobilienmarkt ist oft der Ort, an dem Finanzsystem, Ungleichheit und reale Lebensqualität zusammenstoßen.

### 6. Energiemärkte

Energie ist kein normaler Markt. Sie ist ein Input fast aller anderen Märkte.

Man simuliert Energiemärkte, wenn man Inflation, Industrieproduktion, Klimapolitik, Versorgungssicherheit oder geopolitische Schocks verstehen will.

Fragen:

- Wie wirken Energiepreisschocks auf Inflation?
- Welche Industrien werden unrentabel?
- Wie stabil ist ein Stromsystem mit viel erneuerbarer Energie?
- Wie wirken CO₂-Preise?
- Welche Rolle spielen Speicher, Netze und Grundlast?

Wichtige Mechanismen:

- Grenzkosten
- Netzkapazität
- Speicher
- Importabhängigkeit
- Preisspitzen
- Substitution
- Regulierung
- Emissionspreise

Ein Energieschock ist oft kein isolierter Preisschock, sondern ein systemweiter Kostenschock.

### 7. Finanzmärkte

Finanzmärkte sollte man simulieren, wenn Erwartungen, Liquidität, Vermögenseffekte oder Ansteckung wichtig sind.

Fragen:

- Wie entstehen Blasen?
- Wann kommt es zu Fire Sales?
- Wie übertragen sich Schocks zwischen Aktien, Anleihen, Banken und Immobilien?
- Wie wirken Margin Calls?
- Wie wichtig sind Liquidität und Vertrauen?

Wichtige Mechanismen:

- Hebel
- Liquiditätsbedarf
- Bewertungsänderungen
- Risikoprämien
- Erwartungen
- Portfolioumschichtungen
- institutionelle Investoren

Finanzmärkte sind nicht nur „Casino“. Sie beeinflussen Finanzierungskosten, Vermögen, Sicherheiten und Vertrauen.

### 8. Außenhandel und Devisenmärkte

Diese brauchst du, sobald die Wirtschaft offen ist.

Fragen:

- Wie wirken Zölle?
- Was passiert bei Wechselkursschocks?
- Wie abhängig ist eine Wirtschaft von Importen?
- Wie übertragen sich globale Lieferkettenprobleme?
- Wie wirken Kapitalflüsse?

Wichtige Mechanismen:

- Importpreise
- Exportnachfrage
- Wechselkurse
- Handelsbilanzen
- Kapitalflüsse
- globale Lieferketten
- geopolitische Risiken

Für kleine offene Volkswirtschaften ist dieser Block nicht optional.

### 9. Plattform-, Daten- und Aufmerksamkeitsmärkte

Für moderne digitale Ökonomien sind diese Märkte besonders wichtig.

Fragen:

- Warum entstehen Winner-take-most-Strukturen?
- Wie wirken Netzwerkeffekte?
- Wann wird eine Plattform monopolistisch?
- Wie beeinflussen Rankings, Empfehlungen und Datenvorteile Wettbewerb?

Wichtige Mechanismen:

- Netzwerkeffekte
- Skalenerträge
- Datenakkumulation
- Lock-in
- Multi-Homing
- algorithmische Preis- oder Nachfrageverteilung

Diese Märkte sind klassisch schlecht durch einfache Angebots-Nachfrage-Modelle erklärbar.

### 10. Versicherungs-, Gesundheits- und Bildungssektor

Diese sind keine normalen Märkte, weil Information, Risiko und öffentliche Interessen stark verzerrend wirken.

Man simuliert sie, wenn man Wohlfahrt, Humankapital, soziale Mobilität oder staatliche Ausgaben verstehen will.

Fragen:

- Wie wirken Versicherungspflichten?
- Wie entstehen adverse Selektion und moral hazard?
- Wie beeinflusst Bildung langfristiges Einkommen?
- Wie wirken Studiengebühren, Gesundheitskosten oder Rentensysteme?

Hier sind Institutionen oft wichtiger als Preise.

## 7. Welche Märkte sollte man zuerst simulieren?

Ich würde nach Erkenntnisziel priorisieren.

### Wenn du Konjunktur und Inflation verstehen willst

Simuliere:

1. Gütermärkte
2. Arbeitsmarkt
3. Kreditmarkt
4. Energie/Importe
5. Staat/Zentralbank

Warum? Inflation entsteht nicht nur aus „zu viel Geld“. Sie kann aus Nachfrage, Angebot, Löhnen, Energie, Wechselkursen, Marktmacht oder Erwartungen entstehen.

### Wenn du Finanzkrisen verstehen willst

Simuliere:

1. Banken und Kredit
2. Immobilien/Sicherheiten
3. Firmenbilanzen
4. Haushaltsverschuldung
5. Finanzmärkte
6. Zentralbank/Liquidität

Warum? Krisen entstehen oft durch Bilanzverknüpfungen, Hebel und Vertrauen, nicht durch den Gütermarkt allein.

### Wenn du Ungleichheit verstehen willst

Simuliere:

1. Arbeitsmarkt
2. Bildung/Qualifikation
3. Vermögensmärkte
4. Immobilien
5. Steuern/Transfers
6. Erbschaften und Kapitalerträge

Warum? Ungleichheit entsteht nicht nur durch Löhne. Vermögen, Immobilien, Bildung, Erbschaften und Zugang zu Kapital sind oft entscheidender.

### Wenn du Wachstum und Innovation verstehen willst

Simuliere:

1. Firmeninvestitionen
2. Kapitalstock
3. Forschung/Technologie
4. Arbeitskräfte und Bildung
5. Kredit/Finanzierung
6. Wettbewerb und Markteintritt

Warum? Wachstum ist nicht einfach mehr Konsum, sondern Kapazitätsaufbau, Produktivität und institutionelle Dynamik.

### Wenn du Klimapolitik verstehen willst

Simuliere:

1. Energie
2. Industrieproduktion
3. Haushaltskonsum
4. Investitionen
5. staatliche CO₂-Politik
6. Verteilungseffekte
7. internationale Wettbewerbsfähigkeit

Warum? Klimapolitik ist ein Strukturwandelproblem, kein isoliertes Steuerproblem.

### Wenn du Wohnungsnot verstehen willst

Simuliere:

1. Bodenmarkt
2. Baukapazitäten
3. Mieten
4. Einkommen
5. Zinsen/Hypotheken
6. Regulierung
7. Migration und Haushaltsbildung

Warum? Wohnungsmärkte reagieren langsam. Bau dauert. Boden ist knapp. Kreditbedingungen treiben Preise. Regulierung verändert Angebot.

## 8. Welche Dinge außer Märkten muss man simulieren?

Ein großer Fehler ist zu glauben, Wirtschaft bestehe nur aus Märkten. Viele entscheidende Dinge sind keine Märkte, sondern Regeln, Bilanzen und Institutionen.

### A. Bilanzen

Jede Forderung ist irgendwo eine Verbindlichkeit. Jedes Defizit ist irgendwo ein Überschuss. Jeder Kredit erzeugt eine Schuldner-Gläubiger-Beziehung.

Eine gute Simulation muss konsistent sein:

- Haushalte haben Einkommen, Ausgaben, Vermögen und Schulden.
- Firmen haben Umsätze, Kosten, Kapital und Kredite.
- Banken haben Aktiva, Passiva und Eigenkapital.
- Der Staat hat Einnahmen, Ausgaben und Schulden.

Ohne Bilanzlogik produziert man schnell ökonomische Fantasie.

### B. Erwartungen

Akteure handeln nicht nur nach Gegenwartsdaten, sondern nach Erwartungen.

- Firmen investieren, wenn sie Nachfrage erwarten.
- Haushalte sparen, wenn sie Unsicherheit erwarten.
- Banken vergeben Kredit, wenn sie Rückzahlung erwarten.
- Investoren kaufen, wenn sie Preissteigerungen erwarten.

Erwartungen können stabilisieren oder destabilisieren.

### C. Institutionen

Steuern, Arbeitsrecht, Insolvenzrecht, Mietrecht, Bankenregulierung, Zentralbankregeln, Sozialversicherung, Subventionen und Wettbewerbsrecht formen Märkte.

Institutionen sind nicht „Details“. Sie bestimmen oft das Ergebnis.

### D. Netzwerke

Lieferketten, Bankverflechtungen, soziale Netzwerke, regionale Arbeitsmärkte und Plattformen sind Netzwerke.

Netzwerke sind wichtig, weil sie Kaskaden ermöglichen. Ein einzelner Ausfall kann harmlos oder systemisch sein — je nachdem, wo er im Netzwerk liegt.

### E. Zeitverzögerungen

Viele Anpassungen passieren nicht sofort.

Bau dauert. Umschulung dauert. Investitionen dauern. Kreditprüfung dauert. Preisverhandlungen dauern. Löhne ändern sich nicht täglich. Infrastruktur dauert Jahre.

Zeitverzögerungen erzeugen Zyklen, Engpässe und Überreaktionen.

## 9. Welche Modelltypen passen zu welchen Zielen?

### Gleichgewichtsmodelle

Gut für:

- Steuerpolitik
- Handelsmodelle
- langfristige Allokation
- Effizienzvergleiche

Schwach bei:

- Krisen
- Instabilität
- Heterogenität
- Netzwerken
- plötzlichen Kaskaden

### Agentenbasierte Modelle

Gut für:

- heterogene Akteure
- emergente Dynamiken
- Märkte mit Friktionen
- Krisen
- Netzwerke
- Verteilung

Schwach bei:

- Kalibrierung
- Interpretierbarkeit
- sauberer Identifikation
- Rechenaufwand

### Stock-Flow-Consistent-Modelle

Gut für:

- Geld
- Kredit
- Bilanzen
- sektorale Finanzierungsströme
- Makro-Stabilität

Schwach bei:

- Mikroverhalten
- detailliertem Marktdesign
- granularen Netzwerken

### Netzwerkmodelle

Gut für:

- Lieferketten
- Banken
- Ansteckung
- systemische Risiken

Schwach bei:

- allgemeiner Makroökonomie, wenn sie isoliert genutzt werden

### Spieltheoretische oder auktionstheoretische Simulationen

Gut für:

- Marktdesign
- Plattformen
- Strommärkte
- Frequenzauktionen
- Bietstrategien

Schwach bei:

- breiter Makro- und Verteilungsdynamik

## 10. Der wichtigste Designgrundsatz

Baue nicht zuerst ein großes Modell. Baue zuerst die **kleinste Simulation, die deine Frage beantworten kann**.

Schlechte Frage:

> „Ich möchte die Wirtschaft simulieren.“

Bessere Frage:

> „Ich möchte wissen, ob steigende Zinsen in einem hochverschuldeten Immobilienmarkt zuerst Konsum, Bauinvestitionen oder Bankstabilität treffen.“

Dann weißt du, was du brauchst:

- Haushalte
- Hypotheken
- Banken
- Immobilienpreise
- Bauwirtschaft
- Zinssatz
- Ausfälle
- Konsum

Du brauchst vielleicht keinen internationalen Handel, keine Bildung, keine Plattformmärkte und keine Landwirtschaft.

## 11. Eine sinnvolle allgemeine Architektur

Für ein ernsthaftes, aber noch kontrollierbares Modell würde ich so starten.

### Agenten

- Haushalte
- Firmen
- Banken
- Staat
- Zentralbank
- eventuell Ausland

### Märkte

- Arbeitsmarkt
- Gütermarkt
- Kreditmarkt
- Immobilienmarkt
- Energiemarkt
- Kapitalmarkt

### Zustände

- Einkommen
- Vermögen
- Schulden
- Preise
- Löhne
- Beschäftigung
- Produktion
- Kapitalstock
- Lagerbestände
- Bankkapital
- Staatsverschuldung

### Entscheidungen

- Haushalte konsumieren, sparen, arbeiten und leihen.
- Firmen setzen Preise, produzieren, investieren, stellen ein, entlassen und leihen.
- Banken vergeben Kredite, verlangen Sicherheiten und reagieren auf Ausfälle.
- Staat besteuert, transferiert und investiert.
- Zentralbank setzt Zinsen oder Liquiditätsbedingungen.

### Schocks

- Zinsschock
- Produktivitätsschock
- Energiepreisschock
- Nachfrageeinbruch
- Bankenverlust
- Migrationsschock
- Lieferkettenausfall
- Steueränderung
- Regulierung

### Outputs

- BIP
- Inflation
- Arbeitslosigkeit
- Löhne
- Gewinne
- Insolvenzen
- Kreditvolumen
- Ausfallraten
- Vermögensverteilung
- Mieten
- Staatsdefizit
- Energieverbrauch
- Wohlfahrt nach Gruppen

## 12. Was eine gute Simulation leisten sollte

Eine gute Wirtschaftssimulation sollte nicht nur Kurven ausspucken. Sie sollte erklären:

- Warum passiert etwas?
- Über welchen Kanal passiert es?
- Mit welcher Zeitverzögerung?
- Wer ist betroffen?
- Welche Annahmen sind entscheidend?
- Welche Politik ändert wirklich etwas?
- Wo ist das System fragil?

Die beste Simulation ist nicht die mit den meisten Variablen. Es ist die, bei der du nach einem Experiment sagen kannst:

> „Jetzt weiß ich, welcher Mechanismus das Ergebnis erzeugt.“

## 13. Klare Empfehlung

Wenn du ein Wirtschaftssystem simulieren willst, beginne nicht mit „allen Märkten“. Beginne mit diesen drei Kernfragen:

1. **Welche Dynamik interessiert mich?**  
   Inflation, Krise, Wachstum, Ungleichheit, Wohnungsnot, Klimawandel, Arbeitslosigkeit, Marktmacht?

2. **Welche Mechanismen könnten diese Dynamik verursachen?**  
   Kredit, Löhne, Energie, Erwartungen, Vermögen, Regulierung, Netzwerke, Marktmacht?

3. **Welche Märkte sind dafür unvermeidlich?**  
   Nur diese gehören zuerst ins Modell.

Für eine breite Wirtschaftssimulation wären die ersten Märkte fast immer:

> **Arbeitsmarkt, Gütermarkt, Kreditmarkt, Kapital-/Investitionsmarkt, Immobilienmarkt, Energiemarkt und Staat/Zentralbank als institutioneller Rahmen.**

Danach ergänzt man je nach Ziel: Außenhandel, Finanzmärkte, Plattformmärkte, Bildung, Gesundheit, Versicherungen, Lieferketten oder regionale Märkte.

Die nüchterne Wahrheit ist:

> Eine Wirtschaftssimulation wird nur dann wertvoll, wenn sie nicht versucht, die Welt vollständig abzubilden, sondern wenn sie die entscheidenden Kausalmechanismen brutal klar isoliert.

## 14. Praktische Start-Checkliste

Vor dem Bau einer Simulation solltest du diese Fragen beantworten:

| Frage | Warum sie wichtig ist |
|---|---|
| Welche konkrete Hypothese teste ich? | Verhindert ein zielloses Universalmodell. |
| Welche Akteure entscheiden wirklich? | Bestimmt Agenten und Verhaltensregeln. |
| Welche Märkte übertragen die Wirkung? | Bestimmt Modellgrenzen. |
| Welche Bestände und Flüsse müssen bilanziell konsistent sein? | Verhindert ökonomisch unmögliche Ergebnisse. |
| Welche Friktionen sind kausal wichtig? | Macht das Modell realistisch genug. |
| Welche Schocks oder Politiken will ich testen? | Definiert Experimente. |
| Welche Outputs entscheiden über Erfolg oder Misserfolg? | Verhindert falsche Zielgrößen. |
| Welche Parameter sind unsicher? | Erzwingt Sensitivitätsanalyse. |
| Für wen sind die Ergebnisse relevant? | Erzwingt Verteilungsanalyse. |
| Was wäre ein Gegenbeweis gegen meine Hypothese? | Schützt vor Modellbestätigung statt Erkenntnis. |
