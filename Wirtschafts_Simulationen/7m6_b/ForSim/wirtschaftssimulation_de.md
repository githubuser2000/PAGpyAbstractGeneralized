# Komplette Wirtschaftssimulation der Zahlen-Winkel-Währungen

Zu einer **kompletten Wirtschaftssimulation auf Grundlage deiner Zahlen-Winkel-Währungen** gehören nicht nur Länder, Regierungen, Völker, Märkte und Firmen. Das sind nur die sichtbaren Akteure. Entscheidend sind zusätzlich: **Bilanzen, Regeln, Informationsflüsse, Unsicherheit, Machtmissbrauch, Kredit, Eigentum, Zeit und Sanktionen**.

Der Kern wäre:

\[
\text{Wirtschaft} = \text{Akteure} + \text{Märkte} + \text{Bilanzen} + \text{Regeln} + \text{Erwartungen} + \text{Schocks}
\]

und deine Währung ist nicht nur:

\[
m
\]

sondern:

\[
M = (m,\theta,\rho,h)
\]

mit:

\[
m = \text{Zahlenbetrag}
\]

\[
\theta = \text{Winkelrichtung: gut/böse + beliebt/unbeliebt}
\]

\[
\rho = \text{Sicherheit / Konfidenz des Winkels}
\]

\[
h = \text{Herkunftsgeschichte / Transaktionshistorie}
\]

Ohne \(\rho\) und \(h\) wird das System naiv, weil dann jeder so tun könnte, als sei sein Winkel objektiv und sauber.

---

## 1. Länder und Jurisdiktionen

Du brauchst mehrere Länder, aber nicht nur als Namen. Jedes Land braucht eigene Institutionen:

\[
L_i = (\text{Regierung}, \text{Volk}, \text{Gerichte}, \text{Zentralbank}, \text{Steuersystem}, \text{Regulierer})
\]

Jedes Land kann eigene Definitionen haben für:

\[
\text{gut/böse}
\]

\[
\text{legal/illegal}
\]

\[
\text{subventioniert/bestraft}
\]

\[
\text{anerkannt/nicht anerkannt}
\]

Das ist wichtig, weil ein Objekt in Land A gut und in Land B böse sein kann.

Beispiel:

\[
\theta_A = 30^\circ
\]

\[
\theta_B = 150^\circ
\]

Dann entsteht internationaler Winkelkonflikt. Genau daraus entstehen Handelsspannungen, Sanktionen, Arbitrage, Schwarzmarkt und diplomatische Machtspiele.

---

## 2. Regierungen als Gut/Böse-Orakel

Mehrere Regierungen legen die Achse **gut vs. böse** fest. Aber sie dürfen in der Simulation nicht als perfekte Wahrheitsmaschinen auftreten.

Jede Regierung braucht Eigenschaften:

\[
G_i = (\text{Kompetenz}, \text{Korruption}, \text{Ideologie}, \text{Interessen}, \text{Informationsqualität}, \text{Macht})
\]

Dann bewertet sie Firmen, Produkte, Branchen, Handlungen und Geldflüsse.

Zum Beispiel:

\[
g_i(x) \in [-1,1]
\]

mit:

\[
-1 = \text{maximal böse}
\]

\[
+1 = \text{maximal gut}
\]

Dazu gehört immer eine Unsicherheit:

\[
\sigma_i(x)
\]

Eine Regierung kann also sagen:

\[
g_i(\text{Firma A}) = 0{,}7 \pm 0{,}2
\]

Das bedeutet: Sie hält Firma A für eher gut, aber nicht mit absoluter Sicherheit.

Wichtig sind außerdem:

- internationale Regierungskoalitionen
- Vetorechte
- Sanktionen
- Korruptionsrisiko
- politische Fehleinschätzungen
- Propaganda
- Lobbyismus
- gerichtliche Korrekturen
- Regierungswechsel
- Revolutionen oder Putsche
- Notstandsrechte

Ohne diese Faktoren wird deine Gut/Böse-Achse zu glatt.

---

## 3. Völker als Beliebt/Unbeliebt-Orakel

Mehrere Völker legen die Achse **beliebt vs. unbeliebt** fest.

Aber auch Völker sind nicht homogen. Ein Volk besteht aus Gruppen:

\[
V_i = \{v_{i1}, v_{i2}, v_{i3}, ...\}
\]

Zum Beispiel:

- Arbeiter
- Unternehmer
- Rentner
- Studenten
- religiöse Gruppen
- Stadtbevölkerung
- Landbevölkerung
- Minderheiten
- politische Lager
- Medienmilieus
- Konsumentenklassen

Jede Gruppe hat eigene Präferenzen:

\[
p_{ij}(x) \in [-1,1]
\]

mit:

\[
-1 = \text{maximal unbeliebt}
\]

\[
+1 = \text{maximal beliebt}
\]

