# Q-Wirtschaftssimulation – farbiger UTF-8-Art-Bericht

Dieser Bericht ersetzt die trockene Endausgabe durch viele farbige UTF-8-Art-Darstellungen. Jede Abbildung beschreibt zuerst, was simuliert wird und warum diese Sicht wichtig ist. Danach folgt eine Auswertung, damit die Grafik nicht nur dekorativ ist, sondern ökonomisch lesbar wird.

Die Farben sind bewusst kräftig: Regenbogenbalken stehen für positive Mengen, Produktion, Beschäftigung oder Verteilung; Risiko- und Schuldanzeigen gehen von Grün über Gelb/Orange nach Rot. In der Terminalfassung werden zusätzlich ANSI-Farben verwendet.

## UTF-8 Art 01 – Makro-Cockpit

### Was wird simuliert und warum?
Simuliert wird der Endzustand der gesamten Volkswirtschaft: BQP, Preisniveau, Inflation, Arbeitslosigkeit, Q-Geldmenge, Q-Schulden, Kreditbestand und Ungleichheit. Diese Darstellung ist wichtig, weil sie sichtbar macht, ob die Wirtschaft nur groß wirkt oder auch tragfähig ist. In einer Q-Ökonomie reicht ein hoher Umsatz nicht aus; entscheidend ist, ob Geld, Schuld, Arbeit und semantische Münzstruktur zusammenpassen.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🌈 Q-Ökonomie Makro-Cockpit                                                                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Szenario: balanced             Perioden: 10    Haushalte: 40    Firmen: 14    Banken: 2                      ║
║ BQP / Marktumsatz     🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛  193.32 ZW                                                  ║
║ Preisindex            🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  1.22                                                       ║
║ Arbeitslosigkeit      ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0.0 %                                                      ║
║ Inflation letzte Per. 🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  1.8 %                                                      ║
║ Q-Geldmenge positiv   🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧  5.74 Tsd. ZW                                               ║
║ Q-Schulden            ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0.00 ZW  Verhältnis 0.00                                   ║
║ Kreditbestand         ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  81.46 ZW                                                   ║
║ Haushalts-Gini        🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0.05                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Das Cockpit zeigt den Endzustand der Simulation. Entscheidend ist die Gleichzeitigkeit von realem Umsatz, Q-Geldmenge, Q-Schulden, Beschäftigung und Preisniveau. Diese Größen dürfen nicht isoliert gelesen werden: Eine Wirtschaft kann hohe Umsätze haben und trotzdem semantisch krank sein, wenn die Schulden in Q16, Q18 oder Q20 liegen. Die Verschuldung wirkt relativ niedrig. Das lässt Raum für produktive Investitionen, solange die Geldmenge nicht nur in niedrigen Münzen konzentriert ist.

## UTF-8 Art 02 – BQP-Zeitpfad

### Was wird simuliert und warum?
Simuliert wird die Entwicklung des Brutto-Q-Produkts beziehungsweise des Marktumsatzes über alle Perioden. Das BQP ist hier kein strenges reales Bruttoinlandsprodukt, sondern die beobachtete Wertbewegung im Simulationsmarkt. Die Kurve ist wichtig, weil sie zeigt, ob Produktion und Nachfrage wachsen, stagnieren oder in Krisenphasen einbrechen.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 📈 BQP und Marktumsatz im Zeitverlauf                                                                               ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ BQP                    █▂▁▂▂▂▃▄▄▅                                                                                  ║
║                        Start 230.86 ZW │ Ende 193.32 ZW │ Min 151.81 ZW │ Max 230.86 ZW                            ║
║ Transaktionen          ▆▁▅▄▂▅█▄▄▂                                                                                  ║
║                        Start 436.00 │ Ende 409.00 │ Min 403.00 │ Max 450.00                                        ║
║ Exporte                ▆█▃▃▄▄▃▂▁▃                                                                                  ║
║                        Start 3.86 ZW │ Ende 1.46 ZW │ Min 0.00 ZW │ Max 5.85 ZW                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Das BQP fiel von 230.86 ZW auf 193.32 ZW; der beobachtete Korridor lag zwischen 151.81 ZW und 230.86 ZW. Die Richtung ist für diese Kennzahl grundsätzlich belastend. Die Zahl der Transaktionen fiel von 436.00 auf 409.00; der beobachtete Korridor lag zwischen 403.00 und 450.00. Die Richtung ist für diese Kennzahl grundsätzlich belastend. Wenn BQP und Transaktionen auseinanderlaufen, entsteht ein Hinweis auf Preisveränderungen, Konzentration oder Exportabhängigkeit. Ein steigendes BQP mit fallenden Transaktionen kann zum Beispiel bedeuten, dass wenige teure Güter dominieren.

