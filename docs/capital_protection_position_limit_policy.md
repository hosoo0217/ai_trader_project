# Capital Protection Position Limit Policy

## Scope

Documentation-only policy for how maximum position limits should behave in capital protection logic.

## Purpose

Define whether maximum position limits are global, per-system, per-instrument, account-specific, and whether pending orders count toward the limit.

## Current implementation checkpoint

Current capital protection logic already has max_open_positions, open_positions, and MAX_POSITIONS protection_status metadata. Paper broker and trading profile code also use max_open_positions, but this policy defines intended capital protection behavior before future enforcement changes.

## Trigger basis

MAX_POSITIONS should trigger when open_positions is greater than or equal to max_open_positions and max_open_positions is greater than zero.

A max_open_positions value of zero should mean the position limit check is disabled by default, matching the current capital protection behavior.

## Limit scope

By default, max_open_positions should be interpreted as a global limit for the capital protection state being evaluated.

This policy does not approve automatic per-system, per-strategy, per-instrument, or account-specific position limit behavior unless that scope is explicitly provided by the caller and covered by tests.

Reports should clearly state which scope was used when position-limit behavior is simulated or evaluated.

## Pending orders

Pending orders should not count toward MAX_POSITIONS by default because current capital protection state tracks open_positions, not pending_orders.

Pending-order counting must not be added implicitly. It requires a separate explicit state field, policy update, and tests before enforcement.

## New-entry behavior

MAX_POSITIONS should act as a new-entry block by default.

When the limit is reached, capital protection should block additional entries but should not automatically close, reduce, reverse, or modify already-open positions.

Existing positions should continue to be managed by the existing strategy, paper broker, or test harness rules.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, external API usage, real order execution, automatic position closing, automatic position reduction, implicit per-instrument limits, implicit per-account limits, or pending-order counting.

## Test implications for future code changes

Future code changes should prove that MAX_POSITIONS triggers when open_positions is greater than or equal to max_open_positions, max_open_positions equal to zero disables the check, the default scope is global to the evaluated capital protection state, pending orders do not count by default, and already-open positions are not automatically closed or modified.

## Recommended next step

Update the policy decision plan to mark position limit policy completed after this document is reviewed, indexed, and committed.
