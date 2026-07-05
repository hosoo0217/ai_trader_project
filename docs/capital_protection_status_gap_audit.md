# Capital Protection Status Gap Audit

## Scope

This is a documentation-only audit of the current capital protection implementation versus `docs/capital_protection_spec.md`.

No strategy rule is changed. No risk rule is changed. No broker, live trading, paper trading, MT5, Sierra live, CME live data, external API, or real order path is changed or approved.

## Current implementation

`core/capital_protection.py` already provides a conservative `CapitalProtectionEngine`.

The current engine:
- evaluates emergency stop
- evaluates disabled trading
- evaluates manual pause
- evaluates daily loss limit
- evaluates daily profit target
- evaluates consecutive loss limit
- evaluates maximum open positions
- returns a decision object only
- does not execute orders
- does not connect to a broker
- does not perform live or paper trading

## Current status behavior

The current `CapitalProtectionDecision.status` is generic:
- `allowed`
- `blocked`

The reason text contains the specific cause, for example:
- `Emergency stop activated`
- `Daily loss limit reached`
- `Daily profit target reached`
- `Maximum consecutive losses reached`
- `Maximum open positions reached`

## Original spec gap

`docs/capital_protection_spec.md` lists more specific protection statuses:
- `DAILY_LOSS_LOCK`
- `TARGET_REACHED`
- `LOSS_STREAK`
- `MAX_POSITIONS`
- `NEWS_PROTECTION`
- `SESSION_PROTECTION`
- `SPREAD_PROTECTION`
- `VOLATILITY_PROTECTION`
- `EMERGENCY_STOP`
- `MANUAL_PAUSE`

Resolved in `7c47d6e` by adding optional `CapitalProtectionDecision.protection_status` metadata while preserving the generic `CapitalProtectionDecision.status` contract.

## Compatibility note

Existing tests currently expect generic status values.

Known examples:
- `tests/test_capital_protection.py` expects `decision.status == "blocked"` for blocked cases.
- `tests/test_safety_gate.py` creates blocked capital decisions with `status="blocked"`.

Changing status directly from `blocked` to specific values would require coordinated test updates.

## Resolution status

The safe compatibility path was completed in `7c47d6e`.

`CapitalProtectionDecision.status` remains generic:
- `allowed`
- `blocked`

`CapitalProtectionDecision.protection_status` now carries optional specific metadata for capital protection block reasons.

Validation completed:
- focused compatibility tests passed: `36 passed`
- full pytest passed: `875 passed`

Any future change must remain decision-only unless separately reviewed. This audit does not approve broker, live trading, paper trading behavior changes, MT5, Sierra live, CME live data, external API, or real order paths.
