# Backtest Quality Conditional Cooldown A/B Diagnostic Plan

## Safety scope

This is a research-only A/B diagnostic plan.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated reports must remain under ignored `private_data`.

## Background

The full 5m loss-cluster diagnostic showed that the largest drawdown contributor came from repeated losses during local clusters.

The post-loss cooldown candidate diagnostic showed strong improvement on the full 5m run.

The multi-timeframe robustness diagnostic showed that cooldown is not robust enough as a simple global rule because 10m results were mixed and cooldown 2/3 turned negative.

Therefore the next research step is not to implement cooldown directly. The next step is to test cooldown as a conditional A/B diagnostic.

## Decision

Do not implement a global cooldown rule.

Do not enforce Order Flow confirmation.

Keep Order Flow diagnostic-only.

Test cooldown only as a research diagnostic, preferably conditional on local loss-cluster behavior.

## Candidate A/B variants

| Variant | Description | Purpose |
|---|---|---|
| A | Baseline current behavior | Control. |
| B1 | Global post-loss cooldown 3 | Check balanced cooldown candidate. |
| B2 | Global post-loss cooldown 10 | Check strongest full 5m but high over-filter risk. |
| C1 | Cooldown only after two losses within nearby iterations | Target clusters instead of every loss. |
| C2 | Cooldown only after same-direction repeated losses | Test re-entry failure without blocking all actions. |
| C3 | Cooldown only inside detected loss-cluster zones | Test cluster-specific drawdown control. |

## Required metrics

Each variant must report:
- executed trades
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
- effect on largest known loss clusters

## Acceptance criteria

A candidate should not be accepted unless it:
- improves max drawdown materially
- improves profit factor
- does not rely only on deleting sample size
- does not remove too many winners
- works better than Order Flow alignment alone
- is checked across at least 1m, 5m, and 10m diagnostic data

## Rejection criteria

Reject a candidate if:
- it improves only the full 5m run but fails 10m badly
- it reduces trade count too aggressively
- it improves win rate but lowers total PnL without clear drawdown benefit
- it duplicates Order Flow filtering logic
- it touches live, paper, broker, MT5, Sierra live, CME live data, external API, or real order paths

## Next concrete task

Create a no-code A/B diagnostic script or report generator that reads existing ignored diagnostic JSON files and writes candidate comparison reports under `private_data`.

Only after the A/B diagnostic is documented and reviewed should any implementation be considered.
