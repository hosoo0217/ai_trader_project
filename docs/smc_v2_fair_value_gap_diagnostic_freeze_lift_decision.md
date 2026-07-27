# SMC v2 Fair Value Gap Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-FAIR-VALUE-GAP-FREEZE-LIFT-DECISION-2026-07-27`.
- Parent review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Parent specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Implementation-order phase: `6 - FAIR VALUE GAP`.
- Implementation parent commit:
  `2448d957d6f853fbb275f17c64b86ae03e6ccc44`.
- Requested module: standalone Fair Value Gap diagnostics.
- Current task type: documentation-only formal decision record.
- Decision classification:
  `APPROVED - DOCUMENTATION DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`.
- Global code-freeze status: `ACTIVE`.
- Python implementation authorized by this record: `False`.
- Test or fixture change authorized by this record: `False`.
- Integration authorized by this record: `False`.
- Staging, commit, or push authorized by this record: `False`.

This record reserves and specifies one possible future Fair Value Gap task. It
does not make the bounded exception operational, authorize code, or transfer
authority from any completed dependency task.

## 2. Effective-State Interpretation

The accepted implementation order is:

1. Shared primitives and test helpers.
2. Equal High and Equal Low.
3. Swing Hierarchy and Dealing Range.
4. Internal and External Liquidity Mapping.
5. Premium, Equilibrium, and Discount.
6. Fair Value Gap.

The first five phases are committed, pushed, independently checkpointed, and
present on local and live `main`. Their completion satisfies the dependency-order
gate for this documentation decision only.

The possible later implementation becomes operational only after all of these
separate gates pass:

1. independent final audit of this record,
2. documentation-only staging, commit, and push checkpoints,
3. local and live remote identity confirmation,
4. clean-worktree and reserved-target collision checks,
5. a read-only implementation preflight against this exact contract,
6. explicit human authorization for the exact three-path implementation scope,
7. test-first execution limited to that scope, and
8. a separate independent final code, test, scope, hash, and diff audit.

The global freeze remains active for every path outside that later exact task.

## 3. Locked Decision Inputs and Dependency Evidence

This decision is derived from the accepted planning package and completed
dependency checkpoints:

- `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256:
    `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`
- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`
- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`
  - SHA-256:
    `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`
- `smc/smc_v2_primitives.py`
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `smc/dealing_range.py`
  - SHA-256:
    `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `smc/liquidity_map.py`
  - SHA-256:
    `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`
- `smc/premium_discount.py`
  - SHA-256:
    `DC137E0FD66699E6B09A676DB63C17CF2F7AFB6BEC9EE5E01C53580902BC11A8`
- `docs/smc_v2_premium_discount_checkpoint.md`
  - SHA-256:
    `CE745D76B8CF7166E44E2C7FF4C34FE7A511C205936340078768521B68755B09`

The accepted specification locks these FVG semantics:

- exactly three fully closed candles form one candidate window,
- a bullish gap is at least two ticks between candle `i-2` high and candle `i`
  low,
- a bearish gap is at least two ticks between candle `i` high and candle `i-2`
  low,
- the middle candle real-body-to-range ratio is at least `0.60`,
- the candidate becomes knowable only when candle `i` closes,
- original boundaries never change,
- fill and close-through invalidation are distinct,
- the three formation candles cannot fill their own gap, and
- no default time expiry exists.

Shared primitives are a direct immutable dependency. `DealingRangeEventType` may
be imported only to type and validate optional caller-supplied `BOS` or `CHOCH`
metadata. The future module must not construct, mutate, or rerun Dealing Range,
Liquidity Map, Premium/Discount, swing, BOS, or CHOCH analysis.

## 4. Exact Change Authorized in This Documentation Task

Only this new file may be created in the current task:

- `docs/smc_v2_fair_value_gap_diagnostic_freeze_lift_decision.md`

No existing documentation, Python, test, fixture, configuration, private data,
external evidence, or generated report may change in this task. Staging, commit,
push, implementation, detector execution, and integration remain separate gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later implementation preflight and explicit human authorization pass, the
future task is reserved to exactly these three paths:

- production module: `smc/fair_value_gap.py`
- dedicated unit tests: `tests/test_fair_value_gap.py`
- implementation checkpoint: `docs/smc_v2_fair_value_gap_checkpoint.md`

All fixtures must be synthetic and inline in the dedicated test file. No external
or separate fixture file is reserved or authorized by this record.

The later task must not edit `smc/__init__.py`, `smc/smc_v2_primitives.py`,
`smc/dealing_range.py`, `smc/liquidity_map.py`, `smc/premium_discount.py`, or
any existing SMC v1 module. Direct imports of completed shared-primitives types
and `DealingRangeEventType` are sufficient. Any need for another path is a stop
condition requiring a new scope review and explicit human approval before that
edit occurs.

