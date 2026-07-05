# Backtest Quality Conditional Cooldown A/B Diagnostic Summary

## Safety scope

This is a research-only diagnostic summary.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated detailed reports remain under ignored `private_data`.

## Source

`private_data/sierra_chart/bulk_30d_sc_delayed/conditional_cooldown_ab_diagnostic/conditional_cooldown_ab_diagnostic_report.md`

## Key result

The conditional cooldown A/B diagnostic found that the detected loss-cluster-zone cooldown variant is the most promising research candidate.

This does not approve implementation. It only identifies the next candidate for deeper A/B validation.

## Main comparison

| Dataset | Baseline PnL | Baseline max DD | Best tested candidate | Candidate PnL | Candidate max DD | Interpretation |
|---|---:|---:|---|---:|---:|---|
| 1m bullish 200 | 20.00 | 60.00 | B1 global cooldown 3 | 90.00 | 20.00 | Positive, but small sample. |
| 5m bullish 200 | 270.00 | 30.00 | C3 detected loss-cluster-zone cooldown 10 | 305.00 | 20.00 | Improves PnL and drawdown. |
| 10m bullish 200 | 15.00 | 110.00 | C3 detected loss-cluster-zone cooldown 10 | 90.00 | 30.00 | Improves PnL and drawdown. |
| 5m bullish full | 95.00 | 335.00 | C3 detected loss-cluster-zone cooldown 10 | 540.00 | 70.00 | Strongest result, but needs validation. |

## Important details

On the full 5m run, C3 detected loss-cluster-zone cooldown 10 produced:
- kept trades: 101
- blocked trades: 87
- wins: 62
- losses: 39
- PnL: 540.00
- win rate: 61.39%
- profit factor: 2.38
- max drawdown: 70.00
- removed winners: 17
- removed losses: 70
- removed PnL: -445.00

This is materially better than the baseline full 5m result:
- trades: 188
- wins: 79
- losses: 109
- PnL: 95.00
- win rate: 42.02%
- profit factor: 1.09
- max drawdown: 335.00

## Interpretation

The result supports the loss-cluster hypothesis more strongly than Order Flow enforcement.

A simple global cooldown remains risky because previous robustness diagnostics showed mixed behavior, especially on 10m.

The detected loss-cluster-zone variant appears more targeted because it blocks fewer winners relative to removed losses in the full 5m result.

## Recommendation

Do not implement this as strategy code yet.

Research module status: the formal checklist and research-only CLI module are completed in `c2b2c03 analysis: add conditional cooldown diagnostic`.

Next research step: review generated ignored `private_data` reports and document interpretation only. Do not implement strategy enforcement yet.

Order Flow confirmation remains diagnostic-only and should not be enforced.

