# SMC v2 and Volume Profile Implementation Plan

## 1. Record Status

- Document status: `ACCEPTED FOR BOUNDED FREEZE-LIFT REVIEW`.
- Work type: documentation-only architecture, test, safety, and continuity plan.
- Baseline Git commit: `c8327f76d4e436520b5713c2a6ca33559a6b7c41`.
- Baseline branch: `main`.
- Baseline regression: `881 passed` on `2026-07-18` using
  `.\venv\Scripts\python.exe -m pytest -q`.
- Code-freeze status: `ACTIVE`.
- Strategy implementation authorization: `NOT GRANTED BY THIS DOCUMENT`.
- Paper-trading authorization: `NOT GRANTED`.
- Live-trading authorization: `NOT GRANTED`.
- Broker, Sierra live, CME live, MT5, and external-API authorization: `NOT GRANTED`.

This document does not lift the active code freeze. It prepares a bounded future
change package that must pass the repository's proposal, review, implementation
plan, final review, readiness, freeze-lift, and explicit human-approval gates
before implementation begins.

## 2. Objective

Design a backward-compatible, deterministic, explainable, test-first SMC v2 and
historical Volume Profile research layer without changing the current strategy,
risk behavior, execution decisions, or previously preserved evidence.

The future research layer is intended to add:

1. Fair Value Gap (FVG).
2. Order Block.
3. Breaker Block.
4. Mitigation Block.
5. Premium, Equilibrium, and Discount zones.
6. Equal High and Equal Low liquidity pools.
7. Internal and External liquidity mapping.
8. Inducement candidates.
9. Dealing Range.
10. Kill-zone-specific SMC context.
11. Historical price-level Volume Profile.

Fibonacci analysis is explicitly excluded from this change package.

## 3. Why This Must Be a New Version

The current SMC implementation combines market structure, BOS/CHOCH, and a
simple liquidity sweep into a summarized context. The current Order Flow layer
supports historical full-footprint import, Delta/CVD, basic imbalance, basic
absorption, and research replay, but it does not implement a complete session or
anchored Volume Profile.

The locked July OOS result classified the frozen system as
`VALID_OOS_EVIDENCE — PERFORMANCE_FAILED`. New concepts must not be tuned on that
observed outcome or presented as a favorable rerun of the same strategy. Any
future decision-affecting integration must use a new strategy version and a new,
unseen, pre-registered validation sequence.

## 4. Non-Negotiable Compatibility Contract

Future implementation must preserve all of the following until a later,
separately approved decision-integration phase:

- Existing public dataclass fields, function signatures, CLI defaults, and
  report meanings.
- Existing Market Structure, BOS/CHOCH, Liquidity Sweep, SMCContext, CRT,
  Order Flow, DecisionContext, risk, session, news, spread, volatility, and
  exit behavior.
- Current behavior when every new feature flag is disabled.
- Existing tests and historical golden captures.
- Existing OOS evidence and its failed classification.
- Offline-only behavior and the absence of broker or live-data connectivity.

New modules must be disabled by default. Detector output may be exported for
diagnostic research only; it must not block, approve, resize, enter, exit, or
otherwise alter a simulated trade during the detector phase.

## 5. Canonical Input and Time Rules

### 5.1 Closed-bar rule

At decision index `t`, a detector may use only bars and footprint levels that
were fully closed and available at `t`. A later candle may confirm an earlier
swing, but the swing becomes usable only at the later confirmation time. Tests
must fail if a result is emitted earlier than its confirmation time.

### 5.2 Required Market fields

- UTC-normalized timestamp.
- Open, High, Low, Close.
- Stable chronological source index.
- Instrument tick size supplied by configuration or locked metadata.
- Timeframe supplied explicitly rather than inferred silently.

### 5.3 Required Volume Profile fields

Official Volume Profile output requires full price-level footprint rows:

- bar timestamp or stable bar index,
- traded price level,
- bid volume,
- ask volume,
- total volume or a validated bid-plus-ask derivation.