Die Gesamtbeliebtheit wäre dann etwa:

\[
p_i(x)=\sum_j w_{ij}p_{ij}(x)
\]

Aber auch hier brauchst du Unsicherheit und Manipulation:

- Umfragen
- Wahlen
- Referenden
- Streiks
- Boykotte
- Proteste
- Social Media
- Medienkampagnen
- Zensur
- Desinformation
- kollektive Hysterie
- langsame kulturelle Verschiebungen
- kurzfristige Trends

Die Beliebtheitsachse ist nicht Wahrheit. Sie ist Resonanz, Zustimmung, Abneigung und soziale Energie.

---

## 4. Aggregation zum Winkel

Aus Regierungsgutartigkeit und Volksbeliebtheit entsteht der Winkel.

Eine einfache Variante:

\[
x = \text{Gutartigkeit}
\]

\[
y = \text{Beliebtheit}
\]

Dann:

\[
\theta = \operatorname{atan2}(y,x)
\]

Der Betrag der normativen Kraft:

\[
r_\theta = \sqrt{x^2+y^2}
\]

Die Sicherheit:

\[
\rho = \text{Einigkeit der Regierungen und Völker}
\]

Wenn Regierungen und Völker stark übereinstimmen, ist \(\rho\) hoch. Wenn sie sich widersprechen, ist \(\rho\) niedrig.

Beispiel:

\[
x = 0{,}8,\quad y = 0{,}7
\]

heißt: gut und beliebt.

\[
x = 0{,}8,\quad y = -0{,}6
\]

heißt: gut, aber unbeliebt.

\[
x = -0{,}7,\quad y = 0{,}9
\]

heißt: böse, aber beliebt.

Gerade der dritte Fall ist politisch explosiv. Eine Simulation muss solche Fälle erzeugen können.

---

## 5. Die Währung selbst

Jede Geldeinheit braucht mehrere Eigenschaften:

\[
M = (m,\theta,\rho,o,t,h)
\]

mit:

\[
m = \text{Zahlenbetrag}
\]

\[
\theta = \text{Winkel}
\]

\[
\rho = \text{Konfidenz}
\]

\[
o = \text{Ursprung}
\]

\[
t = \text{Zeitpunkt}
\]

\[
h = \text{Historie}
\]

Die Historie ist wichtig. Sonst entsteht sofort Winkelwäsche.

Beispiel:

Eine Firma verdient Geld durch Ausbeutung:

\[
1000 \angle 160^\circ
\]

Dann spendet sie 10 % davon an eine beliebte Sache und versucht, alles als gut erscheinen zu lassen. Ohne Historie könnte sie den Winkel manipulieren. Mit Historie bleibt sichtbar:

\[
\text{Herkunft: toxisch}
\]

\[
\text{Nachträgliche Verbesserung: teilweise}
\]

Also braucht die Simulation eine Art **Vektor-Buchhaltung mit Herkunftsspur**.

---

## 6. Winkel-Buchhaltung

Normale Buchhaltung reicht nicht. Firmen, Banken und Staaten brauchen Bilanzen mit Vektoren.

Normale Bilanz:

\[
\text{Aktiva} = \text{Passiva} + \text{Eigenkapital}
\]

Vektorbilanz:

\[
\vec{A} = \vec{L} + \vec{E}
\]

Aber das ist nicht trivial, weil sich entgegengesetzte Winkel teilweise auslöschen können.

Eine Firma könnte numerisch reich, aber normativ toxisch sein:

\[
\text{Zahlenvermögen hoch}
\]

\[
\text{Winkel schlecht}
\]

Oder sie könnte beliebt und gut sein, aber kaum Liquidität haben.

Deshalb brauchst du getrennte Kennzahlen:

\[
\text{Liquidität}
\]

\[
\text{Solvenz}
\]

\[
\text{Winkelqualität}
\]

\[
\text{Winkelrisiko}
\]

\[
\text{Reputationskapital}
\]

\[
\text{politisches Risiko}
\]

---

## 7. Haushalte und Individuen

Die fehlen in deiner Liste noch deutlich. Ohne Haushalte gibt es keine echte Nachfrage, keine Arbeit, keine Wahlen, keine Konsumentenpsychologie.

Jeder Mensch oder Haushalt braucht:

\[
H_i = (\text{Einkommen}, \text{Vermögen}, \text{Bedürfnisse}, \text{Werte}, \text{Beruf}, \text{Bildung}, \text{politische Meinung})
\]

Haushalte entscheiden:

- was sie kaufen
- wo sie arbeiten
- wen sie wählen
- welche Firmen sie boykottieren
- welche Winkel sie akzeptieren
- wie viel Risiko sie tragen
- ob sie sparen, konsumieren oder investieren

Jeder Haushalt hat also auch eigene Winkelpräferenzen:

\[
\theta_i^K = \text{Kaufwinkel}
\]