## UTF-8 Art 03 – Geld, Kredit und Schulden

### Was wird simuliert und warum?
Simuliert wird die monetäre Tragfähigkeit: positive Q-Geldmenge, Q-Schulden, Kreditbestand, neue Kredite, Rückzahlungen und Ausfallverluste. Die Darstellung ist notwendig, weil diese Wirtschaft semantische Schulden kennt. Eine hohe Schuld ist besonders kritisch, wenn sie in Betrieb, Architektur oder Maschinenfähigkeit liegt.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 💳 Q-Geld, Q-Schulden und Kreditdynamik                                                                             ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ positive Q-Geldmenge   ▁▂▃▃▄▅▆▇▇█                                                                                  ║
║                        Start 5.14 Tsd. ZW │ Ende 5.74 Tsd. ZW │ Min 5.14 Tsd. ZW │ Max 5.74 Tsd. ZW                ║
║ Q-Schulden             ▄▄▄▄▄▄▄▄▄▄                                                                                  ║
║                        Start 0.00 ZW │ Ende 0.00 ZW │ Min 0.00 ZW │ Max 0.00 ZW                                    ║
║ Kreditbestand          ▁▁▂▂▃▃▆▆██                                                                                  ║
║                        Start 13.13 ZW │ Ende 81.46 ZW │ Min 13.13 ZW │ Max 84.16 ZW                                ║
║ Ausfallverluste        ▄▄▄▄▄▄▄▄▄▄                                                                                  ║
║                        Start 0.00 ZW │ Ende 0.00 ZW │ Min 0.00 ZW │ Max 0.00 ZW                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die positive Q-Geldmenge stieg von 5.14 Tsd. ZW auf 5.74 Tsd. ZW; der beobachtete Korridor lag zwischen 5.14 Tsd. ZW und 5.74 Tsd. ZW. Die Richtung ist für diese Kennzahl grundsätzlich günstig. Die Q-Schulden blieb weitgehend stabil von 0.00 ZW auf 0.00 ZW; der beobachtete Korridor lag zwischen 0.00 ZW und 0.00 ZW. Der Kreditbestand stieg von 13.13 ZW auf 81.46 ZW; der beobachtete Korridor lag zwischen 13.13 ZW und 84.16 ZW. Gesund ist ein Kreditpfad nur dann, wenn die daraus finanzierte Produktion die passenden Q-Münzen erzeugt. Kredit, der nur Liquidität schafft, aber Q10-, Q16- oder Q18-Lücken vergrößert, wird später zur Strukturkrise.

## UTF-8 Art 04 – Arbeitsmarkt und Löhne

