# Mega-Wirtschaftssimulation in PyPy3 Python

Fertig. Ich habe ein großes, lauffähiges PyPy3-kompatibles Wirtschafts-Simulationspaket gebaut.

## Downloads

- [Simulator: `mega_economy_sim.py`](sandbox:/mnt/data/mega_economy_sim.py)
- [README / Anleitung](sandbox:/mnt/data/README_mega_economy_sim.md)
- [Sample Baseline CSV](sandbox:/mnt/data/sample_baseline.csv)
- [Sample Baseline Summary JSON](sandbox:/mnt/data/sample_baseline_summary.json)
- [Sample Scenario Comparison CSV](sandbox:/mnt/data/sample_comparison.csv)
- [Sample Scenario Comparison JSON](sandbox:/mnt/data/sample_comparison.json)
- [Alles als ZIP](sandbox:/mnt/data/mega_economy_sim_package.zip)

## Enthaltene Simulationsbestandteile

Enthalten sind unter anderem:

- Haushalte mit Einkommen, Vermögen, Bildung, Skill, Gesundheit, Konsum, Miete, Immobilienbesitz, Hypotheken, Schulden, Plattformnutzung und Versicherung.
- Firmen in vielen Sektoren: Food, Retail, Manufacturing, Construction, Housing, Energy, Transport, Health, Education, Finance, DigitalPlatform, ProfessionalServices, Exportables, GovernmentSupply.
- Arbeitsmarkt mit Matching, Skill-Fit, regionaler Mobilität, Löhnen, Arbeitslosigkeit und Automatisierungsdruck.
- Gütermärkte mit Nachfrage, Angebot, Inventar, Preisen, Markups, Knappheit und Importsubstitution.
- Kredit-/Bankensystem mit Bankbilanzen, Eigenkapital, Reserven, Kreditvergabe, NPLs, Defaults, Bailouts und Bankfailures.
- Immobilienmarkt mit regionalen Hauspreisen, Mieten, Leerstand, Bauverzögerungen, Hypotheken und Affordability.
- Energiemarkt mit fossilen Preisen, erneuerbarer Kapazität, Storage, Netzstabilität, Shortages, CO₂-Preis und Emissionen.
- Staat mit Steuern, Transfers, Arbeitslosengeld, Renten, Bildung, Gesundheit, Infrastruktur, Bailouts, Defizit und Schulden.
- Zentralbank mit Taylor-ähnlicher Reaktionsfunktion, Policy Rate, Krisenreaktion und Liquiditätsfazilität.
- Finanzmarkt mit Aktienindex, Bond Yield, Credit Spread, Financial Stress und Asset-Crash-Pressure.
- Außenhandel mit Importen, Exporten, Wechselkurs, Zöllen und Trade Balance.
- Plattformmarkt mit Netzwerkeffekten, User Share, Take Rate, Datenvorteil und Konzentration.
- Versicherung, Gesundheit, Bildung, Migration, Human Capital, Supply-Chain-Netzwerke und Firmenneugründungen.

## Beispielstart

```bash
pypy3 mega_economy_sim.py --quiet --out baseline.csv --json baseline_summary.json
```

## Größerer Lauf

```bash
pypy3 mega_economy_sim.py --steps 120 --households 800 --firms 160 --banks 8 \
  --scenario climate_transition --policy green \
  --out climate.csv --json climate_summary.json
```

## Szenariovergleich

```bash
pypy3 mega_economy_sim.py --steps 40 --households 300 --firms 80 --banks 5 \
  --compare baseline energy_shock financial_crisis climate_transition ai_automation \
  --out comparison.csv --json comparison.json
```

## Eingebaute Szenarien

```text
baseline
energy_shock
supply_chain_break
financial_crisis
housing_boom_bust
climate_transition
protectionism
ai_automation
austerity
stimulus
pandemic_like
stagflation_combo
```

## Schocks kombinieren

```bash
pypy3 mega_economy_sim.py \
  --scenario baseline \
  --compound energy_shock,financial_crisis,supply_chain_break
```

## Hinweis zur Skalierung

Die Defaults sind absichtlich moderat gesetzt, damit das Modell schnell startet. Für maximale Größe einfach `--households`, `--firms`, `--banks` und `--steps` hochsetzen. PyPy3 ist dafür klar besser als CPython.
