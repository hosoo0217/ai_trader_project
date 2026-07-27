# SMC v2 Premium, Equilibrium, and Discount Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-PREMIUM-DISCOUNT-FREEZE-LIFT-DECISION-2026-07-27`.
- Parent review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Parent specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Implementation-order phase: `5 - PREMIUM, EQUILIBRIUM, AND DISCOUNT`.
- Implementation parent commit:
  `4588d2966b3c4ba5215f9e990a0520ee51d5cdbe`.
- Requested module: standalone Premium, Equilibrium, and Discount diagnostics.
- Current task type: documentation-only formal decision record.
- Decision classification:
  `APPROVED - DOCUMENTATION DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`.
- Global code-freeze status: `ACTIVE`.
- Python implementation authorized by this record: `False`.
- Test or fixture change authorized by this record: `False`.
- Integration authorized by this record: `False`.
- Staging, commit, or push authorized by this record: `False`.

This record reserves and specifies one possible future Premium, Equilibrium, and
Discount task. It does not make the bounded exception operational, authorize
code, or transfer authority from any completed dependency task.

## 2. Effective-State Interpretation

The accepted implementation order is:

1. Shared primitives and test helpers.
2. Equal High and Equal Low.
3. Swing Hierarchy and Dealing Range.
4. Internal and External Liquidity Mapping.
5. Premium, Equilibrium, and Discount.

The first four phases are committed, pushed, and independently checkpointed.
Their completion satisfies the dependency-order gate for this documentation
decision only. The fifth capability derives its zones directly from canonical
Dealing Range snapshots; it does not need to consume Liquidity Map output.

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

The accepted parent plan locks these semantics:

- zones exist only when a valid Dealing Range exists,
- Equilibrium is the arithmetic midpoint of that locked range,
- prices below Equilibrium are Discount,
- prices above Equilibrium are Premium,
- exact midpoint equality is Equilibrium, and
- every interpretation carries the Dealing Range identity and direction so that
  a bare price level cannot be treated as directional confirmation.

The completed Liquidity Map phase is an implementation-order prerequisite, not a
runtime input requirement. Any need to import or consume Liquidity Map output in
the future standalone module is a stop condition requiring a new review.

## 4. Exact Change Authorized in This Documentation Task

Only this new file may be created in the current task:

- `docs/smc_v2_premium_discount_diagnostic_freeze_lift_decision.md`

No existing documentation, Python, test, fixture, configuration, private data,
external evidence, or generated report may change in this task. Staging, commit,
push, implementation, detector execution, and integration remain separate gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later implementation preflight and explicit human authorization pass, the
future task is reserved to exactly these three paths:

- production module: `smc/premium_discount.py`
- dedicated unit tests: `tests/test_premium_discount.py`
- implementation checkpoint: `docs/smc_v2_premium_discount_checkpoint.md`

All fixtures must be synthetic and inline in the dedicated test file. No external
or separate fixture file is reserved or authorized by this record.

The later task must not edit `smc/__init__.py`, `smc/smc_v2_primitives.py`,
`smc/dealing_range.py`, `smc/liquidity_map.py`, or any existing SMC v1 module.
Direct imports of completed immutable Dealing Range and shared-primitives types
are sufficient. Any need for another path is a stop condition requiring a new
scope review and explicit human approval before that edit occurs.

## 6. Exact Functional Boundary

The future standalone module may implement only:

- validation and causal chronological consumption of immutable canonical
  `DealingRangeSnapshot` values,
- validation and causal chronological consumption of fully closed integer-tick
  `PremiumDiscountObservation` values,
- selection of at most one active external Dealing Range at each effective
  moment,
- exact Decimal-based integer- or half-tick Equilibrium calculation,
- deterministic `DISCOUNT`, `EQUILIBRIUM`, and `PREMIUM` classification within
  the selected active range,
- explicit outside-range omission with `NONE` semantics,
- immutable zone-set versioning driven only by material range evidence,
- deterministic zone-set, classification, and snapshot identities,
- explicit valid, invalid, unknown, none, and ambiguous results, and
- pure prefix-invariant analysis over immutable tuples.

The future module must not:

- detect raw swings or structure events,
- construct, extend, replace, invalidate, or repair Dealing Ranges,
- infer a range from raw OHLC or visual hindsight,
- consume Liquidity Map output,
- interpret Premium or Discount as a trade direction, entry, reversal, bias, or
  quality score,
- add Fibonacci levels, quartiles, optimal-trade-entry bands, or configurable
  retracement thresholds, or
- call any strategy, decision, risk, execution, I/O, network, or registration
  path.

## 7. Locked Input Contracts

### 7.1 Top-Level Contract

The exact top-level inputs are:

- `dealing_ranges: tuple[DealingRangeSnapshot, ...] | None`
- `observations: tuple[PremiumDiscountObservation, ...] | None`

