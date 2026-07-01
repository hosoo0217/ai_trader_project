# ACSIL Day3 1-Day 5m Validation Logic Gap

This document records the day3 one-session (1-day chart load) ACSIL full footprint validation result for the 5m timeframe and the observed A/B diagnostic logic gap.

It is documentation only. It does not change strategy rules, main decision logic, risk rules, broker behavior, live trading behavior, paper trading behavior, MT5 login behavior, Sierra live trading behavior, CME live data behavior, or external API behavior.

## 1. Dataset

- Source: `ACSIL_FULL_FOOTPRINT`
- Timeframe: `5m`
- Range type: one-session / 1-day chart load
- Market range end: `2026-07-01 09:35:00`
- Footprint was trimmed into matched file ending `2026-07-01 09:35:00`
- Candles: `188`
- Levels: `8852`
- Invalid levels: `0`
- Data quality: `PASSED`

## 2. Order Flow Context

- Active: `True`
- Bias: `BULLISH`
- Confidence: `70.0`
- Delta direction: `BUYING_PRESSURE`
- Imbalance bias: `BULLISH`
- Absorption bias: `NEUTRAL`
- Final CVD: `183.00`
- Blocking reasons: `None`

## 3. Bullish Backtest

- Scenario: `bullish`
- Total iterations: `26`
- Executed trades: `5`
- Blocked trades: `21`
- Wins: `0`
- Losses: `5`
- PnL: `-50.00`
- Max drawdown: `50.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough iterations for reliable evaluation`

## 4. Bullish A/B Diagnostic

- A executed trades: `5`
- A PnL: `-50.00`
- B simulated executed trades: `5`
- B simulated blocked trades: `21`
- Trades B would block by Order Flow confirmation: `0`
- Trades B would block because Order Flow was `NEUTRAL`: `0`
- Simulated B PnL: `-50.00`
- Simulated B max drawdown: `50.00`
- B did not improve the result.

## 5. Bearish Backtest

- Scenario: `bearish`
- Total iterations: `26`
- Executed trades: `5`
- Blocked trades: `21`
- Wins: `0`
- Losses: `5`
- PnL: `-50.00`
- Max drawdown: `50.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough iterations for reliable evaluation`

## 6. Bearish A/B Diagnostic

- A executed trades: `5`
- A PnL: `-50.00`
- B simulated executed trades: `5`
- B simulated blocked trades: `21`
- Trades B would block by Order Flow confirmation: `0`
- Trades B would block because Order Flow was `NEUTRAL`: `0`
- Simulated B PnL: `-50.00`
- Simulated B max drawdown: `50.00`
- B did not improve the result.

## 7. Important Logic Gap

- In the bearish run, Order Flow bias was `BULLISH` with confidence `70.0`.
- The bearish scenario still executed `5` losing trades.
- The simulated B behavior did not block them.
- This suggests the current A/B diagnostic only counts `NEUTRAL` Order Flow as a simulated block and does not currently model opposite-bias blocking.
- This is an implementation readiness STOP.
- The Order Flow confirmation proposal must not be implemented until the intended blocking semantics are clarified and tested.
- Required clarification: should SELL/bearish trades be blocked when Order Flow is `BULLISH`, and should BUY/bullish trades be blocked when Order Flow is `BEARISH`?
- No strategy rule was changed.

## 8. Conclusion

- 10m one-session validation supported NEUTRAL/low-confidence blocking as safety evidence.
- 5m one-session validation revealed that simple Order Flow bias alignment is not enough.
- 5m bullish remained losing even with BULLISH Order Flow confidence `70`.
- 5m bearish revealed an A/B diagnostic logic gap because opposite-bias blocking was not simulated.
- This does NOT prove profitability.
- This does NOT approve implementation.
- More design review and tests are required before any code change.
