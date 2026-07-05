# Backtest Quality Post-Loss Cooldown Candidate Diagnostic

## Safety scope

This is a research-only candidate diagnostic.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated source reports remain under ignored `private_data`.

## Source

`private_data/sierra_chart/bulk_30d_sc_delayed/per_entry_orderflow_5m_bullish_full_incremental/per_entry_orderflow_replay_diagnostic.json`

## Baseline

| Trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown |
|---:|---:|---:|---:|---:|---:|---:|
| 188 | 79 | 109 | 95.00 | 42.02% | 1.09 | 335.00 |

## Post-loss cooldown diagnostic

A trade is skipped if it appears within the configured iteration cooldown after the most recent kept losing trade.

| Cooldown | Kept trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown | Removed wins | Removed losses | Removed PnL |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 142 | 67 | 75 | 255.00 | 47.18% | 1.34 | 225.00 | 12 | 34 | -160.00 |
| 2 | 122 | 63 | 59 | 355.00 | 51.64% | 1.60 | 145.00 | 16 | 50 | -260.00 |
| 3 | 113 | 60 | 53 | 370.00 | 53.10% | 1.70 | 135.00 | 19 | 56 | -275.00 |
| 5 | 99 | 53 | 46 | 335.00 | 53.54% | 1.73 | 145.00 | 26 | 63 | -240.00 |
| 10 | 77 | 49 | 28 | 455.00 | 63.64% | 2.62 | 75.00 | 30 | 81 | -360.00 |
| 15 | 68 | 41 | 27 | 345.00 | 60.29% | 2.28 | 90.00 | 38 | 82 | -250.00 |
| 20 | 56 | 31 | 25 | 215.00 | 55.36% | 1.86 | 90.00 | 48 | 84 | -120.00 |

## Finding

Post-loss cooldown is a stronger candidate than Order Flow enforcement for this full 5m run.

Cooldown values from 2 to 10 improve PnL, win rate, profit factor, and max drawdown versus baseline.

The strongest metric result is cooldown 10, but it keeps only 77 of 188 trades and removes 30 winners. This creates over-filtering risk.

Cooldown 3 is a more balanced diagnostic candidate because it keeps 113 trades, improves PnL to 370.00, improves profit factor to 1.70, and reduces max drawdown to 135.00.

## Recommendation

Do not implement a strategy rule yet.

Next diagnostic step: compare cooldown 2, 3, 5, and 10 against the largest loss clusters and against other timeframes or scenarios before approving any code change.

Order Flow confirmation remains diagnostic-only and should not be enforced.
