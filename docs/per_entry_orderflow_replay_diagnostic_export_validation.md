# Per-entry Order Flow replay diagnostic export validation

## Scope

This document records validation results for the diagnostic-only per-entry Order Flow replay export.

The export is research-only and does not change:
- strategy execution
- risk behavior
- broker behavior
- paper trading
- live trading
- MT5 login
- Sierra live connection
- CME live data connection
- real order paths
- external API behavior

Generated report files remained under `private_data` and were not committed.

## Validation commands

The diagnostic export was run on the Sierra delayed 30-day matched datasets with:

- `--export-per-entry-orderflow-replay-diagnostic`
- `--backtest-max-iterations 200`
- `--profile apex`
- `--scenario bullish`

## Results

| Timeframe | A executed trades | A PnL | Non-neutral OF kept | Non-neutral OF PnL | Aligned OF kept | Aligned OF PnL | Missing snapshots |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1m | 18 | 20.00 | 1 | -10.00 | 0 | 0.00 | 0 |
| 5m | 38 | 270.00 | 8 | 95.00 | 3 | 45.00 | 0 |
| 10m | 46 | 15.00 | 11 | -35.00 | 6 | -35.00 | 0 |

## Interpretation

The diagnostic export matched the previous manual per-entry replay analysis.

The result confirms:
- per-entry replay snapshot matching works
- `window_end` index matching produced no missing snapshots for the 200-iteration validation runs
- the export correctly reports current A behavior, non-neutral replay snapshot behavior, and direction-aligned replay snapshot behavior

The result does not justify enforcing Order Flow confirmation:
- 1m aligned replay kept no trades
- 5m aligned replay kept only 3 trades
- 10m aligned replay produced negative PnL
- behavior is not stable across timeframes

## Decision

Do not enforce Order Flow confirmation.

Keep the per-entry Order Flow replay export as a diagnostic-only research tool.
