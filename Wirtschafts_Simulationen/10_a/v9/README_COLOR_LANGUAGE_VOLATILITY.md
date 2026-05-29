# Planet Truth Paradigm Architecture — Color, Language, and Volatility Edition

This update adds the following features to the simulation script:

## New features

- **Very colorful UTF-8 terminal output** using ANSI colors
- **Entity-specific colors** in terminal output:
  - Countries
  - Companies
  - Households
  - Banks
  - Central banks
  - UN
  - Defense organizations
  - Currencies / WK / keywords / bars / sparklines
- **Language parameter**:
  - `--lang en` (default)
  - `--lang de`
- **Global volatility parameter**:
  - `--volatility`
- **Truth-currency volatility parameter** for the planetary truth currency WK:
  - `--truth-volatility`
- **Fiat-currency volatility parameter** for national numeric currencies:
  - `--fiat-volatility`
- **UTF-8 width safety margin** increased to **5 characters**
- `--print-art` is **enabled by default**
- `--no-print-art` disables only terminal art printing
- `--color` is **enabled by default**
- `--no-color` disables ANSI colors in terminal output

## Important command-line parameters

```bash
--lang en|de
--volatility FLOAT
--truth-volatility FLOAT
--fiat-volatility FLOAT
--color / --no-color
--print-art / --no-print-art
```

## Examples

### English, default colorful output

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --lang en \
  --out run_en
```

### German, no color, no stdout art

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --lang de \
  --no-color \
  --no-print-art \
  --out run_de
```

### Higher overall volatility

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset large \
  --months 240 \
  --workers auto \
  --volatility 1.8 \
  --truth-volatility 2.0 \
  --fiat-volatility 1.4 \
  --out run_volatile
```

### Lower volatility / more stable world

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py \
  --preset standard \
  --months 120 \
  --workers auto \
  --volatility 0.4 \
  --truth-volatility 0.3 \
  --fiat-volatility 0.5 \
  --out run_stable
```

## Notes

- **ANSI colors are used for terminal printing**.
- Files written to the output directory remain **plain text** without ANSI escape sequences.
- Language selection affects the written summary/report as well.
- Volatility works by applying broad stochastic perturbations to:
  - planetary truth layers,
  - fiat holdings,
  - debt,
  - routed message magnitudes,
  - event severity.

## Test runs created

- `/mnt/data/lang_en_test`
- `/mnt/data/lang_de_test`
- `/mnt/data/color_test`
