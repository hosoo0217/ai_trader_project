# SMC v2 Order Block Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-ORDER-BLOCK-FREEZE-LIFT-DECISION-2026-07-28`.
- Parent review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Parent specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Implementation-order phase: `7 - ORDER BLOCK`.
- Implementation parent commit:
  `212a7e0ad029cc22caf357e09b512e7a42b7bad1`.
- Requested module: standalone Order Block diagnostics.
- Current task type: documentation-only formal decision record.
- Decision classification:
  `APPROVED - DOCUMENTATION DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`.
- Global code-freeze status: `ACTIVE`.
- Python implementation authorized by this record: `False`.
- Test or fixture change authorized by this record: `False`.
- Integration authorized by this record: `False`.
- Staging, commit, or push authorized by this record: `False`.

This record reserves and specifies one possible future Order Block task. It does
not make the bounded exception operational, authorize code, or transfer
authority from any completed dependency task.

## 2. Effective-State Interpretation

The accepted implementation order completed before this decision is:

1. Shared primitives and test helpers.
2. Equal High and Equal Low.
3. Swing Hierarchy and Dealing Range.
4. Internal and External Liquidity Mapping.
5. Premium, Equilibrium, and Discount.
6. Fair Value Gap.
7. Order Block documentation decision.

The first six phases are committed, pushed, independently checkpointed, and
present on local and live `main`. Their completion satisfies the dependency-order
gate for this documentation decision only.

Fair Value Gap completion is an implementation-order dependency. An FVG is not a
required Order Block input, formation condition, filter, confidence modifier, or
identity field in this version.

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
- `smc/fair_value_gap.py`
  - SHA-256:
    `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`
- `docs/smc_v2_fair_value_gap_checkpoint.md`
  - SHA-256:
    `74BD85C1CAF19CAC94385034206D365150FD128D42BF50438486162194C05234`

The accepted specification locks these Order Block foundations:

- the causal trigger is a confirmed bullish or bearish BOS or CHOCH,
- the final displacement close breaks the referenced confirmed swing by at
  least one exact tick,
- displacement contains one to three consecutive fully closed candles,
- at least one displacement candle has body-to-range ratio at least `0.60` and
  body size at least the locked preceding-body median,
- at least ten preceding valid bars are required,
- the source is the most recent opposite-colored candle inside the finite
  ten-bar pre-displacement search window,
- wick and body boundaries are both preserved,
- the active v1 zone is wick-inclusive,
- formation candles cannot mitigate their own block,
- no default time expiry exists, and
- source swing, displacement candles, and structure event remain linked.

Shared primitives, confirmed swings, and confirmed structure events are direct
immutable dependencies. The future module must not construct, mutate, rerun, or
reinterpret swing, BOS, CHOCH, Dealing Range, Liquidity Map, Premium/Discount, or
FVG analysis.

## 4. Exact Change Authorized in This Documentation Task

Only this new file may be created in the current task:

- `docs/smc_v2_order_block_diagnostic_freeze_lift_decision.md`

No existing documentation, Python, test, fixture, configuration, private data,
external evidence, or generated report may change in this task. Staging, commit,
push, implementation, detector execution, and integration remain separate gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later implementation preflight and explicit human authorization pass, the
future task is reserved to exactly these three paths:

- production module: `smc/order_block.py`
- dedicated unit tests: `tests/test_order_block.py`
- implementation checkpoint: `docs/smc_v2_order_block_checkpoint.md`

All fixtures must be synthetic and inline in the dedicated test file. No external
or separate fixture file is reserved or authorized by this record.

The later task must not edit `smc/__init__.py`, `smc/smc_v2_primitives.py`,
`smc/dealing_range.py`, `smc/liquidity_map.py`, `smc/premium_discount.py`,
`smc/fair_value_gap.py`, or any existing SMC v1 module. Direct imports of
completed shared-primitives types and `normalize_utc_timestamp`, plus
`DealingRangeSwing`, `DealingRangeSwingSide`,
`DealingRangeStructureEvent`, `DealingRangeEventType`, and the public
`make_dealing_range_id` identity builder are sufficient.

Any need for another path is a stop condition requiring a new scope review and
explicit human approval before that edit occurs.

## 6. Exact Functional Boundary

The future standalone module may implement only:

- validation and chronological consumption of immutable fully closed
  integer-tick candles,
- validation and chronological consumption of caller-supplied confirmed swings
  and confirmed BOS or CHOCH structure events,
- deterministic bullish and bearish one-to-three-candle displacement
  qualification,
- deterministic source-candle selection from the finite backward window,
- immutable wick, body, proximal, distal, and exact midpoint boundaries,
- deterministic lifecycle transitions from later fully closed candles,
- immutable block, transition, and snapshot histories,
- exact status, reason, and blocking-reason output,
- deterministic identity construction, and
- prefix-invariant standalone diagnostics.

The future module may not:

- load a CSV, pandas object, broker feed, Sierra data, external API, or saved
  report,
- detect or confirm swings, BOS, CHOCH, Dealing Ranges, liquidity pools, FVGs,
  or any other upstream structure,
- infer missing foreign identities or repair caller-supplied foreign evidence,
- implement Mitigation Block, Breaker Block, Inducement, kill-zone, Volume
  Profile, confidence, signal, filter, or execution behavior,
- treat an Order Block as a BUY, SELL, entry, target, reversal, readiness, or
  trading-edge conclusion,
- use outcomes, PnL, trade results, private data, or candidate OOS evidence, or
- tune any formation, median, boundary, lifecycle, or invalidation threshold.

## 7. Locked Input Contracts

### 7.1 Top-Level Contract

The analyzer accepts exactly:

- `instrument: str`
- `timeframe: str`
- `candles: tuple[OrderBlockCandle, ...] | None`
- `swings: tuple[DealingRangeSwing, ...] | None`
- `structure_events: tuple[DealingRangeStructureEvent, ...] | None`

`instrument` and `timeframe` are stripped and uppercased exactly once. Empty
normalized values are `INVALID`.

If any one of `candles`, `swings`, or `structure_events` is `None`, complete
top-level context was not supplied and the analyzer returns `UNKNOWN`.

All supplied collections must be tuples. The analyzer must not accept generators,
lists, pandas objects, dictionaries, mutable adapters, or hidden global context.

An explicit empty swing tuple or structure-event tuple is complete supplied
evidence containing no such record. It is not automatically `UNKNOWN`.

### 7.2 Fully Closed Integer-Tick Candle Contract

`OrderBlockCandle` is a frozen dataclass with exactly:

- `index: int`
- `timestamp: datetime`
- `open_tick: int`
- `high_tick: int`
- `low_tick: int`
- `close_tick: int`

Every candle is declared fully closed by inclusion in the immutable tuple. The
future analyzer does not connect to a clock or decide whether a live candle has
closed.

Exact validation rules are:

- booleans, floats, strings, and Decimal prices are invalid for integer-tick
  fields,
- `index` is a non-negative exact integer,
- `timestamp` is timezone-aware and normalized to UTC,
- `low_tick <= open_tick <= high_tick`,
- `low_tick <= close_tick <= high_tick`, and
- `low_tick <= high_tick`.

A bullish candle has `close_tick > open_tick`. A bearish candle has
`close_tick < open_tick`. A doji has equality and is neither bullish nor bearish.

A zero-range candle is valid OHLC evidence but cannot satisfy a positive
body-to-range displacement-quality test.

Candle indices and normalized timestamps are independently strictly increasing
and unique. Caller order is causal order and is never silently sorted,
deduplicated, repaired, coerced, or backfilled. Adjacent tuple members are
adjacent supplied closed candles; numeric source indices need not differ by one.

### 7.3 Confirmed Swing Contract

Each supplied swing is an immutable `DealingRangeSwing` with exactly its
committed public fields:

- `side: DealingRangeSwingSide`
- `price_tick: int`
- `provenance: SMCV2EventProvenance`
- `swing_id: str`

The Order Block analyzer must:

- require `provenance` to be an intact `SMCV2EventProvenance`,
- require `source_indices` and `source_timestamps` to be immutable tuples of
  equal length containing exactly one source member,
- require the source index and confirmation index to be non-negative exact
  integers and every timestamp to be timezone-aware and normalized to UTC,
- require the source index/timestamp pair and confirmation index/timestamp pair
  to resolve exactly to supplied candles,
- require `confirmation_index >= source_index + 2`, preserving the committed
  two-closed-bar confirmation-delay rule,
- require confirmation timestamp to be strictly later than the source
  timestamp through the resolved strictly ordered candle tuple,
- require `price_tick` to be an exact non-boolean integer equal to the resolved
  source candle high for `HIGH` or low for `LOW`,
- validate `swing_id` as a lowercase 64-character SHA-256 identity,
- require a broken bullish-event swing to be `HIGH`,
- require a broken bearish-event swing to be `LOW`, and
- require both broken-swing confirmation index and normalized timestamp to be
  strictly before the selected displacement start.

Swing tuple order is strictly increasing by:

1. confirmation index,
2. the single provenance source index,
3. `side.value`, and
4. `swing_id`.

No separately exposed public swing-ID builder exists in the committed dependency
surface. The Order Block analyzer therefore treats a shape-valid `swing_id` as
immutable foreign identity evidence and validates all locally available
provenance, price, candle-reference, side, uniqueness, and ordering facts. It
must not invent a private swing-ID algorithm or claim to re-prove unavailable
foreign construction context.

Duplicate swing IDs, duplicate source-side identities, dangling candle
references, malformed provenance, source/confirmation mismatch, side-specific
price mismatch, confirmation-delay violation, or non-increasing composite order
is `INVALID`.

### 7.4 Confirmed Structure-Event Contract

Each supplied event is an immutable `DealingRangeStructureEvent` with exactly
its committed public fields:

- `direction: SMCV2Direction`
- `event_type: DealingRangeEventType`
- `broken_swing_id: str`
- `provenance: SMCV2EventProvenance`
- `event_id: str`

Only exact `BULLISH` or `BEARISH` direction and exact `BOS` or `CHOCH` type are
eligible. The analyzer must:

- require `provenance` to be an intact `SMCV2EventProvenance`,
- require non-empty immutable `source_indices` and `source_timestamps` tuples
  with equal length,
- require source indices to be non-negative exact integers, strictly increasing,
  and numerically contiguous by exactly one,
- require source timestamps to be timezone-aware, normalized to UTC, and
  independently strictly increasing,
- require every provenance source index/timestamp pair to resolve exactly to one
  supplied candle,
- require the final provenance source index and normalized timestamp to equal
  the event confirmation index and normalized timestamp,
- require that confirmation pair to resolve exactly to the final provenance
  candle,
- recompute the canonical event identity through public
  `make_dealing_range_id(identity_kind="EVENT", ...)` using the complete
  provenance source-index tuple, direction, event type, broken-swing ID,
  confirmation index, and a zero-width `SMCV2TickRange` at the broken-swing
  price, and require exact `event_id` match,
- require `broken_swing_id` to resolve exactly once in the supplied swing tuple,
- require event confirmation index and normalized timestamp to resolve to the
  final displacement candle,
- require the final close to satisfy the exact directional one-tick break.

