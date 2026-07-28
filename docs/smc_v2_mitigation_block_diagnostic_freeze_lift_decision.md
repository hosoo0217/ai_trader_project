# SMC v2 Mitigation Block Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision identifier: `SMC-V2-MITIGATION-BLOCK-FREEZE-LIFT-2026-07-28`.
- Record type: documentation-only formal bounded-freeze decision.
- Repository: `C:\Users\hosoo\Desktop\ai_trader_project`.
- Parent checkpoint commit: `d34e5125d0db396324fc734caff8b440c172e138`.
- Parent checkpoint subject: `feat(smc): add Order Block diagnostics`.
- Branch at decision preparation: `main`.
- Local `HEAD` and local `origin/main` matched the parent checkpoint.
- Worktree was clean before this record was created.
- Dependency order through standalone Order Block diagnostics is complete.
- Eighth bounded capability: Mitigation Block event.
- Current task changes this decision record only.
- No operational Python freeze lift is granted by this record.
- No implementation, integration, staging, commit, push, paper, or live authority
  is granted.
- Global code freeze remains active for every file.

The decision is to define one possible later standalone diagnostic implementation
without activating it. The future exception remains reserved and ineffective
until every documentation, preflight, implementation, test, audit, and promotion
gate below passes separately.

## 2. Effective-State Interpretation

The accepted version-1 Mitigation Block is not an independently discovered
candle, a second price zone, or a replacement Order Block. It is the first
qualifying midpoint-retest event of one canonical Order Block.

The source Order Block remains the sole owner of:

- direction,
- source candle,
- structural-event linkage,
- wick boundaries,
- body boundaries,
- proximal boundary,
- distal boundary,
- midpoint, and
- Order Block lifecycle.

The Mitigation Block event references that immutable source evidence. It never
creates, widens, narrows, moves, reverses, or relabels the source zone.

One source Order Block may produce at most one `MitigationBlock`. A proximal-only
touch or an upper-half partial penetration is not a Mitigation Block. The first
later observation that reaches or crosses the midpoint without the same-candle
adverse close-through is the only creation event.

After creation, the Mitigation Block event has only two states:

- `MITIGATED`
- `INVALIDATED`

There is no expiry, replacement, reactivation, second mitigation version, or
standalone candle selection in version 1.

## 3. Locked Decision Inputs and Dependency Evidence

This record depends directly on the accepted SMC v2 specification, freeze-lift
review, shared primitives, and completed standalone Order Block checkpoint.

The exact dependency evidence at decision preparation is:

- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`
- `docs/smc_v2_volume_profile_change_proposal_review.md`
  - SHA-256:
    `C94DDD8843DC849D1F3C141DAA8942F94C11F23CC189B99AFD7E45A4898762FA`
- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`
  - SHA-256:
    `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`
