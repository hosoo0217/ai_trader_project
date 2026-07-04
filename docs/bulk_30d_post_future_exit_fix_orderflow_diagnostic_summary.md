# Bulk 30-day post future-exit-fix Order Flow diagnostic summary

## Safety scope

This is diagnostic-only research.

No strategy rule was changed.
No risk rule was changed.
No broker code was changed.
No live trading code was changed.
No paper trading, live trading, broker connection, Sierra Chart live connection, external API, or real order is approved.

## Baseline

- Branch: `main`
- Starting commit: `6fc89ef fix: use post-entry candles for backtest exit simulation`
- Prior checkpoint tag: `bulk-sierra-backtest-runner-profile-checkpoint` at `f1f3da7`
- Dataset folder: `private_data/sierra_chart/bulk_30d_sc_delayed`
- Dataset source: Sierra Chart delayed exports
- Matched audit status: 10m, 5m, and 1m all had 22 matched sessions and 0 mismatched sessions

## Reason for this addendum

The exit simulation timing bug was fixed before this diagnostic pass. `BacktestRunner` now passes post-entry future candles into `PaperTradingFlow`, so exit simulation no longer uses pre-entry lookback candles.

Older 5m and 10m bulk runner outputs were produced before this fix and showed all-loss profiles. They are no longer authoritative for post-fix exit behavior.

## Commands run

5m rerun:

```powershell
.\venv\Scripts\python.exe analysis\bulk_sierra_backtest_runner.py --market-csv private_data\sierra_chart\bulk_30d_sc_delayed\bulk_30d_5m_market_matched.csv --footprint-csv private_data\sierra_chart\bulk_30d_sc_delayed\bulk_30d_5m_footprint.csv --timeframe 5m --max-iterations 200 --profile apex --side both --output-dir private_data\sierra_chart\bulk_30d_sc_delayed\backtest_5m_apex_runner_after_future_exit_fix
```

10m rerun:

```powershell
.\venv\Scripts\python.exe analysis\bulk_sierra_backtest_runner.py --market-csv private_data\sierra_chart\bulk_30d_sc_delayed\bulk_30d_10m_market_matched.csv --footprint-csv private_data\sierra_chart\bulk_30d_sc_delayed\bulk_30d_10m_footprint.csv --timeframe 10m --max-iterations 200 --profile apex --side both --output-dir private_data\sierra_chart\bulk_30d_sc_delayed\backtest_10m_apex_runner_after_future_exit_fix
```

The 1m post-fix rerun already existed at:

`private_data/sierra_chart/bulk_30d_sc_delayed/backtest_1m_apex_runner_after_future_exit_fix`

## Post-fix A current behavior

| Timeframe | Scenario | Iterations | A executed | A PnL | A win rate | Wins | Losses |
|---|---|---:|---:|---:|---:|---:|---:|
| 1m | bullish | 200 | 18 | +20.00 | 44.44% | 8 | 10 |
| 1m | bearish | 200 | 18 | +20.00 | 44.44% | 8 | 10 |
| 5m | bullish | 200 | 38 | +270.00 | 68.42% | 26 | 12 |
| 5m | bearish | 200 | 38 | +270.00 | 68.42% | 26 | 12 |
| 10m | bullish | 200 | 46 | +15.00 | 41.30% | 19 | 27 |
| 10m | bearish | 200 | 46 | +15.00 | 41.30% | 19 | 27 |

## Simulated B Order Flow confirmation behavior

| Timeframe | Scenario | B executed | B blocked by Order Flow | Neutral blocks | Blocked wins | Blocked losses |
|---|---|---:|---:|---:|---:|---:|
| 1m | bullish | 0 | 18 | 18 | 8 | 10 |
| 1m | bearish | 0 | 18 | 18 | 8 | 10 |
| 5m | bullish | 0 | 38 | 38 | 26 | 12 |
| 5m | bearish | 0 | 38 | 38 | 26 | 12 |
| 10m | bullish | 0 | 46 | 46 | 19 | 27 |
| 10m | bearish | 0 | 46 | 46 | 19 | 27 |

All simulated Order Flow confirmation blocks were because Order Flow was `NEUTRAL`. There were no low-confidence, opposite-bias, or data-quality blocks in these reports.

## Interpretation

The post-fix results no longer support the earlier simple conclusion that neutral Order Flow would only block losing trades.

On the 30-day matched dataset, simulated Order Flow confirmation would block every executed trade across 1m, 5m, and 10m because the current bulk Order Flow context is neutral. After the exit timing fix, that includes many winners:

- 1m: 8 wins and 10 losses blocked per scenario
- 5m: 26 wins and 12 losses blocked per scenario
- 10m: 19 wins and 27 losses blocked per scenario

This means Order Flow confirmation remains useful as diagnostic instrumentation, but the current neutral-context behavior is too blunt to justify enforcement.

## Next research step

Do not implement Order Flow enforcement from these results.

The next diagnostic step should investigate why the bulk Order Flow context is neutral across full-session exports. Priority checks:

- Whether context should be computed from a rolling pre-entry footprint window instead of the entire 30-day footprint file
- Whether the context combiner thresholds neutralize meaningful 5m/10m imbalance evidence
- Whether per-iteration Order Flow snapshots can be exported without changing trading behavior