\[
\theta_i^V = \text{Verkaufswinkel}
\]

Beim Kaufen fragt er:

„Akzeptiere ich dieses Produkt zu diesem Preis und diesem Winkel?“

Beim Arbeiten fragt er:

„Akzeptiere ich Lohn von dieser Firma mit dieser Winkelqualität?“

Das ist stark, weil Arbeit dann nicht nur Lohn gegen Zeit ist, sondern auch moralische Kompatibilität.

---

## 8. Firmen, Konzerne und Eigentümerstrukturen

Firmen brauchst du nicht nur als Produzenten. Sie haben innere Struktur:

\[
F_i = (\text{Kapital}, \text{Arbeitskräfte}, \text{Technologie}, \text{Lieferketten}, \text{Management}, \text{Eigentümer}, \text{Schulden})
\]

Wichtig sind:

- kleine Firmen
- mittelständische Firmen
- Konzerne
- Monopole
- Kartelle
- Plattformunternehmen
- Banken
- Versicherungen
- Logistikunternehmen
- Rüstungsunternehmen
- Medienunternehmen
- Energiekonzerne
- Rohstofffirmen
- Technologieunternehmen
- Schattenfirmen
- Briefkastenfirmen

Konzerne brauchen zusätzlich:

\[
\text{Tochtergesellschaften}
\]

\[
\text{Holdingstruktur}
\]

\[
\text{Steuervermeidung}
\]

\[
\text{Jurisdiktionsarbitrage}
\]

\[
\text{Lobbying}
\]

\[
\text{Marktmacht}
\]

Gerade Konzerne sind in deiner Simulation interessant, weil sie Winkel verschieben können: durch Werbung, Lobbyismus, Arbeitsplatzmacht, Spenden, Medienkontrolle und internationale Standortwahl.

---

## 9. Produkte, Dienstleistungen und Güterklassen

Jedes Gut braucht nicht nur Preis und Menge, sondern auch Winkelprofil.

\[
X = (\text{Preis}, \text{Qualität}, \text{Menge}, \text{Nutzen}, \text{Produktionswinkel}, \text{Konsumwinkel})
\]

Produkte können gut produziert, aber schlecht genutzt werden. Oder schlecht produziert, aber beliebt konsumiert werden.

Beispiel:

Ein billiges Produkt kann sehr beliebt sein, aber eine schlechte Produktionsgeschichte haben.

\[
\text{Beliebtheit hoch}
\]

\[
\text{Gutartigkeit niedrig}
\]

Also braucht jedes Produkt mindestens:

- Gebrauchswert
- Marktpreis
- Produktionskosten
- Lieferkettenwinkel
- Konsumwinkel
- Umweltwirkung
- Sozialwirkung
- Legalitätsstatus
- Haltbarkeit
- Substituierbarkeit

Güterklassen:

- Nahrung
- Energie
- Wohnen
- Kleidung
- Gesundheit
- Bildung
- Transport
- Unterhaltung
- Luxusgüter
- Waffen / Sicherheitsgüter
- Daten
- Software
- Rohstoffe
- Maschinen
- Infrastruktur
- Finanzprodukte

---

## 10. Arbeitsmarkt

Der Arbeitsmarkt ist nicht nur ein weiterer Markt. Er verbindet Geld, Würde, Macht, Zeit und Politik.

Jeder Arbeitsplatz hat:

\[
Job = (\text{Lohn}, \text{Arbeitszeit}, \text{Risiko}, \text{Status}, \text{Winkel der Firma}, \text{Winkel der Tätigkeit})
\]

Menschen akzeptieren Jobs nicht nur nach Lohn, sondern auch nach:

- moralischer Verträglichkeit
- Popularität des Arbeitgebers
- Karrierechancen
- Arbeitsplatzsicherheit
- sozialem Status
- politischem Risiko
- familiärem Druck
- Qualifikation
- geografischer Lage

Dann kann es Phänomene geben wie:

\[
\text{hoher Lohn, schlechter Winkel}
\]

oder:

\[
\text{niedriger Lohn, guter Winkel}
\]

Das ist realistisch. Viele Menschen verkaufen nicht nur Arbeit, sondern auch einen Teil ihrer gesellschaftlichen Identität.

---

## 11. Finanzsystem

Das ist einer der wichtigsten fehlenden Blöcke.

Du brauchst:

- Banken
- Zentralbanken
- Kreditmärkte
- Anleihen
- Aktienmärkte
- Versicherungen
- Investmentfonds
- Pensionsfonds
- Schattenbanken
- Börsen
- Market Maker
- Ratingagenturen
- Zahlungsnetzwerke

In deinem Modell gibt es nicht nur Zinsen, sondern auch Winkelzinsen.

Ein Kredit wäre:

\[
K = (m,\theta,\rho,i,T)
\]

mit:

\[
i = \text{Zins}
\]

