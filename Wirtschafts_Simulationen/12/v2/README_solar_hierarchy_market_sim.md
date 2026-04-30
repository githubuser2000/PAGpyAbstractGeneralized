# Solar Hierarchy Market Simulation for PyPy3

This is a large, dependency-free Python / PyPy3 simulation of a hierarchical market economy for the Solar System.

## New in this version

The simulation now includes a **large UTF-8 dashboard** with many textual graphs, diagrams, and visualizations, including:

- organizational hierarchy tree
- hierarchy level histograms for workers, companies, countries, products, and markets
- product access-level histogram
- heatmaps for workers by body × level and companies by body × level
- market domain × level heatmap by trade volume
- market volume by domain
- market trade counts by domain
- company sector table
- worker age table and age histogram
- active privileges by domain
- active burdens by domain
- market ownership by owner kind
- product ownership by owner kind
- entity counts by celestial body
- wallet value summary
- top market micro-shape table with sparklines

All charts are generated using plain UTF-8 characters, so they work directly in terminal output.

## Main file

- `solar_hierarchy_market_sim_pypy3.py`

## Run examples

```bash
pypy3 solar_hierarchy_market_sim_pypy3.py --profile demo --ticks 1
pypy3 solar_hierarchy_market_sim_pypy3.py --profile large --ticks 3 --seed 42
pypy3 solar_hierarchy_market_sim_pypy3.py --profile huge --ticks 2 --json report.json
```

To disable the UTF-8 diagrams:

```bash
pypy3 solar_hierarchy_market_sim_pypy3.py --profile demo --ticks 1 --no-visuals
```

## Profiles

- `demo`: small enough for quick inspection
- `large`: significantly larger system
- `huge`: very large simulation

## Model highlights

- 12 hierarchy levels
- Earth, Moon, Mars, and Solar System scope
- UN-like organizations for Earth, Moon, Mars, and Solar System
- defense organizations
- alliances of countries
- countries
- companies
- workers and employers
- products, privileges, burdens
- many markets by domain and hierarchy level
- **markets themselves are tradable assets**
- hierarchy bundles can be settled as numbers through weighted addition and multiplication by hierarchy height
- deep class inheritance across many inheritance stages

## Output files included

- `solar_hierarchy_market_demo_output_utf8.txt`
- `solar_hierarchy_market_demo_report_utf8.json`
- `solar_hierarchy_market_demo_output_plain.txt`

