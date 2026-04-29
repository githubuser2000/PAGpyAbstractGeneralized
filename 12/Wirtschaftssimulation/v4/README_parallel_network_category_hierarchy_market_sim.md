# Solar Hierarchy Market Simulation — Process-Parallel Network/Category Version

This is a PyPy3-compatible, dependency-free simulation of a Solar-System hierarchy-currency economy with network, queue, duplex, semaphore, topology, category, functor, natural transformation, presheaf, and sheaf structures.

## Parallelization model

This version parallelizes the market-heavy parts with **multiprocessing processes**, not threads.

The central design is a deterministic proposal/merge pipeline:

1. The main process builds one compact per-tick snapshot of actors, wallets, entitlements, products, markets, market-rights exchanges, UN/defense organizations, and routing endpoints.
2. A process pool is forked once per tick.
3. Worker processes generate transaction proposals in parallel.
4. The main process merges proposals sequentially, revalidates wallets/access/current ownership/current stock, settles hierarchy-currency transfers, and mutates canonical state.

This avoids corrupting wallets, product stock, market ownership, categories, and queues while still pushing the expensive random market-search and candidate-generation work into separate processes.

## Parallelized phases

The following phases use worker processes when `--processes` is greater than 1 and `--no-parallel` is not set:

- product market exchange
- market-rights / market-asset exchange
- privilege market exchange
- burden/disadvantage market exchange
- background network packet template generation
- worker-level refresh for larger profiles

The process pool is reused across all market phases in a tick, so the script avoids repeatedly forking a large process tree.

## Race-condition control

Worker processes never directly mutate shared economic state. They only return proposals. The main process rechecks every accepted proposal against current state before applying it.

That means parallel workers can speculate aggressively without causing negative wallets, double-sold products, invalid market ownership, or broken category objects.

## Fast packet injection

Full graph routing is still used where appropriate, but massive parallel background traffic and parallel trade packets use a cheaper local-hop packet injection path. This keeps the network pressure visible through queues, duplex channels, and semaphores without making BFS route search dominate the simulation.

## Useful commands

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 4
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 4 --no-visuals
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile huge --ticks 1 --processes 8 --json report.json --no-visuals
```

Disable parallel execution:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --no-parallel
```

Show per-stage timing diagnostics:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 4 --debug-stages --no-visuals
```

Disable UTF-8 diagrams:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --no-visuals
```

## New CLI flags

- `--processes N`: number of worker processes; `0` means automatic by profile.
- `--no-parallel`: force serial execution.
- `--debug-stages`: print timing for every major tick phase.
- `--no-visuals`: suppress UTF-8 dashboards.

## Validation performed here

PyPy3 is not installed in this environment, so validation was done with CPython using only the standard library. The script is written to remain PyPy3-compatible.

Validated runs:

```bash
python3 -m py_compile solar_hierarchy_market_network_category_sim_pypy3.py
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 4
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 4 --no-visuals
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 4 --quiet --no-visuals
```

The large validation run completed in about 23 seconds in this container and used roughly 1.06 GB RSS under CPython.
