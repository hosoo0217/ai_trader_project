# SMC v2 Dealing Range Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-DEALING-RANGE-FREEZE-LIFT-DECISION-2026-07-19`.
- Parent review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Parent specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Implementation-order phase: `3 - SWING HIERARCHY AND DEALING RANGE`.
- Implementation parent commit:
  `d315b8dee89113926e2ae3f2cdeac537214f3552`.
- Requested module: standalone Swing Hierarchy and Dealing Range diagnostics.
- Current task type: documentation-only formal decision record.
- Decision classification:
  `APPROVED - DOCUMENTATION DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`.
- Global code-freeze status: `ACTIVE`.
- Python implementation authorized by this record: `False`.
- Integration authorized by this record: `False`.
- Staging, commit, or push authorized by this record: `False`.

This record reserves and specifies one possible future Dealing Range task. It
does not make the bounded exception operational, authorize code, or transfer
authority from either the shared-primitives task or the Equal Liquidity task.

## 2. Effective-State Interpretation

The accepted planning package requires the following implementation order:

1. Shared primitives and test helpers.
2. Equal High and Equal Low.
3. Swing Hierarchy and Dealing Range.
4. Internal and External liquidity mapping.
5. Premium, Equilibrium, and Discount.

The first two phases are committed and pushed. Their completion opens only the
dependency gate for this documentation decision. It does not automatically
authorize the third Python task.

The possible later implementation becomes operational only after all of these
separate gates pass:

1. independent final audit of this record,
2. documentation-only staging, commit, and push checkpoints,
3. local and live remote identity confirmation,
4. clean-worktree and collision checks,
5. read-only implementation preflight,
6. explicit human authorization for the exact implementation scope, and
7. test-first execution limited to that scope.

The global freeze remains active for every path outside that later exact task.

## 3. Locked Decision Inputs

This decision is derived from the accepted package and completed dependencies:

- `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256:
    `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`
- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`
- `docs/smc_v2_volume_profile_change_proposal.md`
  - SHA-256:
    `3089BA1CDACCC4353D16D8B3A6BC28D0D21219C1C7AFE2D88B6F0F2936D2E210`
- `docs/smc_v2_volume_profile_change_proposal_review.md`
  - SHA-256:
    `C94DDD8843DC849D1F3C141DAA8942F94C11F23CC189B99AFD7E45A4898762FA`
- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`
  - SHA-256:
    `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`
- `smc/smc_v2_primitives.py`
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `docs/smc_v2_equal_liquidity_diagnostic_freeze_lift_decision.md`
  - SHA-256:
    `4BEE737E6F447FD86B25918E3F2D43934961B8660F9B556AF296E8C4E0497DDE`
- `smc/equal_liquidity.py`
  - SHA-256:
    `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`
- `tests/test_equal_liquidity.py`
  - SHA-256:
    `3AA7AFF377FCCFEBB463615E6B16952B025FBB99432A7F9C2888AC96531B3E83`
- `docs/smc_v2_equal_liquidity_checkpoint.md`
  - SHA-256:
    `0962FE5A71BE1D6DEDF8C9BB63BBA2019DBFE880E4308872702EB8D8C3812A1D`

The Equal Liquidity post-push completion gate recorded `42` focused tests and
`1006` full regression tests passing. These facts establish dependency and
compatibility state only. They are not performance evidence.

## 4. Exact Change Authorized in This Documentation Task

The only repository path authorized for creation or modification now is:

- `docs/smc_v2_dealing_range_diagnostic_freeze_lift_decision.md`

No Python, test, fixture, configuration, package export, existing documentation,
external evidence, or generated report may change in this task. Staging, commit,
push, implementation, detector execution, and integration are separate gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later implementation preflight and explicit authorization pass, the task
is reserved to exactly these paths:

- production module: `smc/dealing_range.py`
- dedicated unit tests: `tests/test_dealing_range.py`
- implementation checkpoint: `docs/smc_v2_dealing_range_checkpoint.md`
- optional synthetic fixture, only if inline fixtures are proven insufficient:
  `tests/fixtures/dealing_range_cases.json`

Inline synthetic fixtures are required by default. The optional JSON path must
remain absent unless a later preflight records a concrete reviewed need.

The later task must not edit `smc/__init__.py`, `smc/smc_v2_primitives.py`,
`smc/equal_liquidity.py`, or any current SMC v1 module. Direct test imports are
sufficient. Any need for another path is a stop condition requiring a new scope
review and explicit human approval before that edit occurs.

## 6. Exact Functional Boundary

The future standalone module may implement only:

- immutable, already-confirmed swing inputs,
- immutable fully closed integer-tick observation inputs,
- immutable caller-supplied confirmed structural-event inputs,
- validation of the supplied structural event against its referenced swing and
  closed confirmation observation,
- deterministic bullish and bearish external Dealing Range construction,
- immutable nested internal-range snapshots,
- protected-boundary preservation, extension, replacement, and invalidation,
- versioned lineage, event, internal-range, and snapshot identities,
- explicit valid, invalid, unknown, none, and ambiguous results, and
- pure prefix-invariant analysis over immutable tuples.

The module does not detect raw swings, infer a displacement narrative, or import
the current float-based v1 Market Structure or BOS/CHOCH analyzers. The caller
supplies already-confirmed events; this module validates and consumes them under
the locked contract below. A future adapter is an integration task.

The module must not implement Internal or External liquidity classification,
Premium or Discount, FVG, Order Block, Mitigation Block, Breaker Block,
Inducement, kill zones, Volume Profile, confidence, signals, trade filtering,
risk, or execution.

## 7. Locked Confirmed-Swing Input Contract

`DealingRangeSwingSide` is a string enum with exactly:

- `HIGH`
- `LOW`

`DealingRangeSwing` is a frozen dataclass containing:

- `side: DealingRangeSwingSide`
- `price_tick: int`
- `provenance: SMCV2EventProvenance`
- `swing_id: str`

Each swing provenance contains exactly one source index and timestamp. The
source index identifies the swing-price bar. The confirmation index is the first
closed bar at which the compatible `swing_lookback=2` process can know the
swing, so it must be at least source index plus `2`.

Swing tuples must be immutable and strictly ordered by confirmation index, then
source index, then side, then swing ID. Duplicate source-side identities,
duplicate swing IDs, invalid side values, boolean or float ticks, naive
timestamps, missing required provenance, and internally malformed provenance
return `INVALID` without leaking attribute or validation exceptions.

The module validates but does not recreate each supplied swing ID. The ID must
be a lowercase 64-character SHA-256 value and must remain side-aware. A raw v1
`SwingPoint`, pandas object, or silently adapted float is invalid input.

Whenever a swing is referenced by an event or range construction, its source
observation is required. A `HIGH` swing price must equal that observation's
`high_tick`; a `LOW` swing price must equal its `low_tick`. Missing source
observation context is `UNKNOWN`; a present contradiction is `INVALID`.

## 8. Locked Closed-Observation Input Contract

`DealingRangeObservation` is a frozen dataclass containing:

- `index: int`
- `timestamp: datetime`
- `high_tick: int`
- `low_tick: int`
- `close_tick: int`

Observations represent fully closed bars only and must satisfy:

- `low_tick <= close_tick <= high_tick`
- integer ticks only, with booleans rejected,
- strictly increasing index,
- strictly increasing normalized UTC timestamp,
- no duplicate or silently sorted rows.

The observation tuple must be continuous across every interval used to build an
external extreme. A missing bar inside a required protected-source-through-
confirmation interval returns `UNKNOWN`; a present malformed bar returns
`INVALID`.

## 9. Locked Confirmed Structure-Event Input Contract

`DealingRangeEventType` is a string enum with exactly:

- `BOS`
- `CHOCH`

`DealingRangeStructureEvent` is a frozen dataclass containing:

- `direction: SMCV2Direction`
- `event_type: DealingRangeEventType`
- `broken_swing_id: str`
- `provenance: SMCV2EventProvenance`
- `event_id: str`

Only `SMCV2Direction.BULLISH` and `SMCV2Direction.BEARISH` are allowed. `NEUTRAL`
and `UNKNOWN` are invalid event directions.

The event provenance source indices are the ordered, contiguous closed bars in
the caller-declared displacement sequence. The first source index is the locked
displacement start. The last source index is the structural confirmation bar,
and it must equal the provenance confirmation index. The last source timestamp
must equal the normalized confirmation timestamp. An event with gaps, duplicate
indices, a future confirmation, or inconsistent timestamps is `INVALID`.

The broken swing must be confirmed strictly before the displacement start. A
bullish event must reference a confirmed `HIGH` swing. A bearish event must
reference a confirmed `LOW` swing. When the top-level swing tuple is supplied as
complete context, a `broken_swing_id` that is not present is a dangling foreign
key and returns `INVALID`. Wrong-side, duplicate, or internally contradictory
identity is also `INVALID`. This differs from failure to find an eligible
protected opposite swing, which remains `UNKNOWN` under Section 11.

The analyzer must regenerate the canonical `EVENT` identity from normalized
instrument, timeframe, direction, event type, referenced broken swing, event
provenance, confirmation index, and broken boundary tick. The supplied
`event_id` must match that value exactly. A malformed hash or mismatch returns
`INVALID`; the supplied ID is never trusted merely because it has 64 characters.

Each event confirmation timestamp must equal the normalized timestamp of the
observation at its confirmation index. A mismatch is `INVALID`.

The supplied structure-event tuple must be strictly increasing by the full
composite key `(confirmation_index, normalized_confirmation_timestamp,
direction.value, event_type.value, event_id)`. The analyzer must not silently
sort it. Identical confirmation index and normalized confirmation timestamp are
allowed and form one same-index event group.

One same-index group permits at most one event per direction. Two events with
the same direction in one group are `INVALID`, even when their event types or
IDs differ. Exactly one valid bullish event and one valid bearish event in one
group are `AMBIGUOUS`. The entire group is rejected atomically: no range,
transition, or terminal snapshot from that index is promoted. Duplicate event
IDs remain `INVALID`.

## 10. Locked One-Tick Close-Break Validation

The future analyzer must validate every supplied event using the closed
confirmation observation:

- bullish confirmation requires
  `close_tick >= broken_high_tick + break_buffer_ticks`,
- bearish confirmation requires
  `close_tick <= broken_low_tick - break_buffer_ticks`, and
- `break_buffer_ticks` is locked to `1` for detector version 1.

A wick through the broken swing without the required close does not confirm an
event. Because the input contract labels each supplied item as a confirmed
structure event, that contradiction is `INVALID`, not `NONE`. A close exactly at
the swing price is also invalid for a supplied confirmed event. The confirmation
candle cannot be replaced by a later candle to rescue it.

The first accepted construction event must be `BOS`. With no prior external
range, a caller-supplied `CHOCH` has insufficient prior directional context and
returns `UNKNOWN`. With an active range, a same-direction event must be `BOS`
and an opposite-direction event must be `CHOCH`. A contradictory supplied type
is `INVALID` rather than silently reclassified.

## 11. Locked Protected Opposite Swing Selection

For a bullish event, protected-swing candidates are confirmed `LOW` swings. For
a bearish event, they are confirmed `HIGH` swings.

A protected candidate is eligible only when all of the following are true:

- its source index is strictly before the displacement start,
- its confirmation index is strictly before the displacement start,
- its normalized confirmation timestamp is strictly before the displacement
  start observation timestamp, and
- it has not been invalidated by malformed or contradictory input.

From eligible candidates, choose the swing with the greatest source index. An
exact source-index tie is resolved by greatest confirmation index, then the
lexicographically smallest swing ID. Duplicate source-side identity remains
invalid and is not repaired by the tie-breaker.

If no eligible protected swing exists, return `UNKNOWN`. Duplicate source-side
protected identities or any contradictory protected identity are `INVALID` and
promote no range. They are not repaired by a tie-breaker and cannot produce an
`AMBIGUOUS` result. After invalid identities are rejected, the locked source,
confirmation, and swing-ID tie-breakers always select at most one protected
swing deterministically.

The protected swing is selected from the pre-displacement snapshot. A swing
confirmed on the displacement start index or later cannot be used retroactively.

## 12. Locked External Range Construction and Exact Midpoint

The external extreme is calculated from the complete inclusive closed-bar
interval beginning at the selected protected swing's source index and ending at
the event confirmation index:

- bullish range:
  - low boundary is the protected `LOW` swing price,
  - high boundary is the maximum observation `high_tick` in the interval;
- bearish range:
  - high boundary is the protected `HIGH` swing price,
  - low boundary is the minimum observation `low_tick` in the interval.

The protected boundary must equal its source observation extreme. A conflict
between the supplied swing price and the source observation is `INVALID`.

Every valid external range satisfies `low_tick < high_tick`. A zero-width or
inverted range is invalid.

The exact midpoint is:

`Decimal(low_tick + high_tick) / Decimal(2)`

It is exposed as `midpoint_tick: Decimal`. It may be an integer tick or an exact
half tick. It must never use binary float, integer truncation, ceiling, floor,
banker's rounding, or a favorable directional tie rule. The midpoint is derived
and is not an independently mutable boundary.

The range becomes first known at the structural event confirmation index and
timestamp. Earlier source bars must not receive the later range label.

## 13. Locked Public API

The proposed public surface of the future module is limited to:

- `DEALING_RANGE_DETECTOR_VERSION`
- `DealingRangeSwingSide`
- `DealingRangeEventType`
- `DealingRangeKind`
- `DealingRangeState`
- `DealingRangeConfig`
- `DealingRangeSwing`
- `DealingRangeObservation`
- `DealingRangeStructureEvent`
- `DealingRangeTransition`
- `DealingRangeSnapshot`
- `DealingRangeResult`
- `make_dealing_range_id`
- `analyze_dealing_ranges`

The exact keyword-only analyzer signature is locked as:

```python
def analyze_dealing_ranges(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...] | None,
    observations: tuple[DealingRangeObservation, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    config: DealingRangeConfig = DealingRangeConfig(),
) -> DealingRangeResult:
    ...
