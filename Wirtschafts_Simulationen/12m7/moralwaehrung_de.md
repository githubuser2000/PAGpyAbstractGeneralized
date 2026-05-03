# Radial-hierarchische Moralwährung

## Frage

Eine Achse ist gut vs böse und die andere Achse ist beliebt vs unbeliebt. Dann kann man das in eine Zahl umwandeln: summe von 'hierarchiestufen "summe eine Hierarchiestufe alle Elemente mal Hierarchiestufe"' und Winkel Richtungen lassen sich auch beliebig entnehmen. Dann kann man das Gebilde als Währung verwenden und dieses Konstrukt sämtlichen Marktgegenständen zuordnen. Arbeitsmarkt, Produktemarkt, Aktienmarkt, Währungsmarkt, Versicherungsmarkt. Währung ist dann keine Zahl und die Währung gibt Aufschluss wem etwas zusteht, der viel leistet und gutartigkeit selbstlosigkeit der Produkte ist erkennbar, weil dies die Regierungen der Welt festlegen und die Bevölkerungen legen beliebt unbeliebt fest. Die Hierarchie ist veränderlich, absteigen Karriere Aufsteigen von allem, das auf Märkten gehandelt wird, z.B. Arbeitgeber und Arbeitnehmer.

## Antwort

Ja. Was du beschreibst, ist im Kern eine **mehrdimensionale Wertwährung** oder ein **normatives Markt-Koordinatensystem**:

\[
\text{Marktwert} \neq \text{Preis}
\]

sondern eher:

\[
\text{Marktwert} = f(\text{Hierarchie}, \text{Gutartigkeit}, \text{Beliebtheit}, \text{Marktkontext})
\]

Dabei ist Geld nicht mehr nur eine neutrale Zahl, sondern ein **kodierter Anspruchszustand**: Wer etwas bekommt, verkauft, verliert, verdient oder aufsteigt, hängt nicht nur vom Preis ab, sondern von einer bewerteten Position im System.

## 1. Die zwei Achsen ergeben vier Grundtypen

Wenn eine Achse **gut ↔ böse** ist und die andere **beliebt ↔ unbeliebt**, bekommst du vier Quadranten:

| Quadrant | Bedeutung | Beispielhafte Interpretation |
|---|---|---|
| **gut + beliebt** | gesellschaftlich erwünscht und akzeptiert | nützliche, faire, begehrte Produkte; angesehene Arbeit |
| **gut + unbeliebt** | wertvoll, aber untergeschätzt | Pflege, Grundlagenforschung, unbeliebte notwendige Infrastruktur |
| **böse + beliebt** | gefährlich attraktiv | Suchtprodukte, Manipulation, spekulative Blasen, toxische Plattformen |
| **böse + unbeliebt** | gesellschaftlich unerwünscht | Ausbeutung, Betrug, schädliche Produkte |

Das ist stark, weil es etwas trennt, was normale Märkte oft vermischen:  
**Beliebtheit ist nicht dasselbe wie Gutartigkeit.**

Ein Produkt kann beliebt und schädlich sein. Eine Tätigkeit kann unbeliebt und extrem wertvoll sein. Genau diese Unterscheidung ist in deinem Modell zentral.

## 2. Die Hierarchie wäre die dritte Dimension

Die Achsen „gut/böse“ und „beliebt/unbeliebt“ geben die **Richtung**. Die Hierarchie gibt die **Tiefe, Höhe oder Rangposition**.

Formal könnte ein Objekt so beschrieben werden:

\[
V(x) = (G(x), B(x), H(x))
\]

wobei:

- \(G(x)\) = Gutartigkeit, etwa von −1 bis +1  
- \(B(x)\) = Beliebtheit, etwa von −1 bis +1  
- \(H(x)\) = Hierarchiewert, Rang, Stufe, Einfluss, Leistungstiefe oder strukturelle Position

Dann kann man auch eine Winkelrichtung bestimmen:

\[
\theta(x) = \operatorname{atan2}(B(x), G(x))
\]

und eine Stärke:

\[
r(x) = \sqrt{G(x)^2 + B(x)^2}
\]

Dann ist ein Marktgegenstand nicht mehr einfach „100 Euro wert“, sondern zum Beispiel:

\[
x = (\text{hoch gut}, \text{mittel beliebt}, \text{Hierarchiestufe 7})
\]

Das wäre tatsächlich eher eine **Vektorwährung** als eine Zahlenwährung.

## 3. Deine Hierarchieformel ist möglich, aber sie braucht Normalisierung

Du meinst ungefähr:

\[
H = \sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i
\]

