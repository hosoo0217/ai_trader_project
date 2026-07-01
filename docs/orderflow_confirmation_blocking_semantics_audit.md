# Order Flow Confirmation Blocking Semantics Audit

This document is a read-only audit of the current Order Flow confirmation A/B diagnostic semantics.

It is documentation only. It does not change strategy code, `main.py`, `orderflow/*.py`, risk rules, live trading behavior, broker behavior, MT5 login behavior, Sierra live trading behavior, CME live data behavior, or external API behavior.

## 1. Current A/B Diagnostic Behavior

Audited references:

- `main.py` (`_would_block_by_orderflow_confirmation`, `_orderflow_confirmation_block_reason`, and A/B report exporter).
- `tests/test_main_mode_runner.py` A/B report tests.

Current `_would_block_by_orderflow_confirmation(item)` behavior:

- For `BUY`: returns `True` unless `orderflow_status == "BULLISH"`.
- For `SELL`: returns `True` unless `orderflow_status == "BEARISH"`.
- For any other action: returns `False`.

Audit answers:

- Does it only block NEUTRAL Order Flow? **No.**
- Does it block low-confidence Order Flow? **Not explicitly.** There is no confidence threshold check inside `_would_block_by_orderflow_confirmation`.
- Does it block opposite-bias situations? **Yes**, if `orderflow_status` is opposite to action (for example SELL with BULLISH, BUY with BEARISH), it returns `True`.
- Does it compare trade direction against Order Flow bias? **Yes.** It compares `final_action` (`BUY`/`SELL`) against directional `orderflow_status`.

Important report-level limitation:

- The A/B report currently exposes a dedicated counter only for `blocked_because_orderflow_neutral`.
- Opposite-bias blocks are included in `blocked_by_orderflow_confirmation`, but not separated into their own explicit metric key.
- This can make opposite-bias blocking less visible in summaries unless blocked-trade details are reviewed.

## 2. Required Blocking Semantics (Decision Matrix)

The intended semantics should be explicitly approved before implementation work.

### BUY / bullish trade

- Order Flow `BULLISH`: **ALLOW**
- Order Flow `NEUTRAL`: **BLOCK**
- Order Flow `BEARISH`: **BLOCK**

### SELL / bearish trade

- Order Flow `BEARISH`: **ALLOW**
- Order Flow `NEUTRAL`: **BLOCK**
- Order Flow `BULLISH`: **BLOCK**

This matrix is the minimum directional confirmation policy implied by existing proposal/readiness docs.

## 3. Day3 Evidence Summary

### Day3 one-session 10m validation

- NEUTRAL / low-confidence Order Flow coincided with losing executed trades.
- Simulated B blocked those trades and avoided observed losses in that sample.

### Day3 one-session 5m validation

- BULLISH Order Flow with confidence `70.0` still had losing bullish trades.
- Bearish scenario had BULLISH Order Flow, while observed A/B summary did not show a simulated blocking improvement.
- This indicates an A/B diagnostic semantics/reporting gap in practice and requires clarification before implementation approval.

## 4. Implementation Readiness Status

Status: **STOP / NOT READY FOR IMPLEMENTATION**

Reason:

- Blocking semantics are not fully finalized as an approved design contract across docs, diagnostics, and required tests.
- Current A/B diagnostic is useful for research, but still incomplete for implementation approval decisions.
- No strategy code should be changed until semantics are explicitly approved and test requirements are locked.

## 5. Required Test Plan Before Any Implementation

Before implementation, tests should verify at minimum:

1. NEUTRAL Order Flow blocks executed trades.
2. Low-confidence Order Flow blocks executed trades, if that is the intended rule.
3. BUY trade is blocked when Order Flow is BEARISH.
4. SELL trade is blocked when Order Flow is BULLISH.
5. BUY trade is allowed when Order Flow is BULLISH and confidence is high.
6. SELL trade is allowed when Order Flow is BEARISH and confidence is high.
7. No-orderflow-data and failed-data-quality behavior is explicitly defined and tested.
8. A/B report counts distinguish:
   - neutral blocks,
   - low-confidence blocks,
   - opposite-bias blocks,
   - data-quality blocks.

## 6. Recommended Next Step

Use a separate docs-only design approval checklist before any code implementation:

- approve final blocking semantics matrix,
- approve confidence and data-quality gating semantics,
- approve A/B report taxonomy for block reasons,
- approve required tests and pass criteria,
- confirm implementation remains disabled until all approvals are complete.

No implementation work should begin in this step.
