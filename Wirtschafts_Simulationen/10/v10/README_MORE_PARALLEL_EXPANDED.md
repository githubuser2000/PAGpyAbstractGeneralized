# Planet Truth Paradigm Architecture — More Parallel Edition

This version broadens process-based parallelism for PyPy3 / CPython multiprocessing.
It still uses **processes, not threads**.

## Main parallelization changes

The simulation now parallelizes more phases:

- agent monthly aging / debt interest / truth decay
- company production and trade intent generation, now with batch workers
- credit-market bank intent generation, now with batch workers
- labor-market wage and truth effects, now with batch workers
- network channel ticks and message delivery batches
- topology construction for all major networks
- country tax-assessment preparation
- public-goods spending by countries
- central-bank policy reactions
- defense-organization decision generation
- sheaf / presheaf section assignment
- functor mapping of economic morphisms
- naturality-gap evaluation
- planetary GDP and truth-vector aggregation
- agent CSV export
- morphism CSV export

The directly mutating transaction-application phase remains controlled and mostly serial, because multiple transactions can touch the same agents, banks, countries, and categories. That is intentional: parallelizing those writes without conflict management would corrupt simulation state.

## More aggressive defaults

Worker caps were increased:

```text
tiny     up to 4 workers
standard up to 8 workers
large    up to 16 workers
epic     up to 32 workers
```

The default process threshold was lowered:

```text
--parallel-min-items 16
```

This means the simulation enters process parallelism earlier and more often.

## Still available

This file also keeps the newer output controls:

```text
--lang en|de
--color / --no-color
--print-art / --no-print-art
--volatility FLOAT
--truth-volatility FLOAT
--fiat-volatility FLOAT
--workers auto|N
```

## Recommended commands

### Large PyPy3 run

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset large \
  --months 240 \
  --workers auto \
  --out run_large_parallel
```

### Epic run with explicit workers

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset epic \
  --months 720 \
  --workers 24 \
  --parallel-min-items 16 \
  --out run_epic_parallel
```

### Quiet benchmark-style run

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --no-print-art \
  --no-color \
  --out run_standard_parallel
```

## Test runs included

- `more_parallel_full_test`: tiny, 3 months, 2 workers
- `more_parallel_full_standard`: standard, 1 month, 4 workers

Both compiled and ran successfully.
