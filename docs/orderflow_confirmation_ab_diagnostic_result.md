# Order Flow Confirmation A/B Diagnostic Result

This document records the research-only A/B diagnostic result for the simulated Order Flow confirmation proposal.

It is documentation only. It does not edit Python code, change strategy logic, implement Order Flow confirmation, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record the first A/B diagnostic result comparing:

- A: current backtest behavior,
- B: simulated Order Flow confirmation behavior.

The B behavior was diagnostic only. It did not change actual execution decisions.

This result helps evaluate whether the proposed Order Flow confirmation rule deserves more backtesting before any implementation is considered.

## 2. Test Setup

The diagnostic was run with:

```text
--simulate-orderflow-confirmation-ab
```

The real Sierra weekday `BAR_SUMMARY` test used:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

The file was passed as:

- `--backtest-market-csv`
- `--orderflow-csv`

The run also used:

- `--backtest-max-iterations 50`

The Sierra CSV is private data and must not be committed.

Generated diagnostic reports should not be committed unless project policy explicitly allows generated reports.

## 3. A Current Behavior Result

A is the current strategy behavior.

Observed A result:

- Total iterations: `50`
- A executed trades: `8`
- A blocked trades: `42`
- A PnL: `-80.00`
- A win rate: `0.00%`
- A max drawdown: `80.00`

In A, the existing backtest behavior executed 8 trades. All 8 were losing SELL trades with neutral Order Flow.

## 4. B Simulated Behavior Result

B is the simulated Order Flow confirmation behavior.

Observed B diagnostic result:

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- Trades B would block by Order Flow confirmation: `8`
- Trades B would block because Order Flow was `NEUTRAL`: `8`
- Simulated B PnL: `0.00`
- Simulated B win rate: `0.00%`
- Simulated B max drawdown: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

B would have blocked all 8 executed A trades because Order Flow was `NEUTRAL`.

This avoided the 8 known losing trades in this specific diagnostic sample, but it also means B produced zero simulated executed trades.

## 5. Blocked Trade List

Trades B would have blocked:

- Iteration `23`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `24`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `25`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `26`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `27`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `29`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `30`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`
- Iteration `31`: `SELL`, Order Flow `NEUTRAL`, PnL avoided `-10.0`

All blocked-by-B trades were current-behavior SELL trades with neutral Order Flow.

## 6. What Improved

In this diagnostic sample, simulated B improved these specific observed outcomes:

- B avoided all 8 losing A trades.
- B avoided `-80.00` of simulated A losses.
- B reduced simulated max drawdown from `80.00` to `0.00`.
- B blocked trades where Order Flow was `NEUTRAL`.

This is useful evidence that the proposed rule would have avoided the exact losing trades seen in this sample.

## 7. What Remains Unproven

This result does not prove:

- B is profitable.
- The proposed rule should be implemented.
- Neutral Order Flow should always block trades.
- The rule will work across more Sierra sessions.
- The rule will work on full price-level footprint data.
- The rule will preserve enough trade opportunities.
- The strategy is ready for paper trading.
- The strategy is ready for live trading.

B produced zero simulated executed trades in this sample, so there is no evidence yet that B can produce profitable trades.

## 8. Main Warning

Main warning:

```text
B simulated behavior blocks every A executed trade
```

This is important.

Avoiding losing trades is good, but blocking every executed trade can also hide risk, reduce sample size, and make the system impossible to evaluate.

More data is required before deciding whether Order Flow confirmation should become a real strategy rule.

## 9. Safety Confirmation

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection.
- No CME live data connection.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No strategy rule changed.

The A/B diagnostic was local, offline, and research-only.

## 10. Next Validation Steps

1. Test more Sierra weekday sessions.
2. Test bullish and bearish scenarios.
3. Test multiple session windows.
4. Track whether B continues to block all trades.
5. Track whether B can preserve valid trades when Order Flow is directional.
6. Later test full price-level footprint data.
7. Compare A and B across more than one market condition.
8. Do not implement the strategy rule yet.
9. Do not weaken other filters just to force trades.
10. Require final human review before any implementation plan.

The next goal is not to prove B is right. The next goal is to collect enough evidence to know whether B is worth implementing later.

## 11. Beginner Summary

The current system took 8 SELL trades in this Sierra test, and all 8 lost. Order Flow was neutral on those trades.

The simulated Order Flow confirmation rule would have blocked all 8 losing trades. That looks helpful, because it would have avoided `-80.00` of losses.

But there is a big caution: the simulated rule also blocked every trade. A rule that blocks everything is not automatically good. It may simply avoid both bad trades and good trades.

So the result is promising enough for more testing, but not enough to implement. More Sierra sessions and later full footprint data are required before changing strategy logic.
