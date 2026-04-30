# PyPy-safe Solar Hierarchy Market Simulation

This version replaces the old heavy live graph with a **data-oriented PyPy-safe architecture**.

The previous build materialized many network nodes, queues, packet objects, morphisms and category objects at once. Under PyPy, the build could succeed but the tick phase could still segfault because the heap was too dense and mutable. This version keeps the economic simulation large but represents network/category/sheaf structures as compact aggregate state instead of a huge recursive object graph.

## Main command

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 2
```

Low-output version:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 2 --quiet --no-visuals
```

Reproducible run:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 2 --seed 42
```

If `--seed` is omitted, the script chooses a fresh seed, so different calls can produce different scenario outcomes.

## What is simulated

- Solar System economy with Earth, Moon and Mars
- UN-like organizations
- defense organizations
- defense alliances
- countries
- companies
- workers
- products
- tradable markets
- privileges and burdens
- market ownership transfer
- hierarchy-currency settlement values
- 12 hierarchy levels
- 12-level goods entitlement hierarchy
- career ascent/descent for workers, companies, countries and alliances
- stochastic macro-scenarios such as defense alerts, care recognition, supply shocks, resource booms and research breakthroughs
- aggregate network, queue, duplex, semaphore, category, functor, natural transformation and sheaf metrics

## Why this should avoid the PyPy segfault

The script no longer mutates a huge live graph of packet/morphism/channel objects during ticks. Large profile still has about 48k entities, but network/category/sheaf systems are represented through aggregate counts and compact statistics.

## Output structure

The runtime output includes:

- global explanation
- list of what else can still be simulated
- abbreviation glossary
- explained numeric summary blocks
- top countries, companies, alliances, markets and workers
- UTF-8 tables and diagrams with explanation before and interpretation after each artifact
- final scenario summary
- group-specific mobility interpretation

