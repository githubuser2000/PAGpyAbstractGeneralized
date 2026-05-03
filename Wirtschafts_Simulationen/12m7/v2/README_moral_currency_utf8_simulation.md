# Radial-hierarchical moral currency simulation

This package contains a PyPy3-compatible, standard-library-only terminal simulation of a radial-hierarchical moral currency / value-vector market layer.

The simulation is intentionally colorful. It uses ANSI colors, UTF-8 diagrams, heat maps, ladders, funnels, timelines, sparklines, allocation strips and tables. Each simulation part prints:

1. what is being simulated,
2. why it is being simulated,
3. only the abbreviations used in that exact part,
4. only the units used in that exact part,
5. the simulation result,
6. an evaluation across multiple possible starting scenarios.

## Run

Default output is English:

```bash
pypy3 moral_currency_utf8_simulation_pypy3.py
```

German output:

```bash
pypy3 moral_currency_utf8_simulation_pypy3.py --lang de
```

A reproducible colorful run:

```bash
pypy3 moral_currency_utf8_simulation_pypy3.py --lang en --seed 17 --ticks 8 --color always
```

If PyPy3 is not installed, the script also runs with Python 3:

```bash
python3 moral_currency_utf8_simulation_pypy3.py --lang de --seed 17 --ticks 6
```

## Parameters

- `--lang en` or `--lang de` chooses the output language. The default is `en`.
- `--seed N` sets the random seed for reproducible runs.
- `--ticks N` sets the number of dynamic simulation steps.
- `--compact` keeps all simulation parts but shortens some tables.
- `--color always|auto|never` controls ANSI colors. The default is `always`.
- `--no-animation` disables tiny pauses between simulation parts.

## Files

- `moral_currency_utf8_simulation_pypy3.py` — main simulation script.
- `moral_currency_utf8_simulation_example_en_color.ansi` — complete English sample output with ANSI colors.
- `moral_currency_utf8_simulation_example_en_text.txt` — complete English sample output without ANSI color codes.
- `moral_currency_utf8_simulation_beispiel_de_farbig.ansi` — complete German sample output with ANSI colors.
- `moral_currency_utf8_simulation_beispiel_de_text.txt` — complete German sample output without ANSI color codes.

## Hinweise auf Deutsch

Die Standardsprache ist Englisch. Für Deutsch nutze:

```bash
pypy3 moral_currency_utf8_simulation_pypy3.py --lang de
```

Die farbigen `.ansi`-Dateien lassen sich in einem Terminal mit ANSI-Unterstützung anzeigen:

```bash
less -R moral_currency_utf8_simulation_beispiel_de_farbig.ansi
```
