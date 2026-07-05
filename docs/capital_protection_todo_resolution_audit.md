# Capital Protection TODO Resolution Audit

## Scope

This is a documentation-only audit of the TODO items in `docs/capital_protection_spec.md`.

No strategy rule is changed. No risk rule is changed. No broker, live trading, paper trading behavior, MT5, Sierra live, CME live data, external API, or real order path is changed or approved.

## Summary

Several capital protection items are already implemented in a basic research-only form. Several TODOs remain design/policy decisions and should not be implemented blindly.

## Rule 1: Daily Loss Lock

Spec status: `DAILY_LOSS_LOCK`

Current implementation:
- `CapitalProtectionConfig.max_daily_loss`
- `CapitalProtectionState.realized_daily_pnl`
- `CapitalProtectionDecision.protection_status="DAILY_LOSS_LOCK"`

Status: partially implemented.

Remaining TODOs:
- define daily reset boundary
- define whether commissions and slippage are included in realized loss
- define persistence/storage for daily state

## Rule 2: Daily Profit Target

Spec status: `TARGET_REACHED`

Current implementation:
- `CapitalProtectionConfig.daily_profit_target`
- blocks when realized daily PnL reaches the target
- `CapitalProtectionDecision.protection_status="TARGET_REACHED"`

Status: partially implemented.

Remaining TODOs:
- decide hard-stop versus soft-stop policy
- decide whether trailing profit targets are supported
- define open-position handling after target hit

## Rule 3: Loss Streak Protection

Spec status: `LOSS_STREAK`

Current implementation:
- `CapitalProtectionConfig.max_consecutive_losses`
- `CapitalProtectionState.consecutive_losses`
- `CapitalProtectionDecision.protection_status="LOSS_STREAK"`

Status: partially implemented.

Remaining TODOs:
- define how losses are counted upstream
- decide whether partial losses count
- define reset behavior after cooldown or next day

## Rule 4: Max Positions

Spec status: `MAX_POSITIONS`

Current implementation:
- `CapitalProtectionConfig.max_open_positions`
- `CapitalProtectionState.open_positions`
- `CapitalProtectionDecision.protection_status="MAX_POSITIONS"`

Status: partially implemented.

Remaining TODOs:
- define separate limits per system
- define whether limits differ by instrument or account type

## Rule 5: News Protection

Spec status: `NEWS_PROTECTION`

Current implementation:
- manual `NewsEvent` windows
- configurable impact blocking for high, medium, and low impact events
- per-event before/after buffers
- no external economic calendar API

Status: partially implemented.

Remaining TODOs:
- external economic calendar feed is unresolved and not approved
- define official high-impact event source
- define production-grade calendar update workflow

## Rule 6: Session Protection

Spec status: `SESSION_PROTECTION`

Current implementation:
- configurable UTC sessions
- enabled/disabled session windows
- weekend blocking
- invalid time blocking

Status: partially implemented.

Remaining TODOs:
- define session policy per strategy/system
- define daylight saving time policy
- define whether instrument-specific sessions are needed

## Rule 7: Spread Protection

Spec status: `SPREAD_PROTECTION`

Current implementation:
- `SpreadFilterConfig.max_spread`
- unknown spread blocking option
- invalid negative spread block
- too-high spread block

Status: partially implemented.

Remaining TODOs:
- define max spread thresholds per instrument
- define max spread thresholds per session
- define whether thresholds differ by account/data source

## Rule 8: Volatility Protection

Spec status: `VOLATILITY_PROTECTION`

Current implementation:
- ATR-based volatility check
- minimum ATR threshold
- maximum ATR threshold
- abnormal last-candle range check
- invalid or insufficient candle data block

Status: partially implemented.

Remaining TODOs:
- define official volatility thresholds per instrument/timeframe
- define which timeframes are authoritative
- define whether ATR alone is sufficient for abnormal volatility detection

## Rule 9: Emergency Stop

Spec status: `EMERGENCY_STOP`

Current implementation:
- `CapitalProtectionState.emergency_stop`
- highest-priority capital protection block
- `CapitalProtectionDecision.protection_status="EMERGENCY_STOP"`

Status: partially implemented.

Remaining TODOs:
- define who/what can trigger emergency stop
- define reset permission policy
- define persistence and audit trail

## Rule 10: Manual Pause

Spec status: `MANUAL_PAUSE`

Current implementation:
- `CapitalProtectionConfig.manual_pause`
- high-priority capital protection block
- `CapitalProtectionDecision.protection_status="MANUAL_PAUSE"`

Status: partially implemented.

Remaining TODOs:
- define pause/resume control surface
- define whether pause applies to one strategy, one account, or the full platform
- define persistence and audit trail

## Current safe conclusion

The current project has research-only implementations for the main protection categories, but the spec TODOs are not fully resolved because several require explicit policy decisions.

Do not implement external calendar feeds, broker integrations, live execution, MT5 login, Sierra live connection, CME live data connection, paper trading behavior changes, or real order paths from this audit.

## Recommended next step

Keep the implemented metadata-only capital protection status change. Resolve remaining TODOs one policy decision at a time, with tests, before any enforcement or integration change.
