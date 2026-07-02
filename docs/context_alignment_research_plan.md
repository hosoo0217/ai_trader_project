# Backtest-Only Context Alignment Research Plan

## Safety

- Research-only plan
- No live trading
- No broker connection
- No real orders
- No strategy rule is enforced by this document
- No risk rule is changed
- Any future implementation must be backtest-only and disabled by default

## Reason For This Plan

Day3 5m showed an important weakness.

Order Flow was BULLISH with confidence 70.0, but BUY trades still lost. The decision trace showed that SMC market structure was BEARISH, CRT context was BEARISH, and context alignment was disabled.

This means Order Flow confirmation alone is not enough for positive entry validation.

## Research Goal

Design a backtest-only context alignment experiment that checks whether trades should be blocked when major context components disagree.

The goal is not to create live trading logic.

The goal is to test whether stricter alignment would reduce losing trades without accidentally blocking too many winners.

## Proposed Context Components

The first research version should inspect:

- Market analyzer bias
- Multi-timeframe bias
- SMC market structure
- SMC BOS/CHOCH direction
- SMC liquidity sweep direction
- CRT context
- Order Flow context
- Order Flow confidence
- Safety gates

## Proposed BUY Rules For Research

A BUY trade should be considered aligned only if:

- Safety gates pass
- Order Flow is BULLISH with confidence >= minimum threshold
- CRT context is not BEARISH
- SMC structure is not strongly BEARISH unless reversal conditions are explicitly confirmed
- SMC BOS/CHOCH or sweep supports bullish direction
- No major context component creates a hard conflict

## Proposed SELL Rules For Research

A SELL trade should be considered aligned only if:

- Safety gates pass
- Order Flow is BEARISH with confidence >= minimum threshold
- CRT context is not BULLISH
- SMC structure is not strongly BULLISH unless reversal conditions are explicitly confirmed
- SMC BOS/CHOCH or sweep supports bearish direction
- No major context component creates a hard conflict

## First Research Experiment

Create a diagnostic-only A/B/C comparison:

- A: current behavior
- B: current simulated Order Flow confirmation
- C: simulated Order Flow confirmation + context alignment filter

C must be diagnostic only.

C must not change live execution.

C must not change risk rules.

C must not place orders.

## Metrics To Compare

For each session and timeframe, compare:

- A executed trades
- A PnL
- B blocked trades
- B PnL
- C blocked trades
- C PnL
- Losing trades avoided by C
- Winning trades accidentally blocked by C
- Neutral Order Flow blocks
- Opposite Order Flow blocks
- CRT conflict blocks
- SMC structure conflict blocks
- Mixed-context blocks

## Required Validation Before Any Enforcement

Before implementation into actual strategy behavior:

- At least 3 clean independent sessions
- Prefer 5 clean independent sessions
- Stronger target: 10 clean independent sessions
- Evidence must show not only losing trades avoided, but also whether winners were accidentally blocked

## Readiness Decision

Current status:

- Order Flow data pipeline: OK
- A/B diagnostic: OK
- Neutral blocking evidence: improving
- Opposite-bias diagnostic: fixed
- Positive aligned-entry evidence: weak
- Context alignment research: needed
- Strategy enforcement: NOT READY
- Paper trading: NOT READY
- Live trading: NOT READY

## Next Step

The next implementation step, if approved later, should be test-first and diagnostic-only.

It should add C simulated behavior to reports without changing A behavior or live execution.
