# Planetenwirtschaft PyPy3-Simulation — erweiterte Makroversion

Dieses Projekt ist eine lauffähige PyPy3/CPython-Simulation des im Chat entwickelten Wirtschaftssystems:

> **Wirtschaft = koordinierte Veränderung realer Zustände**  
> statt Kauf/Verkauf von Dingen über Preis, Wert, Menge und Besitz.

Diese erweiterte Version fügt Bausteine hinzu, die man aus einer Volkswirtschaft kennt — aber übersetzt sie in eine **Planetenwirtschaft ohne Geldlogik**. Es gibt also weiterhin kein BIP, keine Preise, keine Währung, keine Löhne, keine Profite, keine Import-/Exportwerte. Stattdessen gibt es Bedürfnisdifferenzen, Wirkungsflüsse, Sektoren der Reproduktion, Stoffkreisläufe, Zeitbeiträge, Koordination, Wissen, Resilienz und planetare Grenzen.

## Schnellstart

```bash
pypy3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out_planetenwirtschaft
```

Falls PyPy3 nicht installiert ist:

```bash
python3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out_planetenwirtschaft
```

Kleiner Testlauf:

```bash
python3 planetary_effect_economy.py --steps 12 --regions 4 --communes-per-region 3 --population 10000000 --out quick_test
```

## Was neu hinzugefügt wurde

Die Grundversion hatte bereits Planetengrenzen, Bioregionen, Kommunen, Gruppen, Kohorten, Wahrheitsvektoren und globale Umverteilung. Diese Version ergänzt:

| Klassische Volkswirtschaft | Planetenwirtschaftliche Übersetzung |
|---|---|
| Wirtschaftssektoren | Wirkungssektoren: Reproduktion, Energie, Pflege, Wissen, Zirkulation, Kreislauf, Regeneration |
| Produktion | Aktivierung kausaler Effekte |
| Konsum | Annahme einer Bedürfniswirkung |
| Arbeit/Lohnarbeit | freiwilliger oder sozial organisierter Zeit-/Fähigkeitsbeitrag |
| Kapital/Investition | Kapazitätsaufbau: Wohnen, Gesundheit, Lagerung, Wissen, Resilienz, Infrastruktur |
| Staat/öffentlicher Sektor | demokratische Koordination, Governance-Kapazität, Rückkopplung, Fehlerkorrektur |
| Außenhandel | planetar-bioregionale Wirkungsflüsse nach Bedarf und Überschuss |
| Unternehmen/Firmen | Gruppen/Fähigkeitsfelder und Produktions-/Reparatur-/Sorgeverbände |
| Haushalte | Kommunen und Bevölkerungs-Kohorten als Bedürfnis- und Fähigkeitsknoten |
| Ungleichheit | Zufriedenheits- und Versorgungsungleichheit statt Einkommensungleichheit |
| Wachstum/BIP | planetarer Reproduktionsindex, Wohlbefinden, Grenzdruck, Resilienz, Zirkularität |
| Marktpreis | Priorität aus Wahrheitsvektor, Differenz, Dringlichkeit und Wirkungsrichtung |

## Erweiterte Handlungslogik

Die Simulation ersetzt die alten Begriffe „kaufen“ und „verkaufen“ nicht nur sprachlich, sondern technisch:

```text
Kaufen  → Bedürfniswirkung annehmen / Existenz stabilisieren
Verkaufen → Fähigkeit, Zeit, Substanz oder Wirkung beitragen
Handel → kausaler Wirkungsfluss zwischen Differenz und Potenz
```

Jeder Wirkungsfluss wird als Vektor protokolliert:

```text
Kausalität, Zeit, Intensität, Existenz, Potenzen, Wirkungen,
Substanz, Materie, Differenz, Bestimmung, Phänomene, Winkelrichtung
```

Wichtig: Die Simulation verwendet Zahlen, weil Computer rechnen müssen. Diese Zahlen sind aber **keine Preise, Werte oder Geldmengen**. Sie bedeuten Aktivierungsgrad, Priorität, Bedürfnisdeckung, Kapazität, Grenzdruck oder Wirkungsrichtung.

## Handlungsfelder / Domains

```text
water
food
energy
shelter
health
care
education
mobility
manufacturing
storage
governance
knowledge
resilience
repair
ecology
waste
```

Die neuen Felder `manufacturing`, `storage`, `governance`, `knowledge` und `resilience` bilden zusätzliche volkswirtschaftliche Funktionen ab:

- `manufacturing`: Grundindustrie, Werkzeuge, Ersatzteile, materielle Transformation.
- `storage`: Lager, Puffer, Stromspeicher, Vorratssicherheit.
- `governance`: demokratische Koordination, Konfliktlösung, Fehlerkorrektur.
- `knowledge`: Forschung, offene Pläne, technisches Lernen, Fähigkeitsaufbau.
- `resilience`: Katastrophenschutz, Redundanz, Notfallfähigkeit, Schockabsorption.

