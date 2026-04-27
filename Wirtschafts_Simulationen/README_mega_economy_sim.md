# Mega Economy Simulation for PyPy3

This is a deliberately broad, agent-based economic simulation written in **pure Python standard library**. It is designed for **PyPy3** and also runs on CPython 3.10+.

The model is not intended to predict a real economy. It is a causal sandbox for testing mechanisms, stress scenarios, policy rules, market interactions, distributional effects, and systemic fragility.

## What it simulates

The simulation includes these agent groups and institutions:

- households with income, wealth, skills, education, health, debt, mortgages, rent, housing ownership, platform use, insurance, and consumption preferences
- firms across many sectors with production, inventory, prices, markups, labor demand, capital, debt, investment, automation, innovation, energy intensity, emissions, suppliers, and bankruptcy risk
- banks with deposits, reserves, equity, loan books, credit rationing, capital ratios, non-performing loans, liquidity support, bailouts, and failures
- government with income/corporate/VAT/property/carbon taxes, transfers, unemployment benefits, pensions, public health/education/infrastructure spending, debt, deficits, bailouts, and green subsidies
- central bank with a Taylor-like policy rule, inflation target, policy rate, liquidity facility, and crisis response
- foreign sector with exchange rate, imports, exports, tariffs, trade balance, and capital-flow pressure
- energy market with fossil price, renewable capacity, storage, grid reliability, shortages, carbon pricing, emissions, and green investment
- housing market with regional house prices, rents, vacancies, construction lags, mortgages, affordability, and forced sales
- financial market with stock index, bond yield, credit spreads, asset-crash pressure, and financial stress
- platform market with network effects, user share, platform take rate, data advantage, and concentration
- insurance, health, education, migration, and human-capital dynamics

## Main research goals built in

The simulator is useful for exploring questions such as:

- Which channels generate inflation: demand, wages, energy, imports, market power, or supply bottlenecks?
- How do credit cycles, collateral values, defaults, and bank capital interact?
- When does a housing boom turn into a mortgage/banking crisis?
- How do monetary and fiscal policy interact during stagflation or financial stress?
- Who loses and who gains under shocks: renters, owners, low-skill workers, high-skill workers, firms, banks, regions?
- How does carbon pricing plus green investment affect emissions, energy prices, output, and inequality?
- When do platform network effects increase market concentration and fees?
- How do supply-chain disruptions propagate through input-output dependencies?
- How robust is a policy across different scenarios?

## Quick start

```bash
pypy3 mega_economy_sim.py --quiet --out baseline.csv --json baseline_summary.json
```

The default run is intentionally moderate so it finishes quickly on ordinary machines:

```bash
pypy3 mega_economy_sim.py --steps 60 --households 300 --firms 80 --banks 5 \
  --scenario baseline --out baseline.csv --json baseline_summary.json
```

For larger runs, use PyPy3 and scale gradually:

```bash
pypy3 mega_economy_sim.py --steps 120 --households 800 --firms 160 --banks 8 \
  --scenario climate_transition --policy green \
  --out climate.csv --json climate_summary.json
```

## Scenario comparison

```bash
pypy3 mega_economy_sim.py --steps 40 --households 300 --firms 80 --banks 5 \
  --compare baseline energy_shock financial_crisis climate_transition ai_automation \
  --out comparison.csv --json comparison.json
```

## Available built-in scenarios

- `baseline`
- `energy_shock`
- `supply_chain_break`
- `financial_crisis`
- `housing_boom_bust`
- `climate_transition`
- `protectionism`
- `ai_automation`
- `austerity`
- `stimulus`
- `pandemic_like`
- `stagflation_combo`

You can combine shocks:

```bash
pypy3 mega_economy_sim.py --scenario baseline --compound energy_shock,financial_crisis,supply_chain_break
```

## Policy modes

- `balanced`
- `hawkish`
- `dovish`
- `austerity`
- `stimulus`
- `green`

Example:

```bash
pypy3 mega_economy_sim.py --scenario energy_shock --policy hawkish
pypy3 mega_economy_sim.py --scenario energy_shock --policy stimulus
pypy3 mega_economy_sim.py --scenario climate_transition --policy green
```

## Output metrics

The CSV time series includes, among many others:

- GDP proxy, real output, CPI, inflation
- unemployment, wages, income inequality, wealth inequality, poverty
- firm bankruptcies, household defaults, bank failures
- bank capital ratio, NPL ratio, total credit, credit growth, credit spread
- policy rate, financial stress, stock index
- housing prices, rents, affordability, new housing units
- energy price, energy shortage, renewable share, emissions, carbon price
- imports, exports, trade balance, exchange rate
- government revenue, spending, deficit, debt-to-GDP
- platform user share, take rate, concentration
- sector-level prices, output, and HHI concentration

## Important model notes

This is a simulation framework, not a calibrated macroeconomic model. The default parameters are stylized. For serious use, calibrate the parameters, validate scenario behavior, run many seeds, and compare distributions instead of trusting a single trajectory.

The model is intentionally transparent. Most mechanisms are simple and inspectable so you can change them directly.

## Suggested workflow

1. Run a small baseline.
2. Pick one causal question.
3. Run several scenarios with the same seed.
4. Run the same scenario across many seeds.
5. Compare distributions of outcomes, not just one final number.
6. Modify the mechanisms you disagree with.

Example:

```bash
for seed in 1 2 3 4 5; do
  pypy3 mega_economy_sim.py --seed $seed --scenario housing_boom_bust \
    --steps 80 --households 400 --firms 100 --banks 6 \
    --out housing_seed_${seed}.csv --json housing_seed_${seed}.json
 done
```

## Files in this package

- `mega_economy_sim.py` — simulator source code
- `README_mega_economy_sim.md` — this README
- `sample_baseline.csv` — sample default time-series output
- `sample_baseline_summary.json` — sample default final summary
- `sample_comparison.csv` — small scenario-comparison output
- `sample_comparison.json` — small scenario-comparison summary
