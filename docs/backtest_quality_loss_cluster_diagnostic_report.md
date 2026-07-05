# Backtest Quality Loss Cluster Diagnostic Report

## Safety scope

This is a research-only diagnostic report.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated source reports remain under ignored `private_data`.

## Source

Source diagnostic JSON:

`private_data/sierra_chart/bulk_30d_sc_delayed/per_entry_orderflow_5m_bullish_full_incremental/per_entry_orderflow_replay_diagnostic.json`

## Full 5m executed-trade summary

- Executed trades: 188.
- Wins: 79.
- Losses: 109.
- A current PnL: 95.00.
- Non-neutral replay snapshot PnL: -5.00.
- Direction-aligned replay snapshot PnL: -20.00.
- Replay snapshots found: 188.
- Missing replay snapshots: 0.

## Outcome by action side

| Action | Wins | Losses | PnL |
|---|---:|---:|---:|
| BUY | 18 | 48 | -210.00 |
| SELL | 61 | 61 | 305.00 |

## Outcome by replay Order Flow bias

| Replay Order Flow bias | Wins | Losses | PnL |
|---|---:|---:|---:|
| BEARISH | 7 | 11 | -5.00 |
| BULLISH | 4 | 6 | 0.00 |
| NEUTRAL | 68 | 92 | 100.00 |

## Largest nearby-loss clusters

Losses are grouped when the next losing trade is within five backtest iterations of the previous losing trade.

| Iteration range | Time range | Losses | PnL | Actions | Replay Order Flow | Aligned losses |
|---|---|---:|---:|---|---|---:|
| 910-931 | 2026-07-01  07:40:00 to 2026-07-01  20:55:00 | 16 | -160.00 | BUY:10, SELL:6 | BEARISH:2, NEUTRAL:14 | 0 |
| 675-687 | 2026-06-24  07:15:00 to 2026-06-24  12:15:00 | 8 | -80.00 | SELL:8 | BEARISH:1, NEUTRAL:7 | 1 |
| 364-371 | 2026-06-15  18:10:00 to 2026-06-15  21:05:00 | 7 | -70.00 | SELL:7 | NEUTRAL:7 | 0 |
| 726-736 | 2026-06-25  09:00:00 to 2026-06-25  13:10:00 | 7 | -70.00 | BUY:7 | BULLISH:1, NEUTRAL:6 | 1 |
| 219-230 | 2026-06-10  11:45:00 to 2026-06-10  20:50:00 | 6 | -60.00 | SELL:6 | BEARISH:3, NEUTRAL:3 | 3 |
| 272-279 | 2026-06-11  18:50:00 to 2026-06-11  21:45:00 | 6 | -60.00 | BUY:6 | NEUTRAL:6 | 0 |
| 450-459 | 2026-06-17  10:30:00 to 2026-06-17  18:45:00 | 6 | -60.00 | BUY:4, SELL:2 | BULLISH:1, NEUTRAL:5 | 1 |
| 489-494 | 2026-06-18  07:15:00 to 2026-06-18  09:20:00 | 6 | -60.00 | SELL:6 | NEUTRAL:6 | 0 |
| 76-81 | 2026-06-05  10:40:00 to 2026-06-05  12:45:00 | 4 | -40.00 | SELL:4 | NEUTRAL:4 | 0 |
| 776-782 | 2026-06-26  10:20:00 to 2026-06-26  12:50:00 | 4 | -40.00 | BUY:4 | BEARISH:1, NEUTRAL:3 | 0 |
| 25-31 | 2026-06-04  08:55:00 to 2026-06-04  11:25:00 | 3 | -30.00 | BUY:2, SELL:1 | NEUTRAL:3 | 0 |
| 355-358 | 2026-06-15  09:55:00 to 2026-06-15  11:10:00 | 3 | -30.00 | BUY:3 | NEUTRAL:3 | 0 |

## Main finding

The largest nearby-loss cluster is iterations 910-931, with 16 losses and -160.00 PnL.

This cluster is mostly replay Order Flow NEUTRAL, and it has zero direction-aligned Order Flow losses. That means Order Flow enforcement is not the main explanation for the largest drawdown contributor.

The stronger hypothesis is repeated entries during an unfavorable local regime. The next research step should compare these clusters against recent loss streak, session timing, range/volatility state, and context disagreement before any strategy code change.

## Recommendation

Do not change strategy code yet.

Do not enforce Order Flow confirmation.

Next diagnostic: test candidate filters against the largest clusters while preserving enough winners.