Each value must be an immutable tuple or `None`. `None` means that required
top-level context was not supplied and returns `UNKNOWN` before partial analysis.
An empty tuple is complete supplied context and is not missing data.

No `DealingRangeResult` is accepted. The caller must pass its immutable range
snapshot tuple explicitly. Result-to-result status propagation is future
integration and is outside this standalone API.

The module accepts no raw OHLC, pandas object, mutable list, generator, mapping,
file path, configuration file, environment state, or hidden global context.

### 7.2 Fully Closed Integer-Tick Observation Contract

`PremiumDiscountObservation` is a new frozen dataclass with exactly:

- `index: int`
- `timestamp: datetime`
- `price_tick: int`

Every observation must:

- represent a fully closed and already knowable price observation,
- use a non-negative integer index with booleans rejected,
- use one timezone-aware timestamp normalized to UTC,
- use one real integer tick price with booleans rejected,
- use an index that is unique across the complete observation tuple,
- use a normalized timestamp that is unique across the complete observation
  tuple,
- have indices independently strictly increasing, and
- have normalized timestamps independently strictly increasing, and
- contain no future, developing, inferred, interpolated, or floating-point price.

A duplicate index is `INVALID` even when its timestamp differs. A duplicate
normalized timestamp is `INVALID` even when its index differs. Composite-pair
ordering alone is insufficient.

An observation is a generic closed-price query. It is not a BUY, SELL, entry,
stop, target, fill, or trade record. The future standalone analyzer does not
accept a configurable choice among open, high, low, or close; the caller supplies
the already selected closed integer-tick observation under this explicit
contract. A later adapter deciding which market field to pass is integration and
is not authorized here.

### 7.3 Canonical Dealing Range Snapshot Contract

The `dealing_ranges` tuple uses the already implemented frozen
`DealingRangeSnapshot` type. The future module validates only snapshot-local
evidence and relationships that are present in this supplied tuple. Every
supplied snapshot must preserve and validate:

- kind and direction,
- snapshot, lineage, protected-swing, construction-event, and replacement
  identity hash shapes,
- ordered source swing IDs and source indices,
- exact low and high integer ticks,
- exact Decimal midpoint,
- first-known provenance,
- state,
- ordered transitions, and
- ordered transition IDs,
- transition-chain state and causal chronology, and
- every snapshot and transition identity that can be recomputed through the
  public `make_dealing_range_id()` API from fields present on the snapshot.

For every external snapshot:

- `source_swing_ids` and `source_indices` must have equal length and contain at
  least two members,
- source indices must be independently strictly increasing,
- source swing IDs must be unique valid lowercase 64-character SHA-256 values,
- `protected_swing_id` must be one member of `source_swing_ids`,
- `transition_ids` must exactly equal the ordered IDs of `transitions`,
- the first transition must be the canonical
  `None -> ACTIVE | CONSTRUCTION_ACTIVE` transition,
- every later transition must continue the exact prior state and causal time
  chain, and
- the recomputed snapshot and transition IDs must exactly match the supplied
  IDs.

No `DealingRangeSwing` or `DealingRangeStructureEvent` object is supplied to this
API. The future module therefore must not claim to re-prove:

- existence of an upstream swing or structure-event object,
- whether a member swing was truly HIGH or LOW,
- the upstream semantic role of the protected swing among otherwise valid source
  IDs, or
- an event foreign key beyond hash shape and snapshot-local transition
  consistency.

Those facts are accepted as immutable upstream Dealing Range evidence. Proving
them again would require additional inputs and is outside this exact API. The
future module must independently fail closed if any required snapshot-local
field, hash shape, tuple relationship, boundary, midpoint, provenance, state,
transition chain, or recomputable canonical ID is missing, malformed,
contradictory, or internally inconsistent. It must not leak `AttributeError`,
`KeyError`, `IndexError`, enum, Decimal, or timestamp exceptions from internally
malformed frozen instances.

Only a canonical snapshot satisfying all of the following is eligible for zone
construction:

- `kind=EXTERNAL`,
- `state=ACTIVE`,
- direction is exactly `BULLISH` or `BEARISH`,
- `lineage_id`, `protected_swing_id`, and `construction_event_id` are present
  valid lowercase 64-character SHA-256 identities,
- `low_tick < high_tick`,
- `midpoint_tick == (Decimal(low_tick) + Decimal(high_tick)) / Decimal(2)`, and
- its effective moment and lifecycle history satisfy Section 7.4.

Canonical `INTERNAL`, `SUPERSEDED`, and `INVALIDATED` snapshots are valid input
evidence but are never eligible current zone contexts. They must not be silently
converted to active external ranges.

### 7.4 Range Effective Moment and Causal Tuple Order