```

The exact keyword-only identity-builder signature is locked as:

```python
def make_dealing_range_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...],
    swing_ids: tuple[str, ...] = (),
    event_type: DealingRangeEventType | None = None,
    broken_swing_id: str | None = None,
    confirmation_index: int | None = None,
    boundaries: SMCV2TickRange | None = None,
    lineage_id: str | None = None,
    protected_swing_id: str | None = None,
    construction_event_id: str | None = None,
    range_kind: DealingRangeKind | None = None,
    state: DealingRangeState | None = None,
    transition_ids: tuple[str, ...] = (),
    transition_from_state: DealingRangeState | None = None,
    transition_to_state: DealingRangeState | None = None,
    transition_index: int | None = None,
    transition_timestamp: datetime | None = None,
    transition_reason: str | None = None,
    related_event_id: str | None = None,
    replacement_lineage_id: str | None = None,
) -> str:
    ...
```

Both functions require `instrument` and `timeframe` to be strings. Each value is
normalized exactly once as `value.strip().upper()`. An empty normalized value is
invalid. The normalized values are used in every identity payload and analysis
comparison; original casing and surrounding whitespace cannot affect an ID.
Both functions perform no I/O. Positional calls, additional public parameters,
implicit pandas conversion, and hidden global configuration are outside the
locked version-1 API.

`DealingRangeKind` contains exactly `EXTERNAL` and `INTERNAL`.

`DealingRangeState` contains exactly:

- `ACTIVE`
- `SUPERSEDED`
- `INVALIDATED`

The module-specific state enum is deliberate. Replacement is not equivalent to
price invalidation, and the shared primitives must not be edited merely to add a
`SUPERSEDED` state. Transitions are immutable module-specific records rather
than misleading shared lifecycle events.

`DealingRangeConfig` is frozen with these locked version-1 values:

- `swing_confirmation_bars=2`
- `break_buffer_ticks=1`

Both must be real positive integers; booleans are rejected. Version 1 rejects
any different values. Variants require a new recorded specification and cannot
be chosen from observed outcome or performance data.

`DealingRangeTransition` is frozen and contains:

- `transition_id: str`
- `lineage_id: str`
- `from_state: DealingRangeState | None`
- `to_state: DealingRangeState`
- `index: int`
- `timestamp: datetime`
- `reason: str`
- `related_event_id: str | None`
- `replacement_lineage_id: str | None`

`reason` accepts exactly these case-sensitive tokens:

- `CONSTRUCTION_ACTIVE`
- `OBSERVATION_CLOSE_THROUGH_INVALIDATION`
- `CHOCH_CLOSE_THROUGH_INVALIDATION`
- `BOS_PULLBACK_REPLACEMENT`

`CONSTRUCTION_ACTIVE` belongs only to `None -> ACTIVE`.
`OBSERVATION_CLOSE_THROUGH_INVALIDATION` belongs only to an observation-only
`ACTIVE -> INVALIDATED` transition. `CHOCH_CLOSE_THROUGH_INVALIDATION` belongs
only to a reverse-CHOCH `ACTIVE -> INVALIDATED` transition.
`BOS_PULLBACK_REPLACEMENT` belongs only to `ACTIVE -> SUPERSEDED`. Any other
token, casing, surrounding whitespace, or transition-token mismatch is
`INVALID`; reason text is never normalized or treated as free-form text.

The exact transition graph is `None -> ACTIVE`, `ACTIVE -> SUPERSEDED`, and
`ACTIVE -> INVALIDATED`. Transition indices and timestamps are strictly
chronological. `INVALIDATED` and `SUPERSEDED` are terminal for that lineage.
`related_event_id` is required for BOS, CHOCH, or event-driven transitions and
is `None` only for observation-only invalidation. `replacement_lineage_id` is
required only for `SUPERSEDED` and forbidden for `ACTIVE` or `INVALIDATED`.

`DealingRangeSnapshot` is frozen and exposes kind, direction, snapshot ID,
ordered source swing IDs, low tick, high tick, exact Decimal midpoint tick, and
first-known provenance for both range kinds. It also contains these explicitly
kind-dependent fields:

- `lineage_id: str | None`
- `protected_swing_id: str | None`
- `construction_event_id: str | None`
- `state: DealingRangeState | None`
- `transitions: tuple[DealingRangeTransition, ...]`
- `transition_ids: tuple[str, ...]`
- `replacement_lineage_id: str | None`

An `EXTERNAL` snapshot requires lineage, protected swing, construction event,
state, transitions, and exactly matching ordered transition IDs. An `INTERNAL`
snapshot uses its `INTERNAL_RANGE` identity as `snapshot_id`; every external-only
field is `None` and both transition tuples are empty. The ordered transition IDs
of an external snapshot must exactly equal the IDs of the exposed transition
tuple in the same order.

`DealingRangeResult` is frozen and exposes `SMCV2PrimitiveStatus`, immutable
range snapshots, reasons, and blocking reasons.

No runtime enable flag is introduced because there is no runtime import or
integration. The module remains inert unless directly imported and called.

## 14. Locked Deterministic Identity Contract

All IDs are lowercase SHA-256 values generated from canonical JSON with sorted
keys, ASCII encoding, compact separators, and no binary floats.

The identity kinds are exactly:

- `EVENT`
- `TRANSITION`
- `LINEAGE`
- `SNAPSHOT`
- `INTERNAL_RANGE`

Every payload includes detector version, identity kind, normalized instrument,
normalized timeframe, and direction.

An `EVENT` ID additionally includes event type, broken swing ID, ordered event
source indices, confirmation index, and the broken swing boundary tick.

A `TRANSITION` ID additionally includes lineage ID, one transition source index,
normalized transition timestamp, previous state, next state, exact reason token,
optional related event ID, and optional replacement lineage ID. The timestamp
must first pass `normalize_utc_timestamp` and then be serialized exactly as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`; no offset, shortened fraction, or alternate form
is permitted in the canonical payload. The transition source index must equal
`transition_index`. A supplied transition ID must equal the regenerated
canonical value; mismatch is `INVALID`.

