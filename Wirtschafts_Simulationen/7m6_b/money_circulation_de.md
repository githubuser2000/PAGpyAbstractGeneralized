# Wie zirkuliert das Geld aus Wert, Gutartigkeitsgrad und Beliebtheitsgrad, wenn es 2 Winkel gibt?

Das Geld zirkuliert dann nicht mehr wie ein einfacher Strom von Käufer zu Verkäufer. Es zirkuliert als **Doppelstrom**:

\[
\text{Ware/Dienstleistung fließt vom Verkäufer zum Käufer}
\]

\[
\text{Geld fließt vom Käufer zum Verkäufer}
\]

Und beide Ströme haben jeweils eine Richtung im Winkelraum.

Der zentrale Punkt ist:

\[
\boxed{
\text{Jeder Handel ist ein doppelter Winkeltausch.}
}
\]

Der Käufer kauft nicht nur ein Produkt.  
Der Verkäufer kauft gleichzeitig das Geld des Käufers.

---

# 1. Das Geldobjekt

Eine Geldeinheit besteht nicht nur aus Wert:

\[
M = m
\]

sondern aus:

\[
M = (m,g,b,\rho,h)
\]

mit:

\[
m = \text{Zahlenwert}
\]

\[
g = \text{Gutartigkeitsgrad}
\]

\[
b = \text{Beliebtheitsgrad}
\]

\[
\rho = \text{Konfidenz / Sicherheit der Bewertung}
\]

\[
h = \text{Historie / Herkunft}
\]

Der Winkel ergibt sich aus Gutartigkeit und Beliebtheit:

\[
\theta = \operatorname{atan2}(b,g)
\]

Also:

\[
g = \text{x-Achse: gut vs. böse}
\]

\[
b = \text{y-Achse: beliebt vs. unbeliebt}
\]

Der Betrag des Geldes ist:

\[
m
\]

Die Richtung ist:

\[
\theta
\]

Die Glaubwürdigkeit der Richtung ist:

\[
\rho
\]

Eine Zahlung ist also nicht nur:

\[
100
\]

sondern zum Beispiel:

\[
100 \angle 35^\circ,\quad \rho=0{,}82
\]

Das heißt: 100 Wert-Einheiten, mit bestimmter Gutartigkeits-/Beliebtheitsrichtung und bestimmter Sicherheit.

---

# 2. Jeder Akteur hat zwei Winkel

Jeder Akteur \(i\) hat:

\[
\theta_i^K = \text{Kaufwinkel}
\]

\[
\theta_i^V = \text{Verkaufswinkel}
\]

Die beste Definition ist:

\[
\boxed{
\theta_i^K = \text{welche Richtung ich empfangen will}
}
\]

\[
\boxed{
\theta_i^V = \text{welche Richtung ich ausgeben oder verkaufen will}
}
\]

Also:

- Der **Kaufwinkel** ist ein Eingangsfilter.
- Der **Verkaufswinkel** ist ein Ausgangssignal.

Ein Akteur ist dadurch ein **Winkeltransformator**.

Er nimmt Dinge aus einer Richtung auf und gibt Dinge in einer anderen Richtung aus.

\[
\theta_i^K \rightarrow \theta_i^V
\]

Wenn beide Winkel fast gleich sind, ist der Akteur kohärent.

Wenn sie stark auseinanderliegen, verdient oder lebt er von Winkelumwandlung.

---

# 3. Jeder Handel hat zwei Winkelprüfungen

Angenommen:

- Käufer \(A\) kauft von Verkäufer \(B\).
- Verkäufer \(B\) liefert ein Produkt oder eine Dienstleistung.
- Käufer \(A\) zahlt Geld.

Dann gibt es zwei Flüsse:

```text
Produkt / Dienstleistung:
B ─────────────────────────▶ A

Geld:
A ─────────────────────────▶ B
```

Aber jetzt mit Winkeln:

```text
Produktfluss:
B verkauft mit θ_B^V ─────▶ A empfängt mit θ_A^K

Geldfluss:
A zahlt mit θ_A^V ────────▶ B empfängt mit θ_B^K
```

Also müssen zwei Winkeldistanzen passen:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

für den Produktstrom.

Und:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

für den Geldstrom.

Das ist extrem wichtig.

Der Käufer fragt:

> Passt das Produkt, das ich empfange, zu meinem Kaufwinkel?

Der Verkäufer fragt:

> Passt das Geld, das ich empfange, zu meinem Kaufwinkel?

Denn für den Verkäufer ist Geld das empfangene Gut.

---

# 4. Die Kreisdistanz entscheidet über Handelbarkeit

Die Distanz zwischen zwei Winkeln ist:

\[
d(\alpha,\beta)=\arccos(\cos(\alpha-\beta))
\]

Damit liegt:

\[
d \in [0,\pi]
\]

Also:

\[
d=0
\]

heißt: perfekte Kompatibilität.

\[
d=\pi
\]

heißt: maximale Gegensätzlichkeit.

Eine einfache Kompatibilitätsfunktion wäre:

\[
\phi(d)=\cos\left(\frac{d}{2}\right)
\]

Dann gilt:

\[
d=0 \Rightarrow \phi=1
\]