The effective moment of an `ACTIVE` external snapshot is its normalized
`first_known_provenance.confirmation_index` and confirmation timestamp.

For a `SUPERSEDED` or `INVALIDATED` external snapshot:

- at least one transition must exist,
- the last transition must have the matching terminal state,
- its index and normalized timestamp are the snapshot's effective moment, and
- its prior transition history must be an exact immutable prefix of the earlier
  same-lineage snapshot history.

The supplied range tuple must be nondecreasing by effective moment. Equal
effective moments must follow causal order:

1. an old lineage's `SUPERSEDED` or `INVALIDATED` terminal snapshot,
2. then a replacement or reverse-CHOCH lineage's `ACTIVE` snapshot.

For same-lineage `ACTIVE` revisions at one effective moment, the later supplied
revision must be an exact causal extension of prior source and transition
evidence. Direction, lineage ID, snapshot ID, and hash lexical order are not
chronology tie-breakers.

The analyzer must reject a causally out-of-order tuple as `INVALID`. It must not
silently sort, deduplicate, reorder by hash, or select a favorable snapshot.

## 8. Locked Zone Semantics

`PremiumDiscountZone` is a string enum with exactly:

- `DISCOUNT`
- `EQUILIBRIUM`
- `PREMIUM`

For one eligible active external range:

- `low_tick` and `high_tick` are the immutable current range boundaries,
- `equilibrium_tick` is the exact arithmetic midpoint,
- the closed interval from `low_tick` through `high_tick` is the only eligible
  classification domain,
- a price strictly below Equilibrium and inside the range is `DISCOUNT`,
- a price exactly equal to Equilibrium is `EQUILIBRIUM`,
- a price strictly above Equilibrium and inside the range is `PREMIUM`, and
- a price below the range low or above the range high produces no
  classification.

The zone names express location within one range. They do not express order side,
trade side, expected return, confidence, trend, reversal probability, entry
quality, or readiness.

## 9. Locked Active External Range Selection

At each effective moment, the analyzer holds at most one current active external
range.

- An `ACTIVE` external snapshot establishes or revises its lineage.
- A later `SUPERSEDED` or `INVALIDATED` snapshot terminates that lineage.
- A terminal snapshot cannot remain active after its effective moment.
- A new lineage may become active only through a supplied canonical `ACTIVE`
  snapshot.
- Internal ranges never replace the current external range.
- A missing active external range produces no classification.

Two unrelated, individually canonical active external ranges at the same
effective moment, without a locked terminal-to-replacement relationship, are
`AMBIGUOUS`. The analyzer must not choose by direction, tighter range, recency
within the same moment, input hash, source count, or favorable price location.

If one item in an effective group is malformed or contradictory, the complete
group is `INVALID` and nothing from that group is promoted. Earlier valid
snapshots remain immutable evidence.

## 10. Locked Decimal Midpoint, Boundary, and Outside-Range Rules

Equilibrium is calculated exactly as:

```python
(Decimal(low_tick) + Decimal(high_tick)) / Decimal(2)
```

No float conversion, epsilon, rounding, tick snapping, quantization, or tolerance
is allowed after integer-tick input validation.

Consequences:

- an even tick span has an integer-tick Equilibrium that an observation may equal,
- an odd tick span has a half-tick Equilibrium that an integer-tick observation
  can never equal,
- for a half-tick Equilibrium, the adjacent lower integer tick is Discount and
  the adjacent upper integer tick is Premium,
- exact `low_tick` is Discount,
- exact `high_tick` is Premium, and
- `low_tick == high_tick` is invalid upstream range evidence rather than an
  Equilibrium-only range.

An outside-range observation produces no classification, snapshot, or invented
zone. If all complete valid observations are outside every eligible active range,
the overall result is `NONE`.

## 11. Locked Direction-as-Context Rule

Every zone set, classification, and emitted snapshot must carry the exact
`BULLISH` or `BEARISH` direction of its active external range.

Direction does not change the location labels:

- below Equilibrium is Discount in both directions,
- equality is Equilibrium in both directions, and
- above Equilibrium is Premium in both directions.

The module must not convert:

- bullish Discount into BUY,
- bearish Premium into SELL,
- Premium into overbought,
- Discount into oversold, or
- Equilibrium into a target or mean-reversion instruction.

Direction is mandatory causal context so that consumers cannot detach the zone
from its Dealing Range. Any later interpretation of direction plus zone is a
separate decision-integration proposal.

## 12. Locked Public API

The proposed public surface is limited to:

- `PREMIUM_DISCOUNT_DETECTOR_VERSION`
- `PremiumDiscountZone`
- `PremiumDiscountObservation`
- `PremiumDiscountZoneSet`
- `PremiumDiscountClassification`
- `PremiumDiscountSnapshot`
- `PremiumDiscountResult`
- `make_premium_discount_id`
- `analyze_premium_discount`

