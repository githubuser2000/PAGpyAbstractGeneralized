# Q-Ökonomie: vollständiges Wirtschaftssystem einer Zeilenwert-Währung

**Sprache:** Deutsch  
**Version:** 1.0  
**Grundlage:** Die Währung besteht aus Q-Münzen. Die Zeilenhöhe ist der Münzenwert.

---

## 1. Grundidee

Die Q-Ökonomie ist eine semantische Geld-, Kredit- und Produktionsordnung. Sie behandelt nicht nur Geld als ökonomische Einheit, sondern auch Schwierigkeit, Struktur, Code, Schnittstellen, Architektur, Betrieb und fertige Module.

Eine Münze ist eine Tabellenzeile. **Die Zeilenhöhe** ist ihr Wert. **Die Nummerierung** ist ihre Prägung. Der Text im Kontinuum ist ihre semantische Deckung.

```text
Münze Qn = (Nummer n, Wert h, Bedeutung B)
Wert(Qn) = Zeilenhöhe h
Bedeutung(Qn) = semantischer Inhalt im Kontinuum
```

Q20 bedeutet deshalb nicht „zwanzig Einheiten“. Q20 ist die Münze mit der Prägung 20 und dem Wert 4. Vier Q1-Münzen können denselben Nominalwert wie eine Q20-Münze haben, aber sie erfüllen nicht dieselbe Funktion.

---

## 2. Basiseinheiten

Die Basiseinheit heißt **Zeilenwert**.

```text
1 ZW = 1 Zeilenwert
```

Als kleinere Untereinheit kann das **Oktadegramm** verwendet werden:

```text
1 ZW = 18 Oktadegramm
```

Damit gilt:

```text
Wert 1 = 1 ZW = 18 Oktadegramm
Wert 2 = 2 ZW = 36 Oktadegramm
Wert 3 = 3 ZW = 54 Oktadegramm
Wert 4 = 4 ZW = 72 Oktadegramm
```

---

## 3. Münzkatalog

| Münze | Wert | Schicht | Wirtschaftliche Bedeutung |
|---:|---:|---|---|
| Q1 | 1 | Grundschwierigkeit | Aufgabe, Schwierigkeit, Knoten, Problemkern |
| Q2 | 1 | Komplexität | Teil, Kompliziertheit, Molekülelement, Teilstruktur |
| Q3 | 1 | Abstraktion | Theorie, Modell, Zwischenzustand zwischen locker und fest |
| Q4 | 1 | Kristallisation | formales Objekt, Faden, mathematische Gestalt |
| Q5 | 2 | Operation | Enkodieren, Befehl, Kommando, imperatives Programmieren |
| Q6 | 2 | Deklaration | deklarative Beschreibung, Regel, Faden statt Befehl |
| Q7 | 2 | Delegation | Delegieren, Referenzieren, Verantwortungsübertragung |
| Q8 | 2 | Bibliothek | wiederverwendbarer Stein, Wabe, Mineral, Bausteinsammlung |
| Q9 | 2 | Framework | Rahmen, Organisches, Struktur allgemeiner Intelligenz |
| Q10 | 3 | Constraint | Beschränkung, Struktur, Strick, Möglichkeitsraum |
| Q11 | 3 | Schnittstelle | Eingriff, Interface, Gedankeneinsatz |
| Q12 | 3 | Toolbox | Methoden, Mathematik, Algebra, Analysis, Topologie, Kategorien-Theorie |
| Q13 | 3 | Programm | Service, Paradigma, Dienst, Gedankenansatz |
| Q14 | 3 | Orchestrierung | Komposition, Choreographie, Dirigieren, Meisterung |
| Q15 | 3 | Anwendung | Applikation, Werk, Opus |
| Q16 | 3 | Betrieb | Menü, Kernel, Betriebssystem, Ausführung |
| Q17 | 4 | Kompression | Komprimieren; inverse Operation: Dekomprimieren |
| Q18 | 4 | Architektur | Konstruktion, Bauplan, tragende Gesamtform |
| Q19 | 4 | Generierung | Erzeugung; inverse Bewegung: Degenerierung oder Dekadenz |
| Q20 | 4 | Modul/Maschine | fertige Entwicklung, Gerät, Muster, Schwierigkeitsmaschine |

