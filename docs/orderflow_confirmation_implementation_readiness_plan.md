# Order Flow Confirmation Implementation Readiness Plan

This document is a documentation-only readiness plan for the proposed Order Flow confirmation rule.

It does not implement the rule. It does not change strategy execution code, risk rules, broker behavior, live trading behavior, paper trading behavior, MT5 login behavior, Sierra live trading behavior, CME data behavior, or external API behavior.

## 1. Why This Rule Is Being Considered

The proposed Order Flow confirmation rule is being considered because recent validation found a repeated safety pattern:

- Matching ACSIL full footprint imports worked across multiple validation runs.
- Data quality passed on the tested ACSIL full footprint datasets.
- Day2 validation covered matching market OHLC plus matching ACSIL full footprint data across 1m, 5m, and 10m.
- The 5m day2 runs allowed losing trades while Order Flow was `NEUTRAL` with `0.0` confidence.
- The 10m day2 runs allowed losing trades while Order Flow was still effectively not confirming the trade direction; Order Flow remained `NEUTRAL` and confidence stayed below the configured minimum.
- The simulated B diagnostic would have blocked all observed neutral Order Flow losing trades in those 5m and 10m runs.

This is useful safety evidence.

It suggests the current decision flow may be too permissive when Apex execution is allowed while Order Flow is neutral or below the configured confidence threshold.

This is not profitability proof.

The simulated B behavior blocked the observed losing trades, but it also blocked every observed executed trade in the recorded validation samples. Avoiding losing trades is not the same as proving that enough valid winning trades remain. More evidence and explicit approval are required before any execution rule changes.

## 2. What The Proposed Rule Would Do

If approved later, the proposed rule would add a positive Order Flow confirmation requirement before Apex execution.

The intended behavior would be:

- Block Apex execution when Order Flow bias is `NEUTRAL`.
- Block Apex execution when Order Flow confidence is below the configured minimum.
- Block or prevent trust in Order Flow when data quality fails.
- Allow future `BUY` execution only when Order Flow bias is `BULLISH` and confidence meets the configured minimum.
- Allow future `SELL` execution only when Order Flow bias is `BEARISH` and confidence meets the configured minimum.
- Preserve research-only A/B diagnostics so proposed behavior can still be compared without changing live or paper behavior.

This is not approved implementation yet.

This document only defines readiness requirements and likely implementation boundaries. It does not authorize code changes.

## 3. Files Likely Involved Later

Likely future code areas, if HOSOO approves implementation later:

- `main.py`: CLI integration, backtest wiring, diagnostic output, and places where Order Flow context is passed into result reporting.
- `core/backtest_runner.py`: Backtest decision flow, execution blocking, trace reasons, and iteration results if this is where final simulated execution decisions are made.
- Decision-flow modules, if separate from `core/backtest_runner.py`: Any module that converts analysis context into `BUY`, `SELL`, or `NO_TRADE`.
- `orderflow/orderflow_context.py`: Existing Order Flow bias, confidence, and blocking reason model. This may need no rule change if it already exposes enough information.
- `core/safety_gate.py`: Only if the project decides Order Flow confirmation belongs in the safety gate path. This should be handled carefully because risk and safety logic must not be weakened.
- Risk / execution path modules: Only if they currently own final permission to execute simulated trades.
- Tests related to backtest behavior, Order Flow context, Order Flow CLI output, A/B diagnostics, safety gates, and paper-flow integration.

This plan does not require changing any of those files now.

## 4. Required Tests Before Implementation Approval

Before implementation approval, the exact test categories should be defined and reviewed.

Required test categories:

- Neutral Order Flow blocks execution.
- Low-confidence Order Flow blocks execution.
- A bullish trade requires bullish Order Flow confirmation.
- A bearish trade requires bearish Order Flow confirmation.
- Data quality failure blocks execution or prevents Order Flow trust.
- Missing Order Flow data fails safely and does not crash the decision flow.
- A/B diagnostic remains research-only and does not become the execution path.
- Existing report generation remains documentation/research output only.
- No live trading behavior changes.
- No broker behavior changes.
- No MT5 login behavior changes.
- No Sierra live trading behavior changes.
- No CME live data behavior changes.
- No external API behavior changes.
- Existing 829 tests remain passing.

Suggested implementation-test shape:

- Add unit tests for the smallest rule function or decision boundary.
- Add integration tests showing `BUY` plus non-bullish Order Flow becomes blocked.
- Add integration tests showing `SELL` plus non-bearish Order Flow becomes blocked.
- Add regression tests proving the simulated A/B diagnostic still reports simulated behavior without changing current behavior unless the approved rule path is explicitly enabled.
- Add CLI/backtest output tests for clear blocking reasons.

Tests should be written before or alongside any implementation, not after the behavior is already assumed correct.

## 5. Rollback Plan

If a future implementation causes unexpected behavior, rollback should be simple and conservative.

Rollback strategy:

- Create a clean git checkpoint before implementation.
- Keep the implementation in a small isolated branch or single focused commit.
- Keep tests and implementation scoped to Order Flow confirmation only.
- Do not combine this change with risk changes, broker changes, paper trading changes, importer changes, or advanced footprint modules.
- If behavior is wrong, revert the implementation commit with `git revert`.
- Re-run the full pytest baseline after revert.
- Re-run the known validation commands used for the checkpoint.

Git checkpoint strategy:

- Confirm `main` is clean before implementation.
- Record latest passing commit hash.
- Tag or otherwise note the pre-implementation baseline.
- Commit tests and implementation with a clear message.
- Avoid committing private Sierra data or generated report files.

Test baseline strategy:

- Preserve the current `829 passed` baseline.
- Run `.\venv\Scripts\python.exe -m pytest -q` before implementation.
- Run the same command after implementation.
- Compare affected backtest and Order Flow CLI outputs against expected blocking behavior.

## 6. Human Approval Checklist

HOSOO must approve all checklist items before any code implementation:

- [ ] Evidence reviewed.
- [ ] Matching ACSIL validation reviewed.
- [ ] Day2 5m and 10m neutral / low-confidence loss pattern reviewed.
- [ ] Simulated B limitations reviewed, including the risk that B blocked every observed executed trade.
- [ ] Required tests defined.
- [ ] Implementation scope understood.
- [ ] No live trading approved.
- [ ] No broker connection approved.
- [ ] No MT5 login approved.
- [ ] No Sierra live trading connection approved.
- [ ] No CME live data connection approved.
- [ ] No external API calls approved.
- [ ] No `private_data` commit approved.
- [ ] Generated report commit policy understood.
- [ ] Rollback plan ready.
- [ ] Test baseline ready.
- [ ] Paper trading remains disabled unless separately approved.
- [ ] Live trading remains disabled.

Approval of this checklist would approve planning for an implementation step only. It would not approve live trading, broker integration, or paper trading deployment.

## 7. Final Recommendation

Do not implement the Order Flow confirmation rule in this task.

The current evidence supports continued safety validation and a careful implementation-readiness process. It does not prove profitability, and it does not yet prove the rule preserves enough valid trade opportunities.

The next possible step after explicit HOSOO approval is a small isolated implementation branch or focused commit with tests first.

Keep this work research-only. Keep paper trading disabled. Keep live trading disabled. Do not add broker connections, MT5 login, Sierra live trading, CME live data, or external API calls.