### Was wird simuliert und warum?
Simuliert wird der Arbeitsmarkt über Beschäftigung, Arbeitslosigkeit, Durchschnittslohn und die Verteilung auf alle Arbeitstypen. Das ist wichtig, weil das Modell ausdrücklich eine ganze Wirtschaft abbildet: Landwirtschaft, Bau, Pflege, Handel, Industrie, Energie, Forschung, Software/KI und viele andere Arbeitsformen. Arbeit ist hier nicht nur Intelligenzarbeit, sondern gesellschaftliche Produktionsfähigkeit.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 👥 Beschäftigung, Arbeitslosigkeit und Lohn                                                                         ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Arbeitslosigkeit       ▄▄▄▄▄▄▄▄▄▄                                                                                  ║
║                        Start 0.0 % │ Ende 0.0 % │ Min 0.0 % │ Max 0.0 %                                            ║
║ Beschäftigte           ▄▄▄▄▄▄▄▄▄▄                                                                                  ║
║                        Start 40.00 │ Ende 40.00 │ Min 40.00 │ Max 40.00                                            ║
║ Durchschnittslohn      ▁██▆▆▅▅▅▄▂                                                                                  ║
║                        Start 3.59 ZW │ Ende 3.69 ZW │ Min 3.59 ZW │ Max 4.22 ZW                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 👷 Arbeitslandschaft: alle Arbeitsarten, nicht nur Intelligenzarbeit                                                            ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Arbeitstyp                    Beschäftigung                         Lohnbild                                                   ║
║ ────────────────────────────  ───────────────────────────────────  ─────────────────────────                                   ║
║ Management/Organisation       🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩    6                   🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 4.61 ZW                                       ║
║ Wartung                       🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛    5                   🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛ 3.07 ZW                                       ║
║ Ingenieurwesen                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛    4                   🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 4.78 ZW                                       ║
║ Industriearbeit               🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛    3                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.28 ZW                                       ║
║ Software/KI/Automatisierung   🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛    3                   🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛ 4.27 ZW                                       ║
║ Handwerk                      🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛ 3.09 ZW                                       ║
║ Bauarbeit                     🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛ 3.64 ZW                                       ║
║ Gesundheit                    🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛ 4.28 ZW                                       ║
║ Bildung                       🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.23 ZW                                       ║
║ Recht/Verträge                🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.39 ZW                                       ║
║ Kreative Arbeit               🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛ 2.85 ZW                                       ║
║ Öffentlicher Dienst           🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.17 ZW                                       ║
║ Sicherheit                    🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                   🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛ 3.04 ZW                                       ║
║ Energiearbeit                 🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    1                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.42 ZW                                       ║
║ Pflege                        🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    1                   🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛ 2.88 ZW                                       ║
║ Finanzwesen                   🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    1                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛ 3.29 ZW                                       ║
║ Einfache körperliche Arbeit   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Landwirtschaft                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Rohstoffarbeit                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Logistik                      ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Handel                        ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Gastgewerbe                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Forschung                     ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
║ Umweltarbeit                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00 ZW                                       ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Arbeitslosigkeit blieb weitgehend stabil von 0.0 % auf 0.0 %; der beobachtete Korridor lag zwischen 0.0 % und 0.0 %. Der Durchschnittslohn stieg von 3.59 ZW auf 3.69 ZW; der beobachtete Korridor lag zwischen 3.59 ZW und 4.22 ZW. Die Richtung ist für diese Kennzahl grundsätzlich günstig. Die Beschäftigungsbalken zeigen, ob die Volkswirtschaft breit arbeitet oder nur einzelne Bereiche übernutzt. Ein gesundes System braucht nicht nur Software/KI, sondern Nahrung, Energie, Bau, Pflege, Logistik, Bildung, Wartung und öffentliche Dienste.

## UTF-8 Art 05 – Preisniveau und Inflation

### Was wird simuliert und warum?
Simuliert wird, wie sich Preisindex und Inflation über die Perioden bewegen. Diese Sicht ist wichtig, weil Preisdruck in der Q-Ökonomie nicht nur Geldmengenproblem ist. Preissteigerungen können aus realen Güterengpässen, falscher Q-Struktur, Kreditüberdehnung oder mangelnder Betriebsfähigkeit entstehen.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🌡 Preisindex und Inflation                                                                                         ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Preisindex             ▁▂▂▃▄▅▅▆▇█                                                                                  ║
║                        Start 1.05 │ Ende 1.22 │ Min 1.05 │ Max 1.22                                                ║
║ Inflation              █▁▁▁▂▂▂▂▂▂                                                                                  ║
║                        Start 5.5 % │ Ende 1.8 % │ Min 1.3 % │ Max 5.5 %                                            ║
║ Importe                ▁▃▆▅▄█▆▆█▆                                                                                  ║
║                        Start 50.76 ZW │ Ende 60.93 ZW │ Min 50.76 ZW │ Max 66.10 ZW                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Der Preisindex stieg von 1.05 auf 1.22; der beobachtete Korridor lag zwischen 1.05 und 1.22. Die Richtung ist für diese Kennzahl grundsätzlich belastend. Die Inflation fiel von 5.5 % auf 1.8 %; der beobachtete Korridor lag zwischen 1.3 % und 5.5 %. Die Richtung ist für diese Kennzahl grundsätzlich günstig. Importe wirken als Puffer, aber nicht als unbegrenzte Rettung. Wenn Importwerte steigen, während Engpässe bestehen bleiben, liegt wahrscheinlich ein strukturelles Angebotsproblem vor.

## UTF-8 Art 06 – Q-Münzenmatrix