The exact keyword-only analyzer signature is:

```python
def analyze_premium_discount(
    *,
    instrument: str,
    timeframe: str,
    dealing_ranges: tuple[DealingRangeSnapshot, ...] | None,
    observations: tuple[PremiumDiscountObservation, ...] | None,
) -> PremiumDiscountResult:
    ...
```

No public configuration object exists in version 1. Midpoint, boundary,
classification, versioning, and precedence rules are fixed semantics, not
tunable parameters.

The exact keyword-only identity-builder signature is:

```python
def make_premium_discount_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    active_range_lineage_id: str,
    direction: SMCV2Direction,
    source_indices: tuple[int, ...] = (),
    source_swing_ids: tuple[str, ...] = (),
    protected_swing_id: str | None = None,
    construction_event_id: str | None = None,
    boundaries: SMCV2TickRange | None = None,
    equilibrium_tick: Decimal | None = None,
    creation_range_snapshot_id: str | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    current_range_snapshot_id: str | None = None,
    version: int | None = None,
    prior_zone_set_id: str | None = None,
    zone_set_id: str | None = None,
    observation_index: int | None = None,
    observation_timestamp: datetime | None = None,
    price_tick: int | None = None,
    zone: PremiumDiscountZone | None = None,
    classification_id: str | None = None,
) -> str:
    ...
```

Both functions normalize `instrument` and `timeframe` exactly once as
`value.strip().upper()`. Empty normalized values are invalid. Positional calls,
extra public parameters, pandas conversion, file loading, hidden globals, and
environment configuration are forbidden.

`PremiumDiscountZoneSet` is frozen and contains exactly:

- `zone_set_id: str`
- `active_range_lineage_id: str`
- `creation_range_snapshot_id: str`
- `direction: SMCV2Direction`
- `source_swing_ids: tuple[str, ...]`
- `source_indices: tuple[int, ...]`
- `protected_swing_id: str`
- `construction_event_id: str`
- `low_tick: int`
- `high_tick: int`
- `equilibrium_tick: Decimal`
- `version: int`
- `first_known_index: int`
- `first_known_timestamp: datetime`
- `prior_zone_set_id: str | None`

`creation_range_snapshot_id` is immutable creation context. A later active range
snapshot that does not materially change the zone set does not rewrite it.
`first_known_index` and `first_known_timestamp` are the exact normalized
first-known provenance of that creation range snapshot and are immutable with the
zone-set version.

`PremiumDiscountClassification` is frozen and contains exactly:

- `classification_id: str`
- `zone_set_id: str`
- `active_range_lineage_id: str`
- `active_range_snapshot_id: str`
- `direction: SMCV2Direction`
- `zone_set_version: int`
- `observation_index: int`
- `observation_timestamp: datetime`
- `price_tick: int`
- `zone: PremiumDiscountZone`

`PremiumDiscountSnapshot` is frozen and contains exactly:

- `snapshot_id: str`
- `active_range_lineage_id: str`
- `active_range_snapshot_id: str`
- `zone_set_id: str`
- `zone_set_version: int`
- `index: int`
- `timestamp: datetime`
- `classification: PremiumDiscountClassification`
- `classification_id: str`

One snapshot represents one valid inside-range classification. Outside-range
observations emit no classification or snapshot.

`PremiumDiscountResult` is frozen and contains exactly:

- `status: SMCV2PrimitiveStatus`
- `zone_sets: tuple[PremiumDiscountZoneSet, ...] = ()`
- `classifications: tuple[PremiumDiscountClassification, ...] = ()`
- `snapshots: tuple[PremiumDiscountSnapshot, ...] = ()`
- `reasons: tuple[str, ...] = ()`
- `blocking_reasons: tuple[str, ...] = ()`

The object tuples are chronological immutable evidence. Every exposed object ID
must exactly reproduce from the public identity builder.

## 13. Locked Deterministic Identity Contract

`PREMIUM_DISCOUNT_DETECTOR_VERSION` is exactly
`SMC-V2-PREMIUM-DISCOUNT-1`.

The only identity kinds are:

- `ZONE_SET`
- `CLASSIFICATION`
- `SNAPSHOT`

Each ID is a lowercase SHA-256 hex digest of one canonical JSON payload with:

- sorted keys,
- compact separators,
- UTF-8 encoding,
- normalized uppercase instrument and timeframe,
- exact case-sensitive enum values,
- normalized UTC timestamps serialized as
  `YYYY-MM-DDTHH:MM:SS.ffffffZ`,
- integer ticks serialized as integers,
- Equilibrium serialized as a canonical Decimal string ending in `.0` or `.5`,
  and
- ordered tuples serialized without sorting or deduplication.

Every identity-builder parameter is required or forbidden by identity kind as
defined below. There is no partially ignored parameter.

