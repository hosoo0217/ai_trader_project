# ACSIL Day3 1-Day 10m Validation Result

This document records the day3 one-session (1-day chart load) ACSIL full footprint validation result for the 10m timeframe.

It is documentation only. It does not change strategy rules, implement the Order Flow confirmation rule, change risk rules, enable live trading, add broker connections, add MT5 login, add Sierra live trading, add CME live data, or add external API behavior.

## 1. Dataset

- Source: `ACSIL_FULL_FOOTPRINT`
- Time range: `2026-06-30 18:00:00 -> 2026-07-01 09:10:00`
- Timeframe: `10m`
- Range type: one-session / 1-day chart load after setting Sierra Chart Days To Load for Intraday Chart Data Type = `1`
- Candles: `92`
- Levels: `6002`
- Invalid levels: `0`
- Data quality: `PASSED`

## 2. Order Flow Context

- Active: `True`
- Bias: `NEUTRAL`
- Confidence: `30.0`
- Minimum required confidence: `50.0`
- Delta direction: `NEUTRAL`
- Imbalance bias: `BULLISH`
- Absorption bias: `NEUTRAL`
- Final CVD: `96.00`
- Blocking reason: `Confidence 30.0 is below minimum 50.0`

## 3. Bullish Backtest

- Scenario: `bullish`
- Total iterations: `7`
- Executed trades: `2`
- Blocked trades: `5`
- Wins: `0`
- Losses: `2`
- PnL: `-20.00`
- Max drawdown: `20.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough iterations for reliable evaluation`

## 4. Bullish A/B Diagnostic

- A executed trades: `2`
- A PnL: `-20.00`
- B simulated executed trades: `0`
- B simulated blocked trades: `7`
- Trades B would block by Order Flow confirmation: `2`
- Trades B would block because Order Flow was `NEUTRAL`: `2`
- Simulated B PnL: `0.00`
- Warning: B simulated behavior blocks every A executed trade

## 5. Bearish Backtest

- Scenario: `bearish`
- Total iterations: `7`
- Executed trades: `2`
- Blocked trades: `5`
- Wins: `0`
- Losses: `2`
- PnL: `-20.00`
- Max drawdown: `20.00`
- Backtest quality: `INSUFFICIENT_DATA`
- Reason: `Not enough iterations for reliable evaluation`

## 6. Bearish A/B Diagnostic

- A executed trades: `2`
- A PnL: `-20.00`
- B simulated executed trades: `0`
- B simulated blocked trades: `7`
- Trades B would block by Order Flow confirmation: `2`
- Trades B would block because Order Flow was `NEUTRAL`: `2`
- Simulated B PnL: `0.00`
- Warning: B simulated behavior blocks every A executed trade

## 7. Conclusion

- This is a cleaner one-session / 1-day validation than the earlier 3-day chart-load exports.
- Data quality passed.
- Neutral/low-confidence Order Flow again coincided with losing executed trades.
- Simulated Order Flow confirmation would have blocked all observed losing executed trades in both bullish and bearish runs.
- This strengthens safety evidence for the Order Flow confirmation proposal.
- This does NOT prove profitability.
- This does NOT approve implementation.
- Sample size is small, so more independent sessions are still required.
- No strategy rule was changed.
