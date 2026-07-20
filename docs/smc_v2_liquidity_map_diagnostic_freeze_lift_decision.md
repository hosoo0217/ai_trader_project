# SMC v2 Internal and External Liquidity Map Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-LIQUIDITY-MAP-FREEZE-LIFT-DECISION-2026-07-20`.
- Parent review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Parent specification ID: `SMC-V2-VP-SPEC-2026-07-19`.
- Implementation-order phase: `4 - INTERNAL AND EXTERNAL LIQUIDITY MAPPING`.
- Implementation parent commit:
  `a20a6ad7c315d44e99358ffe1f18a90b5a18071b`.
- Requested module: standalone Internal and External Liquidity Map diagnostics.
- Current task type: documentation-only formal decision record.
- Decision classification:
  `APPROVED - DOCUMENTATION DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`.
- Global code-freeze status: `ACTIVE`.
- Python implementation authorized by this record: `False`.
- Test or fixture change authorized by this record: `False`.
- Integration authorized by this record: `False`.
- Staging, commit, or push authorized by this record: `False`.

This record reserves and specifies one possible future Internal and External
Liquidity Mapping task. It does not make the bounded exception operational,
authorize code, or transfer authority from any completed dependency task.

## 2. Effective-State Interpretation

The accepted implementation order is:

1. Shared primitives and test helpers.
2. Equal High and Equal Low.
3. Swing Hierarchy and Dealing Range.
4. Internal and External liquidity mapping.
5. Premium, Equilibrium, and Discount.

The first three phases are committed, pushed, and independently checkpointed.
Their completion satisfies the dependency gate for this documentation decision
only. It does not automatically authorize phase-four Python implementation.

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

## 3. Locked Decision Inputs

This decision is derived from the accepted planning package and completed
dependencies:

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
- `docs/smc_v2_dealing_range_diagnostic_freeze_lift_decision.md`
  - SHA-256:
    `3E629DE15D261CC5D7C2FEE95D205951CFAB71399AB7F35F887578E223E34D1A`
- `smc/dealing_range.py`
  - SHA-256:
    `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`
- `tests/test_dealing_range.py`
  - SHA-256:
    `A6DD0C03BEA9C6091F8E9EAC267930187C99B8F80C386EC52E2A0D91110B36CF`
- `docs/smc_v2_dealing_range_checkpoint.md`
  - SHA-256:
    `F01E781E5CEB55AF22F25823E0DFDDFA305090474F7E0111D57FFCE67445FE66`

The phase-three post-push completion audit confirmed:

- local `HEAD`, local `origin/main`, and live remote `main` at
  `a20a6ad7c315d44e99358ffe1f18a90b5a18071b`,
- `55` focused Dealing Range tests passing,
- `1061` full regression tests passing,
- exact three-file implementation scope, and
- no staged, unstaged, or untracked paths.

These facts establish dependency and compatibility state only. They are not
performance evidence and do not authorize integration.

## 4. Exact Change Authorized in This Documentation Task

The only repository path authorized for creation or modification now is:

- `docs/smc_v2_liquidity_map_diagnostic_freeze_lift_decision.md`

No Python, test, fixture, configuration, package export, existing documentation,
external evidence, or generated report may change in this task. Staging, commit,
push, implementation, detector execution, and integration remain separate gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If a later implementation preflight and explicit human authorization pass, the
future task is reserved to exactly these three paths:

- production module: `smc/liquidity_map.py`
- dedicated unit tests: `tests/test_liquidity_map.py`
- implementation checkpoint: `docs/smc_v2_liquidity_map_checkpoint.md`

All fixtures must be synthetic and inline in the dedicated test file. No fixture
file is reserved or authorized by this record.

The later task must not edit `smc/__init__.py`, `smc/smc_v2_primitives.py`,
`smc/equal_liquidity.py`, `smc/dealing_range.py`, or any existing SMC v1 module.
Direct imports of the completed immutable dependency types are sufficient. Any
need for another path is a stop condition requiring a new scope review and
explicit human approval before that edit occurs.

## 6. Exact Functional Boundary

The future standalone module may implement only:

- validation and chronological consumption of immutable, already-confirmed
  `DealingRangeSwing` values,
- validation and chronological consumption of immutable `EqualLiquidityPool`
  snapshots,
- validation and chronological consumption of immutable `DealingRangeSnapshot`
  values,
- selection of one active external Dealing Range context at each known index,
- deterministic `BUY_SIDE` and `SELL_SIDE` classification,
- deterministic `INTERNAL` and `EXTERNAL` scope classification,
- explicit swing, Equal Liquidity pool, and range-boundary source kinds,
- strict-boundary Internal Liquidity classification,
- immutable classification versioning and scope reclassification evidence,
- deterministic map, boundary, classification, snapshot, and reclassification
  identities,
- explicit valid, invalid, unknown, none, and ambiguous results, and
- pure prefix-invariant analysis over immutable tuples.

The module must not detect raw swings, construct Equal Liquidity pools, construct
or mutate Dealing Ranges, detect sweeps from raw OHLC, or repair upstream data.
It consumes completed diagnostic outputs under the contracts below. A future
adapter or result-to-result pipeline is an integration task.

The module must not implement Premium, Equilibrium, Discount, FVG, Order Block,
Mitigation Block, Breaker Block, Inducement, kill zones, Volume Profile,
confidence, signals, trade filtering, risk, sizing, or execution.

## 7. Locked Input Contracts

### 7.1 Top-Level Contract

The exact top-level inputs are:

- `swings: tuple[DealingRangeSwing, ...] | None`
- `equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None`
- `dealing_ranges: tuple[DealingRangeSnapshot, ...] | None`

Each value must be an immutable tuple or `None`. `None` means the caller did not
supply the complete top-level context and returns `UNKNOWN` before partial
analysis. An empty tuple is complete supplied context and is not missing data.

No `EqualLiquidityResult` or `DealingRangeResult` is accepted. The caller must
pass their immutable snapshot tuples explicitly. Status propagation between
analyzers is future integration and is outside this standalone API.

### 7.2 Confirmed Subordinate-Swing Contract

The `swings` tuple uses the already implemented frozen `DealingRangeSwing` type:

- `side: DealingRangeSwingSide`
- `price_tick: int`
- `provenance: SMCV2EventProvenance`
- `swing_id: str`

`HIGH` maps to `BUY_SIDE`; `LOW` maps to `SELL_SIDE`. This mapping expresses the
side on which resting liquidity is represented. It is not a trading direction,
bias, entry instruction, or expected reversal.

Every swing must:

- have a real integer tick price with booleans rejected,
- contain valid required provenance,
- contain a lowercase 64-character SHA-256 ID,
- be unique by `swing_id`,
- be ordered by the composite key of confirmation index, normalized
  confirmation timestamp, side value, and swing ID, and
- be consistent with every pool or range foreign-key reference to that swing.

The tuple may contain range-defining and subordinate confirmed swings. The
mapping module does not rediscover hierarchy visually. It derives hierarchy only
from the active external range identity and strict price location.

### 7.3 Equal Liquidity Pool Contract

The `equal_liquidity_pools` tuple uses the already implemented frozen
`EqualLiquidityPool` type. Every pool snapshot must preserve:

- side,
- lineage and snapshot IDs,
- ordered member swing IDs and source indices,
- reference, lower, and upper ticks,
- first-known provenance,
- lifecycle state, and
- ordered lifecycle events.

Every member swing ID must resolve to exactly one supplied `DealingRangeSwing`.
An Equal High pool requires all resolved member swings to be `HIGH` and maps to
`BUY_SIDE`. An Equal Low pool requires all resolved member swings to be `LOW`
and maps to `SELL_SIDE`. Source indices, prices, side, reference band, and
provenance must agree across the supplied snapshots and resolved swings.

Multiple immutable snapshots of one pool lineage are allowed. The complete pool
tuple must be nondecreasing by effective index and normalized effective
timestamp. All snapshots sharing that effective moment form one atomic group;
`side`, `lineage_id`, and `snapshot_id` identify and group evidence but are not
chronology tie-breakers.

Within one equal-effective-moment, equal-side, equal-lineage group, membership
revisions have one locked causal order:

- each later `ACTIVE` membership revision has a strictly larger member count,
- its ordered `member_swing_ids` and `source_indices` retain the complete prior
  tuples as exact prefixes and append only newly confirmed members,
- every retained member identity and provenance remains unchanged, prior
  lifecycle events remain an exact prefix, the revised reference/band is the
  exact upstream recomputation for the extended membership, and every prior
  snapshot remains byte-for-byte immutable, and
- any same-moment `SWEPT` or `BROKEN` terminal revision follows the applicable
  `ACTIVE` membership revisions and retains their final membership.

An equal-moment revision that removes, rewrites, reorders, or non-prefix-extends
membership is `INVALID`. Canonical snapshot IDs may be lexicographically
decreasing across a valid causal revision sequence; the analyzer validates each
ID against its content but must not use the hash value to infer chronology.

For one pool snapshot, each resolved member swing has the exact confirmation
composite key:

`(confirmation_index, normalized confirmation_timestamp, source_index, swing_id)`

The latest-member key is the maximum of those member keys. Its first two fields
define the latest-member effective moment. Effective time is locked as follows:

- an `ACTIVE` pool snapshot uses the latest-member effective moment, including a
  later-member join that changes membership, reference tick, or band,
- a `SWEPT` or `BROKEN` terminal pool snapshot uses the later of the latest-member
  effective moment and the last lifecycle event's index and normalized
  timestamp, and
- when those two moments are equal, terminal lifecycle evaluation has
  precedence while the effective index and timestamp remain equal.

The initial two-member formation snapshot's latest-member effective moment must
equal its `first_known_provenance` confirmation moment. A later-member `ACTIVE`
snapshot must not be backdated to that initial first-known moment or initial
`None -> ACTIVE` lifecycle event. Snapshot IDs may not repeat with different
content, and a later snapshot may not remove or alter prior lifecycle evidence.

Only the latest known `ACTIVE` snapshot of a pool lineage is eligible for a
current liquidity-map snapshot. `SWEPT` and `BROKEN` pools remain immutable
historical evidence but are not current Internal Liquidity. The mapping module
does not reinterpret or create pool lifecycle events.

### 7.4 Dealing Range Snapshot Contract

The `dealing_ranges` tuple uses the already implemented frozen
`DealingRangeSnapshot` type. All external and internal snapshots may be supplied,
but only `kind=EXTERNAL` can create or replace the active liquidity-map context.
An `INTERNAL` range is validated and preserved as upstream evidence; it does not
replace the active external range and does not independently create map sources.

An external range snapshot must retain its valid lineage, protected swing,
construction event, state, transition tuple, transition IDs, source swing IDs,
integer boundaries, exact midpoint, and first-known provenance. Every referenced
swing ID must resolve to exactly one supplied `DealingRangeSwing` with matching
side, price, source identity, and provenance where the range contract requires
that relationship.

