# SMC v2 and Volume Profile Recommended Specification

## 1. Record Status

- Specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Status: `ACCEPTED AS TECHNICAL CONTRACT FOR BOUNDED FREEZE-LIFT REVIEW`.
- Accepted by: `HOSOO`.
- Acceptance date: `2026-07-19`.
- Canonical parent plan:
  `docs/smc_v2_volume_profile_implementation_plan.md`.
- Parent-plan SHA-256 at specification start:
  `CD4E85876E311B65F38EB376696D6180934313C420D0915082CBE3FAD5C3CD9C`.
- Baseline Git commit:
  `c8327f76d4e436520b5713c2a6ca33559a6b7c41`.
- Code-freeze status: `ACTIVE`.
- Python implementation: `NOT AUTHORIZED`.
- Decision integration: `NOT AUTHORIZED`.
- Fibonacci: `EXCLUDED`.

This document records the accepted exact v1 research semantics for the ten
technical decisions in Section 17 of the parent plan. Acceptance authorizes use
of these definitions in a bounded freeze-lift review and future test design. It
does not approve code, change the strategy, select profitable parameters from
OOS outcomes, or lift the code freeze.

These definitions are now the pre-implementation technical contract. Changing
them requires a new version and recorded rationale before affected outcome data
is read.

## 2. Shared Determinism Contract

All recommended detectors follow these rules:

1. Use fully closed bars only.
2. Store both event time and first-known confirmation time.
3. Use stable chronological source indices.
4. Normalize prices to a positive instrument tick size.
5. Use strict comparisons after tick normalization.
6. Return `UNKNOWN`, `NONE`, `AMBIGUOUS`, or an invalid-data result instead of
   inventing missing context.
7. Never revise a past emitted snapshot using future bars.
8. Keep original zone boundaries immutable; lifecycle state changes are separate
   timestamped events.
9. Generate deterministic IDs from detector version, instrument, timeframe,
   source index or indices, direction, and normalized boundaries.
10. Remain diagnostic-only and disabled by default.

Recommended shared market defaults:

- Swing lookback: preserve existing `swing_lookback=2` for compatibility.
- Structure confirmation: candle close, not wick alone.
- Structure break buffer: `1` instrument tick.
- All tolerance, boundary, and gap values are integer tick counts internally.
- ATR, rolling medians, and volume statistics use only values available before
  or at the current closed decision bar.

These defaults are specification choices, not conclusions derived from the July
OOS result.

## 3. Decision 1 — Order Block Semantics

### 3.1 Recommended qualifying sequence

A bullish Order Block requires:

1. A previously confirmed swing high.
2. A bullish displacement sequence of one to three consecutive closed candles.
3. The final displacement candle closes at least `1` tick above that swing high,
   producing a confirmed bullish BOS or CHOCH.
4. At least one candle in the displacement sequence has:
   - real-body-to-range ratio greater than or equal to `0.60`, and
   - real body greater than or equal to the median real body of the preceding
     `20` closed bars.
5. At least `10` valid preceding bars exist for the rolling-body comparison;
   otherwise the result is insufficient rather than relaxed.
6. The source candle is the last bearish candle within the `10` closed bars
   immediately preceding the displacement sequence.

A bearish Order Block is the exact mirror: last bullish source candle followed
by qualifying bearish displacement and a close at least `1` tick below a
confirmed swing low.

### 3.2 Boundaries

Store both boundary representations:

- `wick_low` and `wick_high`: complete candle range.
- `body_low` and `body_high`: open/close body range.

The recommended v1 active zone is wick-inclusive because it preserves all source
information. Reports must also display body boundaries so a later registered
research variant can compare them without reconstructing source candles.

For a bullish block:

- proximal boundary: source-candle high,
- distal boundary: source-candle low.

For a bearish block:

- proximal boundary: source-candle low,
- distal boundary: source-candle high.

### 3.3 Lifecycle

- `DETECTED`: qualifying structural close occurs.
- `ACTIVE`: begins on the next bar; the creation sequence cannot mitigate its
  own source block.
- `TOUCHED`: a later wick first enters the wick-inclusive zone.
- `PARTIALLY_MITIGATED`: price enters the zone but does not reach its midpoint.
- `MITIGATED`: price reaches or crosses the zone midpoint.
- `FULLY_TRAVERSED`: price reaches the distal boundary without the invalidating
  close described below.
- `INVALIDATED`: a closed candle finishes at least `1` tick beyond the distal
  boundary in the adverse direction.

No time-based expiry is recommended in v1. An active block ends only through
mitigation-state reporting, invalidation, replacement by an explicitly versioned
structural rule, or end of input. Mitigation does not rewrite the original zone.