`BAR_SUMMARY` data may be used for import smoke tests but must be rejected as an
official Volume Profile source. Distributing one bar's total volume across its
price range or assigning it only to the close would be an approximation and
must not be mislabeled as a true Volume Profile.

### 5.4 Session and timezone rule

All internal calculations use UTC. Display or exchange-local session labels may
be derived only through an explicit timezone and daylight-saving-aware calendar.
Naive local timestamps must fail closed for kill-zone classification.

## 6. Proposed Domain Models

Each detector should return an immutable or effectively immutable result with:

- source and confirmation indices,
- source and confirmation timestamps,
- direction or side,
- price boundaries,
- lifecycle state,
- invalidation reason,
- evidence list,
- data-quality status,
- deterministic trace identifier.

Zone lifecycle vocabulary should be shared where applicable:

`DETECTED -> ACTIVE -> PARTIALLY_TOUCHED -> MITIGATED | INVALIDATED | EXPIRED`

Results must distinguish the price event index from the index at which the event
became knowable. This distinction is required to prevent look-ahead leakage.

## 7. Detector Specifications to Lock Before Coding

The following definitions are proposed starting contracts. Any change must be
made in this document before outcome data is used.

### 7.1 Fair Value Gap

- Bullish three-candle FVG at closed bar `i`: `Low[i] > High[i-2]`.
- Bearish three-candle FVG at closed bar `i`: `High[i] < Low[i-2]`.
- The price interval between those two boundaries is the initial gap.
- Detection is available only after bar `i` closes.
- Minimum gap size must be expressed in instrument ticks; an optional ATR filter
  may be studied only as a separately locked diagnostic parameter.
- The result must record untouched, partial-fill, full-mitigation, invalidation,
  and expiry states without rewriting its original boundaries.
- Wick-touch and close-through semantics must be separate configuration choices.

### 7.2 Equal High and Equal Low

- Candidate points must come from already confirmed swing points.
- Equality uses a locked tick-based tolerance; ATR-based tolerance, if studied,
  must be a separate pre-registered variant.
- A liquidity pool requires a locked minimum number of touches and minimum bar
  separation.
- A pool remains active until a locked sweep, close-through invalidation, or
  expiry rule occurs.
- Cluster price, member swing IDs, first-known time, and invalidation must be
  traceable.

### 7.3 Internal and External Liquidity

- External liquidity is derived from confirmed range-defining or major swing
  extremes.
- Internal liquidity is derived from confirmed subordinate swings and equal
  high/low pools inside the active dealing range.
- Classification must come from an explicit swing hierarchy, never from visual
  hindsight.
- Reclassification is versioned and timestamped; old trace records are not
  mutated silently when a later swing becomes external.

### 7.4 Dealing Range

- A dealing range is bounded by confirmed opposing external swing extremes.
- The range must record its construction event, direction, low, high, midpoint,
  source swings, confirmation time, and invalidation.
- Ambiguous or incomplete ranges return `UNKNOWN`; the detector must not invent
  a range only to enable downstream signals.
- Nested internal ranges may be reported separately but must not replace the
  active external range without an explicit transition rule.

### 7.5 Premium, Equilibrium, and Discount

- These zones exist only when a valid dealing range exists.
- Equilibrium is the arithmetic midpoint of the locked range.
- Prices below equilibrium are Discount and prices above equilibrium are
  Premium; midpoint equality is Equilibrium.
- The interpretation must carry the dealing-range ID and direction so that a
  bare price level cannot be mistaken for directional confirmation.

### 7.6 Order Block

Before coding, the human-reviewed specification must lock:

- the qualifying displacement definition,
- whether BOS or CHOCH confirmation is mandatory,
- the finite backward search window,
- last-opposing-candle selection and tie-breaking,
- body-only, wick-inclusive, or dual boundaries,
- minimum size and maximum age,
- touch, mitigation, invalidation, and expiry semantics.

The v1 detector must not label every opposite-colored candle as an Order Block.
It must retain the causal link from the selected candle to the qualifying
displacement and confirmed structural event.

### 7.7 Mitigation Block

