# Delta-Norm-Wirtschaftssystem / Delta-Norm Economy

**Sprache / Language:** Deutsch und Englisch / German and English  
**Thema / Topic:** Ein Wirtschaftssystem, in dem Geld aus der Abweichung zwischen zwei mathematischen Normen entsteht und Verhalten bezahlt, gekauft und koordiniert wird.  
**Datum / Date:** 30. April 2026  
**Status:** Konzeptmodell, kein politischer Implementierungsaufruf.  

---

## Kurzfassung auf Deutsch

Dieses Modell konstruiert eine Wirtschaft, in der Geld nicht primär als Metall, Banknote, Fiat-Zahl oder Kryptowert verstanden wird, sondern als **Delta zwischen zwei mathematischen Normwerten**. Jede wirtschaftlich relevante Handlung wird als Verhaltensereignis in einem Vektorraum beschrieben. Zwei Normen bewerten dieses Ereignis aus zwei Richtungen:

1. **Beitragsnorm** \(\|\cdot\|_+\): Wie stark erhöht das Verhalten Systemfähigkeit, Nutzen, Wahrheit, Sicherheit, Versorgung, Kooperation oder Zukunftsfähigkeit?
2. **Belastungsnorm** \(\|\cdot\|_-\): Wie stark verbraucht, gefährdet, verzerrt oder belastet das Verhalten Ressourcen, Vertrauen, Aufmerksamkeit, Gesundheit, Umwelt, Infrastruktur oder soziale Ordnung?

Die Währungseinheit heißt **Delta** oder **Δ**. Für ein Verhaltensereignis \(e\) gilt vereinfacht:

\[
\mu(e)=\lambda_d\bigl(\|\Phi_d(e)\|_{+,d}-\|\Phi_d(e)\|_{-,d}\bigr)
\]

Dabei ist \(\Phi_d(e)\) die Vektorisierung des Ereignisses im Bereich \(d\), etwa Nahrung, Arbeit, Medien, Energie, Mobilität, Raumstation oder Mondlogistik. \(\lambda_d\) ist der geldpolitische Umrechnungsfaktor. Ist \(\mu(e)>0\), erzeugt oder verdient das Verhalten Delta. Ist \(\mu(e)<0\), kostet es Delta oder erzeugt eine Rückzahlungs-/Wiedergutmachungspflicht.

Wichtig: Die Differenz zweier Normwerte ist selbst **keine mathematische Norm** mehr. Sie ist ein **monetärer Spread** aus zwei Normen. Genau dieser Spread wird als Geld verwendet.

Das System besitzt eine Zentralbank für Erde, Mond, Satelliten und Raumstationen im Erdorbit: die **Zentralbank des Erde-Mond-Orbit-Systems**, kurz **ZEMO**. Sie verwaltet nicht alle menschlichen Werte, sondern die Stabilität der Delta-Währung, die technische Abrechnung, die Verhaltensmärkte, die Geldmenge, die Normtransparenz und die Rechte der Teilnehmer. Damit das System nicht zu einem totalitären Sozialkreditsystem wird, sind Privatsphäre, Einspruchsrechte, demokratische Normsetzung, minimale Grundversorgung, pluralistische Medienregeln und harte Grenzen gegen politische Gesinnungsbewertung eingebaut.

---

## Executive Summary in English

This model designs an economy in which money is not primarily metal, paper, fiat balance, or crypto scarcity. Money is a **delta between two mathematical norm values**. Every economically relevant action is represented as a behavioral event in a vector space. Two norms evaluate the event from two directions:

1. **Contribution norm** \(\|\cdot\|_+\): How much does the behavior increase system capacity, utility, truth, safety, supply, cooperation, or future viability?
2. **Burden norm** \(\|\cdot\|_-\): How much does the behavior consume, endanger, distort, or burden resources, trust, attention, health, the environment, infrastructure, or social order?

The currency unit is called **Delta** or **Δ**. For a behavioral event \(e\):

\[
\mu(e)=\lambda_d\bigl(\|\Phi_d(e)\|_{+,d}-\|\Phi_d(e)\|_{-,d}\bigr)
\]

Here \(\Phi_d(e)\) is the vectorization of the event in domain \(d\), such as food, labor, media, energy, mobility, orbital stations, or lunar logistics. \(\lambda_d\) is the monetary conversion factor. If \(\mu(e)>0\), the behavior earns or creates Delta. If \(\mu(e)<0\), it costs Delta or creates a restorative liability.

Technically, the difference between two norm values is not itself a mathematical norm. It is a **monetary spread** produced by two norms. That spread is used as money.

The system has a central bank for Earth, Moon, satellites, and stations in Earth orbit: the **Central Bank of the Earth-Moon-Orbit System**, abbreviated **ZEMO**. It does not own all human values. It manages currency stability, settlement, behavioral markets, money supply, norm transparency, and participant rights. To avoid becoming a coercive social-credit regime, the design includes privacy, appeals, democratic norm-setting, universal basic access, pluralistic media rules, and hard barriers against political belief scoring.

---

# Teil I – Deutsch

## 1. Grundidee

In einer gewöhnlichen Wirtschaft bezahlt man mit Geld für Dinge: Brot, Strom, Arbeitszeit, Transport, Nachrichten, Unterhaltung, Wohnung, Maschinen, Kredite. In diesem Modell wird alles als **Verhalten** interpretiert.

Ein Brot ist nicht nur ein Objekt. Es ist die Summe vieler Verhaltensketten: säen, bewässern, düngen, ernten, mahlen, backen, transportieren, verkaufen, essen, entsorgen. Eine Nachricht ist nicht nur Text. Sie ist Verhalten: recherchieren, prüfen, formulieren, gewichten, veröffentlichen, korrigieren, verbreiten. Arbeit ist offensichtlich Verhalten. Konsum ist Verhalten. Auch Nicht-Handeln kann Verhalten sein, etwa das Unterlassen einer Reparatur an einer Raumstation.

Die zentrale These lautet:

> Wirtschaft ist ein System zur Koordination von Verhalten. Geld ist die Zahl, mit der Verhaltensabweichungen messbar, handelbar und verrechenbar werden.

Dieses System macht diese These radikal explizit. Es sagt nicht: „Geld kauft Sachen.“ Es sagt:

> Geld kauft, belohnt, belastet oder überträgt Verhalten.

Das Verhalten wird nicht beliebig bewertet, sondern über zwei mathematische Normen. Der Geldbetrag ist der Unterschied zwischen dem normierten Beitrag und der normierten Belastung.

---

## 2. Mathematischer Kern

### 2.1 Verhaltensraum

Sei \(A\) die Menge aller Akteure: Personen, Unternehmen, Medienhäuser, KI-Agenten, Forschungseinrichtungen, Satellitenbetreiber, Raumstationen, Mondhabitate, Gemeinden, Staaten oder Kooperativen.

Ein wirtschaftlich relevantes Ereignis ist:

\[
e=(a,t,l,d,z)
\]

mit:

- \(a\): Akteur,
- \(t\): Zeitpunkt oder Zeitraum,
- \(l\): Ort oder Infrastrukturkontext, etwa Erde, Mond, Satellit, Station,
- \(d\): Verhaltensdomäne, etwa Nahrung, Arbeit, Medien, Energie,
- \(z\): beobachtbare oder beweisbare Ereignisdaten.

Für jede Domäne \(d\) gibt es eine Abbildung:

\[
\Phi_d:E_d\to\mathbb{R}^{n_d}
\]

Diese Abbildung verwandelt ein Ereignis in einen Vektor. Beispiele:

- Ein Arbeitsereignis wird zu einem Vektor aus Zeit, Qualität, Sicherheit, Kooperationsgrad, Zuverlässigkeit, Lernbeitrag und Ressourcenverbrauch.
- Ein Nachrichtenereignis wird zu einem Vektor aus Faktentreue, Quellenlage, öffentlicher Relevanz, Aktualität, Korrekturverhalten, Manipulationsrisiko und Aufmerksamkeitsverbrauch.
- Ein Essensereignis wird zu einem Vektor aus Nährwert, Energieaufwand, Materialfluss, Gesundheitswirkung, Abfall, Knappheit und kulturellem Nutzen.

### 2.2 Zwei Normen

Für jede Domäne gibt es zwei mathematische Normen auf demselben oder einem transformierten Vektorraum:

\[
\|x\|_{+,d}
\]

und

\[
\|x\|_{-,d}
\]

Die **Plusnorm** misst den Beitrag. Die **Minusnorm** misst die Belastung.

Eine typische Form ist eine gewichtete \(p\)-Norm:

\[
\|x\|_{+,d}=\left(\sum_{j=1}^{n_d}w^+_{d,j}|x_j|^{p_d}\right)^{1/p_d}
\]

\[
\|x\|_{-,d}=\left(\sum_{j=1}^{n_d}w^-_{d,j}|x_j|^{q_d}\right)^{1/q_d}
\]

mit positiven Gewichten \(w^+_{d,j}\) und \(w^-_{d,j}\). Die Gewichte legen fest, was in einer Domäne wichtig ist. In einer Raumstation ist Sauerstoffsicherheit viel höher gewichtet als Bequemlichkeit. Im Journalismus ist Quellenqualität höher gewichtet als Klickzahl. In der Landwirtschaft sind Ernährung, Boden, Wasser, Energie, Arbeitsbedingungen und Abfall relevant.

### 2.3 Geld als Norm-Spread

Der monetäre Wert eines Ereignisses ist:

\[
\mu(e)=\lambda_d\left(\|P^+_d\Phi_d(e)\|_{+,d}-\|P^-_d\Phi_d(e)\|_{-,d}\right)
\]

Dabei sind \(P^+_d\) und \(P^-_d\) Projektionen oder Filter. Sie trennen jene Koordinaten, die als Beitrag bewertet werden, von jenen, die als Belastung zählen. \(\lambda_d\) ist ein Umrechnungsfaktor der Zentralbank.

