# Planet Truth Paradigm Architecture — Verification/Falsification Expanded Edition

Neu in dieser Version:

- Verifikationen und Falsifikationen für **jeden Markt**
- Verifikationen und Falsifikationen für **jede Transaktion**
- Logikprädikat-Elemente für die planetare Wahrheitswährung WK
- zusätzliche Cross-Checks:
  - Land → Land
  - Unternehmen → Unternehmen
  - Land → Unternehmen
  - Unternehmen → Land
- neue UTF-8-Art-Renderer:
  - Prädikat-Ledger
  - Verifikations-Matrix
  - Verifikations-Zeitreihe
- sehr große Dokumentationsblöcke **vor jeder Grafik**
- Interpretationsblöcke **nach jeder Grafik**
- automatische Terminalbreite mit Sicherheitsabzug **5 Zeichen**
- `--print-art` standardmäßig aktiv; `--no-print-art` deaktiviert nur stdout

## Beispiel

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --out run_standard
```

## Wichtige Felder im Output

- `predicate_elements`: Gesamtanzahl aller erzeugten Logikprädikat-Elemente
- `verifications`: Anzahl positiver Prüfungen
- `falsifications`: Anzahl negativer Prüfungen
- `verification_by_market`: Anzahl der Prüfungen je Markt
- `verification_relation_totals`: Anzahl der Prüfungen je Relationstyp

## Dateien

- `summary.txt` — Zusammenfassung plus vollständiger Art-Report
- `utf8_paradigm_architecture_report.txt` — reiner ausführlicher UTF-8-Report
- `history.csv` — Monatsdaten inkl. Verifikationszeitreihen
- `agents.csv` — Agenten-Exports
- `morphisms.csv` — Morphismen/Transaktionen
- `events.json` — Ereignisse
- `summary.json` — Maschinenlesbare Zusammenfassung
