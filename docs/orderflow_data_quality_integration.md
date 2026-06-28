# Order Flow Data Quality Integration

`main.py` now checks footprint CSV quality before it builds Order Flow Context.
This protects the demo and backtest flow from using bad CSV data as if it were
reliable market context.

## Why CSV Data Is Checked First

Order Flow analyzers depend on price levels, bid volume, and ask volume. If the
CSV is empty, malformed, missing levels, or full of invalid values, the
resulting Delta/CVD, Imbalance, and Absorption readings can become misleading.

Bad data should not enter AI decision logic. In v1, the quality gate blocks only
Order Flow Context. It does not crash the app and it does not block the rest of
the paper-trading demo from running safely.

## Status Behavior

- `PASSED`: The CSV data is clean. Order Flow Context can become active.
- `WARNING`: Minor invalid levels were found, but the data is still acceptable.
  Order Flow Context can become active.
- `FAILED`: Quality rules were violated. Order Flow Context stays inactive.
- `EMPTY`: No usable footprint candles were imported. Order Flow Context stays
  inactive.
- `INVALID`: The CSV path or input was unusable. Order Flow Context stays
  inactive.

## Output

When `--orderflow-csv` is provided, the CLI prints an `Order Flow Data Quality`
section with:

- Status
- Passed
- Candle count
- Total levels
- Invalid levels
- Invalid level ratio
- Reasons
- Blocking reasons

If decision tracing is enabled, the Order Flow trace step also includes simple
fields such as `orderflow_data_quality_status`,
`orderflow_data_quality_passed`, and
`orderflow_data_quality_blocking_reasons`.

## Future Plan

The next step is to validate real Sierra Chart exported footprint CSV files with
this same gate before they enter `PaperTradingFlow`. Failed quality should keep
Order Flow as `UNKNOWN` so bad exported data cannot influence SMC + CRT
alignment.