### 3.4 Selection and ambiguity

- If more than one opposite candle exists, choose the most recent qualifying
  candle before displacement.
- If no opposite candle exists inside the finite search window, emit no block.
- Do not label every opposite-colored candle as an Order Block.
- Preserve links to the source swing, displacement candles, and BOS/CHOCH event.

## 4. Decision 2 — Mitigation Block Definition

The recommended v1 Mitigation Block is not an independently discovered candle.
It is a versioned retest event that references a valid, still-active Order Block.
This avoids creating two unrelated zones from the same price action.

A Mitigation Block event requires:

1. A qualifying Order Block under Decision 1.
2. Price must first leave the block in its expected direction and complete the
   linked structural displacement.
3. A later candle returns to the source block for the first time.
4. The returning candle reaches at least the block midpoint.
5. That candle does not close at least `1` tick beyond the distal boundary.

The Mitigation Block uses the original Order Block's immutable boundaries and
stores:

- source Order Block ID,
- first-retouch bar,
- deepest penetration price,
- midpoint reached status,
- close location,
- subsequent invalidation if one occurs.

If price merely touches the proximal edge without reaching the midpoint, record
an Order Block touch, not a Mitigation Block. If price closes through the distal
edge, record invalidation rather than mitigation.

## 5. Decision 3 — Equal High and Equal Low Rules

### 5.1 Candidate construction

- Members must be confirmed swing highs for Equal High or confirmed swing lows
  for Equal Low.
- Required members: at least `2`.
- Equality tolerance: `2` instrument ticks inclusive.
- Minimum source-index separation between adjacent member swings: `3` bars.
- A swing may belong to only one active cluster of the same side; when multiple
  clusters are possible, assign it to the closest cluster price, then the oldest
  cluster ID for an exact tie.
- Cluster reference price is the tick-normalized median of member prices.

### 5.2 Lifecycle

- The pool becomes knowable when its second qualifying swing is confirmed.
- Later qualifying swings may join without changing prior emitted snapshots.
- A high pool is `SWEPT` when a later wick trades at least `1` tick above the
  cluster plus tolerance and the same candle closes at or below the upper
  tolerance boundary.
- A low pool is `SWEPT` by the mirrored condition.
- A high pool is `BROKEN` when a candle closes at least `1` tick above its upper
  tolerance boundary; a low pool uses the mirrored close.
- `SWEPT` and `BROKEN` consume the pool. No default bar-count expiry is used.

The detector must report the member swings, tolerance band, reference price,
first-known time, and consuming event.

## 6. Decision 4 — Swing Hierarchy and Dealing Range

### 6.1 Internal swings

All confirmed swings produced by the compatible `swing_lookback=2` process are
internal swing candidates. They become available only after the two required
right-side bars have closed.

### 6.2 External structure

The recommended external structure is event-driven:

- After a confirmed bullish close break, the protected external low is the most
  recent confirmed swing low preceding the displacement sequence.
- The external high is the highest closed-bar high from that protected low
  through the current confirmation bar.
- After a confirmed bearish close break, the protected external high is the most
  recent confirmed swing high preceding displacement.
- The external low is the lowest closed-bar low from that protected high through
  the current confirmation bar.

A protected boundary changes only after a newly confirmed structural event. A
wick alone does not replace it.

### 6.3 Active Dealing Range

The active range is:

- bullish: protected external low to current external high,
- bearish: current external low to protected external high.

It stores direction, source swing IDs, low, high, midpoint, construction event,
and first-known time.

### 6.4 Transition rules

- A close at least `1` tick through the protected opposite boundary invalidates
  the current directional range and may confirm a CHOCH.
- A new same-direction BOS may extend the external target while preserving the
  protected boundary until a new confirmed pullback swing and subsequent BOS
  establish a replacement range.
- Nested pairs of internal swings are reported as internal ranges only; they do
  not silently replace the external range.
- If the protected swing cannot be identified unambiguously, return `UNKNOWN`.

## 7. Decision 5 — Fair Value Gap Rules

### 7.1 Detection

For closed candle `i`:

- Bullish FVG: `Low[i] - High[i-2] >= 2 ticks`.
- Bearish FVG: `Low[i-2] - High[i] >= 2 ticks`.
- The middle candle `i-1` must have real-body-to-range ratio greater than or
  equal to `0.60`.
- The FVG becomes knowable only when candle `i` closes.

The detector records whether the FVG is linked to a qualifying displacement,
BOS, CHOCH, or neither. Structure linkage is metadata, not a requirement for the
base diagnostic detector.

### 7.2 Boundaries and lifecycle