### Was wird simuliert und warum?
Simuliert wird die vollständige semantische Bilanz aller Münzen Q1 bis Q20: positive Bestände, Schulden und Marktpreise. Diese Darstellung ist das Herz der Q-Wirtschaft. Sie zeigt nicht nur, wie viel Wert vorhanden ist, sondern welche Art von Wert fehlt oder dominiert. Vier Q1 sind nominal so viel wert wie eine Q20, aber sie ersetzen keine fertige Maschine.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🪙 Q-Münzenmatrix: Vermögen, Schulden und Marktpreis                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Münze  Bedeutung                 Vermögen                              Schulden                              Kurs                ║
║ ─────  ────────────────────────  ───────────────────────────────────  ───────────────────────────────────  ─────                 ║
║ Q01    Schwierigkeit             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 965.66                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  1.00              ║
║ Q02    Komplexität               🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 276.66                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  1.00              ║
║ Q03    Abstraktion               🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 189.90                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  1.00              ║
║ Q04    Kristallisation           ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 4.51                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  1.00              ║
║ Q05    Kodierung                 🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛ 576.40                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  2.00              ║
║ Q06    Deklaration               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 1.91                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  2.00              ║
║ Q07    Delegation                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 1.38                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  2.00              ║
║ Q08    Bibliothek                🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 231.50                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  2.00              ║
║ Q09    Framework                 🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 81.48                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  2.00              ║
║ Q10    Constraint                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛ 667.65                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q11    Schnittstelle             🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 450.66                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q12    Toolbox                   🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 275.92                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q13    Programm/Dienst           🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛ 578.74                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q14    Orchestrierung            ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 5.21                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q15    Anwendung                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.94                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q16    Betrieb                   🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛ 678.78                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  3.00              ║
║ Q17    Kompression               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 2.60                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  4.00              ║
║ Q18    Architektur               🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛ 523.90                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  4.00              ║
║ Q19    Generierung               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.46                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  4.00              ║
║ Q20    Modul/Maschine            🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 228.37                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00                  4.00              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Matrix macht sichtbar, ob die Wirtschaft in niedrigen Grundmünzen, mittleren Operationsmünzen oder hohen System- und Kapitalmünzen konzentriert ist. Rote Schuldsegmente in Q16, Q18, Q19 oder Q20 sind besonders ernst, weil sie Betrieb, Architektur, Generierung und fertige Module betreffen. Hohe Bestände bei Q5 ohne passende Q10/Q18-Deckung deuten auf Code- oder Produktionsblasen hin.

## UTF-8 Art 07 – Q-Schuld-Hitzekarte

### Was wird simuliert und warum?
Simuliert wird die Konzentration der Q-Schulden nach Münzart. Die Hitzekarte ist wichtig, weil sie sofort zeigt, an welcher semantischen Stelle die Wirtschaft unter Druck steht. Eine Grundschuld Q1 ist eine ungelöste Aufgabe; eine Q18-Schuld ist fehlende Architektur; eine Q20-Schuld ist fehlende Maschinen- oder Modulreife.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🔥 Q-Schuld-Hitzekarte                                                                                                  ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Legende: grün = kaum Schuld, gelb/orange = angespannt, rot = starke semantische Schuld                                 ║
║ Q01🟩 0.0   Q02🟩 0.0   Q03🟩 0.0   Q04🟩 0.0                                                                              ║
║ Q05🟩 0.0   Q06🟩 0.0   Q07🟩 0.0   Q08🟩 0.0                                                                              ║
║ Q09🟩 0.0   Q10🟩 0.0   Q11🟩 0.0   Q12🟩 0.0                                                                              ║
║ Q13🟩 0.0   Q14🟩 0.0   Q15🟩 0.0   Q16🟩 0.0                                                                              ║
║ Q17🟩 0.0   Q18🟩 0.0   Q19🟩 0.0   Q20🟩 0.0                                                                              ║
║                                                                                                                        ║
║ Top-Schuldmünzen: Q1 Schwierigkeit 0.0 ZW │ Q2 Komplexität 0.0 ZW │ Q3 Abstraktion 0.0 ZW │ Q4 Kristallisation 0.0 ZW │ Q5 Kodierung 0.0 ZW ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die gefährlichsten Felder sind die dunkelsten oder rötesten Felder. Sie zeigen nicht nur finanzielle Last, sondern fehlende Fähigkeit. Wenn die Top-Schulden in System- oder Kapitalmünzen liegen, sollte die Politik nicht einfach Nachfrage erhöhen, sondern gezielt Struktur, Betrieb, Architektur oder Modulbau fördern.

