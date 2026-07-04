# Per-entry Order Flow replay diagnostic implementation plan

## Scope

This plan is diagnostic-only.

No strategy rule will be changed.
No risk rule will be changed.
No live trading, paper trading, broker connection, Sierra Chart live connection, CME data connection, external API, or real order is approved.

## Current confirmed behavior

The current bulk Order Flow A/B diagnostic uses `BacktestIterationTrace.orderflow_status`.

That field is built from the `ORDER_FLOW_CONTEXT` trace step in `PaperTradingFlow`.

`PaperTradingFlow` receives only one `orderflow_context_result` per backtest run.

In CLI backtests, that context comes from `_build_orderflow_context_from_csv()`.

The current CSV builder creates a global/latest Order Flow context:

- Delta/CVD is analyzed over the whole imported footprint CSV.
- Imbalance is analyzed only on the latest footprint candle.
- Absorption is analyzed only on the latest footprint candle.

Therefore the current A/B report is not a per-entry Order Flow diagnostic.

## Why a new diagnostic is needed

Post future-exit-fix results showed that enforcing the current global/latest Order Flow confirmation would block every executed trade.

Per-entry replay snapshot diagnostics showed more nuanced behavior:

| Timeframe | Current executed | Current PnL | Non-neutral kept | Non-neutral PnL | Aligned kept | Aligned PnL |
|---|---:|---:|---:|---:|---:|---:|
| 1m | 18 | +20.00 | 1 | -10.00 | 0 | 0.00 |
| 5m | 38 | +270.00 | 8 | +95.00 | 3 | +45.00 |
| 10m | 46 | +15.00 | 11 | -35.00 | 6 | -35.00 |

This confirms that per-entry replay snapshots are useful for research, but not stable enough for enforcement.

## Proposed diagnostic-only implementation

Add a new export path rather than changing existing trade execution.

Suggested CLI flag:

- `--export-per-entry-orderflow-replay-diagnostic`

Suggested optional arguments:

- `--per-entry-orderflow-report-dir`
- `--per-entry-orderflow-min-confidence`
- `--per-entry-orderflow-window-mode`

Suggested output files:

- `per_entry_orderflow_replay_diagnostic.json`
- `per_entry_orderflow_replay_diagnostic.txt`

## Required inputs

The diagnostic needs:

- backtest market CSV
- footprint CSV
- backtest iteration traces
- executed trade window_start/window_end
- final_action
- outcome
- simulated_pnl

## First implementation design

Keep it report-only.

Steps:

1. Run the normal backtest with `collect_iteration_traces=True`.
2. Load the footprint CSV through `SierraChartImporter`.
3. Replay only up to the maximum executed trade `window_end`.
4. Build `steps_by_index` from replay step index.
5. For each executed trade:
   - match `step = steps_by_index[window_end]`
   - record action, outcome, pnl
   - record replay orderflow_bias, confidence, delta_direction, imbalance_bias, absorption_bias
6. Compute diagnostic-only simulations:
   - current A behavior
   - non-neutral Order Flow only
   - direction-aligned Order Flow only
7. Export JSON and TXT reports.

## Important constraints

Do not modify:

- trade execution
- DecisionEngine
- PaperTradingFlow execution logic
- risk rules
- broker behavior
- live/paper trading behavior

This must remain an offline report/export only.

## Known performance caution

`OrderFlowReplayEngine` currently re-analyzes `candles_so_far` at every step.

Full 1m replay over 25,000+ candles can be slow.

The first implementation should limit replay to the maximum needed executed `window_end`.

A later optimization may be needed for full-dataset replay.

## Open design question

The first diagnostic can match replay snapshot by `window_end` index.

A later, more accurate design may need timestamp matching between market candles and footprint candles instead of assuming index alignment.

That should be validated before any enforcement is considered.

## Decision

Do not enforce Order Flow confirmation.

Implement only a per-entry replay diagnostic export if code changes are made later.