## 6. Exact Functional Boundary

The future standalone module may implement only:

- validation and chronological consumption of immutable fully closed
  integer-tick candles,
- validation and formation-time attachment of optional immutable caller-supplied
  displacement, BOS, or CHOCH identity metadata,
- deterministic bullish and bearish three-candle FVG detection,
- immutable gap boundaries and exact consequent-encroachment midpoint,
- deterministic lifecycle transitions from later fully closed candles,
- immutable gap, transition, and snapshot histories,
- exact status, reason, and blocking-reason output,
- deterministic identity construction, and
- prefix-invariant standalone diagnostics.

The future module may not:

- load a CSV, pandas object, broker feed, Sierra data, external API, or saved
  report,
- detect or confirm swings, displacement sequences, BOS, or CHOCH,
- infer a displacement, BOS, or CHOCH link from future data,
- construct or mutate Dealing Ranges, Liquidity Maps, or Premium/Discount zones,
- implement Order Block, Mitigation Block, Breaker Block, Inducement, kill-zone,
  Volume Profile, confidence, signal, filter, or execution behavior,
- use outcomes, PnL, trade results, private data, or candidate OOS evidence, or
- interpret an FVG as BUY, SELL, entry, reversal, target, readiness, or edge.

## 7. Locked Input Contracts

### 7.1 Top-Level Contract

The analyzer accepts exactly:

- `instrument: str`
- `timeframe: str`
- `candles: tuple[FairValueGapCandle, ...] | None`
- `context_links: tuple[FairValueGapContextLink, ...] | None`

`instrument` and `timeframe` are stripped and uppercased exactly once. Empty
normalized values are `INVALID`.

`candles=None` or `context_links=None` means complete top-level context was not
supplied and returns `UNKNOWN`. An explicit empty context-link tuple declares
that no displacement or structure linkage is supplied; base FVG detection still
proceeds.

All supplied collections must be tuples. The analyzer must not accept generators,
lists, pandas objects, dictionaries, mutable adapters, or hidden global context.

### 7.2 Fully Closed Integer-Tick Candle Contract

`FairValueGapCandle` is a frozen dataclass with exactly:

- `index: int`
- `timestamp: datetime`
- `open_tick: int`
- `high_tick: int`
- `low_tick: int`
- `close_tick: int`

Every candle is declared fully closed by inclusion in the immutable tuple. The
future analyzer does not connect to a clock or attempt to decide whether a live
candle has closed.

Exact validation rules are:

- booleans, floats, strings, and Decimal prices are invalid for integer-tick
  fields,
- `index` is a non-negative exact integer,
- `timestamp` is timezone-aware and normalized to UTC,
- `low_tick <= open_tick <= high_tick`,
- `low_tick <= close_tick <= high_tick`, and
- `low_tick <= high_tick`.

A zero-range candle is valid OHLC evidence but has no defined positive
body-to-range ratio and cannot satisfy the middle-candle displacement-quality
rule.

Candle indices and normalized timestamps are independently strictly increasing
and unique. Caller order is causal order and is never silently sorted,
deduplicated, repaired, coerced, or backfilled. Adjacent tuple members represent
adjacent supplied closed candles; numeric source indices need not differ by one.

### 7.3 Caller-Supplied Context-Link Contract

`FairValueGapContextLink` is a frozen dataclass with exactly:

- `formation_end_index: int`
- `formation_end_timestamp: datetime`
- `displacement_id: str | None`
- `structure_event_id: str | None`
- `structure_event_type: DealingRangeEventType | None`

Every non-null identity is a lowercase 64-character SHA-256 value.
`structure_event_id` and `structure_event_type` must either both be present or
both be absent. A present structure-event type is exactly `BOS` or `CHOCH`.
`displacement_id` is independently optional.

A context-link record with neither displacement nor structure metadata is
`INVALID`; an empty context-link tuple is the canonical declaration of no links.

The link effective moment must exactly equal the formation-ending candle index
and normalized timestamp. A link is valid only if a qualifying FVG is formed at
that exact moment. A link to a non-FVG formation is dangling and `INVALID`.

Context-link effective moments are nondecreasing. Records at one effective moment
form one atomic group:

- one valid link is attached,
- an exact duplicate link is `INVALID`, and
- two distinct otherwise valid links for the same formation are `AMBIGUOUS`.

The analyzer does not choose among conflicting displacement or structure
identities. Link hash values are identity evidence, not chronology tie-breakers.

The future analyzer validates only link-local shape and formation-moment
reconciliation. It does not require unavailable displacement or structure-event
objects, and it does not re-prove the foreign event's market meaning.

### 7.4 Formation Windows and Effective Groups