Every external or internal Dealing Range snapshot uses exactly its
`first_known_provenance.confirmation_index` and normalized
`first_known_provenance.confirmation_timestamp` as its effective moment. The
complete range tuple must be nondecreasing by effective index and normalized
effective timestamp. All snapshots sharing that moment form one atomic group;
range kind, direction, optional lineage ID, and snapshot ID validate identity
and lifecycle relationships but are not chronology tie-breakers.

Within one equal-effective-moment group, a replacement or reverse-CHOCH causal
chain has one locked supplied order: the old external lineage's exactly one
`SUPERSEDED` or `INVALIDATED` terminal snapshot comes first, and the replacement
lineage's `ACTIVE` snapshot comes strictly after it. This precedence applies in
both bullish-to-bearish and bearish-to-bullish reversals regardless of direction
text, lineage-ID order, or snapshot-hash order. A new `ACTIVE` replacement placed
before its required old-lineage terminal is `INVALID`; the analyzer must not
silently reorder it. Unrelated same-moment internal evidence has no authority to
alter this external causal chain.

For a `SUPERSEDED` or `INVALIDATED` external snapshot, the final transition index
and normalized timestamp must exactly equal that snapshot's effective moment.
For an initial or replacement `ACTIVE` external snapshot, its `None -> ACTIVE`
transition must match its effective moment. A later same-lineage `ACTIVE`
extension is permitted to have no new transition: its effective moment still
comes from the extension snapshot's new `first_known_provenance`, while its last
transition may remain the earlier construction transition. Such an extension
must retain the lineage and protected boundary and must contain the upstream
snapshot changes required by the locked Dealing Range extension contract.

Prior snapshots must be byte-for-byte immutable.

At the end of one effective-index group, at most one valid external range may be
`ACTIVE`. A valid `SUPERSEDED` or `INVALIDATED` snapshot terminates that lineage.
Contradictory snapshots of one lineage are `INVALID`. Two independently valid,
unrelated external lineages that both claim active status at the same effective
index and timestamp are `AMBIGUOUS` and produce no partial same-index map
snapshot. A later unrelated lineage claiming active status while an earlier
lineage remains active without a valid same-index terminal or replacement link
is a contradictory chronology and is `INVALID`, not `AMBIGUOUS`. These outcomes
do not depend on the supplied direction, lineage-ID, or snapshot-hash lexical
order.

### 7.5 Cross-Source Foreign-Key Contract

IDs are semantic foreign keys, not labels that may be matched by price alone.

- A referenced swing ID absent from a complete supplied swing tuple is
  `INVALID`, not `UNKNOWN`.
- One ID resolving to conflicting side, price, index, timestamp, or provenance
  is `INVALID`.
- An Equal Liquidity member ID and a Dealing Range source ID may refer to the
  same confirmed swing only when their complete shared identity agrees.
- Duplicate IDs, contradictory lineage versions, or silently repaired foreign
  keys are forbidden.

## 8. Locked Side, Scope, and Source Semantics

`LiquiditySide` contains exactly:

- `BUY_SIDE`
- `SELL_SIDE`

`LiquidityScope` contains exactly:

- `INTERNAL`
- `EXTERNAL`

`LiquiditySourceKind` contains exactly:

- `SWING`
- `EQUAL_LIQUIDITY_POOL`
- `RANGE_BOUNDARY`

Stable source IDs are locked as follows:

- a `SWING` source ID is its exact supplied `swing_id`,
- an `EQUAL_LIQUIDITY_POOL` source ID is its stable supplied `lineage_id`, and
- a `RANGE_BOUNDARY` source ID is the canonical `BOUNDARY` identity generated
  for one active range lineage and side.

A pool `snapshot_id` and a range `snapshot_id` are classification context, not
stable source IDs.

Side is independent from range direction:

- a high, upper boundary, or Equal High pool is `BUY_SIDE`, and
- a low, lower boundary, or Equal Low pool is `SELL_SIDE`.

Neither side nor scope is a bullish or bearish recommendation. No automatic
direction, action, confidence, or trade eligibility is emitted.

## 9. Locked Active External Range and Boundary Rules

One valid `ACTIVE` external Dealing Range is the sole classification context.
Without one, complete valid inputs produce `NONE`; the analyzer must not invent a
range from swings or pools.

For every active external range:

- the exact high tick creates one `BUY_SIDE | EXTERNAL | RANGE_BOUNDARY`
  reference,
- the exact low tick creates one `SELL_SIDE | EXTERNAL | RANGE_BOUNDARY`
  reference,
- both boundary references exist regardless of bullish or bearish range
  direction, and
- each boundary source is scoped to that external range lineage, while each
  boundary classification records its immutable creation-context range snapshot
  and the containing map snapshot records the current range snapshot.

A confirmed swing becomes `EXTERNAL` only when all of these hold:

1. its exact swing ID occurs in the active external snapshot's
   `source_swing_ids`,
2. its side matches the corresponding boundary side,
3. its integer price equals that exact boundary tick, and
4. its confirmation provenance is not later than the active range snapshot's
   effective event.

The protected swing must satisfy this relationship. A target-side source swing
may also be External when the same exact identity and boundary requirements
hold. A price match without source-identity linkage is insufficient and must not
promote a subordinate swing to External.

Range-boundary source IDs are stable within one external lineage and side. A
same-lineage target extension creates a new boundary classification version,
not a new map lineage. A replacement or reverse range creates a new map lineage
and new boundary source IDs.

## 10. Locked Strictly-Inside Internal Classification

A supplied confirmed swing is `INTERNAL` only when:

- it is known by the current effective index,
- it is not an exact range-defining External swing under Section 9, and
- `range.low_tick < swing.price_tick < range.high_tick`.

An active Equal Liquidity pool is `INTERNAL` only when its full tolerance band
is strictly inside the active external range:

`range.low_tick < pool.lower_tick <= pool.reference_tick <= pool.upper_tick < range.high_tick`

The following are not Internal:

- a swing exactly equal to either boundary without the exact range-defining
  identity,
- a pool whose lower or upper band equals a boundary,
- a pool whose band crosses a boundary,
- a swing or pool outside the active range,
- a `SWEPT` or `BROKEN` pool, or
- a source not yet known at the current effective index.

Those sources are omitted from the current map. Omission is not automatically
`AMBIGUOUS` or `INVALID`. It becomes `INVALID` only when the input itself violates
a locked contract.

Equal Liquidity pools are Internal-only in this version. A pool touching or
crossing an external boundary does not become External merely because of price.
External equal-pool semantics would require a separately reviewed specification.

## 11. Locked Boundary-Equality and No-Double-Counting Rule

Boundary equality is identity-sensitive:

- the canonical `RANGE_BOUNDARY` reference always represents the boundary,
- an exactly linked range-defining swing may also be classified as External with
  `source_kind=SWING`,
- an unrelated swing at the same price is omitted rather than promoted,
- an Equal Liquidity pool touching the boundary is omitted rather than promoted,
  and
- no source may appear twice under the same source kind, source ID, map ID, and
  classification version.

The boundary record and a linked swing record are not duplicates because they
have different source kinds and preserve different causal evidence. Consumers
must not sum them as independent liquidity quantity; this module provides
classification, not size estimation.

## 12. Locked Public API

The proposed public surface is limited to:

- `LIQUIDITY_MAP_DETECTOR_VERSION`
- `LiquiditySide`
- `LiquidityScope`
- `LiquiditySourceKind`
- `LiquidityClassification`
- `LiquidityReclassification`
- `LiquidityMapSnapshot`
- `LiquidityMapResult`
- `make_liquidity_map_id`
- `analyze_liquidity_map`

The exact keyword-only analyzer signature is:

```python
def analyze_liquidity_map(
    *,
    instrument: str,
    timeframe: str,
    swings: tuple[DealingRangeSwing, ...] | None,
    equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None,
    dealing_ranges: tuple[DealingRangeSnapshot, ...] | None,
) -> LiquidityMapResult:
    ...
```

No public configuration object exists in version 1. Strict-inside behavior,
source kinds, identity rules, and precedence are fixed semantics, not tunable
parameters.

The exact keyword-only identity-builder signature is:

```python
def make_liquidity_map_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    active_range_lineage_id: str,
    source_indices: tuple[int, ...] = (),
    source_kind: LiquiditySourceKind | None = None,
    source_id: str | None = None,
    side: LiquiditySide | None = None,
    scope: LiquidityScope | None = None,
    boundaries: SMCV2TickRange | None = None,
    active_range_snapshot_id: str | None = None,
    version: int | None = None,
    prior_classification_id: str | None = None,
    new_classification_id: str | None = None,
    classification_ids: tuple[str, ...] = (),
    reclassification_ids: tuple[str, ...] = (),
    event_index: int | None = None,
    event_timestamp: datetime | None = None,
    from_scope: LiquidityScope | None = None,
    to_scope: LiquidityScope | None = None,
    reason: str | None = None,
) -> str:
    ...
```

Both functions normalize `instrument` and `timeframe` exactly once as
`value.strip().upper()`. Empty normalized values are invalid. Positional calls,
extra public parameters, pandas conversion, file loading, hidden globals, and
environment configuration are forbidden.

`LiquidityClassification` is frozen and contains exactly:

- `classification_id: str`
- `source_kind: LiquiditySourceKind`
- `source_id: str`
- `side: LiquiditySide`
- `scope: LiquidityScope`
- `source_indices: tuple[int, ...]`
- `boundaries: SMCV2TickRange`
- `active_range_lineage_id: str`
- `active_range_snapshot_id: str`
- `version: int`
- `classification_index: int`
- `classification_timestamp: datetime`
- `prior_classification_id: str | None`

`active_range_snapshot_id` on a classification is the immutable creation
context: it identifies the exact range snapshot under which that classification
version first became known. It is not rewritten to the current range snapshot
when an unchanged classification is reused. The containing
`LiquidityMapSnapshot.active_range_snapshot_id` separately identifies the current
map context.

`LiquidityReclassification` is frozen and contains exactly:

- `reclassification_id: str`
- `source_kind: LiquiditySourceKind`
- `source_id: str`
- `side: LiquiditySide`
- `from_scope: LiquidityScope`
- `to_scope: LiquidityScope`
- `prior_classification_id: str`
- `new_classification_id: str`
- `index: int`
- `timestamp: datetime`
- `reason: str`

`LiquidityMapSnapshot` is frozen and contains exactly:

- `map_id: str`
- `snapshot_id: str`
- `active_range_lineage_id: str`
- `active_range_snapshot_id: str`
- `index: int`
- `timestamp: datetime`
- `classifications: tuple[LiquidityClassification, ...]`
- `classification_ids: tuple[str, ...]`
- `reclassifications: tuple[LiquidityReclassification, ...]`
- `reclassification_ids: tuple[str, ...]`