\[
d=\pi \Rightarrow \phi=0
\]

Der Handel wird also stärker, je besser die Winkel zusammenpassen.

Für einen vollständigen Handel brauchst du beide Seiten:

\[
\Phi = \phi(d_X)\cdot \phi(d_M)\cdot \rho_X \cdot \rho_M
\]

mit:

\[
d_X = \text{Produkt-Winkeldistanz}
\]

\[
d_M = \text{Geld-Winkeldistanz}
\]

\[
\rho_X = \text{Konfidenz des Produktwinkels}
\]

\[
\rho_M = \text{Konfidenz des Geldwinkels}
\]

Wenn \(\Phi\) hoch ist, zirkuliert Geld leicht.

Wenn \(\Phi\) niedrig ist, entstehen Abschläge, Gebühren, Versicherungen, Audits, Rotation oder gar kein Handel.

---

# 5. Der Handel als Ablauf

Ein vollständiger Handel sieht so aus:

## Schritt 1: Käufer erzeugt Nachfrage

Käufer \(A\) sagt:

\[
\text{Ich will ein Gut mit Richtung nahe } \theta_A^K
\]

Zum Beispiel:

\[
\theta_A^K = 30^\circ
\]

Das heißt: Der Käufer sucht etwas, das gutartig und einigermaßen beliebt ist.

## Schritt 2: Verkäufer bietet an

Verkäufer \(B\) sagt:

\[
\text{Ich verkaufe ein Gut mit Richtung } \theta_B^V
\]

Zum Beispiel:

\[
\theta_B^V = 55^\circ
\]

Dann ist die Produktdistanz:

\[
d_X = 25^\circ
\]

Das ist relativ nah. Der Käufer akzeptiert wahrscheinlich.

## Schritt 3: Käufer bietet Zahlung an

Käufer \(A\) zahlt nicht mit neutralem Geld, sondern mit Geld aus seinem Ausgangswinkel:

\[
\theta_A^V
\]

Zum Beispiel:

\[
\theta_A^V = 80^\circ
\]

Das Geld ist vielleicht sehr beliebt, aber nur mäßig gutartig.

## Schritt 4: Verkäufer prüft Zahlung

Verkäufer \(B\) hat einen Kaufwinkel für eingehende Werte:

\[
\theta_B^K
\]

Zum Beispiel:

\[
\theta_B^K = 70^\circ
\]

Dann ist die Gelddistanz:

\[
d_M = 10^\circ
\]

Das Geld passt gut zum Verkäufer.

## Schritt 5: Handel wird ausgeführt

Wenn beide Distanzen klein genug sind:

\[
d_X \leq \varepsilon_X
\]

\[
d_M \leq \varepsilon_M
\]

dann wird gehandelt.

Der Käufer bekommt das Produkt.

Der Verkäufer bekommt das Geld.

Aber beide bekommen nicht nur Wert, sondern auch Winkelqualität.

---

# 6. Was zirkuliert wirklich?

Es zirkulieren drei Dinge gleichzeitig:

\[
\boxed{
\text{Wert}
}
\]

\[
\boxed{
\text{Gutartigkeit}
}
\]

\[
\boxed{
\text{Beliebtheit}
}
\]

Aber sie zirkulieren nicht gleich.

## Wert zirkuliert durch Zahlung

\[
A \rightarrow B
\]

Der Käufer verliert Zahlenwert.

Der Verkäufer gewinnt Zahlenwert.

## Gutartigkeit zirkuliert durch Herkunft, Produktion und Bewertung

Gutartigkeit entsteht oder verschwindet durch reale Handlungen:

- saubere Lieferketten
- faire Arbeit
- geringe Schäden
- gute Produkte
- Reparatur von Schäden
- Rechtmäßigkeit
- Umweltwirkung
- soziale Wirkung
- Transparenz
- Audits
- Gerichte
- Regierungsbewertung

Gutartigkeit ist also nicht bloß Meinung. Sie ist stärker an reale Folgen und institutionelle Prüfung gebunden.

## Beliebtheit zirkuliert durch Akzeptanz und Aufmerksamkeit

Beliebtheit entsteht durch:

- Nachfrage
- Kundenzufriedenheit
- Medien
- Trends
- Werbung
- soziale Netzwerke
- kulturelle Symbolik
- politische Lager
- Boykotte
- Proteste
- Influencer
- Herdenverhalten

Beliebtheit ist schneller beweglich als Gutartigkeit.

Deshalb kann Beliebtheit schneller steigen und schneller abstürzen.

---

# 7. Die Bilanzänderung beim Käufer

Vor dem Kauf hat Käufer \(A\):

\[
M_A = (m_A,g_A,b_A)
\]

Er zahlt:

\[
\Delta M = (p,g_{\text{pay}},b_{\text{pay}})
\]

Dann sinkt sein Geldbestand:

\[
m_A' = m_A - p
\]

Seine abgegebene Geldrichtung ist:

\[
\theta_A^V
\]

Gleichzeitig bekommt er ein Produkt:

\[
X = (u,g_X,b_X)
\]

mit Nutzen \(u\), Gutartigkeit \(g_X\), Beliebtheit \(b_X\).