Die vier Wertschichten:

```text
Wert 1: Q1–Q4     Grundmünzen
Wert 2: Q5–Q9     Operationsmünzen
Wert 3: Q10–Q16   Systemmünzen
Wert 4: Q17–Q20   Kapitalmünzen
```

---

## 4. Addition, Vermögen und Portfolio

Münzen können addiert werden. Addiert wird zuerst der Zeilenwert.

Beispiel:

```text
2 × Q1
1 × Q8
3 × Q10
1 × Q20
```

Nominalwert:

```text
2 × 1 ZW = 2 ZW
1 × 2 ZW = 2 ZW
3 × 3 ZW = 9 ZW
1 × 4 ZW = 4 ZW
Gesamtwert = 17 ZW
```

In Oktadegramm:

```text
17 ZW × 18 = 306 Oktadegramm
```

Portfolio:

```text
Wallet = (Q1:2, Q8:1, Q10:3, Q20:1)
Wert = 17 ZW
```

Wichtig: Gleicher Nominalwert bedeutet nicht gleiche semantische Funktion.

```text
4 × Q1 = 4 ZW
1 × Q20 = 4 ZW
aber: 4 × Q1 ≠ 1 × Q20
```

Vier Aufgabenkerne sind noch keine fertige Maschine. Eine fertige Maschine kann in Aufgabenkerne zerlegt werden, aber sie ist ihnen nicht gleich.

---

## 5. Schulden und inverse Operationen

Schulden sind negative Münzbestände.

```text
-1 × Q18 = ich schulde eine Architektureinheit
```

Ein Konto kann nominal positiv, aber semantisch gefährdet sein:

```text
+3 × Q5 -1 × Q10
```

Nominal:

```text
3 × Q5 = 6 ZW
-1 × Q10 = -3 ZW
Netto = +3 ZW
```

Semantisch fehlt aber Q10, also Struktur und Beschränkung.

> Ein Akteur kann nominal reich und semantisch illiquide sein.

Schuld und inverse Operation sind verschieden:

```text
-Q17  = Schuld an Kompression
1/Q17 = Dekompression
-Q19  = Schuld an Generierung
1/Q19 = Degenerierung
```

Vier Schuldarten:

| Schuldart | Bedeutung | Beispiel |
|---|---|---|
| Wertschuld | nur ein Wertbetrag wird geschuldet | 10 ZW |
| Höhenschuld | eine Wertklasse wird geschuldet | drei Münzen der Höhe 2 |
| Typenschuld | eine bestimmte Münzart wird geschuldet | 2 × Q10 |
| Projektschuld | eine konkrete Leistung wird geschuldet | Q13-Service mit Q11-Schnittstelle |

---

## 6. Konten, Bilanz und Reichtum

Ein Konto ist kein einzelner Kontostand, sondern ein Vektor aus 20 Münzarten.

```text
Konto A:
Q1:  10
Q2:   5
Q3:   2
Q5:   8
Q6:  -1
Q8:   3
Q9:   1
Q10: -2
Q20:  1
```

Negative Werte sind Schulden. Das Konto wird zweifach gelesen:

```text
Nominale Lesart = Summe aller Bestände × Zeilenwert
Semantische Bilanz = Überschüsse und Mängel je Münzart
```

Drei Reichtumsformen:

1. **Nominaler Reichtum:** Gesamtwert in ZW.
2. **Semantischer Reichtum:** Besitz der richtigen Münzarten für reale Handlungsfähigkeit.
3. **Liquiditätsreichtum:** Fähigkeit, fällige Schulden in der richtigen Münzart zu bedienen.

Eine Firma mit viel Q5 und Q13 besitzt viel Code und viele Services. Wenn sie zugleich Q10, Q16 und Q18 schuldet, hat sie Struktur-, Betriebs- und Architekturschulden.

---

## 7. Märkte

Die Q-Ökonomie braucht mehrere Märkte.

### Münzmarkt