- `smc/smc_v2_primitives.py`
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`
- `docs/smc_v2_order_block_diagnostic_freeze_lift_decision.md`
  - SHA-256:
    `2E3608C1387C052004B97B45DFDC2EA363A51AB42425A916B894EFA8E4D60C69`
- `smc/order_block.py`
  - SHA-256:
    `C504A98DA82D154EEE03346A256159BA8854FF2FC56EC437E344781D8F0138C5`
- `tests/test_order_block.py`
  - SHA-256:
    `07749D3EDC3FCE85164DB011625336EA6ABE9D7FBFFFE746A52EE082D1280728`
- `docs/smc_v2_order_block_checkpoint.md`
  - SHA-256:
    `22C7A0D649D39F1C719BFA98B3E137F67A83560F9D65022BB058798260751DBA`

The accepted specification states that a Mitigation Block:

- references a valid Order Block,
- is not independently discovered,
- requires a later return,
- requires midpoint reach or cross,
- does not qualify on proximal-only contact,
- does not qualify when the same candle closes through the distal boundary, and
- preserves the original Order Block boundaries.

This record narrows those statements into executable deterministic contracts. It
does not alter the accepted upstream definitions.

## 4. Exact Change Authorized in This Documentation Task

This task authorizes creation of exactly:

- `docs/smc_v2_mitigation_block_diagnostic_freeze_lift_decision.md`

No other documentation file may change. No Python, test, fixture, configuration,
generated evidence, or integration file may change.

This task does not make the future implementation exception operational. The
record must first pass independent final audit and separate documentation
checkpoint gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later explicit human decision makes the bounded implementation exception
operational, the only reserved paths are:

- `smc/mitigation_block.py`
- `tests/test_mitigation_block.py`
- `docs/smc_v2_mitigation_block_checkpoint.md`

All three reserved paths were absent when this record was prepared.

No external fixture file is reserved. All future fixtures must be inline
synthetic test data inside `tests/test_mitigation_block.py`.

The reserved scope does not include:

- `smc/__init__.py`,
- `smc/smc_v2_primitives.py`,
- `smc/order_block.py`,
- any completed SMC v2 module,
- any legacy SMC module,
- any runner, configuration, trace, strategy, risk, or execution path, or
- any additional documentation file.

Need for a fourth path is a stop condition, not implicit authorization.

## 6. Exact Functional Boundary

The future standalone analyzer may:

- consume immutable canonical Order Block objects,
- validate complete canonical Order Block transition and snapshot histories,
- consume fully closed integer-tick observations,
- identify the first qualifying midpoint retest for each eligible source block,
- preserve the source block's original immutable geometry,
- record deepest penetration and close location on that first qualifying retest,
- record later source close-through invalidation,
- emit deterministic immutable objects, transitions, and snapshots,
- return fail-closed statuses and reasons, and
- remain completely offline and outcome-blind.

The analyzer may not:

- discover or reconstruct Order Blocks from candles,
- infer source candles, swings, BOS, CHOCH, or displacement,
- repair missing or malformed Order Block history,
- treat a proximal touch as mitigation,
- create multiple mitigation objects for one source block,
- mutate source geometry or Order Block history,
- create Breaker Blocks,
- aggregate context or confidence,
- emit trade direction, entries, exits, stops, targets, sizing, or PnL,
- read files, pandas objects, environment configuration, or external data, or
- integrate into any current analysis, decision, trace, strategy, risk, or
  execution path.

The output is diagnostic evidence only. Direction is mandatory source context,
not a BUY, SELL, reversal, or readiness signal.

The only allowed direct module dependencies for a later implementation are:

- Python standard-library modules required for frozen dataclasses, datetime,
  Decimal, enums, hashing, canonical JSON, and validation,
- `smc.smc_v2_primitives` for `SMCV2Direction`, `SMCV2PrimitiveStatus`,
  `SMCV2TickRange`, and UTC normalization, and
- `smc.order_block` for `OrderBlockState`, `OrderBlock`,
  `OrderBlockTransition`, `OrderBlockSnapshot`, and `make_order_block_id`.

Importing an analyzer from a completed diagnostic module, importing a legacy SMC
module, or adding a package export is forbidden.

## 7. Locked Input Contracts

### 7.1 Top-Level Contract

The analyzer accepts exactly:

- normalized instrument text,
- normalized timeframe text,
- `tuple[OrderBlock, ...] | None`,
- `tuple[OrderBlockTransition, ...] | None`,
- `tuple[OrderBlockSnapshot, ...] | None`, and
- `tuple[MitigationBlockObservation, ...] | None`.

Top-level `None` means the required context is missing and returns `UNKNOWN`
before present-input validation.

A present container must be a tuple. Lists, generators, sets, dictionaries,
pandas objects, and arbitrary iterables are invalid. The analyzer performs no
silent tuple conversion and no sorting.

Complete empty tuples are valid and return `NONE`.

If `order_blocks` is empty while either source-history tuple is nonempty, or if
any source-history object references a block absent from `order_blocks`, the
complete input is `INVALID`.

Instrument and timeframe are normalized exactly once with
`value.strip().upper()`. Empty normalized values are invalid.

### 7.2 Canonical Order Block Contract

Every supplied source object must be an exact frozen `OrderBlock` from
`smc.order_block`.

The analyzer validates only locally executable canonical evidence:

- every required field has the exact committed type,
- booleans are forbidden where integer ticks or indices are required,
- every timestamp is timezone-aware and normalizes to UTC,
- `block_id` is a lowercase 64-character SHA-256 string,
- direction is exactly `BULLISH` or `BEARISH`,
- wick and body ranges are ordered,
- body boundaries are inside wick boundaries,
- proximal and distal ticks reconcile with direction,
- midpoint is the exact Decimal integer or half tick of wick boundaries,
- source moment strictly precedes displacement start,
- displacement index and timestamp tuples have equal lengths from one to three,
- both displacement tuples are independently strictly increasing,
- detection moment equals the final displacement moment, and
- `make_order_block_id(identity_kind="BLOCK", ...)` reproduces `block_id`
  exactly from the supplied object's own fields.

The Mitigation analyzer does not require unavailable swing or structure-event
objects and does not semantically re-prove their existence. It trusts only the
canonical source IDs already sealed into the locally reproducible Order Block
identity.

Source blocks are supplied in strictly increasing canonical formation order:

1. detection index,
2. normalized detection timestamp,
3. source candle index,
4. direction value,
5. displacement-index tuple, and
6. block ID only after causal fields are equal.

Duplicate block IDs, duplicate complete objects, noncanonical order, or
contradictory objects with the same block ID are `INVALID`.

### 7.3 Complete Order Block Transition and Snapshot History

Every supplied `OrderBlockTransition` and `OrderBlockSnapshot` must be the exact
frozen upstream type.

For transitions:

- `block_id` must reference one supplied block,
- every field must satisfy the committed upstream type contract,
- `make_order_block_id(identity_kind="TRANSITION", ...)` must reproduce the
  transition ID,
- every transition edge and exact reason token must be valid under the committed
  Order Block lifecycle,
- effective moments must not precede source detection,
- the first transition is exactly `None -> DETECTED`,
- later transitions are monotonic,
- `INVALIDATED` is terminal,
- `FULLY_TRAVERSED` may only remain unchanged or later invalidate, and
- same-effective transitions follow upstream causal order rather than hash order.

For snapshots:

- `block_id` must reference one supplied block,
- every field must satisfy the committed upstream type contract,
- `make_order_block_id(identity_kind="SNAPSHOT", ...)` must reproduce the
  snapshot ID,
- each snapshot corresponds one-to-one with one transition,
- the final transition target state and moment equal snapshot state and moment,
- `transition_ids` are the exact ordered complete history prefix,
- every later snapshot extends the prior prefix by exactly one transition ID,
- no transition or snapshot is skipped, reordered, duplicated, or replaced, and
- the final snapshot for each block represents the complete supplied history
  through the final observation moment.

The transition tuple and snapshot tuple are separate evidence streams. Each tuple
independently uses nondecreasing effective moments. At an equal moment:

- causal transitions for one source block stay in upstream lifecycle order,
- the snapshot tuple exact-mirrors that transition causal order through each
  snapshot's final transition ID,
- independent source blocks use the canonical block order from Section 7.2 in
  both tuples, and
- direction, snapshot ID, transition ID, and hash lexical order never override
  causal order.

Every transition must have exactly one corresponding snapshot and every snapshot
must correspond to exactly one transition. Missing, extra, forked, or
contradictory source history is `INVALID`.

### 7.4 Fully Closed Integer-Tick Observation Contract

`MitigationBlockObservation` is frozen and contains exactly:

- `index: int`
- `timestamp: datetime`
- `high_tick: int`
- `low_tick: int`
- `close_tick: int`

Each observation must satisfy:

- index is a nonnegative integer and not a boolean,
- timestamp is timezone-aware and UTC-normalizable,
- high, low, and close are integers and not booleans,
- `low_tick <= high_tick`,
- `low_tick <= close_tick <= high_tick`, and
- the close is final; partial or live candles are forbidden.

Observation indices and normalized timestamps are independently strictly
increasing. Duplicate index, duplicate normalized timestamp, decreasing index,
decreasing timestamp, or non-tuple input is `INVALID`.

An observation is market evidence shared across all eligible source blocks. It
does not contain or imply a selected source block ID.

### 7.5 Effective Groups and Completeness Boundary

One observation index and normalized timestamp define one observation effective
group. The group also contains every source Order Block transition and snapshot
at that exact moment.

The caller must supply complete upstream source history for the observation
horizon. When observations are nonempty, the supplied observation horizon is
exactly the inclusive interval from the first observation composite moment
through the final observation composite moment. Exact reconciliation rules are:

- a source state change implied by a valid observation must have its canonical
  upstream transition and snapshot at that moment,
- every post-formation source transition inside the supplied observation horizon
  must reconcile with the observation that caused it,
- a qualifying mitigation creation must bind the source block's exact deepest
  same-moment transition and corresponding snapshot,
- a later mitigation invalidation must bind the exact source close-through
  transition and corresponding snapshot, and
- an in-horizon missing observation, transition, snapshot, excess source-history
  revision, or disagreement is `INVALID`.

Order Block formation and canonical post-formation history may predate the first
supplied observation. Pre-horizon source transitions are validated structurally
and causally but are not revalidated against observations the caller did not
supply.

If pre-horizon canonical history shows a transition to `MITIGATED` or
`FULLY_TRAVERSED` and the exact observation that first reached midpoint is absent,
the source's Mitigation creation fields cannot be reconstructed and the result is
`UNKNOWN`. A later observation must not be relabeled as the first qualifying
retest.

Pre-horizon `FIRST_ELIGIBLE_BAR`, `WICK_TOUCHED`, or `PARTIAL_MITIGATION`
history may establish the current eligible state without creating a Mitigation
event. A pre-horizon direct `CLOSE_THROUGH_INVALIDATION` that never passed through
`MITIGATED` or `FULLY_TRAVERSED` establishes an ineligible source and does not
require a missing Mitigation event.

Any post-formation source transition after the final supplied observation is
excess future source history for that supplied horizon and is `INVALID`.

When `observations=()`, there is no supplied observation horizon. After canonical
source-history validation, a source history that already reaches `MITIGATED` or
`FULLY_TRAVERSED` returns `UNKNOWN` because the required creation observation is
absent; canonical histories that never contain a qualifying midpoint/traversal
transition produce no Mitigation event and may return `NONE`.

## 8. Locked Source Eligibility and Canonical Linkage

One source Order Block is eligible for a first qualifying midpoint retest only
when its causal state immediately before the deepest same-observation source
transition is one of:

- `ACTIVE`
- `TOUCHED`
- `PARTIALLY_MITIGATED`

`DETECTED` becomes eligible only if the same effective group first contains the
canonical `DETECTED -> ACTIVE` transition. The later deepest transition in that
same group may then qualify.

These pre-observation states are ineligible for new mitigation creation:

- `MITIGATED`
- `FULLY_TRAVERSED`
- `INVALIDATED`

An already mitigated or traversed source never creates a second
`MitigationBlock`. An invalidated source never creates or reactivates one.

Creation requires exact same-group upstream evidence:

- the deepest source transition ends in `MITIGATED` or `FULLY_TRAVERSED`,
- its reason is respectively `MIDPOINT_MITIGATION` or `DISTAL_TRAVERSAL`,
- its effective moment equals the observation moment,
- its corresponding source snapshot exact-matches that state and moment, and
- its transition-history prefix is complete.

The immutable Mitigation object binds:

- the canonical source block ID,
- that deepest source transition ID, and
- its corresponding source snapshot ID.

The source transition and snapshot bindings are creation context. They never
change on the immutable Mitigation object even if the source later invalidates.

## 9. Locked First Qualifying Midpoint-Retest Semantics

The first qualifying midpoint retest is the earliest valid observation strictly
after the source block detection moment that:

1. is evaluated while the source has an eligible causal pre-state,
2. reaches or crosses the exact source midpoint,
3. does not close one tick or more through the distal boundary,
4. reconciles with the exact same-moment canonical source transition and
   snapshot, and
5. occurs before any prior qualifying midpoint retest for that source block.

For a bullish source:

- `low_tick <= midpoint_tick` means the midpoint is reached or crossed,
- `close_tick <= distal_tick - 1` is adverse close-through invalidation, and
- qualifying mitigation therefore requires
  `low_tick <= midpoint_tick` and `close_tick >= distal_tick`.

For a bearish source:

- `high_tick >= midpoint_tick` means the midpoint is reached or crossed,
- `close_tick >= distal_tick + 1` is adverse close-through invalidation, and
- qualifying mitigation therefore requires
  `high_tick >= midpoint_tick` and `close_tick <= distal_tick`.

Because source ticks are integers and midpoint is an exact Decimal integer or
half tick, comparisons are mathematical and must not use float conversion or
ambient Decimal rounding.

Midpoint equality qualifies. A direct move to or beyond the distal boundary also
qualifies when the close does not meet adverse close-through invalidation.

Formation candles cannot create mitigation. The observation must be strictly
later than source detection. The first eligible post-detection candle may create
mitigation after the causal `DETECTED -> ACTIVE` transition is processed.

## 10. Locked Proximal-Only and Partial-Penetration Non-Qualification

A source-zone return that does not reach the midpoint is not a Mitigation Block.

For a bullish source:

- exact proximal touch is `low_tick == proximal_tick`,
- partial penetration is `midpoint_tick < low_tick < proximal_tick`, and
- a candle remaining above proximal is outside the source zone.

For a bearish source:

- exact proximal touch is `high_tick == proximal_tick`,
- partial penetration is `proximal_tick < high_tick < midpoint_tick`, and
- a candle remaining below proximal is outside the source zone.

These observations may reconcile with upstream Order Block `TOUCHED` or
`PARTIALLY_MITIGATED` transitions, but emit no Mitigation object.

An earlier proximal-only or partial return does not permanently disqualify the
source. A strictly later first midpoint-reaching observation may still create the
one Mitigation event while the source remains eligible.

No hidden "first touch only" rule exists. The locked event is first qualifying
midpoint retest, not first contact with any part of the zone.

## 11. Locked Boundaries, Penetration, Close, and Direction Semantics

The Mitigation object copies and preserves exactly:

- `wick_low_tick`,
- `wick_high_tick`,
- `body_low_tick`,
- `body_high_tick`,
- `proximal_tick`,
- `distal_tick`, and
- `midpoint_tick`

from the canonical source Order Block.

For a bullish source:

- proximal is wick high,
- distal is wick low,
- deepest penetration is the qualifying observation `low_tick`.

For a bearish source:

- proximal is wick low,
- distal is wick high,
- deepest penetration is the qualifying observation `high_tick`.

`close_tick` is the exact qualifying observation close. `midpoint_reached` is
always exactly `True` for an emitted Mitigation object. Supplying or constructing
a Mitigation identity with `midpoint_reached=False` is invalid.

The midpoint is the source Order Block's already canonical Decimal integer or
half tick. The Mitigation analyzer does not recalculate it using floats and must
exact-match it against the source wick boundaries.

Direction must be exactly the source Order Block direction. Bullish and bearish
rules are exact mirrors. Direction remains descriptive context only and may not
be converted into a signal.

No later observation may change the immutable creation:

- boundaries,
- midpoint,
- first-retouch moment,
- deepest penetration,
- close location,
- source IDs, or
- direction.

## 12. Locked Lifecycle, Invalidation, and Same-Index Precedence

`MitigationBlockState` contains exactly:

- `MITIGATED`
- `INVALIDATED`

Creation emits:

- `from_state=None`,
- `to_state=MITIGATED`, and
- reason `FIRST_QUALIFYING_MIDPOINT_RETEST`.

The only later state change is:

- `from_state=MITIGATED`,
- `to_state=INVALIDATED`, and
- reason `SOURCE_CLOSE_THROUGH_INVALIDATION`.

Later invalidation requires:

- a strictly later observation,
- bullish `close_tick <= distal_tick - 1` or bearish
  `close_tick >= distal_tick + 1`,
- the canonical same-moment source Order Block transition to `INVALIDATED`,
- reason `CLOSE_THROUGH_INVALIDATION`, and
- the corresponding complete source Order Block snapshot.

If the first midpoint-reaching observation also closes through the distal
boundary, invalidation has precedence and no Mitigation object, transition, or
snapshot is created for that source. The source Order Block invalidation remains
upstream evidence; this module does not reinterpret it as mitigation.

If an already emitted Mitigation object later receives a close-through
observation, exactly one `MITIGATED -> INVALIDATED` transition and one snapshot
are appended.

`INVALIDATED` is terminal. There is no:

- expiry,
- reactivation,
- replacement,
- regression,
- repeated invalidation,
- new deepest-penetration revision,
- second mitigation event, or
- boundary mutation.

Wick traversal without adverse close-through cannot invalidate the Mitigation
event. End of input preserves the latest state.

## 13. Locked Public API

The proposed public surface is limited to:

- `MITIGATION_BLOCK_DETECTOR_VERSION`
- `MitigationBlockState`
- `MitigationBlockObservation`
- `MitigationBlock`
- `MitigationBlockTransition`
- `MitigationBlockSnapshot`
- `MitigationBlockResult`
- `make_mitigation_block_id`
- `analyze_mitigation_blocks`

The exact keyword-only analyzer signature is:

```python
def analyze_mitigation_blocks(
    *,
    instrument: str,
    timeframe: str,
    order_blocks: tuple[OrderBlock, ...] | None,
    order_block_transitions: tuple[OrderBlockTransition, ...] | None,
    order_block_snapshots: tuple[OrderBlockSnapshot, ...] | None,
    observations: tuple[MitigationBlockObservation, ...] | None,
) -> MitigationBlockResult:
    ...