Wenn das Produkt konsumiert wird, wird es nicht einfach zu Geld. Es verändert:

- Nutzen
- Lebensstandard
- Reputation
- zukünftige Präferenzen
- politische Meinung
- Nachfrage
- eventuell eigene Produktivität

Bei einem Haushalt:

\[
\text{Produkt} \rightarrow \text{Nutzen / Zufriedenheit / Meinung}
\]

Bei einer Firma:

\[
\text{Produkt} \rightarrow \text{Input / Lieferkette / neuer Produktionswinkel}
\]

Das ist wichtig: Wenn eine Firma einen schlechten Input kauft, kann dieser schlechte Winkel später in ihr eigenes Produkt eingehen.

---

# 8. Die Bilanzänderung beim Verkäufer

Verkäufer \(B\) gibt ein Produkt ab:

\[
X_B = (u,g_X,b_X)
\]

und erhält Geld:

\[
M_{\text{in}} = (p,g_M,b_M)
\]

Sein Geldbestand steigt:

\[
m_B' = m_B + p
\]

Aber seine Geldqualität verändert sich ebenfalls:

\[
g_B' = g_B + g_M
\]

\[
b_B' = b_B + b_M
\]

Sein neuer Cashwinkel wird:

\[
\theta_B^{\text{cash}}=
\operatorname{atan2}(b_B',g_B')
\]

Wenn viele Kunden mit gutem und beliebtem Geld zahlen, wird die Firmenkasse in diese Richtung gezogen.

Wenn viele Kunden mit toxischem Geld zahlen, wird die Firmenkasse belastet.

Das heißt:

\[
\boxed{
\text{Nicht nur Produkte haben Herkunft. Auch Kundengeld hat Herkunft.}
}
\]

---

# 9. Vektor-Geldbörse: Geld wird als Bündel geführt

In der Praxis sollte ein Akteur seine Geldbörse nicht nur als Summe speichern.

Er hat viele Geldlots:

\[
M_i = \{M_{i1},M_{i2},M_{i3},...\}
\]

Jedes Lot hat:

\[
(m,g,b,\rho,h)
\]

Also zum Beispiel:

```text
Lot 1: 500 Wert, guter Winkel, hohe Konfidenz
Lot 2: 200 Wert, beliebt, aber fragwürdig
Lot 3: 100 Wert, toxisch, niedrige Konfidenz
```

Wenn der Akteur zahlt, wählt er aus, welches Geld er ausgibt.

Das nennt man Coin Selection.

Mögliche Strategien:

## Bestes Geld zuerst

Der Akteur zahlt mit gutem Geld, um bessere Preise zu bekommen.

## Schlechtestes Geld zuerst

Der Akteur versucht, toxisches Geld loszuwerden.

## Passendes Geld zuerst

Der Akteur sucht Geldlots, deren Winkel zum Kaufwinkel des Verkäufers passen.

## Tarnmischung

Der Akteur mischt schlechtes Geld mit gutem Geld, um einen akzeptablen Durchschnittswinkel zu erzeugen.

Genau hier entsteht Winkelwäsche.

---

# 10. Der Verkäufer kann Zahlung ablehnen

Der Verkäufer akzeptiert nicht jedes Geld gleich.

Er prüft:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

Wenn das Geld zu weit von seinem Kaufwinkel entfernt ist, gibt es mehrere Möglichkeiten:

## Ablehnung

\[
d_M > \varepsilon
\Rightarrow
\text{kein Handel}
\]

## Abschlag

Der Verkäufer akzeptiert das Geld, aber nur mit Wertverlust:

\[
m_{\text{eff}} = m \cdot \phi(d_M)
\]

Zum Beispiel:

\[
100 \angle 160^\circ
\]

zählt bei ihm vielleicht nur als:

\[
62
\]

## Aufpreis

Der Käufer muss mehr zahlen:

\[
p_{\text{required}} = \frac{p}{\phi(d_M)}
\]

## Rotation

Ein Winkelhändler oder eine Bank dreht das Geld gegen Gebühr:

\[
\theta_A^V \rightarrow \theta_B^K
\]

mit Kosten:

\[
C_{\text{rot}}=\lambda m \tan^2\left(\frac{d_M}{2}\right)
\]

Je größer die Winkeldistanz, desto teurer wird die Drehung.

## Audit

Die Herkunft wird geprüft. Wenn der schlechte Winkel auf falschen Informationen beruht, kann die Konfidenz oder Richtung korrigiert werden.

---

# 11. Der Käufer kann Produkt ablehnen

Gleichzeitig prüft der Käufer:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

Wenn das Produkt zu weit vom gewünschten Kaufwinkel entfernt ist:

## Kein Kauf

Das Produkt bleibt liegen.

## Preisnachlass

Der Verkäufer muss billiger werden.

## Produktverbesserung

Der Verkäufer investiert in echte Verbesserung:

\[
\text{Wert} \rightarrow \text{Gutartigkeit}
\]

## Marketing

Der Verkäufer investiert in Wahrnehmung:

\[
\text{Wert} \rightarrow \text{Beliebtheit}
\]

## Zertifizierung