- \(\mu(e)>0\): Verhalten erzeugt Netto-Beitrag. Der Akteur erhält Delta.
- \(\mu(e)=0\): Beitrag und Belastung gleichen sich aus.
- \(\mu(e)<0\): Verhalten erzeugt Netto-Belastung. Der Akteur bezahlt Delta oder erhält eine Verpflichtung zur Kompensation.

Die Währungseinheit ist:

\[
1\;\Delta
\]

oder kurz:

\[
1\;D
\]

Ein Kontostand eines Akteurs \(a\) entwickelt sich als:

\[
B_a(t+1)=B_a(t)+\sum_{e\in E_a(t)}\mu(e)+T_a(t)-F_a(t)
\]

mit:

- \(B_a(t)\): Delta-Kontostand,
- \(E_a(t)\): Ereignisse des Akteurs im Zeitraum,
- \(T_a(t)\): Transfers, Löhne, Käufe, Vertragszahlungen,
- \(F_a(t)\): Gebühren, Steuern, Rückzahlungen, Sanktionen, Ausgleichspflichten.

---

## 3. Warum das Geld ist

Damit etwas Geld ist, muss es mindestens vier Funktionen erfüllen.

### 3.1 Recheneinheit

Delta ist die gemeinsame Zahl, in der Preise angegeben werden. Ein Medienartikel, ein Kilogramm Nahrung, eine Stunde Wartungsarbeit, eine Orbitkorrektur, ein medizinischer Dienst, eine Forschungsleistung und eine Werbekampagne können alle in Delta bewertet werden.

### 3.2 Tauschmittel

Akteure übertragen Delta, wenn sie Verhalten kaufen. Ein Habitat kann Wartungsverhalten kaufen. Eine Gemeinde kann Nachrichtenrecherche kaufen. Eine Person kann Nahrung kaufen, also die Verhaltenskette hinter der Nahrung bezahlen. Ein Unternehmen kann Arbeitsverhalten kaufen.

### 3.3 Wertaufbewahrung

Delta ist ein Anspruch auf künftig anerkanntes positives Verhalten anderer Akteure. Wer Delta hält, hält keinen moralischen Rang, sondern Kaufkraft über Verhaltensleistungen.

### 3.4 Maß für spätere Zahlungen

Kredite, Versicherungen, Anleihen, Löhne und Leasingverträge werden als Ansprüche auf zukünftige Delta-Flüsse geschrieben. Ein Kredit ist die Erwartung, dass der Schuldner künftig genügend positive Verhaltensdeltas erzeugt oder Delta-Transfers erhält.

---

## 4. Die Zentralbank des Erde-Mond-Orbit-Systems: ZEMO

### 4.1 Name und Zuständigkeit

Die Zentralbank heißt:

**Zentralbank des Erde-Mond-Orbit-Systems**, kurz **ZEMO**.

Ihr Währungsraum umfasst:

- Erde,
- Mond,
- Satelliten im Erdorbit,
- Raumstationen im Erdorbit,
- Kommunikations-, Navigations-, Energie- und Forschungsinfrastruktur zwischen Erde und Mond.

Später kann das System auf Mars, Asteroiden oder andere Habitate erweitert werden. Der Grundraum bleibt zunächst Erde-Mond-Orbit, weil dort Ressourcen, Kommunikation, Abhängigkeiten und Sicherheitsfragen eng zusammenhängen.

### 4.2 Mandat

Die ZEMO hat sechs Hauptaufgaben:

1. **Stabilität der Delta-Währung**: Die Kaufkraft von Delta soll über Grundgüter und Grundverhalten hinweg stabil bleiben.
2. **Norm-Transparenz**: Die verwendeten Normen, Gewichte, Datenquellen und Berechnungen müssen öffentlich prüfbar sein.
3. **Geldschöpfung und Geldvernichtung**: Delta wird geschaffen, wenn verifizierbares Verhalten die Systemfähigkeit erhöht. Delta wird vernichtet oder gebunden, wenn Verhalten knappe Ressourcen verbraucht oder Risiken erzeugt.
4. **Abrechnung und Finalität**: Transaktionen zwischen Erde, Mond, Satelliten und Stationen müssen sicher abgeschlossen werden können, auch bei Kommunikationsverzögerungen oder Ausfällen.
5. **Schutz vor Manipulation**: Norm-Gaming, gefälschte Daten, Medienmanipulation, Scheinverhalten und Scheinknappheit werden erkannt und sanktioniert.
6. **Rechte und Grenzen**: Die ZEMO darf nicht zur totalen Verhaltenspolizei werden. Sie sichert Einspruch, Privatsphäre, Grundversorgung und pluralistische Lebensformen.

### 4.3 Gewaltenteilung innerhalb der ZEMO

Damit die Zentralbank nicht alle Werte der Gesellschaft bestimmt, besteht sie aus getrennten Kammern:

#### A. Monetäre Kammer

Sie setzt Umrechnungsfaktoren \(\lambda_d\), Liquiditätsquoten, Reserveanforderungen und Stabilitätsziele.

#### B. Normenkammer

Sie verwaltet die mathematischen Normfamilien, darf Gewichte aber nur nach transparenten Verfahren ändern. Sie ist nicht identisch mit der Regierung.

#### C. Daten- und Orakelkammer

Sie zertifiziert Messsysteme, Sensoren, Medienbelege, Arbeitsnachweise, Lieferkettennachweise und Audits.

#### D. Rechtekammer

Sie prüft Beschwerden, schützt Privatsphäre, stoppt missbräuchliche Normen und kann Abrechnungen aussetzen.

#### E. Erde-Mond-Orbit-Rat

Er sorgt dafür, dass Erde, Mond, Satellitenbetreiber und Raumstationen nicht gegenseitig dominiert werden. Eine Mondkolonie darf nicht allein nach irdischen Komfortnormen bewertet werden. Eine Erdregion darf nicht nach Stationsnotfallnormen leben müssen.

---

## 5. Geldschöpfung

Delta entsteht nicht einfach durch Drucken. Delta entsteht aus verifiziertem Netto-Beitrag.

### 5.1 Primäre Geldschöpfung

Die ZEMO schreibt neues Delta gut, wenn Verhalten nachweislich Systemkapazität erhöht. Beispiele:

- Reparatur kritischer Infrastruktur,
- Produktion von Nahrung mit niedriger Belastung und hoher Versorgungssicherheit,
- Verbesserung von Sauerstoff-, Wasser- oder Energie-Recycling in Habitaten,
- zuverlässige Nachrichtenrecherche von öffentlichem Interesse,
- medizinische Versorgung,
- Bildung und Ausbildung,
- Forschung mit reproduzierbaren Ergebnissen,
- Risikoreduktion im Orbit, etwa Vermeidung oder Beseitigung von Trümmern,
- Pflegearbeit und soziale Stabilisierung,
- Software- und Sicherheitswartung wichtiger Systeme.

Mathematisch:

\[
\Delta M^+_t=\sum_{e\in E_t^{valid}}\max(0,\mu(e))\cdot \rho_e
\]

\(\rho_e\) ist ein Verifikationsfaktor zwischen 0 und 1. Unklare oder schwach bewiesene Ereignisse erzeugen weniger oder vorläufiges Delta.

### 5.2 Geldvernichtung

Delta wird vernichtet, gesperrt oder als Rückstellung gebunden, wenn Verhalten knappe Systemkapazität verbraucht oder Risiken erzeugt:

- hoher Ressourcenverbrauch,
- vermeidbarer Abfall,
- gefährliches Verhalten im Orbit,
- Falschinformation mit messbarem Schaden,
- Vertragsbruch,
- Infrastrukturverschleiß,
- Produktion mit versteckten Folgekosten,
- Aufmerksamkeitsausbeutung durch Täuschung.

Mathematisch:

\[
\Delta M^-_t=\sum_{e\in E_t^{valid}}\max(0,-\mu(e))\cdot \sigma_e
\]

\(\sigma_e\) ist ein Belastungs- oder Haftungsfaktor.

### 5.3 Sekundäre Geldübertragung

Die meisten Alltagszahlungen schaffen kein neues Geld. Sie übertragen vorhandenes Delta:

- Lohnzahlung,
- Kauf von Nahrung,
- Bezahlung eines Medienabos,
- Miete,
- Reparaturauftrag,
- Transportticket,
- Softwarelizenz,
- Stationswartung.

Der Unterschied ist wichtig: Nicht jede gute Tat druckt Geld. Sonst entstünde Inflation. Geldschöpfung erfordert verifizierbaren Netto-Zuwachs an Systemfähigkeit oder einen von der ZEMO genehmigten öffentlichen Auftrag.

---

## 6. Märkte für Verhalten

### 6.1 Verhaltensvertrag

Ein Marktvertrag lautet nicht mehr nur „Ware gegen Geld“, sondern:

\[
C=(a,b,d,T,g,\Pi,E,p)
\]

mit:

- \(a\): Käufer,
- \(b\): Anbieter,
- \(d\): Domäne,
- \(T\): Zeitraum,
- \(g\): Zielvektor oder Verhaltensziel,
- \(\Pi\): Preisformel in Delta,
- \(E\): Beweisstandard,
- \(p\): Datenschutzstufe.

Beispiel: Eine Raumstation kauft von einem Techniker nicht „eine Stunde Zeit“, sondern „sicheres Wartungsverhalten am CO₂-Filter mit dokumentierter Prüfung und Fehlerreduktion“. Der Techniker wird nicht für Anwesenheit bezahlt, sondern für verifiziertes Verhalten.

### 6.2 Verhaltensbörse

Es gibt Börsen für standardisierte Verhaltenstypen:

- Arbeitsdeltas,
- Pflegedeltas,
- Forschungsdeltas,
- Nachrichten- und Wahrheitsdeltas,
- Energiedeltas,
- Recyclingdeltas,
- Orbit-Sicherheitsdeltas,
- Nahrungsdeltas,
- Transportdeltas,
- Bildungsdeltas.

Ein Anbieter verkauft die Bereitschaft oder Fähigkeit, ein Verhalten zu erzeugen. Ein Käufer erwirbt das Verhalten oder dessen Ergebnis.

