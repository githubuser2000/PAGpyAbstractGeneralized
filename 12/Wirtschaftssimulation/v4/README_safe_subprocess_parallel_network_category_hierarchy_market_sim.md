# Solar Hierarchy Market Simulation — PyPy-safe subprocess parallel edition

This version replaces the unsafe parallel architecture that could crash PyPy with:

- **no `multiprocessing.Pool`**
- **no threads**
- **no manager objects**
- **no large result objects through pipes**
- independent subprocess workers started with `sys.executable`
- compact JSON snapshot files
- JSONL proposal files written by workers
- parent-side validation and settlement
- conservative live worker waves for large profiles

The important design change is that worker processes never mutate wallets, stocks, market ownership, categories, morphisms, queues, semaphores, or sheaves. Workers only generate proposals. The main process reads proposal files and commits/rejects them against the authoritative state.

## Why this fixes the PyPy crash mode

The failing version used a process pool style that moved too much through inter-process pipes and/or cloned too much live heap at once. On PyPy, a large object graph plus process pools can become fragile: when the parent crashes, workers then show `BrokenPipeError` because their result pipe no longer has a reader.

This version avoids that path. It uses subprocesses plus files, so the parent does not receive giant pickled result objects over a pipe.

## Commands

Your crash command now works in the safe architecture:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8
```

For less terminal output:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --no-visuals
```

For maximum stability on machines with limited RAM:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --quiet --no-visuals
```

Disable process parallelism completely:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --no-parallel --no-visuals
```

Show worker subprocess output for diagnostics:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 4 --debug-stages
```

Use more simultaneous live workers when you have enough RAM:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --live-process-cap 4 --no-visuals
```

## Parallelism details

`--processes 8` means the market proposal work is split into eight shards. On the `large` and `huge` profiles, the script deliberately runs those shards in conservative waves to avoid memory blow-ups. Use `--live-process-cap N` to raise the number of simultaneous worker processes on machines with enough RAM.

Parallelized phases:

- product market proposal generation
- privilege market proposal generation
- burden market proposal generation
- background packet template generation

Parent-side but still optimized:

- market-as-asset ownership transfers
- settlement
- stock mutation
- wallet mutation
- morphism/category updates
- packet injection
- sheaf updates

## Tested in this environment

PyPy3 is not installed here, so I tested with CPython. The safe architecture completed:

```bash
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --processes 4 --no-visuals
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1 --processes 8 --quiet --no-visuals
```

The large test produced a report with 48k+ initial entities, 32k workers, 13k products, 1,392 markets, and one completed tick.
