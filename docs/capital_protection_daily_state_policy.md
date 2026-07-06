# Capital Protection Daily State Policy

## Scope

Documentation-only policy for daily capital protection state. No strategy, risk, broker, live trading, paper trading behavior, MT5, Sierra live, CME live data, external API, or real order path is changed or approved.

## Purpose

Define how one trading day is interpreted for daily loss lock, daily profit target, loss streak reset, daily PnL tracking, and future persistence decisions.

## Current implementation checkpoint

Current implementation is in-memory and decision-only. It already has max daily loss, daily profit target, realized daily PnL, consecutive losses, and optional protection_status metadata.

## Daily reset boundary

Use the UTC calendar day as the default daily reset boundary.

Default daily window: 00:00:00 UTC to 23:59:59 UTC.

Reason: existing session, news, and time filters use UTC-oriented logic, and UTC keeps backtests reproducible without local daylight saving ambiguity.

## Realized PnL basis

Daily realized PnL should use closed trade results only.

Default calculation should include gross closed-trade PnL. Simulated commission and simulated slippage may be included only when those values are available and clearly reported.

When commission or slippage is unavailable, reports must clearly state whether daily PnL is gross or partially simulated.

## Open and unrealized PnL

Open or unrealized PnL should not count toward daily loss lock or daily profit target by default.

Reason: current capital state uses realized_daily_pnl, and realized-only behavior is easier to reproduce and test. Unrealized PnL can fluctuate and should require a separate policy before being used for blocking.

## Daily loss lock and daily profit target

Daily loss lock should trigger when realized_daily_pnl is less than or equal to negative absolute max_daily_loss. The expected protection_status is DAILY_LOSS_LOCK.

Daily profit target should trigger when realized_daily_pnl is greater than or equal to absolute daily_profit_target. The expected protection_status is TARGET_REACHED.

Both checks should use realized PnL only by default.

## Loss streak reset

Default loss streak reset should occur at the UTC daily reset boundary.

Within the same UTC day, a losing closed trade should increment the streak, a winning closed trade should reset the streak to zero, and a breakeven trade should not increment the streak.

Partial-loss behavior is not approved here. It should be defined separately in the loss counting policy.

## Persistence

Current daily capital protection state may remain in-memory for research and backtest mode.

Future persistence must be reviewed separately before implementation. It must define storage location, reset schedule, audit trail, corruption handling, and manual override rules.

This policy does not approve persistent account-state storage.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, external API usage, real order execution, automatic reset schedulers, or persistent account-state storage.

## Test implications for future code changes

Future code changes should prove that daily reset uses UTC, daily loss lock uses realized PnL only, daily profit target uses realized PnL only, open PnL does not affect daily lock by default, and loss streak reset behavior is covered after the loss counting policy is finalized.

## Recommended next step

Write the loss counting policy before changing code, because loss streak behavior depends on how trade outcomes are classified.