### 6.3 Preise

Der Preis eines Verhaltensbündels ist:

\[
P(C)=\mathbb{E}\left[\sum_{e\in C}\mu(e)\right]+R(C)+L(C)+K(C)
\]

mit:

- erwarteter Norm-Spread,
- Risikoaufschlag \(R(C)\),
- Liquiditätsaufschlag \(L(C)\),
- Koordinationskosten \(K(C)\).

---

## 7. Arbeit und Arbeitnehmersein

In diesem System ist Arbeit ein vertraglich begrenzter Verhaltensraum. Ein Arbeitgeber kauft nicht den Menschen, sondern bestimmte, definierte, zeitlich begrenzte Verhaltensereignisse.

### 7.1 Arbeitsvektor

Ein Arbeitsereignis kann Koordinaten haben wie:

- Zeitaufwand,
- Outputqualität,
- Sicherheitsverhalten,
- Teamkoordination,
- Zuverlässigkeit,
- Lernbeitrag,
- Dokumentationsqualität,
- Ressourcenverbrauch,
- Fehlerquote,
- Erholungs- und Überlastungsrisiko.

Die Plusnorm belohnt Qualität, Sicherheit, Kooperation und Lernbeitrag. Die Minusnorm belastet Fehler, vermeidbare Risiken, Ressourcenverschwendung und Schädigung anderer.

### 7.2 Lohn

Ein Lohn ist ein erwarteter positiver Delta-Flow:

\[
W_a=\sum_{t\in T}\mathbb{E}[\mu(e_{a,t}^{work})]+\text{Knappheitsprämie}+\text{Risikoausgleich}
\]

Das Modell darf aber nicht bedeuten, dass jeder private Moment eines Arbeitnehmers bewertet wird. Nur vertraglich definierte, arbeitsrelevante und rechtlich zulässige Verhaltensdaten dürfen eingehen.

### 7.3 Arbeitnehmerrechte

Es gibt harte Regeln:

- keine Bewertung privater Gedanken,
- keine permanente Überwachung ohne konkreten Zweck,
- keine versteckte biometrische Auswertung,
- Recht auf Erklärung jeder relevanten Delta-Buchung,
- Recht auf Einspruch,
- Recht auf arbeitsfreie Räume,
- Mindestlohn oder Grunddelta für notwendige Arbeit,
- Schutz vor Diskriminierung durch Normgewichte.

---

## 8. Nahrung, Essen und Konsum

### 8.1 Nahrung als Verhalten

Essen ist Verbrauchsverhalten, Gesundheitsverhalten, Kulturverhalten und Lieferkettenverhalten zugleich. Ein Lebensmittelpreis enthält daher nicht nur Angebot und Nachfrage, sondern den Delta-Spread der gesamten Kette.

Ein Nahrungsvektor kann enthalten:

- Kalorien,
- Mikronährstoffe,
- Proteine,
- Wasserverbrauch,
- Energieverbrauch,
- Bodenbelastung,
- Transportdistanz,
- Kühlaufwand,
- Abfall,
- Arbeitsbedingungen,
- Gesundheitswirkung,
- kultureller oder sozialer Wert.

### 8.2 Preisformel

Ein Lebensmittel kostet Delta, wenn seine Belastungsnorm hoch ist. Es kann subventioniert oder sogar positiv bewertet werden, wenn es Versorgung, Gesundheit, Kreislaufwirtschaft und lokale Resilienz stärkt.

Beispiel:

\[
\mu(food)=\lambda_{food}(\|nutrition+resilience+culture\|_+-\|scarcity+waste+harm\|_-)
\]

Normales Essen darf nicht moralisch kriminalisiert werden. Deshalb gibt es ein **Grundversorgungsdelta**. Jeder Mensch erhält Zugang zu notwendiger Nahrung, Wasser, medizinischer Basisversorgung, Wohnen und Kommunikation. Das Delta-System steuert Knappheit und Verhalten, aber es darf Existenz nicht zur Ware machen.

### 8.3 Konsum allgemein

Konsum bedeutet: Man kauft die Verhaltenskette, die ein Produkt erzeugt hat, und übernimmt einen Teil der zukünftigen Verhaltensfolgen. Ein Smartphone ist nicht nur ein Gerät, sondern Bergbau-, Fabrik-, Design-, Software-, Transport-, Nutzungs-, Reparatur- und Entsorgungsverhalten.

Der Preis enthält:

- Produktionsdelta,
- Materialdelta,
- Arbeitsdelta,
- Nutzungsdelta,
- Reparierbarkeitsdelta,
- Recyclingdelta,
- Informationsdelta, etwa Wahrheit der Werbung.

---

## 9. Medien, Massenmedien und Nachrichten

Dieser Bereich ist zentral, weil Nachrichten nicht nur Information sind. Sie formen Verhalten. Wer Nachrichten kontrolliert, beeinflusst Konsum, Arbeit, Wahlen, Sicherheit, Märkte, Angst, Vertrauen und Konflikte. Deshalb braucht das Delta-System besonders strenge Regeln für Medien.

### 9.1 Nachricht als Verhaltensereignis

Ein Nachrichtenereignis \(e_{news}\) kann Koordinaten haben:

- Faktentreue,
- Quellenqualität,
- Quellentransparenz,
- Trennung von Nachricht und Meinung,
- Aktualität,
- öffentliche Relevanz,
- Korrekturgeschwindigkeit,
- Kontexttiefe,
- Unsicherheitskennzeichnung,
- Sensationalismus,
- Manipulationsabsicht,
- Aufmerksamkeitsverbrauch,
- Schaden durch Fehlleitung,
- Schutz gefährdeter Personen,
- Vielfalt der Perspektiven.

### 9.2 Medien-Delta

Die Geldformel lautet:

\[
\mu(news)=\lambda_{news}(\|truth+relevance+correction+context\|_+-\|deception+manipulation+avoidable_harm\|_-)
\]

Ein Medium verdient Delta nicht einfach durch Reichweite. Reichweite ohne Qualität kann sogar negativ sein. Ein kleiner, korrekt recherchierter lokaler Warnhinweis kann mehr Delta verdienen als eine massenhaft verbreitete, aber manipulative Schlagzeile.

### 9.3 Keine Wahrheitsdiktatur

Das System darf nicht entscheiden: „Diese Meinung ist erlaubt, jene Meinung ist verboten.“ Bewertet wird nicht politische Gesinnung, sondern überprüfbares Medienverhalten:

- Wurden Quellen angegeben?
- Wurden Tatsachenbehauptungen geprüft?
- Wurde Unsicherheit markiert?
- Wurde eine falsche Behauptung korrigiert?
- Wurde Meinung als Meinung gekennzeichnet?
- Wurde absichtlich eine falsche Darstellung verbreitet?
- Wurde eine Person oder Gruppe durch nachweislich falsche Information geschädigt?

Unpopuläre, neue oder unbequeme Positionen dürfen nicht negativ bewertet werden, nur weil sie unbequem sind. Neue Hypothesen erhalten einen Unsicherheitsstatus, keinen Strafstatus.

### 9.4 Massenmedien und Aufmerksamkeitsmärkte

Aufmerksamkeit ist selbst ein knapper Verhaltensraum. Massenmedien kaufen Aufmerksamkeit und verkaufen Verhaltenswahrscheinlichkeit an Werbekunden, Parteien, Unternehmen oder Bewegungen. Im Delta-System wird auch dieses Verhalten bilanziert.

Eine Werbekampagne hat positive Delta, wenn sie nützliche, wahrheitsgemäße Information vermittelt. Sie hat negative Delta, wenn sie manipuliert, verschleiert, suchtähnliche Muster ausnutzt oder absichtlich falsche Erwartungen erzeugt.

### 9.5 Nachrichtenfonds

Die ZEMO betreibt keinen Propagandafonds, sondern einen **öffentlichen Nachrichtenfonds**. Dieser kauft bestimmte Verhaltensleistungen:

- Katastrophenwarnungen,
- lokale Recherchen,
- wissenschaftliche Replikation,
- Korruptionsaufdeckung,
- Infrastrukturwarnungen,
- Raumwetter- und Orbitrisikomeldungen,
- Gesundheitsinformationen,
- Faktenarchive.

Finanziert wird der Fonds durch eine kleine Delta-Gebühr auf große Aufmerksamkeitsmärkte und durch direkte ZEMO-Geldschöpfung für verifizierte öffentliche Informationsgüter.

---

## 10. Unternehmen

Ein Unternehmen ist ein Akteur, der Verhaltensketten organisiert. Gewinn ist nicht nur Umsatz minus Kosten, sondern positiver Delta-Flow minus negativer Delta-Flow.

\[
Profit_\Delta=\sum \mu(e_{sales})+\sum \mu(e_{production})-\sum \mu(e_{resource})-\sum \mu(e_{risk})
\]

Ein Unternehmen kann reich werden, wenn es Verhalten koordiniert, das mehr Systemfähigkeit erzeugt als es Belastung verursacht. Es kann nicht dauerhaft reich werden, indem es Kosten versteckt, weil versteckte Kosten später als negative Delta nachgebucht werden.

### 10.1 Bilanz

Eine Delta-Bilanz enthält:

- Finanzkonto,
- Verhaltensaktiva,
- Reputations- und Vertrauensdelta,
- Ressourcenverpflichtungen,
- Rückstellungen für Schäden,
- Medien- und Informationshaftung,
- Arbeitsverhaltensverpflichtungen,
- Kreislauf- und Entsorgungspflichten.

### 10.2 Insolvenz

Insolvenz bedeutet nicht nur Zahlungsunfähigkeit, sondern Unfähigkeit, künftige positive Delta-Flüsse glaubwürdig zu erzeugen. Sanierung bedeutet: Das Unternehmen muss sein Verhalten so ändern, dass die Plusnorm wieder über der Minusnorm liegt.

---

## 11. Kredite, Zinsen und Vermögen

### 11.1 Kredit

Ein Kredit ist ein Vertrag über zukünftige Delta-Flüsse. Die Bank fragt nicht nur: „Hast du Sicherheiten?“, sondern:

> Welche positiven Verhaltensdeltas kannst du in Zukunft plausibel erzeugen?

Der Kreditbetrag ist der Barwert erwarteter Delta-Flüsse:

\[
Loan\leq \sum_{t=1}^{T}\frac{\mathbb{E}[\mu_t]}{(1+r_t)^t}\cdot \theta
\]

\(\theta\) ist ein Sicherheitsfaktor.

### 11.2 Zins

Der Zins besteht aus:

- Zeitpräferenz,
- Ausfallrisiko,
- Normänderungsrisiko,
- Liquiditätsrisiko,
- Verifikationsrisiko,
- Systemrisiko.

### 11.3 Vermögen

Vermögen ist die Fähigkeit, künftige positive Delta-Flüsse zu kontrollieren oder zu empfangen. Land, Maschinen, Medienmarken, Software, Daten, Satelliten, Mondhabitate und Patente sind Vermögen, wenn sie erwartbar positive Norm-Spreads erzeugen.

---

## 12. Erde, Mond, Satelliten und Raumstationen

### 12.1 Warum ein gemeinsamer Währungsraum?

Erde, Mond und Orbit sind physisch verbunden. Satelliten liefern Kommunikation, Navigation, Klimadaten, Forschung und Sicherheit. Raumstationen und Mondhabitate hängen von Lieferketten, Energie, Wasser, Sauerstoff, Reparatur und präziser Information ab. Ein Fehler im Orbit kann irdische Kommunikation treffen. Eine schlechte Erdpolitik kann Mondlogistik gefährden. Deshalb ist ein gemeinsames Abrechnungssystem sinnvoll.

### 12.2 Orbit-Domäne

Orbitverhalten hat besonders hohe Risikogewichte:

- Kollisionsvermeidung,
- Trümmervermeidung,
- Bahnkorrekturen,
- sichere Deorbit-Prozesse,
- Frequenzdisziplin,
- Strahlungswarnungen,
- Stationssicherheit,
- Notfallprotokolle,
- Datenintegrität.

Ein Betreiber, der Satelliten sicher entsorgt, erhält positive Delta. Ein Betreiber, der Trümmer erzeugt, erhält massive negative Delta und muss Sicherheiten hinterlegen.

### 12.3 Mond-Domäne

Auf dem Mond sind Wasser, Energie, geschlossene Kreisläufe, Habitatdruck, Strahlungsschutz, Reparierbarkeit und psychologische Stabilität entscheidend. Die Gewichte unterscheiden sich daher von der Erde.

Ein Verhalten, das auf der Erde harmlos ist, kann auf dem Mond teuer sein. Ein kleines Leck, ein unnötiger Materialverlust oder falsche Information über Vorräte kann dort lebensgefährlich sein.

### 12.4 Raumstations-Domäne

In Raumstationen gilt eine besondere Regel:

> Lebensunterhalt darf nie wegen negativem Kontostand verweigert werden.

Luft, Druck, Temperatur, medizinische Notversorgung und Rückkehrsicherheit sind Grundrechte. Negative Delta erzeugt Verpflichtungen, aber keine akute Erpressbarkeit.

---

## 13. Persönliche Konten

Jeder Akteur hat mehrere getrennte Konten:

### 13.1 Alltagskonto

Für Käufe, Löhne, Miete, Nahrung, Mobilität, Medien und normale Verträge.

### 13.2 Grundversorgungskonto

Nicht pfändbar. Deckt minimale Nahrung, Wasser, Wohnen, Gesundheit, Kommunikation und grundlegende Mobilität.

### 13.3 Vertragskonto

Für spezifische Verhaltensverträge mit klaren Nachweisen.

### 13.4 Haftungskonto

Für negative Delta, Rückstellungen, Schäden und Wiedergutmachung.

### 13.5 Reputationsregister

Kein universeller Sozialscore. Es enthält domänenspezifische, erklärbare, anfechtbare Verhaltensnachweise. Ein guter Journalist muss nicht automatisch ein guter Mechaniker sein. Ein schlechter Kreditnehmer darf nicht automatisch politisch entwertet werden.

---

## 14. Datenschutz und Freiheit

Ein Wirtschaftssystem, das Verhalten bewertet, ist gefährlich, wenn es falsch gebaut wird. Es kann Freiheit zerstören, Konformismus erzwingen und Macht missbrauchen. Deshalb enthält das Modell harte Grenzen.

### 14.1 Nur wirtschaftlich relevante Verhaltensereignisse

Private Gedanken, intime Beziehungen, legale politische Meinungen, Religion, Kunstgeschmack, persönliche Lebensführung und nicht-schädliche Eigenheiten sind keine allgemeine Währungsgrundlage.

### 14.2 Datenminimalität

Für jede Buchung gilt:

> Es darf nur die geringste Datenmenge verarbeitet werden, die zur Abrechnung nötig ist.

Wenn ein Zero-Knowledge-Nachweis reicht, darf kein Rohdatum gespeichert werden. Wenn eine aggregierte Messung reicht, darf keine Personendauerüberwachung erfolgen.

### 14.3 Erklärbarkeit

Jede relevante Delta-Buchung muss erklärbar sein:

- Welche Domäne?
- Welcher Vektor?
- Welche Norm?
- Welche Gewichte?
- Welche Beweise?
- Welche Einspruchsfrist?

### 14.4 Einspruch

Jeder Akteur kann Delta-Buchungen anfechten. Bei hohem Schaden gilt menschliche Prüfung. Automatische Systeme dürfen vorläufig buchen, aber nicht endgültig über existenzielle Rechte entscheiden.

---

## 15. Demokratische Normsetzung

Die wichtigste politische Frage lautet: Wer bestimmt die Gewichte?

Die Antwort in diesem Modell lautet: nicht eine Person, nicht ein Konzern, nicht allein die Zentralbank.

### 15.1 Normenverfassung

Es gibt eine **Delta-Normenverfassung**. Sie legt fest:

- welche Domänen überhaupt bewertet werden dürfen,
- welche Daten verboten sind,
- welche Grundrechte unantastbar sind,
- wie Gewichte geändert werden,
- wie Minderheiten geschützt werden,
- wie wissenschaftliche Evidenz eingeht,
- wie Notfallnormen befristet werden.

### 15.2 Normparlamente

Für wichtige Domänen gibt es Normparlamente oder Normräte:

- Medienrat,
- Arbeitsrat,
- Nahrungsrat,
- Energierat,
- Orbitrat,
- Mondrat,
- Gesundheitsrat,
- Datenschutzrat.

Diese Räte definieren nicht jede einzelne Zahlung, sondern die zulässigen Normrahmen.

### 15.3 Langsame Änderungen

Normen dürfen nicht hektisch geändert werden, weil sonst Geld instabil wird. Gewichtsänderungen haben:

- Ankündigungsfrist,
- Testphase,
- Folgenabschätzung,
- Einspruchsphase,
- Übergangsregeln.

---

## 16. Inflation, Deflation und Stabilität

### 16.1 Delta-Preisindex

Die ZEMO misst einen **Delta-Preisindex**. Er enthält nicht nur Waren, sondern Verhaltensbündel:

- Grundnahrung,
- Wohnraum,
- Energie,
- Kommunikation,
- Gesundheitsbasis,
- Transport,
- glaubwürdige Nachrichten,
- Arbeitsstunde verschiedener Qualifikationen,
- Orbit-Sicherheitsdienst,
- Stationsversorgung,
- Mondlogistik.

### 16.2 Inflation

Inflation entsteht, wenn zu viel Delta für schwach verifizierte oder überbewertete Plusnormen geschaffen wird. Gegenmittel:

- Verifikationsfaktor senken,
- \(\lambda_d\) reduzieren,
- Norm-Gewichte prüfen,
- Geldschöpfung auf öffentliche Aufträge begrenzen,
- Rückstellungen erhöhen,
- Scheinverhalten sanktionieren.

### 16.3 Deflation

Deflation entsteht, wenn zu wenig Delta entsteht oder zu viele negative Buchungen Kaufkraft vernichten. Gegenmittel:

- öffentliche Delta-Aufträge,
- Grundversorgungsdelta erhöhen,
- Liquidität bereitstellen,
- belastende Normen überprüfen,
- produktive Verhaltenserzeugung vorfinanzieren.

---

## 17. Steuern und öffentliche Güter

Steuern sind in diesem System keine bloße Abgabe, sondern eine Umlenkung von Delta in gemeinschaftliche Verhaltensaufträge.

### 17.1 Steuerarten

- Ressourcenbelastungssteuer,
- Aufmerksamkeitsmarktabgabe,
- Orbitrisikoabgabe,
- Medienmanipulationshaftung,
- Luxusverbrauchsabgabe,
- Infrastrukturbeitrag,
- Automatisierungsdividende,
- Datenextraktionsabgabe.

### 17.2 Öffentliche Güter

Steuereinnahmen kaufen Verhalten, das Märkte unterproduzieren:

- Grundlagenforschung,
- öffentliche Dateninfrastruktur,
- Bildung,
- Pflege,
- Katastrophenschutz,
- vertrauenswürdige Nachrichtenarchive,
- Orbitreinigung,
- Klimaanpassung,
- Mond- und Stationssicherheit.

---

## 18. Versicherungen

Versicherungen bündeln negative Delta-Risiken. Eine Station versichert Druckverlust. Ein Medienhaus versichert Recherchefehler. Ein Landwirt versichert Ernteausfall. Ein Satellitenbetreiber versichert Kollisionsrisiken.

Die Prämie ist:

\[
Premium=\mathbb{E}[negative\;\Delta]+capital\;buffer+verification\;cost+systemic\;risk
\]

Versicherungen haben einen positiven Effekt: Sie belohnen Prävention. Wer nachweislich Risiken senkt, zahlt weniger.

---

## 19. Bildung und Kultur

Bildung erzeugt zukünftige positive Delta-Fähigkeit. Kultur erzeugt Sinn, Kooperation, Identität, Kritikfähigkeit und psychologische Stabilität. Das Modell darf Kultur nicht nur nach Markt-Klicks bewerten.

