# Order Flow Replay

Order Flow replay means processing footprint candles one by one and recording
how Order Flow Context changes over time.

This is CSV, research, and backtesting logic only. It does not connect to live
Sierra Chart data, CME, brokers, or any external API. It also does not create
trade signals or real orders.

## Why Replay Exists

A single final Order Flow Context can hide how the context changed along the
way. Replay keeps a step-by-step record so later reports, backtests, and review
tools can see the progression.

Each replay step stores:

- candle delta
- cumulative delta
- Delta/CVD direction
- Imbalance bias
- Absorption bias
- combined Order Flow bias
- combined confidence
- reasons and blocking reasons

## Candle-by-Candle Processing

For each candle, the replay engine uses all candles from the start through the
current candle for Delta/CVD. This lets cumulative delta grow through the replay.

Imbalance and Absorption are checked only on the current candle because those
patterns describe the current footprint candle's price levels and candle shape.

The engine then combines Delta/CVD, Imbalance, and Absorption into one
Order Flow Context snapshot for that step.

## Data Quality

By default, replay runs `OrderFlowDataQualityChecker` before processing candles.

If quality is `PASSED` or `WARNING`, replay can continue. If quality is
`FAILED`, `EMPTY`, or `INVALID`, replay stops safely and returns a failed result
with blocking reasons.

## CSV Replay

`OrderFlowReplayEngine.replay_csv()` loads a CSV with `SierraChartImporter` and
then runs the same replay logic.

The CSV must include fields that resolve to:

- `time`
- `open`
- `high`
- `low`
- `close`
- `price`
- `bid_volume`
- `ask_volume`

## Future Plan

Replay output can later connect to:

- backtest reports
- Order Flow research dashboards
- AI coach review
- comparison between SMC, CRT, and Order Flow context over time

For v1, replay stays standalone and is not integrated into `PaperTradingFlow`.