A `LINEAGE` ID additionally includes protected swing ID, first construction
event ID, direction, and initial low and high ticks. A same-direction extension
that preserves the protected swing preserves the lineage ID. A replacement or
reverse range creates a new lineage ID.

A `SNAPSHOT` ID additionally includes lineage ID, current construction event ID,
ordered source swing IDs, current low and high ticks, state, and ordered
transition IDs. State or boundary changes create a new snapshot without
rewriting prior snapshots. Every transition ID is regenerated and checked before
the snapshot ID is built.

An `INTERNAL_RANGE` ID includes exactly two ordered opposing swing IDs, their
ordered source indices, direction, and low and high ticks.

Required and forbidden fields are validated separately for each identity kind.
Unknown identity kinds, malformed hashes, unordered source identities, or
semantically impossible payload shapes are invalid.

The identity-specific required and forbidden parameter schemas are locked:

- `EVENT` requires non-empty event `source_indices`, empty `swing_ids`, event
  type, broken swing ID, confirmation index, and a one-price boundary where
  lower and upper ticks both equal the broken swing price. It forbids every
  lineage, range, state, transition, and replacement parameter.
- `TRANSITION` requires exactly one source index, empty `swing_ids`, lineage ID,
  from state or the explicit initial `None`, to state, transition index,
  timestamp, reason, and the event or observation relationship rules above. It
  forbids event type, broken swing, confirmation, boundary, protected swing,
  construction event, range kind, state, and `transition_ids`.