Eine kulturelle Leistung kann positive Delta haben, wenn sie:

- Wissen bewahrt,
- Gemeinschaft stiftet,
- Kritik ermöglicht,
- Traumata verarbeitet,
- Kreativität erhöht,
- psychologische Gesundheit stärkt,
- Dialog zwischen Gruppen ermöglicht.

Aber Kunst darf nicht zur reinen Normerfüllung werden. Deshalb braucht Kultur einen Autonomiebereich, in dem Experimente geschützt sind, auch wenn ihr Nutzen erst später sichtbar wird.

---

## 20. Beispielrechnungen

### 20.1 Raumstationswartung

Ein Techniker repariert ein CO₂-Filtersystem.

- Plusnorm: Sicherheit, Lebensschutz, Fehlerreduktion, Dokumentation = 13,0
- Minusnorm: Materialverbrauch, Arbeitsrisiko, Ausfallzeit = 2,0
- \(\lambda_{station}=20\)

\[
\mu=20(13-2)=220\Delta
\]

Der Techniker oder sein Team erhält 220 Delta. Ein Teil kann direkt von der Station bezahlt werden, ein Teil kann von der ZEMO als Systemstabilitätsgeld geschaffen werden.

### 20.2 Manipulative Massennachricht

Ein Medium veröffentlicht eine stark verbreitete, irreführende Schlagzeile.

- Plusnorm: öffentliche Relevanz und Aktualität = 1,0
- Minusnorm: Täuschung, Schaden, Korrekturverzögerung, Aufmerksamkeitsmissbrauch = 9,0
- \(\lambda_{news}=10\)

\[
\mu=10(1-9)=-80\Delta
\]

Das Medium muss 80 Delta zahlen oder durch Korrekturverhalten teilweise ausgleichen.

### 20.3 Gute lokale Warnmeldung

Eine kleine Redaktion meldet rechtzeitig ein Trinkwasserproblem mit Quellen und Handlungshinweisen.

- Plusnorm: Relevanz, Genauigkeit, Prävention, Korrekturstruktur = 8,4
- Minusnorm: Unsicherheit, Aufmerksamkeitskosten = 1,2
- \(\lambda_{news}=10\)

\[
\mu=10(8,4-1,2)=72\Delta
\]

Die Redaktion verdient 72 Delta, auch wenn die Reichweite kleiner ist als bei großen Medien.

### 20.4 Nahrung

Eine Mahlzeit hat hohen Nährwert, geringe Verschwendung, aber moderaten Transportaufwand.

- Plusnorm: Ernährung, Gesundheit, lokale Resilienz = 4,0
- Minusnorm: Energie, Verpackung, Transport = 2,7
- \(\lambda_{food}=5\)

\[
\mu=5(4,0-2,7)=6,5\Delta
\]

Die Lieferkette kann positive Delta erhalten. Der Käufer zahlt trotzdem einen Preis, weil er Arbeit, Material und Organisation der Kette vergütet. Der positive Norm-Spread kann den Preis senken.

---

## 21. Missbrauch und Gegenmaßnahmen

### 21.1 Norm-Gaming

Akteure könnten versuchen, nur die gemessenen Koordinaten zu optimieren. Gegenmaßnahmen:

- zufällige Audits,
- robuste Indikatoren,
- Messrotation,
- qualitative Prüfung,
- Whistleblower-Belohnung,
- spätere Nachbuchung versteckter Schäden.

### 21.2 Verhaltensmonopole

Wer Messdaten kontrolliert, könnte die Wirtschaft kontrollieren. Gegenmaßnahmen:

- offene Standards,
- unabhängige Orakel,
- Datenportabilität,
- Trennung von Messung und Zahlung,
- öffentliche Referenzmodelle.

### 21.3 Politische Unterdrückung

Die größte Gefahr ist, dass eine Regierung oder Zentralbank Normen nutzt, um Opposition zu bestrafen. Gegenmaßnahmen:

- Verbot von Gesinnungskoordinaten,
- Schutz politischer Meinung,
- unabhängige Rechtekammer,
- Medienpluralismus,
- internationale und orbitale Vetorechte,
- öffentliche Normhistorie,
- gerichtliche Überprüfung.

### 21.4 Arme werden dauerhaft negativ

Wenn negative Delta zu streng wirken, werden Menschen gefangen. Gegenmaßnahmen:

- Grundversorgungskonto,
- Schuldenschnitt nach Wiedergutmachung,
- Bildungs- und Arbeitszugang,
- keine Zinsen auf existenzielle Negativkonten,
- restorative statt rein punitive Logik.

---

## 22. Implementierungsphasen

### Phase 1: Freiwillige Pilotmärkte

Start in Bereichen, in denen Verhalten gut messbar und gesellschaftlich nützlich ist:

- Recycling,
- Energieeinsparung,
- lokale Nachrichtenqualität,
- Pflegeleistungen,
- Open-Source-Sicherheitsarbeit,
- Stations- und Satellitensicherheit.

### Phase 2: Öffentliche Delta-Aufträge

Gemeinden, Stationen und Forschungseinrichtungen kaufen mit Delta konkrete Verhaltensleistungen.

### Phase 3: Teilwährung

Delta wird neben bestehenden Währungen verwendet. Preise werden doppelt ausgezeichnet.

### Phase 4: Erde-Mond-Orbit-Abrechnung

Satelliten, Raumstationen und Mondhabitate nutzen Delta als primäre Abrechnungseinheit für Sicherheit, Logistik, Energie, Wasser, Nachrichten und Wartung.

### Phase 5: Vollwirtschaft mit Verfassung

Erst nach stabiler Erfahrung, demokratischer Legitimation und starken Grundrechten wird Delta zur dominanten Währung.

---

## 23. Philosophischer Kern

Dieses System macht sichtbar, was in jeder Wirtschaft bereits geschieht: Menschen bezahlen einander dafür, dass sie Verhalten verändern. Ein Lohn verändert Arbeitsverhalten. Ein Preis verändert Konsumverhalten. Werbung verändert Aufmerksamkeitsverhalten. Nachrichten verändern Erwartungsverhalten. Kredite verändern Zukunftsverhalten. Steuern verändern Ressourcenverhalten.

Der Unterschied ist: Das Delta-System sagt offen, was bewertet wird, und zwingt die Bewertung in transparente mathematische Formen.

Das ist seine Stärke und seine Gefahr.

Seine Stärke: Versteckte Kosten werden sichtbar. Medienverhalten wird verantwortlicher. Orbit- und Mondrisiken werden korrekt bepreist. Öffentliche Güter können direkt bezahlt werden.

Seine Gefahr: Wenn falsch gebaut, wird es eine Maschine zur sozialen Kontrolle.

Darum ist die wichtigste Formel nicht nur:

\[
\mu(e)=\lambda(\|e\|_+-\|e\|_-)
\]

sondern auch:

> Kein Delta ohne Rechte. Keine Norm ohne Einspruch. Keine Medienbewertung ohne Pluralismus. Keine Verhaltensökonomie ohne Privatsphäre. Keine Zentralbank ohne Gewaltenteilung.

---

## 24. Minimale Verfassung des Delta-Systems

1. **Menschenwürde ist nicht käuflich.** Delta bewertet Handlungen, nicht den Wert einer Person.
2. **Kein universeller Sozialscore.** Es gibt domänenspezifische Nachweise, keine totale Bürgerzahl.
3. **Grundversorgung ist garantiert.** Nahrung, Wasser, Luft, Notmedizin, Basiskommunikation und Schutz vor akuter Gefahr sind nicht von Kontostand abhängig.
4. **Politische Meinung ist geschützt.** Bewertet werden überprüfbare Schäden und Vertragsbrüche, nicht Gesinnung.
5. **Medienpluralismus ist Pflicht.** Wahrheitsprozesse werden bewertet, nicht erlaubte Ideologien.
6. **Jede Norm ist öffentlich.** Gewichte, Formeln, Datenquellen und Änderungen sind nachvollziehbar.
7. **Jede relevante Buchung ist anfechtbar.** Automatisierung ersetzt keine Rechte.
8. **Datenminimalität gilt immer.** Kein Rohdatum, wenn ein Nachweis reicht.
9. **Normen ändern sich langsam.** Geld darf nicht durch plötzliche Bewertungswechsel zerstört werden.
10. **ZEMO ist geteilt.** Geldpolitik, Normsetzung, Datenprüfung und Rechtekontrolle sind getrennt.

---

## 25. Kompakte Definition

Das Delta-Norm-Wirtschaftssystem ist eine Wirtschaftsordnung, in der jede wirtschaftlich relevante Handlung als Vektor in einem domänenspezifischen Verhaltensraum dargestellt wird. Zwei mathematische Normen messen Beitrag und Belastung dieser Handlung. Die Differenz der beiden Normwerte, skaliert durch geldpolitische Faktoren, erzeugt einen positiven oder negativen Delta-Betrag. Dieser Betrag dient als Währung, Preis, Lohn, Steuerbasis, Kreditgrundlage, Versicherungsmaß und Steuerungsimpuls. Eine Zentralbank für Erde, Mond, Satelliten und Raumstationen stabilisiert die Währung, während eine Normenverfassung verhindert, dass aus Verhaltensgeld ein totalitäres Kontrollsystem wird.

---

# Part II – English

## 1. Core Idea

In a conventional economy, people pay money for things: bread, electricity, labor time, transportation, news, entertainment, housing, machines, and loans. In this model, everything is interpreted as **behavior**.

A loaf of bread is not merely an object. It is the sum of many behavioral chains: sowing, watering, fertilizing, harvesting, milling, baking, transporting, selling, eating, and disposing. A news item is not just text. It is behavior: investigating, verifying, framing, publishing, correcting, and distributing. Labor is obviously behavior. Consumption is behavior. Even non-action can be behavior, such as failing to repair a life-support system on a station.

The central thesis is:

> An economy is a system for coordinating behavior. Money is the number that makes behavioral deviations measurable, tradable, and settleable.

