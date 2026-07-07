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

Status: completed by capital_protection_daily_state_policy.md.

Resolved decisions:
- daily reset boundary uses the UTC calendar day
- timezone basis is UTC
- daily PnL uses closed-trade realized PnL only by default
- open and unrealized PnL do not affect daily loss lock or daily profit target by default
- commission and slippage inclusion must be reported only when available
- daily capital protection state remains in-memory unless a separate persistence policy is approved

Safe output remains documentation-only and does not approve broker connection, live data, or order execution.

### 2. Loss counting policy

Status: completed by capital_protection_loss_counting_policy.md.

Resolved decisions:
- loss counting uses finalized closed trade records only
- closed losses increment the consecutive loss streak
- closed wins reset the consecutive loss streak to zero
- breakeven trades do not increment or reset the streak by default
- partial exits do not update the streak until the logical trade is closed
- UTC daily reset clears the streak
- cooldown completion does not reset the streak by default

Safe output remains documentation-only and does not approve broker connection, live data, order execution, or automatic cooldown reset behavior.

### 3. Profit target policy

Status: completed by capital_protection_profit_target_policy.md.

Resolved decisions:
- TARGET_REACHED triggers from realized daily PnL only
- open and unrealized PnL do not trigger TARGET_REACHED by default
- after TARGET_REACHED, new entries are blocked for the rest of the UTC daily window by default
- already-open positions are not automatically closed, reduced, reversed, or modified
- trailing profit target behavior is not approved by default
- TARGET_REACHED resets at the UTC daily reset boundary
- independent reset schedulers are not approved

Safe output remains documentation-only and does not approve broker connection, live data, order execution, forced position closing, trailing target behavior, or independent reset schedulers.

### 4. Position limit policy

Status: completed by capital_protection_position_limit_policy.md.

Resolved decisions:
- MAX_POSITIONS triggers when open_positions is greater than or equal to max_open_positions
- max_open_positions equal to zero disables the position limit check by default
- max_open_positions is interpreted as a global limit for the evaluated capital protection state by default
- per-system, per-strategy, per-instrument, and account-specific limits are not approved unless explicitly provided and tested
- pending orders do not count toward MAX_POSITIONS by default
- MAX_POSITIONS blocks new entries but does not automatically close, reduce, reverse, or modify already-open positions

Safe output remains documentation-only and does not approve broker connection, live data, order execution, implicit scoped limits, pending-order counting, or automatic position changes.

### 5. Session policy

Status: completed by capital_protection_session_policy.md.

Resolved decisions:
- session schedule uses UTC session windows by default
- naive datetimes are treated as UTC and timezone-aware datetimes are converted to UTC
- default enabled sessions are London, New York, and London New York Overlap
- Asian session remains disabled by default unless explicitly enabled by a strategy-specific policy
- weekend blocking remains enabled by default
- daylight saving time and exchange-local timezone handling are not inferred dynamically
- instrument-specific or profile-specific sessions require explicit configuration, documentation, and tests
- session filtering blocks or allows new entries only and does not automatically close, reduce, reverse, or modify already-open positions

Safe output remains documentation-only and does not approve live exchange connection, broker connection, external API usage, dynamic exchange calendar lookup, automatic DST inference, order execution, paper trading behavior changes, or automatic position changes.

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

Start with the spread policy because daily state, loss counting, profit target, position limit, and session policies are now completed, and spread threshold behavior still needs explicit instrument and session guardrails.
