# Design der Q-Wirtschaftssimulation

## 1. Grundidee

Die Simulation setzt die Q-Währung als Vektorwährung um. Jeder Akteur besitzt ein Wallet mit 20 Münzpositionen:

```text
Wallet = (Q1, Q2, ..., Q20)
```

Positive Werte sind Vermögen. Negative Werte sind Schulden. Der Nominalwert einer Position ist:

```text
Wert(Qi) = Menge(Qi) × Zeilenwert(Qi)
```

Die Zeilenwerte sind:

```text
Q1–Q4   = 1 ZW
Q5–Q9   = 2 ZW
Q10–Q16 = 3 ZW
Q17–Q20 = 4 ZW
```

## 2. Semantik statt bloßem Skalar

Ein normaler Geldbetrag ist eine Zahl. Die Q-Währung ist ein semantischer Vektor.

Beispiel:

```text
4 × Q1  = 4 ZW
1 × Q20 = 4 ZW
```

Nominal sind beide gleich. Semantisch nicht:

- `Q1` ist Aufgabe/Schwierigkeit.
- `Q20` ist Modul/Maschine/fertige Entwicklung.

Darum kennt das Modell neben nominaler Solvenz auch semantische Solvenz.

## 3. Produktion

Eine Firma besitzt ein Produktionsrezept:

```text
Arbeitsmix + Inputs + Kapital + Q-Struktur → Outputgut + Q-Münzprägung
```

Beispiel Software/KI:

```text
Softwarearbeit + Forschung + Engineering + Energie + Wissen
→ Automatisierungsdienst
→ Q5/Q6/Q8/Q9/Q10/Q13/Q17/Q19
```

Beispiel Bau:

```text
Bauarbeit + Handwerk + Engineering + Rohstoffe + Energie
→ Wohnraum/Bauleistung
→ Q4/Q10/Q11/Q18/Q20
```

Die Q-Münzen werden nicht frei gedruckt. Das Münzamt prägt sie proportional zu Outputwert, Sektor-Q-Signatur und Qualität.

## 4. Qualität und technische Schuld

Produktion hat eine Qualität. Qualität hängt ab von:

- passendem Arbeitsmix,
- Fähigkeit der Beschäftigten,
- Kapitalstock,
- Automatisierung,
- Inputversorgung,
- Q-Struktur,
- bestehender Schuld.

Niedrige Qualität erzeugt negative Q-Positionen in kritischen Münzen des Sektors.

Beispiele:

- Energie mit schwacher Betriebsstruktur erzeugt `-Q16`.
- Bau mit schlechter Konstruktion erzeugt `-Q18`.
- Software ohne Constraints erzeugt `-Q10` und `-Q18`.

## 5. Arbeit

Arbeit ist nicht nur Intelligenzarbeit. Jeder Arbeitstyp hat:

- Basislohn,
- Fähigkeitsprofil,
- Q-Lohnsemantik,
- sektorale Verwendung.

Beispiel:

```text
Bauarbeit → Q4/Q10/Q18/Q20
Pflege → Q11/Q13/Q14/Q16
Forschung → Q1/Q3/Q12/Q17/Q19
Landwirtschaft → Q1/Q2/Q10/Q16
```

Haushalte haben Fähigkeiten in allen Arbeitstypen. Der Arbeitsmarkt matcht Stellen und Haushalte über Lohn, Fähigkeit und Präferenz.

## 6. Gütermarkt

Haushalte konsumieren essentielle und diskretionäre Güter. Firmen kaufen Inputs. Der Staat kauft öffentliche Güter. Die Außenwelt kauft Exportgüter.

Güterpreise passen sich an:

- Lagerbestand,
- Verkäufe,
- Engpässe,
- Qualität,
- sektorale Lage.

## 7. Kreditmarkt

Banken vergeben Kredite an Firmen, Haushalte oder Staat. Kredite haben:

- Zweck,
- Q-Münztyp,
- Zinssatz,
- Laufzeit,
- Ausfallrisiko,
- Restrukturierung.

Der Kredittyp richtet sich nach Zweck:

```text
working_capital    → Q5
input_purchase     → Q10
wage_bridge        → Q11
capital_investment → Q18
automation         → Q19
public_deficit     → Q16
```

## 8. Staat

Der Staat hat mehrere Rollen:

- Steuern erheben,
- Transfers zahlen,
- öffentliche Güter kaufen,
- Bildung/Gesundheit/Infrastruktur stabilisieren,
- Arbeitslosigkeit über ein öffentliches Jobprogramm abfedern,
- Gemeingüter wie Q8/Q9/Q12/Q16 fördern.

Das Jobprogramm ist absichtlich produktiv modelliert. Es erzeugt öffentliche Güter und eine moderate Q-Deckung, statt nur Geld zu verteilen.

## 9. Außenhandel

Der Rest der Welt kauft exportfähige Güter. Importe wirken als begrenzter Puffer bei starken Engpässen. Sie sind aber nicht unbegrenzt: der Staat kann nicht beliebig importieren, ohne Liquidität zu verlieren.

## 10. Krisenlogik

Krisen entstehen, wenn nominale Werte und semantische Struktur auseinanderfallen.

Typische Krisen:

```text
+Q5, -Q10, -Q18
```

Bedeutung: viel Code, aber zu wenig Constraints und Architektur.

```text
+Q13, -Q16
```

Bedeutung: viele Dienste, aber zu wenig Betrieb.

```text
+Q19, -Q10, -Q16, -Q18
```

Bedeutung: viel Generierung, aber schlechte Begrenzung, Ausführung und Architektur.

## 11. Simulationsablauf pro Periode

1. Politik und Q-Knappheiten aus Vorperiode auswerten.
2. Arbeitsmarkt matcht Haushalte und Firmen.
3. Öffentliches Jobprogramm stabilisiert extreme Arbeitslosigkeit.
4. Banken vergeben Brückenkredite.
5. Firmen zahlen Löhne.
6. Staat zahlt Transfers und erhebt Einkommensteuer.
7. Firmen kaufen Inputs.
8. Firmen produzieren und Münzamt prägt Q-Münzen.
9. Haushalte konsumieren.
10. Staat kauft öffentliche Güter.
11. Rest der Welt kauft Exporte und begrenzt Importe.
12. Preise und Firmengewinne werden aktualisiert.
13. Gewinnsteuern werden erhoben.
14. Kredite werden bedient oder restrukturiert.
15. Q-Schulden werden semantisch repariert.
16. Insolvenzen und Gründungen werden verarbeitet.
17. Berichtskennzahlen werden gespeichert.

## 12. Erweiterungsideen

Das Projekt ist so angelegt, dass man es ausbauen kann:

- echte Input-Output-Matrix,
- Regionen/Städte,
- politische Parteien,
- Unternehmensgründungen durch Haushalte,
- Demografie und Familien,
- Technologiebaum,
- Zentralbankregeln,
- unterschiedliche Rechtssysteme,
- Handel zwischen mehreren Q-Ökonomien,
- Visualisierung,
- Kalibrierung auf echte Daten.
