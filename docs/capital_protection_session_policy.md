# Capital Protection Session Policy

## Scope

Documentation-only policy for how session filtering should behave before any future production enforcement or integration change.

## Purpose

Define the official default session schedule, timezone basis, daylight saving behavior, weekend blocking, and instrument-specific session restrictions for capital protection documentation.

## Current implementation checkpoint

Current session filtering uses UTC session windows, treats naive datetimes as UTC with a reason note, converts timezone-aware datetimes to UTC, can block weekends, and has no broker, exchange, live data, or external API connection.

## Default session schedule

The default documented session basis should remain UTC.

Default enabled sessions are London 07:00 to 16:00 UTC, New York 13:00 to 21:00 UTC, and London New York Overlap 13:00 to 16:00 UTC.

The Asian session 00:00 to 06:00 UTC should remain disabled by default unless a strategy-specific policy explicitly enables it.

## Timezone and daylight saving policy

UTC should remain the default and authoritative session basis.

Local exchange timezone conversion and daylight saving time adjustment should not be added implicitly. Any exchange-local schedule or DST-aware behavior must be defined in a separate explicit policy and covered by tests.

## Weekend behavior

Weekend blocking should remain enabled by default for conservative behavior.

If weekend trading is allowed for a specific strategy or market, that exception must be explicitly documented and covered by tests before enforcement.

## Instrument-specific sessions

Instrument-specific session schedules are not approved by default.

The default policy should not infer a separate schedule for futures, forex, crypto, indices, or metals unless the caller provides an explicit strategy or instrument policy and tests cover that behavior.

Reports should clearly state whether the default UTC schedule or an explicit instrument-specific schedule was used.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, exchange calendar API usage, external API usage, real order execution, local exchange timezone conversion, automatic daylight saving adjustment, or implicit instrument-specific sessions.

## Test implications for future code changes

Future code changes should prove that UTC is the authoritative session basis, naive datetimes are treated as UTC with a reason note, timezone-aware datetimes are converted to UTC, weekend blocking works when enabled, disabled sessions block trading, outside-session times block trading, and no exchange calendar or external API is required.

## Recommended next step

Update the policy decision plan to mark session policy completed after this document is reviewed, indexed, and committed.