A present `DealingRangeStructureEvent` declares that a confirmed structural
event exists. If its resolved final close does not satisfy the required
directional one-tick break of its referenced swing, the supplied event is
internally inconsistent and the complete effective group is `INVALID`. The
analyzer must not downgrade that inconsistency to a raw-candle near miss or
`NONE`.

Structure-event tuple order is strictly increasing by:

1. confirmation index,
2. normalized confirmation timestamp,
3. `direction.value`,
4. `event_type.value`, and
5. `event_id`.

Events with the same confirmation index and timestamp form one atomic event
group. Exact duplicate event IDs or records are `INVALID`. Multiple distinct
canonical events are permitted for validation as one atomic group:

- zero qualifying candidates emit no block,
- exactly one qualifying candidate is deterministic,
- two or more distinct otherwise qualifying candidates are `AMBIGUOUS`, and
- no candidate from an ambiguous group is promoted.

The analyzer never selects among distinct qualifying event/swing links by hash,
price, event type, or tuple position.

### 7.5 Effective Groups

The effective moment of:

- a candle is its index and normalized timestamp,
- a structure event is its confirmation index and normalized confirmation
  timestamp,
- a newly detected block is the final displacement candle and matched event
  confirmation moment, and
- a lifecycle transition is the later candle moment that first makes the
  transition knowable.

One complete effective group contains:

- the candle,
- every swing whose confirmation occurs at that moment,
- every structure event confirmed at that moment,
- every lifecycle update to prior blocks,
- every Order Block candidate ending at that moment, and
- every resulting transition and snapshot.

A prefix cannot end inside one effective group.

## 8. Locked Structural Break Semantics

A bullish Order Block candidate requires exactly:

1. a caller-supplied canonical confirmed swing with side `HIGH`,
2. a caller-supplied canonical confirmed bullish `BOS` or `CHOCH` event that
   references that swing,
3. swing confirmation strictly before displacement begins,
4. event confirmation exactly at the final displacement candle, and
5. final displacement close at least one tick above the swing:
   `final_close_tick >= swing.price_tick + 1`.

A bearish candidate is the exact mirror:

1. the referenced confirmed swing side is `LOW`,
2. event direction is `BEARISH`,
3. event type is `BOS` or `CHOCH`,
4. swing confirmation is strictly before displacement begins, and
5. `final_close_tick <= swing.price_tick - 1`.

A wick-only excursion through the swing or a close equal to the swing price is a
valid raw-candle near miss only when the complete structure-event evidence is an
explicit empty tuple or contains no event matching that candle and swing. Such a
near miss emits no block and may return `NONE`.

A present event that claims confirmation for that candle and swing but lacks the
exact directional one-tick close-break is `INVALID`. A mismatched direction,
swing side, event type, broken-swing reference, confirmation moment, or foreign
identity is also `INVALID`, not a relaxed near miss.

Complete valid inputs containing no supplied matching confirmed event emit no
block and may return `NONE`. A malformed or internally inconsistent present
event never reaches `NONE`.

## 9. Locked Displacement and Median Semantics

For one matched event, candidate displacement sequences are exactly the
available contiguous suffixes of that event's validated provenance
`source_indices` and normalized `source_timestamps`, ending at the event
confirmation candle with lengths `3`, `2`, and `1`, evaluated in that order.
Each suffix pair must resolve exactly, after required UTC normalization, to the
corresponding supplied-candle index and timestamp tuple.

The selected Order Block `displacement_indices` and
`displacement_timestamps` must equal one of those exact provenance suffixes.
They may not be assembled from candles outside the matched event provenance,
skip a provenance member, reorder a member, or substitute an equal-priced candle.
A non-suffix, index mismatch, timestamp mismatch, or suffix not ending at the
event confirmation moment is `INVALID`.

Every candle in:

- a bullish displacement sequence must be bullish, and
- a bearish displacement sequence must be bearish.

A sequence qualifies only if at least one member satisfies both:

1. exact real-body-to-range ratio at least `0.60`, using integer
   cross-multiplication:
   `5 * abs(close_tick - open_tick) >= 3 * (high_tick - low_tick)`, and
2. real body at least the locked preceding-body median.

The median baseline is the last up to `20` supplied closed candles strictly
before that candidate sequence begins:

- fewer than `10` valid preceding candles is insufficient,
- `10` through `19` available preceding candles use all available members,
- `20` or more available preceding candles use only the most recent `20`, and
- displacement members and source selection never enter their own median
  baseline.

Body sizes are non-negative exact integer ticks. Sorted median rules are:

- odd member count: the exact center integer body,
- even member count: exact Decimal average of the two center integer bodies,
- no float conversion or Decimal-context rounding, and
- canonical serialization uses exact `.0` or `.5`, with every signed zero
  normalized to `0.0`.

The selected displacement is the longest qualifying suffix. A shorter suffix is
considered only if every longer suffix fails a locked qualification rule. The
analyzer emits at most one displacement selection per valid structure event.

The selected sequence, comparison baseline, median, and qualifying member do not
become tunable configuration.

If the exact event and directional close-break exist but fewer than ten preceding
bars are available for every possible sequence, the result is `UNKNOWN` with an
insufficient-history blocking reason and no same-group promotion.

## 10. Locked Source-Candle Selection and Formation

For the selected displacement start, the source search window is exactly the last
up to ten supplied closed candles strictly before displacement begins.

- A bullish block requires the most recent bearish candle in that window.
- A bearish block requires the most recent bullish candle in that window.
- A doji is never an opposite-colored source.
- If multiple eligible source candles exist, choose the one with the greatest
  causal tuple position, independent of hash or price.