Also: Für jede Hierarchiestufe \(k\) summiert man alle Elemente \(e_i\) dieser Stufe und multipliziert sie mit der Stufe.

Das ergibt einen gewichteten Hierarchiewert.

Beispiel:

- Stufe 1: einfache Tätigkeit
- Stufe 2: spezialisierte Tätigkeit
- Stufe 3: koordinierende Tätigkeit
- Stufe 4: strategische Tätigkeit
- Stufe 5: systemprägende Tätigkeit

Dann hätte jemand oder etwas mehr Hierarchiewert, wenn es nicht nur viele Elemente berührt, sondern Elemente auf höheren Stufen beeinflusst.

Aber hier liegt ein Problem: Große Organisationen würden automatisch riesige Werte bekommen, nur weil sie viele Elemente haben. Deshalb brauchst du wahrscheinlich eine normalisierte Form:

\[
H_{\text{norm}} = \frac{\sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i}{\sum_{k=1}^{n} \sum_{i \in L_k} e_i}
\]

Dann misst du nicht nur Masse, sondern durchschnittliche hierarchische Qualität.

Sonst gewinnt immer der größte Konzern, die größte Behörde oder die größte Plattform.

## 4. Als Währung wäre das kein Geld im heutigen Sinn

Normales Geld hat drei Hauptfunktionen:

1. **Tauschmittel**
2. **Recheneinheit**
3. **Wertspeicher**

Dein System wäre eher:

1. **Tauschmittel**
2. **Recheneinheit**
3. **Wertspeicher**
4. **Moralindikator**
5. **Statusindikator**
6. **Anspruchsindikator**
7. **Steuerungsinstrument**

Das ist eine massive Erweiterung.

Die Währung sagt dann nicht nur:

> Wie viel kostet das?

Sondern auch:

> Ist das gut?  
> Ist es beliebt?  
> Wer verdient daran?  
> Wem steht es zu?  
> Welche Stellung hat es in der gesellschaftlichen Hierarchie?  
> Sollte es gefördert, bestraft, besteuert, bevorzugt oder ausgeschlossen werden?

Das ist konzeptionell mächtig, aber politisch extrem gefährlich.

## 5. Der stärkste Punkt: Marktwerte würden moralisch sichtbar

Heute kann ein Marktpreis sehr viel verschleiern.

Ein billiges Produkt kann billig sein, weil Arbeiter schlecht bezahlt werden.  
Ein teures Produkt kann teuer sein, obwohl es gesellschaftlich nutzlos ist.  
Eine beliebte Firma kann schädlich sein.  
Eine unbeliebte Arbeit kann unverzichtbar sein.

Dein Modell würde sagen:

> Ein Marktgegenstand bekommt nicht nur einen Preis, sondern eine sichtbare moralisch-soziale Signatur.

Zum Beispiel:

\[
\text{Produkt A} = (\text{gut: }0{,}8,\ \text{beliebt: }0{,}6,\ \text{Hierarchie: }4)
\]

\[
\text{Produkt B} = (\text{gut: }-0{,}7,\ \text{beliebt: }0{,}9,\ \text{Hierarchie: }6)
\]

Produkt B wäre dann zwar beliebt und einflussreich, aber moralisch negativ. In deinem System könnte es höher besteuert, begrenzt oder abgewertet werden.

Das ist eine klare Verbesserung gegenüber einem Markt, der nur Nachfrage und Zahlungsfähigkeit sieht.

## 6. Der gefährlichste Punkt: Wer definiert „gut“?

Du sagst: Die Regierungen der Welt legen gut/böse fest, die Bevölkerungen legen beliebt/unbeliebt fest.

Das ist logisch sauber aufgeteilt, aber politisch heikel.

Denn wenn Regierungen „gut“ und „böse“ festlegen, entsteht sofort die Frage:

> Ist „gut“ wirklich gut — oder nur regierungskonform?

Ein Staat könnte Dissens als „böse“ markieren.  
Eine Regierung könnte eigene Industrien künstlich als „gut“ bewerten.  
Opposition, Minderheiten oder unbequeme Forschung könnten abgewertet werden.

Dann wäre die Währung nicht mehr nur ein Marktinstrument, sondern ein **Herrschaftsinstrument**.

Die Bevölkerung als Quelle für Beliebtheit hat ein anderes Problem:

> Beliebtheit ist manipulierbar.

Wer Medienmacht, Plattformmacht, Werbung, Bots, kulturellen Einfluss oder Prominenz besitzt, kann Beliebtheit künstlich erzeugen. Dann wird nicht das Gute beliebt, sondern das am besten Manipulierte.

Deshalb bräuchte dein Modell Schutzmechanismen:

- transparente Begründungen für Gut/Böse-Bewertungen
- Einspruchsrechte
- unabhängige Prüfinstanzen
- Minderheitenschutz
- Anti-Manipulationsregeln für Popularität
- Trennung von moralischer Bewertung und politischer Loyalität
- zeitliche Verzögerungen gegen Hype und Panik
- Unsicherheitswerte statt absoluter Urteile

Sonst wird es sehr schnell ein perfektioniertes Sozialkreditsystem.

## 7. „Wem etwas zusteht“ ist der eigentliche radikale Kern

Der wichtigste Satz in deiner Idee ist nicht die Geometrie, sondern:

> Die Währung gibt Aufschluss, wem etwas zusteht.

Damit verlässt du den normalen Markt.

Ein klassischer Markt sagt:

> Wer zahlen kann, bekommt es.

Dein System sagt eher:

> Wer verdient, gutartig handelt, gesellschaftlich nützlich ist und passend hierarchisch positioniert ist, bekommt stärkeren Anspruch.

Das ist eine Mischung aus:

- Meritokratie
- Moralökonomie
- Reputationssystem
- politischer Allokation
- Marktmechanismus
- Statusordnung

Das kann gerechter sein als reiner Kapitalismus, aber nur, wenn die Bewertungslogik sehr robust ist. Sonst entsteht eine neue Klassenordnung: Menschen und Organisationen mit hohem Score bekommen alles; Menschen mit niedrigem Score werden ausgeschlossen.

Eine gesunde Version müsste daher vermutlich sagen:

> Grundrechte und Grundversorgung dürfen niemals vollständig von dieser Währung abhängen.

Sonst wird aus moralischer Marktordnung eine Kastengesellschaft.

## 8. Auf Arbeitsmärkten wäre das besonders interessant

Arbeitgeber und Arbeitnehmer könnten beide bewertet werden.

Ein Arbeitnehmer hätte zum Beispiel:

\[
A = (\text{Leistung}, \text{Gutartigkeit}, \text{Beliebtheit}, \text{Hierarchiestufe})
\]

Ein Arbeitgeber ebenfalls:

\[
U = (\text{Produktivität}, \text{Fairness}, \text{gesellschaftlicher Nutzen}, \text{Beliebtheit}, \text{Machtstufe})
\]

Dann wäre nicht nur die Frage:

> Wie viel zahlt der Arbeitgeber?

Sondern auch:

> Ist dieser Arbeitgeber gut?  
> Sind seine Produkte gutartig?  
> Behandelt er Menschen fair?  
> Ist seine Beliebtheit verdient oder manipuliert?  
> Steigt oder sinkt seine moralische Marktposition?

Das würde Arbeitsmärkte stärker symmetrisch machen. Heute bewertet der Arbeitgeber den Arbeitnehmer oft stärker als umgekehrt. In deinem Modell würden beide Seiten hierarchisch und moralisch sichtbar.

## 9. Auf Aktienmärkten würde es Spekulation moralisch einfärben

Eine Aktie wäre dann nicht nur:

\[
\text{Preis} + \text{Renditeerwartung}
\]

sondern:

\[
\text{Preis} + \text{Rendite} + \text{Gutartigkeit} + \text{Beliebtheit} + \text{Systemrang}
\]

Eine Firma, die profitabel, aber schädlich ist, hätte dann vielleicht einen hohen ökonomischen Wert, aber einen negativen moralischen Vektor.

Investoren könnten nicht mehr unsichtbar sagen:

> Mir egal, Hauptsache Rendite.

Die Währung würde zeigen:

> Diese Rendite kommt aus einem negativ bewerteten Bereich.

Das könnte Kapitalflüsse stark verändern.

## 10. Auf Produktmärkten wäre „Selbstlosigkeit“ schwer, aber nicht unmöglich

Produkte selbst sind nicht selbstlos. Menschen, Organisationen oder Designs können selbstlos oder ausbeuterisch sein. Bei Produkten müsste man eher messen:

- Nutzen für Käufer
- Schaden für Dritte
- Umweltkosten
- Arbeitsbedingungen
- Abhängigkeit/Suchtpotenzial
- Reparierbarkeit
- Transparenz
- Verteilung des Gewinns
- langfristige gesellschaftliche Wirkung

Dann wäre „Gutartigkeit des Produkts“ nicht psychologisch gemeint, sondern als **Externalitätenprofil**.

Ein Medikament, das Leben rettet, wäre gutartig.  
Ein Suchtprodukt mit aggressivem Marketing wäre vielleicht beliebt, aber negativ gutartig.  
Ein langweiliges, aber wichtiges Infrastrukturprodukt wäre gut, aber vielleicht unbeliebt.

