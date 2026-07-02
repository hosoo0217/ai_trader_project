# Context Alignment Diagnostic Implementation Checklist

## Safety Boundary

This checklist is for a future diagnostic-only implementation.

- No live trading
- No broker connection
- No real orders
- No strategy execution enforcement
- No risk rule change
- No paper trading deployment
- No external API connection
- No private_data commit

## Purpose

The purpose is to add a C simulated diagnostic path:

- A: current behavior
- B: simulated Order Flow confirmation
- C: simulated Order Flow confirmation plus context alignment filter

C must only appear in diagnostic reports.

C must not change actual A execution behavior.

## Required Implementation Rules

Any future implementation must:

1. Be test-first.
2. Be disabled-by-default or diagnostic-only.
3. Leave current A behavior unchanged.
4. Leave risk rules unchanged.
5. Leave broker/live execution unchanged.
6. Add clear report counters.
7. Add clear blocked-trade reasons.
8. Clearly separate C behavior from B behavior.

## Proposed C Blocking Reasons

C should report separate counters for:

- Order Flow neutral block
- Order Flow low-confidence block
- Order Flow opposite-bias block
- Order Flow data-quality block
- CRT conflict block
- SMC market-structure conflict block
- Mixed-context conflict block

## Minimum Tests Required

Tests should verify:

- C does not change A executed trades.
- C does not change B simulated behavior.
- BUY can be blocked when CRT context is BEARISH.
- SELL can be blocked when CRT context is BULLISH.
- BUY can be blocked when SMC structure is strongly BEARISH without reversal confirmation.
- SELL can be blocked when SMC structure is strongly BULLISH without reversal confirmation.
- Report labels correctly show BUY/SELL side.
- Report counters correctly separate B and C blocks.
- Existing 841 tests still pass.

## Files Allowed For Future Code Implementation

Allowed if explicitly approved later:

- main.py
- tests/test_main_mode_runner.py
- diagnostic/reporting code related to Order Flow A/B report only
- docs related to the implementation

## Files Not Allowed Without Separate Approval

Do not modify:

- risk/*
- broker/*
- live execution logic
- MT5 logic
- Sierra live connection logic
- strategy enforcement rules
- private_data/*
- reports/* committed files

## Approval Required

Before code implementation, HOSOO must explicitly approve:

"I approve test-first diagnostic-only Context Alignment C implementation. Do not enforce it in strategy execution."

Without that approval, this remains a research checklist only.
