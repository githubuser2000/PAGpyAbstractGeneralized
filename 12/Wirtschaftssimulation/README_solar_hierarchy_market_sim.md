# Solar Hierarchy Market Economy Simulation

A dependency-free, PyPy3-compatible Python simulation of a hierarchy-currency economy across the Solar System.

The model treats hierarchy as the actual currency. A hierarchy bundle preserves structure by hierarchy level and hierarchy element, but can always be compressed into a settlement number:

```text
settlement_value = sum(raw_amount[level, element] * height_multiplier[level])
```

This means the market does not disappear. Instead, every trade is a trade of structured hierarchy: products, labor, privileges, burdens, market access, companies, countries, alliances, defense organizations and markets themselves can all be represented as hierarchy-bearing tradable objects.

## What is included

- 12 hierarchy levels, from Survival to Solar Apex.
- Solar System, Earth, Moon and Mars.
- Solar System UN, Earth UN, Moon UN and Mars UN.
- Defense organizations at solar and planetary level.
- Country alliances below defense organizations.
- Countries below alliances and planetary UN structures.
- Companies/employers below countries.
- Workers/employees with age curves, traits, occupations and mobility.
- Products with domain, status, stock and minimum entitlement level.
- Many markets across scopes, domains and hierarchy levels.
- Market-rights exchanges where markets themselves are traded as assets.
- Tradable privileges and tradable disadvantages/burdens.
- Automatic rise for strong economic and military actors.
- Manual status lift for helpers, care workers, educators, media and culture workers.
- Deep class inheritance with many levels, but ID-based relationships for large-run stability.

## Run examples

```bash
pypy3 solar_hierarchy_market_sim_pypy3.py --profile demo --ticks 2
pypy3 solar_hierarchy_market_sim_pypy3.py --profile large --ticks 5 --seed 42
pypy3 solar_hierarchy_market_sim_pypy3.py --profile huge --ticks 2 --json report.json
```

CPython also works:

```bash
python3 solar_hierarchy_market_sim_pypy3.py --profile demo --ticks 2 --json report.json
```

## Profiles

| Profile | Countries | Companies | Workers | Products | Markets |
|---|---:|---:|---:|---:|---:|
| demo | 15 | 100 | 1,500 | 700 | 1,125 |
| large | 102 | 1,600 | 30,000 | 12,000 | 1,125 |
| huge | 255 | 5,500 | 150,000 | 42,000 | 1,125 |

Markets are numerous because they are generated for several scopes, 25 domains and 12 hierarchy levels. Market-rights exchanges are also markets.

## CLI options

```text
--profile {demo,large,huge}
--ticks N
--seed N
--json PATH
--quiet
```

## Validation

This package was syntax-checked and run here with CPython because PyPy3 is not installed in this environment. The code is dependency-free and intentionally written for PyPy3 compatibility.

Included sample outputs:

- `solar_hierarchy_market_demo_output.txt`
- `solar_hierarchy_market_demo_report.json`
- `solar_hierarchy_market_large_tick1_output.txt`
