# Vector Currency Economy Simulation V5

PyPy3-kompatible, reine-Standardbibliothek-Simulation für eine Zahlen-Winkel-Währung:

```text
M = (amount, theta, confidence, origin, history)
```

- `amount`: normaler Zahlenbetrag / Kaufkraft / Wertgewicht des Winkels
- `theta`: Winkel aus Gut/Böse-Achse und Beliebt/Unbeliebt-Achse
- `confidence`: Sicherheit des Winkels, also Konfidenz der Bewertung
- `origin` und `history`: Herkunft, Provenienz und Winkelwäsche-Risiko

V5 erweitert V4 um ein sehr viel dichteres, bunteres UTF‑8/ANSI-Art-Dashboard. Die Terminalbreitenerkennung aus V4 bleibt erhalten: automatisch erkannte Breite, minus 5 Zeichen Sicherheitsabstand, ANSI-/UTF‑8-bewusste Displaybreitenmessung und harter Umbruch innerhalb der Rahmen.

Die Simulation ist kein kalibriertes Realweltmodell. Sie ist ein lauffähiges Forschungsgerüst für Experimente mit einer politisch-ökonomischen Vektorwährung.

## Ausführen

Empfohlen mit PyPy3:

```bash
pypy3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Oder mit CPython:

```bash
python3 vector_currency_sim.py --steps 60 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --verbose
```

Mit sehr dichtem buntem UTF‑8/ANSI-Dashboard:

```bash
pypy3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --art --art-every 6
```

Ohne ANSI-Farben, aber weiterhin mit UTF‑8-Art:

```bash
pypy3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --seed 42 --out metrics.csv --summary summary.json --events events.csv --art --art-every 6 --no-color
```

## Dashboard-Flags

- `--art`: gibt das sehr große UTF‑8/ANSI-Dashboard während des Simulationslaufs aus.
- `--art-every N`: druckt das Dashboard alle `N` Schritte. Der erste und letzte Schritt werden immer gezeigt.
- `--art-width N`: optionale Maximalbreite. `0` bedeutet automatische Terminalerkennung. Auch explizite Werte werden auf `Terminalbreite - 5` gedeckelt.
- `--no-color`: deaktiviert ANSI-Farben, lässt aber die UTF‑8-Diagramme stehen.

## V5: zusätzliche Art-Diagramme

V5 enthält zusätzlich zu den V3/V4-Diagrammen viele neue Ausgaben:

- Art-Legende für Farben und Diagrammsprache
- Geldmassen-River nach Haushalten, Firmen, Banken, Fonds, Regierungen und Zentralbanken
- Vektor-Bilanz nach Akteursklasse: Betrag zerlegt in x=Gut/Böse und y=Beliebt/Unbeliebt
- 360° Winkel-Liquiditätsrad für Cashwinkel, Kaufwinkel, Verkaufswinkel und K/V-Gap
- Order-Ausführungsleiter: konkrete Käufer-Kaufwinkel treffen Verkäufer-Verkaufswinkel
- Kauf-/Verkaufswinkel-Spread-Histogramm
- Dreiecksbörse `Wert ↔ Gutartigkeit ↔ Beliebtheit`
- Finanzsystem-Karte für Kredit, Bonds, Aktien, Hypotheken, Versicherung und FX
- Orakel-Divergenz: Regierung/Gerichte vs. Völker/Medien je Land
- Verfassungs-/Gerichtsschutz gegen Winkelmissbrauch
- Sektor-Heatmap `Wert × Gutartigkeit × Beliebtheit`
- Sektorökonomie mit Arbeit, Preisen, Löhnen, Profit und Produktivität
- Lieferketten-Matrix: Vorleistungen und externe Effekte je Sektor
- Konzern-/Holding-Netzwerk mit Opazität, Tax Havens und Transfer Pricing
- Medien-/Beliebtheitsmachtkarte
- Ratingmarkt als Dritt-Orakel für Bonität und Winkelkonfidenz
- Demografie & Human Capital
- Krisen-Seismograph für Inflation, Arbeitslosigkeit, Legitimitätslücke, Winkelvolatilität, Winkelwäsche, Schwarzmarkt, Kapitalflüsse und Pollution

## Währungskern

```text
M = m · e^(iθ)
θ = atan2(Beliebtheit, Gutartigkeit)
effektive Kaufkraft ≈ m · ρ · cos(Δθ/2)
```

Jeder wichtige Akteur besitzt sichtbar:

```text
Kaufwinkel      θ_K = welche Winkelqualität er akzeptiert
Verkaufswinkel  θ_V = welche Winkelqualität er verlangt
Spread          Δθ  = Distanz zwischen Kaufen und Verkaufen
```

Der Betrag `m` ist weiterhin Kaufkraft, aber zugleich Gewicht des Winkels im Markt. Ein großer Akteur mit viel Geld zieht das Winkelorderbuch stärker als ein kleiner Akteur.

## Dateien

- `vector_currency_sim.py`: Hauptdatei, direkt ausführbar.
- `vector_currency_sim_v5.py`: identische V5-Kopie mit explizitem Namen.
- `demo_metrics.csv`: Beispielausgabe eines Demolaufs.
- `demo_summary.json`: Zusammenfassung des Demolaufs.
- `demo_events.csv`: Ereignislog des Demolaufs.
- `demo_art_ansi.txt`: Beispielausgabe des bunten V5-Dashboards mit ANSI-Farben.
- `demo_art_plain.txt`: dieselbe Dashboard-Art ohne ANSI-Farben.
- `demo_art_narrow.txt`: Schmalterminal-Beispiel.
- `COVERAGE.md`: Abdeckung der eingebauten Mechaniken.
- `CHANGELOG_V2.md`, `CHANGELOG_V3.md`, `CHANGELOG_V4.md`, `CHANGELOG_V5.md`: Entwicklungsschritte.
- `ART_DASHBOARD.md`: Erklärung der UTF‑8-Diagramme.
- `SMOKE_TEST_REPORT.txt`: Testnotizen.

## Terminalbreite und Umbruch

Das Dashboard nutzt `shutil.get_terminal_size()` aus der Standardbibliothek. Für die Ausgabe gilt:

```text
sichere Breite = erkannte Terminalspalten - 5
```

Alle Boxen, Tabellen, Ereigniszeilen, Kompasslegenden und langen Erklärungstexte werden mit ANSI-/UTF‑8-bewusster Displaybreite gemessen. ANSI-Farbcodes zählen nicht als Zeichen; breite Unicode-Zeichen und Emoji werden konservativ behandelt. Wenn eine Zeile zu lang ist, wird sie innerhalb des Rahmens umgebrochen. Der Rahmen selbst bleibt innerhalb der sicheren Breite.

## Hinweis

`pypy3` war in der Erstellungsumgebung nicht installiert. Der Code wurde mit CPython kompiliert und mit Demo-Läufen getestet. Er nutzt nur die Python-Standardbibliothek und sollte deshalb unter PyPy3 laufen.
