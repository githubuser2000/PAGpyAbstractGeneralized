# Universe Circular Economy Simulation v4

PyPy3-compatible simulation of the Universe/Kosmos circular economy based on the 20-station EarthType loop and 22-station VulcanType loop.

This version moves the heavy explanation layer into the **terminal output**. The Markdown report remains compact, while the console becomes the colorful simulation cockpit.

## What changed in v4

- Repeated long explanations are capped. By default, one explanation or one multi-letter unit definition appears **at most twice**.
- Live numbers, formulas, company names, scenarios, colors and diagrams still appear as data; only repeated explanatory text is suppressed.
- Most companies remain **partial-cycle companies**, for example `GRO = 3→5`, `FHV = 5→7`, `DIG = 8→13`, `CMP = 13→16`, `RSO = 15→19`.
- Rare integrators still exist, but the economy is no longer modeled as if most companies controlled a full loop.
- The terminal output contains a very colorful UTF-8 simulation atlas.
- Each multi-letter unit has its own color badge.
- Each UTF-8 art panel contains:
  - what is being simulated,
  - why that part of the economy matters,
  - only the multi-letter units that actually occur in that panel,
  - a colorful UTF-8 diagram,
  - an evaluation below the diagram with multiple possible outcome scenarios.
- Default language is English. Use `--lang de` for German.

## Run in English

```bash
pypy3 universe_circular_economy_simulation_v4.py \
  --seed 7331 \
  --ticks 80 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 55 \
  --calculation-output sample \
  --calculation-limit 18 \
  --utf8-art-output all \
  --explanation-repeat-limit 2 \
  --report-dir uce_report_v4
```

## Run in German

```bash
pypy3 universe_circular_economy_simulation_v4.py \
  --lang de \
  --seed 7331 \
  --ticks 80 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 55 \
  --calculation-output sample \
  --calculation-limit 18 \
  --utf8-art-output all \
  --explanation-repeat-limit 2 \
  --report-dir uce_report_v4_de
```

## Important parameters

```text
--lang {en,de}
    Output language. Default: en.

--calculation-output {none,sample,all}
    none   = no individual calculation blocks
    sample = representative colored calculations
    all    = every ledger calculation with before/formula/after blocks

--calculation-limit N
    Number of calculation blocks in sample mode.

--art-output {none,sample,all}
--utf8-art-output {none,sample,all}
    Print no UTF-8 art, selected UTF-8 art panels, or all panels.
    Both parameter names are accepted.

--art-limit N
--utf8-art-limit N
    Number of UTF-8 art panels in sample mode.
    Both parameter names are accepted.

--explanation-repeat-limit N
    Maximum number of times the same explanation may appear.
    Default: 2.

--no-color
    Disable ANSI colors. The diagrams remain UTF-8, but without terminal color.
```

## Core formula checks

```text
EarthType  4→17 in pass 4 = 73 SG
VulcanType 4→17 in pass 4 = 79 SG
```

## Core formulas

```text
SG  = (REP_end - REP_start) * NCL + END - STA
UKE = SG / NCL
ESV = SG * MAT * QAL * USE * JUS
```

## Output files

The simulation writes:

```text
final_report.md        # compact summary
final_state.json       # final state of planets and budgets
snapshots.csv          # time series per planet
ledger.csv             # every loop calculation
companies.csv          # companies and partial-cycle segment licenses
trades.csv             # inter-company handoffs
identity_samples.csv   # sample identities with cycle-passport data
```

The large explanatory layer is in the terminal output, not in `final_report.md`.

## Viewing color output

ANSI color files are meant to be viewed in a terminal:

```bash
cat uce_demo_terminal_v4_de_ansi.txt
```

Many editors show the escape sequences literally. That is normal; the color appears when the file is printed by an ANSI-capable terminal.

## Runtime note

The script uses only the Python standard library. In the build environment, `pypy3` was not installed, so syntax checks and demo runs were executed with `python3`. The code is written to be PyPy3-compatible.