Q-Münzen werden gegeneinander getauscht:

```text
1 × Q20 gegen 4 × Q1
1 × Q18 gegen 2 × Q5
1 × Q13 gegen 1 × Q10
```

Ein Tausch kann nominal ausgeglichen, aber semantisch unausgeglichen sein.

### Arbeitsmarkt

Menschen oder Agenten verkaufen Leistungen:

```text
Q5-Arbeit: Kodieren
Q6-Arbeit: Spezifikation
Q10-Arbeit: Constraints und Struktur
Q11-Arbeit: Schnittstellen
Q18-Arbeit: Architektur
Q20-Arbeit: Modulbau
```

### Gütermarkt

Produkte und Dienste haben eine Q-Signatur. Beispiel:

```text
Analyse-Service:
Q10: 2
Q11: 1
Q12: 1
Q13: 2
Q16: 1
```

### Kreditmarkt

Hier werden Forderungen und Schulden gehandelt.

```text
A schuldet B 5 × Q18.
B verkauft die Forderung an C.
C zahlt wegen Ausfallrisiko weniger als den Nennwert.
```

### Terminmarkt

Hier werden zukünftige Lieferungen gehandelt.

```text
Lieferung in 30 Tagen: 3 × Q13 + 1 × Q16
Preis heute: 12 ZW
```

### Versicherungsmarkt

Versicherungen decken Ausfälle bestimmter Münzarten, besonders Q16, Q18 und Q20.

### Gemeingütermarkt

Q8, Q9, Q12 und Q16 sind häufig Gemeingüter. Bibliotheken, Frameworks, Werkzeuge und Infrastruktur müssen teilweise öffentlich oder gemeinschaftlich finanziert werden.

---

## 8. Preise und Wechselkurse

Es gibt Nominalpreis und Marktpreis.

```text
Nominalpreis(Qi) = Zeilenwert h(Qi)
```

Der Marktpreis entsteht aus Knappheit, Qualität, Dringlichkeit und Vertrauen:

```text
Marktpreis(Qi) =
Nominalwert(Qi)
× Knappheit
× Qualitätsfaktor
× Dringlichkeitsfaktor
× Vertrauensfaktor
```

Beispiel:

```text
Q18 nominal = 4 ZW
Knappheit: ×1,5
Qualität: ×1,2
Dringlichkeit: ×1,3
Vertrauen: ×1,1
Marktpreis = 4 × 1,5 × 1,2 × 1,3 × 1,1 = 10,296 ZW
```

Bei Typenschulden reicht gleicher Nominalwert nicht aus. Wer Q18 schuldet, kann nicht automatisch mit Q17 zahlen. Der Gläubiger kann einen semantischen Abschlag festlegen:

```text
1 × Q17 zählt als 60 % Ersatz für 1 × Q18
```

Das heißt **semantischer Haircut**.

---

## 9. Produktion und Produktionsrezepte

Produktion heißt: Schwierigkeit wird in strukturierte, ausführbare und wiederverwendbare Formen verwandelt.

Hauptwertkette:

```text
Q1 Aufgabe
→ Q2 Zerlegung
→ Q3 Abstraktion
→ Q4 formale Gestalt
→ Q5/Q6 Programmierung oder Spezifikation
→ Q8/Q9 Wiederverwendung und Rahmen
→ Q10/Q11 Struktur und Schnittstelle
→ Q13 Service
→ Q15 Anwendung
→ Q18 Architektur
→ Q20 Maschine/Modul
```

Produktionsrezepte:

```text
Output Q5 Kodierleistung:
Q1 Aufgabe + Q3 Modell + Arbeitszeit

Output Q6 Spezifikation:
Q1 Aufgabe + Q3 Abstraktion + Q10 Constraint

Output Q8 Bibliothek:
mehrere Q5 + mindestens ein Q6 + Q12 Werkzeugkompetenz + Q17 Kompression

Output Q9 Framework:
Q8 Bibliotheken + Q10 Constraints + Q11 Schnittstellen + Q13 Dienstlogik

Output Q13 Service:
Q5 Code + Q6 Spezifikation + Q10 Constraints + Q11 Schnittstelle + Q8 Bibliothek

Output Q18 Architektur:
Q10 Constraints + Q11 Schnittstellen + Q14 Orchestrierung + Q17 Kompression + Q3/Q4 Gestalt

Output Q20 Modul/Maschine:
Q13 Programm + Q15 Anwendung + Q16 Betrieb + Q18 Architektur + Q19 Generierung
```

