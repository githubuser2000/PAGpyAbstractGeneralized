# CHANGELOG V5

V5 ist ein großes Dashboard-/Visualisierungsupdate für die Vektorwährungs-Simulation.

## Neu

- deutlich dichteres, bunteres UTF‑8/ANSI-Art-Dashboard
- neue Art-Legende
- Geldmassen-River nach Akteursklasse
- Vektor-Bilanz nach Akteursklasse: x=Gut/Böse, y=Beliebt/Unbeliebt
- 360° Winkel-Liquiditätsrad für Cashwinkel, Kaufwinkel, Verkaufswinkel und K/V-Gap
- Order-Ausführungsleiter für konkrete Käufer-/Verkäufer-Winkelkontakte
- Kauf-/Verkaufswinkel-Spread-Histogramm
- Dreiecksbörse `Wert ↔ Gutartigkeit ↔ Beliebtheit`
- Finanzsystem-Karte
- Orakel-Divergenz je Land: Regierung/Gerichte vs. Volk/Medien vs. Währung
- Verfassungs-/Gerichtsschutz-Dashboard
- Sektor-Heatmap `Wert × Gutartigkeit × Beliebtheit`
- Sektorökonomie: Arbeit, Preise, Löhne, Profit, Technologie
- Lieferketten-Matrix mit Inputsektoren, Umweltlast und Sozialnutzen
- Konzern-/Holding-Netzwerk mit Opazität, Tax Havens und Transfer Pricing
- Medien-/Beliebtheitsmacht-Karte
- Ratingmarkt als Dritt-Orakel
- Demografie-/Human-Capital-Diagramm
- Krisen-Seismograph

## Weiterhin enthalten

- automatische Terminalbreitenerkennung
- Sicherheitsabzug von 5 Zeichen
- `--art-width 0` als Auto-Modus
- explizite Breite wird weiterhin auf `Terminalbreite - 5` gedeckelt
- ANSI-/UTF‑8-bewusste Displaybreitenmessung
- Boxrahmen werden nicht breiter als die sichere Terminalbreite
- PyPy3-kompatibel
- nur Python-Standardbibliothek

## Teststatus

In der Erstellungsumgebung war `pypy3` nicht installiert. Der Code wurde mit CPython kompiliert und mit Demo-/Smoke-Tests inklusive `--art`, `--no-color`, ANSI-Farben und schmalen Terminalbreiten ausgeführt.
