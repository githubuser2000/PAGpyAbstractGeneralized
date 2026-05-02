# Universe Circular Economy Simulation v2

PyPy3-compatible simulation of a universe/cosmos economy based on the stacked `for`-loop currency.

This version adds the requested specialization rule: **most companies only operate a partial cycle segment** such as `5→7` or `15→19`. Rare integrators can close longer loops.

## Run

Default language is English:

```bash
pypy3 universe_circular_economy_simulation_v2.py \
  --seed 7331 \
  --ticks 60 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 45 \
  --report-dir uce_report_v2
```

German report and console output:

```bash
pypy3 universe_circular_economy_simulation_v2.py \
  --lang de \
  --seed 7331 \
  --ticks 60 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 45 \
  --report-dir uce_report_v2_de
```

## Key parameters

| Parameter | Meaning |
|---|---|
| `--lang {en,de}` | Output language. Default: `en`. |
| `--ticks` | Number of simulation ticks. |
| `--universes` | Number of universes inside the cosmos. |
| `--systems` | Star systems per universe. |
| `--planets-per-system` | Planets per star system. |
| `--companies-per-planet` | Companies per planet. Most become partial-cycle companies. |
| `--explain-limit` | Number of individual ledger calculations explained in the Markdown report. |
| `--report-dir` | Output directory for report files. |
| `--no-color` | Disable ANSI colors in console output. Markdown remains colorful. |

## Outputs

The report directory contains:

| File | Meaning |
|---|---|
| `final_report.md` | Colorful Markdown report with explanations above every evaluation section. |
| `final_state.json` | Full structured final state. |
| `snapshots.csv` | Tick-by-tick planet metrics. |
| `ledger.csv` | Every SG calculation with formula, outcome and explanations in English/German. |
| `companies.csv` | All companies with segments, money, debt, fairness and reputation. |
| `trades.csv` | Local segment handoffs between companies. |
| `identity_samples.csv` | Large remaining identities with cycle passports. |

## Segment examples

| Segment | Span | Meaning |
|---|---:|---|
| `FHV` | `5→7` | Fertilizer-to-harvest company. |
| `RSO` | `15→19` | Decomposition-to-soil company. |
| `DIG` | `8→13` | Eating-to-slurry company. |
| `CMP` | `13→17` | Compost-to-reintegration company. |
| `LCI` | `17→1` | Rare loop-closure integrator. |
| `FUL` | `1→20` | Rare full Earth-cycle company. |
| `FUV` | `1→22` | Rare full Vulcan-cycle company. |

## Currency formula

```text
SG_raw = (REP_end - REP_start) * NCL + END - STA
UKE = SG_raw / NCL
ESV = SG_raw * MAT * QAL * USE * JUS
VSG = ESV if verified else 0
USG = ESV if not verified else 0
CLD = damage/open-loop cost
NCL(EarthType)=20
NCL(VulcanType)=22
```

Formula checks included in console output:

```text
EarthType 4→17 pass 4 = 73 SG
VulcanType 4→17 pass 4 = 79 SG
```

## Notes

The script uses only the Python standard library. It is written for PyPy3 but was also test-run with CPython 3 in this environment.
