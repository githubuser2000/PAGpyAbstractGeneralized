# Changelog V6 — English Edition

V6 keeps the V5 economic mechanics and dashboard panels, but converts the package to English.

## Changed

- Converted all user-visible script output from German to English.
- Converted dashboard panel titles, labels, explanatory text, and legends to English.
- Converted documentation to English.
- Converted buy/sell dashboard markers from `K/V` to `B/S`.
- Renamed the dashboard title to `V6 EXTREME UTF-8/ANSI Dashboard — Vector currency: value × goodness × popularity`.

## Preserved

- PyPy3-compatible, standard-library-only architecture.
- Terminal width detection and safe wrapping at terminal width minus five characters.
- Dense UTF-8/ANSI art dashboard mode.
- Multiple countries, governments, peoples, markets, firms, banks, central banks, funds, rating agencies, courts, supply chains, externalities, fraud, crises, and triadic exchange.
- CSV, JSON, and event-log output.

## Verification performed here

- `python3 -m py_compile vector_currency_sim.py`
- short demo run with plain UTF-8 dashboard output
- short demo run with ANSI-color dashboard output
- search for common German words in the main script and generated demo outputs
