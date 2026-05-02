# Universe Circular Economy Simulation v3

PyPy3-compatible, dependency-free simulation of the Universe/Cosmos Circular Economy.

This version changes the explanation behavior requested by the user:

- Detailed explanations are printed in the **terminal output**, not buried inside the Markdown report.
- Each printed calculation has three colored blocks:
  1. **BEFORE THE CALCULATION** — what is simulated, why this partial-cycle company exists, and what the abbreviations mean.
  2. **THE CALCULATION** — the raw arithmetic for `SG`, `UKE`, and `ESV`.
  3. **AFTER THE CALCULATION** — verification, minted money, unverified claims, tax, subsidy, debt and alternative possible outcomes.
- Every abbreviation receives a color badge in ANSI terminal output.
- Segment codes such as `FHV`, `RSO`, `DIG`, `CMP`, `LCI`, `VUL` also receive colored badges.
- Most companies only operate a part of the cycle, for example `5→7` or `15→19`.
- The Markdown report is now compact on purpose. It is an archive summary. The teaching output belongs to the console.

## Run with PyPy3

English is the default:

```bash
pypy3 universe_circular_economy_simulation_v3.py \
  --seed 7331 \
  --ticks 60 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 45 \
  --calculation-output sample \
  --calculation-limit 36 \
  --report-dir uce_report_v3
```

German output:

```bash
pypy3 universe_circular_economy_simulation_v3.py \
  --lang de \
  --seed 7331 \
  --ticks 60 \
  --systems 2 \
  --planets-per-system 3 \
  --companies-per-planet 45 \
  --calculation-output sample \
  --calculation-limit 36 \
  --report-dir uce_report_v3_de
```

Print every calculation, including before/formula/after blocks:

```bash
pypy3 universe_circular_economy_simulation_v3.py \
  --ticks 20 \
  --systems 1 \
  --planets-per-system 2 \
  --companies-per-planet 20 \
  --calculation-output all
```

For very large simulations, `--calculation-output all` can produce a huge terminal stream. Use `sample` for a readable representative stream.

## New parameters

```text
--lang {en,de}                 Output language. Default: en.
--calculation-output {none,sample,all}
                                none   = only summary
                                sample = colorful representative calculation stream
                                all    = every ledger calculation gets before/formula/after output
--calculation-limit N           Number of calculations printed in sample mode.
--no-color                      Disable ANSI color.
```

## Core formula

```text
SG = (REP_end - REP_start) * NCL + END - STA
UKE = SG / NCL
ESV = SG * MAT * QAL * USE * JUS
```

Control values:

```text
EarthType:  4→17 in pass 4 = 73 SG
VulcanType: 4→17 in pass 4 = 79 SG
```

## Generated files

```text
final_report.md        Compact archive summary; detailed explanations are in terminal output.
final_state.json       Machine-readable final state.
snapshots.csv          Planet time series.
ledger.csv             Full calculation ledger.
companies.csv          All companies and their partial segments.
trades.csv             Segment handoffs and trades.
identity_samples.csv   Sample identity passports.
```

The code uses only the Python standard library, so it is intended to run under PyPy3.