This term has materially different definitions across SMC/ICT sources. Coding
is blocked until one exact definition is selected and illustrated with positive,
negative, and ambiguous fixtures. The selected rule must specify:

- prerequisite structure and liquidity event,
- relationship to an existing Order Block,
- zone boundaries,
- first eligible retest,
- mitigation completion,
- invalidation and expiry.

### 7.8 Breaker Block

- A Breaker candidate must reference a previously detected Order Block.
- The original block must first satisfy the locked invalidation rule.
- A confirmed structural transition must support the role reversal.
- The Breaker retains the source Order Block ID and may not be created as an
  unrelated standalone zone.
- Retest, mitigation, invalidation, and expiry rules require deterministic
  fixtures.

### 7.9 Inducement

Inducement is the highest-subjectivity feature and is implemented last. A future
specification must tie an inducement candidate to:

- an active dealing range,
- a target external-liquidity pool,
- a confirmed internal-liquidity feature,
- an observable sweep or trap sequence,
- a confirmation time and invalidation.

The detector must be allowed to return `NONE` or `AMBIGUOUS`. It must never use a
subsequent winning or losing outcome to decide retrospectively that inducement
existed.

### 7.10 Kill-zone-specific SMC context

- Kill zones are time-context labels, not independent BUY or SELL signals.
- Exchange, instrument, timezone, daylight-saving policy, weekdays, holidays,
  early closes, and session boundaries must be explicit.
- Initial research output should label Asia, London, New York AM, and New York
  PM only after their exact schedules are approved.
- Overnight intervals must handle date boundaries deterministically.
- A kill-zone label may summarize contemporaneous SMC events but cannot alter
  decisions during the diagnostic phase.

### 7.11 Historical Volume Profile

- Aggregate validated full-footprint volume by exact instrument price tick over
  a locked window.
- Initial window types: completed exchange session, fixed rolling window, and
  explicitly anchored historical window.
- POC is the price level with maximum aggregate total volume; ties require a
  deterministic rule locked before coding.
- Value Area uses a locked target percentage and deterministic expansion from
  POC; tie behavior must be specified and tested.
- Output must include POC, VAH, VAL, total volume, covered volume, source type,
  window boundaries, completeness, and data-quality state.
- Developing values must use only footprint rows available at the decision time.
- HVN/LVN require a separately specified smoothing and prominence method and
  must not be inferred from arbitrary visual inspection.
- Volume Profile remains an Order Flow research result. It is not silently added
  to the SMC confidence score.

## 8. Architecture Boundary

Planned detector modules should be isolated by responsibility. A future reviewed
file plan may include:

- `smc/equal_liquidity.py`
- `smc/liquidity_map.py`
- `smc/dealing_range.py`
- `smc/fair_value_gap.py`
- `smc/order_block.py`
- `smc/mitigation_block.py`
- `smc/breaker_block.py`
- `smc/inducement.py`
- `smc/kill_zones.py`
- `smc/smc_v2_context.py`
- `orderflow/volume_profile.py`

Modules may consume shared market primitives, but they must not mutate one
another or call the Decision Engine. They produce structured evidence that is
assembled through a new versioned context adapter.

The existing `SMCContextResult` must remain compatible. New fields should not be
inserted into existing required positional construction. Prefer a new
`SMCV2ContextResult` plus an explicit compatibility adapter, or optional nested
results with safe defaults after a dedicated compatibility review.

## 9. Feature Flags and Modes

Every future feature requires an independent disabled-by-default flag. At least
three operational modes must be distinguishable:

1. `OFF`: detector is not run; current behavior is byte-compatible where
   practical.
2. `DIAGNOSTIC`: detector runs and is traced, but cannot affect a decision.
3. `DECISION_CANDIDATE`: reserved for a later separately approved A/B research
   harness; it is not authorized by this plan.

There is no implicit master switch that activates all modules. Dependencies must
fail closed or return `UNKNOWN`, not silently enable prerequisites.

## 10. Test Strategy

### 10.1 Unit tests per detector

- Positive, negative, boundary, malformed-input, insufficient-data, duplicate,
  and ambiguous cases.