```

The exact keyword-only identity-builder signature is:

```python
def make_mitigation_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_order_block_id: str | None = None,
    source_order_block_snapshot_id: str | None = None,
    source_order_block_transition_id: str | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    first_retouch_index: int | None = None,
    first_retouch_timestamp: datetime | None = None,
    deepest_penetration_tick: int | None = None,
    close_tick: int | None = None,
    midpoint_reached: bool | None = None,
    mitigation_id: str | None = None,
    from_state: MitigationBlockState | None = None,
    to_state: MitigationBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: MitigationBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    ...
```

No configuration object exists in version 1. Source eligibility, midpoint,
direction, invalidation, no-expiry, identity, chronology, and status rules are
fixed semantics.

`MitigationBlockObservation` is frozen and contains exactly the five fields in
Section 7.4.

`MitigationBlock` is frozen and contains exactly:

- `mitigation_id: str`
- `direction: SMCV2Direction`
- `source_order_block_id: str`
- `source_order_block_snapshot_id: str`
- `source_order_block_transition_id: str`
- `wick_low_tick: int`
- `wick_high_tick: int`
- `body_low_tick: int`
- `body_high_tick: int`
- `proximal_tick: int`
- `distal_tick: int`
- `midpoint_tick: Decimal`
- `first_retouch_index: int`
- `first_retouch_timestamp: datetime`
- `deepest_penetration_tick: int`
- `close_tick: int`
- `midpoint_reached: bool`

`MitigationBlockTransition` is frozen and contains exactly:

- `transition_id: str`
- `mitigation_id: str`
- `source_order_block_id: str`
- `source_order_block_snapshot_id: str`
- `source_order_block_transition_id: str`
- `from_state: MitigationBlockState | None`
- `to_state: MitigationBlockState`
- `index: int`
- `timestamp: datetime`
- `reason: str`

`MitigationBlockSnapshot` is frozen and contains exactly:

- `snapshot_id: str`
- `mitigation_id: str`
- `source_order_block_id: str`
- `source_order_block_snapshot_id: str`
- `source_order_block_transition_id: str`
- `direction: SMCV2Direction`
- `state: MitigationBlockState`
- `index: int`
- `timestamp: datetime`
- `transition_ids: tuple[str, ...]`

`MitigationBlockResult` is frozen and contains exactly:

- `status: SMCV2PrimitiveStatus`
- `mitigations: tuple[MitigationBlock, ...] = ()`
- `transitions: tuple[MitigationBlockTransition, ...] = ()`
- `snapshots: tuple[MitigationBlockSnapshot, ...] = ()`
- `reasons: tuple[str, ...] = ()`
- `blocking_reasons: tuple[str, ...] = ()`

Both functions normalize instrument and timeframe exactly once as
`value.strip().upper()`. Positional calls, extra parameters, silent coercion,
file loading, pandas conversion, hidden globals, and environment configuration
are forbidden.

## 14. Locked Deterministic Identity Contract

`MITIGATION_BLOCK_DETECTOR_VERSION` is exactly:

- `SMC-V2-MITIGATION-BLOCK-1`

The only identity kinds are:

- `MITIGATION`
- `TRANSITION`
- `SNAPSHOT`

Every identity includes:

- detector version,
- exact identity kind,
- normalized instrument,
- normalized timeframe, and
- exact direction.

Canonical payloads use:

- sorted-key compact ASCII JSON,
- UTC timestamps serialized as `YYYY-MM-DDTHH:MM:SS.ffffffZ`,
- enum `.value` strings,
- integer ticks,
- exact Decimal midpoint `.0` or `.5` text with every signed zero canonicalized
  as `0.0`,
- ordered tuples, and
- lowercase SHA-256 output.

No float, Python object representation, locale, insertion order, set order,
process ID, wall clock, random seed, or ambient Decimal context may affect an
identity.

### 14.1 `MITIGATION`

`MITIGATION` requires exactly:

- direction,
- source Order Block ID,
- creation source Order Block snapshot ID,
- creation source Order Block transition ID,
- wick boundaries,
- body boundaries,
- proximal tick,
- distal tick,
- midpoint tick,
- first-retouch index,
- normalized first-retouch timestamp,
- deepest-penetration tick,
- close tick, and
- `midpoint_reached=True`.

The builder validates:

- all three source IDs are lowercase SHA-256 strings,
- body is inside wick,
- proximal and distal reconcile with direction,
- midpoint exactly reconciles with wick boundaries,
- deepest penetration and close are integer ticks and not booleans,
- deepest penetration reaches or crosses midpoint in the correct direction,
- bullish direction requires `close_tick >= deepest_penetration_tick`,
- bearish direction requires `close_tick <= deepest_penetration_tick`,
- close does not meet adverse one-tick close-through invalidation, and
- first-retouch moment is valid.

`MITIGATION` forbids:

- `mitigation_id`,
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
- source Order Block ID,
- current source Order Block snapshot ID,
- current source Order Block transition ID,
- mitigation ID,
- from state, including `None` only for creation,
- to state,
- effective index,
- normalized effective timestamp, and
- one exact lifecycle reason.

Allowed edges and reasons are exactly:

- `None -> MITIGATED`
  - `FIRST_QUALIFYING_MIDPOINT_RETEST`
- `MITIGATED -> INVALIDATED`
  - `SOURCE_CLOSE_THROUGH_INVALIDATION`

Every other edge, repeated state, wrong reason, `None -> INVALIDATED`, or
transition out of `INVALIDATED` is invalid.

`TRANSITION` forbids:

- wick boundaries,
- body boundaries,
- proximal tick,
- distal tick,
- midpoint tick,
- first-retouch fields,
- deepest-penetration tick,
- close tick,
- `midpoint_reached`,
- `state`, and
- non-empty `transition_ids`.

### 14.3 `SNAPSHOT`

`SNAPSHOT` requires exactly:

- direction,
- source Order Block ID,
- current source Order Block snapshot ID,
- current source Order Block transition ID,
- mitigation ID,
- current state,
- effective index,
- normalized effective timestamp, and
- a non-empty ordered transition-ID tuple.

The analyzer must:

- recompute and exact-match every Mitigation transition ID,
- require the final transition target state and moment to equal snapshot state
  and moment,
- require source IDs to equal the final linked transition's source IDs, and
- require `transition_ids` to be the complete immutable Mitigation history.

`SNAPSHOT` forbids:

- wick boundaries,
- body boundaries,
- proximal tick,
- distal tick,
- midpoint tick,
- first-retouch fields,
- deepest-penetration tick,
- close tick,
- `midpoint_reached`,
- `from_state`,
- `to_state`, and
- `reason`.

For all three kinds, every public builder parameter is either exact required
data or exact forbidden default data. Missing required values, forbidden
non-default values, malformed hashes, invalid enums, boundary or midpoint
mismatch, impossible lifecycle edges, wrong reason tokens, and unknown identity
kinds raise only `TypeError` or `ValueError`.

## 15. Locked Immutable Lifecycle and Snapshot Contract

One immutable `MitigationBlock` is emitted exactly once per source Order Block.
It is never revised.

Creation emits exactly:

- one `MitigationBlock`,
- one `None -> MITIGATED` transition, and
- one `MITIGATED` snapshot.

Later source close-through emits exactly:

- no new Mitigation object,
- one `MITIGATED -> INVALIDATED` transition, and
- one `INVALIDATED` snapshot.

Transition history is append-only:

- creation snapshot contains only the creation transition ID,
- invalidated snapshot contains creation then invalidation transition IDs,
- no snapshot may skip, reorder, duplicate, replace, or remove a transition,
- no object or snapshot is rewritten, and
- `INVALIDATED` is terminal.

Creation-source snapshot and transition IDs remain on the immutable
`MitigationBlock`. A later transition and snapshot carry the later current
source Order Block snapshot and transition IDs that prove invalidation.

Different source Order Blocks are evaluated independently. Multiple source
blocks may produce mitigation events from one market observation. Deterministic
independent output order is:

1. earlier source Order Block detection index,
2. earlier normalized detection timestamp,
3. earlier source candle index,
4. direction value,
5. displacement-index tuple,
6. source Order Block ID, and
7. mitigation ID only after causal source fields are equal.

Identity hash order never moves later market evidence ahead of earlier evidence.

## 16. Locked Chronology and Same-Index Processing Precedence

All complete caller-supplied tuples are validated without sorting.

For each observation effective group, processing order is exactly:

1. validate the observation and independent observation chronology,
2. collect every source Order Block transition and snapshot at that moment,
3. validate the complete source-history group and causal order,
4. clone the strictly prior immutable Mitigation analysis state,
5. evaluate close-through invalidation for every existing nonterminal Mitigation
   object,
6. append valid later invalidation transitions and snapshots in canonical source
   order,
7. evaluate source blocks without an existing Mitigation object,
8. derive each source's causal pre-observation state,
9. apply source eligibility,
10. apply same-candle close-through invalidation precedence,
11. apply midpoint-reach qualification and source-history reconciliation,
12. append each deterministic immutable Mitigation object,
13. append its creation transition and snapshot, and
14. promote the group only after every source and object succeeds.

Consequences:

- existing Mitigation invalidation is evaluated before new creation,
- a first retest that closes through never creates mitigation,
- an earlier proximal-only touch may be followed by later valid creation,
- multiple independent source blocks may create deterministic separate events,
- exact duplicate candidate evidence is invalid,
- no hash or price tie-break chooses among contradictory source histories, and
- any group-level error promotes nothing from that group or after it.

Strictly prior promoted evidence remains immutable when the failing effective
moment is determinable. If malformed required fields prevent a safe effective
moment, no trustworthy prefix is claimed.

## 17. Locked Result Status Semantics

`SMCV2PrimitiveStatus` is used exactly:

- `UNKNOWN`
  - any top-level required tuple is `None`,
  - observation coverage begins too late to establish the first qualifying
    midpoint retest for a supplied source, or
  - required context is absent but not malformed.
- `NONE`
  - complete empty inputs,
  - complete canonical sources with no qualifying midpoint retest,
  - only outside-zone, proximal-only, or partial-penetration observations,
  - first midpoint reach is overridden by same-candle source invalidation and no
    other Mitigation object exists, or
  - no emitted Mitigation object after all valid groups.
- `VALID`
  - at least one deterministic Mitigation object is emitted and no later group
    fails.
- `AMBIGUOUS`
  - remains part of the shared `SMCV2PrimitiveStatus` vocabulary, but the
    version-1 Mitigation analyzer has no reachable valid emission branch for it.
- `INVALID`
  - malformed present input,
  - invalid or noncanonical source Order Block identity,
  - incomplete, forked, missing, extra, or noncanonical source lifecycle
    history,
  - invalid observation ticks or chronology,
  - duplicate source or observation evidence,
  - source direction, geometry, transition, snapshot, observation, midpoint, or
    close-through mismatch,
  - forbidden builder fields,
  - impossible Mitigation lifecycle,
  - exception leakage from malformed nested input, or
  - any other contract violation.

Top-level `UNKNOWN` is evaluated before validation of present inputs.

Shared status precedence remains:

1. `INVALID`
2. `AMBIGUOUS`
3. incomplete-history `UNKNOWN`
4. `VALID`
5. `NONE`

The reachable version-1 analyzer precedence is therefore `INVALID`, then
incomplete-history `UNKNOWN`, then `VALID`, then `NONE`.

Same-source duplicate, forked, or contradictory candidate evidence is an
input-integrity failure and therefore `INVALID`, not `AMBIGUOUS`. Multiple
independent source blocks qualifying at one observation are deterministic
multiple outputs and therefore not ambiguous. The implementation must not invent
an `AMBIGUOUS` path, discard an independent source, or select a winner to make
this shared vocabulary value reachable.

If a later problem has a determinable effective moment, valid objects,
transitions, and snapshots strictly before that group remain immutable evidence
in the fail-closed result. Nothing from the failing group or after it is
promoted.

## 18. Locked Prefix-Invariance Contract

A prefix is eligible for comparison only when it ends after one complete
observation effective group, including:

- all source Order Block transitions at that moment,
- all corresponding source snapshots,
- all existing Mitigation lifecycle evaluations, and
- all new Mitigation creation evaluations.

Every appended observation and source-history group must have an effective
moment strictly later than the prefix boundary. Adding an earlier observation,
adding historical source evidence, or appending a partial same-effective group
is not an eligible prefix extension.

For every valid complete-group prefix, strictly later evidence must preserve
every prior:

- Mitigation object and ID,
- source Order Block linkage,
- direction,
- wick and body boundaries,
- proximal and distal ticks,
- midpoint,
- first-retouch moment,
- deepest penetration,
- close location,
- transition and transition ID,
- snapshot and snapshot ID,
- lifecycle state, and
- tuple order

byte-for-byte.

Later evidence may append one invalidation transition and snapshot to an existing
Mitigation object. It may not rewrite creation, attach a new source snapshot to
the immutable object, change penetration, insert earlier evidence, create a
second event for one source, or expire an event.

Repeated analysis of identical immutable inputs must produce dataclass-equal
results and byte-identical canonical identity payloads.

## 19. Locked Inline Synthetic 40-Case Unit-Test Matrix

All future fixtures are inline, synthetic, integer-tick, timezone-aware,
outcome-blind, and independent of saved project reports or market data.

The exact logical matrix is:

1. Any one top-level source/history/observation tuple set to `None` returns
   `UNKNOWN`; no partial object is emitted and normalized empty instrument or
   timeframe is `INVALID`.
2. Four complete empty tuples return `NONE` with empty immutable output tuples.
3. Instrument/timeframe strip-uppercase normalization and equivalent UTC
   timestamps produce deterministic equal identities; naive timestamps fail
   closed.
4. Canonical bullish and bearish Order Block objects reproduce through
   `make_order_block_id`; malformed hash, boolean tick/index, invalid direction,
   boundary, midpoint, displacement, or detection data returns `INVALID` without
   exception leakage.
5. Source blocks are accepted only in exact canonical formation order; duplicate
   IDs, duplicate objects, contradictory same-ID objects, and silent-sort input
   return `INVALID`.
6. Canonical source formation transition and snapshot histories exact-match
   their public identities and complete prefix chains.
7. Missing, extra, skipped, reordered, duplicated, forked, wrong-reason, or
   impossible in-horizon source transition/snapshot history returns `INVALID`;
   a canonical pre-horizon midpoint/traversal transition whose exact observation
   is unavailable, including an empty observation tuple, returns `UNKNOWN` and
   cannot relabel a later retest.
8. The separate transition and snapshot tuples each use nondecreasing moments;
   at equal moments snapshot order exact-mirrors transition causal order through
   final transition IDs, independent blocks use canonical source order, one-to-one
   correspondence is enforced, and decreasing hashes do not invalidate evidence.
9. Observation required fields, frozen state, integer/non-boolean ticks,
   timezone awareness, and `low <= close <= high` are enforced.
10. Observation tuple must be exact tuple with independently strictly increasing
    indices and timestamps; list input, duplicate index, duplicate normalized
    timestamp, and either decreasing dimension return `INVALID`.
11. A bullish source whose causal pre-state is `ACTIVE` and whose low first
    reaches midpoint with a noninvalidating close emits one Mitigation object.
12. The bearish mirror whose high first reaches midpoint with a noninvalidating
    close emits one Mitigation object.
13. `TOUCHED` and `PARTIALLY_MITIGATED` pre-states remain eligible in both
    directions; `MITIGATED`, `FULLY_TRAVERSED`, and `INVALIDATED` do not create a
    new object.
14. A same-effective `DETECTED -> ACTIVE` transition precedes the qualifying
    deeper source transition and allows first-eligible-candle mitigation; a
    detection-moment observation cannot mitigate its own source.
15. Source transition to `MITIGATED` with `MIDPOINT_MITIGATION` and direct source
    transition to `FULLY_TRAVERSED` with `DISTAL_TRAVERSAL` both qualify when the
    observation reconciles and does not close through.
16. Bullish and bearish exact midpoint equality qualifies, including integer and
    half-tick midpoint cases without float conversion.
17. Arbitrary-magnitude positive and negative ticks preserve exact Decimal
    integer/half-tick comparisons independent of ambient Decimal precision.
18. Bullish deepest penetration equals observation low and requires
    `close_tick >= deepest_penetration_tick`; bearish deepest penetration equals
    observation high and requires `close_tick <= deepest_penetration_tick`.
    Impossible depth/close geometry fails from the public identity builder with
    only `TypeError` or `ValueError`; valid close location is stored exactly.
19. Exact proximal touch produces no Mitigation object and reconciles only with
    the appropriate source touch behavior.
20. Strict proximal-to-midpoint partial penetration produces no Mitigation
    object; a strictly later first midpoint-reaching observation may qualify.
21. Observation remaining outside the source zone produces no event and no
    source lifecycle mutation.
22. An in-horizon observation that geometrically reaches midpoint but lacks the
    exact canonical same-moment source transition/snapshot is `INVALID`; an
    in-horizon supplied transition without its reconciling observation is also
    `INVALID`, while only the locked pre-horizon missing-creation boundary is
    `UNKNOWN`.
23. A qualifying creation exact-matches source block, deepest source transition,
    and corresponding source snapshot IDs; wrong source linkage is `INVALID`.
24. Bullish first midpoint reach with `close <= distal - 1` and bearish mirror
    with `close >= distal + 1` are overridden by source invalidation and create no
    Mitigation object.
25. Bullish close exactly at distal and bearish close exactly at distal do not
    meet one-tick close-through and may qualify when midpoint is reached.
26. Wick movement beyond distal without adverse close-through may qualify by the
    source's deepest `FULLY_TRAVERSED` transition and does not create an
    `INVALIDATED` Mitigation state.
27. Emitted Mitigation fields exactly preserve source wick/body/proximal/distal
    boundaries, midpoint, direction, creation source IDs, first-retouch moment,
    deepest penetration, close, and `midpoint_reached=True`.
28. Creation emits exactly `None -> MITIGATED` with reason
    `FIRST_QUALIFYING_MIDPOINT_RETEST` and one exact complete-history snapshot.
29. A strictly later bullish/bearish source close-through emits exactly
    `MITIGATED -> INVALIDATED` with reason
    `SOURCE_CLOSE_THROUGH_INVALIDATION` and exact current source IDs.
30. Existing Mitigation invalidation is processed before new same-observation
    creations; the complete group uses canonical independent source order.
31. `INVALIDATED` is terminal; no expiry, reactivation, replacement, repeated
    invalidation, state regression, penetration revision, or second source event
    occurs.
32. One observation may deterministically create or invalidate multiple
    independent source events; hash and dictionary order do not alter output.
33. A determinably later malformed or missing in-horizon observation or
    source-history group returns `INVALID`, preserves strictly prior immutable
    evidence, and promotes nothing from the failing group or after it;
    pre-horizon missing creation observation returns `UNKNOWN`, and unknowable
    effective moment claims no trustworthy prefix.
34. Shared precedence remains `INVALID` over `AMBIGUOUS` over incomplete-history
    `UNKNOWN` over `VALID` over `NONE`, but `AMBIGUOUS` has no reachable valid
    version-1 branch: same-source duplicate/forked evidence is `INVALID`, while
    independent multi-source evidence is deterministic and must not be collapsed
    into a fabricated ambiguity.
35. `MITIGATION` identity exhaustively enforces every required/forbidden field,
    direction/source/boundary/midpoint/retouch/depth/close sensitivity,
    direction-specific depth/close envelope reconciliation, impossible-pair
    `TypeError`/`ValueError` containment, instrument/timeframe normalization,
    signed-zero canonicalization, equivalent UTC determinism, and malformed
    nested-input containment.
36. `TRANSITION` identity exhaustively enforces every required/forbidden field,
    both allowed edges, all impossible edges, exact reason tokens, source-link
    sensitivity, effective-moment sensitivity, and malformed-hash rejection.
37. `SNAPSHOT` identity exhaustively enforces every required/forbidden field,
    nonempty ordered unique complete transition history, final state/moment/source
    reconciliation, history-order sensitivity, and malformed-hash rejection.
38. Public builder and analyzer expose exact keyword-only names/defaults; every
    public dataclass has exact fields and frozen state; enums, version, exports,
    and unknown identity-kind rejection are exact.
39. Repeated input is deterministic; complete-group prefix invariance holds for
    strictly later appends; partial/same-effective or historical appends are
    ineligible comparisons and cannot silently reorder evidence.
40. The standalone module has no file I/O, pandas, external fixture, raw-candle
    detector, legacy SMC, Breaker, context, strategy, risk, execution, config,
    registration, network, or integration dependency, and focused plus full
    regression suites pass.

The matrix contains exactly `40` numbered logical cases. Parameterization may
expand physical test count but may not rename, omit, merge away, or add logical
case numbers without a separately reviewed documentation change.

## 20. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/order_block.py`, `smc/__init__.py`,
  or any completed SMC v2 module,