## Ausgabedateien

Nach einem Lauf erscheinen im Ausgabeordner:

| Datei | Inhalt |
|---|---|
| `summary.json` | Endzusammenfassung mit Anfang, Ende, Delta und erweiterten Kennzahlen |
| `timeline.csv` | globale Monats-Zeitreihe |
| `macro_accounts.csv` | planetare Makrokonten nach Domain/Sektor: Bedarf, Verfügbarkeit, Differenz, Priorität, Zeitbeitrag |
| `effect_flow_audit.csv` | Audit der letzten Handlungsrunde: Kauf/Verkauf/Handel als Wirkungsfluss ersetzt |
| `communes_final.csv` | Endzustand aller Kommunen mit Beständen, Kapazitäten und Prioritäten |
| `truth_audit.csv` | höchste Wahrheitswert-Prioritäten des letzten Schritts |
| `manifest.md` | menschenlesbare Interpretation des Laufs |

## Neue Kennzahlen

| Kennzahl | Bedeutung |
|---|---|
| `wellbeing` | Wohlbefinden aus Bedürfnisdeckung, Gesundheit, Autonomie, Vertrauen, Civic-Kapazität und planetarer Sicherheit |
| `unmet_basic` | unerfüllte Grundbedürfnisse |
| `overshoot` | Summe der Überschreitungen planetarer Grenzen über 1.0 |
| `avg_truth_error` | Fehler der gesellschaftlichen Wahrheits-/Rückkopplungslogik |
| `avg_autonomy` | Freiheit/Autonomie der Personen/Kohorten |
| `avg_trust` | Vertrauen in die Koordination |
| `contribution_time` | verfügbare und aktivierte Zeit-/Fähigkeitsbeiträge |
| `satisfaction_inequality` | Ungleichheit der Versorgung/Wohlbefindenslage |
| `resilience_index` | Puffer, Notfallfähigkeit, Lagerung und planetare Sicherheit |
| `circularity_index` | Verhältnis von Reparaturmaterial zu Abfall/Restdifferenz |
| `coordination_quality` | Demokratie, Vertrauen und niedriger Wahrheitsfehler zusammen |
| `basic_buffer_months` | Pufferdeckung von Wasser, Nahrung und Energie |
| `macro_capacity` | Summe gesellschaftlicher Kapazitäten: Wohnen, Gesundheit, Pflege, Bildung, Mobilität, Produktion, Lagerung, Governance, Wissen, Resilienz |
| `planetary_reproduction_index` | Gesamtindikator für planetare Reproduktion statt BIP |

## Szenarien

```bash
pypy3 planetary_effect_economy.py --scenario planetary_commons
pypy3 planetary_effect_economy.py --scenario local_democracy
pypy3 planetary_effect_economy.py --scenario technocratic_control
pypy3 planetary_effect_economy.py --scenario ecological_crisis
pypy3 planetary_effect_economy.py --scenario scarcity_shock
```

| Szenario | Bedeutung |
|---|---|
| `planetary_commons` | Standard: demokratische planetare Commons-Logik |
| `local_democracy` | stärkere kommunale Demokratie, weniger Zentralisierung |
| `technocratic_control` | Kontrollsystem: hohe Zentralisierung, niedrige Privatsphäre, schwache Korrektur |
| `ecological_crisis` | Start mit überschrittenen planetaren Grenzen |
| `scarcity_shock` | Start mit Wasser-/Nahrungs-/Energieknappheit |

## Planetar statt national

Die Simulation ist planetar, weil:

1. planetare Grenzen als Systembedingungen wirken,
2. globale Überschüsse nach Bedürfnisdifferenzen verteilt werden,
3. Regionen Bioregionen und Versorgungsknoten sind, keine Nationalstaaten,
4. die Erde nicht als Rohstofflager, sondern als Lebensbedingung modelliert wird,
5. Abfall, Boden, Wasser, Klima, Energie und Biosphäre zur Wirtschaft selbst gehören,
6. „Außenhandel“ zu innerplanetarem Wirkungsfluss wird,
7. Wohlbefinden nicht gegen Planetenschutz ausgespielt wird.

## Technische Hinweise

- Keine externen Bibliotheken.
- Kompatibel mit PyPy3 und CPython 3.
- Reproduzierbar über `--seed`.
- Standardgröße: 8,1 Milliarden synthetische Menschen, 12 Bioregionen, 96 Kommunen, 120 Monate.
- Das Modell ist synthetisch und nicht empirisch kalibriert. Es ist ein Simulationsbaukasten, kein Prognosemodell.

## Lesereihenfolge

1. `summary.json` für die Enddiagnose.
2. `timeline.csv` für Zeitverlauf.
3. `macro_accounts.csv` für planetare Makrobilanzen.
4. `effect_flow_audit.csv` für die neue Handelslogik.
5. `truth_audit.csv` für die Prioritäten aus Wahrheitswerten.
6. `communes_final.csv` für lokale Unterschiede.
