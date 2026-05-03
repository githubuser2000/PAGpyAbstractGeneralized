# Deutsch und English: Radial-hierarchische Moralwährung / Radial-Hierarchical Moral Currency

---

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


---

# Radial-Hierarchical Moral Currency

## Question

One axis is good vs. evil, and the other axis is popular vs. unpopular. Then this can be converted into a number: the sum over “hierarchy levels: sum of all elements in one hierarchy level times that hierarchy level,” and angular directions can also be extracted arbitrarily. Then the structure can be used as a currency, and this construct can be assigned to all market objects: the labor market, product market, stock market, currency market, insurance market. The currency is then not a number, and the currency gives information about who is entitled to something: the one who performs a lot; and the goodness or selflessness of products becomes recognizable because the governments of the world define this, while populations define popular vs. unpopular. The hierarchy is changeable: descending, career advancement, rising, for everything traded on markets, for example employers and employees.

## Answer

Yes. What you are describing is, at its core, a **multidimensional value currency** or a **normative market-coordinate system**:

\[
\text{market value} \neq \text{price}
\]

but rather:

\[
\text{market value} = f(\text{hierarchy}, \text{goodness}, \text{popularity}, \text{market context})
\]

Money is no longer merely a neutral number, but a **coded state of entitlement**: who receives something, sells something, loses something, earns something, or rises in rank no longer depends only on price, but on an evaluated position within the system.

## 1. The two axes create four basic types

If one axis is **good ↔ evil** and the other is **popular ↔ unpopular**, you get four quadrants:

| Quadrant | Meaning | Example interpretation |
|---|---|---|
| **good + popular** | socially desired and accepted | useful, fair, desired products; respected work |
| **good + unpopular** | valuable but underestimated | care work, basic research, unpopular necessary infrastructure |
| **evil + popular** | dangerously attractive | addictive products, manipulation, speculative bubbles, toxic platforms |
| **evil + unpopular** | socially unwanted | exploitation, fraud, harmful products |

This is powerful because it separates something that ordinary markets often mix together:  
**Popularity is not the same thing as goodness.**

A product can be popular and harmful. An activity can be unpopular and extremely valuable. This distinction is central to your model.

## 2. Hierarchy would be the third dimension

The axes “good/evil” and “popular/unpopular” provide the **direction**. Hierarchy provides the **depth, height, or rank position**.

Formally, an object could be described like this:

\[
V(x) = (G(x), B(x), H(x))
\]

where:

- \(G(x)\) = goodness, roughly from −1 to +1  
- \(B(x)\) = popularity, roughly from −1 to +1  
- \(H(x)\) = hierarchy value, rank, level, influence, depth of contribution, or structural position

Then an angular direction can also be determined:

\[
\theta(x) = \operatorname{atan2}(B(x), G(x))
\]

and a magnitude:

\[
r(x) = \sqrt{G(x)^2 + B(x)^2}
\]

Then a market object is no longer simply “worth 100 euros,” but for example:

\[
x = (\text{highly good}, \text{moderately popular}, \text{hierarchy level 7})
\]

This would indeed be more of a **vector currency** than a numerical currency.

## 3. Your hierarchy formula is possible, but it needs normalization

You mean roughly:

\[
H = \sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i
\]

So: for every hierarchy level \(k\), you sum all elements \(e_i\) of that level and multiply them by the level.

This produces a weighted hierarchy value.

Example:

- Level 1: simple activity
- Level 2: specialized activity
- Level 3: coordinating activity
- Level 4: strategic activity
- Level 5: system-shaping activity

Then someone or something would have more hierarchy value if it does not merely touch many elements, but influences elements at higher levels.

But there is a problem here: large organizations would automatically get enormous values simply because they contain many elements. That is why you would probably need a normalized form:

\[
H_{\text{norm}} = \frac{\sum_{k=1}^{n} k \cdot \sum_{i \in L_k} e_i}{\sum_{k=1}^{n} \sum_{i \in L_k} e_i}
\]

Then you measure not merely mass, but average hierarchical quality.

Otherwise the largest corporation, the largest authority, or the largest platform always wins.