- imports from or edits to legacy `smc/market_structure.py`,
  `smc/bos_choch.py`, `smc/liquidity_sweep.py`, or current SMC context,
- raw candle, CSV, pandas, adapter, replay, or external-data ingestion,
- Order Block reconstruction, source swing reconstruction, BOS/CHOCH
  reconstruction, or source-history repair,
- Breaker Block, Inducement, kill-zone, Volume Profile, context aggregation,
  confidence, signal, or filter code,
- runtime flag, CLI, runner, trace, package-registration, decision-path, or
  execution wiring,
- current SMC, CRT, Order Flow, DecisionContext, action, risk, sizing, stop,
  target, entry, exit, balance, or PnL changes,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- tuning, optimization, favorable reruns, or saved OOS outcome use,
- private data, generated reports, external evidence, Fibonacci analysis, or
  external fixtures, and
- staging, committing, or pushing future implementation without separate gates.

Any forbidden dependency is a stop condition. It does not authorize a workaround
or implicit scope expansion.

## 21. Mandatory Pre-Implementation Gates

Before any later Python, test, or checkpoint edit:

1. independently audit this decision record,
2. correct and re-audit any semantic or structural finding,
3. checkpoint this documentation record separately from code,
4. confirm the record on local and live `main`,
5. confirm a clean worktree and matching `HEAD = origin/main`,
6. run and record the full regression baseline,
7. verify all three reserved implementation targets remain absent,
8. verify every locked dependency file and hash remains unchanged,
9. perform a read-only implementation preflight against the exact API,
   invariants, 40-case matrix, rollback, and stop conditions here, and