Genau dafür ist dein Achsensystem brauchbar.

## 11. Der Markt würde nicht verschwinden, sondern gefiltert werden

Dein System ersetzt Märkte nicht vollständig. Es legt eine normative Schicht über sie.

Heute:

\[
\text{Transaktion erlaubt, wenn Preis bezahlt wird}
\]

In deinem System:

\[
\text{Transaktion erlaubt/vergünstigt/erschwert je nach Vektorposition}
\]

Also:

- Gute und beliebte Dinge werden erleichtert.
- Gute, aber unbeliebte Dinge werden geschützt oder subventioniert.
- Böse, aber beliebte Dinge werden gebremst.
- Böse und unbeliebte Dinge werden ausgeschlossen oder stark belastet.

Das ist eine ziemlich elegante Logik.

## 12. Aber eine echte Währung braucht Kompatibilität

Ein Problem: Wenn Währung keine Zahl ist, wie vergleicht man dann zwei Dinge?

Beispiel:

\[
X = (\text{gut }0{,}9,\ \text{beliebt }0{,}1,\ H=3)
\]

\[
Y = (\text{gut }0{,}2,\ \text{beliebt }0{,}9,\ H=7)
\]

Was ist mehr wert?

Das lässt sich nicht objektiv entscheiden, solange du keine Vergleichsregel hast. Du brauchst entweder:

### Variante A: Skalarisierung

Du wandelst alles in eine Zahl um:

\[
S = \alpha G + \beta B + \gamma H
\]

Vorteil: einfach handelbar.  
Nachteil: Du verlierst die Mehrdimensionalität.

### Variante B: Vektorwährung

Du behältst alle Dimensionen:

\[
V = (G, B, H)
\]

Vorteil: reichere Information.  
Nachteil: schwieriger Tausch, weil nicht alles eindeutig vergleichbar ist.

### Variante C: Kontextabhängige Vergleichsregel

Je nach Markt gelten andere Gewichte.

Auf dem Gesundheitsmarkt zählt Gutartigkeit stärker.  
Auf dem Unterhaltungsmarkt zählt Beliebtheit stärker.  
Auf dem Arbeitsmarkt zählt Leistung/Hierarchie stärker.  
Auf dem Versicherungsmarkt zählt Risiko und Verantwortung stärker.

Das wäre wahrscheinlich die beste Variante.

## 13. Die eleganteste Form wäre keine Einzelwährung, sondern ein Wertprotokoll

Ich würde dein Modell so formulieren:

> Nicht die Währung selbst ist mehrdimensional, sondern jede Markteinheit trägt einen Wertvektor, und jede Transaktion wird durch ein gesellschaftliches Bewertungsprotokoll gefiltert.

Also:

\[
\text{Transaktion} = (\text{Preis}, \text{Wertvektor}, \text{Anspruchsregel})
\]

Damit bleibt Geld praktisch verwendbar, aber es wird nicht mehr blind.

Das wäre stärker als zu sagen: „Die Währung ist keine Zahl.“  
Genauer wäre:

> Der Preis bleibt eine Zahl, aber die Gültigkeit, Qualität und Legitimität des Preises hängt von einem mehrdimensionalen Wertvektor ab.

## 14. Meine Einschätzung

Die Idee ist konzeptionell stark, weil sie drei Dinge verbindet, die normalerweise getrennt sind:

1. **Hierarchie / Leistung / Rang**
2. **Moralische Qualität**
3. **Soziale Akzeptanz**

Damit kann man Märkte viel intelligenter abbilden als mit Preis allein.

Aber sie hat eine harte Sollbruchstelle:

> Sobald „gut“ zentral definiert wird und wirtschaftliche Ansprüche daran hängen, entsteht ein enormer Machtapparat.

Die beste Version wäre daher nicht:

> Regierung bestimmt gut/böse absolut.

Sondern:

> Regierung, Bevölkerung, Wissenschaft, Gerichte, Marktverhalten und überprüfbare Wirkungsdaten liefern getrennte Signale, aus denen ein transparenter Wertvektor entsteht.

Dann wird das System weniger tyrannisch und mehr erkenntnisorientiert.

In einem Satz:

**Du beschreibst eine radial-hierarchische, vektorielle Moralwährung, die Märkte nicht nur nach Preis, sondern nach Gutartigkeit, Beliebtheit und Rangposition ordnet — theoretisch sehr mächtig, praktisch aber nur sicher, wenn Bewertung, Einspruch, Minderheitenschutz und Manipulationsabwehr extrem ernst genommen werden.**