`classifications` is the complete current eligible classification set for that
map snapshot, with at most one current classification per stable source key.
`reclassifications` contains only scope changes created in that snapshot's
effective group; it is not a cumulative copy of earlier reclassifications. A new
snapshot is emitted only when the active range snapshot, current classification
set, classification version, or event-local reclassification set materially
changes. An unchanged classification may therefore appear in a later map
snapshot while retaining its original classification ID, version, and immutable
creation-context `active_range_snapshot_id`. No-op input versions cannot create
duplicate snapshots.

`LiquidityMapResult` is frozen and contains exactly:

- `status: SMCV2PrimitiveStatus`
- `snapshots: tuple[LiquidityMapSnapshot, ...] = ()`
- `reclassifications: tuple[LiquidityReclassification, ...] = ()`
- `reasons: tuple[str, ...] = ()`
- `blocking_reasons: tuple[str, ...] = ()`

The top-level `reclassifications` tuple is the ordered, duplicate-free union of
all reclassification objects exposed by the emitted snapshots. Its order is by
index, normalized timestamp, source-kind value, source ID, and reclassification
ID. It must not contain an object absent from every snapshot or omit an object
present in a snapshot.

## 13. Locked Deterministic Identity Contract

All IDs are lowercase SHA-256 values generated from canonical JSON with sorted
keys, ASCII encoding, compact separators, no binary floats, and detector version
included. Timestamp inputs pass `normalize_utc_timestamp` and serialize exactly
as `YYYY-MM-DDTHH:MM:SS.ffffffZ`.

Identity kinds are exactly:

- `MAP`
- `BOUNDARY`
- `CLASSIFICATION`
- `SNAPSHOT`
- `RECLASSIFICATION`

Every identity includes normalized instrument, normalized timeframe, identity
kind, and active external range lineage ID. The lineage ID and every other ID
parameter must be lowercase 64-character hexadecimal text. The exact schemas
below account for every optional parameter in `make_liquidity_map_id`; an
unlisted value is never silently accepted.

### 13.1 `MAP`

`MAP` requires only the common instrument, timeframe, identity kind, and active
external range lineage ID. It requires these exact defaults for every remaining
parameter:

- `source_indices=()`
- `source_kind=None`
- `source_id=None`
- `side=None`
- `scope=None`
- `boundaries=None`
- `active_range_snapshot_id=None`
- `version=None`
- `prior_classification_id=None`
- `new_classification_id=None`
- `classification_ids=()`
- `reclassification_ids=()`
- `event_index=None`
- `event_timestamp=None`
- `from_scope=None`
- `to_scope=None`
- `reason=None`

One external range lineage has one stable map ID.

### 13.2 `BOUNDARY`

`BOUNDARY` requires:

- `source_kind=RANGE_BOUNDARY`,
- one side, and
- the common active external range lineage ID.

It requires these exact defaults for every other optional parameter:

- `source_indices=()`
- `source_id=None`
- `scope=None`
- `boundaries=None`
- `active_range_snapshot_id=None`
- `version=None`
- `prior_classification_id=None`
- `new_classification_id=None`
- `classification_ids=()`
- `reclassification_ids=()`
- `event_index=None`
- `event_timestamp=None`
- `from_scope=None`
- `to_scope=None`
- `reason=None`

`scope=None` is mandatory for `BOUNDARY`; `EXTERNAL` is implicit semantic meaning
and is not stored in the stable boundary-source identity. Boundary source
identity is stable by lineage and side. Current boundary price, source indices,
scope, and active range snapshot belong to the boundary's `CLASSIFICATION`
identity, not its stable source ID.

### 13.3 `CLASSIFICATION`

`CLASSIFICATION` requires:

- `source_indices`: a non-empty, strictly increasing tuple,
- `source_kind`: one valid source kind,
- `source_id`: one valid stable source ID,
- `side`: one valid side,
- `scope`: one valid scope,
- `boundaries`: valid integer-tick boundaries,
- `active_range_snapshot_id`: the immutable creation-context range snapshot ID,
- `version`: a positive integer with booleans rejected,
- `event_index`: a non-negative integer, and
- `event_timestamp`: a normalized timestamp.

Version `1` requires `prior_classification_id=None`. Version above `1` requires
the exact immediately prior classification ID. It requires these exact defaults
for every remaining parameter:

- `new_classification_id=None`
- `classification_ids=()`
- `reclassification_ids=()`
- `from_scope=None`
- `to_scope=None`
- `reason=None`

The source tuple and active range snapshot jointly determine first-known
classification time. The classification event is the later composite of source
availability and active range effective time at creation. A reused unchanged
classification retains that creation moment and creation-context range snapshot.
Future data is not included.

### 13.4 `SNAPSHOT`

`SNAPSHOT` requires:

- `active_range_snapshot_id`: one active range snapshot ID,
- `event_index`: a non-negative integer,
- `event_timestamp`: a normalized timestamp,
- `classification_ids`: at least two ordered IDs for the canonical boundaries,
  and
- `reclassification_ids`: an ordered tuple that may be empty.

It requires these exact defaults for every remaining parameter:

- `source_indices=()`
- `source_kind=None`
- `source_id=None`
- `side=None`
- `scope=None`
- `boundaries=None`
- `version=None`
- `prior_classification_id=None`
- `new_classification_id=None`
- `from_scope=None`
- `to_scope=None`
- `reason=None`

Classification IDs are ordered by scope value, side value, source-kind value,
source ID, and classification ID. Reclassification IDs are ordered by
source-kind value, source ID, and reclassification ID.

The exposed ID tuples must exactly equal the corresponding ordered object tuples.

### 13.5 `RECLASSIFICATION`

`RECLASSIFICATION` requires:

- `source_kind=SWING`,
- `source_id`: one valid stable source ID,
- `side`: one valid side,
- `prior_classification_id`: the exact prior classification ID,
- `new_classification_id`: the exact new classification ID,
- `event_index`: a non-negative integer,
- `event_timestamp`: a normalized timestamp,
- `from_scope` and `to_scope`: distinct valid scopes, and
- `reason`: one exact reason token.

The common active external range lineage ID is the new classification context.
It requires these exact defaults for every remaining parameter:

- `source_indices=()`
- `scope=None`
- `boundaries=None`
- `active_range_snapshot_id=None`
- `version=None`
- `classification_ids=()`
- `reclassification_ids=()`

`prior_classification_id` and `new_classification_id` must differ and must resolve
to the exact adjacent classification versions named by the reclassification.

The exact case-sensitive reason tokens are:

- `INTERNAL_TO_EXTERNAL_RANGE_DEFINING`
- `EXTERNAL_TO_INTERNAL_SUBORDINATE`

Reason text is never normalized or accepted as free-form text. A same-scope
classification version is not a reclassification and emits no reclassification
record.

Unknown identity kinds, missing required parameters, forbidden non-default
parameters, malformed hashes, invalid versions, unordered identities, or
semantically impossible payloads raise `TypeError` or `ValueError`. The analyzer
catches required-input identity failures and returns `INVALID`; it does not leak
an attribute, key, index, decimal, or enum exception.

## 14. Locked Immutable Versioning and Reclassification

Classification history is keyed by `(source_kind, source_id)` within one
chronological analysis.

- The first eligible classification has version `1`.
- A materially changed classification under a later active-range snapshot uses
  the next integer version and links the exact prior classification ID.
- Material changes include scope, active range lineage, side, boundaries,
  ordered source indices, or other source identity evidence.
- A changed current `active_range_snapshot_id` alone is not a classification
  change. An otherwise unchanged classification retains the snapshot ID under
  which that version was created; the later containing map snapshot records the
  new current range snapshot ID.
- An identical classification payload reuses its existing classification ID and
  does not create a duplicate version.
- A range-boundary price extension creates the next boundary classification
  version.
- A same-lineage extension that leaves the protected boundary price and evidence
  unchanged reuses that protected boundary's existing classification ID and
  version.
- A source omitted after losing eligibility remains in prior immutable snapshots
  but is absent from the current snapshot.
- Re-entry later creates the next classification version; absence itself does
  not invent an `INTERNAL` or `EXTERNAL` scope.

A reclassification record is emitted only when one continuously identifiable
`SWING` source changes between `INTERNAL` and `EXTERNAL`:

- Internal to External requires the swing to become an exact range-defining
  boundary identity under Section 9.
- External to Internal requires a later active range in which the same swing is
  no longer range-defining and is strictly inside.

`RANGE_BOUNDARY` sources are always External. Equal Liquidity pools are
Internal-only in version 1. Neither can emit a scope reclassification.

No prior `LiquidityClassification`, `LiquidityReclassification`, or
`LiquidityMapSnapshot` is mutated, removed, reordered, or rewritten when later
input is appended.

## 15. Locked Chronology and Same-Index Processing Precedence

Each supplied tuple must already satisfy its locked ordering contract. Swings
retain their strict composite order. Pool and range snapshots use nondecreasing
effective moments plus the causal same-moment revision and transition rules in
Sections 7.3 and 7.4. The analyzer must reject a causally out-of-order tuple as
`INVALID`; it must not silently sort, deduplicate, use an identity hash as a
chronology key, or choose a favorable record.

All input events sharing an effective index and normalized timestamp form one
atomic group. The full group is validated before state mutation or output.

The exact processing order is:

1. capture immutable pre-index active-range, pool-lineage, classification, and
   map snapshots,
2. validate every swing, pool, range, foreign key, identity, and lifecycle item
   in the same-index group,
3. apply terminal `INVALIDATED` or `SUPERSEDED` external-range evidence to the
   pre-index range,
4. select at most one valid post-transition `ACTIVE` external range,
5. apply Equal Liquidity pool lifecycle changes, so same-index `SWEPT` or
   `BROKEN` pools are terminal before current-map classification,
6. make newly confirmed same-index swings and newly active pool snapshots
   available,
7. create or update the map and its two canonical boundary references,
8. classify exact range-defining swings as External,
9. classify remaining eligible swings and active pools using strict-inside
   rules,
10. create required immutable classification versions and scope
    reclassifications,
11. emit at most one deterministic map snapshot for the group, and
12. preserve all prior snapshots byte-for-byte.

If an old range terminates and a replacement range activates in one group, old
termination is applied before the new map is classified. If the group contains
two unrelated valid active-range candidates, the result is `AMBIGUOUS` and no
same-index map snapshot or reclassification is emitted. Any malformed item makes
the group `INVALID` with the same no-partial-promotion rule. Atomic grouping does
not erase causal order: same-lineage pool revisions and old-terminal-to-new-active
range chains are validated in supplied causal order, while otherwise unrelated
same-moment records are evaluated without direction, lineage, or hash-order bias.

## 16. Locked Result Status Semantics

- `VALID`: at least one valid liquidity-map snapshot is emitted.
- `NONE`: all top-level contexts are complete and valid, but no valid active
  external Dealing Range ever exists.
- `UNKNOWN`: at least one required top-level context is `None`.
- `AMBIGUOUS`: complete individually valid inputs produce two unrelated active
  external range candidates at the same effective index and timestamp, with no
  deterministic lifecycle relationship.
- `INVALID`: malformed type, enum, hash, provenance, tick, chronology,
  lifecycle, snapshot, foreign key, side, price, boundary, version, identity,
  duplicate, contradiction, or required field is present.

