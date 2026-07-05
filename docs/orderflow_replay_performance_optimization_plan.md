# Order Flow replay performance optimization plan

## Scope

This document plans a performance optimization for the diagnostic-only Order Flow replay path.

This plan does not approve or change:
- strategy execution
- entry rules
- exit rules
- risk behavior
- broker behavior
- paper trading
- live trading
- MT5 login
- Sierra live connection
- CME live data connection
- real order paths
- external API behavior

## Problem

The current per-entry Order Flow replay diagnostic export works correctly, but replay can become slow on larger runs.

Observed behavior:
- 200-iteration validation runs completed successfully.
- Full 5m diagnostic run reached backtest completion but became slow during replay export.
- The replay engine currently recalculates Delta/CVD over `candles_so_far` for every replay step.
- This creates repeated work and can behave like an O(n^2) replay path on larger footprint datasets.

Current 200-iteration validation remained correct:
- 1m: A +20, non-neutral -10, aligned 0
- 5m: A +270, non-neutral +95, aligned +45
- 10m: A +15, non-neutral -35, aligned -35

## Goal

Make diagnostic replay export faster while preserving the same diagnostic results.

The first target is to optimize replay snapshot generation for export use, not to change trade logic.

## Non-goals

Do not:
- enforce Order Flow confirmation
- change DecisionEngine behavior
- change PaperTradingFlow execution behavior
- change BacktestRunner trade simulation behavior
- change risk sizing
- connect to broker/live data
- include `private_data` in Git

## Proposed design

Add or refactor a replay path that builds per-candle Order Flow snapshots incrementally.

Instead of recalculating Delta/CVD from the full historical candle list at every step, maintain running state such as:
- cumulative delta
- previous cumulative delta
- delta direction
- current candle imbalance result
- current candle absorption result
- combined Order Flow context for the current step

The optimized path should produce the same per-step fields used by the diagnostic export:
- index
- time
- candle_delta
- cumulative_delta
- delta_direction
- imbalance_bias
- absorption_bias
- orderflow_bias
- orderflow_confidence
- reasons
- blocking_reasons

## Implementation stages

### Stage 1: Baseline and guard tests

Add tests that compare current replay snapshots against optimized replay snapshots on a small fixture.

Required assertions:
- same number of steps
- same step indexes
- same cumulative delta
- same delta direction
- same imbalance bias
- same absorption bias
- same combined Order Flow bias
- same confidence where deterministic

### Stage 2: Incremental replay builder

Create an internal incremental snapshot builder for diagnostic replay.

Possible names:
- `OrderFlowIncrementalReplayEngine`
- `OrderFlowReplaySnapshotBuilder`
- `OrderFlowReplayEngine.replay_incremental`

The implementation should avoid changing the public report schema unless necessary.

### Stage 3: Wire diagnostic export to optimized path

Use the optimized replay path only inside per-entry diagnostic export.

The export should still:
- match executed trades by `window_end`
- compute current A behavior
- compute non-neutral snapshot behavior
- compute direction-aligned snapshot behavior
- write the same JSON/TXT report filenames

### Stage 4: Validate with existing Sierra delayed datasets

Re-run the same validation:

| Timeframe | Expected A PnL | Expected non-neutral PnL | Expected aligned PnL |
|---|---:|---:|---:|
| 1m | 20.00 | -10.00 | 0.00 |
| 5m | 270.00 | 95.00 | 45.00 |
| 10m | 15.00 | -35.00 | -35.00 |

The optimized path must reproduce these values.

### Stage 5: Full-run performance check

After correctness is confirmed, run a larger diagnostic export.

Target:
- full 5m diagnostic export should complete without manual interruption
- no change to backtest result
- no tracked `private_data` changes

## Acceptance criteria

The optimization is acceptable only if:
- all focused replay tests pass
- all related backtest/export tests pass
- full test suite passes
- 1m/5m/10m 200-iteration validation results remain unchanged
- diagnostic JSON/TXT schema remains compatible
- no strategy/risk/live/paper/broker behavior changes
- `git status --short` stays clean after generated reports remain under ignored `private_data`

## Decision

Proceed only with performance optimization for diagnostic replay export.

Do not enforce Order Flow confirmation.