\[
T = \text{Laufzeit}
\]

Der Zinssatz hängt dann ab von:

\[
\text{Ausfallrisiko}
\]

\[
\text{Winkelrisiko}
\]

\[
\text{politischem Risiko}
\]

\[
\text{Beliebtheitsrisiko}
\]

\[
\text{Liquiditätsrisiko}
\]

Eine Firma mit schlechtem Winkel muss höhere Zinsen zahlen oder findet nur noch toxische Finanzierung.

---

## 12. Zentralbanken und Geldschöpfung

Jede Währung braucht eine Emissionsregel.

In deinem System muss eine Zentralbank nicht nur Menge steuern:

\[
M
\]

sondern auch Winkelqualität im Umlauf:

\[
\Theta
\]

Eine Zentralbank könnte also beobachten:

\[
\text{Inflation}
\]

\[
\text{Arbeitslosigkeit}
\]

\[
\text{Winkelverteilung des Geldes}
\]

\[
\text{Liquidität je Winkelzone}
\]

\[
\text{Vertrauenskrisen}
\]

\[
\text{Winkelpaniken}
\]

Neue Begriffe wären möglich:

### Zahleninflation

Normale Preissteigerung.

### Winkelinflation

Alle behaupten, gut zu sein, aber die Konfidenz sinkt.

\[
\rho \downarrow
\]

### Winkeldeflation

Nur noch extrem „sauberes“ Geld wird akzeptiert; Handel friert ein.

### Winkelpanik

Akteure fliehen aus einem Winkelbereich, weil dieser plötzlich als böse oder unbeliebt gilt.

---

## 13. Winkelmärkte

Das ist spezifisch für deine Idee.

Neben normalen Märkten brauchst du Märkte für Winkel selbst:

- Winkeltausch
- Winkelabsicherung
- Winkeloptionen
- Winkel-Futures
- Reputationsderivate
- Gutartigkeitsswaps
- Beliebtheitsswaps
- Sanktionsversicherungen
- Boykottversicherungen
- politische Risikoabsicherung

Ein einfacher Winkeltausch:

\[
m \angle \theta_1 \rightarrow m' \angle \theta_2
\]

mit:

\[
m' = m \cdot q(d)
\]

und:

\[
d = d(\theta_1,\theta_2)
\]

Je größer die Winkeldistanz, desto teurer die Umwandlung.

Das erzeugt eine neue Branche: **Winkel-Market-Maker**.

Diese kaufen schwierige Winkel und verkaufen akzeptablere Winkel. Aber das ist gefährlich, weil daraus moralische Geldwäsche entstehen kann.

Deshalb brauchst du:

- Prüfstellen
- Audits
- Herkunftsnachweise
- Reputationsstrafen
- Betrugsdetektion
- Transparenzregeln
- Verjährungsregeln
- Einspruchsverfahren

---

## 14. Eigentum, Verträge und Gerichte

Ohne Rechtssystem gibt es keine stabile Wirtschaft.

Du brauchst:

\[
\text{Eigentumsrechte}
\]

\[
\text{Vertragsrecht}
\]

\[
\text{Haftung}
\]

\[
\text{Insolvenzrecht}
\]

\[
\text{Arbeitsrecht}
\]

\[
\text{Kartellrecht}
\]

\[
\text{Steuerrecht}
\]

\[
\text{Datenschutzrecht}
\]

\[
\text{Sanktionsrecht}
\]

Bei deiner Währung kommt ein neues Rechtsproblem hinzu:

**Wer darf einen Winkel verändern?**

Darf ein Gericht sagen:

\[
\theta = 140^\circ \rightarrow 80^\circ
\]

weil eine Firma rehabilitiert wurde?

Darf eine Regierung sagen:

\[
\theta = 40^\circ \rightarrow 170^\circ
\]

weil eine Organisation verboten wurde?

Darf ein Volk durch Boykott einen Winkel verschlechtern?

Diese Fragen müssen als Regeln in die Simulation.

---

## 15. Steuern und Staatsausgaben

Staaten müssen Einnahmen und Ausgaben haben.

Steuern können in deinem Modell winkelabhängig sein:

\[
Tax = f(m,\theta,\rho)
\]

Zum Beispiel:

- gutes und beliebtes Geld wird niedriger besteuert
- böses Geld wird höher besteuert
- unsicheres Geld wird geprüft
- toxisches Geld wird eingefroren
- staatlich erwünschte Investitionen werden subventioniert

Staatsausgaben haben ebenfalls Winkel:

- Sozialausgaben
- Militär
- Infrastruktur
- Bildung
- Gesundheit
- Subventionen
- Rettungspakete
- Polizeiapparat
- Propaganda
- Forschung

Eine Regierung kann also nicht nur Geld ausgeben, sondern Winkel erzeugen oder zerstören.

---

## 16. Internationale Wirtschaft

Sobald mehrere Länder existieren, brauchst du:

- Wechselkurse
- Kapitalflüsse
- Handelsabkommen
- Zölle
- Sanktionen
- Embargos
- Migration
- multinationale Konzerne
- Steuerparadiese
- Entwicklungshilfe
- geopolitische Blöcke
- Reservewährungen
- Rohstoffabhängigkeiten
- Lieferketten über Grenzen

In deinem Modell kommt dazu:

\[
\text{Winkelübersetzung}
\]

Ein Winkel in Land A ist nicht automatisch derselbe in Land B.

Du brauchst also eine Transformationsmatrix:

\[
\theta_B = T_{A \rightarrow B}(\theta_A)
\]

Beispiel:

Ein Produkt gilt in Land A als gut und beliebt. In Land B gilt es als unmoralisch, aber trotzdem begehrt.

Das erzeugt Arbitrage:

\[
\text{kaufen in gutem Winkelraum}
\]

\[
\text{verkaufen in beliebtem Winkelraum}
\]

---

## 17. Medien und Informationssystem

Das ist absolut zentral. Winkel entstehen nicht nur durch Tatsachen, sondern durch Wahrnehmung.

Du brauchst:

- Nachrichtenmedien
- soziale Netzwerke
- Influencer
- staatliche Medien
- investigative Journalisten
- Plattformalgorithmen
- Zensur
- Leaks
- Whistleblower
- Propaganda
- Skandale
- Gerüchte
- Gegenöffentlichkeiten

Ein Skandal kann den Winkel einer Firma abrupt ändern:

\[
\theta_t = 30^\circ
\]

\[
\theta_{t+1} = 150^\circ
\]

Das ist ein Winkelcrash.

Eine erfolgreiche PR-Kampagne kann Beliebtheit erhöhen, ohne Gutartigkeit zu erhöhen:

\[
y \uparrow,\quad x = \text{gleich}
\]

Das ist eine realistische und gefährliche Dynamik.

---

## 18. Bildung, Kultur und Ideologie

Völker bewerten nicht im luftleeren Raum. Ihre Beliebtheitsskala hängt von Kultur ab.

Du brauchst:

- Bildungssysteme
- Religionen
- politische Ideologien
- historische Traumata
- Nationalmythen
- Klassenbewusstsein
- moralische Tabus
- Generationenkonflikte
- Wertewandel

Sonst reagieren alle Völker gleich. Das wäre langweilig und falsch.

Ein konservatives Volk, ein technokratisches Volk, ein egalitäres Volk und ein konsumorientiertes Volk bewerten dieselbe Firma verschieden.

---

## 19. Lieferketten und Herkunft

Das ist bei Winkelgeld extrem wichtig.

Ein Produkt hat nicht nur einen Verkäuferwinkel, sondern eine ganze Herkunftskette:

\[
\theta_{\text{Produkt}} =
F(\theta_{\text{Rohstoffe}},\theta_{\text{Arbeit}},\theta_{\text{Transport}},\theta_{\text{Firma}},\theta_{\text{Energie}})
\]

Beispiel:

Ein Smartphone hat Winkelanteile aus:

- Rohstoffabbau
- Arbeitsbedingungen
- Energieverbrauch
- Patenten
- Datenpolitik
- Marketing
- Reparierbarkeit
- geopolitischer Herkunft
- Konsumentennutzen

Der Endwinkel ist also eine gewichtete Mischung.

Ohne Lieferkettenmodell ist Winkelgeld leicht manipulierbar.

---

## 20. Umwelt und externe Effekte

Eine vollständige Simulation braucht externe Effekte:

- CO₂
- Wasserverbrauch
- Artensterben
- Luftverschmutzung
- Gesundheitskosten
- Lärm
- Müll
- Ressourcenerschöpfung
- Flächenverbrauch
- soziale Schäden
- Kriminalität
- öffentliche Sicherheit

Diese Effekte beeinflussen die Gut/Böse-Achse.

Ein Produkt kann profitabel und beliebt sein, aber langfristig schädlich. Dann entsteht:

\[
x < 0,\quad y > 0
\]

also: böse, aber beliebt.

Das ist einer der wichtigsten Fälle deines Modells.

---

## 21. Innovation und Technologie

Wirtschaft verändert sich durch Technologie.

Du brauchst:

- Forschung und Entwicklung
- Patente
- Automatisierung
- Produktivitätswachstum
- KI-Systeme
- Plattformeffekte
- Netzwerkeffekte
- Monopolisierung
- kreative Zerstörung
- neue Branchen
- veraltete Branchen

Technologie kann Winkel verschieben.

Eine neue Technologie kann zuerst unbeliebt sein, aber später als gut gelten:

\[
(+,-) \rightarrow (+,+)
\]

Oder zuerst beliebt und später als schädlich erkannt werden:

\[
(-,+) \rightarrow (-,-)
\]

---