## UTF-8 Art 08 – Güterengpässe

### Was wird simuliert und warum?
Simuliert wird, welche realen Güter und Dienste nicht ausreichend verfügbar waren. Diese Sicht verbindet das Q-System mit der gewöhnlichen Wirtschaft: Nahrung, Energie, Wohnen, Gesundheit, Bildung, Transport, Industrie, Kultur, Sicherheit und weitere Güter. Die Begründung ist einfach: Eine Währung bleibt abstrakt, wenn sie nicht in reale Versorgung übersetzt wird.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🧺 Güterengpässe und Preisdruck                                                                                     ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Umwelt/Resilienz           │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩│ 19.6  Preis×1.00                                               ║
║ Handelsleistung            │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩│ 19.5  Preis×1.29                                               ║
║ Gastgewerbe                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛│ 15.4  Preis×1.30                                               ║
║ Kultur/Kreativität         │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛│ 13.1  Preis×1.51                                               ║
║ Wartung                    │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛│ 12.2  Preis×1.33                                               ║
║ Industriegüter             │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 11.9  Preis×1.15                                               ║
║ Nahrung                    │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 9.7  Preis×1.44                                                ║
║ Software/KI/Automatisierun │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 9.5  Preis×1.00                                                ║
║ Rohstoffe                  │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 8.8  Preis×1.48                                                ║
║ Forschung/Wissen           │🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 6.1  Preis×1.00                                                ║
║ Sicherheit                 │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 4.4  Preis×1.00                                                ║
║ Öffentliche Leistung       │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 4.4  Preis×1.25                                                ║
║ Energie                    │🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 3.6  Preis×1.06                                                ║
║ Finanzdienst               │🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 3.4  Preis×1.11                                                ║
║ Transport/Logistik         │🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 2.9  Preis×0.94                                                ║
║ Wohnraum/Bau               │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.4  Preis×1.29                                                ║
║ Gesundheitsleistung        │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0  Preis×1.30                                                ║
║ Bildungsleistung           │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0  Preis×1.40                                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Hohe Engpässe zeigen, dass die Nachfrage nicht durch Produktion, Importe oder öffentliche Stabilisierung gedeckt wurde. Entscheidend ist der Zusammenhang zwischen Engpass und Preisverhältnis. Ein hoher Engpass mit starkem Preisaufschlag ist ein harter Angebotsmangel; ein hoher Engpass ohne Preisreaktion kann auf Marktträgheit oder staatliche Puffer hindeuten.

## UTF-8 Art 09 – Sektorenlandkarte

### Was wird simuliert und warum?
Simuliert wird die Wirtschaftsstruktur nach Sektoren: Umsatz, Profit, Anzahl der Firmen und Automatisierungsgrad. Diese Abbildung ist wichtig, weil eine vollständige Volkswirtschaft nicht an einem einzigen Sektor hängt. Landwirtschaft, Rohstoffe, Energie, Industrie, Bau, Gesundheit, Bildung, Logistik, Handel, Finanzwesen, öffentlicher Dienst, Kultur, Wartung, Forschung, Umwelt und Sicherheit müssen zusammenwirken.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🏭 Sektorenlandkarte: Umsatz, Profit und Automatisierung                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Sektor                    Umsatzbild                         Profitbild                    Firmen  Auto                      ║
║ ────────────────────────  ────────────────────────────────  ──────────────────────────  ──────  ────                         ║
║ Industrie                 🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 32.4             🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛│ +6.42                1  0.19                         ║
║ Kreativwirtschaft         🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛ 21.8             🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩│ +11.67               1  0.01                         ║
║ Gesundheit                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛ 20.0             🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛│ +3.68                1  0.11                         ║
║ Wartung                   🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛ 17.6             🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛│ +2.75                1  0.11                         ║
║ Bildung                   🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛ 16.4             🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛│ +5.50                1  0.05                         ║
║ Bau                       🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛ 16.4             🟥🟥🟥🟥🟥⬛⬛⬛⬛⬛│ -5.38                1  0.07                         ║
║ Energie                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 13.4             🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛│ +0.69                1  0.07                         ║
║ Öffentlicher Dienst       🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 13.2             🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛│ -1.34                1  0.09                         ║
║ Handel                    🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 12.7             🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛│ +5.08                1  0.09                         ║
║ Gastgewerbe               🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 8.8              🟩🟩🟩🟩🟩🟩🟩🟩⬛⬛│ +8.75                1  0.11                         ║
║ Finanzwesen               🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 8.4              🟥🟥🟥🟥🟥⬛⬛⬛⬛⬛│ -5.94                1  0.19                         ║
║ Rohstoffe                 🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 7.3              🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛│ +3.87                1  0.07                         ║
║ Landwirtschaft            🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 3.6              🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛│ +3.55                1  0.09                         ║
║ Logistik                  🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 1.3              🟥🟥🟥🟥⬛⬛⬛⬛⬛⬛│ -4.87                1  0.04                         ║
║ Software/KI/Automatisier  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ +0.00                0  0.00                         ║
║ Forschung                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ +0.00                0  0.00                         ║
║ Umwelt/Resilienz          ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ +0.00                0  0.00                         ║
║ Sicherheit                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ +0.00                0  0.00                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die größten Umsatzbalken zeigen, wo die Nachfrage konzentriert ist. Die Profitbalken zeigen, ob Sektoren Kapital aufbauen oder ausbluten. Negative Profitzonen können auf Preisdeckel, Inputmangel, zu geringe Nachfrage oder hohe Schuldlast hinweisen. Ein hoher Automatisierungswert ist produktiv, wird aber riskant, wenn Beschäftigung, Qualifikation oder Q10/Q16/Q18-Struktur nicht mitwachsen.