- `LINEAGE` requires exactly two ordered source indices and exactly two ordered
  swing IDs for the protected and broken swings, protected swing ID,
  construction event ID,
  `range_kind=EXTERNAL`, and initial boundaries. It forbids event-specific,
  snapshot-state, transition, and replacement parameters.
- `SNAPSHOT` requires ordered source indices and swing IDs, boundaries, lineage
  ID, construction event ID, `range_kind=EXTERNAL`, state, and ordered
  transition IDs. Source and swing-ID tuple lengths must match and contain at
  least the protected and broken swing identities. Replacement lineage is
  required exactly when state is `SUPERSEDED`; it is forbidden otherwise. Event
  and transition-construction parameters are forbidden. `range_kind=INTERNAL`
  is invalid for `SNAPSHOT` because internal snapshots use `INTERNAL_RANGE`.
- `INTERNAL_RANGE` requires exactly two ordered source indices, exactly two
  ordered opposing swing IDs, `range_kind=INTERNAL`, and boundaries. It forbids
  event, lineage, protected-swing, state, transition, and replacement
  parameters.

A direct `make_dealing_range_id` call with a forbidden non-default parameter or
missing required semantic parameter raises `TypeError` or `ValueError`; values
are not ignored to make a payload fit. When the analyzer validates a supplied
event or constructs a result, it catches that identity-contract failure and
returns an `INVALID` result with an explicit blocking reason.

## 15. Locked Same-Direction BOS Extension and Replacement

For an active bullish range, a later bullish `BOS` is same-direction. The
bearish case is the exact mirror.

Before processing a same-direction BOS, the analyzer captures one immutable
`pre_index_active_range` snapshot. Lifecycle and invalidation observations at
the same index are evaluated against that snapshot. A range invalidated at that
index cannot then be extended or replaced.

If no new eligible protected pullback swing exists, the event may extend only
the external target:

- bullish: the high may increase but may not decrease,
- bearish: the low may decrease but may not increase,
- protected boundary and lineage ID remain unchanged, and
- a non-extending event does not create a duplicate snapshot.

A new protected pullback swing may establish a replacement range only if it:

- is the opposite side required by the range direction,
- has source and confirmation strictly after the prior range construction
  event,
- has confirmation strictly before the new event displacement start,
- lies strictly inside the prior active external boundaries,
- does not cross or invalidate the prior protected boundary, and
- is selected by the locked protected-swing tie rules.

The later same-direction BOS first emits a terminal `SUPERSEDED` snapshot for
the old lineage, then creates one new `ACTIVE` lineage from the confirmed
pullback swing. The old and new snapshots are immutable and explicitly linked.

A pullback swing alone never replaces the active range. Replacement requires a
later confirmed same-direction BOS.

## 16. Locked Reverse CHOCH and Same-Index Precedence

For an active bullish range, a bearish `CHOCH` must close at least `1` tick below
the protected low. For an active bearish range, a bullish `CHOCH` must close at
least `1` tick above the protected high.

The reverse event's `broken_swing_id` must equal the active range's protected
swing ID. Referencing another same-side swing cannot invalidate the protected
boundary and is `INVALID`.

A wick alone beyond the protected boundary does not invalidate or reverse the
range. A close exactly at the protected boundary also does not invalidate it.

At a valid reverse-CHOCH confirmation index, processing order is locked:

1. capture the immutable `pre_index_active_range`,
2. validate the event reference and confirmation observation against that
   pre-index snapshot,
3. evaluate the close-through invalidation against the same snapshot,
4. coalesce the observation and CHOCH into exactly one canonical `INVALIDATED`
   transition for the old lineage,
5. emit exactly one old-lineage terminal snapshot,
6. select the new opposite protected swing from context confirmed strictly
   before the displacement start,
7. construct the new reverse range, and
8. emit its first `ACTIVE` snapshot.

The old range must be invalidated before the new lineage exists. The same event
cannot extend the old lineage, reuse a terminal lineage, or consume context
confirmed at or after displacement start.

Observation-based invalidation and CHOCH event processing at the same index are
not two lifecycle events. They share the canonical transition ID associated
with the reverse event. A second invalidation transition or duplicate terminal
snapshot is `INVALID`.

If the old range is invalidated but complete context for the new reverse range
is missing, the old invalidation remains valid while the attempted new range is
reported as `UNKNOWN`. The analyzer must not resurrect the old range or invent a
replacement boundary.

## 17. Locked Nested Internal-Range Semantics

Every valid confirmed swing is an internal swing candidate. Internal-range
reporting does not classify liquidity and does not change external hierarchy.

An internal range requires two chronologically adjacent eligible swings of
opposite side in the combined confirmed-swing sequence:

- `LOW` then `HIGH` is `BULLISH`,
- `HIGH` then `LOW` is `BEARISH`.

Both source prices must lie strictly inside the active external boundaries.
Both swings must be confirmed no later than the internal range first-known
index. The internal low and high are the two swing prices, the exact midpoint
uses the same Decimal rule, and first-known time is the later swing confirmation.

An internal pair with a boundary equal to or outside an external boundary is not
nested and is not emitted as an internal range. Same-side adjacent swings do not
form a pair. An internal range never replaces, extends, invalidates, or changes
the protected swing of the external range.

Prior internal snapshots are immutable. Later external replacement may change
which internal pairs are eligible prospectively, but it cannot relabel a prior
emitted internal snapshot using future information.

## 18. Locked Result Status Semantics

The top-level `swings`, `observations`, and `structure_events` inputs each accept
an immutable tuple or `None`.

- `VALID`: at least one valid external or internal range snapshot is emitted.
- `NONE`: complete valid context is supplied but no qualifying confirmed range
  exists.
- `UNKNOWN`: a required top-level context is `None`, an eligible protected swing
  is absent, a required construction interval is incomplete, or an initial
  `CHOCH` lacks prior range context. A dangling supplied foreign-key identity is
  not missing context; it is `INVALID` under Section 9.
- `AMBIGUOUS`: exactly one valid bullish event and one valid bearish event occur
  in the same confirmation-index and normalized-timestamp group.
- `INVALID`: malformed type, identity, provenance, chronology, OHLC relation,
  tick, configuration, event type, direction, close-break relationship,
  impossible transition, duplicate source, duplicate or contradictory protected
  identity, or internally malformed required field is present.

An empty supplied tuple is complete context, not missing context. Empty swings
or structure events can return `NONE`. Invalid rows are not discarded. The
analyzer must not silently coerce, sort, repair, infer, or choose a favorable
candidate.

Top-level missing context is checked first and returns `UNKNOWN` with no partial
analysis. For complete top-level inputs, result precedence is `INVALID`, then
`AMBIGUOUS`, then `UNKNOWN`, then `VALID`, then `NONE`. Chronologically valid
snapshots strictly before a later failing index remain immutable evidence, but
no snapshot from the failing index is promoted.

