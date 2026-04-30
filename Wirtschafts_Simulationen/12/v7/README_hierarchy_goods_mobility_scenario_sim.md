# Solar Hierarchy Market Simulation — Goods, Mobility, Scenario Diversity

This version extends the hierarchy-currency economy simulation with four major additions:

1. **What else can still be simulated**
   - The runtime output now includes a large list of additional future simulation dimensions.

2. **12-level hierarchy of goods**
   - Every hierarchy level `L01` to `L12` now has a concrete set of example goods, rights and access bundles.
   - The output includes multiple UTF-8 diagrams for the goods hierarchy.

3. **Career mobility**
   - Workers, companies, countries and alliances can rise or fall relative to their initial hierarchy levels.
   - The output includes numeric mobility summaries plus multiple UTF-8 mobility diagrams.

4. **More diverse outcomes across runs**
   - Each tick can trigger multiple macro-scenario shocks such as:
     - resource boom
     - research breakthrough
     - media polarization
     - defense alert
     - governance reform
     - supply shock
     - care recognition
     - interplanetary expansion
   - These shocks affect different populations and domains, producing more varied outcomes between runs.

## New output design

The script now prints:

- a global explanation at the start,
- a list of what can still be simulated,
- explanation of abbreviations,
- explanation blocks before numeric output,
- interpretation blocks after numeric output,
- explanation blocks before each UTF-8 table/diagram,
- interpretation blocks after each UTF-8 table/diagram,
- a final balanced scenario summary,
- group-specific mobility interpretations.

## Main file

- `solar_hierarchy_market_network_category_sim_pypy3.py`

## Example usage

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --no-visuals
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 3 --seed 123
```

## Files included here

- updated simulation script
- demo output with visuals
- demo output without visuals
- demo JSON report

