# GAW PyPy3 UTF-8 Art Simulation

This is a very colourful terminal simulation of the **Stacked Labour-Block Economy** / **Gestapelte Arbeitsblock-Wirtschaft**.

The UTF-8 art is printed directly in the program output. No separate art file is used.

## Start

```bash
pypy3 gaw_pypy3_simulation.py
```

English is the default language.

## Language

```bash
pypy3 gaw_pypy3_simulation.py --language en
pypy3 gaw_pypy3_simulation.py --language de
```

German aliases also work:

```bash
pypy3 gaw_pypy3_simulation.py --sprache de
```

## Scenarios

```bash
pypy3 gaw_pypy3_simulation.py --scenario normal
pypy3 gaw_pypy3_simulation.py --scenario crisis
pypy3 gaw_pypy3_simulation.py --scenario research
pypy3 gaw_pypy3_simulation.py --scenario house
```

German aliases:

```bash
pypy3 gaw_pypy3_simulation.py --szenario krise
pypy3 gaw_pypy3_simulation.py --szenario forschung
pypy3 gaw_pypy3_simulation.py --szenario hausbau
```

## Parts

```bash
pypy3 gaw_pypy3_simulation.py --parts all
pypy3 gaw_pypy3_simulation.py --parts short
pypy3 gaw_pypy3_simulation.py --parts factors,work,market,summary
```

German aliases:

```bash
pypy3 gaw_pypy3_simulation.py --teile alle
pypy3 gaw_pypy3_simulation.py --teile kurz
pypy3 gaw_pypy3_simulation.py --teile faktoren,arbeit,markt,zusammenfassung
```

Available canonical parts:

```text
factors, work, project, market, fund, credit, resources, damage, periods, verification, summary
```

## Other options

```bash
pypy3 gaw_pypy3_simulation.py --periods 8 --seed 7
pypy3 gaw_pypy3_simulation.py --width 140
pypy3 gaw_pypy3_simulation.py --no-color
```

The script uses only the Python standard library and is intended to run with PyPy3. It was syntax-checked and executed with Python 3 in this environment.