- Bullish lower boundary: `High[i-2]`; upper boundary: `Low[i]`.
- Bearish lower boundary: `High[i]`; upper boundary: `Low[i-2]`.
- Consequent encroachment: arithmetic midpoint of the immutable gap.
- `TOUCHED`: a later wick enters the gap.
- `PARTIALLY_FILLED`: some gap remains and midpoint is not reached.
- `MIDPOINT_FILLED`: consequent encroachment is reached.
- `FULLY_FILLED`: price reaches the far boundary.
- `INVALIDATED`: a candle closes at least `1` tick beyond the far boundary.

The three formation candles cannot fill their own FVG. No default time expiry is
recommended. Reports must distinguish a full fill from a close-through
invalidation.

## 8. Decision 6 — Breaker Block Rules

A Breaker Block must reference an existing Order Block and may not be detected as
an unrelated standalone candle zone.

Required sequence:

1. A valid Order Block exists.
2. A later candle closes at least `1` tick beyond its distal boundary, setting
   the source block to `INVALIDATED`.
3. That close or a subsequent close within the next `10` closed bars confirms a
   BOS or CHOCH in the invalidation direction.
4. The original wick-inclusive boundaries are reclassified as a Breaker zone at
   the structure-confirmation close.
5. The Breaker is eligible for retest only from the next bar.

A failed bearish Order Block becomes a bullish Breaker; a failed bullish Order
Block becomes a bearish Breaker.

Breaker lifecycle uses `ACTIVE`, `TOUCHED`, `PARTIALLY_MITIGATED`, `MITIGATED`,
and `INVALIDATED`. Invalidation is a close at least `1` tick through the Breaker
distal boundary in the direction adverse to its new role. The result retains the
source Order Block and structure-event IDs.

## 9. Decision 7 — Inducement Sequence

Inducement is implemented last and only as a confirmed historical narrative,
not as an early predictive label.

Recommended bullish inducement requires, in chronological order:

1. An active bullish Dealing Range.
2. An active external buy-side liquidity target above current price.
3. A confirmed internal sell-side pool inside the range.
4. A later candle sweeps that internal sell-side pool and closes back above its
   tolerance boundary.
5. Within the next `3` closed bars, bullish displacement under Decision 1
   confirms bullish BOS or CHOCH.
6. That displacement creates a qualifying bullish FVG under Decision 5.

The swept internal pool becomes a confirmed bullish inducement event only after
step 6 is knowable. Bearish inducement is the exact mirror.

If the external target, internal pool, reclaim, structural confirmation, or FVG
is missing, return `NONE`. If simultaneous opposing sequences satisfy the rules,
return `AMBIGUOUS`. No outcome, entry, exit, PnL, or later target hit participates
in the label.

## 10. Decision 8 — Kill-zone Calendar and Time Rules

### 10.1 Time authority

- Internal source timestamps: timezone-aware UTC.
- Session definition timezone: IANA `America/New_York`.
- Daylight-saving conversion: timezone database rules, never a fixed UTC offset.
- Interval semantics: start inclusive, end exclusive.

### 10.2 Recommended diagnostic windows

- Asia: `20:00` to `00:00` New York time.
- London: `02:00` to `05:00` New York time.
- New York AM: `07:00` to `10:00` New York time.
- New York PM: `13:00` to `16:00` New York time.

The Asia window belongs to the following trade date because it crosses midnight.
Only Monday through Friday trade dates are eligible.

### 10.3 Holidays and early closes

No external calendar API is authorized. Use a versioned, manually reviewed local
calendar containing exchange holidays and early closes. When calendar coverage
is missing, the time window may be labeled with quality
`CALENDAR_UNVERIFIED`, but it cannot be used for decision research. A holiday or
closed-session interval returns `SESSION_CLOSED`, not a kill-zone signal.

Kill-zone membership is context metadata only and has no directional meaning.

## 11. Decision 9 — Volume Profile Rules

### 11.1 Initial authorized profile type

The recommended first implementation supports completed GC exchange sessions
only. Rolling and manually anchored profiles remain planned variants and must not
be silently mixed with session results.

Recommended GC session boundary:

- session timezone: `America/New_York`,
- start: `18:00` on the prior calendar day,
- end: `17:00` on the trade date,
- maintenance interval: `17:00` to `18:00`,
- start inclusive and end exclusive.

Calendar validation follows Decision 8.

### 11.2 Data qualification

- Source must be validated `ACSIL_FULL_FOOTPRINT` or an equivalently reviewed
  full price-level format.
