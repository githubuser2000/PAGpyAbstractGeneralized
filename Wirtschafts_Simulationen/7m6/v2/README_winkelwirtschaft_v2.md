# Winkelwirtschaft / Angular Vector-Currency Economy v2

This package contains a PyPy3-compatible terminal simulation of the angular vector-currency economy.

Core rule: `EA`, `EB` and `EC` are three competing Euro vectors. Their vector length remains identical: `|€⃗| = 1 VE`. They compete by angle, not by numerical exchange-rate length.

## Run

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py
```

English is the default output language:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --lang en
```

German output:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --lang de
```

Readable short demo:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --ticks 2 --detail short --width 100
```

Disable ANSI colors:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --no-color
```

German aliases also work:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --lang de --detail kurz --ohne-farbe
```

## Scenarios

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario resonance
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario power
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario wellbeing
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario fragmented
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario scarcity
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --scenario tradeboom
```

The final UTF-8 art gallery is enabled by default. It can be disabled with:

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py --no-utf8-gallery
```

## Exports

```bash
pypy3 winkelwirtschaft_simulation_pypy3_v2_utf8.py \
  --export-csv history.csv \
  --export-currencies-csv currencies.csv \
  --export-md report.md
```
