# ACSIL Day3 1-Day 1m Validation Result

This document records the day3 one-session (1-day chart load) ACSIL full footprint validation result for the 1m timeframe after the Order Flow A/B diagnostic semantics fixes.

It is documentation only. It does not change `main.py`, strategy code, risk rules, broker behavior, live trading behavior, or external API behavior.

## 1. Dataset

- Source: `ACSIL_FULL_FOOTPRINT`
- Timeframe: `1m`
- Range type: one-session / 1-day chart load
- Footprint range: `2026-06-30 18:00:00 -> 2026-07-01 11:36:00`
- Market file was trimmed into matched file ending `2026-07-01 11:36:00`
- Market rows: `1056`
- Candles: `1056`
- Levels: `21578`
- Invalid levels: `0`
- Data quality: `PASSED`

## 2. Order Flow Context

- Active: `True`
- Bias: `NEUTRAL`
- Confidence: `30.0`
- Delta direction: `NEUTRAL`
- Imbalance bias: `BEARISH`
- Absorption bias: `NEUTRAL`
- Final CVD: `-954.00`
- Blocking reason: `Confidence 30.0 is below minimum 50.0`

## 3. Bullish Backtest

- Scenario: bullish / `BUY`
- Total iterations: `50`
- Executed trades: `2`
- Blocked trades: `48`
- Wins: `0`
- Losses: `2`
- A PnL: `-20.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough executed trades for reliable evaluation`

## 4. Bullish A/B Diagnostic

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- Trades B would block by Order Flow confirmation: `2`
- Trades B would block because Order Flow was `NEUTRAL`: `2`
- Opposite-bias blocks: `0`
- Simulated B PnL: `0.00`
- Blocked trade label: `BUY blocked`

## 5. Bearish Backtest

- Scenario: bearish / `SELL`
- Total iterations: `50`
- Executed trades: `2`
- Blocked trades: `48`
- Wins: `0`
- Losses: `2`
- A PnL: `-20.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough executed trades for reliable evaluation`

## 6. Bearish A/B Diagnostic

- B simulated executed trades: `0`
- B simulated blocked trades: `50`
- Trades B would block by Order Flow confirmation: `2`
- Trades B would block because Order Flow was `NEUTRAL`: `2`
- Opposite-bias blocks: `0`
- Simulated B PnL: `0.00`
- Blocked trade label: `SELL blocked`

## 7. Conclusion

- 1m validation confirms the post-fix A/B diagnostic still blocks NEUTRAL Order Flow trades.
- Both bullish and bearish 1m runs had losing executed A trades.
- Simulated B blocked those trades and avoided the observed losses.
- Data quality passed.
- This remains research-only diagnostic evidence.
- Strategy execution was not changed.
- This does not prove profitability.
- More independent sessions are still required before any strategy enforcement.