The public builder validates type, normalization, exact required/forbidden
parameters, payload-local arithmetic, and any referenced identity that can be
recomputed entirely from its supplied arguments. It never resolves a SHA-256
foreign key into an object. The analyzer performs cross-object reconciliation
against the supplied `DealingRangeSnapshot` objects and its analyzer-created
`PremiumDiscountZoneSet` and `PremiumDiscountClassification` objects before
calling the builder.

### 13.1 `ZONE_SET`

`ZONE_SET` requires:

- one valid active external range lineage ID,
- `direction` exactly `BULLISH` or `BEARISH`,
- a strictly increasing `source_indices` tuple containing at least two members,
- an ordered `source_swing_ids` tuple of the same length containing unique valid
  hashes,
- valid `protected_swing_id` and `construction_event_id`,
- `protected_swing_id` present exactly once in `source_swing_ids`,
- valid `boundaries` with `lower_tick < upper_tick`,
- exact `equilibrium_tick`,
- valid `creation_range_snapshot_id`,
- non-negative `first_known_index`,
- normalized `first_known_timestamp`,
- positive integer `version`, and
- `prior_zone_set_id=None` for version `1`, otherwise one valid prior zone-set ID.

The analyzer requires `first_known_index` and normalized
`first_known_timestamp` to exactly match the creation
`DealingRangeSnapshot.first_known_provenance`. The public identity builder includes
both values in the canonical `ZONE_SET` payload. Equivalent timezone-aware
representations of the same UTC instant therefore produce the same ID; a
different instant or index produces a different ID.

`ZONE_SET` requires these exact defaults for remaining parameters:

- `current_range_snapshot_id=None`
- `zone_set_id=None`
- `observation_index=None`
- `observation_timestamp=None`
- `price_tick=None`
- `zone=None`
- `classification_id=None`

The payload includes all required causal source evidence. A zone-set ID does not
depend on a later unchanged current range snapshot ID.

### 13.2 `CLASSIFICATION`

`CLASSIFICATION` requires:

- one valid active external range lineage ID,
- `direction` exactly matching the active range,
- valid `current_range_snapshot_id`,
- valid `zone_set_id`,
- valid `boundaries` with `lower_tick < upper_tick`,
- exact `equilibrium_tick`,
- non-negative `observation_index`,
- normalized `observation_timestamp`,
- one integer `price_tick`,
- one exact `PremiumDiscountZone`, and
- `version` equal to the referenced positive zone-set version.

`CLASSIFICATION` requires these exact defaults for remaining parameters:

- `source_indices=()`
- `source_swing_ids=()`
- `protected_swing_id=None`
- `construction_event_id=None`
- `creation_range_snapshot_id=None`
- `first_known_index=None`
- `first_known_timestamp=None`
- `prior_zone_set_id=None`
- `classification_id=None`

The public builder validates `price_tick` and `zone` directly against its supplied
boundaries and Equilibrium and rejects an outside-range price. The analyzer
additionally requires those boundaries and Equilibrium to exactly match the
referenced `PremiumDiscountZoneSet`. The builder does not resolve a zone-set
object from its hash.

### 13.3 `SNAPSHOT`

`SNAPSHOT` requires:

- one valid active external range lineage ID,
- `direction` exactly matching the current range,
- valid `current_range_snapshot_id`,
- valid `zone_set_id`,
- valid `boundaries` with `lower_tick < upper_tick`,
- exact `equilibrium_tick`,
- non-negative `observation_index`,
- normalized `observation_timestamp`,
- one integer `price_tick`,
- one exact `PremiumDiscountZone`,
- valid `classification_id`, and
- `version` equal to the referenced positive zone-set version.

`SNAPSHOT` requires these exact defaults for remaining parameters:

- `source_indices=()`
- `source_swing_ids=()`
- `protected_swing_id=None`
- `construction_event_id=None`
- `creation_range_snapshot_id=None`
- `first_known_index=None`
- `first_known_timestamp=None`
- `prior_zone_set_id=None`

The public builder first validates the supplied price and zone against the
supplied boundaries and Equilibrium. It then recomputes the exact
`CLASSIFICATION` identity from instrument, timeframe, active range lineage,
direction, current range snapshot, zone-set ID, version, boundaries,
Equilibrium, observation moment, price, and zone. The supplied
`classification_id` must exactly match that recomputed identity before the
`SNAPSHOT` ID is created. The analyzer additionally requires the supplied context
to exactly match the referenced classification and zone-set objects. No identity
kind accepts free-form reason text.

Unknown kinds, missing required parameters, forbidden non-default parameters,
malformed hashes, invalid versions, inconsistent Decimal values, invalid enums,
or payload-locally impossible combinations raise only `TypeError` or `ValueError`
from the public builder. Cross-object mismatches that cannot be resolved from
builder arguments are `INVALID` in the analyzer. The analyzer catches
required-input identity failures and returns `INVALID` without leaking internal
exceptions.

