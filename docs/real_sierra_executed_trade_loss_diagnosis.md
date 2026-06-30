# Real Sierra Executed Trade Loss Diagnosis

This document records the research-only diagnosis of executed losing trades from a real Sierra Chart weekday `BAR_SUMMARY` backtest.

It is documentation only. It does not add features, change strategy logic, change risk logic, add execution rules, connect Sierra Chart live, connect CME live data, connect MT5, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

The purpose of this document is to summarize what the exported backtest trade trace diagnostics showed about the executed losing trades.

The diagnostic report was created to understand why a 50-iteration real Sierra backtest produced 8 executed trades and why all 8 executed trades lost.

This document is not a strategy-change proposal and does not approve paper trading or live trading.

## 2. Test Setup

The diagnostic run used the private local Sierra Chart CSV:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

The same file was used as:

- backtest market candles through `--backtest-market-csv`,
- Order Flow context through `--orderflow-csv`.

The run also used:

- `--backtest-max-iterations 50`
- `--export-backtest-trade-traces`

The diagnostic exports were:

```text
reports/backtest_trade_traces.txt
reports/backtest_trade_traces.json
```

These report files are generated diagnostic outputs and should not be committed unless project policy explicitly allows generated reports to be tracked.

The private Sierra CSV must not be committed.

## 3. Summary Result

Observed diagnostic summary:

- Scenario: `bullish`
- Profile: `Apex Futures Scalper`
- Total iterations: `50`
- Executed trades: `8`
- Blocked trades: `42`
- Final balance: `49920.00`
- Total PnL: `-80.00`
- Win rate: `0.00%`
- Max drawdown: `80.00`
- Backtest quality: `INSUFFICIENT_DATA`

The result is still insufficient for reliable performance evaluation because only 8 trades executed.

## 4. Common Blocking Reasons

The most common blocking reasons were:

- Confidence below threshold: `27`
- Disabled Asian session: `9`
- Outside all allowed sessions: `4`
- Strong SMC conflict: `2`

This confirms that most iterations were blocked rather than forced into trades.

The blocked-trade behavior is useful safety behavior and should not be weakened just to create more entries.

## 5. Executed Trade Pattern

The executed trades shared a clear pattern:

- Executed trades were `SELL` trades.
- SELL entries were mainly supported by multi-timeframe, SMC, and CRT bearish context.
- Safety gate passed.
- Risk engine allowed the trades.
- Risk engine used `max_volume`.
- Order Flow was `NEUTRAL` on executed trades.
- Order Flow confidence was `0.0`.

The important pattern is that SELL trades could execute without directional Order Flow confirmation.

## 6. Loss Pattern

The loss pattern was consistent:

- All executed trades closed as `LOSS`.
- Simulated PnL was `-10.0` per trade.
- Exit simulation result was `STOP_LOSS`.
- Total executed-trade PnL was `-80.00`.

This does not prove that every future SELL trade will fail, but it does show that this smoke-test sample produced repeated stop-loss outcomes.

## 7. Order Flow Interpretation

Order Flow data quality passed, but the source was Sierra `BAR_SUMMARY`.

Important Order Flow observations:

- Order Flow bias was `NEUTRAL` on executed trades.
- Order Flow confidence was `0.0`.
- The CSV source was `BAR_SUMMARY`.
- `BAR_SUMMARY` is not full price-level footprint data.
- `BAR_SUMMARY` creates one synthetic close-price level per candle.

This means the Order Flow pipeline loaded safely, but it did not provide true directional footprint confirmation.

The executed SELL trades were therefore not supported by strong directional Order Flow evidence.

## 8. Risk Interpretation

The risk engine allowed the executed trades.

Observed risk behavior:

- Risk engine did not block the executed trades.
- Safety gate passed.
- The trades used `max_volume`.
- The simulated exits hit stop loss.

This suggests the risk system permitted trades that the strategy logic considered valid, but the market outcome was unfavorable in this sample.

This does not mean the risk engine malfunctioned. It means the allowed trades still need deeper diagnosis, especially because all executed examples lost.

## 9. What This Suggests

This diagnosis suggests:

- The current entry logic can execute losing SELL trades when Order Flow is neutral.
- Multi-timeframe, SMC, and CRT bearish context can be enough to permit SELL execution.
- Neutral Order Flow may not be strong enough confirmation for this sample.
- The losing trades should be inspected individually before changing strategy rules.
- A future rule proposal could consider requiring directional Order Flow confirmation before execution.

That possible rule must not be implemented directly from this document.

Any rule change should first go through a change proposal and require backtest evidence.

## 10. What This Does Not Prove

This diagnosis does not prove:

- The whole system is broken.
- The strategy can never work.
- Every SELL trade is bad.
- Order Flow neutral trades should always be blocked.
- `BAR_SUMMARY` is enough for serious Order Flow validation.
- The system is ready for paper trading.
- The system is ready for live trading.
- Strategy filters should be weakened.
- New execution rules should be added immediately.

This is still an early research diagnostic result.

## 11. Safety Confirmation

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra Chart live connection.
- No CME live data connection.
- No real order execution.
- No external APIs.
- No `private_data` committed.

The diagnostic run stayed local, offline, and research-only.

## 12. Next Diagnostic Steps

1. Inspect all 8 executed trades in the JSON report if needed.
2. Review each executed trade's decision trace, context, stop-loss outcome, and simulated PnL.
3. Add an optional rule proposal later: require Order Flow directional confirmation before execution.
4. Do not implement that rule yet.
5. First create a change proposal and require backtest evidence.
6. Test more weekday sessions.
7. Test full price-level footprint export later.
8. Do not weaken filters just to force trades.
9. Do not start paper trading from this result.
10. Do not start live trading from this result.

More diagnostics are needed before changing strategy rules.

## 13. Beginner Summary

This diagnostic report looked at the trades that actually executed in a 50-iteration real Sierra backtest.

The system blocked most trades, which is good safety behavior. But the 8 trades it did execute were all SELL trades, and every one hit stop loss for `-10.0`.

The biggest clue is that Order Flow was neutral with `0.0` confidence on those executed trades. The data quality passed, but the source was Sierra `BAR_SUMMARY`, not full footprint data.

So the lesson is caution: the system did not crash, and it did block many trades, but the executed trades need deeper review. This result is not enough for paper trading or live trading, and no strategy rule should be changed without a proper proposal and more backtest evidence.