## 4. As a currency, this would not be money in today’s sense

Normal money has three main functions:

1. **Medium of exchange**
2. **Unit of account**
3. **Store of value**

Your system would be more like:

1. **Medium of exchange**
2. **Unit of account**
3. **Store of value**
4. **Moral indicator**
5. **Status indicator**
6. **Entitlement indicator**
7. **Control instrument**

That is a massive extension.

The currency would then no longer merely say:

> How much does this cost?

It would also say:

> Is this good?  
> Is this popular?  
> Who earns from it?  
> Who is entitled to it?  
> What position does it have in the social hierarchy?  
> Should it be promoted, punished, taxed, preferred, or excluded?

Conceptually this is powerful, but politically extremely dangerous.

## 5. The strongest point: market values would become morally visible

Today a market price can conceal a great deal.

A cheap product can be cheap because workers are badly paid.  
An expensive product can be expensive even though it is socially useless.  
A popular company can be harmful.  
An unpopular job can be indispensable.

Your model would say:

> A market object receives not only a price, but a visible moral-social signature.

For example:

\[
\text{Product A} = (\text{good: }0.8,\ \text{popular: }0.6,\ \text{hierarchy: }4)
\]

\[
\text{Product B} = (\text{good: }-0.7,\ \text{popular: }0.9,\ \text{hierarchy: }6)
\]

Product B would then be popular and influential, but morally negative. In your system it could be taxed more heavily, restricted, or devalued.

This is a clear improvement over a market that sees only demand and purchasing power.

## 6. The most dangerous point: who defines “good”?

You say: the governments of the world define good/evil, and populations define popular/unpopular.

That division is logically clean, but politically delicate.

Because if governments define “good” and “evil,” the question immediately arises:

> Is “good” truly good — or merely government-conforming?

A state could mark dissent as “evil.”  
A government could artificially rate its own industries as “good.”  
Opposition, minorities, or inconvenient research could be devalued.

Then the currency would no longer be merely a market instrument, but an **instrument of rule**.

Using the population as the source of popularity has a different problem:

> Popularity is manipulable.

Whoever has media power, platform power, advertising, bots, cultural influence, or celebrity can manufacture popularity artificially. Then what becomes popular is not the good, but the best-manipulated.

Therefore your model would need safeguards:

- transparent justifications for good/evil ratings
- rights of appeal
- independent review bodies
- minority protection
- anti-manipulation rules for popularity
- separation of moral evaluation and political loyalty
- time delays against hype and panic
- uncertainty values instead of absolute judgments

Otherwise it very quickly becomes a perfected social-credit system.

## 7. “Who is entitled to something” is the real radical core

The most important sentence in your idea is not the geometry, but this:

> The currency gives information about who is entitled to something.

With that, you leave the normal market.

A classical market says:

> Whoever can pay gets it.

Your system says rather:

> Whoever deserves it, acts with goodness, is socially useful, and is appropriately positioned in the hierarchy receives a stronger claim.

This is a mixture of:

- meritocracy
- moral economy
- reputation system
- political allocation
- market mechanism
- status order

This can be fairer than pure capitalism, but only if the evaluation logic is very robust. Otherwise a new class order emerges: people and organizations with high scores get everything; people with low scores are excluded.

A healthy version would therefore probably have to say:

> Fundamental rights and basic provision must never depend entirely on this currency.

Otherwise moral market order turns into a caste system.

## 8. On labor markets this would be especially interesting

Employers and employees could both be evaluated.

An employee could have, for example:

\[
A = (\text{performance}, \text{goodness}, \text{popularity}, \text{hierarchy level})
\]

An employer likewise:

\[
U = (\text{productivity}, \text{fairness}, \text{social benefit}, \text{popularity}, \text{power level})
\]

Then the question would no longer be only:

> How much does the employer pay?

But also:

> Is this employer good?  
> Are its products good?  
> Does it treat people fairly?  
> Is its popularity deserved or manipulated?  
> Is its moral market position rising or falling?

This would make labor markets more symmetrical. Today the employer often evaluates the employee more strongly than the other way around. In your model, both sides would become hierarchically and morally visible.