## 22. Kriminalität, Betrug und Schattenwirtschaft

Das darfst du nicht weglassen. Ein System mit moralisch-sozialer Währung erzeugt sofort neue Betrugsformen.

Du brauchst:

- Geldwäsche
- Winkelwäsche
- Bestechung
- Fake-Beliebtheit
- Bot-Netzwerke
- Scheinfirmen
- Strohmänner
- gefälschte Lieferketten
- manipulierte Audits
- Insiderhandel
- Marktmanipulation
- Kartelle
- Schmuggel
- Schwarzarbeit
- Sanktionsumgehung
- politische Erpressung

Neue spezifische Straftat:

\[
\text{Winkelmanipulation}
\]

Zum Beispiel: Eine Firma kauft künstlich Beliebtheit, damit ihr Geld einen besseren Winkel bekommt.

Oder: Eine Regierung erklärt Gegner als böse, um deren Vermögen zu entwerten.

Ohne adversarisches Modell wird die Simulation moralisch naiv.

---

## 23. Militär, Sicherheit und Zwang

Staaten bestehen nicht nur aus Regeln, sondern auch aus Durchsetzung.

Du brauchst:

- Polizei
- Geheimdienste
- Militär
- Grenzschutz
- Sanktionseinheiten
- Cyberabwehr
- Gerichte
- Gefängnisse
- Notstandsapparate

Warum? Weil Währungen nur funktionieren, wenn Ansprüche durchsetzbar sind.

In deinem System können Staaten Winkel auch als Waffe benutzen:

\[
\text{Feindliche Firma} \rightarrow \theta = \text{böse/unbeliebt}
\]

\[
\text{Sanktioniertes Land} \rightarrow \text{Winkelblockade}
\]

Das ist geopolitisch enorm wichtig.

---

## 24. Zeit, Erwartungen und Gedächtnis

Eine Wirtschaftssimulation braucht Zeit.

Nicht alles passiert sofort. Es gibt:

- Produktionszeiten
- Lieferverzögerungen
- Vertragslaufzeiten
- Kreditlaufzeiten
- Wahlzyklen
- Investitionszyklen
- Reputationsverzögerungen
- Informationsverzögerungen
- Gerichtsverfahren
- politische Trägheit

Der Winkel sollte auch Gedächtnis haben:

\[
\theta_t = \alpha \theta_{\text{neu}} + (1-\alpha)\theta_{t-1}
\]

Sonst würde jeder Skandal sofort alles zerstören und jede PR-Kampagne sofort alles retten.

Du brauchst also Trägheit:

\[
\alpha = \text{Reaktionsgeschwindigkeit}
\]

Ein hohes \(\alpha\): Gesellschaft reagiert schnell.  
Ein niedriges \(\alpha\): Gesellschaft vergisst langsam und urteilt stabiler.

---

## 25. Schocks und Krisen

Eine gute Simulation braucht Störungen.

Mögliche Schocks:

- Finanzkrise
- Bank Run
- Krieg
- Pandemie
- Naturkatastrophe
- Energieschock
- Lieferkettenbruch
- Korruptionsskandal
- Leak
- Wahlumsturz
- Revolution
- Hyperinflation
- Währungsflucht
- Boykottwelle
- Technologiebruch
- Cyberangriff
- Staatsbankrott
- Konzernpleite

Bei deinem System zusätzlich:

- Winkelcrash
- Vertrauenscrash
- Gut/Böse-Neubewertung
- Beliebtheitswelle
- moralische Panik
- internationale Winkelspaltung
- Orakel-Korruption
- Massenboykott
- Reputationsbankrott

---

## 26. Märkte im Detail

Du hast Produkte, Dienstleistungen und Arbeitsmarkt genannt. Dazu kommen:

### Gütermärkte

Nahrung, Energie, Rohstoffe, Konsumgüter.

### Dienstleistungsmärkte

Gesundheit, Bildung, Beratung, Pflege, Unterhaltung.

### Arbeitsmärkte

Löhne, Qualifikationen, Migration, Arbeitslosigkeit.

### Kapitalmärkte

Aktien, Anleihen, Kredite, Beteiligungen.

### Immobilienmärkte

Wohnraum, Land, Gewerbeimmobilien.

### Rohstoffmärkte

Öl, Gas, Metalle, Wasser, seltene Erden.

### Energiemärkte

Strom, Speicher, Netze, Erzeugung.

### Datenmärkte

Nutzerdaten, Trainingsdaten, Überwachung, Privatsphäre.

### Technologiemärkte

Software, KI, Patente, Rechenleistung.

### Versicherungsmärkte

Risikoabsicherung, Katastrophen, Krankheit, politische Risiken.

### Winkelmärkte

Rotation, Absicherung, Konfidenz, Reputation.

### Schwarz- und Graumärkte

Alles, was offiziell blockiert, aber weiter nachgefragt wird.

