# Context Alignment Gate v1

This document explains the SMC + CRT alignment gate used for research and backtesting.

## Why SMC and CRT Alignment Matters

SMC and CRT observe different aspects of the market:
- SMC focuses on structure and liquidity intent.
- CRT focuses on range behavior and manipulation/expansion clues.

When both contexts point in the same direction, confidence in decision quality is stronger.

## Why Conflicting Context Should Block Trading

If SMC says bullish while CRT says bearish, or the opposite, context quality is contradictory.

In v1, this conflict is treated as a safety condition:
- gate status becomes CONFLICT_BLOCKED
- confidence adjustment is negative
- the gate does not create any entry signal

This helps avoid forcing decisions when market interpretation is inconsistent.

## Why Neutral CRT May Still Allow Waiting or Continuation

CRT can be NEUTRAL when range behavior does not provide directional confirmation.

Depending on configuration:
- NEUTRAL CRT can be allowed with status NEUTRAL_WAIT
- or blocked when stricter alignment is required

This supports conservative continuation logic without pretending there is strong confirmation.

## Why This Is Not a Trade Signal

The alignment gate does not generate BUY or SELL orders.

It only validates whether existing context modules (SMC and CRT) are aligned enough to support a broader decision stack.
Risk controls, safety gates, and decision engine checks still remain mandatory.

## Future Plan: Add Order Flow Alignment

A future version is expected to add Order Flow alignment as an additional context check:
- SMC + CRT + Order Flow directional agreement
- stronger conflict handling when pressure contradicts structure/range
- richer confidence adjustment using three-domain evidence

The goal remains the same: improve decision quality for research and backtesting, without enabling live trading execution.