---

## 10. Geldschöpfung und Münzamt

Neue Münzen entstehen nicht willkürlich. Sie werden geprägt, wenn eine Leistung geprüft und anerkannt wurde.

```text
validierte Architektur → neue Q18-Münzen
validierter Service → neue Q13-Münzen
validiertes Modul → neue Q20-Münzen
```

Das Münzamt hat fünf Aufgaben:

```text
1. Münzen prägen
2. Münzen vernichten
3. Münzarten klassifizieren
4. Fälschungen verhindern
5. Preisstabilität sichern
```

Die Währung ist nicht durch Gold gedeckt, sondern durch **verifizierte semantische Arbeit**.

Validatoren prüfen Arbeit:

```text
Q5-Validator prüft Code.
Q6-Validator prüft Spezifikationen.
Q10-Validator prüft Constraints.
Q18-Validator prüft Architektur.
Q20-Validator prüft Modulreife.
```

Falsche Validierung führt zu Reputationsverlust und Strafschulden.

---

## 11. Banken, Kredit und Zinsen

Banken vergeben Kredit, erzeugen aber nicht automatisch echten Wert. Kredit schafft Zahlungsfähigkeit; Deckung entsteht erst durch produktive Arbeit.

Beispiel:

```text
Bank leiht Firma F:
3 × Q18
2 × Q13

Firma F erhält:
+3 Q18 +2 Q13

Gleichzeitig entsteht:
-3 Q18 -2 Q13 plus Zinsen
```

Zinsen entstehen aus Zeit, Risiko, Knappheit und semantischer Schwierigkeit:

```text
Zins(Qi) =
Basiszins
+ Ausfallrisiko
+ Knappheitszuschlag
+ Komplexitätszuschlag
- Sicherheitenabschlag
```

Hohe Münzen wie Q18 und Q20 tragen oft höhere Zinsen, weil ihr Ausfall ganze Systeme beschädigen kann.

---

## 12. Technische Schuld als echte Schuld

Technische Schuld wird als reale Q-Schuld gebucht.

| Schuld | Bedeutung |
|---|---|
| -Q1 | ungelöste Grundaufgabe |
| -Q2 | unzerlegtes Problem |
| -Q3 | fehlendes Modell |
| -Q4 | fehlende formale Präzision |
| -Q5 | fehlende Implementierung |
| -Q6 | fehlende Spezifikation |
| -Q7 | ungeklärte Verantwortung |
| -Q8 | fehlende Bibliothek oder Wiederverwendung |
| -Q9 | fehlender Rahmen |
| -Q10 | fehlende Constraints |
| -Q11 | kaputte Schnittstelle |
| -Q12 | fehlendes Werkzeug |
| -Q13 | fehlender Dienst |
| -Q14 | Koordinationsschuld |
| -Q15 | nicht gelieferte Anwendung |
| -Q16 | Betriebs- oder Laufzeitschuld |
| -Q17 | unkomprimierte Komplexität |
| -Q18 | Architekturschuld |
| -Q19 | fehlende Generierungsfähigkeit |
| -Q20 | fehlendes Modul oder unfertige Maschine |

Ein Projekt mit viel Q5, aber negativen Q10 und Q18, wirkt produktiv, ist aber strukturell krank.

```text
+20 Q5
-10 Q10
-5 Q18
```

Das heißt: viel Code, schlechte Struktur, schlechte Architektur.

---

## 13. Akteure, Arbeitsteilung und Fähigkeiten

Akteure sind Haushalte, Firmen, Banken, Validatoren, Staat, Gemeingüterfonds und Außenhandelspartner.

Fähigkeiten werden als Q-Profil beschrieben:

```text
Agent A:
Q1: 0.8
Q2: 0.7
Q3: 0.5
Q5: 0.9
Q6: 0.4
Q10: 0.3
Q18: 0.1
```

Das bedeutet: stark im Erkennen und Codieren, schwach in Struktur und Architektur.

Berufe entstehen entlang der Münzarten:

```text
Q1/Q2-Analyst: findet und zerlegt Probleme
Q3/Q4-Theoretiker: modelliert und formalisiert
Q5-Programmierer: implementiert
Q6-Spezifizierer: beschreibt deklarativ
Q7-Koordinator: delegiert und referenziert
Q8-Bibliothekar: baut wiederverwendbare Komponenten
Q9-Frameworkbauer: schafft Rahmen
Q10-Constraint-Ingenieur: setzt Grenzen und Struktur
Q11-Interface-Designer: verbindet Systeme
Q12-Toolsmith: baut Werkzeuge
Q13-Servicebauer: erstellt Dienste
Q14-Orchestrator: komponiert Abläufe
Q15-Anwendungsbauer: macht Gebrauchswerke
Q16-Betriebsingenieur: hält Ausführung stabil
Q17-Kompressor: verdichtet Komplexität
Q18-Architekt: konstruiert tragende Formen
Q19-Generatorbauer: baut Erzeugungssysteme
Q20-Modulbauer: liefert fertige Maschinen
```

---

## 14. Staat, Steuern und Gemeingüter

Der Staat schützt die Währung, stabilisiert Krisen und finanziert Gemeingüter. Steuern können in ZW erhoben werden:

```text
Einkommensteuer: Prozentsatz des Nominalwerts
Transaktionssteuer: kleine Abgabe auf Marktgeschäfte
Schuldenabgabe: Zuschlag auf riskante Q18/Q20-Hebelung
```

Öffentliche Ausgaben fördern besonders:

```text
Q8 Bibliotheken
Q9 Frameworks
Q12 Werkzeuge
Q16 Infrastruktur
Bildung
Validierung
öffentliche Sicherheit
```

Antimonopol-Regeln sind wichtig, weil Q8, Q9, Q16, Q18 und Q20 Produktionsbedingungen kontrollieren können. Mittel sind offene Schnittstellen, Interoperabilitätspflicht, Zwangslizenzen, Gemeingüterabgaben und notfalls Aufspaltung.

---

## 15. Inflation, Deflation und Krisen

Inflation bedeutet hier nicht nur steigende Preise. Sie bedeutet, dass eine Münzart ohne ausreichende semantische Deckung vermehrt wird.

```text
Q5-Inflation  = viel Code ohne Spezifikation, Constraints und Architektur
Q13-Inflation = viele Services ohne Zuverlässigkeit
Q18-Inflation = behauptete Architektur ohne tragende Konstruktion
Q20-Inflation = unfertige Module werden als Maschinen verkauft
```

Deflation bedeutet: Es gibt zu wenige gültige Münzen für vorhandene Aufgaben. Beispiel: viele Q1-Aufgaben, aber zu wenig Q5, Q10 und Q18.

Typische Krise:

```text
Q5:  sehr hoch
Q13: hoch
Q15: hoch
Q10: niedrig
Q16: niedrig
Q18: niedrig
```

Das heißt: viel Code und viele Anwendungen, aber zu wenig Struktur, Betrieb und Architektur. Die Krise zeigt sich als Ausfälle, Integrationsprobleme, Sicherheitslücken und Wartungsstau.

Krisenpolitik darf nicht blind Geld drucken. Sie muss die fehlenden Münzarten stärken.

---

## 16. Qualität, Reputation und Eigentum

Nicht jede Münze gleicher Art hat dieselbe Qualität. Qualitätsklassen:

```text
A = geprüft, stabil, wiederverwendbar
B = brauchbar, aber begrenzt
C = experimentell
D = problematisch
F = ungültig oder gescheitert
```

Q18-A ist wertvoller als Q18-C, obwohl beide nominal 4 ZW haben.

Reputation wird je Münzart geführt:

```text
Agent A:
Q5-Reputation: 90
Q6-Reputation: 60
Q10-Reputation: 45
Q18-Reputation: 20
```

Eigentum besteht an Münzen, Artefakten und Nutzungsrechten:

```text
Münzeigentum: 5 × Q10
Artefakteigentum: Programm, Bibliothek, Maschine
Nutzungsrecht: Lizenz auf Q8, Q9 oder Q20
```

---

## 17. Lizenzökonomie und Handel mit Aufgaben

Q8-Bibliotheken, Q9-Frameworks, Q13-Services, Q15-Anwendungen und Q20-Module können lizenziert werden.

Beispiel:

```text
Q8-Bibliothek:
Einmalige Nutzung: 1 ZW
Kommerzielle Nutzung: 2 Q5 pro Monat
Open-Commons-Lizenz: öffentlich finanziert
```

Auch Aufgaben können gehandelt werden. Q1 ist Rohstoff: Eine gute Aufgabe, Forschungsfrage oder Kundenanforderung kann gekauft und verkauft werden. Eine gute Aufgabe ist wertvoll, weil sie Grundlage einer Q1→Q20-Kette werden kann.

---

## 18. Wertkette Q1 → Q20 und Intelligenz

Die zentrale Wirtschaftsbewegung:

```text
Q1 → Q20
Aufgabe → Maschine
```

Vollständige Kette:

```text
Q1  Aufgabe erkennen
Q2  Aufgabe zerlegen
Q3  Modell bilden
Q4  formalisieren
Q5  implementieren
Q6  deklarieren
Q7  delegieren
Q8  Bibliothek bauen
Q9  Framework schaffen
Q10 Constraints setzen
Q11 Schnittstellen bauen
Q12 Werkzeuge bereitstellen
Q13 Service erstellen
Q14 Dienste orchestrieren
Q15 Anwendung bauen
Q16 Betrieb sichern
Q17 Komplexität komprimieren
Q18 Architektur konstruieren
Q19 Generierung ermöglichen
Q20 Modul/Maschine liefern
```

Intelligenz ist Transformationsfähigkeit:

```text
Intelligenz = Fähigkeit, Q1 in höhere Q-Formen zu verwandeln
```

Niedrige Transformation:

```text
Q1 → Q5 = Aufgabe wird Code
```

Hohe Transformation:

```text
Q1 → Q18 → Q19 → Q20 = Aufgabe wird architektonisch gefasst, generativ gemacht und als Maschine geliefert
```

---

## 19. Börse, Preisindex, Geldmenge und Insolvenz

An der Q-Börse haben Münzen Marktpreise. Beispiel:

| Münze | Nominal | Marktpreis |
|---:|---:|---:|
| Q1 | 1 | 0,8 |
| Q5 | 2 | 2,4 |
| Q8 | 2 | 3,1 |
| Q10 | 3 | 5,0 |
| Q13 | 3 | 3,6 |
| Q18 | 4 | 9,5 |
| Q20 | 4 | 7,8 |

Der Q-Preisindex misst einen typischen Entwicklungszyklus:

```text
4 × Q1
2 × Q5
2 × Q8
2 × Q10
1 × Q13
1 × Q16
1 × Q18
1 × Q20
```

Geldmenge wird je Münzart gemessen:

```text
M(Q18) = Menge gültiger Q18-Münzen
L(Q18) = offene Schulden in Q18
```

Gefährlich:

```text
L(Q18) sehr hoch
M(Q18) niedrig
```

Das ist eine Architekturschuldenkrise.

Insolvenz kann nominal oder semantisch sein. Nominale Insolvenz heißt: Gesamtschulden übersteigen Gesamtvermögen. Semantische Insolvenz heißt: Gesamtwert reicht, aber die richtigen Münzarten fehlen.

---

## 20. Forschung, Außenhandel und R-Kontinuum

Forschung erzeugt vor allem:

```text
Q1 neue Aufgaben
Q3 neue Abstraktionen
Q4 neue formale Objekte
Q12 neue Werkzeuge
Q17 Kompressionen
Q19 Generierungsprinzipien
```

