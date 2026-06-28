# Order Flow Absorption Analyzer v1

This document explains the first absorption analyzer used by this project.

This module is research-only.
It does not connect to live trading systems, brokers, Sierra Chart live feeds, CME live feeds, or external APIs.

## What Absorption Means

Absorption describes a situation where aggressive market orders appear strong, but price does not continue in the expected direction.

For example, buyers may aggressively lift the ask, creating strong positive delta. If the candle still fails to close near its high, that can suggest passive sellers absorbed the buying pressure.

Absorption is not proof by itself. It is a clue that strong participation may have met strong opposing liquidity.

## Buy Absorption

Buy absorption means aggressive sellers may be absorbed by passive buyers.

v1 detection rule:

- large negative delta
- high total volume
- small candle body relative to candle range
- candle fails to close near the low

Interpretation:

Large sell-side aggression appeared, but price did not close near the low. This can suggest buyers absorbed selling pressure.

v1 bias:

- `BULLISH`

## Sell Absorption

Sell absorption means aggressive buyers may be absorbed by passive sellers.

v1 detection rule:

- large positive delta
- high total volume
- small candle body relative to candle range
- candle fails to close near the high

Interpretation:

Large buy-side aggression appeared, but price did not close near the high. This can suggest sellers absorbed buying pressure.

v1 bias:

- `BEARISH`

## Why Absorption Can Show Large Passive Players

Footprint data separates bid-side and ask-side volume inside a candle.

When one side is very aggressive but price does not make directional progress, the opposing side may be providing enough passive liquidity to slow or stop the move.

This is why absorption can sometimes highlight areas where larger passive participants may be active.

## Why Absorption Alone Is Not a Trade Signal

Absorption only describes one kind of order flow behavior.

It does not:

- place trades
- create entries
- manage risk
- confirm market structure
- validate stop loss or take profit placement

A candle can show absorption and still continue in the original direction later. Absorption should be treated as one research signal, not a complete trading decision.

## Future Plan

Future versions can combine absorption context with:

- Delta / CVD trend behavior
- imbalance clusters
- SMC market structure and liquidity context
- CRT candle range behavior
- risk filters and safety gates

The long-term goal is to make absorption one explainable input inside a broader `DecisionContext`, while keeping the module safe, testable, and offline.