An empty supplied tuple is complete context. Empty swings, pools, or ranges may
produce `NONE`; they are not `UNKNOWN`. A dangling supplied foreign key is
`INVALID`, not missing context.

Top-level missing context is checked first and returns `UNKNOWN` without partial
analysis. For complete inputs, precedence is `INVALID`, then `AMBIGUOUS`, then
`VALID`, then `NONE`. Valid snapshots strictly before a later failing index
remain immutable evidence, but nothing from the failing index is promoted.

## 17. Locked Prefix-Invariance Contract

Every classification uses only source and active-range evidence knowable at its
classification index. Every snapshot uses only the fully validated effective
group at or before its snapshot index.

For any valid input prefix, appending future swings, pool snapshots, or range
snapshots must preserve every previously emitted object and ID byte-for-byte.
Later evidence may append new versions, reclassifications, and snapshots; it may
not revise a past scope, price, timestamp, reason, order, or identity.

Same-effective-moment causal order is part of the validated immutable prefix.
Future evidence cannot retrospectively reorder a pool membership revision or a
range terminal/replacement chain. Conversely, a later run must not reorder prior
objects merely because canonical snapshot hashes, directions, or lineage IDs
compare differently; those values validate identity and relationships, not time.

Repeated analysis of identical immutable inputs must produce dataclass-equal
results and byte-identical canonical identity payloads.

## 18. Locked Inline Synthetic 40-Case Unit-Test Matrix

The later dedicated tests must use obviously synthetic inline fixtures and cover
exactly these numbered logical cases, with parameterization allowed:

1. Bullish active external range produces upper Buy-Side and lower Sell-Side
   External boundary references.
2. Bearish active external range produces the same side-correct boundary roles
   without converting side into trade direction.
3. Strictly inside confirmed `HIGH` swing maps to `BUY_SIDE | INTERNAL`.
4. Strictly inside confirmed `LOW` swing maps to `SELL_SIDE | INTERNAL`.
5. Strictly inside active Equal High pool maps to `BUY_SIDE | INTERNAL`.
6. Strictly inside active Equal Low pool maps to `SELL_SIDE | INTERNAL`.
7. Exact one-tick-inside swing and pool-band boundaries are accepted as
   Internal.
8. Exact range-defining protected and target-side swing identities at their
   matching boundaries map to External.
9. Unrelated same-price swing at a boundary is omitted and never promoted by
   price equality alone.
10. Equal Liquidity band touching either range boundary is omitted.
11. Equal Liquidity band crossing either range boundary is omitted.
12. Outside swings and pools are omitted without invalidating otherwise valid
    context.
13. Only latest `ACTIVE` pool-lineage snapshot is eligible; `SWEPT` and `BROKEN`
    snapshots remain historical and are excluded from the current map.
14. `SUPERSEDED` and `INVALIDATED` range snapshots terminate their lineage and
    cannot remain active.
15. Complete valid context without an active external range returns `NONE`.
16. `swings=None`, `equal_liquidity_pools=None`, and `dealing_ranges=None` each
    return `UNKNOWN` with no partial promotion.
17. Complete empty tuples return `NONE`.
18. Active external range with no subordinate source still returns `VALID` with
    exactly two canonical boundary classifications.
19. Missing, wrong-type, and internally malformed swing required fields return
    `INVALID` without exception leakage.
20. Missing, wrong-type, and internally malformed Equal Liquidity pool required
    fields return `INVALID` without exception leakage.
21. Missing, wrong-type, and internally malformed Dealing Range snapshot
    required fields return `INVALID` without exception leakage.
22. Dangling Equal Liquidity member swing identity returns `INVALID`.
23. Dangling Dealing Range source or protected swing identity returns `INVALID`.
24. Cross-source side, price, source-index, timestamp, or provenance conflict
    returns `INVALID`.
25. Duplicate swing, pool lineage/snapshot, range lineage/snapshot, or semantic
    source identity returns `INVALID`.
26. Out-of-order swing, pool, and range tuples return `INVALID` without silent
    sorting.
27. Multiple valid snapshots of one pool or range lineage are accepted only with
    monotonic immutable lifecycle evidence and unique snapshot IDs; same-effective
    later-member `ACTIVE` pool revisions use increasing member counts and exact
    prior-member/source-index prefix extension, including a valid sequence whose
    canonical snapshot IDs decrease lexicographically, while a terminal pool uses
    the later of the latest member-confirmation moment and last lifecycle event.
28. Same-index group validation is atomic; one malformed member produces no
    same-index classification, reclassification, or snapshot.
29. Same-index old-range terminal evidence precedes replacement-range `ACTIVE`
    evidence and classification for both bullish-to-bearish and
    bearish-to-bullish reversals, independent of direction, lineage-ID, and
    snapshot-hash lexical order.
30. Same-index new range, newly confirmed swing, and newly active pool use the
    locked post-transition availability order without using canonical IDs as
    chronology tie-breakers or silently sorting the supplied causal chain.
31. Same-index pool `SWEPT` or `BROKEN` transition excludes that pool from the
    emitted current-map snapshot.
32. Two unrelated individually valid active-range candidates at one effective
    index and timestamp return `AMBIGUOUS` with no same-index partial promotion,
    regardless of their supplied direction, lineage-ID, or snapshot-hash order.
