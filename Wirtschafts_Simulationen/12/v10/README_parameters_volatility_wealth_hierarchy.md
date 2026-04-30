# Solar Hierarchy Market Simulation — Parameters, Value Formula, Color Output

## Language

English is the default:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1
```

German:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --lang de
```

## New parameters

### `--volatility FLOAT`

Default: `1.0`

Controls how unstable the simulation is:

- macro-shock strength
- number of scenario events
- price noise
- trade intensity
- packet/queue/semaphore pressure
- speed and probability of hierarchy changes indirectly through status pressure

Examples:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --volatility 0.4
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --volatility 2.5
```

### `--wealth FLOAT`

Default: `1.0`

Scales initial endowments, wallets, productive elements and settlement flows.

Examples:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --wealth 0.6
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --wealth 2.0
```

### `--hierarchy-shift FLOAT`

Default: `1.0`

Controls how fast status differences become level changes.

- Low values make the hierarchy inert.
- High values make ascent and descent happen faster.

Examples:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --hierarchy-shift 0.4
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --hierarchy-shift 2.5
```

### Optional asymmetric controls

```bash
--up-shift FLOAT
--down-shift FLOAT
```

These multiply upward or downward movement separately.

Example:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py \
  --volatility 2.5 --wealth 1.8 --hierarchy-shift 2.2 --up-shift 1.4 --down-shift 0.8
```

## Color output

Color is enabled by default through ANSI escape codes.

Disable colors:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --no-color
```

Disable visual diagrams:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --no-visuals
```

## Value formula

A hierarchy bundle `B` contains amounts `x(l,e)` at hierarchy level `l` and hierarchy element `e`.

The compressed settlement value is:

```text
H(B) = Σ_l Σ_e x(l,e) · M_l · w_e
```

Where:

- `x(l,e)` is the raw amount of hierarchy element `e` at level `l`.
- `M_l` is the hierarchy height multiplier for level `l`.
- `w_e` is the element weight, for example labor, capital, trust, governance, market access, military, science, privilege or burden.

For an entity:

```text
Status_H = H(structure) + Wallet_H + 0.15 · Privilege_H − 0.15 · Burden_H
```

The entity's hierarchy level is then determined by comparing `Status_H` against the twelve level thresholds. The parameter `--hierarchy-shift` controls how quickly the entity moves toward the threshold-implied level.

## Seed 42

The seed is the deterministic starting value of the random generator.

`--seed 42` means:

- the run is reproducible,
- the same parameters produce the same results,
- it is not more correct or better than another seed,
- another seed produces different shocks, trades, winners and losers.

Without `--seed`, the program chooses a fresh seed from current time and process ID.

