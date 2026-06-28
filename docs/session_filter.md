# Session Filter

## Why Session Filter Exists
The session filter is a safety layer that controls when trading is allowed during paper trading and backtesting.

Its purpose is to avoid low-quality market periods and keep behavior predictable.

This module is research-only:
- no live trading
- no broker connection
- no external API

## UTC Session Times
All session times are UTC.

Default windows:
- London: 07:00 to 16:00 UTC (enabled)
- New York: 13:00 to 21:00 UTC (enabled)
- London New York Overlap: 13:00 to 16:00 UTC (enabled)
- Asian: 00:00 to 06:00 UTC (disabled by default)

The filter can also block weekends for conservative behavior.

## Apex Futures Scalping Use Case
For Apex-style futures scalping, the highest liquidity and cleaner movement often appear around London and New York sessions.

The overlap window is usually treated as a high-focus period because participation is stronger.

## Why Asian Session May Be Disabled
The Asian session can be disabled by default in conservative setups because:
- volatility can be lower for some instruments
- momentum can be weaker or inconsistent
- spread and execution conditions may be less favorable for certain strategies

Disabling it by default helps reduce overtrading during quieter conditions.

## Safe Behavior Rules
- Invalid or missing time blocks trading.
- If filter is disabled, trading is allowed with a clear reason.
- Weekend blocking can be enabled.
- Enabled sessions allow trading.
- Disabled matching sessions block trading.
- If no session matches, trading is blocked.

Naive datetime values are handled safely by treating them as UTC and adding a reason note.

## Future Plan
A future version can support profile-specific session templates so each trading profile can use its own allowed windows.

Example direction:
- Apex profile: stricter London/New York focus
- Spot profile: broader intraday coverage
- Safe profile: heavily restricted schedule
