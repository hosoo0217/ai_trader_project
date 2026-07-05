# Backtest Quality Conditional Cooldown A/B Research Module Checklist

## Purpose

Define the minimum checklist before creating any research-only diagnostic module for conditional cooldown A/B testing.

This checklist does not approve strategy implementation.

## Safety boundary

- No live trading.
- No paper trading.
- No broker connection.
- No MT5 login.
- No Sierra live connection.
- No CME live data connection.
- No external API.
- No real order.
- No change to production strategy behavior.
- No change to risk execution behavior.
- No Order Flow enforcement.

## Allowed scope

The module may only:

- read existing ignored diagnostic JSON files under `private_data`
- reproduce baseline and cooldown variant metrics
- write diagnostic reports under `private_data`
- optionally write tracked summary docs under `docs` after manual review

## Required input

- `executed_trade_replay_snapshots` from existing per-entry replay diagnostic JSON
- `iteration_index`
- `final_action`
- `outcome`
- `simulated_pnl`
- optional replay Order Flow fields for diagnostic labeling only

## Required variants

- A baseline
- B1 global post-loss cooldown 3
- B2 global post-loss cooldown 10
- C1 cooldown after two nearby losses
- C2 cooldown after same-direction nearby losses
- C3 detected loss-cluster-zone cooldown

## Required metrics

- kept trades
- blocked trades
- wins
- losses
- total PnL
- win rate
- profit factor
- max drawdown
- removed winners
- removed losses
- removed PnL
- effect on largest loss clusters

## Rejection conditions

Reject the candidate if:

- it improves only one dataset but damages others materially
- it deletes too many winners relative to removed losses
- it relies on future information not available at decision time
- it requires Order Flow confirmation enforcement
- it touches live, paper, broker, MT5, Sierra live, CME live data, external API, or real order paths

## Acceptance conditions for deeper research

A candidate may move to deeper research only if:

- it improves drawdown consistently
- it improves or preserves PnL across multiple datasets
- it reduces clustered losses without excessive winner deletion
- it can be reproduced from existing trace data
- it remains diagnostic-only

## Current best research candidate

The current best tested candidate is C3 detected loss-cluster-zone cooldown 10.

This is not approved for strategy implementation.

## Next step

Create a research-only script or CLI path that reproduces the conditional cooldown A/B report from ignored `private_data` inputs without changing strategy, risk, broker, live, or paper trading behavior.