---

## 27. Preisbildung

Jeder Handel braucht mindestens:

\[
(\text{Menge}, \text{Zahlenpreis}, \text{Kaufwinkel}, \text{Verkaufswinkel}, \text{Konfidenz}, \text{Jurisdiktion})
\]

Ein Kaufangebot:

\[
Bid = (p_B, q_B, \theta_B^K, r_B)
\]

Ein Verkaufsangebot:

\[
Ask = (p_A, q_A, \theta_A^V, r_A)
\]

Handel findet statt, wenn:

\[
p_B \geq p_A
\]

und:

\[
d(\theta_B^K,\theta_A^V) \leq \varepsilon
\]

Oder wenn die Winkeldistanz über eine Gebühr ausgeglichen wird:

\[
C = \lambda m \tan^2\left(\frac{d}{2}\right)
\]

Dann wird der effektive Handelswert:

\[
m_{\text{eff}} = m \cdot q(d,\rho)
\]

mit beispielsweise:

\[
q(d,\rho)=\rho \cos\left(\frac{d}{2}\right)
\]

Das heißt: Gleicher Winkel und hohe Sicherheit geben volle Kaufkraft. Großer Winkelabstand oder geringe Sicherheit reduziert die effektive Kaufkraft.

---

## 28. Nutzenfunktionen der Akteure

Jeder Akteur braucht Entscheidungsregeln.

Ein Haushalt maximiert nicht nur Konsum:

\[
U = f(\text{Konsum}, \text{Preis}, \text{Winkel}, \text{Status}, \text{Risiko}, \text{Werte})
\]

Eine Firma maximiert nicht nur Gewinn:

\[
\Pi = \text{Gewinn} - \text{Winkelkosten} - \text{Regulierungsrisiko} - \text{Reputationsrisiko}
\]

Eine Regierung maximiert vielleicht:

\[
G = f(\text{Stabilität}, \text{Macht}, \text{Wohlstand}, \text{Ideologie}, \text{Sicherheit})
\]

Ein Volk oder eine Gruppe maximiert vielleicht:

\[
V = f(\text{Lebensstandard}, \text{Identität}, \text{Gerechtigkeit}, \text{Sicherheit}, \text{Status})
\]

Das ist wichtig: Nicht alle Akteure verfolgen dasselbe Ziel.

---

## 29. Macht und Ungleichheit

Eine vollständige Simulation braucht Machtverhältnisse.

Nicht jeder Akteur hat gleiche Wirkung auf Winkel.

Ein großer Konzern kann durch Werbung Beliebtheit beeinflussen.  
Eine Regierung kann durch Gesetz Gutartigkeit definieren.  
Eine Plattform kann Sichtbarkeit kontrollieren.  
Eine Bank kann Finanzierung entziehen.  
Ein reiches Individuum kann Medien kaufen.

Also brauchst du:

\[
\text{Vermögensverteilung}
\]

\[
\text{Marktmacht}
\]

\[
\text{politische Macht}
\]

\[
\text{Medienmacht}
\]

\[
\text{Netzwerkmacht}
\]

\[
\text{Gewaltmacht}
\]

Ohne Machtmodell wirkt die Simulation zu demokratisch und zu harmlos.

---

## 30. Moralische Verfassung des Systems

Das ist der wichtigste politische Schutzmechanismus.

Weil deine Währung Gut/Böse und Beliebt/Unbeliebt einpreist, kann sie leicht totalitär werden. Deshalb brauchst du eine Verfassungsebene:

- Minderheitenschutz
- Grundrechte
- Einspruchsverfahren
- Transparenzpflicht
- Gewaltenteilung
- unabhängige Gerichte
- Schutz vor rückwirkender Entwertung
- Schutz vor Massenhysterie
- Schutz vor Regierungswillkür
- Schutz vor Konzernmanipulation
- Recht auf Rehabilitation
- Recht auf Erklärung
- Recht auf alternative Orakel

Sonst wird aus Winkelgeld schnell ein Gehorsamkeitsgeld.

---

## 31. Messgrößen der Simulation

Du brauchst Ausgaben, damit man beurteilen kann, ob das System funktioniert.

Normale Kennzahlen:

\[
\text{BIP}
\]

\[
\text{Inflation}
\]

\[
\text{Arbeitslosigkeit}
\]

\[
\text{Produktivität}
\]

\[
\text{Löhne}
\]

\[
\text{Vermögensverteilung}
\]

\[
\text{Handelsbilanz}
\]

\[
\text{Staatsverschuldung}
\]

Neue Kennzahlen für dein System:

\[
\text{Winkelverteilung des Geldes}
\]

\[
\text{durchschnittliche Gutartigkeit}
\]

\[
\text{durchschnittliche Beliebtheit}
\]

\[
\text{Winkelvolatilität}
\]

\[
\text{Winkel-Liquidität}
\]

