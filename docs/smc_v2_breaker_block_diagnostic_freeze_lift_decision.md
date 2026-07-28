# SMC v2 Breaker Block Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-BREAKER-BLOCK-FREEZE-LIFT-2026-07-28`.
- Decision type: documentation-only bounded diagnostic freeze-lift record.
- Ninth bounded capability: Breaker Block.
- Repository baseline: `5e76de341d8ce1b96442b1818e0ff481723da414`.
- Baseline branch: `main`.
- Local `HEAD`, local `origin/main`, and live remote `main` matched at review time.
- Worktree at decision start: clean.
- Existing global code freeze: active.
- Paper-trading approval: none.
- Live-trading approval: none.
- Runtime or strategy integration approval: none.

This record defines one future standalone diagnostic capability. It does not
authorize Python implementation, tests, fixtures, staging, commit, push,
integration, configuration, tuning, signal use, paper use, or live use.

The accepted implementation order places Breaker Block after Shared Primitives,
Dealing Range, Order Block, and Mitigation Block. Completion of those
dependencies removes the ordering blocker only. It does not transfer their
freeze-lift authority to this task.

## 2. Effective-State Interpretation

A Breaker Block is not a standalone candle pattern and is not a second attempt
to detect an Order Block. It is a deterministic role reversal of one already
canonical Order Block.

The source Order Block must first become `INVALIDATED` through its exact locked
one-tick adverse close-through rule. That invalidation establishes the proposed
Breaker direction:

- failed bearish Order Block -> bullish Breaker;
- failed bullish Order Block -> bearish Breaker.

The invalidation alone does not create a Breaker. A canonical BOS or CHOCH in
the proposed Breaker direction must confirm on the invalidation close or on one
of the next ten fully closed observations. The original wick-inclusive and body
boundaries are retained without mutation. Proximal and distal roles are
recomputed from the new direction.

The Breaker becomes `ACTIVE` at the structure-confirmation close. Its formation
observation cannot retest, touch, mitigate, or invalidate the Breaker it creates.
Retest eligibility begins with the first strictly later closed observation.

This is historical diagnostic evidence only. It has no confidence weight,
signal direction, entry instruction, stop placement, target placement, sizing,
filter, execution, or readiness meaning.

## 3. Locked Decision Inputs and Dependency Evidence

The decision is grounded in the accepted planning package:

- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`;
  - Breaker Block is dependency-order capability 9;
  - the accepted role-reversal sequence is the source Order Block invalidation,
    same-direction BOS or CHOCH confirmation within the locked window, original
    zone reuse, and next-bar retest eligibility.
- `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256:
    `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`;
  - Breaker Block is an isolated future module;
  - it must retain the source Order Block identity and must not become a
    standalone zone detector.
- `docs/smc_v2_volume_profile_change_proposal_review.md`
  - SHA-256:
    `C94DDD8843DC849D1F3C141DAA8942F94C11F23CC189B99AFD7E45A4898762FA`;
  - the role-reversed invalidated Order Block with structural confirmation is an
    accepted technical decision.

The required implementation dependencies are present and committed:

- `smc/smc_v2_primitives.py`
  - commit: `b6ff9f940ebe0b088164482e9623bb3ef73ded4b`;
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`.
- `smc/dealing_range.py`
  - commit: `a20a6ad7c315d44e99358ffe1f18a90b5a18071b`;
  - SHA-256:
    `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`.
- `smc/order_block.py`
  - commit: `d34e5125d0db396324fc734caff8b440c172e138`;
  - SHA-256:
    `C504A98DA82D154EEE03346A256159BA8854FF2FC56EC437E344781D8F0138C5`.
- `smc/mitigation_block.py`
  - commit: `5e76de341d8ce1b96442b1818e0ff481723da414`;
  - SHA-256:
    `3200FC79CBFAE81C7EC23B955CCCA9248C1B0CF556CCCDC0023A61753988F2CC`.

The Mitigation Block completion is an implementation-order gate. Breaker Block
does not consume Mitigation Block objects and must not infer Breaker state from
Mitigation output.

The post-push audit reran:

- focused Mitigation Block tests: `48 passed`;
- full regression: `1370 passed`;
- production imports of `smc.mitigation_block`: `0`;
- integration changes: none.

No performance, OOS, PnL, entry, exit, target-hit, generated-report, private,
broker, account, or external evidence was used to select these rules.

## 4. Exact Change Authorized in This Documentation Task

The only authorized change in this documentation task is creation of:

- `docs/smc_v2_breaker_block_diagnostic_freeze_lift_decision.md`

No existing file may be edited. This task does not authorize creation of the
reserved implementation files.

The decision file must be independently audited before any staging
authorization. Staging, commit, and push require separate explicit gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If and only if this decision record completes every documentation promotion gate
and a later post-push readiness audit passes, one possible bounded
implementation task may reserve exactly:

- `smc/breaker_block.py`
- `tests/test_breaker_block.py`
- `docs/smc_v2_breaker_block_checkpoint.md`

These targets were absent at decision time. A future target collision is a stop
condition, not overwrite authorization.

No external fixture is reserved. All future fixtures must be inline and
synthetic in `tests/test_breaker_block.py`.

The future exception may not include:

- `smc/smc_v2_primitives.py`;
- `smc/dealing_range.py`;
- `smc/order_block.py`;
- `smc/mitigation_block.py`;
- `smc/__init__.py`;
- any legacy SMC module;
- configuration, runner, trace, strategy, risk, execution, broker, API, data,
  report, or integration code.

## 6. Exact Functional Boundary

The future module may:

- validate immutable canonical Order Block objects and complete source histories;
- validate locally verifiable confirmed swing and structure-event evidence;
- identify the exact source invalidation transition and snapshot;
- select the earliest qualifying BOS or CHOCH inside the locked 0-to-10 closed
  bar window;
- create one role-reversed Breaker per qualifying source Order Block;
- retain immutable source IDs and original zone geometry;
- apply the locked Breaker lifecycle to strictly later observations;
- emit deterministic immutable Breaker, transition, snapshot, and result
  evidence;
- fail closed without exception leakage;
- preserve strictly prior evidence when a determinably later group fails.

The future module may not:

- detect a standalone candle zone;
- reconstruct, modify, or repair an Order Block;
- reconstruct market structure or invent a BOS or CHOCH;
- infer an absent source invalidation;
- extend the ten-bar confirmation window;
- use a formation candle as a retest;
- mutate source boundaries;
- create expiry, replacement, confidence, score, signal, or trade semantics;
- call any Decision Engine or execution path;
- register itself with current runtime code.

## 7. Locked Input Contracts

### 7.1 Top-level container contract

The analyzer accepts only:

- normalized non-empty `instrument` and `timeframe`;
- `order_blocks: tuple[OrderBlock, ...] | None`;
- `order_block_transitions: tuple[OrderBlockTransition, ...] | None`;
- `order_block_snapshots: tuple[OrderBlockSnapshot, ...] | None`;
- `swings: tuple[DealingRangeSwing, ...] | None`;
- `structure_events: tuple[DealingRangeStructureEvent, ...] | None`;
- `observations: tuple[BreakerBlockObservation, ...] | None`.

Each non-`None` container must be an exact tuple. Lists, generators, mappings,
sets, coercion, silent sorting, silent deduplication, or repaired values are
forbidden.

Instrument and timeframe are stripped and uppercased before identity use. Empty
normalized text is invalid.

### 7.2 BreakerBlockObservation

`BreakerBlockObservation` is frozen and contains exactly:

- `index: int`;
- `timestamp: datetime`;
- `high_tick: int`;
- `low_tick: int`;
- `close_tick: int`.

Required validation:

- index is a non-negative integer and not `bool`;
- timestamp is timezone-aware and normalized to UTC;
- high, low, and close are integers and not `bool`;
- `low_tick <= close_tick <= high_tick`;
- observation indices are strictly increasing;
- normalized observation timestamps are independently strictly increasing;
- duplicate index or duplicate normalized timestamp is invalid.

The observation tuple supplies all locally required source, swing, event,
invalidation, confirmation, and lifecycle moments. No raw or external data may
be fetched.

### 7.3 Canonical OrderBlock

Every source block must be a frozen `OrderBlock` with all required fields
present. The analyzer must:

- validate direction as exactly bullish or bearish;
- validate all integer fields as non-boolean integers;
- validate all timestamps as timezone-aware;
- validate hash fields as lowercase 64-character SHA-256 text;
- validate displacement tuple lengths, ordering, and confirmation relationship;
- validate wick/body containment, directional proximal/distal, exact midpoint,
  and detection moment;
- require `source_swing_id` to resolve to exactly one supplied canonical swing;
- recompute `block_id` with public `make_order_block_id(identity_kind="BLOCK",
  ...)`;
- reject missing, duplicate, forked, contradictory, reordered, or dangling
  source evidence.

The Breaker analyzer does not redetect the Order Block from candles and does not
re-evaluate its original displacement quality.

The source Order Block tuple is strictly increasing by the exact composite key:

1. `detection_index`;
2. normalized `detection_timestamp`;
3. `source_candle_index`;
4. `direction.value`;
5. `displacement_indices`; and
6. `block_id`.

`block_id` is used only after the preceding causal fields are equal. Duplicate
keys, decreasing keys, duplicate block IDs, or silently sorted input are
`INVALID`.

### 7.4 Complete Order Block transition and snapshot history

Transition and snapshot tuples are separate immutable streams. Each stream must
be independently nondecreasing by the composite effective moment `(index,
normalized timestamp)`.

At an equal effective moment:

- transitions for one source block remain in upstream lifecycle causal order;
- the snapshot tuple exact-mirrors that transition order through each snapshot's
  final transition ID;
- independent source blocks use the canonical Order Block composite order from
  Section 7.3 in both tuples; and
- direction, transition ID, snapshot ID, and hash lexical order are identity or
  validation data, never chronology tie-breaks.

For each source block:

- transitions and snapshots form a complete one-to-one history;
- each transition ID is recomputed with public `make_order_block_id`;
- each snapshot ID is recomputed with public `make_order_block_id`;
- snapshot direction exactly equals source block direction;
- each snapshot contains the exact ordered complete transition-ID prefix;
- state transitions never regress or fork;
- no transition follows terminal source `INVALIDATED`;
- the final source transition used for Breaker formation is exactly
  `to_state=INVALIDATED` with reason `CLOSE_THROUGH_INVALIDATION`;
- the corresponding final snapshot is exactly `INVALIDATED`;
- the final snapshot's last transition ID equals that invalidation transition
  ID;
- source invalidation index and timestamp match between transition and snapshot.

Missing, extra, skipped, reordered, duplicate, forked, wrong-reason, impossible,
or mismatched histories are invalid.

Canonical source histories ending in `DETECTED`, `ACTIVE`, `TOUCHED`,
`PARTIALLY_MITIGATED`, `MITIGATED`, or `FULLY_TRAVERSED` remain valid inputs but
are not Breaker candidates. They do not require a synthetic invalidation and do
not create `UNKNOWN`.

### 7.5 Confirmed DealingRangeSwing

Every supplied swing must be a frozen `DealingRangeSwing`. The analyzer must
validate locally available facts:

- side is exactly `HIGH` or `LOW`;
- price is an integer tick and not `bool`;
- provenance is a canonical `SMCV2EventProvenance`;
- provenance has exactly one source index and timestamp;
- confirmation does not precede the committed two-bar delay;
- source and confirmation timestamps exact-match their observations;
- price exact-matches the source observation high for a high swing or low for a
  low swing;
- swing ID is a lowercase 64-character hash;
- IDs and source-side identities are unique;
- the tuple follows the locked strictly increasing swing composite order.

The exact swing composite key is:

`(confirmation_index, source_index, side.value, swing_id)`

Duplicate or decreasing keys are `INVALID`. `swing_id` is used only after the
preceding causal fields are equal and may not move later evidence ahead of
earlier evidence.

There is no public standalone swing-ID builder. The Breaker analyzer validates
hash shape, provenance, price, ordering, uniqueness, and references, but must not
invent a private replacement identity algorithm.

### 7.6 Confirmed DealingRangeStructureEvent

Every event must be a frozen `DealingRangeStructureEvent`. Required validation:

- direction is exactly bullish or bearish;
- type is exactly BOS or CHOCH;
- broken swing reference exists;
- broken swing side is `HIGH` for bullish and `LOW` for bearish;
- event provenance source indices are contiguous;
- source-index and source-timestamp tuple lengths match;
- the final source index and timestamp equal the confirmation moment;
- every provenance moment exact-matches a supplied observation;
- the broken swing confirmed strictly before displacement began;
- confirmation close passes the exact one-tick broken-swing close rule;
- public `make_dealing_range_id(identity_kind="EVENT", ...)` reproduces
  `event_id`;
- tuple order follows the locked event composite key.

The exact event composite key is:

`(confirmation_index, normalized_confirmation_timestamp, direction.value,
event_type.value, event_id)`

The event tuple must be strictly increasing by this key. Events with the same
confirmation index and normalized timestamp remain one atomic group; their
direction and type values validate deterministic within-group caller order but
do not reorder one effective group across another.

Same confirmation group rules are:

- repeated object or repeated event ID -> `INVALID`;
- more than one event in the same direction -> `INVALID`;
- one canonical bullish and one canonical bearish event -> `AMBIGUOUS`;
- no same-group partial promotion is allowed.

### 7.7 Foreign validation boundary

The analyzer validates only supplied, locally recomputable evidence. It may use:

- public shared primitive validators;
- public `make_order_block_id`;
- public `make_dealing_range_id`;
- supplied observations, swings, events, source blocks, transitions, and
  snapshots.

It must not demand unavailable raw Order Block candles, reconstruct source
signals, call a private dependency function, or trust an unvalidated foreign
identity.

## 8. Locked Source Invalidation Semantics

A source Order Block becomes eligible for Breaker consideration only after its
canonical final history reaches `INVALIDATED`.

The invalidation observation must exact-match the final invalidation transition
and snapshot moment.

Required close geometry:

- bullish source Order Block:
  - invalidation close `<= source distal_tick - 1`;
  - proposed Breaker direction is bearish.
- bearish source Order Block:
  - invalidation close `>= source distal_tick + 1`;
  - proposed Breaker direction is bullish.

Close exactly at the source distal boundary is not the one-tick invalidation and
cannot form a Breaker.

Wick-only passage through source distal without the adverse close is not source
invalidation.

A supplied source `INVALIDATED` transition that lacks this exact observation
geometry is invalid. A geometric close-through without the exact source
transition and snapshot is also invalid.

Observation-coverage status is:

- source invalidation strictly before the first supplied observation, including
  an empty observation tuple, is incomplete pre-horizon evidence and returns
  `UNKNOWN` for that source;
- no later observation or structure event may be relabeled as the missing source
  invalidation;
- source invalidation inside the supplied observation horizon without its exact
  observation is `INVALID`;
- source invalidation strictly after the final supplied observation is
  post-horizon history and is `INVALID`;
- all determinably later supplied groups must reconcile before a pre-horizon
  `UNKNOWN` may be returned;
- later `INVALID` or `AMBIGUOUS` evidence retains its higher final precedence.

The source invalidation moment is immutable Breaker creation evidence.

## 9. Locked Structure-Confirmation Window and Selection

### 9.1 Window definition

The qualifying event may confirm:

- on the source invalidation observation; or
- on any of the next ten supplied fully closed observations.

The window is positional in the canonical observation tuple:

- invalidation observation position: offset `0`;
- first later closed observation: offset `1`;
- tenth later closed observation: offset `10`.

Numeric source-index gaps do not replace positional counting. Missing or
duplicate observation moments are not silently repaired.

Offset `10` qualifies. Offset `11` does not qualify.

### 9.2 Direction and type

The event direction must equal the proposed Breaker direction and be the exact
opposite of the source Order Block direction.

Both canonical BOS and canonical CHOCH qualify. The event type is retained as
immutable context and does not change Breaker direction or lifecycle.

### 9.3 Earliest-event selection

For one source block:

- qualifying events are evaluated chronologically;
- the earliest qualifying confirmation moment wins;
- later events do not replace, revise, or enrich the Breaker;
- event hash lexical order is not a chronological selector.

At the earliest confirmation moment:

- one matching event creates the Breaker;
- exact duplicate or same-direction forked events are invalid;
- a canonical opposing-direction pair makes the atomic group ambiguous;
- ambiguous formation promotes no Breaker, transition, or snapshot.

Independent source blocks remain independently eligible. They may reference the
same canonical qualifying event when each complete causal chain satisfies this
record. Their outputs follow canonical source-block order.

### 9.4 Incomplete and exhausted windows

When no qualifying event has yet appeared:

- fewer than ten strictly later closed observations after a valid source
  invalidation leaves the confirmation window incomplete and returns `UNKNOWN`;
- a complete offset-0-through-offset-10 window with no qualifying event returns
  `NONE` for that source;
- an event first confirming at offset `11` or later does not retroactively form
  a Breaker.

Malformed or mismatched present evidence is `INVALID`, not `UNKNOWN`.

## 10. Locked Role-Reversal Geometry

The Breaker retains the exact source Order Block geometry:

- wick low and high;
- body low and high;
- exact Decimal midpoint.

No boundary may expand, contract, shift, round, or follow later price.

Directional role reversal is:

- bullish Breaker:
  - source must be bearish;
  - proximal tick = original wick high;
  - distal tick = original wick low.
- bearish Breaker:
  - source must be bullish;
  - proximal tick = original wick low;
  - distal tick = original wick high.

The midpoint is exactly:

`Decimal(wick_low_tick + wick_high_tick) / Decimal(2)`

Canonical serialization is exact integer or half tick:

- integer midpoint -> `.0`;
- half-tick midpoint -> `.5`;
- every zero-valued Decimal representation -> `0.0`;
- no float conversion;
- no dependence on ambient Decimal precision;
- arbitrary-magnitude positive or negative integer ticks remain exact.

Body boundaries must remain inside wick boundaries. Role reversal changes
proximal/distal interpretation only; it does not reverse or mutate stored low and
high values.

## 11. Locked Formation and First-Eligible Retest

Breaker formation occurs at the selected structure-event confirmation moment.
Creation emits:

- `from_state=None`;
- `to_state=ACTIVE`;
- reason `ROLE_REVERSAL_CONFIRMED`.

The formation transition binds:

- source Order Block ID;
- source invalidation transition ID;
- source invalidation snapshot ID;
- selected structure-event ID;
- Breaker direction;
- source invalidation moment;
- structure-confirmation moment;
- immutable zone geometry.

The formation observation cannot:

- touch;
- partially mitigate;
- mitigate;
- invalidate;
- revise geometry;
- create a second lifecycle transition.

Retest eligibility requires both observation index and normalized timestamp to be
strictly later than the formation moment.

There is no requirement that integer indices be numerically consecutive.
Eligibility is based on canonical closed-observation chronology.

## 12. Locked Lifecycle and Same-Index Precedence

### 12.1 States

The exact Breaker lifecycle vocabulary is:

- `ACTIVE`;
- `TOUCHED`;
- `PARTIALLY_MITIGATED`;
- `MITIGATED`;
- `INVALIDATED`.

No `DETECTED`, `FULLY_TRAVERSED`, `EXPIRED`, `SUPERSEDED`, replacement, or
reactivation state exists in version 1.

### 12.2 Bullish retest geometry

For a bullish Breaker on a strictly later observation:

- `low_tick > proximal_tick` -> no lifecycle change;
- `low_tick == proximal_tick` -> `TOUCHED`;
- `midpoint_tick < Decimal(low_tick) < Decimal(proximal_tick)` ->
  `PARTIALLY_MITIGATED`;
- `Decimal(low_tick) <= midpoint_tick` with no invalidating close ->
  `MITIGATED`;
- `close_tick <= distal_tick - 1` -> `INVALIDATED`.

### 12.3 Bearish retest geometry

For a bearish Breaker:

- `high_tick < proximal_tick` -> no lifecycle change;
- `high_tick == proximal_tick` -> `TOUCHED`;
- `Decimal(proximal_tick) < Decimal(high_tick) < midpoint_tick` ->
  `PARTIALLY_MITIGATED`;
- `Decimal(high_tick) >= midpoint_tick` with no invalidating close ->
  `MITIGATED`;
- `close_tick >= distal_tick + 1` -> `INVALIDATED`.

### 12.4 Precedence and direct transitions

Same-index close-through invalidation has precedence over touch, partial
mitigation, midpoint mitigation, and wick traversal.

Direct deeper transitions are allowed when geometry skips shallower states:

- `ACTIVE -> PARTIALLY_MITIGATED`;
- `ACTIVE -> MITIGATED`;
- `TOUCHED -> MITIGATED`;
- `ACTIVE`, `TOUCHED`, `PARTIALLY_MITIGATED`, or `MITIGATED` ->
  `INVALIDATED`.

No state regression is allowed. Repeated observations at the current or a
shallower depth emit no new transition.

Wick passage beyond distal without the adverse one-tick close is `MITIGATED`;
version 1 has no `FULLY_TRAVERSED` state.

`INVALIDATED` is terminal. There is no default expiry.

### 12.5 Exact transition reasons

The only allowed reason tokens are:

- `ROLE_REVERSAL_CONFIRMED`;
- `WICK_TOUCHED`;
- `PARTIAL_MITIGATION`;
- `MIDPOINT_MITIGATION`;
- `CLOSE_THROUGH_INVALIDATION`.

Any other spelling, casing, whitespace, alias, or reason is invalid.

## 13. Locked Public API

The public surface is exactly:

- `BREAKER_BLOCK_DETECTOR_VERSION`;
- `BreakerBlockState`;
- `BreakerBlockObservation`;
- `BreakerBlock`;
- `BreakerBlockTransition`;
- `BreakerBlockSnapshot`;
- `BreakerBlockResult`;
- `make_breaker_block_id`;
- `analyze_breaker_blocks`.

The exact keyword-only analyzer signature is:

```python
def analyze_breaker_blocks(
    *,
    instrument: str,
    timeframe: str,
    order_blocks: tuple[OrderBlock, ...] | None,
    order_block_transitions: tuple[OrderBlockTransition, ...] | None,
    order_block_snapshots: tuple[OrderBlockSnapshot, ...] | None,
    swings: tuple[DealingRangeSwing, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    observations: tuple[BreakerBlockObservation, ...] | None,
) -> BreakerBlockResult:
    ...
```

The exact keyword-only identity-builder signature is:

```python
def make_breaker_block_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction,
    source_order_block_id: str | None = None,
    source_order_block_invalidation_transition_id: str | None = None,
    source_order_block_invalidation_snapshot_id: str | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    wick_boundaries: SMCV2TickRange | None = None,
    body_boundaries: SMCV2TickRange | None = None,
    proximal_tick: int | None = None,
    distal_tick: int | None = None,
    midpoint_tick: Decimal | None = None,
    source_invalidation_index: int | None = None,
    source_invalidation_timestamp: datetime | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    breaker_id: str | None = None,
    from_state: BreakerBlockState | None = None,
    to_state: BreakerBlockState | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    reason: str | None = None,
    state: BreakerBlockState | None = None,
    transition_ids: tuple[str, ...] = (),
) -> str:
    ...