## 14. Locked Immutable Zone-Set Versioning and Lifecycle

Zone-set history is keyed by active external range lineage.

- The first material zone set for one lineage has version `1`.
- A materially changed later `ACTIVE` snapshot for the same lineage creates the
  next integer version and links the exact prior zone-set ID.
- Material evidence consists exactly of direction, ordered source swing IDs,
  ordered source indices, protected swing ID, construction event ID, low tick,
  high tick, and exact Equilibrium.
- A changed current `DealingRangeSnapshot.snapshot_id` alone is not material.
- An identical material zone-set payload reuses the prior zone-set ID, version,
  and immutable creation range snapshot ID.
- A changed boundary necessarily changes Equilibrium and creates a new version.
- A source-evidence change creates a new version even if boundaries are
  unchanged.
- A changed lineage begins a separate version-1 history.

The zone module creates no independent mutable lifecycle event. Zone-set
eligibility mirrors the supplied external Dealing Range lifecycle:

- `ACTIVE` makes the current version eligible,
- `SUPERSEDED` terminates old-lineage eligibility,
- `INVALIDATED` terminates old-lineage eligibility, and
- a replacement `ACTIVE` snapshot establishes a new current lineage.

Past zone sets, classifications, and snapshots are never mutated, removed,
reordered, relabeled, or assigned to a later range context. A later range
revision never reclassifies an earlier observation.

## 15. Locked Chronology and Same-Index Processing Precedence

The caller-supplied range and observation tuples must already satisfy their
locked causal order. The analyzer rejects invalid order and never silently sorts.

All range snapshots and observations sharing an effective index and normalized
timestamp form one atomic group. The full group is validated before state
mutation or output.

All causal records already known for one effective moment must be supplied as one
complete atomic group. The caller must not present a group as complete and then
append another range revision or observation at that same or an earlier effective
moment in a later prefix. Same-effective causal records may coexist in one input
only under the locked order below.

The exact same-group processing order is:

1. capture immutable pre-group active range, zone-set histories, classifications,
   and snapshots,
2. validate every range snapshot, transition, identity, lifecycle relationship,
   and observation in the group,
3. apply an old lineage's `SUPERSEDED` or `INVALIDATED` terminal snapshot,
4. apply at most one causally valid new or revised `ACTIVE` external snapshot,
5. ignore canonical internal snapshots for current-zone eligibility,
6. resolve or reuse the exact material zone-set version,
7. classify the same-group observation against the post-transition active range,
8. emit at most one classification and one snapshot for that observation, and
9. preserve all earlier evidence byte-for-byte.

Therefore:

- an observation at an initial range-construction moment may use that fully known
  new `ACTIVE` range,
- an observation at old-lineage termination without a replacement has no active
  range and emits nothing,
- an observation at terminal-old plus replacement-new evidence uses only the new
  post-transition range,
- an observation cannot be classified under both old and new ranges, and
- a malformed or ambiguous group produces no same-group partial promotion.

A duplicate observation index or duplicate normalized observation timestamp is
`INVALID`, including when the other field differs. If two unrelated active
external ranges survive one group, the result is `AMBIGUOUS`. Hash, direction,
range width, price location, and input order among unrelated candidates cannot
resolve ambiguity.

## 16. Locked Result Status Semantics

- `VALID`: at least one valid inside-range classification and corresponding
  snapshot is emitted.
- `NONE`: both top-level contexts are complete and valid, but no observation is
  classifiable inside an eligible active external range.
- `UNKNOWN`: at least one required top-level context is `None`.
- `AMBIGUOUS`: complete individually valid inputs yield multiple unrelated
  active external range candidates at one effective moment without a causal
  lifecycle relationship.
- `INVALID`: malformed type, enum, hash, provenance, Decimal midpoint, tick,
  chronology, lifecycle, transition, snapshot, identity, duplicate,
  contradiction, or required field is present.

An empty supplied tuple is complete context. Empty ranges or observations produce
`NONE`, not `UNKNOWN`. An internal or terminal range by itself is valid historical
input but does not create an eligible zone.

Top-level missing context is checked first and returns `UNKNOWN` without partial
analysis. For complete inputs, precedence is `INVALID`, then `AMBIGUOUS`, then
`VALID`, then `NONE`.

Valid objects strictly before a later failing effective group remain immutable
evidence in an `INVALID` or `AMBIGUOUS` result. Nothing from the failing group or
after it is promoted.

## 17. Locked Prefix-Invariance Contract

Every classification uses only a fully validated range and observation knowable
at its observation moment.

A prefix is eligible for a prefix-invariance comparison only when it ends after a
complete effective group. Every range snapshot and observation appended for the
longer comparison must have an effective moment strictly later than the last
effective moment in that complete prefix. Appending a same-effective or earlier
record is not a future-prefix extension; it violates the caller contract and is
`INVALID`.