The reverse-CHOCH exception in Section 16 is deliberate: a valid close through
the old protected boundary emits the old terminal snapshot before new-range
context is selected. If that new context is missing, the overall result is
`UNKNOWN` and may contain that already-complete old terminal snapshot; it never
contains a partial new range.

## 19. Locked Chronology and Prefix-Invariance Rules

All evaluation uses fully closed observations and the event-time snapshot known
at each confirmation index.

The full same-index event group is validated before any state mutation or
snapshot emission. A duplicate-direction group returns `INVALID`. An opposing-
direction group returns `AMBIGUOUS`. In either case, the atomic no-partial-
promotion rule in Section 9 overrides the normal pipeline below: no transition
or snapshot from that index is emitted, while earlier immutable snapshots remain
unchanged.

When an observation, a swing confirmation, and a structure event share an index,
the locked order is:

1. capture one immutable `pre_index_active_range`,
2. evaluate the observation against that snapshot and record a pending terminal
   condition without emitting twice,
3. validate any event reference that requires the old range against the same
   pre-index snapshot,
4. coalesce observation and event evidence into at most one terminal transition,
5. emit the old terminal snapshot before any new lineage,
6. make newly confirmed swings available for later prospective use,
7. validate the remaining event context against the locked pre-displacement
   eligibility rules,
8. process permitted extension, replacement, or reverse construction, and
9. emit immutable new snapshots.

If the pending terminal condition conflicts with a same-direction BOS, the old
range terminates and that BOS cannot extend or replace it. If it matches a valid
reverse CHOCH, the exactly-one transition rule in Section 16 applies.

Newly confirmed same-index swings are unavailable for protected-swing selection
because eligibility is strictly pre-displacement. Appending future observations,
swings, or events must preserve every prior result snapshot byte-for-byte.

## 20. Locked Inline Synthetic 36-Case Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
exactly these numbered logical cases, with parameterization allowed:

1. Bullish external range positive construction.
2. Bearish external range positive construction.
3. Exact `1`-tick bullish and bearish close-break boundaries.
4. A supplied confirmed event closing exactly at the broken swing returning
   `INVALID` with no transition.
5. A supplied confirmed wick-only event returning `INVALID` with no transition.
6. `swings=None` returning `UNKNOWN` without partial promotion.
7. `observations=None` returning `UNKNOWN` without partial promotion.
8. `structure_events=None` returning `UNKNOWN` without partial promotion.
9. Complete empty tuples returning `NONE`.
10. Missing, wrong-type, and internally malformed swing required fields, plus a
    complete tuple containing a dangling `broken_swing_id`, returning `INVALID`
    without exception leakage; missing eligible protected swing remains
    `UNKNOWN`.
11. Missing, wrong-type, and internally malformed event required fields,
    confirmation-observation timestamp mismatch, and canonical `event_id`
    mismatch returning `INVALID` without exception leakage.
12. Invalid observation type, boolean or float tick, chronology, timestamp, and
    OHLC relationship returning `INVALID`.
13. Swing confirmation exactly source plus `2` accepted; earlier confirmation
    rejected.
14. Broken swing confirmation strictly before displacement start.
15. Protected swing confirmation strictly before displacement start.
16. Same-index or later protected confirmation excluded without hindsight.
17. Most-recent protected-swing selection and deterministic tie resolution.
18. Missing protected swing returning `UNKNOWN`.
19. Public `analyze_dealing_ranges()` rejection of duplicate or contradictory
    protected identities as `INVALID`, with no promoted range.
20. Inclusive protected-source-through-confirmation bullish maximum and bearish
    minimum.
21. Missing interval observation returning `UNKNOWN`; malformed present row
    returning `INVALID`.
22. Swing price and source observation conflict returning `INVALID`.
23. Integer midpoint and both odd-sum exact half-tick midpoint directions.
24. Event, transition, lineage, snapshot, and internal-range ID repeatability;
    instrument/timeframe strip-plus-uppercase normalization; exact UTC
    transition timestamp serialization; exact reason-token identity coverage;
    mismatch rejection; required/forbidden payload schemas; and direction
    separation.
25. Same-direction BOS target extension preserving protected boundary and
    lineage.
26. Non-extending same-direction BOS producing no duplicate snapshot.
27. Later extension preserving every prior snapshot unchanged.
28. Confirmed pullback plus later BOS replacement and linked `SUPERSEDED` state.
29. Pullback without later BOS not replacing the active range.
30. Bullish and bearish protected-boundary invalidation with exact boundary
    non-invalidation and wick-only non-invalidation.
31. Reverse CHOCH pre-index-snapshot validation, invalidation-before-new-range
    precedence, exactly one transition, and duplicate-invalidation rejection.
32. Reverse invalidation with missing new-range context preserving old terminal
    state and returning `UNKNOWN` for the attempted construction.