- `BAR_SUMMARY` is rejected for official profiles.
- Price must align to tick size.
- Negative or non-finite volume fails the profile.
- Each bar and price level must be uniquely attributable to one session.
- Total aggregated volume must equal validated source-level total volume.
- A missing expected market bar or invalid level sets completeness to
  `INCOMPLETE`; incomplete profiles remain reportable but unqualified.

### 11.3 POC

- Aggregate total volume at each normalized price tick.
- POC is the price with maximum aggregate volume.
- If tied, select the candidate closest to the session volume-weighted mean
  price.
- If still tied, select the lower price.
- Report all tied candidates as metadata even though one canonical POC is chosen.

### 11.4 Value Area

- Target: `70%` of total session volume.
- Start with POC included.
- Compare the immediately adjacent unused price level above and below the
  included range.
- Add the side with greater aggregate volume.
- On an exact tie, add the lower-price side first.
- Continue until included volume is greater than or equal to the target.
- VAH is the highest included price; VAL is the lowest included price.
- Report actual covered volume and percentage.

This one-level-at-a-time algorithm is chosen for determinism. A future two-level
expansion method would be a different registered version.

### 11.5 HVN and LVN

HVN/LVN are not part of initial Volume Profile v1. They require a separately
reviewed smoothing, neighborhood, and prominence specification. POC, VAH, and
VAL must not be mislabeled as complete HVN/LVN analysis.

## 12. Decision 10 — Feature Flags and Bounded Freeze-lift Scope

### 12.1 Recommended flags

The future configuration should have one master diagnostic flag and independent
module flags, all defaulting to `False`:

- `enable_smc_v2_diagnostics`
- `enable_dealing_range_diagnostic`
- `enable_equal_liquidity_diagnostic`
- `enable_liquidity_map_diagnostic`
- `enable_fvg_diagnostic`
- `enable_order_block_diagnostic`
- `enable_mitigation_block_diagnostic`
- `enable_breaker_block_diagnostic`
- `enable_inducement_diagnostic`
- `enable_kill_zone_diagnostic`
- `enable_volume_profile_diagnostic`

The master flag cannot implicitly enable a child flag. A child flag is effective
only when the master and that child are both true. Missing prerequisites return
`UNKNOWN` with reasons.

No decision-enforcement flag is defined in this specification.

### 12.2 Recommended first bounded freeze lift

If separately approved, the first freeze lift should authorize only:

- new standalone detector modules under `smc/`,
- new `orderflow/volume_profile.py`,
- new dedicated tests,
- synthetic public test fixtures containing no private market data,
- module exports required solely for direct testing,
- related documentation.

It should not authorize changes to:

- `main.py`,
- `core/decision_engine.py`,
- `core/context_alignment.py`,
- `core/paper_trading_flow.py`,
- risk or broker modules,
- existing execution behavior,
- existing SMC confidence calculation,
- existing Order Flow confidence calculation,
- private data, generated reports, or external evidence,
- CLI behavior, live connections, or external APIs.

Diagnostic trace integration is a later separate gate after standalone detectors
and prefix-invariance tests pass.

## 13. Dependency and Implementation Order

Recommended dependency order:

1. Shared tick, confirmation-time, ID, and lifecycle primitives.
2. Equal High/Equal Low.
3. Swing hierarchy and Dealing Range.
4. Internal/External liquidity mapping.
5. Premium/Equilibrium/Discount.
6. FVG.
7. Order Block.
8. Mitigation Block event.
9. Breaker Block.
10. Kill-zone context.
11. Inducement.
12. Session Volume Profile.

Inducement must not be implemented before its range, liquidity, displacement,
structure, and FVG dependencies are independently validated.

## 14. Minimum Fixture Matrix Before Coding Approval

Each detector specification requires synthetic fixtures for:

- one bullish positive case,
- one bearish positive case,
- one near miss at exactly one tick outside the rule,
- one insufficient-history case,
- one ambiguous case where applicable,
- one invalid-data case,
- one prefix-invariance case,
- one lifecycle case through invalidation,
- one deterministic tie case where applicable.

Order Block, Breaker, Mitigation, and Inducement fixtures must include the full
causal event chain. Volume Profile fixtures must conserve volume exactly and
exercise POC and Value Area ties.

## 15. Recommendation Summary

The ten decisions are technically resolvable without Fibonacci and without
changing current execution behavior. The recommended approach favors:

- closed-bar determinism,
- tick-based boundaries,
- explicit causal links,
- no silent time expiry,
- strict lifecycle histories,
- full-footprint-only official Volume Profile,
- diagnostic-only disabled defaults,
- small standalone implementation scope.

Approval of this specification authorizes its use as the detailed contract for
the accepted proposal review and future test design. It does not itself
authorize Python code.
