# CHANGELOG V3

## Neu gegenüber V2

### 1. Expliziter Dreifachmarkt

V3 ergänzt eine neue Simulationsphase:

```python
triadic_value_goodness_popularity_market(stats)
```

Diese Phase modelliert ausdrücklich den Tausch zwischen:

```text
Wert
Gutartigkeit
Beliebtheit
```

Neue Handelsrichtungen:

- `value_buy_goodness_volume`: Wert kauft Gutartigkeit durch Compliance, Audits, Umwelt, Arbeitsschutz und Transparenz.
- `value_buy_popularity_volume`: Wert kauft Beliebtheit durch Werbung, Service, Community und Medien.
- `popularity_buy_goodness_volume`: Beliebtheit kauft Gutartigkeit, weil ein sozial akzeptierter Akteur Reformkosten glaubwürdiger tragen kann.
- `goodness_buy_popularity_volume`: Gutartigkeit kauft Beliebtheit, wenn gute Handlungen über Medien, Gerichte und Zivilgesellschaft sichtbar werden.
- `value_good_pop_exchange_fees`: Reibung, Gebühren, Ineffizienz und moralische Tauschkosten.
- `triadic_exchange_count`: Anzahl der Dreifachtausch-Ereignisse pro Schritt.

### 2. Schutz gegen magische Winkelwäsche

Der Dreifachmarkt ist absichtlich nicht neutral-glatt. Folgende Faktoren verschlechtern echte Gutartigkeitstransformation und erhöhen Reibung:

- Betrug
- geringe Transparenz
- schwache Gerichte
- geringe Medienfreiheit
- Korruption
- geringe Produktqualität
- schlechte Reputation

Reine Beliebtheitskäufe können daher die Konfidenz senken und den Winkelwäscheindex erhöhen.

### 3. Großes UTF‑8/ANSI-Dashboard

Neue CLI-Flags:

```bash
--art
--art-every N
--art-width N
--no-color
```

Das Dashboard rendert:

- Makro-Cockpit
- Vektor-Kompass
- Dreifachhandel Wert/Gutartigkeit/Beliebtheit
- Marktflussdiagramm
- Kreis-Orderbuch für Kaufwinkel und Verkaufswinkel
- Akteurstabelle mit zwei Winkeln je Akteur
- Länderpanels
- Firmenquadrantenkarte Gutartigkeit × Beliebtheit
- externe Effekte und Sicherheitsventile
- Ereignisband

### 4. Verbose-Ausgabe erweitert

Die normale `--verbose`-Zeile zeigt nun zusätzlich:

```text
V→G = Wert kauft Gutartigkeit
V→P = Wert kauft Beliebtheit
```

### 5. Neue Demodateien

- `demo_art_ansi.txt`
- `demo_art_plain.txt`
- `demo_art_metrics.csv`
- `demo_art_summary.json`
- `demo_art_events.csv`
- `run_demo_art.sh`
- `ART_DASHBOARD.md`
