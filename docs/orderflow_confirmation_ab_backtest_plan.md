# Order Flow Confirmation A/B Backtest Plan

This document defines the research-only A/B backtest plan for the Order Flow confirmation proposal.

It is documentation only. It does not edit Python code, implement the rule, change strategy logic, change risk rules, create live trading code, connect live systems, or approve paper/live trading.

## 1. Purpose

The purpose of this plan is to compare current Apex Futures Scalper behavior against a proposed Order Flow confirmation behavior before any implementation.

The proposal has been registered and reviewed as `NEEDS_BACKTEST`.

No strategy rule should be changed until an A/B test report exists, tests pass, private data remains uncommitted, and final human review approves the next step.

## 2. Proposal Being Tested

Proposal:

Require directional Order Flow confirmation before Apex Futures Scalper execution, especially for GC scalping.

The proposed behavior is:

- Apex GC `BUY` requires Order Flow `BULLISH` confirmation above a researched threshold.
- Apex GC `SELL` requires Order Flow `BEARISH` confirmation above a researched threshold.
- Order Flow `NEUTRAL` blocks execution or downgrades the action to `NO_TRADE`.
- The exact confidence threshold must be researched.
- No threshold should be hardcoded before evidence exists.

This proposal is not approved for implementation yet.

## 3. Current Evidence

Current observed evidence came from a real Sierra weekday `BAR_SUMMARY` backtest:

- Total iterations: `50`
- Executed trades: `8`
- Blocked trades: `42`
- Final balance: `49920.00`
- Total PnL: `-80.00`
- Win rate: `0.00%`
- All 8 executed trades were `SELL` losses.
- Exit result: `STOP_LOSS`
- Order Flow was `NEUTRAL` on executed trades.
- Order Flow confidence was `0.0`.
- Data quality: `PASSED`
- Source was `BAR_SUMMARY`, not full price-level footprint data.

This evidence does not prove the system is broken. It does justify testing whether neutral Order Flow should block Apex GC execution.

## 4. A/B Test Definition

### A: Current Behavior

Current behavior allows trades when:

- MTF supports the trade direction,
- SMC supports or does not block the trade direction,
- CRT supports the trade direction,
- safety gate passes,
- risk engine allows the trade,
- Order Flow remains `NEUTRAL`.

This is the baseline behavior.

### B: Proposed Behavior

Proposed behavior would require directional Order Flow confirmation:

- Apex GC `BUY` requires Order Flow `BULLISH` confirmation above threshold.
- Apex GC `SELL` requires Order Flow `BEARISH` confirmation above threshold.
- Order Flow `NEUTRAL` blocks execution or downgrades the final action to `NO_TRADE`.
- The threshold must be researched and documented before implementation.

The B behavior should be tested only as a research comparison before any strategy code change.

## 5. Required Input Data

Required data for the A/B study:

- Current Sierra weekday `BAR_SUMMARY` file.
- More Sierra weekday sessions.
- Bullish scenarios.
- Bearish scenarios.
- Multiple session windows.
- Later full price-level footprint export.

`BAR_SUMMARY` is useful for early comparison, but it is not full footprint data. Full price-level footprint export is still needed before stronger Order Flow conclusions.

## 6. Metrics To Compare

Compare A and B using:

- Total iterations.
- Executed trades.
- Blocked trades.
- Win rate.
- Total PnL.
- Max drawdown.
- Profit factor.
- Average PnL per trade.
- Common blocking reasons.
- How many trades were blocked only because Order Flow was `NEUTRAL`.
- Whether the rule blocks everything.
- Whether losses reduce without eliminating all trades.

The comparison must include both performance and safety behavior.

## 7. Minimum Evidence Before Implementation

Minimum evidence required before implementation:

- A/B test report exists.
- B does not simply block all trades.
- B reduces bad trades or improves drawdown without hiding risk.
- B keeps enough executed trades to evaluate behavior.
- Bullish and bearish scenarios are tested.
- More than one Sierra session is tested.
- `BAR_SUMMARY` results are documented.
- Full footprint data is tested later when available.
- Tests pass.
- No `private_data` committed.
- Final human review still required.

Without this evidence, the rule should not be implemented.

## 8. Risks Of The Proposed Rule

Risks:

- The proposed rule may block too many trades.
- It may appear safer only because it avoids nearly all execution.
- It may overfit to one losing `BAR_SUMMARY` sample.
- It may behave differently with full price-level footprint data.
- Neutral Order Flow on `BAR_SUMMARY` may reflect limited data, not true market neutrality.
- A poorly chosen confidence threshold may block valid trades.
- The rule may reduce sample size below useful validation levels.

These risks must be measured, not guessed.

## 9. What Would Count As Improvement

B would count as an improvement if evidence shows:

- Stop-loss trades are reduced.
- Max drawdown improves.
- Total PnL improves or losses become meaningfully smaller.
- Profit factor improves.
- Average PnL per trade improves.
- Bad neutral-Order-Flow trades are blocked.
- The rule does not block everything.
- Enough trades remain to evaluate behavior.
- Safety filters remain intact.

Improvement must be shown across more than one session or market condition.

## 10. What Would Count As Failure

B would count as a failure if:

- It blocks nearly all trades.
- It produces too few trades to evaluate.
- It does not improve drawdown.
- It does not reduce losing trades.
- It worsens total PnL.
- It worsens profit factor.
- It only looks better by hiding risk.
- It performs inconsistently across bullish and bearish scenarios.
- It depends on one overfit confidence threshold.

If B fails, the proposal should remain unimplemented or be revised for another review cycle.

## 11. Safety Requirements

All A/B validation must follow these safety requirements:

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection.
- No CME live data connection.
- No real order execution.
- No external APIs.
- No `private_data` committed.
- No generated reports committed unless project policy explicitly allows them.
- No weakening filters just to force trades.

The A/B test is local, offline, and research-only.

## 12. Implementation Gate

Implementation is blocked until:

- A/B test evidence exists.
- The evidence is documented.
- Tests pass.
- Private data remains uncommitted.
- A final human review approves implementation planning.

The current status remains `NEEDS_BACKTEST`.

This plan is not approval to change strategy code.

## 13. Beginner Summary

The current system can take Apex GC trades even when Order Flow is neutral. In the latest 50-iteration Sierra test, 8 SELL trades executed, and all 8 hit stop loss while Order Flow was neutral.

The proposed idea is simple: maybe Apex GC trades should require Order Flow to agree before entering.

But the project should not implement that rule yet. First, compare old behavior against the proposed behavior using more data. If the proposed rule reduces bad trades without blocking everything, it can move to final human review later.

For now, this is only an A/B backtest plan.