For any such valid complete-group prefix, appending strictly later ranges or
observations must preserve every previously emitted zone set, classification,
snapshot, ID, version, timestamp, price, zone, and order byte-for-byte.

Later evidence may:

- append a materially changed zone-set version,
- terminate an old range,
- establish a new range lineage, and
- append new classifications and snapshots.

Later evidence may not:

- change a past Discount, Equilibrium, or Premium label,
- attach a past observation to a newer range snapshot,
- rewrite a zone-set creation context,
- reorder equal-moment causal range evidence,
- fill an earlier missing range using future information, or
- reinterpret direction as a trade signal.

Repeated analysis of identical immutable inputs must produce dataclass-equal
results and byte-identical canonical identity payloads.

## 18. Locked Inline Synthetic 36-Case Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
exactly these numbered logical cases, with parameterization allowed:

1. Bullish active external range classifies an inside price below Equilibrium as
   `DISCOUNT`.
2. Bullish active external range classifies exact integer-tick midpoint equality
   as `EQUILIBRIUM`.
3. Bullish active external range classifies an inside price above Equilibrium as
   `PREMIUM`.
4. Bearish active external range classifies below, equal, and above prices with
   the same location labels while carrying `BEARISH` context.
5. Direction never inverts zone labels or produces BUY, SELL, bias, confidence,
   or readiness output.
6. Exact low boundary is `DISCOUNT` and exact high boundary is `PREMIUM`.
7. One tick below the range and one tick above the range are outside and omitted.
8. Complete valid observations all outside the range return `NONE`.
9. Even range span produces exact integer-tick Equilibrium.
10. Odd range span produces exact half-tick Equilibrium; adjacent integer ticks
    classify Discount and Premium with no possible equality.
11. Negative, zero, and positive integer tick values preserve exact Decimal
    arithmetic without float conversion.
12. Zero-width, reversed, or midpoint-inconsistent range evidence returns
    `INVALID`.
13. `dealing_ranges=None` and `observations=None` each return `UNKNOWN` without
    partial promotion.
14. Complete empty range and observation tuples return `NONE`.
15. Canonical internal-only, superseded-only, and invalidated-only range context
    returns `NONE`.
16. Initial canonical `ACTIVE` external range is usable exactly at its
    first-known construction moment.
17. Terminal old range without replacement precedes a same-moment observation,
    leaving no eligible range and no classification.
18. Same-moment old terminal then new `ACTIVE` replacement classifies only under
    the new range for both bullish-to-bearish and bearish-to-bullish reversals.
19. Same-lineage unchanged active revision reuses zone-set ID, version, and
    immutable creation range snapshot context.
20. Same-lineage material boundary extension creates exactly one next zone-set
    version with recalculated exact Equilibrium and prior ID link.
21. Same-lineage source-identity change with unchanged boundaries creates the
    next version, while a current snapshot-ID-only change does not.
22. New range lineage begins an independent version-1 zone set and leaves prior
    lineage evidence immutable.
23. Two unrelated valid active external ranges at one effective moment return
    `AMBIGUOUS` with no same-group output, independent of direction and hash
    order.
24. One malformed item in a same-moment group returns `INVALID` with no
    same-group classification or snapshot.
25. Missing, wrong-type, and internally malformed observation required fields,
    duplicate indices with different timestamps, and duplicate normalized
    timestamps with different indices return `INVALID` without exception leakage.
26. Missing, wrong-type, and internally malformed Dealing Range required fields
    return `INVALID` without exception leakage.
27. Malformed snapshot-local hash shapes, unequal or fewer-than-two source ID and
    index tuples, a protected ID absent from source IDs, mismatched transition ID
    tuples, broken transition chains, and recomputable snapshot or transition ID
    mismatches return `INVALID`; no unavailable upstream swing/event existence or
    protected-side role is claimed to be re-proved.
28. Duplicate observations, duplicate snapshot identities, contradictory
    same-lineage revisions, and impossible lifecycle transitions return
    `INVALID`.
29. Independently non-increasing observation indices or timestamps, causally
    out-of-order range tuples, and same-effective or earlier append attempts
    after a complete prefix return `INVALID` without silent sorting or
    hash-based chronology.
30. `ZONE_SET` identity is deterministic, source-aware, direction-aware,
    boundary-aware, version-aware, normalized by instrument/timeframe, binds the
    exact first-known index and UTC-normalized timestamp, requires equal
    source-ID/source-index tuple lengths of at least two, and enforces its exact
    required/forbidden schema.
31. `CLASSIFICATION` identity is deterministic across equivalent UTC timestamps,
    carries exact range direction and current snapshot context, requires
    boundaries and Equilibrium, and rejects an outside price, price/zone mismatch,
    zone-set object mismatch in the analyzer, or forbidden parameter.