For each candle at tuple position `i >= 2`, the formation window is exactly the
three adjacent supplied candles at positions `i-2`, `i-1`, and `i`.

The effective moment of:

- one candle group is its candle index and normalized timestamp,
- a newly formed gap is the ending candle index and normalized timestamp, and
- one lifecycle transition is the later candle index and normalized timestamp
  that first makes that transition knowable.

One complete effective group contains the candle, every context-link record for
that formation moment, every lifecycle update to previously active gaps, and any
newly formed gap. A prefix cannot end inside that group.

## 8. Locked Three-Candle Detection Semantics

For the three fully closed candles `i-2`, `i-1`, and `i`:

- bullish raw gap size is
  `low_tick[i] - high_tick[i-2]`,
- bearish raw gap size is
  `low_tick[i-2] - high_tick[i]`, and
- the required minimum is exactly `2` ticks inclusive.

A bullish FVG forms only when:

`low_tick[i] - high_tick[i-2] >= 2`

A bearish FVG forms only when:

`low_tick[i-2] - high_tick[i] >= 2`

Exactly one direction can qualify for one valid OHLC formation window. A one-tick
gap is a valid near miss and emits no gap.

The middle candle `i-1` must satisfy:

`real_body_ticks / full_range_ticks >= 0.60`

The implementation must compare exact integers as:

`5 * abs(close_tick - open_tick) >= 3 * (high_tick - low_tick)`

This avoids float and Decimal-context dependence. A zero-range middle candle does
not qualify.

The gap becomes knowable only after candle `i` closes. No candidate, identity,
transition, snapshot, or link may be emitted at `i-2` or `i-1`.

## 9. Locked Boundaries and Consequent Encroachment

For a bullish FVG:

- lower or far boundary: `high_tick[i-2]`,
- upper or proximal boundary: `low_tick[i]`.

For a bearish FVG:

- lower or proximal boundary: `high_tick[i]`,
- upper or far boundary: `low_tick[i-2]`.

The ordered immutable boundary interval is always
`SMCV2TickRange(lower_tick, upper_tick)`, with positive width of at least two
ticks.

Consequent encroachment is the exact arithmetic midpoint:

`(lower_tick + upper_tick) / 2`

The implementation must construct the midpoint by integer-sum parity so the
result is exactly an integer tick or half tick. It must not use float,
context-sensitive Decimal division, `quantize()`, or rounding.

Canonical text serialization is:

- every integer midpoint uses `.0`,
- every half-tick midpoint uses `.5`,
- every zero-valued Decimal uses exact `0.0`, and
- arbitrary-magnitude positive and negative ticks are context-independent.

Original boundaries and consequent encroachment never move, shrink, extend, or
recalculate after formation.

## 10. Locked Lifecycle and Fill Semantics

`FairValueGapState` is a string enum with exactly:

- `ACTIVE`
- `TOUCHED`
- `PARTIALLY_FILLED`
- `MIDPOINT_FILLED`
- `FULLY_FILLED`
- `INVALIDATED`

At the formation-ending candle close, a new gap receives an initial
`None -> ACTIVE` transition. The initial transition reason is exactly
`FORMATION_CONFIRMED`.

Only candles with effective moments strictly later than formation may affect the
new gap. The three formation candles cannot touch, fill, or invalidate their own
gap.

For a bullish FVG, later price approaches downward:

- `TOUCHED`: later `low_tick` equals the upper proximal boundary,
- `PARTIALLY_FILLED`: later `low_tick` is strictly below the upper boundary but
  strictly above consequent encroachment,
- `MIDPOINT_FILLED`: later `low_tick` reaches or crosses consequent encroachment
  but remains strictly above the lower far boundary,
- `FULLY_FILLED`: later `low_tick` reaches or crosses the lower far boundary
  without close-through invalidation, and
- `INVALIDATED`: later `close_tick` is at least one tick below the lower far
  boundary.

For a bearish FVG, later price approaches upward:

- `TOUCHED`: later `high_tick` equals the lower proximal boundary,
- `PARTIALLY_FILLED`: later `high_tick` is strictly above the lower boundary but
  strictly below consequent encroachment,
- `MIDPOINT_FILLED`: later `high_tick` reaches or crosses consequent encroachment
  but remains strictly below the upper far boundary,
- `FULLY_FILLED`: later `high_tick` reaches or crosses the upper far boundary
  without close-through invalidation, and
- `INVALIDATED`: later `close_tick` is at least one tick above the upper far
  boundary.

One candle may jump directly to the deepest state it reaches. Exact same-candle
precedence is:

1. `INVALIDATED`
2. `FULLY_FILLED`
3. `MIDPOINT_FILLED`
4. `PARTIALLY_FILLED`
5. `TOUCHED`
6. no transition