- If no eligible source exists in the finite window, emit no block.
- A candle outside the ten-candle window is never used.

The source candle must be strictly earlier than every displacement member. The
selected source, broken swing, displacement tuple, and matched structure event
are immutable formation evidence.

A block becomes first known in state `DETECTED` only when the final displacement
candle and matched event are confirmed. It is not active on any source,
comparison-baseline, swing-confirmation, or displacement candle.

## 11. Locked Boundaries, Midpoint, and Direction Context

Every block stores both source-candle boundary representations:

- `wick_low_tick = source.low_tick`
- `wick_high_tick = source.high_tick`
- `body_low_tick = min(source.open_tick, source.close_tick)`
- `body_high_tick = max(source.open_tick, source.close_tick)`

The v1 lifecycle zone is exactly wick-inclusive.

For a bullish block:

- `proximal_tick = wick_high_tick`
- `distal_tick = wick_low_tick`

For a bearish block:

- `proximal_tick = wick_low_tick`
- `distal_tick = wick_high_tick`

The exact consequent midpoint is:

`(wick_low_tick + wick_high_tick) / 2`.

It is calculated with integer arithmetic and represented as Decimal exact
integer or half-tick evidence. Canonical text is `.0` or `.5`, is independent of
ambient Decimal precision, supports arbitrary-magnitude positive and negative
ticks, and normalizes every zero representation to `0.0`.

Direction is mandatory formation and lifecycle context. It is not a trading
signal and never implies an entry, target, risk instruction, or expected outcome.

Original wick, body, proximal, distal, and midpoint values never change after
formation.

## 12. Locked Lifecycle and Same-Candle Precedence

`OrderBlockState` contains exactly:

- `DETECTED`
- `ACTIVE`
- `TOUCHED`
- `PARTIALLY_MITIGATED`
- `MITIGATED`
- `FULLY_TRAVERSED`
- `INVALIDATED`

Formation emits `None -> DETECTED` with reason `FORMATION_CONFIRMED`.

On the first fully closed candle strictly after the displacement-ending candle,
the block emits `DETECTED -> ACTIVE` with reason `FIRST_ELIGIBLE_BAR` before that
candle is evaluated for deeper lifecycle evidence. The formation sequence and
every earlier candle are ineligible to touch, mitigate, traverse, or invalidate
their own block.

For a bullish block, a later candle's `low_tick` controls wick-depth progression:

- `TOUCHED`: `low_tick == proximal_tick`,
- `PARTIALLY_MITIGATED`:
  `midpoint_tick < low_tick < proximal_tick`,
- `MITIGATED`: `distal_tick < low_tick <= midpoint_tick`,
- `FULLY_TRAVERSED`: `low_tick <= distal_tick` without adverse close-through,
  and
- `INVALIDATED`: `close_tick <= distal_tick - 1`.

For a bearish block, the exact mirror uses `high_tick`:

- `TOUCHED`: `high_tick == proximal_tick`,
- `PARTIALLY_MITIGATED`:
  `proximal_tick < high_tick < midpoint_tick`,
- `MITIGATED`: `midpoint_tick <= high_tick < distal_tick`,
- `FULLY_TRAVERSED`: `high_tick >= distal_tick` without adverse close-through,
  and
- `INVALIDATED`: `close_tick >= distal_tick + 1`.

Same-candle deepest-state precedence is exactly:

1. `INVALIDATED`,
2. `FULLY_TRAVERSED`,
3. `MITIGATED`,
4. `PARTIALLY_MITIGATED`,
5. `TOUCHED`,
6. unchanged current state.

The analyzer may skip intermediate states when one candle reaches a deeper
state. It must not emit synthetic intermediate transitions merely to fill the
graph.

Allowed later transitions are monotonic from any state except `INVALIDATED` to
any strictly deeper state in that precedence depth, or to `INVALIDATED`.
`FULLY_TRAVERSED` may only remain unchanged or later become `INVALIDATED`;
`INVALIDATED` alone is terminal. Shallower later observations do not regress
state. Mitigation never rewrites original boundaries.

No time expiry, maximum age, replacement, overlap suppression, or
best-block selection exists in version 1. End of input preserves the latest
state.

## 13. Locked Public API

The proposed public surface is limited to:

- `ORDER_BLOCK_DETECTOR_VERSION`
- `OrderBlockState`
- `OrderBlockCandle`
- `OrderBlock`
- `OrderBlockTransition`
- `OrderBlockSnapshot`
- `OrderBlockResult`
- `make_order_block_id`
- `analyze_order_blocks`

The exact keyword-only analyzer signature is:

```python
def analyze_order_blocks(
    *,
    instrument: str,
    timeframe: str,
    candles: tuple[OrderBlockCandle, ...] | None,
    swings: tuple[DealingRangeSwing, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
) -> OrderBlockResult:
    ...
```

No public configuration object exists in version 1. Break buffer, displacement
length, body ratio, median window, minimum history, source window, boundary,
midpoint, lifecycle, invalidation, and no-expiry rules are fixed semantics.

The exact keyword-only identity-builder signature is:

```python
def make_order_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_candle_index: int | None = None,
    source_candle_timestamp: datetime | None = None,
    source_swing_id: str | None = None,
    displacement_indices: tuple[int, ...] = (),
    displacement_timestamps: tuple[datetime, ...] = (),
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    detection_index: int | None = None,
    detection_timestamp: datetime | None = None,
    block_id: str | None = None,
    from_state: OrderBlockState | None = None,
    to_state: OrderBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: OrderBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    ...
```

Both functions normalize `instrument` and `timeframe` exactly once as
`value.strip().upper()`. Empty normalized values are invalid. Positional calls,
extra public parameters, pandas conversion, file loading, hidden globals, and
environment configuration are forbidden.

