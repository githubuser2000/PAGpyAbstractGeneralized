# Wirtschaftssimulation nach Größenordnung

Diese Simulation übersetzt das abstrakte Währungsmodell in ein ausführbares PyPy3-Skript. Es nutzt nur die Python-Standardbibliothek und ist als Ein-Datei-Programm aufgebaut.

## Enthaltene Ebenen

| Größenordnung | Währung | Umsetzung im Skript |
|---|---|---|
| Land | Zahl | `CountryNumberCurrency`: Wert, Inflation, Schulden, Kaufkraft |
| Mehrere verbündete Länder | Winkel | `AlliedAngleCurrency`: Achsen gut/böse und beliebt/unbeliebt; Umrechnung über `tan`/`cotan` |
| Verteidigungsorganisation | Raum statt Zahl | `DefenseSpaceCurrency`: beliebig viele Dimensionen; Volumen wird zur Zahl; menschenbezogene Bindungen sind geschützt und nicht handelbar |
| UN-Assets | Asset-Währung | `UNAssetCurrency`: Aktien, Derivate, Fonds, Zertifikate, Währungskorb |
| Planet | Fuzzy-Wahrheitsstapel | `FuzzyTruthStackCurrency`: Werte von −1 bis +1, gestapelt zu Zahl |
| Sternensystem | Hierarchie | `HierarchyCurrency`: zwei Summen plus Multiplikation |
| Galaxie | Topologischer Monoid | `GalaxyMonoidCurrency`: unäre Operationen wie Invertieren und Verdrehen |
| Cluster von Galaxien | Topologische Gruppe | `ClusterGroupCurrency`: additionsähnliche Aggregation/Konkatenation kleinerer Währungen |
| Universum | For-Schleifen-Zirkulation | `UniverseLoopCurrency`: 20 Punkte pro Schleife; 3 Durchläufe = 60 Einheiten; plus Kreislaufwirtschaftsschuld/-beitrag |

## Start

```bash
pypy3 wirtschaftssimulation_pypy3.py --steps 120 --seed 42
```

Falls PyPy3 nicht installiert ist, läuft das Skript auch mit CPython 3:

```bash
python3 wirtschaftssimulation_pypy3.py --steps 120 --seed 42
```

## Beispiele

```bash
# Regeneratives Szenario mit JSON- und CSV-Ausgabe
pypy3 wirtschaftssimulation_pypy3.py \
  --steps 200 \
  --scenario regenerative \
  --seed 7 \
  --json-out result.json \
  --csv-out history.csv

# Volatiles Szenario mit mehr Ländern
pypy3 wirtschaftssimulation_pypy3.py \
  --steps 300 \
  --scenario volatile \
  --countries 14 \
  --alliances 4 \
  --planets 3

# Monte-Carlo-Modus
pypy3 wirtschaftssimulation_pypy3.py \
  --monte-carlo 25 \
  --steps 100 \
  --scenario extraction \
  --json-out monte_carlo.json
```

## Szenarien

- `balanced`: neutrale Ausgangslage
- `regenerative`: höhere Kreislaufpolitik, mehr Wahrheits-/Governance-Bias, geringere Volatilität
- `extraction`: rohstofflastig, geringere Kreislaufpolitik, mehr ökologische Schuld
- `militarized`: stärkere Verteidigungsräume, höhere Spannungs-/Volatilitätslast
- `volatile`: höhere Asset-Volatilität und mehr Schocks

## Zentrale Messwerte

- `total_country_number`: Summe der Zahlenwährungen aller Länder
- `avg_alliance_tan_value`: Winkelwährung der Bündnisse als tan-Zahl
- `defense_volume_number`: Raumwährung über Volumen in Zahl umgerechnet
- `protected_human_agency_links`: geschützte, nicht handelbare menschenbezogene Verantwortungs-/Agency-Links
- `un_asset_value`: Gesamtwert der UN-Assets
- `avg_truth_mean`: mittlerer Wahrheitswert der Planeten
- `hierarchy_number`: Sternensystem-Hierarchie als Zahl
- `cluster_number`: additionsähnliche Gruppenzahl des Galaxienclusters
- `universe_units`: For-Schleifen-Einheiten, bei Länge 20 also 60 nach 3 vollständigen Durchläufen
- `universe_stacked_value`: Schleifeneinheiten + Kreislaufbeitrag − Kreislaufschuld
- `systemic_risk`: verdichtetes Risikosignal aus Inflation, Schuldenstress, Lügenlast, Kreislaufschuld und Verteidigungsdruck