```

No configuration object exists in version 1. The one-tick buffer, ten-bar
confirmation window, boundaries, eligibility, lifecycle, identity, chronology,
and status semantics are fixed.

### 13.1 Exact public dataclass fields

`BreakerBlockObservation`:

- `index: int`;
- `timestamp: datetime`;
- `high_tick: int`;
- `low_tick: int`;
- `close_tick: int`.

`BreakerBlock`:

- `breaker_id: str`;
- `direction: SMCV2Direction`;
- `source_order_block_id: str`;
- `source_order_block_invalidation_transition_id: str`;
- `source_order_block_invalidation_snapshot_id: str`;
- `structure_event_id: str`;
- `structure_event_type: DealingRangeEventType`;
- `wick_low_tick: int`;
- `wick_high_tick: int`;
- `body_low_tick: int`;
- `body_high_tick: int`;
- `proximal_tick: int`;
- `distal_tick: int`;
- `midpoint_tick: Decimal`;
- `source_invalidation_index: int`;
- `source_invalidation_timestamp: datetime`;
- `confirmation_index: int`;
- `confirmation_timestamp: datetime`.

`BreakerBlockTransition`:

- `transition_id: str`;
- `breaker_id: str`;
- `source_order_block_id: str`;
- `source_order_block_invalidation_transition_id: str`;
- `source_order_block_invalidation_snapshot_id: str`;
- `structure_event_id: str`;
- `from_state: BreakerBlockState | None`;
- `to_state: BreakerBlockState`;
- `index: int`;
- `timestamp: datetime`;
- `reason: str`.

`BreakerBlockSnapshot`:

- `snapshot_id: str`;
- `breaker_id: str`;
- `source_order_block_id: str`;
- `source_order_block_invalidation_transition_id: str`;
- `source_order_block_invalidation_snapshot_id: str`;
- `structure_event_id: str`;
- `direction: SMCV2Direction`;
- `state: BreakerBlockState`;
- `index: int`;
- `timestamp: datetime`;
- `transition_ids: tuple[str, ...]`.

`BreakerBlockResult`:

- `status: SMCV2PrimitiveStatus`;
- `breakers: tuple[BreakerBlock, ...] = ()`;
- `transitions: tuple[BreakerBlockTransition, ...] = ()`;
- `snapshots: tuple[BreakerBlockSnapshot, ...] = ()`;
- `reasons: tuple[str, ...] = ()`;
- `blocking_reasons: tuple[str, ...] = ()`.

Every field in `BreakerBlockObservation`, `BreakerBlock`,
`BreakerBlockTransition`, and `BreakerBlockSnapshot` is required and has no
default. `BreakerBlockResult.status` is required and has no default; only the
five result tuple fields shown above have the exact empty-tuple defaults.
Every public dataclass is frozen. Result collections are immutable tuples.

## 14. Locked Deterministic Identity Contract

### 14.1 Common identity rules

The exact identity kinds are:

- `BREAKER`;
- `TRANSITION`;
- `SNAPSHOT`.

Every identity:

- binds `BREAKER_BLOCK_DETECTOR_VERSION`;
- uses stripped-uppercase instrument and timeframe;
- serializes enums by exact `.value`;
- normalizes timestamps to UTC;
- serializes timestamps as exact
  `YYYY-MM-DDTHH:MM:SS.ffffffZ`;
- serializes midpoint with exact `.0` or `.5`;
- uses sorted-key compact ASCII JSON;
- hashes UTF-8 bytes with lowercase SHA-256;
- rejects malformed nested values with only `TypeError` or `ValueError`.

### 14.2 BREAKER schema

`BREAKER` requires:

- direction;
- source Order Block ID;
- source invalidation transition ID;
- source invalidation snapshot ID;
- selected structure-event ID and type;
- wick and body boundaries;
- proximal, distal, and midpoint;
- source invalidation index and timestamp;
- confirmation index and timestamp.

`BREAKER` forbids:

- breaker ID;
- from state;
- to state;
- effective index;
- effective timestamp;
- reason;
- state;
- transition IDs.

Builder validation must reconcile:

- direction is opposite source direction in analyzer context;
- body is inside wick;
- role-reversed proximal/distal match direction;
- midpoint exactly matches wick;
- invalidation moment does not follow confirmation;
- confirmation lies inside the locked positional window in analyzer context;
- all required hashes have exact lowercase SHA-256 shape.

### 14.3 TRANSITION schema

`TRANSITION` requires:

- direction;
- breaker ID;
- source Order Block ID;
- source invalidation transition ID;
- source invalidation snapshot ID;
- structure-event ID;
- from state, including exact `None` for creation;
- to state;
- effective index and timestamp;
- exact reason.

`TRANSITION` forbids:

- structure-event type;
- wick boundaries;
- body boundaries;
- proximal;
- distal;
- midpoint;
- source invalidation index and timestamp;
- confirmation index and timestamp;
- snapshot state;
- transition IDs.

Only the lifecycle edges and reason tokens in Section 12 are valid.

### 14.4 SNAPSHOT schema

`SNAPSHOT` requires:

- direction;
- breaker ID;
- source Order Block ID;
- source invalidation transition ID;
- source invalidation snapshot ID;
- structure-event ID;
- state;
- effective index and timestamp;
- non-empty ordered unique transition IDs.

`SNAPSHOT` forbids:

- structure-event type;
- wick boundaries;
- body boundaries;
- proximal;
- distal;
- midpoint;
- source invalidation index and timestamp;
- confirmation index and timestamp;
- from state;
- to state;
- reason.

The final transition ID must correspond to the snapshot state and effective
moment. Transition history is complete, immutable, ordered, and prefix-growing.

## 15. Locked Immutable Lifecycle and Snapshot Contract

Creation emits exactly one Breaker, one transition, and one snapshot.

Every later state change:

- retains the exact immutable Breaker object;
- appends exactly one transition;
- appends exactly one snapshot;
- preserves all prior output objects byte-for-byte;
- extends transition history by exact prefix;
- uses the same source Order Block, invalidation transition, invalidation
  snapshot, structure event, direction, and boundaries.

No later observation may revise:

- source IDs;
- event type;
- direction;
- wick or body boundaries;
- proximal or distal;
- midpoint;
- invalidation moment;
- confirmation moment.

No lifecycle event is emitted when the effective state does not change.

## 16. Locked Chronology and Same-Index Processing Precedence

The analyzer processes complete effective groups in supplied causal order and
never silently sorts input.

For one effective observation group, the exact order is:

1. validate the immutable pre-group source and Breaker state;
2. validate the complete swing and structure-event group;
3. validate existing Breaker adverse close-through transitions;
4. evaluate existing Breaker touch or mitigation transitions;
5. evaluate source Order Block invalidation evidence;
6. evaluate qualifying Breaker formation events;
7. promote the complete group atomically.

This order ensures:

- existing Breaker invalidation precedes a new independent Breaker formation;
- a formation observation cannot retest its new Breaker;
- no partial output survives a failing or ambiguous group.

Within an effective group:

- independent source candidates use source invalidation moment first, then the
  exact canonical Order Block composite key from Section 7.3;
- source transition and snapshot records use the separate-stream causal and
  mirrored ordering from Section 7.4;
- swings and events retain the exact supplied composite order from Sections 7.5
  and 7.6;
- event, transition, snapshot, swing, and block hashes are identity validation,
  not cross-moment chronology;
- dictionary or set iteration order cannot affect output.

A determinably later malformed group returns `INVALID`, preserves only strictly
prior promoted evidence, and promotes nothing from the failing group or after.
An unknowable malformed effective moment claims no trustworthy prefix.

## 17. Locked Result Status Semantics

The exact final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

### 17.1 INVALID

Return `INVALID` for present malformed or contradictory evidence, including:

- wrong container type;
- malformed required fields;
- naive timestamp;
- boolean tick or index;
- noncanonical source identity;
- incomplete or forked history;
- source invalidation geometry mismatch;
- dangling swing or event reference;
- noncanonical event identity;
- duplicate or same-direction forked same-group event;
- chronology violation;
- identity schema violation;
- impossible lifecycle edge;
- failing effective-group reconciliation.

No exception may leak from the analyzer. Public identity builder failures are
limited to `TypeError` or `ValueError`.

### 17.2 AMBIGUOUS

Return `AMBIGUOUS` only when one atomic confirmation group contains one
canonical bullish and one canonical bearish structure event and at least one
source Breaker decision depends on that group.

The ambiguous group promotes no Breaker evidence. Independent strictly prior
evidence is retained.

### 17.3 UNKNOWN

Return `UNKNOWN` when:

- any required top-level context is `None`; or
- a canonical source invalidation is strictly before the supplied observation
  horizon and its exact close geometry cannot be reconstructed; or
- a canonical invalidated source has fewer than ten strictly later closed
  observations, no qualifying event has appeared, and the confirmation window
  remains genuinely incomplete.

Present malformed or mismatched evidence is never downgraded to `UNKNOWN`.
All determinably later supplied groups must reconcile before `UNKNOWN` may be
returned.

### 17.4 VALID

Return `VALID` when at least one Breaker is deterministically formed and no
higher-precedence condition exists.

### 17.5 NONE

Return `NONE` when complete valid inputs contain no Breaker, including:

- complete empty tuples;
- no invalidated source Order Block;
- exhausted offset-0-through-offset-10 window without a qualifying event;
- only nonmatching events after the locked window is exhausted;
- first matching event after the locked window.

Independent multiple valid Breakers are deterministic `VALID`, not ambiguous.

## 18. Locked Prefix-Invariance Contract

Prefix invariance applies only when:

- the earlier input ends at a complete effective-group boundary;
- the appended evidence begins at a strictly later effective moment;
- the earlier prefix is valid and internally complete;
- dependency histories required inside the earlier horizon are unchanged;
- every source block, source transition, source snapshot, swing, and event tuple
  retains its exact locked composite-order prefix.

Under those conditions, every earlier Breaker, transition, snapshot, status
reason, and blocking reason remains byte-for-byte unchanged when later evidence
is appended.

The following are not eligible prefix comparisons:

- same-effective append;
- insertion into an earlier event group;
- partial source transition/snapshot group;
- partial swing/event provenance;
- history repair;
- replacement of a source identity;
- append that exposes an earlier malformed claim.

Ineligible input is validated normally and may return `INVALID`, `AMBIGUOUS`, or
`UNKNOWN`. It must not be silently reordered into an eligible prefix.

## 19. Locked Inline Synthetic 44-Case Unit-Test Matrix

The future test module must retain exactly the following sequential logical case
numbers. Parameterization may increase physical test collection but may not add,
remove, skip, rename, or merge away logical case numbers.

1. Any required top-level tuple set to `None` returns `UNKNOWN`; no partial
   output is emitted, and normalized empty instrument or timeframe is invalid.
2. Complete empty tuples return `NONE` with immutable empty outputs.
3. Instrument/timeframe normalization and equivalent UTC timestamps are
   deterministic; naive timestamps fail closed.
4. Observation fields, frozen state, integer/non-boolean ticks, and
   `low <= close <= high` are enforced.
5. Observation tuple type and independently strict index/timestamp chronology
   are enforced; duplicates and silent-sort inputs are invalid.
6. Canonical bullish and bearish source Order Blocks reproduce through the
   public identity builder; malformed nested block data fails closed.
7. Source block tuples use the exact detection-index, normalized-detection-time,
   source-index, direction, displacement-index-tuple, and block-ID composite key;
   unique IDs, no-silent-sort behavior, and contradictory or duplicate identity
   rejection are exact.
8. Complete source transition/snapshot histories reproduce every identity and
   exact ordered prefix; one-source equal-moment records retain upstream
   lifecycle causal order.
9. Separate transition and snapshot tuples independently preserve nondecreasing
   effective moments; snapshots mirror transition causal order, independent
   sources use canonical block order, and hashes never become chronology
   tie-breaks.
10. The final source invalidation is exactly `CLOSE_THROUGH_INVALIDATION` with
    matching `INVALIDATED` snapshot; missing, wrong, forked, or post-terminal
    history is invalid; pre-horizon missing invalidation observation is
    `UNKNOWN`, while in-horizon missing or post-horizon history is `INVALID`.
11. Confirmed swing provenance, side, price, confirmation delay, exact
    `(confirmation_index, source_index, side.value, swing_id)` composite order,
    uniqueness, no-silent-sort behavior, and observation reconciliation are
    enforced.
12. Confirmed event contiguous provenance, broken-swing side, one-tick close,
    event-ID recomputation, exact `(confirmation_index,
    normalized_confirmation_timestamp, direction.value, event_type.value,
    event_id)` composite order, no-silent-sort behavior, and reference validation
    are enforced.
13. A failed bearish Order Block plus qualifying bullish confirmation creates a
    bullish Breaker.
14. A failed bullish Order Block plus qualifying bearish confirmation creates a
    bearish Breaker.
15. Confirmation on the exact source invalidation observation qualifies.
16. Confirmation on a strictly later observation inside the window qualifies.
17. Confirmation at exact offset `10` qualifies.
18. Confirmation first appearing at offset `11` or later does not qualify.
19. A valid invalidated source with pre-horizon missing invalidation observation
    or an incomplete no-event confirmation window returns `UNKNOWN`; no later
    observation is relabeled, and determinably later malformed evidence still
    takes `INVALID` precedence.
20. A complete exhausted no-event window returns `NONE`.
21. Canonical events in the wrong direction do not form a Breaker; present event
    contradictions remain invalid.
22. Canonical BOS qualifies and its exact event type is retained.
23. Canonical CHOCH qualifies and its exact event type is retained.
24. Earliest qualifying event wins; later BOS/CHOCH does not replace or enrich
    the immutable Breaker.
25. Original wick/body boundaries, exact midpoint, reversed proximal/distal,
    direction, source IDs, invalidation moment, and confirmation moment are
    preserved in both directions.
26. Formation emits exactly `None -> ACTIVE` with
    `ROLE_REVERSAL_CONFIRMED` and one exact complete-history snapshot.
27. Formation observation cannot retest; the first strictly later observation
    is eligible even when numeric indices are not consecutive.
28. Exact bullish and bearish proximal equality emits `TOUCHED`.
29. Strict proximal-to-midpoint penetration emits `PARTIALLY_MITIGATED`.
30. Exact integer/half-tick midpoint equality emits `MITIGATED` with
    Decimal-context-independent arbitrary-magnitude behavior.
31. Direct deeper midpoint penetration may move `ACTIVE` or `TOUCHED` directly
    to `MITIGATED`; wick beyond distal without close-through remains mitigated.
32. Same-index adverse close-through overrides touch/partial/mitigation and
    emits only `INVALIDATED`.
33. Strictly later close-through invalidates `ACTIVE`, `TOUCHED`,
    `PARTIALLY_MITIGATED`, or `MITIGATED` in exact bullish/bearish mirrors.
34. No state regression, repeated transition, expiry, replacement, boundary
    mutation, reactivation, or post-`INVALIDATED` change is possible.
35. Duplicate event IDs, exact duplicate events, or multiple same-direction
    same-group events are invalid; one bullish plus one bearish canonical event
    produces atomic `AMBIGUOUS` without partial promotion.
36. Multiple independent source blocks and shared qualifying events produce
    deterministic canonical output using source invalidation moment followed by
    the exact canonical Order Block key, independent of hash, set, or dictionary
    order.
37. A determinably later malformed block/history/swing/event/observation group
    returns `INVALID`, preserves strictly prior immutable evidence, and promotes
    nothing from the failing group or later.
38. Final status precedence is exactly
    `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`; incomplete windows cannot
    suppress later invalid evidence.
39. `BREAKER` identity exhaustively enforces all required/forbidden fields,
    source/event/boundary/direction/moment sensitivity, normalization, midpoint
    canonicalization, hash validation, and exception containment.
40. `TRANSITION` identity exhaustively enforces all required/forbidden fields,
    every allowed direct edge, every impossible edge, exact reasons, source-link
    sensitivity, and effective-moment sensitivity.
41. `SNAPSHOT` identity exhaustively enforces all required/forbidden fields,
    ordered unique complete transition history, state/moment/source
    reconciliation, history-order sensitivity, and malformed hashes.
42. Public analyzer and builder expose exact keyword-only names/defaults; every
    public dataclass has the exact locked field names, annotations, frozen state,
    and result tuple defaults; version, enum values, exports, and unknown
    identity-kind rejection are exact.
43. Repeated input is deterministic; strictly later complete-group append
    preserves every exact composite-order tuple prefix; same-effective, partial,
    historical, reordering, or repairing appends are ineligible and never
    silently sorted.
44. The standalone module has no file I/O, pandas, external fixture, legacy SMC,
    Mitigation consumption, context, config, strategy, risk, execution,
    registration, network, or integration dependency; focused and full
    regression suites pass.

The matrix contains exactly `44` logical cases.

## 20. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing file;
- creation of any file other than the future reserved paths after later gates;
- external fixtures or market data;
- edits to completed SMC v2 dependencies;
- import or modification of legacy SMC modules;
- Order Block, swing, BOS, or CHOCH reconstruction;
- Mitigation Block consumption or mutation;
- Breaker expiry, replacement, scoring, confidence, signal, filter, or trade
  semantics;
- Inducement, kill-zone, Volume Profile, context aggregation, trace integration,
  decision integration, or execution integration;
- runtime flags, CLI, configuration, package exports, or adapters;
- tuning from backtest, OOS, PnL, entry, exit, or outcome evidence;
- paper or live progression.

## 21. Mandatory Pre-Implementation Gates

Before implementation may begin:

1. this exact decision record is independently audited;
2. all semantic or structural findings are corrected documentation-only;
3. the corrected record receives exact one-file staging authorization;
4. cached diff and commit preflight pass;
5. the exact decision record is committed and separately authorized for push;
6. live remote hash and clean worktree are verified;
7. a post-push Breaker implementation-readiness audit passes;
8. the future three targets remain absent;
9. dependency hashes remain exact;
10. an explicit human decision operationally activates only the exact future
    three-path implementation exception.

No gate may be inferred from completion of an earlier capability.

## 22. Implementation Stop Conditions

The future task must stop without fallback if:

- any reserved target already exists;
- any path outside the exact three-path scope changes;
- dependency hash or commit evidence changes unexpectedly;
- source invalidation cannot be reconciled exactly;
- the 0-to-10 closed-bar window cannot be evaluated without guessing;
- swing or event foreign identity cannot be validated from supplied evidence;
- same-group event cardinality cannot be classified deterministically;
- role-reversed proximal/distal or midpoint is ambiguous;
- formation-bar non-retest cannot be preserved;
- lifecycle or same-index precedence conflicts with this record;
- identity required/forbidden schemas cannot be enforced exactly;
- malformed required fields leak exceptions;
- prefix invariance fails;
- an external fixture, generated report, performance result, private data, or
  network input becomes necessary;
- runtime, strategy, risk, config, registration, trace, execution, or
  integration work becomes necessary;
- focused tests or full regression fail;
- implementation appears necessary to resolve ambiguity in this decision.

A stop condition freezes the task. It does not authorize widened scope, silent
coercion, silent sorting, relaxed validation, rounding, tuning, or a favorable
reinterpretation.

## 23. Completion, Rollback, Promotion, and Global-Freeze Gates

Later implementation completion requires:

- independent review of every changed line;
- exact three-path reconciliation;
- all 44 logical cases passing;
- full regression passing;
- exact source invalidation and 0-to-10 confirmation-window evidence;
- exact role reversal, boundaries, first eligibility, lifecycle, status,
  identity, atomic-group, fail-closed, and prefix-invariance evidence;
- proof that no current production import or execution path changed;
- proof that no sensitive, generated, or external evidence was added;
- a completed Breaker Block checkpoint;
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created implementation
paths and requires explicit instruction before destructive removal. After
commit, rollback must use a bounded revert of the task commit rather than
history rewriting. Every rollback requires focused tests, full regression, and
clean-scope audit.

Successful implementation would prove only standalone deterministic Breaker
Block conformance. It would not prove trading edge, OOS improvement, strategy
value, readiness, threshold approval, paper approval, live approval, or
permission for kill-zone, Inducement, Volume Profile, context, or integration
work.

The global code freeze remains active outside the exact future task. No later
module inherits authorization from this record.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `CAPABILITY=BREAKER_BLOCK`
- `IMPLEMENTATION_ORDER_POSITION=9`
- `DOCUMENTATION_ONLY=True`
- `EXACT_DOCUMENTATION_PATHS_CHANGED=1`
- `FUTURE_IMPLEMENTATION_PATHS_RESERVED=3`
- `INLINE_SYNTHETIC_LOGICAL_CASES=44`
- `EXTERNAL_FIXTURE_AUTHORIZED=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `PAPER_TRADING_AUTHORIZED=False`
- `LIVE_TRADING_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
- `NEXT_REQUIRED_GATE=INDEPENDENT_FINAL_DOCUMENTATION_AUDIT`
