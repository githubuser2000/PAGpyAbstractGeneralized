# RWÖ / RCE Scalar Bridge UTF-8 Simulation

This package contains an extended PyPy3/Python 3 simulation of a **relational currency economy** in which the relational table can also be converted into a classical market-economy number.

The new conversion rule is:

```text
cell contribution = cell value × row factor × column factor
MEV = Σ(XIJ × RFA × CFA)
```

In German:

```text
Zellbeitrag = Zellenwert × Zeilenfaktor × Spaltenfaktor
MEV = Σ(XIJ × RFA × CFA)
```

## What changed in this version

- Adds simulation parts **15–24** on scalar conversion from relational table to classical market number.
- Keeps the earlier simulation parts **1–14**.
- Adds many more colorful Unicode / UTF-8 diagrams, heatmaps, funnels, waterfalls, dashboards, gate diagrams and scenario bars.
- Each UTF-8 art block has its own explanation above it:
  - what is simulated,
  - why it is simulated,
  - only the abbreviations that occur in that specific art block,
  - colored units used in that art block.
- Each UTF-8 art block has its own evaluation below it.
- Adds automatic terminal width detection and subtracts **5 characters** so output is less likely to wrap incorrectly.
- English is the default language. German can be selected with `--lang de`.

## Run

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py
```

If PyPy3 is not installed:

```bash
python3 rwoe_scalar_bridge_utf8_simulation.py
```

## Language

English is the default:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --lang en
```

German:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --lang de
```

## Select parts

Run only the new scalar bridge parts:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --parts 15-24
```

Run individual parts:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --parts 15,20,24
```

German alias:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --teile 15-24 --lang de
```

## Colors

Disable ANSI colors:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --no-color
```

## Width handling

By default the script detects the terminal width and subtracts 5 characters:

```text
layout_width = detected_terminal_width - 5
```

Manual override also subtracts 5 characters:

```bash
pypy3 rwoe_scalar_bridge_utf8_simulation.py --width 100
```

This renders with an internal width of 95.

## Main new abbreviations

Abbreviations are explained locally in the output only where they occur. Important new ones include:

- `XIJ`: cell value.
- `RFA`: row factor.
- `CFA`: column factor.
- `MEV`: market-equivalent value.
- `ILS`: information loss score.
- `DGR`: dignity risk score.
- `CNV`: convertibility score.
- `NBM`: numeric boom meter.

The output itself gives the detailed local explanation per diagram.
