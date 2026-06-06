# CHANGELOG V4

V4 ist ein Dashboard-/Terminal-Robustheitsupdate für die Vektorwährungs-Simulation.

## Neu

- automatische Terminalbreitenerkennung über `shutil.get_terminal_size()`
- Sicherheitsabzug von 5 Zeichen vor der Dashboardausgabe
- `--art-width 0` als Auto-Modus; positive Werte werden auf `Terminalbreite - 5` gedeckelt
- ANSI-/UTF‑8-bewusste Displaybreitenmessung
- ANSI-Sequenzen zählen nicht als sichtbare Zeichen
- breite UTF‑8-Zeichen und Emoji werden konservativ behandelt
- Boxrahmen werden nie breiter als die erkannte sichere Breite
- Boxinhalte, lange Tabellenzeilen, Ereignisse und Erklärungssätze werden innerhalb der Box umgebrochen
- defensiver finaler Umbruchpass für zukünftige Renderer
- Tests mit simulierten Terminalbreiten 80, 50, 30, 20 und 10 Spalten

## Unverändert

- PyPy3-kompatibel
- nur Python-Standardbibliothek
- dieselben ökonomischen Mechaniken wie V3
- weiterhin buntes UTF‑8/ANSI-Dashboard mit `--art`
