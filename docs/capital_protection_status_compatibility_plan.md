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

## Implementation status

Implemented in `7c47d6e` (`core: add capital protection status metadata`).

The implemented change adds optional specific protection metadata without breaking the generic status contract.

Implemented shape:
- keep `status` as `allowed` or `blocked`
- add optional `protection_status`
- keep `reasons` human-readable
- keep `allowed` as the main logic flag

Example blocked decision:
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

## Validation

Validation completed after implementation:
- existing `status == "blocked"` tests still pass
- allowed decisions keep `status == "allowed"`
- blocked decisions expose the correct optional `protection_status`
- `SafetyGate` behavior does not change
- `DecisionEngine` behavior does not change
- focused compatibility tests passed: `36 passed`
- full pytest passed: `875 passed`

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

Keep this change backward-compatible. Do not change strategy behavior, broker behavior, live trading behavior, paper trading behavior, or order execution behavior from this metadata-only improvement.