Close-through invalidation therefore takes precedence over a wick that also
fully fills the gap. Reports must never mislabel that candle as only a full fill.

Allowed monotonic transitions are:

- `ACTIVE -> TOUCHED | PARTIALLY_FILLED | MIDPOINT_FILLED | FULLY_FILLED | INVALIDATED`
- `TOUCHED -> PARTIALLY_FILLED | MIDPOINT_FILLED | FULLY_FILLED | INVALIDATED`
- `PARTIALLY_FILLED -> MIDPOINT_FILLED | FULLY_FILLED | INVALIDATED`
- `MIDPOINT_FILLED -> FULLY_FILLED | INVALIDATED`

`FULLY_FILLED` and `INVALIDATED` are terminal. A later shallower observation does
not regress state and emits no transition. No bar-count, clock-time, session, or
calendar expiry exists in version 1.

Exact lifecycle reason tokens are:

- `FORMATION_CONFIRMED`
- `WICK_TOUCH`
- `PARTIAL_FILL`
- `MIDPOINT_FILL`
- `FULL_FILL`
- `CLOSE_THROUGH_INVALIDATION`

No other public transition reason is valid.

## 11. Locked Optional Linkage and No-Retroactivity Rule

The base detector does not require a displacement, BOS, or CHOCH link. A gap with
no context link is valid and records all link fields as `None`.

A valid formation-time context link may record:

- displacement only,
- BOS only,
- CHOCH only,
- displacement plus BOS, or
- displacement plus CHOCH.

The future module treats those values only as immutable diagnostic metadata. It
does not infer strength, confidence, confluence, direction confirmation, or
trade relevance.

Linkage is fixed at formation. Every supplied link asserts that its first-known
moment is the linked formation-ending candle, and the standalone full-batch
analyzer validates that asserted formation moment. This API is stateless and has
no incremental enrichment operation, so it must not claim that it can infer the
wall-clock arrival order of two separately supplied batches. Adding a link for an
already analyzed older formation is not an eligible strictly-later prefix
extension and cannot be used to claim prefix invariance; if supplied as a new
complete batch, it is evaluated only as asserted contemporaneous formation-time
evidence. Later-confirmed structure evidence cannot enrich, replace, or version
an existing gap under this contract.

If future research requires later-confirmed link enrichment, that is a new
versioned specification and separate freeze-lift decision.

## 12. Locked Public API

The proposed public surface is limited to:

- `FAIR_VALUE_GAP_DETECTOR_VERSION`
- `FairValueGapState`
- `FairValueGapCandle`
- `FairValueGapContextLink`
- `FairValueGap`
- `FairValueGapTransition`
- `FairValueGapSnapshot`
- `FairValueGapResult`
- `make_fair_value_gap_id`
- `analyze_fair_value_gaps`

The exact keyword-only analyzer signature is:

```python
def analyze_fair_value_gaps(
    *,
    instrument: str,
    timeframe: str,
    candles: tuple[FairValueGapCandle, ...] | None,
    context_links: tuple[FairValueGapContextLink, ...] | None,
) -> FairValueGapResult:
    ...
```

No public configuration object exists in version 1. Minimum gap size, middle-body
ratio, boundaries, fill thresholds, invalidation, lifecycle, and no-expiry rules
are fixed semantics, not tunable parameters.

The exact keyword-only identity-builder signature is:

```python
def make_fair_value_gap_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...] = (),
    source_timestamps: tuple[datetime, ...] = (),
    boundaries: SMCV2TickRange | None = None,
    midpoint_tick: Decimal | None = None,
    formation_end_index: int | None = None,
    formation_end_timestamp: datetime | None = None,
    displacement_id: str | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    gap_id: str | None = None,
    from_state: FairValueGapState | None = None,
    to_state: FairValueGapState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: FairValueGapState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    ...
```

Both functions normalize `instrument` and `timeframe` exactly once as
`value.strip().upper()`. Empty normalized values are invalid. Positional calls,
extra public parameters, pandas conversion, file loading, hidden globals, and
environment configuration are forbidden.

`FairValueGap` is frozen and contains exactly:

- `gap_id: str`
- `direction: SMCV2Direction`
- `source_indices: tuple[int, int, int]`
- `source_timestamps: tuple[datetime, datetime, datetime]`
- `lower_tick: int`
- `upper_tick: int`
- `midpoint_tick: Decimal`
- `formation_end_index: int`
- `formation_end_timestamp: datetime`
- `displacement_id: str | None`
- `structure_event_id: str | None`
- `structure_event_type: DealingRangeEventType | None`

`FairValueGapTransition` is frozen and contains exactly:

- `transition_id: str`
- `gap_id: str`
- `from_state: FairValueGapState | None`
- `to_state: FairValueGapState`
- `index: int`
- `timestamp: datetime`
- `reason: str`

