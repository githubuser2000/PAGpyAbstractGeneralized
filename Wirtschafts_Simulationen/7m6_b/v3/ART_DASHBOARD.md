# Erklärung des UTF‑8/ANSI-Dashboards

Das Dashboard ist absichtlich bunt und dicht. Es soll nicht nur hübsch aussehen, sondern die zentralen Spannungen der Vektorwährung sichtbar machen.

## 1. Makro-Cockpit

Zeigt klassische Wirtschaftsdaten und neue Winkelmetriken:

- BIP
- Geldmenge
- Inflation
- Arbeitslosigkeit
- durchschnittliche Cash-Konfidenz
- Gutartigkeit auf der x-Achse
- Beliebtheit auf der y-Achse
- Legitimität und Legitimitätslücke
- Gini-Ungleichheit
- durchschnittlicher Winkelspread

Die kleinen Blocklinien sind Sparklines der letzten Simulationsschritte.

## 2. Vektor-Kompass

Der Kompass zeigt:

```text
◎ Weltgeldwinkel
¤ Cashwinkel
K Kaufwinkel
V Verkaufswinkel
```

Die Achsen sind:

```text
rechts  = gut
links   = böse
oben    = beliebt
unten   = unbeliebt
```

Damit sieht man sofort, ob das Geld eher gut/beliebt, gut/unbeliebt, böse/beliebt oder böse/unbeliebt steht.

## 3. Dreifachhandel

Das Diagramm zeigt live den Handel zwischen:

```text
Wert ↔ Gutartigkeit ↔ Beliebtheit
```

Die vier Flüsse sind:

```text
Wert → Gutartigkeit
Wert → Beliebtheit
Beliebtheit → Gutartigkeit
Gutartigkeit → Beliebtheit
```

Das entspricht der Idee, dass Gutartigkeit nicht nur durch Geld gekauft werden kann, sondern auch durch soziale Akzeptanz, Vertrauen und glaubwürdige Reformfähigkeit. Gleichzeitig kann Beliebtheit gekauft werden, ohne dass dadurch echte Gutartigkeit entsteht. Das erhöht den Winkelwäscheindex.

## 4. Marktflussdiagramm

Dieses Diagramm zeigt die simulierten Abschnitte als Zahlungs- und Wertflüsse:

- Haushalte kaufen von Firmen.
- Firmen zahlen Löhne.
- Firmen kaufen B2B-Inputs.
- Staaten nehmen Steuern und zahlen Subventionen.
- Banken vergeben Kredite.
- internationale Märkte handeln über FX und Kapitalflüsse.
- Winkelmärkte rotieren Cashwinkel gegen Kosten.
- Schwarzmarktvolumen wird sichtbar.

## 5. Kreis-Orderbuch

Das Kreis-Orderbuch teilt den Winkelraum in 12 Zonen. Für jede Zone sieht man:

```text
Kauf-Bid-Tiefe     Winkelzone     Verkaufs-Ask-Tiefe
```

Jeder Akteur hat zwei Winkel:

```text
Kaufwinkel    θ_K
Verkaufswinkel θ_V
```

Der Betrag des Akteurs gewichtet die Tiefe. Große Akteure bewegen den Winkelmarkt stärker.

## 6. Akteurstabelle

Die Tabelle zeigt die größten Akteure nach Wertgewicht:

- Typ
- Name
- Wert
- Cashwinkel
- Kaufwinkel
- Verkaufswinkel
- Spread
- Konfidenz
- Quadrant

Diese Tabelle ist wichtig, weil sie die Abstraktion „jeder hat zwei Winkel“ konkret macht.

## 7. Länderpanel

Zeigt je Land:

- BIP
- Wechselkurs
- Währungswinkel
- Legitimität
- Arbeitslosigkeit
- Inflation
- Proteste
- Infrastruktur
- Biodiversität
- Kriminalität
- Gerichtsunabhängigkeit

Damit wird sichtbar, dass der gleiche Winkel in verschiedenen Ländern anders politisch und sozial eingebettet ist.

## 8. Firmenkarte

Die Firmenkarte ist ein Koordinatensystem:

```text
x = Gutartigkeit
 y = Beliebtheit
```

Punkte sind Firmen. Größere Symbole stehen für größere Wertgewichte. Damit sieht man direkt die vier gefährlichen Quadranten:

```text
gut + beliebt
gut + unbeliebt
böse + beliebt
böse + unbeliebt
```

Besonders wichtig ist der Quadrant `böse + beliebt`, weil dort populistische, süchtig machende, ausbeuterische oder propagandistisch gestützte Märkte entstehen können.

## 9. Externe Effekte

Zeigt Schäden und Sicherheitsventile:

- Pollution
- Health Burden
- Biodiversity
- Crime Index
- Privacy Damage
- Infrastructure Quality
- Minority Harm
- Scandals
- Strikes
- Defaults
- Constitutional Overrides

## 10. Ereignisband

Zeigt die wichtigsten jüngsten Ereignisse:

- Skandale
- Audits
- Patentereignisse
- Boykotte
- Sanktionen
- Schocks
- Gerichtsentscheidungen
- politische Eingriffe

So sieht man, wodurch sich Winkel und Konfidenz verschieben.
