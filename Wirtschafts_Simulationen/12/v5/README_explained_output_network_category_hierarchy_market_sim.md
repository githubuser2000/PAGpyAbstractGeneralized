# Solar Hierarchy Market Simulation — Explained Output Edition

This is the safe subprocess-parallel PyPy3 simulation of a solar hierarchy-currency market economy, now with an expanded runtime explanation layer.

The explanations are part of the **script output**, not just comments in the source. The simulation prints explanatory text before and after its numeric reports and UTF-8 visual artifacts.

## What was added

At the beginning of the simulation output:

- a full explanation of what the simulation is modeling
- the goal of the model
- the meaning of hierarchy as currency
- a glossary for `H`, `L01`–`L12`, `entity`, `node`, `channel`, `FIFO`, `LIFO`, `half-duplex`, `full-duplex`, `semaphore`, `morphism`, `hom-set`, `functor`, `NT`, `presheaf`, `sheaf`, `AB`, `BA`, `Fly`, `Block`, and `p/m`

Around every numeric output block:

- explanation above the block
- the numeric data itself
- interpretation below the block

Covered numeric blocks include:

- build start
- build report
- tick report
- metadata
- counts
- trade
- network
- parallel subprocess metrics
- category metrics
- level distributions
- top countries
- top companies
- top markets
- top workers
- recent trades / morphism events

Around every UTF-8 visual artifact:

- explanation above the artifact
- the individual UTF-8 chart/table/tree/heatmap itself
- interpretation below the artifact

The script now wraps individual visual artifacts, not only whole visual groups. For example, worker levels, company levels, country levels, product levels, market levels, body × level heatmaps, network histograms, category tables, sheaf tables, market domain diagrams, and safe subprocess parallelism diagrams all receive their own explanation and evaluation.

At the end of the simulation output:

- a balanced scenario summary explaining several possible random outcomes caused by different seeds
- concentration scenario
- federated balancing scenario
- infrastructure bottleneck scenario
- sheaf coherence / fragmentation scenario
- manual-lift correction scenario

## Run examples

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 2
```

Without UTF-8 visuals but still with explanations around numeric blocks:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 2 --no-visuals
```

Large profile, stable subprocess architecture:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --quiet --no-visuals
```

More conservative memory behavior:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --live-process-cap 1 --quiet --no-visuals
```

## Notes

The implementation still uses subprocesses rather than threads. Worker processes generate proposals through files; the parent process validates and commits all authoritative state changes.

The demo files were generated with CPython in this environment because PyPy3 is not installed here. The script is standard-library-only and designed for PyPy3 execution.
