# Capital Protection Status Compatibility Plan

## Scope

This is a documentation-only compatibility plan for future capital protection status improvements.

No strategy rule is changed. No risk rule is changed. No broker, live trading, paper trading, MT5, Sierra live, CME live data, external API, or real order path is changed or approved.

## Current contract

`CapitalProtectionDecision.status` currently uses a generic contract:
- `allowed`
- `blocked`

Existing tests and downstream safety code rely on this contract.

Known compatibility points:
- `tests/test_capital_protection.py` checks `decision.status == "blocked"`.
- `tests/test_safety_gate.py` creates blocked capital decisions with `status="blocked"`.
- `SafetyGate` and `DecisionEngine` use `allowed` and `reasons` for blocking behavior, not specific status names.

## Target improvement

Future work may add specific protection metadata without breaking the generic status contract.

Recommended future shape:
- keep `status` as `allowed` or `blocked`
- add optional `protection_status`
- keep `reasons` human-readable
- keep `allowed` as the main logic flag

Example future blocked decision:
- `allowed=False`
- `status="blocked"`
- `protection_status="DAILY_LOSS_LOCK"`
- `reasons=["Daily loss limit reached"]`

## Specific status mapping

| Rule | Generic status | Proposed protection_status |
|---|---|---|
| Emergency stop | blocked | EMERGENCY_STOP |
| Trading disabled | blocked | TRADING_DISABLED |
| Manual pause | blocked | MANUAL_PAUSE |
| Daily loss limit | blocked | DAILY_LOSS_LOCK |
| Daily profit target | blocked | TARGET_REACHED |
| Consecutive losses | blocked | LOSS_STREAK |
| Maximum open positions | blocked | MAX_POSITIONS |

## Test plan for future code change

Future code change should add or update tests to prove:
- existing `status == "blocked"` tests still pass
- allowed decisions keep `status == "allowed"`
- blocked decisions expose the correct optional `protection_status`
- `SafetyGate` behavior does not change
- `DecisionEngine` behavior does not change
- full pytest passes

## Not allowed

This plan does not approve:
- strategy enforcement changes
- broker integration
- live trading
- paper trading behavior changes
- MT5 login
- Sierra live connection
- CME live data connection
- external API usage
- real order execution

## Recommended next step

Implement only optional metadata in a small, backward-compatible code change after this plan is reviewed.