Der Verkäufer lässt den Winkel glaubwürdiger machen:

\[
\rho \uparrow
\]

Das bedeutet: Der Produktwinkel bestimmt Absatzfähigkeit.

Der Geldwinkel bestimmt Zahlungsfähigkeit.

---

# 12. Die zwei Winkel erzeugen vier Rollen in jeder Transaktion

In jeder Transaktion gibt es vier relevante Winkel:

\[
\theta_A^K = \text{Käufer empfängt Produkt}
\]

\[
\theta_A^V = \text{Käufer gibt Geld ab}
\]

\[
\theta_B^K = \text{Verkäufer empfängt Geld}
\]

\[
\theta_B^V = \text{Verkäufer gibt Produkt ab}
\]

Daraus entstehen zwei Matchings:

\[
\theta_A^K \leftrightarrow \theta_B^V
\]

für die Ware.

\[
\theta_B^K \leftrightarrow \theta_A^V
\]

für das Geld.

Das ist die vollständige Umlaufmechanik.

```text
                 Produktwinkel
          θ_B^V ───────────────▶ θ_A^K
          Verkäufer               Käufer


                   Geldwinkel
          θ_B^K ◀─────────────── θ_A^V
          Verkäufer               Käufer
```

Ein Handel ist stabil, wenn beide Verbindungen kurz sind.

Ein Handel ist instabil, wenn eine Verbindung kurz und die andere lang ist.

---

# 13. Beispiel: guter Handel

Käufer \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Verkäufer \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Dann:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

Beide Seiten passen.

Das Produkt passt zum Käufer.

Das Geld passt zum Verkäufer.

Der Handel ist hoch liquide.

\[
\Phi \approx 1
\]

Das Geld zirkuliert leicht.

---

# 14. Beispiel: Produkt passt, Geld passt nicht

Käufer \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 150^\circ
\]

Verkäufer \(B\):