Außenhandel verbindet die Q-Ökonomie mit anderen Wirtschaften. Exportiert werden besonders Q8, Q9, Q13, Q15, Q18 und Q20. Importiert werden Rohstoffe, Hardware, Energie, Daten, Arbeit und Kapital.

Das R-Kontinuum ist reale Ausführung oder praktische Wirklichkeit. Q-Wert wird besonders stark, wenn er in R-Wirkung übergeht:

```text
Q18 Architektur + Q20 Modul → reale Maschine → R-Wert
Q13 Service + Q16 Betrieb → laufender Dienst → R-Nutzen
```

---

## 21. Triple-Store-Ledger, Verträge und Simulation

Die Buchhaltung erfolgt als semantisches Triple-Store-Ledger:

```text
(Subjekt, Prädikat, Objekt)
```

Beispiele:

```text
(Agent A, besitzt, 3 × Q10)
(Agent A, schuldet, 1 × Q18 an Agent B)
(Projekt P, benötigt, 2 × Q5)
(Projekt P, erzeugt, 1 × Q13)
(Q17, inverse Operation, Dekompression)
```

Ein Vertrag enthält:

```text
Parteien
Lieferobjekt
Q-Signatur
Preis
Fälligkeit
Qualitätsgrad
Sanktion
Validierung
```

Simulation läuft in Perioden:

```text
1. Aufgaben entstehen.
2. Akteure wählen Handlungen.
3. Märkte öffnen.
4. Produktion findet statt.
5. Ergebnisse werden validiert.
6. Münzen werden geprägt oder abgelehnt.
7. Zahlungen werden gebucht.
8. Schulden werden aktualisiert.
9. Preise werden angepasst.
10. Reputation wird aktualisiert.
11. Staat und Münzamt reagieren.
```

---

## 22. Gesetze der Q-Ökonomie

```text
1. Münzgesetz: Jede Q-Münze hat Nummer, Zeilenwert und Bedeutung.
2. Additionsgesetz: Münzenwerte addieren sich nach Zeilenhöhe.
3. Semantikgesetz: Gleicher Nominalwert bedeutet nicht gleiche Funktion.
4. Schuldgesetz: Negative Münzbestände sind Schulden.
5. Inversionsgesetz: 1/Qi ist inverse Operation, -Qi ist Schuld.
6. Produktionsgesetz: Produktion verwandelt Q1-Schwierigkeit in höhere Q-Formen.
7. Validierungsgesetz: Neue Münzen entstehen nur durch geprüfte Leistung.
8. Preisgesetz: Marktpreise entstehen aus Nominalwert, Knappheit, Qualität, Risiko und Vertrauen.
9. Solvenzgesetz: Gesundheit braucht nominale und semantische Zahlungsfähigkeit.
10. Stabilitätsgesetz: Hohe Münzen müssen durch Struktur, Betrieb und Architektur gedeckt sein.
```

---

## 23. Schlussdefinition

Die Q-Ökonomie ist eine semantische Geld-, Kredit- und Produktionsordnung.

Ihre Währung besteht aus Q1 bis Q20. Der Wert jeder Münze ist ihre Zeilenhöhe. Münzen können addiert, getauscht, verliehen und geschuldet werden. Schulden sind negative Q-Bestände. Inverse Operationen werden als 1/Qi geschrieben und sind keine Schulden.

Produktion ist die Transformation von Schwierigkeit in strukturierte, ausführbare und wiederverwendbare Formen. Wohlstand entsteht, wenn Q1-Aufgaben über Q5-Code, Q10-Struktur, Q13-Dienste, Q18-Architektur und Q20-Module in reale Wirkung überführt werden.

Krisen entstehen, wenn nominaler Reichtum und semantische Zahlungsfähigkeit auseinanderfallen. Stabilität entsteht durch Validierung, offene Schnittstellen, gute Architektur, sichtbare Schulden und öffentliche Gemeingüter.

**Kernsatz:** Diese Wirtschaft bezahlt nicht bloß Arbeit. Sie bezahlt die gelungene Verwandlung von Schwierigkeit in funktionsfähige Intelligenz.