- Exact tick-boundary and floating-point normalization cases.
- Lifecycle transition tests.
- Deterministic tie-breaking tests.
- Stable trace-ID tests.

### 10.2 Look-ahead tests

- Prefix invariance: the result at index `t` must be identical whether the input
  ends at `t` or contains later bars.
- Confirmation-delay tests for swing-derived features.
- No future range boundary, future mitigation, future session, or future profile
  volume may appear in an earlier decision snapshot.

### 10.3 Time tests

- UTC and exchange-local conversion.
- Daylight-saving transitions.
- Overnight date changes.
- Weekend, holiday, and early-close behavior.
- Naive or invalid timestamps fail closed.

### 10.4 Volume Profile tests

- Full-footprint aggregation and volume conservation.
- Bid, ask, total, and price-tick validation.
- POC ties and Value Area ties.
- Session, rolling, and anchored windows.
- Incomplete sessions and missing price levels.
- Explicit rejection of `BAR_SUMMARY` as an official profile.

### 10.5 Compatibility and integration tests

- Full existing pytest suite remains passing.
- All new flags off reproduces the current SMC/CRT/Order Flow/decision behavior.
- Diagnostic mode changes traces only, not actions, allowed status, risk plan,
  entry, exit, PnL, or iteration accounting.
- Existing dataclass construction used by tests and callers remains valid.
- CLI help and default commands remain backward-compatible.

### 10.6 Property and metamorphic tests

- Adding future bars cannot alter past emitted snapshots.
- Scaling price and tick size consistently preserves structural relationships.
- Re-running identical inputs produces byte-stable normalized JSON evidence.
- Shuffling footprint price-level row order within one bar does not change a
  completed profile.

## 11. Quality Gates

No phase may advance merely because code was written. Each phase requires:

- reviewed definition and fixtures,
- focused unit tests passing,
- full regression suite passing,
- no unexplained snapshot or public-interface change,
- no new live, broker, credential, or external-API path,
- code review of look-ahead and state transitions,
- documentation and checkpoint update,
- explicit authorization for the next phase.

Any target collision, dirty unexpected file, baseline mismatch, test regression,
unexplained output difference, or ambiguous requirement is a stop condition.

## 12. Delivery Phases

### Phase 0 — Governance and specification

- Review this plan.
- Resolve every definition marked as blocked or requiring a locked choice.
- Create and review the formal change proposal.
- Record a separate code-freeze-lift decision limited to diagnostic-only work.
- Complete implementation plan, final review, readiness, and explicit approval.

### Phase 1 — Shared primitives

- Timestamp, tick normalization, source/confirmation identity, zone lifecycle,
  deterministic IDs, and prefix-invariance test helpers.
- No trading-decision integration.

### Phase 2 — Range and liquidity foundation

- Dealing Range.
- Equal High/Equal Low.
- Internal/External liquidity mapping.
- Premium/Equilibrium/Discount.

### Phase 3 — Imbalance and institutional zones

- FVG.
- Order Block.
- Mitigation Block after its definition is approved.
- Breaker Block after Order Block lifecycle passes review.

### Phase 4 — Time and advanced narrative

- Kill-zone context.
- Inducement last, after lower-subjectivity features are stable.

### Phase 5 — Volume Profile

- Session, rolling, and anchored historical profiles from full-footprint data.
- POC and Value Area first; HVN/LVN only after a separate method review.

### Phase 6 — Diagnostic context and trace integration

- Add versioned context and trace output.
- Prove current execution decisions remain unchanged.
- Generate read-only coverage, conflict, and redundancy evidence.

### Phase 7 — Independent research evaluation

- Pre-register detector versions and parameters.
- Use unseen independent data.
- Run coverage and stability analysis before any performance experiment.
- Use ablation tests to measure incremental information and redundancy.

### Phase 8 — Separate future decision proposal

Only if diagnostic evidence is sufficient, create a new proposal for a new
strategy version. This plan does not authorize that proposal's implementation.

## 13. Validation and Overfitting Controls

- The July OOS candidate may be used for regression reproduction, not for
  selecting profitable thresholds or favorable rules.
