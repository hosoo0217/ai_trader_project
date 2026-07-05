# Capital Protection Policy Decision Plan

## Scope

This is a documentation-only policy decision plan for the remaining TODO items in `capital_protection_todo_resolution_audit.md`.

No strategy rule is changed. No risk rule is changed. No broker, live trading, paper trading behavior, MT5, Sierra live, CME live data, external API, or real order path is changed or approved.

## Current checkpoint

The metadata-only capital protection status change is implemented.

Current compatibility contract:
- `CapitalProtectionDecision.status` remains generic: `allowed` / `blocked`
- `CapitalProtectionDecision.protection_status` carries optional specific capital protection metadata

Validation checkpoint:
- focused compatibility tests passed: `36 passed`
- full pytest passed: `875 passed`

## Decision order

Resolve the remaining policy TODOs in this order.

### 1. Daily state policy

Reason: daily loss, daily profit target, and loss streak all depend on the same reset boundary.

Decisions needed:
- daily reset boundary
- timezone basis
- whether commissions and slippage are included
- whether state is in-memory only or persisted

Safe output:
- documentation-only policy
- no broker connection
- no live data
- no order execution

### 2. Loss counting policy

Reason: loss streak protection depends on how a closed trade is classified.

Decisions needed:
- closed trades only versus partial losses
- whether breakeven counts
- reset after win, next day, or cooldown
- source of truth for trade outcome

Safe output:
- documentation-only policy
- tests only after policy is explicit

### 3. Profit target policy

Reason: target handling can alter trading behavior and must be explicit before code changes.

Decisions needed:
- hard stop versus soft stop
- whether open positions continue
- whether trailing profit target is allowed
- reset boundary

Safe output:
- documentation-only policy first
- no automatic enforcement change without tests

### 4. Position limit policy

Reason: max position logic needs account/system/instrument scope before enforcement changes.

Decisions needed:
- global versus per-system limit
- per-instrument limit
- account-specific limit
- whether pending orders count

Safe output:
- documentation-only policy first

### 5. Session policy

Reason: session filter exists, but production policy is not fully defined.

Decisions needed:
- official session schedule per strategy/system
- UTC-only versus local exchange timezone
- daylight saving time handling
- instrument-specific sessions

Safe output:
- documentation-only policy first
- no live exchange connection

### 6. Spread policy

Reason: spread threshold exists, but instrument/session thresholds are undefined.

Decisions needed:
- max spread per instrument
- max spread per session
- behavior when spread is unknown
- account/data-source differences

Safe output:
- documentation-only policy first

### 7. Volatility policy

Reason: ATR-based filter exists, but official thresholds are not defined.

Decisions needed:
- authoritative timeframe
- ATR thresholds per instrument/timeframe
- abnormal candle definition
- whether ATR alone is sufficient

Safe output:
- documentation-only policy first

### 8. Manual pause and emergency stop policy

Reason: controls exist as state/config fields, but trigger/reset authority is not defined.

Decisions needed:
- who can trigger emergency stop
- who can reset emergency stop
- manual pause scope
- persistence and audit trail

Safe output:
- documentation-only policy first

### 9. News policy

Reason: manual news windows exist, but external calendar feed is unresolved and not approved.

Decisions needed:
- manual-only versus external feed
- official high-impact source
- update workflow
- event buffer rules

Safe output:
- manual-only policy can be documented
- external economic calendar feed remains not approved unless separately reviewed

## Not allowed from this plan

This plan does not approve:
- broker integration
- live trading
- paper trading behavior changes
- MT5 login
- Sierra live connection
- CME live data connection
- external API usage
- automatic order execution
- real-money trading

## Recommended next step

Start with the daily state policy because it affects daily loss lock, profit target, and loss streak behavior.
