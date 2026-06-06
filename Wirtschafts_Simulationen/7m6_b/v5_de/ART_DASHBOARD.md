# V5: Erklärung des sehr bunten UTF‑8/ANSI-Dashboards

Das Dashboard ist absichtlich sehr dicht. Es zeigt dieselbe Vektorökonomie aus vielen Perspektiven: Geldfluss, Winkelrichtung, Kauf-/Verkaufswinkel, Orakelkonflikt, Sektorstruktur, Finanzsystem, Lieferketten, Macht, Medien, Konfidenz und Krise.

V5 behält die terminal-sichere V4-Ausgabe bei:

```text
sichere Breite = Terminalspalten - 5
```

ANSI-Farbcodes werden bei der Breitenmessung ignoriert; breite Unicode-Zeichen und Emoji werden konservativ gezählt. Rahmen werden nie breiter als die sichere Breite. Lange Tabellenzeilen und Diagramme werden innerhalb der Boxen umbrochen.

## Neue V5-Diagramme

### 1. Art-Legende

Erklärt die Farbsprache:

```text
grün       = gut, beliebt, positiver Wert
rot        = Risiko, Böse, Verlust, Krise
magenta    = Beliebtheit, Medienmacht, Popularitätsachse
gelb       = Geld, Wert, Winkelrotation
blau/cyan  = Institutionen, Finanzsystem, Lieferketten, Datenflüsse
```

### 2. Geldmassen-River

Zeigt, welche Akteursklasse wie viel gerichtetes Geld hält:

```text
Haushalte | Firmen | Banken | Fonds | Regierungen | Zentralbanken
```

Für jede Klasse werden Betrag, Cashwinkel, Konfidenz und Winkelkonzentration angezeigt.

### 3. Vektor-Bilanz nach Akteursklasse

Zerlegt die gehaltene Geldmenge in:

```text
x = Gutartigkeit/Bösartigkeit
y = Beliebtheit/Unbeliebtheit
```

So wird sichtbar, ob zum Beispiel Firmen zwar viel Wert halten, aber in einer schlechten oder unbeliebten Richtung liegen.

### 4. 360° Winkel-Liquiditätsrad

Zeigt vier Heat-Strips:

```text
Cashwinkel
Kaufwinkel
Verkaufswinkel
K/V-Gap
```

Damit sieht man, an welchen Winkelzonen Liquidität konzentriert ist und wo Kauf- und Verkaufsseite auseinanderfallen.

### 5. Order-Ausführungsleiter

Verknüpft konkrete Käufer und Verkäufer:

```text
Käufer-Kaufwinkel K  trifft  Verkäufer-Verkaufswinkel V
```

Daraus entstehen Distanz `Δθ`, Kompatibilität und effektiver handelbarer Wert.

### 6. Spread-Histogramm

Zeigt, wie weit Kaufwinkel und Verkaufswinkel der Akteure auseinanderliegen. Kleine Spreads bedeuten hohe Winkel-Liquidität; große Spreads bedeuten soziale oder moralische Marktspaltung.

### 7. Dreiecksbörse

Visualisiert den Handel der drei Kernobjekte:

```text
Wert ↔ Gutartigkeit ↔ Beliebtheit
```

Sie macht die kritische Frage sichtbar: Wird Gutartigkeit wirklich geschaffen, oder nur durch Wert und Beliebtheit kosmetisch gekauft?

### 8. Finanzsystem-Karte

Zeigt Kredit, Defaults, Bonds, Aktien, Dividenden, Hypotheken, Versicherungen, FX und Reserveinterventionen. In dieser Simulation handelt das Finanzsystem auch Winkelrisiko und Konfidenzrisiko.

### 9. Orakel-Divergenz

Je Land werden drei Marker gezeigt:

```text
G = Regierungs-/Gerichtswinkel
P = gewichtete Volksideologie
W = Währungswinkel
```

Große Distanzen zwischen G und P zeigen Legitimitätsrisiko.

### 10. Verfassungs-/Gerichtsschutz

Zeigt Gerichtsunabhängigkeit, Verfassungsschutz, Minderheitenschutz, Korruption, Regulatory Capture und Propagandabudget. Diese Box ist zentral, weil Winkelgeld sonst zum Gehorsamkeitsgeld werden kann.

### 11. Sektor-Heatmap

Jeder Sektor bekommt Balken für:

```text
Wertgewicht
Gutartigkeit
Beliebtheit
Konfidenz
Winkel
```

### 12. Sektorökonomie

Zeigt reale Wirtschaftsdaten hinter den Winkeln: Arbeit, Preise, Löhne, Profit und Technologie/Produktivität.

### 13. Lieferketten-Matrix

Zeigt, welche Inputs die Sektoren verwenden und wie Umwelt- und Sozialnutzen in den Produktwinkel einfließen.

### 14. Konzern-/Holding-Netzwerk

Zeigt Konzernopazität, Tochtergesellschaften, Tax-Haven-Länder, konsolidierte Winkel, Transfer Pricing und vermiedene Steuern.

### 15. Medien-/Beliebtheitsmacht

Zeigt Firmen, die über Medienmacht, Werbung und Markenmacht die Popularitätsachse bewegen können.

### 16. Ratingmarkt

Ratingagenturen wirken als Dritt-Orakel. Sie haben Bias, Genauigkeit, Korruption und Einfluss. Außerdem werden auffällige Firmenratings angezeigt.

### 17. Demografie & Human Capital

Zeigt Altersstruktur, Humankapital, Gesundheit und Migration. Diese Faktoren beeinflussen Arbeit, Produktivität, politische Geduld und Winkelpräferenzen.

### 18. Krisen-Seismograph

Sparklines für zentrale Frühwarnsignale:

```text
Inflation
Arbeitslosigkeit
Legitimitätslücke
Winkelvolatilität
Winkelwäsche
Black Market
Kapitalflüsse
Pollution Δ
```

## Weiterhin enthaltene Diagramme aus V3/V4

- Makro-Cockpit
- Vektor-Kompass
- Dreifachhandel-Diagramm
- Marktflussdiagramm
- Kreis-Orderbuch
- Akteurstabelle mit Cashwinkel/Kaufwinkel/Verkaufswinkel
- Länderpanel
- Firmenkarte Gutartigkeit × Beliebtheit
- externe Effekte
- Ereignisband
