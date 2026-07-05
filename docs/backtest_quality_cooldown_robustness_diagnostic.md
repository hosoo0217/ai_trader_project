# Backtest Quality Cooldown Robustness Diagnostic

## Safety scope

This is a research-only robustness diagnostic.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated source reports remain under ignored `private_data`.

## Source diagnostics

- `per_entry_orderflow_1m_bullish_200_incremental`
- `per_entry_orderflow_5m_bullish_200_incremental`
- `per_entry_orderflow_10m_bullish_200_incremental`
- `per_entry_orderflow_5m_bullish_full_incremental`

## Result summary

| Dataset | Baseline PnL | Best cooldown note | Robustness interpretation |
|---|---:|---|---|
| 1m bullish 200 | 20.00 | Cooldown 3 improved to 90.00 | Positive but small sample only. |
| 5m bullish 200 | 270.00 | Cooldown 10 kept PnL at 200.00 with better PF/DD | Quality improved, but PnL dropped versus baseline. |
| 10m bullish 200 | 15.00 | Cooldown 1 improved to 35.00; cooldown 2 and 3 turned negative | Not robust on 10m. |
| 5m bullish full | 95.00 | Cooldown 10 improved to 455.00; cooldown 3 improved to 370.00 | Strong on full 5m, but may be regime-specific. |

## Detailed metrics

### 1m bullish 200 incremental

| Cooldown | Trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 18 | 8 | 10 | 20.00 | 44.44% | 1.20 | 60.00 |
| 1 | 14 | 8 | 6 | 60.00 | 57.14% | 2.00 | 40.00 |
| 2 | 12 | 8 | 4 | 80.00 | 66.67% | 3.00 | 20.00 |
| 3 | 11 | 8 | 3 | 90.00 | 72.73% | 4.00 | 20.00 |
| 5 | 10 | 7 | 3 | 75.00 | 70.00% | 3.50 | 20.00 |
| 10 | 10 | 7 | 3 | 75.00 | 70.00% | 3.50 | 20.00 |

### 5m bullish 200 incremental

| Cooldown | Trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 38 | 26 | 12 | 270.00 | 68.42% | 3.25 | 30.00 |
| 1 | 32 | 22 | 10 | 230.00 | 68.75% | 3.30 | 30.00 |
| 2 | 29 | 21 | 8 | 235.00 | 72.41% | 3.94 | 20.00 |
| 3 | 28 | 20 | 8 | 220.00 | 71.43% | 3.75 | 20.00 |
| 5 | 25 | 18 | 7 | 200.00 | 72.00% | 3.86 | 20.00 |
| 10 | 20 | 16 | 4 | 200.00 | 80.00% | 6.00 | 10.00 |

### 10m bullish 200 incremental

| Cooldown | Trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 46 | 19 | 27 | 15.00 | 41.30% | 1.06 | 110.00 |
| 1 | 34 | 15 | 19 | 35.00 | 44.12% | 1.18 | 55.00 |
| 2 | 29 | 11 | 18 | -15.00 | 37.93% | 0.92 | 60.00 |
| 3 | 25 | 8 | 17 | -50.00 | 32.00% | 0.71 | 75.00 |
| 5 | 23 | 10 | 13 | 20.00 | 43.48% | 1.15 | 40.00 |
| 10 | 15 | 6 | 9 | 0.00 | 40.00% | 1.00 | 30.00 |

### 5m bullish full incremental

| Cooldown | Trades | Wins | Losses | PnL | Win rate | Profit factor | Max drawdown |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 188 | 79 | 109 | 95.00 | 42.02% | 1.09 | 335.00 |
| 1 | 142 | 67 | 75 | 255.00 | 47.18% | 1.34 | 225.00 |
| 2 | 122 | 63 | 59 | 355.00 | 51.64% | 1.60 | 145.00 |
| 3 | 113 | 60 | 53 | 370.00 | 53.10% | 1.70 | 135.00 |
| 5 | 99 | 53 | 46 | 335.00 | 53.54% | 1.73 | 145.00 |
| 10 | 77 | 49 | 28 | 455.00 | 63.64% | 2.62 | 75.00 |

## Finding

Post-loss cooldown is a useful diagnostic candidate, but it is not robust enough to implement as a strategy rule yet.

The strongest result is the full 5m run, where cooldown 3 and cooldown 10 both improve PnL, profit factor, win rate, and max drawdown.

The 10m 200-run result is the main warning. Cooldown 2 and cooldown 3 turn the result negative, which means a simple global cooldown rule may overfit the 5m regime.

The 5m 200-run result also warns that cooldown can improve quality metrics while reducing total PnL versus baseline.

## Recommendation

Do not implement cooldown yet.

Next research step: design an A/B diagnostic plan that tests cooldown as a conditional filter, not a global rule. Candidate conditions include local loss clusters, session timing, repeated same-direction entries, and volatility/range state.

Order Flow confirmation remains diagnostic-only and should not be enforced.
