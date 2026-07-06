# Capital Protection Loss Counting Policy

## Scope

Documentation-only policy for how trade outcomes are counted for capital protection loss streak logic.

## Purpose

Define how closed trade outcomes are classified as win, loss, or breakeven before they affect consecutive loss protection.

## Current implementation checkpoint

Current capital protection state already has consecutive loss protection and a LOSS_STREAK protection_status. This policy defines the intended source-of-truth behavior before future code or test changes.

## Source of truth

Loss counting should use finalized closed trade records only. A trade should affect the loss streak only after the position is fully closed and its realized PnL is known.

Open positions, unrealized PnL, floating drawdown, partial fills, pending orders, canceled orders, and rejected orders should not directly increment or reset the loss streak.

## Outcome classification

A closed trade should count as a loss when finalized realized PnL is less than zero.

A closed trade should count as a win when finalized realized PnL is greater than zero.

A closed trade should count as breakeven when finalized realized PnL equals zero.

## Loss streak update rules

A loss should increment the consecutive loss streak by one.

A win should reset the consecutive loss streak to zero.

A breakeven trade should not increment the streak and should not reset the streak by default.

## Partial exits and aggregated trades

Partial exits should not update the loss streak until the full logical trade is closed.

If a strategy splits one intended trade into multiple fills, the fills should be aggregated into one logical trade outcome before loss streak counting.

If aggregation is unavailable, the report must clearly state that each closed record was counted independently.

## Reset behavior

The consecutive loss streak should reset to zero after a winning closed trade.

The streak should also reset at the UTC daily reset boundary defined by capital_protection_daily_state_policy.md.

Cooldown completion should not reset the loss streak by default unless a separate cooldown reset policy is approved.

## Not approved

This policy does not approve broker integration, live trading, paper trading behavior changes, MT5 login, Sierra live connection, CME live data connection, external API usage, real order execution, or automatic cooldown reset behavior.

## Test implications for future code changes

Future code changes should prove that closed losses increment the streak, closed wins reset the streak, breakeven trades do not change the streak by default, partial exits do not update the streak until the logical trade is closed, and UTC daily reset clears the streak.

## Recommended next step

Update the policy decision plan to mark loss counting policy completed after this document is reviewed and committed.