This system makes that thesis explicit. It does not say, “money buys things.” It says:

> Money buys, rewards, burdens, or transfers behavior.

Behavior is evaluated through two mathematical norms. The monetary amount is the difference between the normed contribution and the normed burden.

---

## 2. Mathematical Core

### 2.1 Behavioral Space

Let \(A\) be the set of all actors: individuals, companies, media organizations, AI agents, research institutions, satellite operators, space stations, lunar habitats, municipalities, states, or cooperatives.

An economically relevant event is:

\[
e=(a,t,l,d,z)
\]

where:

- \(a\): actor,
- \(t\): time or period,
- \(l\): location or infrastructure context, such as Earth, Moon, satellite, or station,
- \(d\): behavioral domain, such as food, labor, media, or energy,
- \(z\): observable or provable event data.

For each domain \(d\), there is a map:

\[
\Phi_d:E_d\to\mathbb{R}^{n_d}
\]

This map turns an event into a vector. Examples:

- A labor event becomes a vector of time, quality, safety, cooperation, reliability, learning contribution, and resource use.
- A news event becomes a vector of factual accuracy, source quality, public relevance, timeliness, correction behavior, manipulation risk, and attention consumption.
- A food event becomes a vector of nutrition, energy use, material flow, health effect, waste, scarcity, and cultural value.

### 2.2 Two Norms

For every domain, there are two mathematical norms on the same or a transformed vector space:

\[
\|x\|_{+,d}
\]

and

\[
\|x\|_{-,d}
\]

The **plus norm** measures contribution. The **minus norm** measures burden.

A typical form is a weighted \(p\)-norm:

\[
\|x\|_{+,d}=\left(\sum_{j=1}^{n_d}w^+_{d,j}|x_j|^{p_d}\right)^{1/p_d}
\]

\[
\|x\|_{-,d}=\left(\sum_{j=1}^{n_d}w^-_{d,j}|x_j|^{q_d}\right)^{1/q_d}
\]

with positive weights \(w^+_{d,j}\) and \(w^-_{d,j}\). The weights define what matters in a domain. In a space station, oxygen safety is weighted more heavily than comfort. In journalism, source quality is weighted more heavily than clicks. In agriculture, nutrition, soil, water, energy, labor conditions, and waste matter.

### 2.3 Money as Norm Spread

The monetary value of an event is:

\[
\mu(e)=\lambda_d\left(\|P^+_d\Phi_d(e)\|_{+,d}-\|P^-_d\Phi_d(e)\|_{-,d}\right)
\]

Here \(P^+_d\) and \(P^-_d\) are projections or filters. They separate coordinates counted as contribution from coordinates counted as burden. \(\lambda_d\) is a conversion factor set by the central bank.

- \(\mu(e)>0\): behavior creates net contribution. The actor receives Delta.
- \(\mu(e)=0\): contribution and burden cancel out.
- \(\mu(e)<0\): behavior creates net burden. The actor pays Delta or receives a restorative obligation.

The currency unit is:

\[
1\;\Delta
\]

or simply:

\[
1\;D
\]

The balance of actor \(a\) evolves as:

\[
B_a(t+1)=B_a(t)+\sum_{e\in E_a(t)}\mu(e)+T_a(t)-F_a(t)
\]

where:

- \(B_a(t)\): Delta account balance,
- \(E_a(t)\): events of the actor during the period,
- \(T_a(t)\): transfers, wages, purchases, contractual payments,
- \(F_a(t)\): fees, taxes, repayments, sanctions, compensation duties.

---

## 3. Why This Is Money

For something to be money, it must perform at least four functions.

### 3.1 Unit of Account

Delta is the common number in which prices are quoted. A media article, a kilogram of food, an hour of maintenance labor, an orbital correction, medical service, research output, and an advertising campaign can all be priced in Delta.

### 3.2 Medium of Exchange

Actors transfer Delta when they buy behavior. A habitat can buy maintenance behavior. A municipality can buy investigative reporting. A person can buy food, meaning the behavioral chain behind the food. A company can buy labor behavior.

### 3.3 Store of Value

Delta is a claim on future recognized positive behavior by other actors. Holding Delta is not holding moral rank. It is holding purchasing power over behavioral services.

### 3.4 Standard of Deferred Payment

Loans, insurance contracts, bonds, wages, and leases are written as claims on future Delta flows. A loan is the expectation that the debtor will generate enough positive behavioral deltas or receive enough Delta transfers in the future.

---

## 4. Central Bank of the Earth-Moon-Orbit System: ZEMO

### 4.1 Name and Jurisdiction

The central bank is called:

**Central Bank of the Earth-Moon-Orbit System**, abbreviated **ZEMO**.

Its currency area includes:

- Earth,
- the Moon,
- satellites in Earth orbit,
- space stations in Earth orbit,
- communication, navigation, energy, and research infrastructure between Earth and Moon.

Later, the system can be expanded to Mars, asteroids, or other habitats. The initial core is Earth-Moon-Orbit because resources, communications, dependencies, and safety questions are tightly linked there.

### 4.2 Mandate

ZEMO has six main tasks:

1. **Stability of the Delta currency**: Delta purchasing power should remain stable across basic goods and basic behaviors.
2. **Norm transparency**: The norms, weights, data sources, and calculations must be publicly auditable.
3. **Money creation and destruction**: Delta is created when verifiable behavior increases system capacity. Delta is destroyed or locked when behavior consumes scarce resources or creates risks.
4. **Settlement and finality**: Transactions between Earth, Moon, satellites, and stations must settle safely, even with communication delays or outages.
5. **Protection against manipulation**: Norm gaming, fake data, media manipulation, fake behavior, and artificial scarcity are detected and sanctioned.
6. **Rights and limits**: ZEMO must not become a total behavior police system. It protects appeals, privacy, basic access, and plural ways of life.

### 4.3 Separation of Powers Within ZEMO

To prevent the central bank from defining all social values, it is divided into separate chambers.

#### A. Monetary Chamber

It sets conversion factors \(\lambda_d\), liquidity quotas, reserve requirements, and stability targets.

#### B. Norm Chamber

It manages mathematical norm families but may change weights only through transparent procedures. It is not identical to the government.

#### C. Data and Oracle Chamber

It certifies measurement systems, sensors, media evidence, labor proofs, supply-chain proofs, and audits.

#### D. Rights Chamber

It reviews complaints, protects privacy, stops abusive norms, and can suspend settlements.

#### E. Earth-Moon-Orbit Council

It ensures that Earth, Moon, satellite operators, and space stations do not dominate each other. A lunar colony must not be judged only by Earth comfort norms. An Earth region must not be forced to live by emergency station norms.

---

## 5. Money Creation

Delta is not created by arbitrary printing. Delta emerges from verified net contribution.

### 5.1 Primary Money Creation

ZEMO credits new Delta when behavior demonstrably increases system capacity. Examples:

- repairing critical infrastructure,
- producing food with low burden and high supply security,
- improving oxygen, water, or energy recycling in habitats,
- reliable public-interest journalism,
- medical care,
- education and training,
- reproducible research,
- risk reduction in orbit, such as debris prevention or removal,
- care work and social stabilization,
- software and security maintenance for critical systems.

Mathematically:

\[
\Delta M^+_t=\sum_{e\in E_t^{valid}}\max(0,\mu(e))\cdot \rho_e
\]

\(\rho_e\) is a verification factor between 0 and 1. Unclear or weakly proven events create less or provisional Delta.

### 5.2 Money Destruction

Delta is destroyed, locked, or reserved when behavior consumes scarce system capacity or creates risks:

- high resource use,
- avoidable waste,
- dangerous orbital behavior,
- misinformation with measurable harm,
- breach of contract,
- infrastructure wear,
- production with hidden downstream costs,
- attention exploitation through deception.

Mathematically:

\[
\Delta M^-_t=\sum_{e\in E_t^{valid}}\max(0,-\mu(e))\cdot \sigma_e
\]

\(\sigma_e\) is a burden or liability factor.

### 5.3 Secondary Transfers

Most everyday payments do not create new money. They transfer existing Delta:

- wages,
- food purchases,
- media subscriptions,
- rent,
- repair contracts,
- transport tickets,
- software licenses,
- station maintenance.

The distinction matters: not every good action prints money. Otherwise inflation follows. Money creation requires verified net growth in system capacity or a public mandate approved by ZEMO.

---

## 6. Behavioral Markets

### 6.1 Behavioral Contract

A market contract is no longer only “good for money.” It is:

\[
C=(a,b,d,T,g,\Pi,E,p)
\]

where:

- \(a\): buyer,
- \(b\): provider,
- \(d\): domain,
- \(T\): period,
- \(g\): target vector or behavioral target,
- \(\Pi\): price formula in Delta,
- \(E\): proof standard,
- \(p\): privacy level.

Example: A space station buys from a technician not “one hour of time,” but “safe maintenance behavior on the CO₂ filter with documented inspection and risk reduction.” The technician is paid not for mere presence, but for verified behavior.

### 6.2 Behavioral Exchange

There are exchanges for standardized behavior types:

- labor deltas,
- care deltas,
- research deltas,
- news and truth deltas,
- energy deltas,
- recycling deltas,
- orbital safety deltas,
- food deltas,
- transport deltas,
- education deltas.

A provider sells the readiness or ability to generate behavior. A buyer acquires the behavior or its result.

### 6.3 Prices

The price of a behavioral bundle is:

\[
P(C)=\mathbb{E}\left[\sum_{e\in C}\mu(e)\right]+R(C)+L(C)+K(C)
\]

where:

- expected norm spread,
- risk premium \(R(C)\),
- liquidity premium \(L(C)\),
- coordination cost \(K(C)\).

---

## 7. Labor and Employment

In this system, labor is a contractually bounded behavioral space. An employer does not buy the person. It buys specific, defined, time-limited behavioral events.

### 7.1 Labor Vector

A labor event may contain coordinates such as:

- time input,
- output quality,
- safety behavior,
- team coordination,
- reliability,
- learning contribution,
- documentation quality,
- resource use,
- error rate,
- recovery and overload risk.