## UTF-8 Art 10 – Staat, Banken und Außenhandel

### Was wird simuliert und warum?
Simuliert werden öffentliche Finanzen, Kreditkanäle und der Außenhandel. Diese Darstellung ist nötig, weil Krisen nicht nur innerhalb von Firmen entstehen. Staatliche Transfers, öffentliche Käufe, Kredite, Rückzahlungen, Ausfälle, Exporte und Importe stabilisieren oder destabilisieren das ganze System.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🏦 Staat, Banken und Außenhandel                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Steuereinnahmen        │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 27.64 ZW                                                   ║
║ Transfers              │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 16.00 ZW                                                   ║
║ öffentliche Käufe      │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 39.10 ZW                                                   ║
║ Staatsnettovermögen    │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 1.09 Tsd. ZW                                               ║
║ Kreditbestand          │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 81.46 ZW                                                   ║
║ neuer Kredit           │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 11.71 ZW                                                   ║
║ Rückzahlungen          │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 17.57 ZW                                                   ║
║ Ausfallverluste        │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 ZW                                                    ║
║ Exporte                │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 1.46 ZW                                                    ║
║ Importe                │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 60.93 ZW                                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Ein tragfähiger Staat stabilisiert, ohne nur Schulden zu verschieben. Hohe öffentliche Käufe sind produktiv, wenn sie Q16-Infrastruktur, Q12-Werkzeuge, Bildung, Gesundheit oder Gemeingüter erzeugen. Banken sind nützlich, wenn Kredit echte Transformation finanziert; sie werden gefährlich, wenn Ausfälle steigen und die Kredite semantische Lücken nur verdecken.

## UTF-8 Art 11 – Haushalte und Ungleichheit

### Was wird simuliert und warum?
Simuliert wird die Verteilung des Haushaltsvermögens. Diese Abbildung ist wichtig, weil eine Wirtschaft auch dann instabil werden kann, wenn die Gesamtsumme gut aussieht, aber Haushalte keinen Zugang zu Arbeit, Bildung, Gesundheit oder Konsum haben. Ungleichheit schwächt Nachfrage, soziale Stabilität und die Fähigkeit, neue Q1-Aufgaben produktiv zu bearbeiten.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 👥 Haushalte, Vermögen und Ungleichheit                                                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Haushaltsvermögen als Verteilung. Negative Bereiche zeigen Schuld- oder Armutspositionen.                        ║
║ 38.6 bis 41.5                │🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    1                                                     ║
║ 41.5 bis 44.4                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛│    7                                                     ║
║ 44.4 bis 47.3                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛│    8                                                     ║
║ 47.3 bis 50.2                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪│    9                                                     ║
║ 50.2 bis 53.1                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪│    9                                                     ║
║ 53.1 bis 56.0                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    4                                                     ║
║ 56.0 bis 58.9                │🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    1                                                     ║
║ 58.9 bis 61.8                │🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    1                                                     ║
║                                                                                                                  ║
║ Durchschnitt 48.84 ZW │ Minimum 38.65 ZW │ Maximum 61.78 ZW │ Gini 0.051                                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Verteilung zeigt, ob das Vermögen breit liegt oder in wenigen oberen Bereichen konzentriert ist. Ein hoher Gini-Wert bedeutet nicht automatisch Zusammenbruch, aber er zeigt, dass Teilhabe und Nachfrage enger werden. In einer Q-Wirtschaft ist das besonders relevant, weil Bildung und Fähigkeiten bestimmen, welche Münzen Haushalte überhaupt erzeugen können.