`FairValueGapSnapshot` is frozen and contains exactly:

- `snapshot_id: str`
- `gap_id: str`
- `direction: SMCV2Direction`
- `state: FairValueGapState`
- `index: int`
- `timestamp: datetime`
- `transition_ids: tuple[str, ...]`

`FairValueGapResult` is frozen and contains exactly:

- `status: SMCV2PrimitiveStatus`
- `gaps: tuple[FairValueGap, ...] = ()`
- `transitions: tuple[FairValueGapTransition, ...] = ()`
- `snapshots: tuple[FairValueGapSnapshot, ...] = ()`
- `reasons: tuple[str, ...] = ()`
- `blocking_reasons: tuple[str, ...] = ()`

Object tuples are chronological immutable evidence. Every exposed object ID must
exactly reproduce from the public identity builder.

## 13. Locked Deterministic Identity Contract

`FAIR_VALUE_GAP_DETECTOR_VERSION` is exactly `SMC-V2-FAIR-VALUE-GAP-1`.

The only identity kinds are:

- `GAP`
- `TRANSITION`
- `SNAPSHOT`

Every identity includes:

- normalized instrument,
- normalized timeframe,
- detector version,
- exact identity kind, and
- exact direction.

Canonical payloads use:

- sorted-key compact ASCII JSON,
- UTC timestamps serialized as `YYYY-MM-DDTHH:MM:SS.ffffffZ`,
- enum `.value` strings,
- integer ticks,
- exact midpoint `.0` or `.5` text, and
- lowercase SHA-256 output.

No Python object representation, float, unordered set, dictionary insertion
order, locale, process ID, wall clock, random seed, or ambient Decimal context may
affect identity.

### 13.1 `GAP`

`GAP` requires exactly:

- direction,
- source indices of length three,
- source timestamps of length three,
- boundaries,
- exact midpoint,
- formation-ending index,
- formation-ending timestamp,
- optional displacement ID,
- optional structure-event ID, and
- optional structure-event type.

The formation-ending index and timestamp must equal the third source index and
normalized third source timestamp. Boundaries and midpoint must reconcile exactly
with direction and the source-candle formation as validated by the analyzer.

The structure-event ID and type pair must be both present or both absent.
Optional IDs are serialized as null when absent.

`GAP` forbids:

- `gap_id`,
- `from_state`,
- `to_state`,
- `effective_index`,
- `effective_timestamp`,
- `reason`,
- `state`, and
- non-empty `transition_ids`.

### 13.2 `TRANSITION`

`TRANSITION` requires exactly:

- direction,
- gap ID,
- from state, including `None` only for initial formation,
- to state,
- effective index,
- effective timestamp, and
- one exact lifecycle reason.

The initial transition must be:

- `from_state=None`,
- `to_state=ACTIVE`, and
- `reason=FORMATION_CONFIRMED`.

Every later transition must match the locked lifecycle graph and exact reason for
its target state. Effective moments must be strictly later than the prior
transition, except no later transition may share the formation moment.

`TRANSITION` forbids:

- non-empty source indices,
- non-empty source timestamps,
- boundaries,
- midpoint,
- formation-ending fields,
- displacement ID,
- structure-event ID,
- structure-event type,
- `state`, and
- non-empty `transition_ids`.

### 13.3 `SNAPSHOT`

`SNAPSHOT` requires exactly:

- direction,
- gap ID,
- current state,
- effective index,
- effective timestamp, and
- a non-empty ordered transition-ID tuple.

The analyzer must recompute and exact-match every transition ID, require the
final transition target state and moment to equal the snapshot state and moment,
and require the ordered tuple to be the complete immutable transition history for
that gap.

`SNAPSHOT` forbids:

- non-empty source indices,
- non-empty source timestamps,
- boundaries,
- midpoint,
- formation-ending fields,
- displacement ID,
- structure-event ID,
- structure-event type,
- `from_state`,
- `to_state`, and
- `reason`.

For every identity kind, every builder parameter is either exact required data or
exact forbidden default data. Missing required values, forbidden non-default
values, malformed hashes, invalid enum values, unreconciled midpoint or boundary
values, and unknown identity kinds raise only `TypeError` or `ValueError`.

## 14. Locked Immutable Lifecycle and Snapshot Contract

One `FairValueGap` object is emitted exactly once at formation and never mutates.
One `FairValueGapTransition` and one corresponding `FairValueGapSnapshot` are
emitted for the initial `ACTIVE` state and for every later state change.

Transition history is append-only. Snapshot `transition_ids` are exact immutable
prefixes:

- the first snapshot has exactly the formation transition ID,
- each later snapshot appends exactly one new transition ID, and
- no snapshot may skip, reorder, replace, or duplicate a transition.