- Parameters must be chosen from market conventions, instrument metadata,
  deterministic synthetic fixtures, or a separately declared development set.
- A new untouched dataset is required for final OOS evaluation.
- Report empty, conflicting, ambiguous, losing, and insufficient groups.
- Do not combine highly correlated features into repeated confidence votes
  without a redundancy audit.
- Detector coverage must be measured before profitability.
- No favorable rerun, manual truncation, post-outcome relabeling, or silent
  parameter adjustment is allowed.

## 14. Rollback Plan

Future implementation should be delivered in small commits by module. Rollback
must be possible by disabling one flag or reverting one bounded module commit.

Before every promotion:

- record parent commit,
- record focused and full-test results,
- verify no unintended generated or private files,
- compare default-mode normalized outputs,
- preserve the previous checkpoint.

No migration may destructively rewrite existing evidence or configuration.

## 15. Documentation and Trace Requirements

Every detector must document:

- exact formula and configuration,
- required input quality,
- first-known time,
- lifecycle and invalidation,
- ambiguous/unknown behavior,
- limitations and known false-positive modes,
- whether it is OFF, DIAGNOSTIC, or separately authorized.

Trace output must explain why a feature exists and why it does not exist. A
chart label without source indices, boundaries, and evidence is insufficient.

## 16. Explicitly Out of Scope

- Fibonacci.
- Machine-learning training or adaptive parameter selection.
- Automatic optimization against saved OOS outcomes.
- Risk-rule changes or position-sizing changes.
- Automatic BUY/SELL enforcement.
- Paper or live trading progression.
- Broker, MT5, Sierra live, CME live, or external-API integration.
- Reclassification or replacement of existing OOS evidence.

## 17. Human Decisions Required Before Coding

Accepted answers for all ten decisions are recorded in
`docs/smc_v2_volume_profile_recommended_specification.md` under specification ID
`SMC-V2-VP-SPEC-2026-07-19`. HOSOO accepted the ten decisions on `2026-07-19`.
The related formal proposal is
`docs/smc_v2_volume_profile_change_proposal.md` with review decision
`ACCEPT_FOR_BOUNDED_FREEZE_LIFT_REVIEW`. The code freeze remains active.

The following must be approved explicitly in the reviewed specification:

1. Order Block displacement, boundaries, search, and invalidation semantics.
2. The exact Mitigation Block definition.
3. Equal High/Low tolerance and touch/separation rules.
4. Swing hierarchy and Dealing Range transition rules.
5. FVG minimum size, touch, mitigation, invalidation, and expiry rules.
6. Breaker confirmation rules.
7. Inducement prerequisite sequence.
8. Kill-zone timezone, schedules, holiday source, and DST policy.
9. Volume Profile window, POC tie, Value Area, and completeness rules.
10. Diagnostic flags and the exact bounded code-freeze-lift scope.

## 18. Resume Checkpoint

Canonical document:
`docs/smc_v2_volume_profile_implementation_plan.md`

Current baseline:

- Expected Git commit: `c8327f76d4e436520b5713c2a6ca33559a6b7c41` before this documentation change.
- Verified regression baseline: `881 passed` on `2026-07-18`.
- Fibonacci: excluded.
- Code freeze: active.
- Python, strategy, risk, Order Flow, and exporter source changes: not yet authorized.
- Existing OOS classification: preserved as
  `VALID_OOS_EVIDENCE — PERFORMANCE_FAILED`.

Next authorized step:

> Independently validate and checkpoint the accepted documentation package,
> review `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`, complete
> the remaining final-review/readiness gates, and obtain an explicit bounded
> freeze-lift decision. Do not edit Python source before those gates pass.

When resuming in a new chat:

1. Read this entire document.
2. Verify Git HEAD, `origin/main`, and working-tree status.
3. Verify the document and baseline test result recorded at the latest checkpoint.
4. Do not repeat completed phases.
5. Do not add Fibonacci.
6. Do not change current decision behavior while new modules remain diagnostic.
7. Stop without editing code if repository state conflicts with this checkpoint.
