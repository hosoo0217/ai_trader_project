# Order Flow Confirmation Change Proposal

This document proposes a possible future strategy rule for requiring directional Order Flow confirmation before execution.

It is a proposal only. It does not edit Python code, implement the rule, change strategy logic, change risk rules, connect live systems, create real order execution, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record a possible strategy improvement idea after diagnosing losing executed trades from a real Sierra weekday `BAR_SUMMARY` 50-iteration backtest.

The idea is to research whether Apex Futures Scalper, especially for GC scalping, should require directional Order Flow confirmation before allowing execution.

This proposal is not approved for implementation yet.

## 2. Evidence From Current Validation

Observed validation result:

- Total iterations: `50`
- Executed trades: `8`
- Blocked trades: `42`
- Final balance: `49920.00`
- Total PnL: `-80.00`
- Win rate: `0.00%`
- All 8 executed trades were losses.
- Executed trades were `SELL` trades.
- Exit result was `STOP_LOSS`.
- Order Flow was `NEUTRAL` on executed trades.
- Order Flow confidence was `0.0`.
- Order Flow data quality passed.
- The data source was Sierra `BAR_SUMMARY`, not full price-level footprint data.

This evidence is not enough to prove the strategy is broken, but it is enough to justify researching whether neutral Order Flow should be allowed for execution.

## 3. Problem Statement

The current decision flow can execute trades when:

- multi-timeframe context supports the trade direction,
- SMC supports or does not block the trade direction,
- CRT supports the trade direction,
- the safety gate passes,
- risk checks allow the trade,
- Order Flow remains neutral.

In the diagnosed test, that allowed SELL trades to execute without directional Order Flow confirmation. All executed examples hit stop loss.

The problem is not that one losing test proves the strategy is invalid. The problem is that the system may be allowing execution when one important confirmation source is neutral.

## 4. Proposed Rule Idea

Research a rule for Apex Futures Scalper that requires directional Order Flow confirmation before execution.

Example rule idea:

- `BUY` requires Order Flow bias `BULLISH` with confidence above a defined threshold.
- `SELL` requires Order Flow bias `BEARISH` with confidence above a defined threshold.
- `NEUTRAL` Order Flow should block the trade or downgrade the final action to `NO_TRADE`.
- The rule should apply only after Order Flow data quality passes.
- The threshold should be validated by backtesting, not guessed.

This rule should be researched first and not implemented immediately.

## 5. Expected Benefit

Expected benefits if validated:

- Reduce trades that execute without directional Order Flow support.
- Prevent neutral Order Flow from acting like confirmation.
- Improve alignment between MTF, SMC, CRT, and Order Flow before execution.
- Potentially reduce stop-loss trades in GC scalping conditions.
- Keep the system conservative when confirmation is incomplete.

The main intended benefit is better selectivity, not more trades.

## 6. Possible Downside

Possible downsides:

- The rule may block too many trades.
- It may block valid trades where Order Flow is neutral because `BAR_SUMMARY` data is weak.
- It may make results look safer only by avoiding nearly all execution.
- It may perform differently on full price-level footprint data.
- It may overfit to one Sierra weekday test.
- It may reduce trade frequency below a useful sample size.

This is why the rule needs backtest evidence before implementation.

## 7. Required Backtest Evidence Before Implementation

Before implementation, evidence must compare old behavior against proposed behavior.

Required validation:

- Compare current behavior vs proposed Order Flow confirmation behavior.
- Test bullish scenarios.
- Test bearish scenarios.
- Test more than one Sierra session.
- Test Sierra `BAR_SUMMARY` data.
- Later test full price-level footprint data.
- Track executed trades.
- Track blocked trades.
- Track win rate.
- Track total PnL.
- Track profit factor.
- Track max drawdown.
- Confirm the rule does not simply block everything.
- Confirm the rule does not hide risk by producing too few trades.
- Confirm no live trading is involved.

The rule should not be implemented unless the comparison shows better safety or quality without destroying useful validation coverage.

## 8. Safety Requirements

Any future research or implementation must follow these safety requirements:

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection.
- No CME live data connection.
- No real order execution.
- No external APIs.
- No `private_data` committed.
- No generated diagnostic reports committed unless project policy explicitly allows them.
- No weakening of existing filters just to force trades.
- No implementation without backtest evidence.

The proposal must remain research-only until reviewed and validated.

## 9. Decision Status

Status: `NEEDS_BACKTEST`

This proposal is not approved for implementation yet.

The next correct step is to design and run a research-only comparison between:

- current behavior,
- proposed Order Flow confirmation behavior.

Only after backtest evidence exists should the project consider a formal implementation plan.

## 10. Beginner Summary

The latest real Sierra backtest showed that the system executed 8 SELL trades. All 8 lost, and Order Flow was neutral with `0.0` confidence on those trades.

This does not mean the whole system is broken. It means there is a sensible question to research: should the system require Order Flow to agree before entering a trade?

The proposed answer is: maybe, but not yet. First, compare the old behavior against the proposed rule across more backtests. If the rule improves safety without blocking everything, then it can be considered later.

For now, the status is `NEEDS_BACKTEST`, not approved for implementation.