Each gap is updated independently. A candle that causes lifecycle changes in
multiple existing gaps forms one atomic effective group. Deterministic output
order for those independent transitions is:

1. earlier formation-ending index,
2. earlier normalized formation-ending timestamp,
3. direction value,
4. lexicographic source-index tuple, and
5. gap ID only as a final identity tie after all causal fields are equal.

Gap ID is not used to move a later formation ahead of an earlier formation.

Terminal gaps remain in immutable history but are not evaluated for later
lifecycle transitions. No terminal snapshot is removed or rewritten.

## 15. Locked Chronology and Same-Index Processing Precedence

The complete caller-supplied candle tuple is validated without sorting before
analysis. The complete context-link tuple and each same-effective link group are
also validated before promotion.

For each valid candle effective group, exact processing precedence is:

1. validate the candle, its ordering, and the complete context-link group,
2. clone the strictly prior immutable analysis state,
3. evaluate every gap active before this candle using the locked deepest-state
   precedence,
4. atomically append all valid lifecycle transitions and snapshots for those
   prior gaps,
5. evaluate the three-candle formation ending at this candle,
6. reconcile zero, one, duplicate, conflicting, or dangling context links,
7. if a gap qualifies, append its immutable `FairValueGap`,
8. append its `None -> ACTIVE` formation transition and initial snapshot, and
9. promote the whole candidate state only after every step succeeds.

This ordering means:

- previously active gaps may fill or invalidate on candle `i`,
- a new gap ending at candle `i` is created only after those updates,
- that new gap cannot consume candle `i` as its own lifecycle observation, and
- any error or ambiguity in the same group promotes nothing from that group.

The analyzer must not use hash order, direction order, dictionary insertion order,
or internal iteration order as market chronology.

## 16. Locked Result Status Semantics

`SMCV2PrimitiveStatus` is used exactly:

- `UNKNOWN`
  - `candles` or `context_links` is `None`.
- `NONE`
  - complete empty inputs,
  - fewer than three valid candles,
  - complete valid inputs with no qualifying FVG, or
  - no emitted gap after all valid windows.
- `VALID`
  - at least one deterministic gap is emitted and no later group fails.
- `AMBIGUOUS`
  - one formation has multiple distinct otherwise valid context links and no
    deterministic link can be selected.
- `INVALID`
  - malformed present input,
  - invalid OHLC relationships,
  - non-increasing or duplicate chronology,
  - duplicate context evidence,
  - dangling, mismatched, or malformed context linkage,
  - identity or lifecycle inconsistency,
  - forbidden public-builder fields, or
  - any violation of this contract.

`UNKNOWN` is evaluated before present-input validation. For complete inputs,
precedence is `INVALID`, then `AMBIGUOUS`, then `VALID`, then `NONE`.

If a later issue has a determinable effective moment, valid gaps, transitions,
and snapshots strictly before that failing group remain immutable evidence in an
`INVALID` or `AMBIGUOUS` result. Nothing from the failing group or after it is
promoted.

If malformed required fields prevent a safe effective moment from being
determined, the result is `INVALID` and must not claim a trustworthy chronological
prefix.

## 17. Locked Prefix-Invariance Contract

A prefix is eligible for comparison only when it ends after one complete candle
effective group, including every same-moment context-link record and every
same-candle lifecycle update.

Every candle and context-link group appended for the longer comparison must have
an effective moment strictly later than the prefix boundary. Adding a link for an
earlier formation, supplying a same-effective partial group, or adding an earlier
candle is not an eligible future-prefix extension. The stateless full-batch API
does not compare historical arrival order and therefore does not label a
separately supplied complete batch `INVALID` solely because another invocation
previously omitted that link. An explicit incremental enrichment API does not
exist.

For every valid complete-group prefix, appending strictly later evidence must
preserve every prior:

- gap and gap ID,
- direction and formation source tuple,
- timestamp,
- boundary and midpoint,
- context-link value,
- transition and transition ID,
- snapshot and snapshot ID,
- lifecycle state, and
- tuple order

byte-for-byte.

Later evidence may append new gaps or advance active gaps. It may not rewrite a
formation, attach hindsight context, regress a lifecycle, change an original
boundary, change a midpoint, insert a transition into earlier history, or expire
a gap by elapsed time.

Repeated analysis of identical immutable inputs must produce dataclass-equal
results and byte-identical canonical identity payloads.

## 18. Locked Inline Synthetic 40-Case Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
exactly these numbered logical cases, with parameterization allowed:

1. Bullish three-candle FVG forms at the exact two-tick minimum.
2. Bearish three-candle FVG forms at the exact two-tick minimum.
3. Bullish and bearish one-tick gaps are valid near misses and emit no FVG.
4. Middle-candle body ratio exactly `0.60` qualifies using exact integer
   cross-multiplication.