\[
\theta_B^K = 50^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Dann:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

Das Produkt passt.

Aber:

\[
d_M = d(50^\circ,150^\circ)=100^\circ
\]

Das Geld passt nicht.

Folge:

- Käufer will kaufen.
- Verkäufer will verkaufen.
- Aber Verkäufer misstraut dem Geld.
- Es braucht Aufpreis, Rotation, Audit oder anderes Geld.

Das ist wie ein Zahlungsproblem trotz vorhandener Kaufkraft.

Der Käufer hat Wert, aber falschen Winkel.

---

# 15. Beispiel: Geld passt, Produkt passt nicht

Käufer \(A\):

\[
\theta_A^K = 30^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Verkäufer \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 150^\circ
\]

Dann:

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

Das Geld passt.

Aber:

\[
d_X = d(30^\circ,150^\circ)=120^\circ
\]

Das Produkt passt nicht.

Folge:

- Der Verkäufer würde das Geld gerne nehmen.
- Der Käufer will das Produkt nicht in dieser Richtung.
- Verkäufer muss verbessern, billiger werden oder eine andere Käufergruppe finden.

Das ist Absatzproblem trotz zahlungsfähiger Kunden.

---

# 16. Beispiel: beide Richtungen passen nicht

Käufer \(A\):

\[
\theta_A^K = 20^\circ
\]

\[
\theta_A^V = 160^\circ
\]

Verkäufer \(B\):

\[
\theta_B^K = 30^\circ
\]

\[
\theta_B^V = 170^\circ
\]

Dann:

\[
d_X = d(20^\circ,170^\circ)=150^\circ
\]

\[
d_M = d(30^\circ,160^\circ)=130^\circ
\]

Das Produkt passt nicht.

Das Geld passt nicht.

Der Handel findet wahrscheinlich nicht statt — außer auf einem Schattenmarkt oder mit extremen Abschlägen.

---

# 17. Umlauf als Transformationskette

Jeder Akteur nimmt eingehende Werte nahe seinem Kaufwinkel auf:

\[
\theta^K
\]

und gibt ausgehende Werte nahe seinem Verkaufswinkel ab:

\[
\theta^V
\]

Damit ist jeder Akteur eine Art wirtschaftlicher Winkeltransformator:

\[
T_i:
(m,g,b)_{\text{in}}
\rightarrow
(m',g',b')_{\text{out}}
\]

oder:

\[
\theta_i^K \rightarrow \theta_i^V
\]

Beispiele:

## Firma

Kauft Inputs und Arbeit:

\[
\theta^K_{\text{Firma}}
\]

produziert Waren:

\[
\theta^V_{\text{Firma}}
\]

Wenn sie reale Qualität erzeugt:

\[
g \uparrow
\]

Wenn sie gute Werbung macht:

\[
b \uparrow
\]

Wenn sie Schäden auslagert:

\[
g \downarrow
\]

Wenn sie beliebt bleibt trotz Schaden:

\[
b \uparrow,\quad g \downarrow
\]

## Haushalt

Empfängt Lohn:

\[
\theta^K_{\text{Haushalt}}
\]

gibt Konsumgeld aus:

\[
\theta^V_{\text{Haushalt}}
\]

Seine Kaufentscheidungen verändern Beliebtheit von Firmen.

## Bank

Empfängt Einlagen:

\[
\theta^K_{\text{Bank}}
\]

gibt Kredite aus:

\[
\theta^V_{\text{Bank}}
\]

Sie erzeugt neues Geld mit Winkel abhängig von Schuldner, Zweck und Risiko.

## Regierung

Empfängt Steuern:

\[
\theta^K_{\text{Staat}}
\]

gibt Staatsausgaben aus:

\[
\theta^V_{\text{Staat}}
\]

Sie kann durch Gesetze Gutartigkeit definieren und durch Ausgaben Winkel verschieben.

## Medien

Empfangen Aufmerksamkeit und Geld:

\[
\theta^K_{\text{Medien}}
\]

geben Beliebtheit oder Unbeliebtheit aus:

\[
\theta^V_{\text{Medien}}
\]

Sie beeinflussen vor allem \(b\), also Beliebtheit.

## Gerichte / Audits

Empfangen Fälle, Beweise, Gebühren:

\[
\theta^K_{\text{Gericht/Audit}}
\]

geben Konfidenz und Gutartigkeitskorrekturen aus:

\[
\theta^V_{\text{Gericht/Audit}}
\]

Sie beeinflussen vor allem \(g\) und \(\rho\).

---

# 18. Die wichtigste Umlaufformel

Für eine Transaktion zwischen Käufer \(A\) und Verkäufer \(B\):

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

Dann:

\[
\text{Handelsvolumen}
=
Q \cdot \phi(d_X)\cdot \phi(d_M)\cdot \rho_X\cdot\rho_M
\]

Oder kompakt:

\[
Q_T = Q_0 \Phi
\]

mit:

\[
\Phi =
\phi(d_X)\phi(d_M)\rho_X\rho_M
\]

Wenn \(\Phi\) hoch ist, zirkuliert viel.

Wenn \(\Phi\) niedrig ist, zirkuliert wenig.

Wenn viele Akteure inkompatible Kauf- und Verkaufswinkel haben, sinkt die Liquidität der gesamten Wirtschaft.

---

# 19. Wie Wert Gutartigkeit kauft

Wert kann Gutartigkeit kaufen, aber nur über reale Veränderung.

Zum Beispiel:

\[
\text{Wert} \rightarrow \text{bessere Arbeitsbedingungen}
\]

\[
\text{Wert} \rightarrow \text{saubere Energie}
\]

\[
\text{Wert} \rightarrow \text{Schadensersatz}
\]

\[
\text{Wert} \rightarrow \text{Produktsicherheit}
\]

\[
\text{Wert} \rightarrow \text{Lieferkettenprüfung}
\]

Dann steigt:

\[
g \uparrow
\]

Eine mögliche Simulationsregel:

\[
\Delta g
=
\eta_g \cdot \log(1+I_g)\cdot R_{\text{real}}\cdot \rho_{\text{audit}}
\]

mit:

\[
I_g = \text{Investition in echte Verbesserung}
\]

\[
R_{\text{real}} = \text{Realitätsfaktor}
\]

\[
\rho_{\text{audit}} = \text{Audit-Konfidenz}
\]

Wenn eine Firma nur behauptet, gut zu sein, aber keine reale Verbesserung macht:

\[
R_{\text{real}} \approx 0
\]

Dann steigt höchstens Beliebtheit kurzfristig, aber nicht echte Gutartigkeit.

---

# 20. Wie Wert Beliebtheit kauft

Wert kann Beliebtheit leichter kaufen:

\[
\text{Wert} \rightarrow \text{Werbung}
\]

\[
\text{Wert} \rightarrow \text{Rabatte}
\]

\[
\text{Wert} \rightarrow \text{Influencer}
\]

\[
\text{Wert} \rightarrow \text{Medienkampagnen}
\]

\[
\text{Wert} \rightarrow \text{Sponsoring}
\]

Dann steigt:

\[
b \uparrow
\]

Eine mögliche Simulationsregel:

\[
\Delta b
=
\eta_b \cdot \log(1+I_b)\cdot M_{\text{media}}\cdot S_{\text{trend}}
-
B_{\text{backlash}}
\]

mit:

\[
I_b = \text{Werbe-/PR-Ausgabe}
\]

\[
M_{\text{media}} = \text{Medienverstärkung}
\]

\[
S_{\text{trend}} = \text{Trendfaktor}
\]

\[
B_{\text{backlash}} = \text{Gegenreaktion}
\]

Beliebtheit ist schneller als Gutartigkeit, aber instabiler.

Deshalb entsteht oft:

\[
b \uparrow,\quad g \text{ bleibt gleich}
\]

oder sogar:

\[
b \uparrow,\quad g \downarrow
\]

Das ist der Fall:

\[
\text{beliebt, aber böse}
\]

---

# 21. Wie Beliebtheit Gutartigkeit kaufen kann

Beliebtheit kann Gutartigkeit nicht direkt kaufen, aber sie kann Reformen erleichtern.

Eine beliebte Firma hat:

- mehr Kundenvertrauen
- mehr politisches Kapital
- leichteren Zugang zu Mitarbeitern
- mehr Geduld der Investoren
- höhere Preissetzungsmacht
- weniger Widerstand gegen Veränderungen

Dann kann sie Beliebtheit in echte Reformfähigkeit umwandeln:

\[
b \rightarrow g
\]

Zum Beispiel:

\[
\Delta g
=
\eta_{bg}\cdot b \cdot I_g \cdot \rho
\]

Aber auch hier braucht es reale Investition.

Beliebtheit allein ist keine Gutartigkeit.

Sie ist nur eine Ressource, mit der Gutartigkeit leichter hergestellt werden kann.

---

# 22. Wie Gutartigkeit Beliebtheit kaufen kann

Gutartigkeit kann Beliebtheit erzeugen, aber nur wenn sie sichtbar wird.

\[
g \rightarrow b
\]

Das braucht:

- Transparenz
- freie Medien
- glaubwürdige Audits
- verständliche Kommunikation
- Bildung
- Zeit
- Vertrauen

Eine mögliche Regel:

\[
\Delta b
=
\eta_{gb}\cdot g \cdot T_{\text{visibility}}\cdot \rho
\]

mit:

\[
T_{\text{visibility}} = \text{Sichtbarkeit}
\]

Wenn niemand die Gutartigkeit sieht, steigt Beliebtheit kaum.

Deshalb kann eine gute, aber unsichtbare Firma unbeliebt bleiben.

---

# 23. Der gefährliche Umlauf: Winkelwäsche

Winkelwäsche entsteht, wenn jemand schlechten Wert in besseren Scheinwinkel verwandelt.

Zum Beispiel:

\[
1000 \angle 160^\circ
\rightarrow
900 \angle 40^\circ
\]

aber ohne echte Verbesserung.

Das kann passieren durch:

- Tochterfirmen
- Zwischenhändler
- Scheinaudits
- PR-Kampagnen
- Spenden
- gekaufte Ratings
- künstliche Beliebtheit
- Bot-Netzwerke
- Steuer- und Winkelparadiese

Dann steigt scheinbar:

\[
g \uparrow,\quad b \uparrow
\]

aber die Konfidenz sollte fallen:

\[
\rho \downarrow
\]

und die Historie \(h\) sollte verdächtig werden.

Darum braucht das System Herkunftsspur:

\[
h = \text{Transaktionshistorie}
\]

Ohne Historie wird Winkelgeld waschbar.

---

# 24. Zirkulation im Arbeitsmarkt

Der Arbeitsmarkt ist besonders wichtig.

Eine Firma kauft Arbeit.

Ein Arbeiter verkauft Arbeit.

Für die Firma ist Arbeit ein Input:

\[
\theta_{\text{Firma}}^K
\]

Für den Arbeiter ist Lohn ein eingehender Wert:

\[
\theta_{\text{Arbeiter}}^K
\]

Gleichzeitig:

- Der Arbeiter verkauft Arbeitskraft mit seinem Verkaufswinkel.
- Die Firma zahlt Lohn mit ihrem Verkaufswinkel.

Also wieder zwei Matchings:

\[
d_{\text{Arbeit}} = d(\theta_{\text{Firma}}^K,\theta_{\text{Arbeiter}}^V)
\]

\[
d_{\text{Lohn}} = d(\theta_{\text{Arbeiter}}^K,\theta_{\text{Firma}}^V)
\]

Wenn die Arbeit passt, aber der Lohnwinkel schlecht ist, verlangt der Arbeiter mehr Lohn.

Wenn der Lohn gut ist, aber die Tätigkeit schlecht ist, kann er trotzdem ablehnen.

Das erklärt reale Fälle:

\[
\text{hoher Lohn, schlechter Arbeitgeber}
\]

\[
\text{niedriger Lohn, guter Zweck}
\]

\[
\text{beliebte Firma, schlechte Arbeitsbedingungen}
\]

\[
\text{unpopulärer Beruf, hoher gesellschaftlicher Nutzen}
\]

---

# 25. Zirkulation im Kreditmarkt

Bei Kredit wird Geld neu erzeugt oder zeitlich verschoben.

Eine Bank gibt Kredit aus:

\[
\theta_{\text{Bank}}^V
\]

Der Schuldner empfängt Kredit:

\[
\theta_{\text{Schuldner}}^K
\]

Später zahlt der Schuldner zurück:

\[
\theta_{\text{Schuldner}}^V
\]

Die Bank empfängt Rückzahlung:

\[
\theta_{\text{Bank}}^K
\]

Also:

\[
d_{\text{Kredit}}=d(\theta_{\text{Schuldner}}^K,\theta_{\text{Bank}}^V)
\]

\[
d_{\text{Rückzahlung}}=d(\theta_{\text{Bank}}^K,\theta_{\text{Schuldner}}^V)
\]

Wenn der Kredit einem guten Zweck dient:

\[
g_{\text{Kredit}} \uparrow
\]

Wenn der Kredit populäre Spekulation finanziert:

\[
b_{\text{Kredit}} \uparrow,\quad g_{\text{Kredit}} \text{ unsicher}
\]

Wenn der Kredit toxische Aktivitäten finanziert:

\[
g_{\text{Kredit}} \downarrow
\]

Dann steigen Zinsen oder Sicherheiten.

Der Zinssatz besteht dann aus:

\[
i = i_0 + i_{\text{Ausfall}} + i_{\text{Winkelrisiko}} + i_{\rho}
\]

Also:

\[
\text{Zins} = \text{Zeitpreis} + \text{Risiko} + \text{Winkelstrafe}
\]

---

# 26. Zirkulation im Staat

Der Staat empfängt Steuern:

\[
\theta_{\text{Staat}}^K
\]

und gibt Staatsausgaben aus:

\[
\theta_{\text{Staat}}^V
\]

Steuern aus toxischen Quellen können problematisch sein:

\[
\text{Soll der Staat schlechtes Geld akzeptieren?}
\]

Wenn ja, muss er es vielleicht reinigen:

\[
\theta_{\text{toxisch}} \rightarrow \theta_{\text{öffentlich legitim}}
\]

durch:

- Gerichte
- Transparenz
- Umverteilung
- Schadensreparatur
- öffentliche Investitionen

Staatsausgaben erzeugen neue Winkel:

- Bildung kann \(g\) erhöhen.
- Propaganda kann \(b\) künstlich erhöhen.
- Infrastruktur kann Wert und Gutartigkeit erhöhen.
- Repression kann kurzfristig Ordnung, aber langfristig schlechten Winkel erzeugen.
- Krieg kann je nach Volk und Regierung sehr verschiedene Winkel bekommen.

Der Staat ist deshalb ein riesiger Winkeltransformator.

---

# 27. Zirkulation zwischen Ländern

Jedes Land hat eigene Achsen.

Was in Land A gut ist, ist in Land B nicht unbedingt gut.

Also braucht man eine Winkelübersetzung:

\[
T_{A\rightarrow B}(\theta)
\]

Ein Exportgeschäft hat dann:

\[
\theta_{\text{Export, A}}
\rightarrow
T_{A\rightarrow B}(\theta_{\text{Export, A}})
\]

Beispiel:

\[
40^\circ \text{ in Land A}
\]

kann werden zu:

\[
110^\circ \text{ in Land B}
\]

Dann entsteht internationale Winkelarbitrage.

Firmen suchen Länder, in denen:

- ihr Produkt beliebter ist
- ihre Gutartigkeit besser bewertet wird
- ihre schlechten Effekte weniger sichtbar sind
- ihre Historie weniger streng geprüft wird

Das ist moralische Standortarbitrage.

---

# 28. Was passiert bei mehreren Märkten?

Jeder Markt hat eine eigene Winkelstruktur.

## Produktmarkt

\[
\theta_{\text{Käufer}}^K
\leftrightarrow
\theta_{\text{Verkäufer}}^V
\]

## Zahlungsmarkt

\[
\theta_{\text{Verkäufer}}^K
\leftrightarrow
\theta_{\text{Käufer}}^V
\]

## Arbeitsmarkt

\[
\theta_{\text{Firma}}^K
\leftrightarrow
\theta_{\text{Arbeiter}}^V
\]

und:

\[
\theta_{\text{Arbeiter}}^K
\leftrightarrow
\theta_{\text{Firma}}^V
\]

## Kreditmarkt

\[
\theta_{\text{Schuldner}}^K
\leftrightarrow
\theta_{\text{Bank}}^V
\]

und später:

\[
\theta_{\text{Bank}}^K
\leftrightarrow
\theta_{\text{Schuldner}}^V
\]

## Kapitalmarkt

Investoren kaufen Firmenanteile:

\[
\theta_{\text{Investor}}^K
\leftrightarrow
\theta_{\text{Firma}}^V
\]

Firmen kaufen Kapital:

\[
\theta_{\text{Firma}}^K
\leftrightarrow
\theta_{\text{Investor}}^V
\]

## Winkelmarkt

Hier wird direkt Richtung gehandelt:

\[
(m,g,b)
\rightarrow
(m',g',b')
\]

mit Gebühr, Risiko und Konfidenzverlust.

---

# 29. Was die zwei Winkel ökonomisch bedeuten

Die Differenz zwischen Kaufwinkel und Verkaufswinkel ist der Kern der Geschäftslogik:

\[
s_i = d(\theta_i^K,\theta_i^V)
\]

Das ist der Winkelspread des Akteurs.

## Kleiner Spread

\[
s_i \approx 0
\]

Der Akteur kauft und verkauft in ähnlicher Richtung.

Das heißt:

- kohärent
- glaubwürdig
- wenig Transformationsleistung
- geringe Arbitrage
- hohe Vertrauenswürdigkeit

## Großer Spread

\[
s_i \gg 0
\]

Der Akteur kauft in einer Richtung und verkauft in einer anderen.

Das kann gut oder schlecht sein.

### Gute Variante

Er kauft schlechte Inputs und verbessert sie real.

\[
\theta^K = \text{schlecht}
\]

\[
\theta^V = \text{gut}
\]

Dann schafft er echte Wertverbesserung.

### Schlechte Variante

Er kauft schlechte Inputs und verkauft sie nur besser verpackt.

\[
\theta^K = \text{schlecht}
\]

\[
\theta^V = \text{scheinbar gut}
\]

Dann betreibt er Winkelwäsche.

### Extraktive Variante

Er kauft gute Inputs und verkauft schlechte Outputs.

\[
\theta^K = \text{gut}
\]

\[
\theta^V = \text{schlecht}
\]

Dann zerstört er Gutartigkeit oder Vertrauen.

---

# 30. Umlauf als Kreislauf in der Gesamtwirtschaft

Die Gesamtwirtschaft sieht dann so aus:

```text
Haushalte
  │ kaufen Produkte
  ▼
Firmen
  │ zahlen Löhne, kaufen Inputs, nehmen Kredite
  ▼
Banken / Kapitalmärkte
  │ finanzieren Firmen und Staaten
  ▼
Staaten
  │ besteuern, regulieren, subventionieren
  ▼
Medien / Völker / Gerichte / Regierungen
  │ bewerten Gutartigkeit, Beliebtheit und Konfidenz
  ▼
Winkelmärkte
  │ rotieren, versichern, prüfen und handeln Richtungen
  ▼
Haushalte und Firmen
```

Wert fließt durch Zahlungen.

Gutartigkeit fließt durch reale Folgen und institutionelle Urteile.

Beliebtheit fließt durch Nachfrage, Medien und soziale Akzeptanz.

Konfidenz fließt durch Nachweis, Transparenz und Streit.

Historie fließt durch die Transaktionskette.

---

# 31. Der Geldumlauf wird selektiv

In normalem Geld gilt:

\[
100 = 100
\]

In deinem System gilt:

\[
100 \angle 30^\circ \neq 100 \angle 150^\circ
\]

Darum zirkuliert Geld nicht mehr überall gleich.

Es bilden sich Zonen:

## Sauberer Hochkonfidenz-Kreislauf

Gutes Geld zirkuliert zwischen vertrauenswürdigen Akteuren.

\[
g \uparrow,\quad b \uparrow,\quad \rho \uparrow
\]

Dort sind Zinsen niedrig, Handel schnell, Spreads klein.

## Populärer, aber fragwürdiger Kreislauf

Beliebtes Geld zirkuliert schnell, aber mit Risiko.

\[
b \uparrow,\quad g \text{ unsicher}
\]

Dort gibt es Blasen und Skandale.

## Guter, aber unbeliebter Kreislauf

Gutartige, aber unpopuläre Aktivitäten brauchen Geduld, Subventionen oder Bildung.

\[
g \uparrow,\quad b \downarrow
\]

Dort droht Unterfinanzierung.

## Toxischer Kreislauf

Schlechtes Geld zirkuliert in Schattenmärkten oder mit hohen Abschlägen.

\[
g \downarrow,\quad b \downarrow,\quad \rho \downarrow
\]

Dort sind Zinsen hoch, Betrug häufig, Liquidität niedrig.

---

# 32. Warum der Umlauf nicht automatisch moralisch wird

Ein häufiger Denkfehler wäre:

> Wenn Gutartigkeit und Beliebtheit im Geld stecken, wird die Wirtschaft automatisch gut.

Nein.

Das System macht moralische Richtung handelbar.

Damit wird sie auch manipulierbar.

Es führt zu drei möglichen Formen:

## Echte Verbesserung

\[
\text{Wert} \rightarrow \text{reale Gutartigkeit}
\]

## Symbolische Verbesserung

\[
\text{Wert} \rightarrow \text{Beliebtheit}
\]

## Betrügerische Verbesserung

\[
\text{Wert} \rightarrow \text{scheinbare Gutartigkeit}
\]

Darum ist \(\rho\), also Konfidenz, absolut zentral.

Ohne Konfidenz wird der Winkel zum Propagandaetikett.

Mit Konfidenz wird der Winkel überprüfbar.

---

# 33. Der knappste Mechanismus

Die kürzeste vollständige Beschreibung lautet:

\[
\boxed{
\text{Akteure empfangen über ihren Kaufwinkel und senden über ihren Verkaufswinkel.}
}
\]

Jeder Handel prüft:

\[
\boxed{
\text{Passt der Verkaufswinkel der Ware zum Kaufwinkel des Käufers?}
}
\]

und:

\[
\boxed{
\text{Passt der Verkaufswinkel des Geldes zum Kaufwinkel des Verkäufers?}
}
\]

Wenn ja, fließen Wert, Gutartigkeit und Beliebtheit leicht.

Wenn nein, entstehen:

- Abschläge
- Aufpreise
- Rotation
- Auditkosten
- Versicherungen
- Wartezeiten
- Schattenmärkte
- Reputationsrisiken
- politische Konflikte

Der Geldumlauf ist also kein Kreis mehr, sondern ein gerichtetes Netzwerk:

\[
\boxed{
\text{Wert fließt entlang kompatibler Winkel.}
}
\]

\[
\boxed{
\text{Gutartigkeit fließt entlang realer Verbesserung und Anerkennung.}
}
\]

\[
\boxed{
\text{Beliebtheit fließt entlang Aufmerksamkeit und Zustimmung.}
}
\]

Die zwei Winkel jedes Akteurs bestimmen, **was er aufnehmen will** und **was er in die Welt abgibt**.

Genau daraus entsteht die Wirtschaftsdynamik.