10. obtain explicit human authorization for only the exact three-path task.

Passing or committing this record is insufficient to begin implementation.

## 22. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target already exists,
- any parent commit or dependency hash differs without separate review,
- another tracked, staged, unstaged, ignored-generated, or untracked file
  appears,
- another path or external fixture appears necessary,
- a completed dependency or public interface appears to require change,
- Order Blocks would need to be rediscovered or reconstructed,
- missing source histories would need inference, repair, or silent completion,
- source geometry, direction, or upstream lifecycle would need mutation,
- fully closed immutable integer-tick observations cannot remain the only new
  price input,
- first qualifying midpoint retest or proximal-only exclusion becomes ambiguous,
- bullish/bearish mirror semantics or exact midpoint comparison require float or
  Decimal-context dependence,
- same-index close-through invalidation precedence cannot be preserved,
- one source could produce multiple Mitigation objects,
- no-expiry, terminal invalidation, immutable history, or prefix invariance
  cannot be demonstrated,
- multiple same-source candidates require hash, price, or insertion order to
  choose a winner,
- identity reconciliation or exhaustive required/forbidden schemas cannot be
  demonstrated,
- malformed required fields leak exceptions outside `TypeError` or `ValueError`
  in the public builder or outside fail-closed result statuses in the analyzer,
