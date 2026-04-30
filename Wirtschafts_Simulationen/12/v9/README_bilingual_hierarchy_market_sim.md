# Solar Hierarchy Market Simulation — bilingual output

This version adds runtime language selection for the PyPy-safe hierarchy-market simulation.

## Language parameter

Default output is English:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1
```

German output:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --lang de
```

Explicit English output:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --lang en
```

The parameter is:

```bash
--lang en|de
```

`en` is the default.

## What is translated

The runtime output now switches between English and German for:

- startup/build/tick reports
- global simulation explanation
- abbreviation explanations
- numeric summary headings
- metric labels
- top-list headings and column explanations
- entity display names where possible
- domain names
- body names: Earth, Moon, Mars, Solar System
- hierarchy level names L01–L12
- goods hierarchy text
- UTF-8 chart titles
- UTF-8 table headers
- chart explanations and interpretations
- final scenario summary
- group-specific mobility interpretations

The underlying internal IDs and JSON keys remain stable so existing tools can still parse reports. Display values inside JSON, such as level names, domains and body names, follow the selected language.

## PyPy-safe architecture

This is still the data-oriented safe version: large network/category/sheaf structures are simulated as aggregate metrics instead of huge live object graphs, so `large --ticks 2` avoids the previous PyPy segmentation-fault pattern.

Example stable large run:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 2 --lang de --quiet --no-visuals
```

## Included outputs

- `pypy_safe_lang_default_en_plain.txt` — default English output without `--lang`
- `pypy_safe_lang_en_plain.txt` — explicit English output
- `pypy_safe_lang_de_plain.txt` — German output without UTF-8 visuals
- `pypy_safe_lang_en_visual.txt` — English output with UTF-8 visuals
- `pypy_safe_lang_de_visual.txt` — German output with UTF-8 visuals
- `pypy_safe_lang_de_large_plain.txt` — large German test output
- JSON reports for English and German demo runs