## UTF-8 Art 12 – Kapital und Automatisierung

### Was wird simuliert und warum?
Simuliert wird, welche Sektoren Kapitalstock und Automatisierungsgrad aufbauen. Diese Sicht ist wichtig, weil Automatisierung nicht nur Software/KI bedeutet. Auch Industrie, Logistik, Energie, Bau, Gesundheit, Verwaltung, Landwirtschaft und Wartung können automatisiert oder kapitalintensiver werden. Produktiv ist das nur, wenn die menschliche und institutionelle Struktur nachzieht.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🤖 Kapital- und Automatisierungslandschaft                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Sektor                    Automatisierung                 Kapitalstock                                               ║
║ ────────────────────────  ─────────────────────────────  ─────────────────────────────                               ║
║ Finanzwesen               🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.19             🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛ 41.4 ZW                                     ║
║ Industrie                 🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.19             🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛ 53.6 ZW                                     ║
║ Wartung                   🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.11             🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛ 49.8 ZW                                     ║
║ Gastgewerbe               🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.11             🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛ 57.8 ZW                                     ║
║ Gesundheit                🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.11             🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛ 53.0 ZW                                     ║
║ Landwirtschaft            🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.09             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧 85.8 ZW                                     ║
║ Handel                    🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.09             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛ 69.6 ZW                                     ║
║ Öffentlicher Dienst       🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.09             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛ 67.7 ZW                                     ║
║ Bau                       🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.07             🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛ 52.9 ZW                                     ║
║ Energie                   🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.07             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛ 77.2 ZW                                     ║
║ Rohstoffe                 🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.07             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛ 71.3 ZW                                     ║
║ Bildung                   🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.05             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛ 81.2 ZW                                     ║
║ Logistik                  🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛ 74.0 ZW                                     ║
║ Kreativwirtschaft         ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.01             🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛ 43.0 ZW                                     ║
║ Software/KI/Automatisier  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00             ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0 ZW                                      ║
║ Forschung                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00             ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0 ZW                                      ║
║ Umwelt/Resilienz          ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00             ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0 ZW                                      ║
║ Sicherheit                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.00             ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0 ZW                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Sektoren mit hohem Kapital und hoher Automatisierung können Produktivität stark erhöhen. Sie können aber auch Beschäftigung verdrängen oder Q16-/Q18-Schulden erzeugen, wenn Betrieb und Architektur nicht ausreichend mitwachsen. Eine gesunde Automatisierungswelle braucht Ausbildung, Wartung, Schnittstellen und robuste Betriebsinfrastruktur.

## UTF-8 Art 13 – Q1 bis Q20 als Produktionskette

### Was wird simuliert und warum?
Simuliert wird die Grundbewegung der Q-Ökonomie: Aufgabe wird zu Teilung, Modell, Form, Operation, System, Architektur, Generierung und schließlich Modul oder Maschine. Diese Darstellung ist begründet, weil sie den Sinn der Münzen sichtbar macht. Die Wirtschaft produziert nicht nur Ware, sondern die Verwandlung von Schwierigkeit in funktionsfähige Struktur.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🧭 Q1→Q20-Produktionskette mit aktuellen Stressmarken                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Grundmünzen      Q1🟩 ── Q2🟩 ── Q3🟩 ── Q4🟩                                                                                        ║
║                     │       │       │       │                                                                                    ║
║ Operationen       Q5🟩 ── Q6🟩 ── Q7🟩 ── Q8🟩 ── Q9🟩                                                                                ║
║                     │       │       │       │       │                                                                            ║
║ Systeme          Q10🟩 ─ Q11🟩 ─ Q12🟩 ─ Q13🟩 ─ Q14🟩 ─ Q15🟩 ─ Q16🟩                                                                  ║
║                     │       │       │       │       │       │       │                                                            ║
║ Kapital          Q17🟩 ───────── Q18🟩 ───────── Q19🟩 ───────── Q20🟩                                                               ║
║                                                                                                                                  ║
║ Lesart: Aufgabe → Teilung → Modell → Form → Code/Regel/Delegation → Struktur/Dienst/Betrieb → Kompression/Architektur/Generierung/Maschine ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Markierungen zeigen, welche Stationen solide und welche belastet sind. Besonders kritisch ist ein Bruch zwischen Q5/Q13 und Q18/Q20: dann gibt es viel Implementierung oder Dienste, aber zu wenig Architektur und Modulreife. Ein Bruch zwischen Q1 und Q3 bedeutet dagegen, dass Aufgaben nicht gut verstanden oder modelliert werden.