32. `SNAPSHOT` identity requires price and zone, recomputes and exact-matches the
    referenced `CLASSIFICATION` ID, binds that classification to its current
    range and observation moment, and rejects object-context mismatches or
    forbidden fields.
33. Identity-builder exact keyword-only signature including first-known fields,
    canonical Decimal `.0`/`.5` serialization, equivalent UTC normalization,
    exact enum values, malformed-hash rejection, and unknown-kind rejection are
    enforced.
34. All public dataclasses are frozen with exact fields, public analyzer and
    identity-builder signatures are keyword-only, and exports are exact.
35. Identical-run repeatability, complete-effective-group prefix boundaries,
    strictly later appended-future prefix invariance, rejection of same-effective
    append attempts, immutable earlier output after a later invalid group, and
    status precedence are exact.
36. The standalone module has no pandas, raw OHLC, Liquidity Map, v1 SMC, I/O,
    network, configuration, registration, strategy, risk, execution, or
    integration dependency, and focused plus full regression suites pass.

The fixture matrix does not justify an external fixture file. Fixtures must not
contain private market data, candidate OOS values, account details, credentials,
copied generated evidence, or outcome-derived parameters.

## 19. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/dealing_range.py`,
  `smc/liquidity_map.py`, or `smc/__init__.py`,
- edits to or imports from legacy `smc/liquidity_sweep.py`,
- importing Liquidity Map output, pandas, raw OHLC analyzers,
  `smc/market_structure.py`, `smc/bos_choch.py`, current SMC context, or another
  current production analyzer,
- swing, BOS, CHOCH, or Dealing Range construction or upstream lifecycle
  mutation,
- Fibonacci, FVG, Order Block, Mitigation Block, Breaker Block, Inducement,
  kill-zone, Volume Profile, or context-aggregation code,
- runtime flags, CLI, runner, adapter, context, trace, package-registration, or
  decision-path wiring,
- current SMC, CRT, Order Flow, DecisionContext, confidence, action, risk,
  sizing, stop, target, entry, exit, balance, or PnL changes,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- tuning, optimization, favorable reruns, or use of saved OOS outcomes,
- private data, generated reports, external evidence, or Fibonacci analysis, and
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
   invariants, 36-case matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only the exact three-path task.

Passing this documentation decision is insufficient to begin coding.

## 21. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target already exists,
- any dependency hash or parent commit differs without a separately reviewed
  checkpoint,
- another tracked, staged, unstaged, ignored-generated, or untracked file appears,
- another path appears necessary,
- raw OHLC, pandas, Liquidity Map output, a v1 analyzer, an adapter, or integration
  appears necessary,
- one active external range cannot be selected without hindsight,
- exact Decimal integer/half-tick Equilibrium cannot be preserved,
- direction cannot remain mandatory non-signal context,
- same-index old-terminal-before-new-active precedence cannot be preserved,
- complete effective-group boundaries and strictly later prefix extension cannot
  be preserved,
- first-known provenance cannot be bound into zone-set identity,
- price/zone and snapshot/classification identity reconciliation cannot remain
  deterministic without resolving hidden state,
- immutable versioning, deterministic identity, or prefix invariance cannot be
  demonstrated,
- a private, candidate, performance, generated, or external fixture appears
  necessary,
- an existing public interface, default output, or execution path changes,
- focused tests or the full regression suite fail, or
- implementation appears necessary to resolve an ambiguity in this record.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, rounding, or an implementation shortcut.

## 22. Completion, Rollback, and Promotion Gates

Later implementation completion requires:

- independent review of every changed line,
- exact three-path reconciliation,
- all 36 numbered logical test cases passing,
- the full regression suite passing,
- deterministic zone-set, classification, and snapshot identity evidence,
- exact midpoint, boundary, direction-context, lifecycle, same-index, versioning,
  fail-closed, and prefix-invariance evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed Premium/Discount checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and clean-scope
audit. Existing v1 and completed dependency files remain intact.

Successful implementation would prove only standalone deterministic
Premium/Equilibrium/Discount conformance. It would not prove trading edge, OOS
improvement, strategy value, readiness, threshold approval, paper approval, live
approval, or permission for FVG or any later phase.

## 23. Global Freeze and Next-Phase Boundary

The global code freeze remains active. This decision reserves one possible
future Premium, Equilibrium, and Discount task only. It does not authorize FVG,
Order Block, Mitigation Block, Breaker Block, Inducement, kill zones, Volume
Profile, context aggregation, trace integration, or decision integration.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=PREMIUM_EQUILIBRIUM_DISCOUNT_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `RESERVED_IMPLEMENTATION_PATHS=3`
- `INLINE_SYNTHETIC_TEST_CASES=36`
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