The plus norm rewards quality, safety, cooperation, and learning. The minus norm burdens errors, avoidable risks, resource waste, and harm to others.

### 7.2 Wage

A wage is an expected positive Delta flow:

\[
W_a=\sum_{t\in T}\mathbb{E}[\mu(e_{a,t}^{work})]+\text{scarcity premium}+\text{risk compensation}
\]

This must not mean that every private moment of an employee is evaluated. Only contractually defined, work-relevant, legally permissible behavioral data may be used.

### 7.3 Employee Rights

Hard rules apply:

- no scoring of private thoughts,
- no permanent surveillance without a specific purpose,
- no hidden biometric analysis,
- right to explanation for every relevant Delta entry,
- right to appeal,
- right to off-work spaces,
- minimum wage or basic Delta for necessary labor,
- protection against discrimination through norm weights.

---

## 8. Food, Eating, and Consumption

### 8.1 Food as Behavior

Eating is consumption behavior, health behavior, cultural behavior, and supply-chain behavior at the same time. A food price therefore contains not only supply and demand, but the Delta spread of the entire chain.

A food vector may include:

- calories,
- micronutrients,
- proteins,
- water use,
- energy use,
- soil burden,
- transport distance,
- cooling effort,
- waste,
- labor conditions,
- health effects,
- cultural or social value.

### 8.2 Price Formula

Food costs Delta when its burden norm is high. It can be subsidized or even positively scored when it strengthens nutrition, health, circularity, and local resilience.

Example:

\[
\mu(food)=\lambda_{food}(\|nutrition+resilience+culture\|_+-\|scarcity+waste+harm\|_-)
\]

Normal eating must not be morally criminalized. Therefore, there is a **basic access Delta**. Every person receives access to necessary food, water, basic medical care, housing, and communication. The Delta system steers scarcity and behavior, but existence itself must not become a commodity.

### 8.3 Consumption in General

Consumption means buying the behavioral chain that created a product and accepting part of the future behavioral consequences. A smartphone is not just a device. It is mining, factory, design, software, transportation, usage, repair, and disposal behavior.

The price includes:

- production delta,
- material delta,
- labor delta,
- usage delta,
- repairability delta,
- recycling delta,
- information delta, such as truth in advertising.

---

## 9. Media, Mass Media, and News

This domain is central because news is not merely information. It shapes behavior. Whoever controls news influences consumption, labor, elections, safety, markets, fear, trust, and conflict. Therefore, the Delta system needs especially strict rules for media.

### 9.1 News as Behavioral Event

A news event \(e_{news}\) may include coordinates such as:

- factual accuracy,
- source quality,
- source transparency,
- separation of news and opinion,
- timeliness,
- public relevance,
- correction speed,
- contextual depth,
- uncertainty labeling,
- sensationalism,
- manipulative intent,
- attention consumption,
- harm through misdirection,
- protection of vulnerable persons,
- diversity of perspectives.

### 9.2 Media Delta

The money formula is:

\[
\mu(news)=\lambda_{news}(\|truth+relevance+correction+context\|_+-\|deception+manipulation+avoidable_harm\|_-)
\]

A media organization does not earn Delta merely through reach. Reach without quality may become negative. A small, accurately researched local warning can earn more Delta than a massively distributed but manipulative headline.

### 9.3 No Truth Dictatorship

The system must not decide: “This opinion is allowed, that opinion is forbidden.” It evaluates verifiable media behavior, not political belief:

- Were sources provided?
- Were factual claims checked?
- Was uncertainty marked?
- Was a false claim corrected?
- Was opinion labeled as opinion?
- Was a false representation intentionally spread?
- Was a person or group harmed by demonstrably false information?

Unpopular, new, or uncomfortable positions must not be penalized merely because they are uncomfortable. New hypotheses receive an uncertainty status, not a punishment status.

### 9.4 Mass Media and Attention Markets

Attention is itself a scarce behavioral space. Mass media buy attention and sell behavioral probability to advertisers, parties, companies, or movements. In the Delta system, that behavior is accounted for as well.

An advertising campaign has positive Delta when it conveys useful, truthful information. It has negative Delta when it manipulates, conceals, exploits addiction-like patterns, or intentionally creates false expectations.

### 9.5 News Fund

ZEMO does not operate a propaganda fund. It operates a **public news fund**. This fund buys specific behavioral services:

- disaster warnings,
- local investigations,
- scientific replication,
- corruption exposure,
- infrastructure warnings,
- space-weather and orbital-risk reporting,
- health information,
- factual archives.

It is financed by a small Delta fee on large attention markets and by direct ZEMO money creation for verified public information goods.

---

## 10. Firms

A firm is an actor that organizes behavioral chains. Profit is not only revenue minus cost, but positive Delta flow minus negative Delta flow.

\[
Profit_\Delta=\sum \mu(e_{sales})+\sum \mu(e_{production})-\sum \mu(e_{resource})-\sum \mu(e_{risk})
\]

A firm can become wealthy when it coordinates behavior that produces more system capacity than burden. It cannot become sustainably wealthy by hiding costs, because hidden costs are later booked back as negative Delta.

### 10.1 Balance Sheet

A Delta balance sheet includes:

- financial account,
- behavioral assets,
- reputation and trust delta,
- resource obligations,
- damage reserves,
- media and information liability,
- labor behavior obligations,
- circularity and disposal duties.

### 10.2 Insolvency

Insolvency means not only inability to pay. It means inability to credibly generate future positive Delta flows. Restructuring means changing firm behavior so the plus norm again exceeds the minus norm.

---

## 11. Credit, Interest, and Wealth

### 11.1 Credit

A loan is a contract over future Delta flows. The bank does not only ask, “What collateral do you have?” It asks:

> What positive behavioral deltas can you plausibly generate in the future?

The loan amount is the present value of expected Delta flows:

\[
Loan\leq \sum_{t=1}^{T}\frac{\mathbb{E}[\mu_t]}{(1+r_t)^t}\cdot \theta
\]

\(\theta\) is a safety factor.

### 11.2 Interest

Interest consists of:

- time preference,
- default risk,
- norm-change risk,
- liquidity risk,
- verification risk,
- system risk.

### 11.3 Wealth

Wealth is the ability to control or receive future positive Delta flows. Land, machines, media brands, software, data, satellites, lunar habitats, and patents are wealth when they are expected to generate positive norm spreads.

---

## 12. Earth, Moon, Satellites, and Space Stations

### 12.1 Why One Currency Area?

Earth, Moon, and orbit are physically linked. Satellites provide communication, navigation, climate data, research, and security. Space stations and lunar habitats depend on supply chains, energy, water, oxygen, repair, and precise information. A mistake in orbit can affect terrestrial communications. Poor Earth policy can endanger lunar logistics. Therefore, a shared settlement system is reasonable.

### 12.2 Orbital Domain

Orbital behavior has especially high risk weights:

- collision avoidance,
- debris prevention,
- orbital corrections,
- safe deorbiting,
- frequency discipline,
- radiation warnings,
- station safety,
- emergency protocols,
- data integrity.

An operator that safely disposes of satellites receives positive Delta. An operator that creates debris receives massive negative Delta and must post collateral.

### 12.3 Lunar Domain

On the Moon, water, energy, closed loops, habitat pressure, radiation protection, repairability, and psychological stability are decisive. The weights therefore differ from Earth.

Behavior that is harmless on Earth may be costly on the Moon. A small leak, unnecessary material loss, or false information about reserves can become life-threatening there.

### 12.4 Space Station Domain

Space stations have a special rule:

> Life support must never be denied because of a negative balance.

Air, pressure, temperature, emergency medical care, and return safety are basic rights. Negative Delta creates obligations, but not immediate coercive vulnerability.

---

## 13. Personal Accounts

Every actor has several separated accounts.

### 13.1 Everyday Account

For purchases, wages, rent, food, mobility, media, and ordinary contracts.

### 13.2 Basic Access Account

Non-seizable. Covers minimal food, water, housing, health, communication, and basic mobility.

### 13.3 Contract Account

For specific behavioral contracts with clear proof standards.

### 13.4 Liability Account

For negative Delta, reserves, damages, and restorative obligations.

### 13.5 Reputation Register

Not a universal social score. It contains domain-specific, explainable, appealable behavioral proofs. A good journalist is not automatically a good mechanic. A bad debtor must not be politically devalued.

---

## 14. Privacy and Freedom

An economy that evaluates behavior is dangerous if built badly. It can destroy freedom, enforce conformity, and abuse power. Therefore, this model contains hard limits.

### 14.1 Only Economically Relevant Behavioral Events

Private thoughts, intimate relationships, legal political opinions, religion, taste in art, personal life choices, and harmless eccentricity are not general currency sources.

### 14.2 Data Minimization

For every entry:

> Only the smallest amount of data necessary for settlement may be processed.

If a zero-knowledge proof is enough, raw data must not be stored. If an aggregate measurement is enough, no permanent personal monitoring may occur.

### 14.3 Explainability

Every relevant Delta entry must be explainable:

- Which domain?
- Which vector?
- Which norm?
- Which weights?
- Which evidence?
- Which appeal period?

### 14.4 Appeals

Every actor can dispute Delta entries. For high-impact cases, human review is required. Automated systems may post provisional entries, but they must not make final decisions about existential rights.

---

## 15. Democratic Norm Setting

The most important political question is: Who sets the weights?

The answer in this model is: not one person, not one corporation, and not the central bank alone.

### 15.1 Norm Constitution

There is a **Delta Norm Constitution**. It determines:

- which domains may be evaluated at all,
- which data are forbidden,
- which basic rights are untouchable,
- how weights are changed,
- how minorities are protected,
- how scientific evidence enters,
- how emergency norms expire.

### 15.2 Norm Councils

Major domains have norm parliaments or councils:

- media council,
- labor council,
- food council,
- energy council,
- orbital council,
- lunar council,
- health council,
- privacy council.

These councils do not define every payment. They define the permissible norm frameworks.

### 15.3 Slow Changes