## UTF-8 Art 14 – Risiko-Radar

### Was wird simuliert und warum?
Simuliert wird die Krisenanfälligkeit der Wirtschaft anhand mehrerer Stressachsen: Arbeitslosigkeit, Schuldenlast, Inflation, Architektur- und Betriebsschuld, Güterengpässe, Ungleichheit und Kreditausfälle. Diese Darstellung ist wichtig, weil Krisen selten aus nur einer Kennzahl entstehen. Sie entstehen durch Koppelungen.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🚨 Risiko-Radar der Q-Wirtschaft                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Arbeitslosigkeit     │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %                                                    ║
║ Schuldenlast         │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 Schulden/Geld                                       ║
║ Inflationsdruck      │🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 1.8 %                                                    ║
║ Q18-Architektur      │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %                                                    ║
║ Q16-Betrieb          │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %                                                    ║
║ Güterengpässe        │🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥│ 144.9 ungedeckt                                          ║
║ Ungleichheit         │🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.051 Gini                                               ║
║ Kreditausfälle       │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 ZW                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Rote oder stark gefüllte Balken sind die vorrangigen Krisenkanäle. Wenn mehrere Achsen gleichzeitig hoch stehen, sollte die Reaktion nicht eindimensional sein. Zum Beispiel löst Geldpolitik allein keine Architekturschuld, und ein Jobprogramm allein löst keinen Energieengpass. Die Q-Ökonomie verlangt gezielte Reparatur nach Münzart und Sektor.

## UTF-8 Art 15 – Ereignis-Timeline

### Was wird simuliert und warum?
Simuliert wird die zeitliche Folge wichtiger Ereignisse: Warnungen, Defaults, Insolvenzen, öffentliche Programme oder andere Stresssignale. Diese Abbildung ist wichtig, weil Kennzahlen nur Zustände zeigen, während Ereignisse den Verlauf erklären. Eine Krise entsteht nicht plötzlich; sie sammelt Vorzeichen.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🕰 Ereignis-Timeline                                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ P   0 │ 🟦init              │ Simulation initialisiert                                                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Timeline hilft, Ursachen zu sortieren. Häufen sich Warnungen früh, dann war die Endlage vorbereitet. Häufen sich Defaults spät, kann eine Kredit- oder Liquiditätskrise entstanden sein. Treten viele öffentliche Maßnahmen auf, war der Staat bereits als Stabilisator aktiv und sollte auf Wirksamkeit geprüft werden.

## UTF-8 Art 16 – Maßnahmenkarte

### Was wird simuliert und warum?
Simuliert wird keine automatische Wahrheit, sondern eine Priorisierung möglicher wirtschaftspolitischer Hebel aus dem Endzustand. Die Karte begründet, wo Interventionen ansetzen könnten: Schuldenrestrukturierung, Q18-Architekturprogramm, Q16-Betriebsinfrastruktur, öffentliches Jobprogramm, Engpassinvestitionen, Commons-Fonds oder Importpuffer.

```text
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ 🛠 Maßnahmenkarte: welche Hebel die Simulation nahelegt                                                                 ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Import-/Inputpuffer          │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛│ kurzfristige Güterknappheit glätten                                  ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Auswertung
Die Maßnahmenkarte ist kein Befehl, sondern eine Diagnoseübersetzung. Sie zeigt, welche Hebel nach den gemessenen Stresspunkten plausibel sind. Der wichtigste Grundsatz bleibt: keine abstrakte Geldflutung, wenn eine semantische Münzlücke vorliegt. Die passende Münze muss repariert oder produktiv erzeugt werden.