`OrderBlockCandle` is frozen and contains exactly the six fields locked in
Section 7.2.

`OrderBlock` is frozen and contains exactly:

- `block_id: str`
- `direction: SMCV2Direction`
- `source_candle_index: int`
- `source_candle_timestamp: datetime`
- `source_swing_id: str`
- `displacement_indices: tuple[int, ...]`
- `displacement_timestamps: tuple[datetime, ...]`
- `structure_event_id: str`
- `structure_event_type: DealingRangeEventType`
- `wick_low_tick: int`
- `wick_high_tick: int`
- `body_low_tick: int`
- `body_high_tick: int`
- `proximal_tick: int`
- `distal_tick: int`
- `midpoint_tick: Decimal`
- `detection_index: int`
- `detection_timestamp: datetime`

`OrderBlockTransition` is frozen and contains exactly:

- `transition_id: str`
- `block_id: str`
- `from_state: OrderBlockState | None`
- `to_state: OrderBlockState`
- `index: int`
- `timestamp: datetime`
- `reason: str`

`OrderBlockSnapshot` is frozen and contains exactly:

- `snapshot_id: str`
- `block_id: str`
- `direction: SMCV2Direction`
- `state: OrderBlockState`
- `index: int`
- `timestamp: datetime`
- `transition_ids: tuple[str, ...]`

`OrderBlockResult` is frozen and contains exactly:

- `status: SMCV2PrimitiveStatus`
- `blocks: tuple[OrderBlock, ...] = ()`
- `transitions: tuple[OrderBlockTransition, ...] = ()`
- `snapshots: tuple[OrderBlockSnapshot, ...] = ()`
- `reasons: tuple[str, ...] = ()`
- `blocking_reasons: tuple[str, ...] = ()`

Object tuples are chronological immutable evidence. Every exposed object ID must
exactly reproduce from the public identity builder.

## 14. Locked Deterministic Identity Contract

`ORDER_BLOCK_DETECTOR_VERSION` is exactly `SMC-V2-ORDER-BLOCK-1`.

The only identity kinds are:

- `BLOCK`
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
- exact midpoint `.0` or `.5` text,
- ordered tuples, and
- lowercase SHA-256 output.

No Python object representation, float, unordered set, dictionary insertion
order, locale, process ID, wall clock, random seed, or ambient Decimal context may
affect identity.

### 14.1 `BLOCK`

`BLOCK` requires exactly:

- direction,
- source-candle index and normalized timestamp,
- source swing ID,
- displacement indices of length one, two, or three,
- equal-length displacement timestamps,
- structure-event ID and type,
- wick and body boundaries,
- proximal and distal ticks,
- exact midpoint,
- detection index, and
- normalized detection timestamp.

The detection moment must equal the final displacement index and timestamp.
Displacement indices and timestamps must be independently strictly increasing.
Source candle must be strictly earlier than displacement start. Direction,
event type, boundary orientation, proximal, distal, and midpoint must reconcile
exactly with the analyzer-validated source and formation.

`BLOCK` forbids:

- `block_id`,
- `from_state`,
- `to_state`,
- `effective_index`,
- `effective_timestamp`,
- `reason`,
- `state`, and
- non-empty `transition_ids`.

### 14.2 `TRANSITION`

`TRANSITION` requires exactly:

- direction,
- block ID,
- from state, including `None` only for formation,
- to state,
- effective index,
- normalized effective timestamp, and
- one exact lifecycle reason.

Exact reason tokens are:

- `FORMATION_CONFIRMED`
- `FIRST_ELIGIBLE_BAR`
- `WICK_TOUCHED`
- `PARTIAL_MITIGATION`
- `MIDPOINT_MITIGATION`
- `DISTAL_TRAVERSAL`
- `CLOSE_THROUGH_INVALIDATION`

The initial transition is exactly:

- `from_state=None`,
- `to_state=DETECTED`, and
- `reason=FORMATION_CONFIRMED`.

The first later transition out of `DETECTED` includes:

- `from_state=DETECTED`,
- `to_state=ACTIVE`, and
- `reason=FIRST_ELIGIBLE_BAR`.

If that first eligible candle reaches a deeper state, the `ACTIVE` transition is
followed at the same effective moment by exactly one causal deeper transition.
Same-moment transitions are ordered by this lifecycle causality, not by hash.

Every other transition must match the locked lifecycle graph and target-state
reason. A direct deeper transition uses only the reason for the emitted target
state.

`TRANSITION` forbids:

- source-candle fields,
- source swing ID,
- non-empty displacement indices,
- non-empty displacement timestamps,
- structure-event fields,
- wick or body boundaries,
- proximal or distal ticks,
- midpoint,
- detection fields,
- `state`, and
- non-empty `transition_ids`.

### 14.3 `SNAPSHOT`

`SNAPSHOT` requires exactly:

- direction,
- block ID,
- current state,
- effective index,
- normalized effective timestamp, and
- a non-empty ordered transition-ID tuple.

The analyzer must recompute and exact-match every transition ID, require the
final transition target state and moment to equal the snapshot state and moment,
and require the ordered tuple to be the complete immutable transition history
for that block.

`SNAPSHOT` forbids:

- source-candle fields,
- source swing ID,
- non-empty displacement indices,
- non-empty displacement timestamps,
- structure-event fields,
- wick or body boundaries,
- proximal or distal ticks,
- midpoint,
- detection fields,
- `from_state`,
- `to_state`, and
- `reason`.