Norms must not change frantically, or money becomes unstable. Weight changes require:

- advance notice,
- testing period,
- impact assessment,
- appeal period,
- transition rules.

---

## 16. Inflation, Deflation, and Stability

### 16.1 Delta Price Index

ZEMO measures a **Delta Price Index**. It contains not only goods, but behavioral bundles:

- basic food,
- housing,
- energy,
- communication,
- basic health,
- transport,
- credible news,
- labor hours at different skill levels,
- orbital safety service,
- station supply,
- lunar logistics.

### 16.2 Inflation

Inflation occurs when too much Delta is created for weakly verified or overvalued plus norms. Countermeasures:

- lower the verification factor,
- reduce \(\lambda_d\),
- review norm weights,
- limit money creation to public mandates,
- increase reserves,
- sanction fake behavior.

### 16.3 Deflation

Deflation occurs when too little Delta is created or too many negative entries destroy purchasing power. Countermeasures:

- public Delta contracts,
- increase basic access Delta,
- provide liquidity,
- review overly burdensome norms,
- pre-finance productive behavior creation.

---

## 17. Taxes and Public Goods

Taxes in this system are not merely extraction. They redirect Delta into shared behavioral contracts.

### 17.1 Tax Types

- resource burden tax,
- attention-market fee,
- orbital-risk fee,
- media manipulation liability,
- luxury consumption fee,
- infrastructure contribution,
- automation dividend,
- data extraction fee.

### 17.2 Public Goods

Tax revenue buys behavior that markets underproduce:

- basic research,
- public data infrastructure,
- education,
- care,
- disaster protection,
- trustworthy news archives,
- orbital cleanup,
- climate adaptation,
- lunar and station safety.

---

## 18. Insurance

Insurance pools negative Delta risks. A station insures against pressure loss. A media organization insures against reporting errors. A farmer insures against crop failure. A satellite operator insures collision risk.

The premium is:

\[
Premium=\mathbb{E}[negative\;\Delta]+capital\;buffer+verification\;cost+systemic\;risk
\]

Insurance has a positive effect: it rewards prevention. Actors who demonstrably reduce risks pay less.

---

## 19. Education and Culture

Education creates future positive Delta capacity. Culture creates meaning, cooperation, identity, critical ability, and psychological stability. The model must not evaluate culture only by market clicks.

A cultural contribution can have positive Delta when it:

- preserves knowledge,
- builds community,
- enables criticism,
- processes trauma,
- increases creativity,
- strengthens psychological health,
- enables dialogue between groups.

But art must not become mere norm compliance. Therefore, culture needs an autonomy zone where experiments are protected even when their usefulness appears only later.

---

## 20. Numerical Examples

### 20.1 Space Station Maintenance

A technician repairs a CO₂ filter system.

- Plus norm: safety, life protection, error reduction, documentation = 13.0
- Minus norm: material use, work risk, downtime = 2.0
- \(\lambda_{station}=20\)

\[
\mu=20(13-2)=220\Delta
\]

The technician or team receives 220 Delta. Part can be paid by the station, part can be created by ZEMO as system-stability money.

### 20.2 Manipulative Mass News

A media organization publishes a widely distributed misleading headline.

- Plus norm: public relevance and timeliness = 1.0
- Minus norm: deception, harm, correction delay, attention abuse = 9.0
- \(\lambda_{news}=10\)

\[
\mu=10(1-9)=-80\Delta
\]

The media organization must pay 80 Delta or partly offset it through corrective behavior.

### 20.3 Good Local Warning

A small newsroom reports a drinking-water issue in time, with sources and practical guidance.

- Plus norm: relevance, accuracy, prevention, correction structure = 8.4
- Minus norm: uncertainty, attention cost = 1.2
- \(\lambda_{news}=10\)

\[
\mu=10(8.4-1.2)=72\Delta
\]

The newsroom earns 72 Delta, even if its reach is smaller than major media.

### 20.4 Food

A meal has high nutritional value, low waste, and moderate transportation burden.

- Plus norm: nutrition, health, local resilience = 4.0
- Minus norm: energy, packaging, transport = 2.7
- \(\lambda_{food}=5\)

\[
\mu=5(4.0-2.7)=6.5\Delta
\]

The supply chain may receive positive Delta. The buyer still pays a price because labor, materials, and coordination must be compensated. The positive norm spread can reduce that price.

---

## 21. Abuse and Countermeasures

### 21.1 Norm Gaming

Actors may try to optimize only the measured coordinates. Countermeasures:

- random audits,
- robust indicators,
- measurement rotation,
- qualitative review,
- whistleblower rewards,
- later booking of hidden damages.

### 21.2 Behavioral Monopolies

Whoever controls measurement data could control the economy. Countermeasures:

- open standards,
- independent oracles,
- data portability,
- separation of measurement and payment,
- public reference models.

### 21.3 Political Repression

The greatest danger is a government or central bank using norms to punish opposition. Countermeasures:

- ban on belief coordinates,
- protection of political opinion,
- independent rights chamber,
- media pluralism,
- international and orbital veto rights,
- public norm history,
- judicial review.

### 21.4 The Poor Become Permanently Negative

If negative Delta is too harsh, people become trapped. Countermeasures:

- basic access account,
- debt discharge after restoration,
- access to education and work,
- no interest on existential negative accounts,
- restorative rather than purely punitive logic.

---

## 22. Implementation Phases

### Phase 1: Voluntary Pilot Markets

Start in areas where behavior is measurable and socially useful:

- recycling,
- energy savings,
- local news quality,
- care work,
- open-source security work,
- station and satellite safety.

### Phase 2: Public Delta Contracts

Municipalities, stations, and research institutions buy concrete behavioral services with Delta.

### Phase 3: Partial Currency

Delta is used alongside existing currencies. Prices are displayed in both systems.

### Phase 4: Earth-Moon-Orbit Settlement

Satellites, space stations, and lunar habitats use Delta as the primary unit of account for safety, logistics, energy, water, news, and maintenance.

### Phase 5: Full Economy With Constitution

Only after stable experience, democratic legitimacy, and strong basic rights does Delta become the dominant currency.

---

## 23. Philosophical Core

This system makes visible what already happens in every economy: people pay each other to change behavior. A wage changes labor behavior. A price changes consumption behavior. Advertising changes attention behavior. News changes expectation behavior. Credit changes future behavior. Taxes change resource behavior.

The difference is that the Delta system says openly what is being evaluated and forces the evaluation into transparent mathematical forms.

That is its strength and its danger.

Its strength: hidden costs become visible. Media behavior becomes more accountable. Orbital and lunar risks are priced correctly. Public goods can be paid for directly.

Its danger: if built badly, it becomes a machine for social control.

Therefore, the most important formula is not only:

\[
\mu(e)=\lambda(\|e\|_+-\|e\|_-)
\]

but also:

> No Delta without rights. No norm without appeal. No media evaluation without pluralism. No behavioral economy without privacy. No central bank without separation of powers.

---

## 24. Minimal Constitution of the Delta System

1. **Human dignity is not for sale.** Delta evaluates actions, not the worth of a person.
2. **No universal social score.** There are domain-specific proofs, not one total citizen number.
3. **Basic access is guaranteed.** Food, water, air, emergency medicine, basic communication, and protection from acute danger do not depend on account balance.
4. **Political opinion is protected.** Verifiable harm and breach of contract may be evaluated, not belief.
5. **Media pluralism is mandatory.** Truth processes are evaluated, not permitted ideologies.
6. **Every norm is public.** Weights, formulas, data sources, and changes are traceable.
7. **Every relevant entry is appealable.** Automation does not replace rights.
8. **Data minimization always applies.** No raw data when proof is enough.
9. **Norms change slowly.** Money must not be destroyed by sudden scoring shifts.
10. **ZEMO is separated.** Monetary policy, norm setting, data verification, and rights review are divided.

---

## 25. Compact Definition

The Delta-Norm Economy is an economic order in which every economically relevant action is represented as a vector in a domain-specific behavioral space. Two mathematical norms measure the contribution and burden of that action. The difference between the two norm values, scaled by monetary policy factors, creates a positive or negative Delta amount. This amount functions as currency, price, wage, tax base, credit foundation, insurance measure, and steering signal. A central bank for Earth, Moon, satellites, and space stations stabilizes the currency, while a norm constitution prevents behavioral money from turning into a totalitarian control system.

---

# Anhang / Appendix: Symboltabelle / Symbol Table

| Symbol | Deutsch | English |
|---|---|---|
| \(A\) | Menge der Akteure | Set of actors |
| \(e\) | Verhaltensereignis | Behavioral event |
| \(d\) | Domäne | Domain |
| \(\Phi_d(e)\) | Vektorisierung des Ereignisses | Vectorization of the event |
| \(\|\cdot\|_{+,d}\) | Beitragsnorm | Contribution norm |
| \(\|\cdot\|_{-,d}\) | Belastungsnorm | Burden norm |
| \(\lambda_d\) | geldpolitischer Umrechnungsfaktor | monetary conversion factor |
| \(\mu(e)\) | Delta-Wert eines Ereignisses | Delta value of an event |
| \(B_a(t)\) | Kontostand eines Akteurs | Balance of an actor |
| ZEMO | Zentralbank des Erde-Mond-Orbit-Systems | Central Bank of the Earth-Moon-Orbit System |
| \(\rho_e\) | Verifikationsfaktor | Verification factor |
| \(\sigma_e\) | Haftungs-/Belastungsfaktor | Liability/burden factor |

---

# Letzter Satz / Final Sentence

**Deutsch:** Dieses Wirtschaftssystem macht Geld zu einer messbaren, handelbaren Differenz zwischen nützlichem und belastendem Verhalten, aber es kann nur legitim sein, wenn Rechte, Privatsphäre, pluralistische Medien und demokratische Normsetzung stärker sind als die reine Rechenmaschine.  

**English:** This economy turns money into a measurable, tradable difference between useful and burdensome behavior, but it can be legitimate only if rights, privacy, pluralistic media, and democratic norm-setting are stronger than the calculation machine itself.