33. Transition-less same-lineage Dealing Range extension uses its snapshot
    `first_known_provenance` effective moment, preserves map ID, versions only
    the changed boundary classification, and reuses the unchanged protected
    boundary classification ID, version, and creation context; equal-moment
    terminal/replacement evidence preserves old-terminal-before-new-`ACTIVE`
    causal order and appended-future analysis preserves that prefix independent
    of hash or direction ordering.
34. Range replacement creates a new map ID and new boundary source identities
    while preserving the old map snapshots.
35. One swing moving from strict Internal to exact range-defining External emits
    one canonical Internal-to-External reclassification.
36. One swing moving from range-defining External to strictly inside a later
    range emits one canonical External-to-Internal reclassification.
37. Same-scope context versioning, source omission, and later re-entry increment
    classification versions without inventing a scope reclassification.
38. MAP, BOUNDARY, CLASSIFICATION, SNAPSHOT, and RECLASSIFICATION IDs are
    repeatable, side-aware, scope-aware, version-aware, instrument/timeframe
    normalized, UTC-normalized, and enforce exact required/forbidden schemas and
    reason tokens.
39. Identical-run repeatability, appended-future prefix invariance, later-invalid
    prior-snapshot preservation, and status precedence are exact.
40. Frozen public dataclasses, exact keyword-only signatures, exact public
    exports, and absence of pandas, v1 SMC, I/O, network, configuration,
    registration, execution, or integration dependencies are enforced.

The fixture matrix does not justify an external fixture file. Fixtures must not
contain private market data, candidate OOS values, account details, credentials,
copied generated evidence, or outcome-derived parameters.

## 19. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python, test, fixture, configuration, or documentation
  file,
- edits to `smc/smc_v2_primitives.py`, `smc/equal_liquidity.py`,
  `smc/dealing_range.py`, or `smc/__init__.py`,
- edits to or imports from legacy `smc/liquidity_sweep.py`,
- importing pandas, `smc/market_structure.py`, `smc/bos_choch.py`, current SMC
  context, or any current production analyzer,
- raw OHLC ingestion, raw swing detection, Equal Liquidity construction, Dealing
  Range construction, sweep detection, or upstream lifecycle mutation,
- Premium, Equilibrium, Discount, FVG, Order Block, Mitigation Block, Breaker
  Block, Inducement, kill-zone, or Volume Profile code,
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
6. verify all three reserved targets remain absent,
7. verify the locked dependency files and hashes remain unchanged,
8. perform a read-only implementation preflight against the exact API,
   invariants, 40-case matrix, rollback, and stop conditions here, and
9. obtain explicit human authorization for only the exact three-path task.

Passing this documentation decision is insufficient to begin coding.

## 21. Implementation Stop Conditions

If implementation is later authorized, stop before further edits if:

- any reserved target collides unexpectedly,
- any additional path, fixture, package export, or dependency edit appears
  necessary,
- the shared-primitives, Equal Liquidity, or Dealing Range API requires amendment,
- legacy `smc/liquidity_sweep.py` appears necessary,
- raw swings, raw OHLC, pandas, a v1 analyzer, or an integration adapter appears
  necessary,
- cross-source swing identities cannot be reconciled exactly,
- one active external range cannot be selected without hindsight,
- boundary equality cannot remain identity-sensitive,
- strict-inside pool-band classification cannot be preserved,
- same-index atomic precedence cannot be preserved,
- immutable versioning, deterministic identity, or prefix invariance cannot be
  demonstrated,
- a private, candidate, performance, generated, or external fixture appears
  necessary,
- an existing public interface, default output, or execution path changes,
- focused tests or the full regression suite fail,
- unrelated staged, unstaged, ignored-generated, or untracked files appear, or
- integration appears necessary to test the standalone module.

A stop condition freezes the task. It does not authorize fallback semantics,
silent coercion, scope expansion, or an implementation shortcut.

## 22. Completion, Rollback, and Promotion Gates

Later implementation completion requires:

- independent review of every changed line,
- exact three-path reconciliation,
- all 40 numbered logical test cases passing,
- the full regression suite passing,
- deterministic map, boundary, classification, snapshot, and reclassification
  identity evidence,
- strict-inside, boundary-equality, lifecycle, same-index, versioning, and
  prefix-invariance evidence,
- proof of no current production import or execution-path change,
- confirmation that no sensitive or generated evidence was added,
- a completed Liquidity Map checkpoint record, and
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is limited to the exact newly created task paths and
requires explicit instruction before destructive removal. After commit, rollback
must use a bounded revert of the task commit rather than history rewriting. Any
rollback must be followed by focused tests, full regression, and clean-scope
audit. Existing v1 and completed dependency files remain intact.

Successful implementation would prove only standalone deterministic Internal
and External Liquidity Map conformance. It would not prove trading edge, OOS
improvement, strategy value, readiness, paper approval, live approval, or
permission for Premium, Equilibrium, Discount, or any later phase.

## 23. Global Freeze and Next-Phase Boundary

The global code freeze remains active. This decision reserves one possible
future Internal and External Liquidity Mapping task only. It does not authorize
Premium, Equilibrium, Discount, FVG, Order Block, Mitigation Block, Breaker
Block, Inducement, kill zones, Volume Profile, or integration.

No later module inherits authorization from this record. Every subsequent phase
requires its own dependency evidence, formal decision, exact preflight, explicit
human implementation authorization, tests, audit, and promotion gates.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `DECISION_SCOPE=INTERNAL_EXTERNAL_LIQUIDITY_MAP_ONLY`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`
- `DEPENDENCY_ORDER_SATISFIED=True`
- `RESERVED_IMPLEMENTATION_PATHS=3`
- `INLINE_SYNTHETIC_TEST_CASES=40`
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