For every identity kind, every builder parameter is either exact required data or
exact forbidden default data. Missing required values, forbidden non-default
values, malformed hashes, invalid enums, impossible lifecycle edges, mismatched
reason tokens, unreconciled boundaries or midpoint, and unknown identity kinds
raise only `TypeError` or `ValueError`.

## 15. Locked Immutable Lifecycle and Snapshot Contract

One `OrderBlock` object is emitted exactly once at formation and never mutates.
One `OrderBlockTransition` and one corresponding `OrderBlockSnapshot` are emitted
for initial `DETECTED` and every later state change.

Transition history is append-only. Snapshot `transition_ids` are exact immutable
prefixes:

- the first snapshot contains exactly the formation transition ID,
- each later snapshot appends exactly one new transition ID,
- two transitions at one first-eligible effective moment produce two causally
  ordered snapshots, and
- no snapshot may skip, reorder, replace, or duplicate a transition.

Each block is updated independently. One candle may advance multiple prior
blocks. Deterministic output order for independent transitions is:

1. earlier detection index,
2. earlier normalized detection timestamp,
3. earlier source-candle index,
4. direction value,
5. lexicographic displacement-index tuple, and
6. block ID only as a final identity tie after causal fields are equal.

Block ID is not used to move later market evidence ahead of earlier evidence.

Invalidated terminal blocks remain in immutable history but are not evaluated
for later lifecycle transitions. A fully traversed block is evaluated only for a
later close-through invalidation. No snapshot is removed or rewritten.

## 16. Locked Chronology and Same-Index Processing Precedence

The complete caller-supplied candle, swing, and structure-event tuples are
validated without sorting before analysis. Each same-effective group is fully
validated before promotion.

For each valid candle effective group, exact processing precedence is:

1. validate the candle and independent index/timestamp ordering,
2. validate every swing confirmation and complete structure-event group at that
   moment,
3. clone the strictly prior immutable analysis state,
4. evaluate every nonterminal block detected before this candle,
5. append all valid prior-block lifecycle transitions and snapshots in locked
   causal order,
6. evaluate matched BOS or CHOCH events ending at this candle,
7. enumerate and select each event's longest qualifying displacement suffix,
8. select the most recent opposite source candle from the exact search window,
9. reconcile zero, one, exact duplicate, or multiple distinct qualifying
   event/swing-linked candidates,
10. append each deterministic immutable block,
11. append its `None -> DETECTED` transition and initial snapshot, and
12. promote the complete candidate state only after every step succeeds.

This ordering means:

- prior blocks may transition on candle `i`,
- a new block ending at candle `i` is created only after those updates,
- the new block cannot consume candle `i` or any formation candle as lifecycle
  evidence,
- one later candle may emit `DETECTED -> ACTIVE` and then one deeper transition
  at the same moment in causal order, and
- an error or ambiguity in any part of the group promotes nothing from that
  group or after it.

The analyzer must not use hash order, price order, dictionary insertion order,
or internal iteration order as market chronology.

## 17. Locked Result Status Semantics

`SMCV2PrimitiveStatus` is used exactly:

- `UNKNOWN`
  - any top-level tuple is `None`, or
  - an otherwise qualifying confirmed event has fewer than ten valid
    pre-displacement comparison bars for every candidate suffix.
- `NONE`
  - complete empty inputs,
  - complete valid inputs with no confirmed matching event,
  - an explicit empty structure-event tuple,
  - a raw-candle close-equal or wick-only near miss with no supplied event
    matching that candle and swing,
  - no qualifying displacement,
  - no opposite source candle in the finite window, or
  - no emitted block after all valid groups.
- `VALID`
  - at least one deterministic block is emitted and no later group fails.
- `AMBIGUOUS`
  - one atomic event group contains two or more distinct otherwise qualifying
    event/swing-linked candidates and no deterministic single candidate exists.
- `INVALID`
  - malformed present input,
  - invalid OHLC or non-increasing chronology,
  - foreign identity or reference mismatch,
  - a present confirmed structure event whose resolved close lacks the exact
    directional one-tick break,
  - duplicate swing or exact duplicate event evidence,
  - direction, swing-side, break, event, boundary, or lifecycle inconsistency,
  - forbidden public-builder fields, or
  - any other violation of this contract.

Top-level `UNKNOWN` is evaluated before present-input validation. For complete
inputs, precedence is `INVALID`, then `AMBIGUOUS`, then insufficient-history
`UNKNOWN`, then `VALID`, then `NONE`.

If a later issue has a determinable effective moment, valid blocks, transitions,
and snapshots strictly before that failing group remain immutable evidence in an
`INVALID`, `AMBIGUOUS`, or `UNKNOWN` result. Nothing from the failing group or
after it is promoted.

If malformed required fields prevent a safe effective moment from being
determined, the result is `INVALID` and must not claim a trustworthy
chronological prefix.

## 18. Locked Prefix-Invariance Contract

A prefix is eligible for comparison only when it ends after one complete candle
effective group, including every same-moment swing confirmation, structure event,
prior-block lifecycle update, and new formation.

Every candle, swing, and event group appended for the longer comparison must have
an effective moment strictly later than the prefix boundary. Adding a historical
swing or structure event, supplying a same-effective partial group, or adding an
earlier candle is not an eligible future-prefix extension.

For every valid complete-group prefix, appending strictly later evidence must
preserve every prior:

- block and block ID,
- direction and formation source,
- displacement tuple and structural linkage,
- wick, body, proximal, distal, and midpoint value,
- transition and transition ID,
- snapshot and snapshot ID,
- lifecycle state, and
- tuple order

byte-for-byte.

Later evidence may append new blocks or advance nonterminal blocks. It may not
rewrite a formation, change displacement selection, attach a different swing or
event, change an original boundary, regress lifecycle, insert an earlier
transition, or expire a block by elapsed time.

