# Research Drawdown Acceptance Criteria

## Purpose

Define the evidence and approval requirements for selecting a research backtest maximum-drawdown percentage threshold.

This document is research-only. It does not approve paper trading, broker integration, live data, live trading, or any strategy or risk-rule implementation.

## Measurement contract

Eligible drawdown evidence must use:

- realized monetary PnL calculated with the correct instrument point value
- peak-to-trough max drawdown across the full realized trade sequence
- a positive starting account balance
- normalized drawdown calculated as:

`drawdown_percent = max_drawdown / starting_balance * 100`

Pre-point-value-correction monetary reports are not eligible as direct threshold evidence.

## Threshold scope

A single universal threshold must not be assumed for every profile.

Any proposed threshold must identify:

- the trading profile
- starting balance
- instrument and point value
- timeframe
- dataset period
- executed-trade count
- normalized max drawdown
- whether the dataset is development, validation, or independent validation evidence

A threshold approved for one profile must not be copied automatically to another profile.

## Minimum evidence requirements

A numerical threshold must remain unapproved unless all of the following are satisfied:

- the run has at least 30 iterations
- the run has at least 20 executed trades
- total PnL is positive when positive PnL is required
- win rate is at least the configured quality minimum
- profit factor is at least the configured quality minimum
- drawdown is calculated from point-value-corrected monetary results
- matching market and Order Flow data quality passes when Order Flow data is included
- at least one genuinely independent, non-overlapping historical period is evaluated
- development-period subsets are not presented as independent evidence
- timeframe and market-regime results are reported separately
- the proposed threshold is not selected only to make the best-performing run pass

Meeting these minimums permits threshold review only. It does not guarantee approval.

## Acceptance behavior

After a positive threshold is explicitly approved and configured:

- a run fails when normalized drawdown exceeds the approved threshold
- a run receives a warning when normalized drawdown exceeds 80% of the approved threshold
- missing or non-positive account balance fails closed
- missing or non-positive threshold fails closed
- insufficient iterations or executed trades remain `INSUFFICIENT_DATA`
- passing drawdown alone does not override failures in PnL, win rate, profit factor, data quality, or other quality gates

## Current corrected Apex evidence

Current matched 200-iteration Apex results are:

| Timeframe | Executed trades | Normalized max drawdown | Quality interpretation |
|---|---:|---:|---|
| 1m | 18 | 1.20% | Insufficient executed trades |
| 5m | 38 | 0.60% | Other metrics pass; drawdown threshold is not configured |
| 10m | 46 | 2.20% | Win rate and profit factor fail |

These results come from the current local historical period and its subsets.

They are useful diagnostic evidence but are not sufficient to approve a numerical threshold because no genuinely independent, non-overlapping local historical period is currently available.

The 5m result must not be used alone to tune a threshold around the best-performing timeframe.

## Current decision

- Numerical research drawdown threshold: **NOT APPROVED**
- Universal cross-profile threshold: **NOT ALLOWED**
- Independent validation evidence: **BLOCKED BY MISSING NON-OVERLAPPING DATA**
- Existing quality behavior: **FAIL CLOSED**
- Strategy or risk implementation approval: **NONE**
- Paper or live deployment approval: **NONE**

## Approval requirement

A numerical threshold may be configured only after:

1. eligible independent evidence is collected and documented
2. results are reviewed against every criterion in this document
3. a profile-specific threshold and rationale are written explicitly
4. HOSOO provides explicit human approval
5. any proposed code or configuration change is reviewed separately

Until those steps are complete, `max_drawdown_percent_allowed` must remain `None`.