- private, candidate, performance, generated, or external evidence is needed,
- runtime, strategy, risk, config, registration, execution, or integration is
  needed,
- focused tests or the full regression suite fail, or
- implementation appears necessary to resolve an ambiguity in this record.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, rounding, tuning, or implementation shortcuts.

## 23. Completion, Rollback, Promotion, and Global-Freeze Gates

Later implementation completion requires:

- independent review of every changed line,
- exact three-path reconciliation,
- all 40 numbered logical test cases passing,
- the full regression suite passing,
- deterministic Mitigation, transition, and snapshot identity evidence,
- exact source-history, eligibility, midpoint, proximal-only, boundary,
  penetration, close, direction, lifecycle, invalidation, atomic-group,
  fail-closed, and prefix-invariance evidence,
- proof that no current production import or execution path changed,
- confirmation that no sensitive, generated, or external evidence was added,
- a completed Mitigation Block checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created implementation task
paths and requires explicit instruction before destructive removal. After commit,
rollback must use a bounded revert of the task commit rather than history
rewriting. Any rollback requires focused tests, full regression, and clean-scope
audit. Existing source and completed dependencies remain intact.

Successful implementation would prove only standalone deterministic Mitigation
Block event conformance. It would not prove trading edge, OOS improvement,
strategy value, readiness, threshold approval, paper approval, live approval, or
permission for Breaker Block or any later phase.

The global code freeze remains active. This record reserves one possible future
Mitigation Block task only. It does not authorize Breaker Block, Inducement, kill
zones, Volume Profile, context aggregation, trace integration, decision
integration, or execution integration.

No later module inherits authorization from this record. Every later phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=MITIGATION_BLOCK_EVENT_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `SOURCE_ORDER_BLOCK_MUTATION_AUTHORIZED=False`
- `RESERVED_IMPLEMENTATION_PATHS=3`
- `INLINE_SYNTHETIC_TEST_CASES=40`
- `OPERATIONAL_FREEZE_LIFT_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