Repeated analysis of identical immutable inputs must produce dataclass-equal
results and byte-identical canonical identity payloads.

## 19. Locked Inline Synthetic 44-Case Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
exactly these numbered logical cases, with parameterization allowed:

1. A bullish one-candle displacement closes exactly one tick above a previously
   confirmed swing high and matched bullish BOS, producing one block.
2. A bearish one-candle displacement closes exactly one tick below a previously
   confirmed swing low and matched bearish BOS, producing the exact mirror.
3. Bullish and bearish CHOCH events qualify under the same exact structural
   rules as BOS.
4. With an explicit empty structure-event tuple or no matching event, a close
   equal to the swing price and a wick-only one-tick excursion are valid
   raw-candle near misses that emit no block and return `NONE`.
5. Bullish event with LOW swing, bearish event with HIGH swing, direction
   mismatch, broken-swing mismatch, and a present event claiming confirmation
   without the exact directional one-tick close-break are `INVALID`.
6. Swing confirmation equal to or later than displacement start is `INVALID`;
   strictly earlier confirmation qualifies.
7. Structure-event provenance source indices are contiguous, source tuples have
   equal length, and the final source index and equivalent UTC timestamp exactly
   match both event confirmation and the final displacement candle.
8. Swing hash shape and all locally available provenance/price facts validate;
   canonical event ID recomputation passes; dangling, malformed, or mismatched
   foreign identity is `INVALID` without exception leakage.
9. One-, two-, and three-candle directional displacement sequences qualify only
   as exact index/timestamp suffixes of the matched event provenance tuple.
10. Bullish sequences containing a bearish or doji member and bearish sequences
    containing a bullish or doji member do not qualify as those suffixes.
11. Body-to-range ratio exactly `0.60` qualifies by integer
    cross-multiplication.
12. One integer-cross-product unit below `0.60` and zero-range evidence fail the
    quality requirement.
13. At least one sequence member meeting both ratio and median conditions is
    sufficient; the remaining directional members need not meet both.
14. Exactly ten comparison bars qualify, nine are insufficient, and an
    otherwise qualifying event with insufficient history returns `UNKNOWN`.
15. Histories of 10 through 19 use every available pre-sequence member; histories
    of 20 or more use only the most recent 20.
16. Odd-count median is the exact center integer; even-count median is the exact
    average of the two centers.
17. Median equality qualifies and one exact half-tick below the median fails.
18. Zero and arbitrary-magnitude non-negative body baselines produce
    Decimal-context-independent `.0` or `.5` median text with canonical zero
    normalized to `0.0`.
19. When multiple event-provenance-bound 3/2/1 suffixes qualify, the longest
    suffix is selected deterministically; shorter suffixes are evaluated only
    after longer failure, and a non-suffix or timestamp-substituted sequence is
    `INVALID`.
20. The median baseline ends strictly before selected displacement and never
    includes displacement or source-selection hindsight.
21. A bullish block selects the most recent bearish source candle in the exact
    preceding ten-candle window.
22. A bearish block selects the most recent bullish source candle in the exact
    preceding ten-candle window.
23. Multiple opposite candles select the causally latest member, independent of
    hash and price; a doji is never selected.
24. The tenth preceding candle is eligible, the eleventh is excluded, and no
    eligible source in-window emits no block.
25. Wick and body boundaries reproduce the exact source OHLC for bullish and
    bearish blocks.
26. Bullish and bearish proximal and distal orientation is exact and
    wick-inclusive.
27. Even-width, odd-width, negative, zero-centered, and arbitrary-magnitude
    source ranges produce exact context-independent integer or half-tick
    midpoint and canonical signed-zero text.
28. Formation emits exactly one immutable block, `None -> DETECTED` transition,
    and initial snapshot; source, baseline, swing, and displacement candles
    cannot mitigate it.
29. First strictly later candle emits `DETECTED -> ACTIVE`; if it also reaches a
    deeper state, ACTIVE and the one deepest transition are causally ordered at
    the same effective moment.
30. Bullish exact proximal touch, strict upper-half entry, midpoint reach, and
    distal reach emit `TOUCHED`, `PARTIALLY_MITIGATED`, `MITIGATED`, and
    `FULLY_TRAVERSED`.
31. Bearish touch, partial mitigation, midpoint mitigation, and distal traversal
    are exact mirrors.
32. Bullish close one tick below distal and bearish close one tick above distal
    emit `INVALIDATED`; boundary-equal closes do not invalidate.
33. Same-candle invalidation takes precedence over traversal, direct jumps use
    the deepest state, and shallower observations never regress lifecycle.
34. `FULLY_TRAVERSED` may only remain unchanged or later become `INVALIDATED`;
    `INVALIDATED` is terminal, and no time expiry, replacement, or boundary
    mutation occurs.
35. `candles=None`, `swings=None`, and `structure_events=None` each return
    `UNKNOWN`; complete empty or valid no-formation inputs return `NONE`.
36. Non-tuple collections, malformed candle fields, boolean ticks, naive
    timestamps, invalid OHLC, and internally malformed dataclasses return
    `INVALID` without nested exception leakage.
37. Duplicate or independently non-increasing candle indices or timestamps,
    malformed swing provenance, duplicate swing identity, and non-increasing
    swing composite order return `INVALID` without silent repair.
38. Malformed event provenance, exact duplicate event ID or record, and
    non-increasing event composite order return `INVALID`.
39. Two distinct otherwise valid qualifying event/swing-linked candidates in one
    atomic group return `AMBIGUOUS`, independent of hash, price, event type, and
    input hash values after locked composite ordering, with no same-group
    promotion.