5. Middle-candle body ratio one exact integer-cross-product unit below the
   threshold and a zero-range middle candle do not qualify.
6. No gap, identity, transition, snapshot, or context attachment is knowable
   before formation candle `i` closes.
7. Bullish lower and upper boundaries are exactly candle `i-2` high and candle
   `i` low.
8. Bearish lower and upper boundaries are exactly candle `i` high and candle
   `i-2` low.
9. Even-width gap produces exact integer-tick consequent encroachment.
10. Odd-width, negative, zero-centered, and arbitrary-magnitude gaps produce exact
    context-independent half/integer midpoint and canonical `.0`/`.5` text,
    including signed-zero normalization to `0.0`.
11. Formation emits exactly one immutable gap, `None -> ACTIVE` transition, and
    initial snapshot; all three formation candles are ineligible to fill it.
12. A later bullish wick exactly touching the proximal upper boundary emits
    `TOUCHED`.
13. A later bullish wick strictly inside but above midpoint emits
    `PARTIALLY_FILLED`.
14. A later bullish wick reaching midpoint but not the far boundary emits
    `MIDPOINT_FILLED`.
15. A later bullish wick reaching the far boundary without close-through emits
    `FULLY_FILLED`.
16. A bullish candle closing at least one tick through the far boundary emits
    `INVALIDATED`, taking precedence over same-candle full fill.
17. Bearish exact touch and partial fill mirror the bullish rules.
18. Bearish midpoint and full fill mirror the bullish rules.
19. Bearish close-through invalidation mirrors bullish invalidation and has the
    same precedence.
20. Direct jumps use the deepest reached state, shallower later observations do
    not regress state, terminal gaps do not transition again, and no time expiry
    occurs.
21. One formation-time displacement-only link is preserved as immutable metadata.
22. One formation-time BOS-only or displacement-plus-BOS link is preserved with
    exact foreign ID and type.
23. One formation-time CHOCH-only or displacement-plus-CHOCH link is preserved
    with exact foreign ID and type.
24. An explicit empty link tuple produces a valid unlinked gap with all optional
    metadata fields `None`.
25. Exact duplicate context-link records for one formation return `INVALID` with
    no same-group promotion.
26. Two distinct otherwise valid context links for one formation return
    `AMBIGUOUS`, independent of tuple order and hash lexical order, with no
    same-group promotion.
27. A dangling link, mismatched formation index/timestamp, and invalid structure
    ID/type pairing return `INVALID`; adding an old-effective link is rejected as
    an eligible prefix-extension comparison, and no incremental enrichment API
    exists.
28. `candles=None` and `context_links=None` each return `UNKNOWN` without partial
    promotion.
29. Complete empty inputs and complete one- or two-candle histories return `NONE`.
30. Three or more valid candles with no qualifying formation return `NONE`.
31. Missing, wrong-type, boolean tick, malformed timestamp, invalid OHLC, and
    internally malformed candle required fields return `INVALID` without
    exception leakage.
32. Missing, wrong-type, malformed hash, invalid event type, meaningless empty
    link, and internally malformed context-link fields return `INVALID` without
    exception leakage.
33. Duplicate or independently non-increasing candle indices or timestamps,
    causally out-of-order links, and non-tuple inputs return `INVALID` without
    silent sorting or repair.
34. One malformed or ambiguous later effective group preserves strictly prior
    immutable evidence, promotes nothing from the failing group, and demonstrates
    atomic multi-gap same-candle processing.
35. `GAP` identity is deterministic, formation-source-aware, direction-aware,
    boundary-aware, midpoint-aware, optional-link-aware, instrument/timeframe
    normalized, UTC normalized, and enforces its exact required/forbidden schema.
36. `TRANSITION` identity is deterministic, gap-aware, lifecycle-aware,
    reason-aware, effective-moment-aware, rejects an impossible graph edge or
    reason mismatch, and enforces its exact required/forbidden schema.
37. `SNAPSHOT` identity is deterministic, recomputes and exact-matches the complete
    ordered transition history, final state, and effective moment, and enforces
    its exact required/forbidden schema.
38. Exact keyword-only public signatures, frozen dataclass fields, exact enum
    values, exports, reason tokens, malformed-hash rejection, equivalent UTC
    normalization, unknown identity kind, and public exception containment are
    enforced.
39. Identical-run repeatability, complete-effective-group prefix boundaries,
    strictly later prefix invariance, same-effective append ineligibility for
    prefix comparison, immutable earlier output after later failure,
    deterministic multi-gap ordering, and status precedence are exact.
40. The standalone module has no pandas, file I/O, raw-data adapter, legacy SMC,
    Liquidity Map, Premium/Discount, Order Block, strategy, risk, execution,
    network, config, registration, or integration dependency, and focused plus
    full regression suites pass.

