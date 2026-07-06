# Capital Protection Profit Target Policy

## Scope

Documentation-only policy for how daily profit target handling should behave in capital protection logic.

## Purpose

Define whether the daily profit target is a hard stop or soft stop, whether open positions are affected, whether trailing target behavior is allowed, and which reset boundary applies.

## Current implementation checkpoint

Current capital protection logic already has daily_profit_target, realized_daily_pnl, and TARGET_REACHED protection_status metadata. This policy defines intended behavior before future code or test changes.

## Trigger basis

Daily profit target should trigger when realized_daily_pnl is greater than or equal to the absolute daily_profit_target value.

The trigger should use closed-trade realized PnL only by default, matching capital_protection_daily_state_policy.md.

Open and unrealized PnL should not trigger TARGET_REACHED by default.

## Hard stop behavior

Daily profit target should be treated as a new-entry hard stop after TARGET_REACHED is triggered.

After the target is reached, new entries should be blocked for the rest of the UTC daily window by default.

This policy does not require forced closing of already-open positions.

## Open position handling

Already-open positions should be managed by the existing strategy or test harness rules.

TARGET_REACHED should block new entries by default, but it should not automatically close, reduce, reverse, or modify existing positions without a separate approved exit policy.

Reports should clearly state whether any open-position behavior was simulated separately from this policy.

## Trailing profit target

Trailing daily profit target behavior is not approved by default.

The default profit target should remain a fixed daily threshold for the UTC daily window.

Any trailing target behavior must be defined in a separate policy before implementation.

## Reset boundary

TARGET_REACHED should reset at the UTC daily reset boundary defined by capital_protection_daily_state_policy.md.

After the reset boundary, new entries may be allowed again only if all other capital protection checks also allow trading.

This policy does not approve any independent scheduler or persistent reset mechanism.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, external API usage, real order execution, forced position closing, trailing target behavior, or independent reset schedulers.

## Test implications for future code changes

Future code changes should prove that TARGET_REACHED is triggered by realized daily PnL only, new entries are blocked after the target is reached, already-open positions are not automatically closed or modified, trailing target behavior is not enabled by default, and the target resets at the UTC daily boundary.

## Recommended next step

Update the policy decision plan to mark profit target policy completed after this document is reviewed and committed.