40. A malformed, insufficient, or ambiguous later group preserves strictly prior
    immutable evidence and promotes no block, transition, or snapshot from the
    failing group.
41. `BLOCK` identity is deterministic and sensitive to source candle, swing,
    exact event-provenance-bound displacement suffix, event, direction, both
    boundaries, proximal/distal, midpoint, detection moment, normalized
    instrument/timeframe, and equivalent UTC timestamps while enforcing its
    exact required/forbidden schema.
42. `TRANSITION` and `SNAPSHOT` identities enforce exhaustive
    required/forbidden schemas, valid lifecycle edges, exact reason tokens,
    complete ordered history, final state/effective-moment reconciliation,
    malformed-hash rejection, and exception containment.
43. Exact keyword-only public signatures and defaults, frozen dataclass fields,
    exact enum values, exports, unknown identity-kind rejection, repeatability,
    complete-group prefix invariance, same-effective append ineligibility, and
    deterministic multi-block ordering are enforced.
44. The standalone module has no pandas, file I/O, raw-data adapter, legacy SMC,
    FVG construction, Mitigation Block, Breaker Block, strategy, risk, execution,
    network, config, registration, or integration dependency, and focused plus
    full regression suites pass.

The matrix contains exactly `44` numbered logical cases. Parameterization may
expand collected pytest functions without changing this logical count.

The fixture matrix does not justify an external fixture file. Fixtures must not
contain private market data, candidate OOS values, account details, credentials,
copied generated evidence, or outcome-derived parameters.

## 20. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/dealing_range.py`,
  `smc/liquidity_map.py`, `smc/premium_discount.py`, `smc/fair_value_gap.py`, or
  `smc/__init__.py`,
- edits to or imports from legacy `smc/market_structure.py`,
  `smc/bos_choch.py`, `smc/liquidity_sweep.py`, or current SMC context,
- raw CSV, pandas, live candle, adapter, replay, or external-data ingestion,
- swing, BOS, CHOCH, Dealing Range, Liquidity Map, Premium/Discount, or FVG
  construction or mutation,
- Mitigation Block, Breaker Block, Inducement, kill-zone, Volume Profile,
  context aggregation, confidence, signal, or filter code,
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

## 21. Mandatory Pre-Implementation Gates

Before any later Python, test, or checkpoint edit:

1. independently audit this record,
2. checkpoint this documentation record separately from code,
3. confirm the record on local and live `main`,
4. confirm a clean worktree and matching `HEAD = origin/main`,
5. run and record the full regression baseline,
6. verify all three reserved implementation targets remain absent,
7. verify the locked dependency files and hashes remain unchanged,
8. perform a read-only implementation preflight against the exact API,
   invariants, 44-case matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only the exact three-path task.

Passing this documentation decision is insufficient to begin coding.

## 22. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target already exists,
- any dependency hash or parent commit differs without a separately reviewed
  checkpoint,
- another tracked, staged, unstaged, ignored-generated, or untracked file
  appears,
- another path or external fixture appears necessary,
- a completed dependency or existing public interface appears to require change,
- fully closed immutable integer-tick input cannot remain the only price input,
- confirmed caller-supplied swing and structure-event boundaries cannot remain
  intact,
- a swing, BOS, or CHOCH would need to be inferred or recomputed semantically,
- exact one-tick close-break, one-to-three displacement, `0.60` integer ratio,
  or longest-suffix selection cannot be preserved,
- minimum-ten/up-to-twenty median or exact even-member tie rule cannot be
  preserved without float or Decimal-context dependence,
- finite ten-candle source selection or doji exclusion cannot remain exact,
- wick/body, proximal/distal, midpoint, or direction rules become ambiguous,
- formation candles cannot be prevented from mitigating their own block,
- invalidation precedence, terminal-state behavior, no-expiry rule, or monotonic
  lifecycle cannot be demonstrated,
- multiple same-index candidates require hash or price order to choose a winner,
- lifecycle history, identity reconciliation, atomic processing, or prefix
  invariance cannot be demonstrated,
- malformed required fields leak exceptions outside `TypeError` or `ValueError`
  in the public builder or outside fail-closed result statuses in the analyzer,
- private, candidate, performance, generated, or external evidence appears
  necessary,
- runtime, strategy, risk, execution, config, registration, or integration
  appears necessary,
- focused tests or the full regression suite fail, or
- implementation appears necessary to resolve an ambiguity in this record.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, rounding, tuning, or an implementation
shortcut.

## 23. Completion, Rollback, Promotion, and Global-Freeze Gates

Later implementation completion requires:

- independent review of every changed line,
- exact three-path reconciliation,
- all 44 numbered logical test cases passing,
- the full regression suite passing,
- deterministic block, transition, and snapshot identity evidence,
- exact structural break, displacement, median, source, boundary, midpoint,
  lifecycle, invalidation, atomic-group, fail-closed, and prefix-invariance
  evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed Order Block checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and clean-scope
audit. Existing v1 and completed dependency files remain intact.

Successful implementation would prove only standalone deterministic Order Block
conformance. It would not prove trading edge, OOS improvement, strategy value,
readiness, threshold approval, paper approval, live approval, or permission for
Mitigation Block, Breaker Block, or any later phase.

The global code freeze remains active. This record reserves one possible future
Order Block task only. It does not authorize Mitigation Block, Breaker Block,
Inducement, kill zones, Volume Profile, context aggregation, trace integration,
decision integration, or execution integration.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=ORDER_BLOCK_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `RESERVED_IMPLEMENTATION_PATHS=3`
- `INLINE_SYNTHETIC_TEST_CASES=44`
- `OPERATIONAL_FREEZE_LIFT_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