## 9. On stock markets, it would morally color speculation

A stock would then not merely be:

\[
\text{price} + \text{expected return}
\]

but:

\[
\text{price} + \text{return} + \text{goodness} + \text{popularity} + \text{system rank}
\]

A company that is profitable but harmful might then have a high economic value, but a negative moral vector.

Investors could no longer invisibly say:

> I do not care, as long as the return is good.

The currency would show:

> This return comes from a negatively evaluated area.

That could strongly change capital flows.

## 10. In product markets, “selflessness” is difficult, but not impossible

Products themselves are not selfless. People, organizations, or designs can be selfless or exploitative. For products, one would more likely need to measure:

- benefit for buyers
- harm to third parties
- environmental costs
- working conditions
- dependency/addiction potential
- repairability
- transparency
- distribution of profit
- long-term social effect

Then “goodness of the product” would not be meant psychologically, but as an **externalities profile**.

A medication that saves lives would be good.  
An addictive product with aggressive marketing might be popular, but negatively good.  
A boring but important infrastructure product would be good, but perhaps unpopular.

That is exactly what your axis system is useful for.

## 11. The market would not disappear, but be filtered

Your system does not fully replace markets. It places a normative layer above them.

Today:

\[
\text{transaction allowed if price is paid}
\]

In your system:

\[
\text{transaction allowed/discounted/made harder depending on vector position}
\]

So:

- Good and popular things are made easier.
- Good but unpopular things are protected or subsidized.
- Evil but popular things are slowed down.
- Evil and unpopular things are excluded or heavily burdened.

That is a fairly elegant logic.

## 12. But a real currency needs compatibility

One problem: if currency is not a number, how do we compare two things?

Example:

\[
X = (\text{good }0.9,\ \text{popular }0.1,\ H=3)
\]

\[
Y = (\text{good }0.2,\ \text{popular }0.9,\ H=7)
\]

Which is worth more?

This cannot be decided objectively as long as you have no comparison rule. You need either:

### Variant A: Scalarization

You convert everything into a number:

\[
S = \alpha G + \beta B + \gamma H
\]

Advantage: easy to trade.  
Disadvantage: you lose multidimensionality.

### Variant B: Vector currency

You keep all dimensions:

\[
V = (G, B, H)
\]

Advantage: richer information.  
Disadvantage: harder exchange, because not everything is clearly comparable.

### Variant C: Context-dependent comparison rule

Different markets apply different weights.

In the healthcare market, goodness counts more strongly.  
In the entertainment market, popularity counts more strongly.  
In the labor market, performance/hierarchy counts more strongly.  
In the insurance market, risk and responsibility count more strongly.

This would probably be the best variant.

## 13. The most elegant form would not be a single currency, but a value protocol

I would formulate your model like this:

> The currency itself is not multidimensional; rather, every market unit carries a value vector, and every transaction is filtered through a social evaluation protocol.

So:

\[
\text{transaction} = (\text{price}, \text{value vector}, \text{entitlement rule})
\]

This keeps money practically usable, but it is no longer blind.

That is stronger than saying: “The currency is not a number.”  
More precisely:

> The price remains a number, but the validity, quality, and legitimacy of the price depend on a multidimensional value vector.

## 14. My assessment

The idea is conceptually strong because it connects three things that are normally kept separate:

1. **Hierarchy / performance / rank**
2. **Moral quality**
3. **Social acceptance**

This allows markets to be represented much more intelligently than by price alone.

But it has a hard breaking point:

> As soon as “good” is centrally defined and economic claims depend on it, an enormous power apparatus emerges.

The best version would therefore not be:

> Government determines good/evil absolutely.

But rather:

> Government, population, science, courts, market behavior, and verifiable impact data provide separate signals from which a transparent value vector emerges.

Then the system becomes less tyrannical and more knowledge-oriented.

In one sentence:

**You are describing a radial-hierarchical, vectorial moral currency that orders markets not only by price, but by goodness, popularity, and rank position — theoretically very powerful, but practically safe only if evaluation, appeal, minority protection, and manipulation resistance are taken extremely seriously.**
