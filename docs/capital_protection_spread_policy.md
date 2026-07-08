# Capital Protection Spread Policy

## Scope

Documentation-only policy for how spread protection should behave before any future production enforcement, broker integration, live data integration, or simulation expansion.

## Purpose

Define conservative spread threshold behavior, unknown-spread handling, instrument and session threshold guardrails, and account or data-source restrictions for capital protection decisions.

## Current implementation checkpoint

Current spread filtering is research-only. The filter is enabled by default, uses max_spread 3.0 by default, blocks unknown spread by default, blocks negative spread as invalid, blocks spread greater than max_spread, and allows spread values less than or equal to max_spread.

## Profile behavior

FUTURES_PROP profiles currently use max_spread 3.0 and allow unknown spread by configuration. SPOT_GOLD profiles currently use max_spread 3.0 and block unknown spread. Fallback profiles use max_spread 0.0 and block unknown spread for conservative safety.

## Resolved policy

Spread protection should run before every new entry attempt when spread configuration is available in the evaluated flow.

Thresholds should remain explicitly configured. Instrument-specific thresholds are not approved implicitly and must be documented, configured, and tested before use.

Session-specific thresholds are not approved implicitly. Wider session thresholds, rollover exceptions, or low-liquidity exceptions require explicit policy, configuration, and tests.

Unknown spread should remain blocked by default for conservative safety. Unknown spread may be allowed only when an explicit profile configuration approves it and tests cover that behavior.

Account-specific and data-source-specific spread behavior should not be inferred automatically. Any difference by account type, broker feed, CSV source, or simulation input must be explicit in configuration, documentation, and tests.

Spread protection blocks or allows new entries only. It does not automatically close, reduce, reverse, or modify already-open positions.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, exchange calendar API usage, external API usage, real order execution, automatic broker spread lookup, automatic feed-specific threshold inference, automatic session threshold widening, or automatic position changes.

## Test implications for future code changes

Future code changes should prove default unknown-spread blocking, configured unknown-spread allowance, negative-spread blocking, too-high-spread blocking, allowed normal spread, disabled-filter allowance, profile-specific behavior, and no broker or external API dependency.

## Recommended next step

Update the policy decision plan to mark spread policy completed after this document is reviewed, indexed, and committed.
