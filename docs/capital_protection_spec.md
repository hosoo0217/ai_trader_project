# Capital Protection Engine Specification

## Purpose
The Capital Protection Engine exists to protect trading capital before generating profit. It is the highest-authority safety layer in the system.

If this engine says "NO", no trade may be executed.

## Design Principles
- Capital preservation is more important than profit.
- No trade is better than a bad trade.
- Safety rules must be enforced before execution.
- The engine should be modular, testable, and explainable.
- This is a specification for future implementation, not trading logic.

## Authority and Enforcement
The Capital Protection Engine has priority over all other decision layers.

If any protection rule blocks trading, the system must:
- reject new entries
- cancel pending permissions where applicable
- preserve existing risk controls
- report the current protection state clearly

## Protection Statuses
The engine may return one or more protection states, including:
- DAILY_LOSS_LOCK
- TARGET_REACHED
- LOSS_STREAK
- MAX_POSITIONS
- NEWS_PROTECTION
- SESSION_PROTECTION
- SPREAD_PROTECTION
- VOLATILITY_PROTECTION
- EMERGENCY_STOP
- MANUAL_PAUSE

## Rule 1: Daily Loss Limit
### Purpose
Prevent excessive daily drawdown.

### Behavior
The engine tracks realized daily loss.

If the configured daily loss limit is reached:
- close all pending permissions
- reject every new trade
- lock trading until the next trading day

### Status
DAILY_LOSS_LOCK

### TODO
- Define configuration values for daily loss thresholds.
- Define how the engine resets at the start of the next trading day.
- Define whether realized loss includes commissions and slippage.

## Rule 2: Daily Profit Target
### Purpose
Prevent overtrading after reaching a daily profit goal.

### Behavior
If the daily profit target is reached:
- stop opening new trades
- allow existing trades to continue according to their rules
- resume trading on the next day

### Status
TARGET_REACHED

### TODO
- Define whether the target is hard-stop or soft-stop.
- Decide whether trailing profit targets should be supported.
- Define if open positions are allowed to continue after target hit.

## Rule 3: Consecutive Losses
### Purpose
Reduce the chance of emotional or revenge trading after a losing streak.

### Behavior
The engine tracks losing trades.

If the maximum consecutive losses is reached:
- pause trading
- require a cooldown period before new trades are allowed

### Status
LOSS_STREAK

### TODO
- Define how a loss is counted.
- Decide whether partial losses or closed trades only count.
- Decide how the cooldown is reset.

## Rule 4: Maximum Open Positions
### Purpose
Limit simultaneous exposure.

### Behavior
The engine enforces a maximum number of open positions.

If the limit is reached:
- block new entries
- allow existing trades to remain open until they are closed or managed

### Status
MAX_POSITIONS

### TODO
- Define separate limits for each system.
- Decide whether limits differ by instrument or account type.

## Rule 5: News Protection
### Purpose
Avoid entering trades during high-impact market events when risk is unpredictable.

### Behavior
Future integration.

High-impact news events should trigger:
- no new positions
- tighter monitoring of existing trades

### Status
NEWS_PROTECTION

### TODO
- Integrate an economic calendar feed.
- Define which news events are considered high impact.
- Decide whether to pause trading only for the event window or also for a buffer period.

## Rule 6: Session Protection
### Purpose
Only allow trading during configured sessions.

### Behavior
Trading is allowed only during authorized sessions such as:
- London
- New York
- Overlap

If a session is disabled, entries during that session should be rejected.

### Status
SESSION_PROTECTION

### TODO
- Define configurable session schedules.
- Decide whether session rules differ by system.
- Define handling for timezone conversion and daylight saving time.

## Rule 7: Spread Protection
### Purpose
Avoid low-quality entries when spreads are too wide.

### Behavior
The engine rejects entries if the spread exceeds the configured threshold.

### Status
SPREAD_PROTECTION

### TODO
- Define max spread thresholds per instrument and session.
- Decide whether spread checks should occur before every entry attempt.

## Rule 8: Volatility Protection
### Purpose
Avoid entering trades when market volatility is abnormal.

### Behavior
The engine rejects entries if volatility is outside the acceptable range.

### Status
VOLATILITY_PROTECTION

### TODO
- Define volatility measurement method.
- Decide which timeframes should be considered.
- Define how abnormal volatility should be detected.

## Rule 9: Emergency Stop
### Purpose
Provide a global kill switch for the platform.

### Behavior
The emergency stop immediately disables every trading engine.

No new trades may be opened while the emergency stop is active.

### Status
EMERGENCY_STOP

### TODO
- Define how the emergency stop is triggered.
- Decide whether it can be reset by the user or only by an administrator.

## Rule 10: Manual Pause
### Purpose
Allow a human operator to pause trading manually.

### Behavior
The user may pause trading at any time.

While manual pause is active:
- no new trades are allowed
- existing positions may be reviewed but not re-entered unless explicitly resumed

### Status
MANUAL_PAUSE

### TODO
- Define how pause and resume controls are exposed.
- Decide whether manual pause affects only one system or the entire platform.

## Decision Priority
The protection engine must evaluate rules in the following order:

Emergency Stop
↓
Daily Loss
↓
Profit Target
↓
Session
↓
News
↓
Spread
↓
Volatility
↓
Risk
↓
Decision Engine

## Future Implementation Notes
The following components are expected in future implementation:
- configuration loader for thresholds and session windows
- state tracker for daily PnL and loss streaks
- interface for checking whether trading is currently allowed
- event system for news, session, spread, and volatility changes
- clear reporting of the blocking reason for each decision

## Summary
The Capital Protection Engine is the highest-priority safety layer. It exists to ensure that no trade can occur when the market, account state, or platform conditions are not safe enough.
