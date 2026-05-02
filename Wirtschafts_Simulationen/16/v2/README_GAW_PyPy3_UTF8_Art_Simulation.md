# GAW PyPy3 UTF-8 Art Simulation

This package contains the colourful terminal simulation of the **Gestapelte Arbeitsblock-Wirtschaft / Stacked Labour Block Economy**.

The UTF-8 art, section explanations, local unit definitions, calculations, summaries and possible outcome scenarios are printed directly to the terminal output.

## Start

```bash
pypy3 gaw_pypy3_simulation.py
```

English is the default output language.

```bash
pypy3 gaw_pypy3_simulation.py --lang en
pypy3 gaw_pypy3_simulation.py --lang de
```

German aliases are also available:

```bash
pypy3 gaw_pypy3_simulation.py --sprache de --szenario krise --perioden 8
```

## Scenarios

```bash
pypy3 gaw_pypy3_simulation.py --scenario normal
pypy3 gaw_pypy3_simulation.py --scenario crisis
pypy3 gaw_pypy3_simulation.py --scenario research
pypy3 gaw_pypy3_simulation.py --scenario house
```

German scenario aliases:

```bash
pypy3 gaw_pypy3_simulation.py --szenario krise
pypy3 gaw_pypy3_simulation.py --szenario forschung
pypy3 gaw_pypy3_simulation.py --szenario hausbau
```

## Parts

Run everything:

```bash
pypy3 gaw_pypy3_simulation.py --parts all
```

Short run:

```bash
pypy3 gaw_pypy3_simulation.py --parts short
```

Selected parts:

```bash
pypy3 gaw_pypy3_simulation.py --parts factors,work,market,summary
pypy3 gaw_pypy3_simulation.py --teile faktoren,arbeit,markt,schluss
```

Available canonical parts:

`factors, work, project, market, fund, credit, resources, damage, periods, verification, summary`

## Other useful options

```bash
pypy3 gaw_pypy3_simulation.py --periods 12 --seed 7
pypy3 gaw_pypy3_simulation.py --width 140
pypy3 gaw_pypy3_simulation.py --no-color
```

`--no-color` keeps the UTF-8 art but removes ANSI colour codes.