33. Same-index composite-key ordering, duplicate-direction events returning
    `INVALID`, opposing bullish and bearish valid events returning `AMBIGUOUS`,
    and atomic no-same-index-partial promotion.
34. Nested bullish and bearish internal ranges, strict-boundary exclusion, and
    proof that internal ranges never replace the external range.
35. Identical-run repeatability and appended-future prefix invariance.
36. Frozen public API, exact keyword-only function signatures, and proof of no
    pandas, v1 SMC, I/O, network, configuration, registration, execution, or
    integration dependency.

The optional JSON fixture is not justified by this matrix and must remain absent
unless a later preflight demonstrates that inline fixtures are insufficient.
Fixtures must contain no private market data, candidate OOS values, account
details, credentials, copied evidence, or outcome-derived parameters.

## 21. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/equal_liquidity.py`, or
  `smc/__init__.py`,
- importing `smc/market_structure.py`, `smc/bos_choch.py`, pandas, or current
  production analyzers,
- raw swing detection or raw BOS/CHOCH discovery,
- Internal or External liquidity mapping or classification,
- Premium, Equilibrium, Discount, FVG, Order Block, Mitigation Block, Breaker
  Block, Inducement, kill-zone, or Volume Profile code,
- runtime feature flags, CLI, runner, adapter, context, or trace wiring,
- current SMC, CRT, Order Flow, DecisionContext, confidence, action, risk,
  sizing, stop, target, entry, exit, balance, or PnL changes,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- tuning, optimization, favorable reruns, or use of saved OOS outcomes,
- private data, generated reports, external evidence, or Fibonacci analysis, and
- staging, committing, or pushing future implementation without separate gates.

Any forbidden dependency is a stop condition. It does not authorize a workaround
or implicit scope expansion.

## 22. Mandatory Pre-Implementation Gates

Before any later Python, test, or checkpoint edit:

1. independently audit this record,
2. checkpoint this documentation record separately from code,
3. confirm the record on local and live `main`,
4. confirm a clean worktree and matching `HEAD = origin/main`,
5. run and record the full regression baseline,
6. verify all reserved targets remain absent,
7. confirm inline fixtures remain sufficient or explicitly review the optional
   fixture path,
8. perform a read-only implementation preflight against the exact API,
   invariants, 36-case matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only that exact implementation task.

Passing this documentation decision is insufficient to begin coding.

## 23. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target collides unexpectedly,
- any additional path or package export appears necessary,
- the shared-primitives API requires amendment,
- the Equal Liquidity module appears to require modification or runtime import,
- a raw swing detector, raw structure detector, pandas input, or v1 adapter
  appears necessary,
- event provenance cannot identify a contiguous displacement sequence,
- protected-swing eligibility cannot remain strictly pre-displacement,
- exact Decimal midpoint behavior cannot be preserved,
- range replacement would require mislabeling `SUPERSEDED` as `INVALIDATED`,
- same-index invalidation-before-construction precedence cannot be preserved,
- deterministic identity or prefix invariance cannot be demonstrated,
- a private, candidate, performance, generated, or external fixture appears
  necessary,
- an existing public interface, default output, or execution path changes,
- focused tests or the full regression suite fail,
- unrelated staged, unstaged, ignored-generated, or untracked files appear, or
- integration appears necessary to test the standalone detector.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, or an implementation shortcut.

## 24. Completion, Rollback, and Promotion Gates

Later implementation completion requires:

- independent review of every changed line,
- exact reserved-path reconciliation,
- all 36 numbered logical test cases passing,
- the full regression suite passing,
- deterministic event, lineage, snapshot, and internal-range identity evidence,
- protected-swing timing, Decimal midpoint, lifecycle, and prefix-invariance
  evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed Dealing Range checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and clean-scope
audit. Existing v1, shared-primitives, and Equal Liquidity files remain intact.

Successful implementation would prove only standalone deterministic Dealing
Range conformance. It would not prove trading edge, OOS improvement, strategy
value, readiness, paper approval, live approval, or permission for phase four.

## 25. Global Freeze and Next-Phase Boundary

The global code freeze remains active. This decision reserves one possible
future Swing Hierarchy and Dealing Range task only. It does not authorize
Internal or External liquidity mapping, Premium or Discount, or any later phase.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 26. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=SWING_HIERARCHY_AND_DEALING_RANGE_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `OPERATIONAL_FREEZE_LIFT_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `TEST_OR_FIXTURE_CHANGE_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STRATEGY_OR_EXECUTION_CHANGE_AUTHORIZED=False`
- `PAPER_PROGRESSION_AUTHORIZED=False`
- `LIVE_PROGRESSION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`

The next permitted action is an independent final audit of this one
documentation record. No implementation action follows automatically.
