# UTF-8 Explained Color Units Edition

This version adds a narrated layer around every UTF-8 artifact printed by the simulation.

## What changed

Every UTF-8 art block, diagram, table, heatmap, sparkline, and network panel is now wrapped like this:

1. **Long explanation before the graphic**
   - what is being simulated,
   - why this part of the model exists,
   - how to read the symbols,
   - how entities/units are colored,
   - what each unit type means in the economy.

2. **The actual UTF-8 graphic**

3. **Result evaluation after the graphic**
   - what the simulation found,
   - how to interpret the result,
   - what consequences follow for the simulated planet.

## Languages

The output language is controlled with:

```bash
--lang en
--lang de
```

Default is English.

## Colors

Terminal color output is enabled by default:

```bash
--color
```

Disable it with:

```bash
--no-color
```

Color semantics:

- Countries have their own color.
- Companies have their own color.
- Households have their own color.
- Banks have their own color.
- Central banks have their own color.
- UN-like institutions have their own color.
- Defense organizations have their own color.
- WK, fiat currencies, keywords, bars, sparklines, positive and negative values are highlighted separately.

Output files remain plain UTF-8 text by default. Colors are for terminal printing.

## Example commands

English, colored terminal output:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --lang en \
  --out run_en_explained
```

German, no color, no stdout art:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --lang de \
  --no-color \
  --no-print-art \
  --out run_de_explained
```

## Test outputs included

- `utf8_explained_test_en/summary.txt`
- `utf8_explained_test_en/utf8_paradigm_architecture_report.txt`
- `utf8_explained_test_de/summary.txt`
- `utf8_explained_test_de/utf8_paradigm_architecture_report.txt`