The fixture matrix does not justify an external fixture file. Fixtures must not
contain private market data, candidate OOS values, account details, credentials,
copied generated evidence, or outcome-derived parameters.

## 19. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/dealing_range.py`,
  `smc/liquidity_map.py`, `smc/premium_discount.py`, or `smc/__init__.py`,
- edits to or imports from legacy `smc/market_structure.py`,
  `smc/bos_choch.py`, `smc/liquidity_sweep.py`, or current SMC context,
- raw CSV, pandas, live candle, adapter, replay, or external-data ingestion,
- swing, displacement, BOS, CHOCH, Dealing Range, Liquidity Map, or
  Premium/Discount construction or mutation,
- Order Block, Mitigation Block, Breaker Block, Inducement, kill-zone, Volume
  Profile, context aggregation, confidence, signal, or filter code,
- runtime flags, CLI, runner, trace, package-registration, decision-path, or
  execution wiring,
- current SMC, CRT, Order Flow, DecisionContext, action, risk, sizing, stop,
  target, entry, exit, balance, or PnL changes,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- tuning, optimization, favorable reruns, or use of saved OOS outcomes,
- private data, generated reports, external evidence, Fibonacci analysis, or
  external fixtures, and
- staging, committing, or pushing future implementation without separate gates.

Any forbidden dependency is a stop condition. It does not authorize a workaround
or implicit scope expansion.

## 20. Mandatory Pre-Implementation Gates

Before any later Python, test, or checkpoint edit:

1. independently audit this record,
2. checkpoint this documentation record separately from code,
3. confirm the record on local and live `main`,
4. confirm a clean worktree and matching `HEAD = origin/main`,
5. run and record the full regression baseline,
6. verify all three reserved implementation targets remain absent,
7. verify the locked dependency files and hashes remain unchanged,
8. perform a read-only implementation preflight against the exact API,
   invariants, 40-case matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only the exact three-path task.

Passing this documentation decision is insufficient to begin coding.

## 21. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target already exists,
- any dependency hash or parent commit differs without a separately reviewed
  checkpoint,
- another tracked, staged, unstaged, ignored-generated, or untracked file appears,
- another path or external fixture appears necessary,
- a completed dependency or existing public interface appears to require change,
- fully closed immutable integer-tick input cannot remain the only price input,
- exact two-tick formation or exact `0.60` integer-ratio comparison cannot be
  preserved,
- exact integer/half-tick midpoint and canonical signed-zero text cannot be
  preserved without Decimal-context dependence,
- formation candles cannot be prevented from filling their own gap,
- close-through invalidation cannot retain precedence over full fill,
- optional links cannot remain formation-time metadata without hindsight,
- lifecycle history, identity reconciliation, atomic same-index processing, or
  prefix invariance cannot be demonstrated,
- deterministic multiple-gap ordering requires hash order as chronology,
- malformed required fields leak exceptions outside `TypeError` or `ValueError`
  in the public builder or outside fail-closed result statuses in the analyzer,
- a private, candidate, performance, generated, or external fixture appears
  necessary,
- runtime, strategy, risk, execution, config, registration, or integration
  appears necessary,
- focused tests or the full regression suite fail, or
- implementation appears necessary to resolve an ambiguity in this record.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, rounding, tuning, or an implementation shortcut.

## 22. Completion, Rollback, and Promotion Gates

Later implementation completion requires:

- independent review of every changed line,
- exact three-path reconciliation,
- all 40 numbered logical test cases passing,
- the full regression suite passing,
- deterministic gap, transition, and snapshot identity evidence,
- exact formation, ratio, boundary, midpoint, lifecycle, invalidation,
  no-retroactivity, same-index, fail-closed, and prefix-invariance evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed FVG checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and clean-scope
audit. Existing v1 and completed dependency files remain intact.

Successful implementation would prove only standalone deterministic FVG
conformance. It would not prove trading edge, OOS improvement, strategy value,
readiness, threshold approval, paper approval, live approval, or permission for
Order Block or any later phase.

## 23. Global Freeze and Next-Phase Boundary

The global code freeze remains active. This decision reserves one possible future
FVG task only. It does not authorize Order Block, Mitigation Block, Breaker Block,
Inducement, kill zones, Volume Profile, context aggregation, trace integration,
decision integration, or execution integration.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=FAIR_VALUE_GAP_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `RESERVED_IMPLEMENTATION_PATHS=3`
- `INLINE_SYNTHETIC_TEST_CASES=40`
- `OPERATIONAL_FREEZE_LIFT_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `TEST_OR_FIXTURE_CHANGE_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STRATEGY_OR_EXECUTION_CHANGE_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