\[
\text{Winkelspread}
\]

\[
\text{Winkelinflation}
\]

\[
\text{Winkelwäsche-Index}
\]

\[
\text{Konfidenzindex}
\]

\[
\text{Legitimitätsindex}
\]

\[
\text{Polarisierungsindex}
\]

\[
\text{Orakel-Vertrauensindex}
\]

\[
\text{Regierungs-Volks-Divergenz}
\]

Besonders wichtig:

\[
D = d(\theta_{\text{Regierung}}, \theta_{\text{Volk}})
\]

Wenn diese Distanz groß wird, entsteht Legitimitätskrise.

---

## 32. Technische Simulationsarchitektur

Für eine ernsthafte Simulation würde ich sie als Hybrid bauen:

### Agentenbasierter Teil

Für Haushalte, Firmen, Banken, Regierungen, Völkergruppen.

### Stock-Flow-Consistent-Teil

Für Bilanzen, Geldflüsse, Kredit, Schulden, Steuern.

### Netzwerkmodell

Für Lieferketten, Eigentum, Medien, Einfluss, Handel.

### Marktmikrostruktur

Für Orderbücher, Preisbildung, Winkelspreads, Liquidität.

### Ereignissystem

Für Schocks, Skandale, Kriege, Krisen, Wahlen.

Formal:

\[
S_t = \text{Gesamtzustand der Welt zu Zeit }t
\]

\[
A_t = \text{Aktionen aller Akteure}
\]

\[
E_t = \text{externe Ereignisse}
\]

\[
S_{t+1} = F(S_t,A_t,E_t)
\]

Das ist die Grundform.

---

## 33. Minimalversion einer ersten Simulation

Für eine erste funktionierende Version würde ich nicht alles sofort bauen. Ich würde mit diesem Kern starten:

- 3 Länder
- 3 Regierungen
- 3 Völker mit je 3 Gruppen
- 1000 Haushalte
- 100 Firmen
- 5 Banken
- 1 Zentralbank pro Land
- 5 Güterklassen
- 1 Arbeitsmarkt
- 1 Kreditmarkt
- 1 Winkelmarkt
- 1 internationaler Handelsmarkt
- einfache Lieferketten
- einfache Steuern
- einfache Wahlen
- einfache Medienereignisse
- Schocksystem
- Vektorwährung mit \(m,\theta,\rho,h\)

Dann beobachtest du:

- Preise
- Löhne
- Arbeitslosigkeit
- Firmenpleiten
- Winkelverteilung
- Winkelspreads
- Handelsvolumen
- internationale Konflikte
- Manipulation
- Ungleichheit
- politische Instabilität

Das wäre schon reich genug, um interessante Dynamiken zu erzeugen.

---

## 34. Die härteste Kurzfassung

Zu deiner Liste gehören zusätzlich vor allem diese fehlenden Blöcke:

1. **Haushalte und Individuen**  
   Ohne sie gibt es keine Nachfrage, Arbeit, Wahlen oder Beliebtheit.

2. **Banken, Zentralbanken und Kredit**  
   Ohne Kredit gibt es keine moderne Wirtschaft.

3. **Bilanzen und Buchhaltung**  
   Ohne Vektor-Bilanzen weiß niemand, wer wirklich reich, solvent oder toxisch ist.

4. **Rechtssystem und Eigentum**  
   Ohne Verträge, Gerichte und Insolvenzregeln zerfällt der Markt.

5. **Medien und Informationsflüsse**  
   Ohne sie entstehen Gut/Böse und Beliebt/Unbeliebt nicht realistisch.

6. **Lieferketten und Herkunftsnachweise**  
   Ohne sie wird Winkelgeld sofort waschbar.

7. **Steuern, Subventionen und Staatsausgaben**  
   Staaten müssen nicht nur bewerten, sondern handeln.

8. **Internationale Wechselkurse und Winkelübersetzung**  
   Mehrere Länder bedeuten mehrere moralische Koordinatensysteme.

9. **Betrug, Manipulation und Schattenmärkte**  
   Jedes mächtige Bewertungssystem erzeugt Angriffe.

10. **Unsicherheit und Konfidenz**  
    Weil weder Regierungen noch Völker unfehlbar sind.

11. **Zeit, Gedächtnis und Verzögerung**  
    Sonst springen Winkel unrealistisch sofort.

12. **Krisen und Schocks**  
    Ohne Krisen testest du das System nicht.

Die vollständige Simulation ist also keine reine Wirtschaftssimulation. Sie ist eine **politisch-ökonomische Zivilisationssimulation mit Vektorwährung**.

Der entscheidende Satz lautet:

\[
\boxed{
\text{Jeder Betrag hat Richtung, jede Richtung hat Unsicherheit, und jede Unsicherheit ist politisch angreifbar.}
}
\]

Wenn du das modellierst, wird die Simulation ernsthaft interessant.
