# Day4 SC Delayed 1m Extended Validation Addendum

## Safety

- Research-only validation
- No live trading
- No broker connection
- No real orders
- No strategy rule was changed
- No risk rule was changed
- private_data was not committed

## Context

After the initial Day4 SC delayed validation, the 1m session was extended from `--backtest-max-iterations 50` to `--backtest-max-iterations 200`.

The available 1m data produced 165 actual iterations. This is expected because the session data ended before 200 iterations were available.

## 1m Extended Bullish

- Requested max iterations: 200
- Actual iterations: 165
- A executed trades: 6
- A blocked trades: 159
- A wins: 0
- A losses: 6
- A PnL: -60.00
- A max drawdown: 60.00
- Order Flow bias: NEUTRAL
- Order Flow confidence: 30.0
- B simulated executed trades: 0
- B simulated blocked trades: 165
- Trades B would block by Order Flow confirmation: 6
- Trades B would block because Order Flow was NEUTRAL: 6
- B simulated PnL: 0.00
- B max drawdown: 0.00

## 1m Extended Bearish

- Requested max iterations: 200
- Actual iterations: 165
- A executed trades: 6
- A blocked trades: 159
- A wins: 0
- A losses: 6
- A PnL: -60.00
- A max drawdown: 60.00
- Order Flow bias: NEUTRAL
- Order Flow confidence: 30.0
- B simulated executed trades: 0
- B simulated blocked trades: 165
- Trades B would block by Order Flow confirmation: 6
- Trades B would block because Order Flow was NEUTRAL: 6
- B simulated PnL: 0.00
- B max drawdown: 0.00

## Interpretation

The extended 1m validation strengthens the Day4 observation.

In both bullish and bearish scenario simulations, current behavior executed 6 trades and all 6 were losing trades. The simulated Order Flow confirmation would have blocked all 6 because Order Flow was NEUTRAL.

This still does not prove profitability. It only shows that, in this Day4 SC delayed 1m extended session, the proposed Order Flow confirmation would have avoided the specific losing trades observed in A behavior.

Bullish and bearish scenarios are separate simulations and should not be treated as simultaneous live results.

## Readiness

- Data pipeline: OK
- A/B diagnostic: OK
- Neutral Order Flow blocking evidence: strengthened
- Strategy enforcement: NOT READY
- Live trading: NOT READY
- More independent sessions required
