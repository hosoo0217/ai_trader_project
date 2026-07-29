# SMC v2 Inducement Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision date: `2026-07-29`.
- Repository: `ai_trader_project`.
- Clean documentation parent:
  `adf857c5013b5ac73dc73ec3fc2ff101694d0dde`.
- Parent subject: `feat(smc): add Kill Zone diagnostics`.
- Eleventh bounded capability: Inducement.
- Decision type: documentation-only bounded diagnostic freeze-lift decision.
- Current global code-freeze state: `ACTIVE`.
- Python implementation authorized by this record: `NO`.
- Integration authorized by this record: `NO`.
- Paper or live use authorized by this record: `NO`.

This record defines one future standalone confirmed-historical Inducement
analyzer. It does not authorize Python implementation, tests, fixtures,
staging, commit, push, integration, configuration, runtime registration,
strategy use, paper use, or live use.

The accepted implementation order places Inducement after Shared Primitives,
Equal Liquidity, Dealing Range, Liquidity Map,
Premium/Equilibrium/Discount, Fair Value Gap, Order Block, Mitigation Block,
Breaker Block, and Kill-zone context. Completion of those standalone
capabilities closes only the dependency-order blocker. It does not transfer
their freeze-lift authority, implementation authority, or integration authority
to this task.

## 2. Effective-State Interpretation

Version-1 Inducement is an immutable confirmed historical narrative. It is not
an early predictive label.

A bullish Inducement requires this exact causal sequence:

1. one active bullish external Dealing Range;
2. one active external buy-side liquidity target strictly above the reclaimed
   sweep close;
3. one confirmed internal sell-side Equal Liquidity pool strictly inside that
   range;
4. one later fully closed observation that penetrates at least one tick below
   the pool tolerance band and closes back at or above its lower boundary;
5. one strictly later bullish BOS or CHOCH confirmation on one of the next
   three supplied fully closed observations; and
6. one qualifying bullish Fair Value Gap whose formation confirmation is
   causally bound to that exact structure event and displacement.

Bearish Inducement is the exact mirror:

1. active bearish external range;
2. active external sell-side target strictly below the reclaimed sweep close;
3. confirmed internal buy-side Equal Liquidity pool;
4. at least one tick of penetration above the pool upper tolerance boundary
   followed by a close at or below that boundary;
5. bearish BOS or CHOCH within the next three closed observations; and
6. causally bound bearish Fair Value Gap.

The event becomes first known only when both the structure confirmation and
qualifying Fair Value Gap are knowable. This record locks those moments to exact
equality. No outcome, later target hit, entry, exit, PnL, win/loss label, risk
result, or favorable hindsight may participate.

## 3. Locked Decision Inputs and Dependency Evidence

This decision is grounded in:

- `docs/smc_v2_volume_profile_recommended_specification.md`
  - SHA-256:
    `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`;
- `docs/smc_v2_volume_profile_implementation_plan.md`
  - SHA-256:
    `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`;
- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_review.md`
  - SHA-256:
    `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`;
- `docs/smc_v2_dealing_range_checkpoint.md`
  - SHA-256:
    `F01E781E5CEB55AF22F25823E0DFDDFA305090474F7E0111D57FFCE67445FE66`;
- `docs/smc_v2_equal_liquidity_checkpoint.md`
  - SHA-256:
    `0962FE5A71BE1D6DEDF8C9BB63BBA2019DBFE880E4308872702EB8D8C3812A1D`;
- `docs/smc_v2_liquidity_map_checkpoint.md`
  - SHA-256:
    `B649009103E0D7CC2E9B4C6A4DC1AA6E48560929A1FDB31B8B6D99E56DF69353`;
- `docs/smc_v2_fair_value_gap_checkpoint.md`
  - SHA-256:
    `74BD85C1CAF19CAC94385034206D365150FD128D42BF50438486162194C05234`;
- `smc/smc_v2_primitives.py`
  - SHA-256:
    `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD`;
- `smc/dealing_range.py`
  - SHA-256:
    `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A`;
- `smc/equal_liquidity.py`
  - SHA-256:
    `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B`;
- `smc/liquidity_map.py`
  - SHA-256:
    `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321`;
- `smc/fair_value_gap.py`
  - SHA-256:
    `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1`.

Verified state at decision time:

- `HEAD = origin/main =
  adf857c5013b5ac73dc73ec3fc2ff101694d0dde`;
- live remote `main` matched that commit;
- worktree status entries: `0`;
- Kill-zone focused evidence: `86 passed`;
- full regression evidence: `1510 passed`;
- current production integration imports for the new standalone modules: `0`;
- `smc/inducement.py`, `tests/test_inducement.py`, and
  `docs/smc_v2_inducement_checkpoint.md`: absent.

## 4. Exact Change Authorized in This Documentation Task

The only authorized change in this documentation task is creation of:

- `docs/smc_v2_inducement_diagnostic_freeze_lift_decision.md`

No existing file may be edited. This task does not authorize creation of the
reserved implementation files.

The decision file must pass an independent final audit before any staging
authorization. Staging, commit, push, implementation, and integration each
require later separate explicit gates.

## 5. Reserved Exact Scope for the Later Implementation Task

If and only if this decision completes every documentation promotion gate and a
later post-push readiness audit passes, one possible bounded implementation task
may reserve exactly:

- `smc/inducement.py`
- `tests/test_inducement.py`
- `docs/smc_v2_inducement_checkpoint.md`

These targets are absent at decision time. A future collision is a stop
condition, not overwrite authorization.

No external fixture, market-data file, generated report, calendar file, or
candidate evidence is reserved. All future evidence must be obviously synthetic
and inline in `tests/test_inducement.py`.

The future exception may not include any existing Python, test, fixture,
documentation, export, registry, configuration, strategy, risk, execution,
report, or integration path.

## 6. Exact Functional Boundary

The future standalone analyzer may:

- validate caller-supplied canonical dependency evidence;
- evaluate only fully closed integer-tick observations;
- identify exact bullish and bearish sweep-and-reclaim sequences;
- enforce the positional next-three-closed-observation confirmation window;
- bind one structure event and one qualifying Fair Value Gap causally;
- emit immutable confirmed Inducement points and complete-history snapshots;
- return explicit fail-closed status and reason evidence.

It may not:

- detect raw swings, Equal Liquidity pools, Dealing Ranges, liquidity maps,
  structure breaks, displacement, Fair Value Gaps, Order Blocks, or sessions;
- repair, enrich, sort, or reinterpret dependency output;
- predict a future target hit;
- score, filter, rank, or recommend trades;
- consume Kill-zone context as a prerequisite;
- use Volume Profile, outcomes, PnL, or performance evidence;
- mutate another detector or register itself anywhere.

Kill-zone evidence is deliberately not an input. Time-window context and
Inducement narrative remain independent standalone outputs until a separately
approved integration design exists.

## 7. Locked Input Contracts

### 7.1 Top-level tuple contracts

The exact analyzer inputs are:

- `dealing_range_snapshots: tuple[DealingRangeSnapshot, ...] | None`;
- `liquidity_map_snapshots: tuple[LiquidityMapSnapshot, ...] | None`;
- `equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None`;
- `structure_events: tuple[DealingRangeStructureEvent, ...] | None`;
- `fair_value_gaps: tuple[FairValueGap, ...] | None`;
- `fair_value_gap_transitions: tuple[FairValueGapTransition, ...] | None`;
- `fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] | None`;
- `observations: tuple[InducementObservation, ...] | None`.

Every supplied collection must be an exact tuple. Lists, iterators, mappings,
sets, subclasses used as substitutes, and silently sorted inputs are invalid.

A `None` top-level tuple means required context is unavailable and returns
`UNKNOWN` only after every supplied counterpart has been fail-closed validated.
A complete empty tuple is valid negative evidence and does not by itself mean
`UNKNOWN`.

### 7.2 `InducementObservation`

The future module locks this exact frozen public dataclass:

```python
@dataclass(frozen=True)
class InducementObservation:
    index: int
    timestamp: datetime
    open_tick: int
    high_tick: int
    low_tick: int
    close_tick: int
    is_closed: bool
```

Validation is exact:

- `index` is a non-negative exact `int`, never `bool`;
- `timestamp` is timezone-aware and normalized to UTC;
- OHLC values are exact integer ticks, never `bool`;
- `low_tick <= open_tick <= high_tick`;
- `low_tick <= close_tick <= high_tick`;
- `is_closed is True`;
- indices and normalized timestamps are independently strictly increasing.

### 7.3 Canonical dependency boundary

Inputs must be exact frozen public dependency types. The future analyzer may use
the existing public identity builders to recompute locally verifiable IDs:

- `make_dealing_range_id`;
- `make_equal_liquidity_id`;
- `make_liquidity_map_id`;
- `make_fair_value_gap_id`.

It must validate embedded histories, hashes, enum values, source references,
effective moments, causal ordering, and exact snapshot contents that are
recomputable from supplied evidence.

`DealingRangeStructureEvent.event_id` cannot be recomputed from the locked input
because the referenced `DealingRangeSwing.price_tick` is deliberately not
supplied. For that foreign identity, validate exact type, direction, event type,
provenance, broken-swing hash shape, event-ID hash shape, ordering, and every
cross-reference available in the supplied FVG evidence. Do not invent or demand
the absent swing tick.

Every `(index, normalized timestamp)` pair in the selected structure event's
provenance and every pair in the selected FVG's
`source_indices`/`source_timestamps` must reconcile exactly with one supplied
`InducementObservation`. A selected source moment that is absent from the
observation tuple, or whose timestamp differs, is `INVALID`; source moments are
never inferred from hashes or treated as an unavailable pre-horizon exception.

The analyzer must not demand raw swing, candle, or event objects that are not
part of the locked input. A fact that cannot be proven from the exact supplied
contracts is not silently reconstructed.

### 7.4 Canonical ordering

No tuple is silently sorted.

- observations follow strict `(index, normalized timestamp)` order;
- structure events follow the existing strict composite order:
  `(confirmation_index, normalized confirmation_timestamp, direction.value,
  event_type.value, event_id)`;
- Fair Value Gaps follow
  `(formation_end_index, normalized formation_end_timestamp,
  direction.value, source_indices, gap_id)`;
- Fair Value Gap transition and snapshot tuples are each independently
  nondecreasing by `(index, normalized timestamp)`;
- at one FVG lifecycle moment, transitions for gaps formed strictly earlier
  retain the originating gap order
  `(formation_end_index, normalized formation_end_timestamp,
  direction.value, source_indices, gap_id)`;
- any new `None -> ACTIVE` formation at that moment follows all lifecycle
  updates for gaps formed earlier, matching the upstream lifecycle-before-
  formation processing precedence;
- the snapshot tuple mirrors the corresponding transition tuple one-for-one:
  same gap, same effective moment, same relative order, and the snapshot's final
  transition ID equals that transition ID;
- Equal Liquidity pool revisions preserve their originating effective-moment
  and membership/lifecycle causal order;
- Dealing Range and Liquidity Map snapshots preserve their originating
  nondecreasing effective moments and same-moment causal precedence.

No supplied tuple is reordered. Hash lexical order is identity evidence only and
is never substituted for the locked upstream causal ordering rules.

## 8. Locked Active Range and Liquidity Roles

Only `DealingRangeKind.EXTERNAL`, `DealingRangeState.ACTIVE` snapshots with
`SMCV2Direction.BULLISH` or `SMCV2Direction.BEARISH` are eligible.

The effective range at a moment is the latest canonical snapshot at or before
that moment for its lineage. A terminal range before confirmation disqualifies
the candidate. A same-lineage boundary revision is used only from its own
effective moment forward and never rewrites prior candidate geometry.

Every selected Liquidity Map snapshot must:

- reference the same active range lineage;
- reference the exact latest pre-group active range snapshot ID;
- be the latest canonical pre-group snapshot before the sweep;
- contain both selected classifications;
- retain the external target classification through confirmation;
- preserve exact classification identities and boundaries.

Direction-specific roles are:

| Direction | External target | Internal pool |
|---|---|---|
| `BULLISH` | `BUY_SIDE`, `EXTERNAL` | `SELL_SIDE`, `INTERNAL` |
| `BEARISH` | `SELL_SIDE`, `EXTERNAL` | `BUY_SIDE`, `INTERNAL` |

The internal classification must have
`source_kind=EQUAL_LIQUIDITY_POOL`. Its `source_id` must equal one supplied
Equal Liquidity pool `lineage_id` exactly. `internal_pool_id` in every future
Inducement object and identity is that same `lineage_id`, never a pool
`snapshot_id`. That pool must be `LOW` side for bullish Inducement and `HIGH`
side for bearish Inducement.

The internal pool band must be strictly inside the selected range:

```text
range.low_tick < pool.lower_tick <= pool.upper_tick < range.high_tick
```

The external target must remain strictly beyond the reclaimed sweep close:

- bullish: `target.boundaries.lower_tick > observation.close_tick`;
- bearish: `target.boundaries.upper_tick < observation.close_tick`.

If multiple external targets qualify, select deterministically:

- bullish: smallest `lower_tick`, then `classification_id`;
- bearish: largest `upper_tick`, then `classification_id`.

An external target may originate from a swing, Equal Liquidity pool, or active
range boundary under the Liquidity Map contract. If it originates from an Equal
Liquidity pool, the corresponding pool lineage must remain `ACTIVE` through
confirmation. A range-boundary target remains eligible only while the same
external range lineage is active. A swing target remains eligible while its
canonical external classification remains present in the latest map snapshot.

Independent internal pool lineages remain independent candidates. One confirmed
pool-sweep sequence is emitted at most once and is never relabeled from a later
observation.

## 9. Locked Sweep and Reclaim Semantics

The selected Equal Liquidity pool must be active immediately before the sweep.
Its supplied lifecycle must record the exact terminal `SWEPT` event at the sweep
observation moment. `BROKEN`, already terminal, malformed, or missing causal
history is not an eligible pool.

Bullish sweep and reclaim require:

```text
observation.low_tick <= pool.lower_tick - 1
observation.close_tick >= pool.lower_tick
```

Bearish sweep and reclaim require:

```text
observation.high_tick >= pool.upper_tick + 1
observation.close_tick <= pool.upper_tick
```

Boundary equality on the reclaim close qualifies. Wick contact without a
one-tick penetration does not qualify. Penetration followed by a close on the
wrong side of the tolerance boundary does not qualify.

The formation/member observations that created the pool cannot be reused as its
Inducement sweep. The sweep moment must be strictly later than the latest member
confirmation effective moment.

The future `Inducement` record stores the actual penetration extreme and reclaim
close. These values never mutate after confirmation.

## 10. Locked Confirmation Window and Causal Binding

### 10.1 Positional three-bar window

The structure event must be effective on one of the next three supplied fully
closed observations after the sweep. The rule is positional, not arithmetic
index subtraction.

Allowed confirmation offsets are exactly `1`, `2`, or `3`. The sweep bar itself
is forbidden. Offset `4` or later does not confirm that candidate.

If the supplied observation horizon ends before all three later positions are
knowable and no qualifying confirmation exists, the unresolved candidate is
`UNKNOWN`. Once all three later closed positions are supplied, absence of the
required event/FVG sequence is complete negative evidence and returns `NONE`
for that candidate.

### 10.2 Structure-event binding

The selected event must:

- be exact canonical `DealingRangeStructureEvent`;
- have direction equal to the candidate direction;
- have type `BOS` or `CHOCH`;
- have confirmation index and timestamp exactly equal to the chosen closed
  observation;
- carry exact canonical provenance and lowercase hash-shaped
  `broken_swing_id`/`event_id` values;
- have every provenance source index/timestamp pair reconcile exactly with the
  corresponding supplied observation;
- reconcile exactly with the selected FVG's structure-event ID and type.

Because no `DealingRangeSwing` tuple is in this analyzer API, the event's broken
swing price and EVENT identity payload are outside the locally recomputable
boundary. Hash shape plus exact supplied cross-reference is required; invented
swing evidence is forbidden.

For one candidate, the earliest qualifying event effective moment wins.
The upstream contract allows at most one event per direction in one effective
group. Two distinct same-direction events at that moment are `INVALID`; exact
duplicates are also `INVALID`. No BOS-versus-CHOCH preference is invented.

### 10.3 Fair Value Gap binding

The selected Fair Value Gap must:

- match the candidate direction;
- have non-`None` `displacement_id`;
- have `structure_event_id` equal to the selected event ID;
- have `structure_event_type` equal to the selected event type;
- have `formation_end_index` and normalized timestamp exactly equal to the
  structure confirmation moment;
- have all three source index/timestamp pairs reconcile exactly with the
  corresponding supplied observations;
- have canonical GAP identity;
- have an exact initial `None -> ACTIVE` formation transition and corresponding
  complete-history snapshot at that same moment.

Represent the event provenance and FVG source evidence as normalized ordered
moment sequences:

```text
event_source_moments =
  tuple(zip(event.provenance.source_indices,
            normalized event.provenance.source_timestamps))

fvg_source_moments =
  tuple(zip(fvg.source_indices,
            normalized fvg.source_timestamps))
```

Both sequences must end at the shared structure-confirmation/FVG-formation
moment. The shorter sequence must be an exact positional suffix of the longer
sequence. Equal-length sequences must therefore match exactly. A skipped,
substituted, reordered, or timestamp-mismatched source member is `INVALID`.
This is the exact version-1 causal binding between the supplied event
displacement sequence and the FVG three-candle formation sequence.

`displacement_id` remains required, non-`None`, lowercase SHA-256 formation-time
metadata and remains an exact field of the canonical GAP identity. No public
dependency object or builder supplied to this analyzer can recompute its foreign
payload. The analyzer therefore validates its shape, immutability, GAP-identity
binding, and no-retroactivity only; it must not claim to have independently
re-proved that opaque ID. The causal proof used by this analyzer is the exact
event/FVG ID-and-type cross-reference, shared confirmation moment, observation
reconciliation, and source-sequence suffix rule above.

Later FVG touch, fill, or invalidation does not retroactively remove a confirmed
Inducement.

Exactly one canonical FVG may bind the selected event at its confirmation
moment. Duplicate or forked matching FVG evidence is `INVALID`; it is not
resolved through a favorable geometry or outcome-derived tie.

## 11. Locked First-Known and No-Retroactivity Contract

The exact first-known Inducement moment is the shared structure-event
confirmation and FVG formation-end moment.

All six prerequisites must be knowable at that moment. The analyzer may not:

- emit at range construction;
- emit at pool formation;
- emit at sweep/reclaim;
- backdate after a later FVG appears;
- enrich a prior event with a later structure or FVG link;
- relabel an earlier nonqualifying sweep after outcome information arrives.

A future append may create a new event only at the new event's own first-known
moment. Previously emitted Inducement objects and IDs remain byte-for-byte
immutable.

## 12. Locked Candidate Selection and Ambiguity

Candidate key:

```text
(
  active_range_lineage_id,
  direction.value,
  internal_pool_classification_id,
  internal_pool_id,
  sweep_index,
  normalized_sweep_timestamp,
)
```

For each candidate, use the deterministic external-target, earliest-event, and
FVG tie rules above. Exact duplicate IDs or forked evidence are `INVALID`, not
extra candidates.

Independent same-direction candidate keys may emit multiple events at one
confirmation moment. Their output order is:

```text
(
  confirmation_index,
  normalized_confirmation_timestamp,
  direction.value,
  sweep_index,
  internal_pool_id,
  inducement_id,
)
```

If at least one valid bullish and at least one valid bearish candidate become
confirmed in the same confirmation effective group, that group is
`AMBIGUOUS`. No Inducement or snapshot from that group is promoted. Strictly
prior immutable evidence is preserved.

`AMBIGUOUS` is not used for malformed duplicates, conflicting identities, or
same-direction forks; those are `INVALID`.

## 13. Locked Public API

The future module may export exactly:

- `INDUCEMENT_DETECTOR_VERSION`;
- `InducementObservation`;
- `Inducement`;
- `InducementSnapshot`;
- `InducementResult`;
- `make_inducement_id`;
- `analyze_inducements`.

No registry, adapter, config loader, CLI helper, feature flag, singleton, or
automatic analyzer is part of the public surface.

### 13.1 Exact frozen dataclasses

```python
@dataclass(frozen=True)
class Inducement:
    inducement_id: str
    direction: SMCV2Direction
    active_range_lineage_id: str
    active_range_snapshot_id: str
    liquidity_map_snapshot_id: str
    external_target_classification_id: str
    internal_pool_classification_id: str
    internal_pool_id: str
    sweep_index: int
    sweep_timestamp: datetime
    sweep_extreme_tick: int
    reclaim_close_tick: int
    structure_event_id: str
    structure_event_type: DealingRangeEventType
    confirmation_index: int
    confirmation_timestamp: datetime
    confirmation_offset_bars: int
    fair_value_gap_id: str
    displacement_id: str


@dataclass(frozen=True)
class InducementSnapshot:
    snapshot_id: str
    index: int
    timestamp: datetime
    inducement_ids: tuple[str, ...]


@dataclass(frozen=True)
class InducementResult:
    status: SMCV2PrimitiveStatus
    inducements: tuple[Inducement, ...] = ()
    snapshots: tuple[InducementSnapshot, ...] = ()
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

`InducementObservation` is locked in Section 7.2. All public dataclasses are
frozen. No field may be added, removed, reordered, renamed, or defaulted
differently without a new decision.

### 13.2 Exact analyzer signature

```python
def analyze_inducements(
    *,
    instrument: str,
    timeframe: str,
    dealing_range_snapshots: tuple[DealingRangeSnapshot, ...] | None,
    liquidity_map_snapshots: tuple[LiquidityMapSnapshot, ...] | None,
    equal_liquidity_pools: tuple[EqualLiquidityPool, ...] | None,
    structure_events: tuple[DealingRangeStructureEvent, ...] | None,
    fair_value_gaps: tuple[FairValueGap, ...] | None,
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...] | None,
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] | None,
    observations: tuple[InducementObservation, ...] | None,
) -> InducementResult:
    ...
```

Every parameter is keyword-only and has no default.

### 13.3 Exact identity-builder signature

```python
def make_inducement_id(
    *,
    identity_kind: str,
    instrument: str,
    timeframe: str,
    direction: SMCV2Direction | None = None,
    active_range_lineage_id: str | None = None,
    active_range_snapshot_id: str | None = None,
    liquidity_map_snapshot_id: str | None = None,
    external_target_classification_id: str | None = None,
    internal_pool_classification_id: str | None = None,
    internal_pool_id: str | None = None,
    sweep_index: int | None = None,
    sweep_timestamp: datetime | None = None,
    sweep_extreme_tick: int | None = None,
    reclaim_close_tick: int | None = None,
    structure_event_id: str | None = None,
    structure_event_type: DealingRangeEventType | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    confirmation_offset_bars: int | None = None,
    fair_value_gap_id: str | None = None,
    displacement_id: str | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    inducement_ids: tuple[str, ...] = (),
) -> str:
    ...
```

Every parameter is keyword-only. Only `identity_kind`, `instrument`, and
`timeframe` lack defaults.

## 14. Locked Deterministic Identity Contract

Identity kinds are exactly `INDUCEMENT` and `SNAPSHOT`.

Common payload fields:

- exact identity kind;
- detector version `SMC-V2-INDUCEMENT-1`;
- stripped uppercase instrument;
- stripped uppercase timeframe.

Canonical serialization uses UTF-8 JSON, sorted keys, compact separators,
uppercase enum tokens, UTC timestamps formatted exactly as
`YYYY-MM-DDTHH:MM:SS.ffffffZ`, ordered tuple arrays, and lowercase SHA-256.
Booleans never satisfy integer fields. Hash inputs are exact lowercase
64-character hexadecimal strings.

### 14.1 `INDUCEMENT` schema

Required:

- bullish or bearish `direction`;
- every range/map/classification/pool/event/FVG/displacement ID;
- sweep index, timestamp, extreme, and reclaim close;
- event type;
- confirmation index, timestamp, and offset;
- `confirmation_offset_bars` in `{1, 2, 3}`.

Forbidden/default:

- `effective_index=None`;
- `effective_timestamp=None`;
- `inducement_ids=()`.

The builder validates:

- sweep moment strictly precedes confirmation moment;
- bullish `sweep_extreme_tick < reclaim_close_tick`;
- bearish `sweep_extreme_tick > reclaim_close_tick`;
- direction and event type are exact enums;
- all identifiers and integer/timestamp fields are canonical.

Dependency-boundary geometry remains analyzer validation because pool and target
boundaries are not builder inputs.

### 14.2 `SNAPSHOT` schema

Required:

- `effective_index`;
- `effective_timestamp`;
- non-empty ordered unique `inducement_ids`.

Required defaults/forbidden:

- `direction=None`;
- every source-specific ID, sweep field, event field, confirmation field, and
  FVG/displacement field is `None`.

Unknown identity kinds, missing required values, forbidden values, malformed
nested values, impossible directional geometry, or noncanonical histories
raise only `TypeError` or `ValueError`.

## 15. Locked Immutable Point and Snapshot Contract

Inducement has no mutable lifecycle in version 1.

There is:

- no `DETECTED` output;
- no active/inactive state;
- no transition stream;
- no mitigation, invalidation, expiry, replacement, or reclassification;
- no later target-hit result.

One confirmed sequence emits one immutable `Inducement`. After each
nonambiguous confirmation effective group, emit exactly one
`InducementSnapshot` containing the complete ordered history of all promoted
Inducement IDs through that group.

Snapshot `index` and `timestamp` equal that confirmation group. Snapshot
identity must be recomputable from its ordered complete history. Duplicate,
missing, reordered, partial, or malformed history is `INVALID`.

## 16. Locked Same-Index Atomic Processing

Each normalized observation effective group is processed atomically:

1. validate all supplied evidence whose effective moment is at or before the
   group;
2. establish the immutable pre-group active range, map, target, and pool state;
3. apply an exact same-group pool `ACTIVE -> SWEPT` event and evaluate the
   observation's penetration and reclaim against the pre-group pool band;
4. create pending candidates only after successful reclaim;
5. for strictly later groups, evaluate canonical structure events;
6. bind qualifying FVG formation evidence at the exact confirmation group;
7. resolve same-direction selection and opposing-direction ambiguity;
8. promote the entire group or none of it.

The sweep bar cannot also confirm the candidate. FVG and structure evidence
must be available together at confirmation.

If any determinable evidence in a group is invalid, the final status is
`INVALID`, nothing from that group or later is promoted, and strictly prior
immutable Inducements and snapshots are preserved.

## 17. Locked Result Status Semantics

Final precedence is:

```text
INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE
```

### `INVALID`

Use for:

- wrong top-level collection type;
- malformed internal dataclass fields;
- noncanonical, duplicate, forked, or dangling IDs;
- broken dependency history or ordering;
- mismatched range/map/pool/event/FVG references;
- missing required observation inside supplied coverage;
- nonclosed observation or invalid ticks;
- no-silent-sort violation;
- impossible identity schema;
- uncontained dependency exception.

### `AMBIGUOUS`

Use only when valid bullish and bearish sequences become confirmed in the same
effective group. Promote no evidence from that group.

### `UNKNOWN`

Use for:

- a required top-level tuple is `None` after supplied counterparts validate;
- a pending reclaimed sweep reaches end of input before all three later closed
  observation positions are knowable;
- required pre-horizon dependency coverage is explicitly unavailable but not
  contradictory.

### `VALID`

Use when at least one nonambiguous Inducement is confirmed and no higher status
applies.

### `NONE`

Use for complete valid evidence with no qualifying sequence, including:

- no eligible active range;
- no external target;
- no internal pool;
- no one-tick sweep;
- no reclaim;
- no matching event within three closed positions;
- no causally bound qualifying FVG.

The accepted high-level statement that a missing sequence component returns
`NONE` applies to complete valid coverage. It does not override `UNKNOWN` for
unavailable context or `INVALID` for malformed/conflicting supplied evidence.

## 18. Locked Prefix-Invariance Contract

Prefix comparison is eligible only when:

- the prefix ends at a complete atomic effective-group boundary;
- every prefix tuple is an exact immutable prefix of its extended counterpart;
- appended observations and dependency evidence have strictly later effective
  moments;
- no pending candidate at the prefix boundary depends on omitted positions.

For an eligible append, every prior Inducement, ID, snapshot, history, reason,
and status contribution remains byte-for-byte unchanged.

The following are not eligible prefix extensions and are validated normally:

- same-effective append;
- historical insertion;
- dependency repair or replacement;
- reordered evidence;
- identity or version mutation;
- partial atomic group;
- backfilled structure event or FVG;
- completion of a previously unresolved candidate.

Completion of a pending candidate in a longer run creates evidence only at its
own later first-known confirmation moment and does not rewrite the shorter run.

## 19. Locked Inline Synthetic 48-Case Unit-Test Matrix

The future test module must retain exact sequential logical cases `1` through
`48`. Parameterization may expand collected tests but may not change the logical
case count.

1. Missing top-level tuple returns `UNKNOWN`; malformed supplied counterpart
   has `INVALID` precedence and no promotion.
2. Lists, iterators, mappings, sets, and tuple subclasses fail closed.
3. Observation exact type, frozen state, closed flag, integer ticks, and OHLC
   geometry.
4. Independent strict observation index/timestamp ordering, duplicate, reorder,
   naive timestamp, and boolean rejection.
5. Canonical active external bullish and bearish Dealing Range validation.
6. Terminal/internal/malformed range and range identity/history rejection.
7. Canonical Liquidity Map snapshot and classification identity reconciliation.
8. Map lineage/snapshot/classification mismatch, fork, duplicate, and causal
   order rejection.
9. Canonical Equal Liquidity pool membership, band, lifecycle, and ID
   reconciliation.
10. Pool side, terminal-state, lifecycle-event, source, and effective-moment
    rejection.
11. Canonical structure-event provenance, every source-moment/observation
    reconciliation, absent/mismatched source rejection, broken-reference/event
    hash shape, ordering, and supplied FVG cross-reference reconciliation.
12. Canonical FVG, all three source-moment/observation reconciliations,
    absent/mismatched source rejection, exact canonical gap ordering, formation
    transition, complete causally ordered and snapshot-mirrored history, context
    link, and identity reconciliation.
13. Full bullish positive sequence.
14. Full bearish mirror positive sequence.
15. Bullish exact one-tick penetration and lower-boundary reclaim equality.
16. Bearish exact one-tick penetration and upper-boundary reclaim equality.
17. Wick contact without penetration is `NONE`.
18. Penetration without reclaim is `NONE`.
19. Pool formation/member moment cannot be reused as sweep.
20. Internal pool must be strictly inside active range.
21. Bullish/bearish internal and external side-role reconciliation.
22. External target must remain strictly beyond reclaimed close.
23. Deterministic nearest external-target selection and ID tie.
24. Multiple independent internal pools remain deterministic independent
    candidates without pool reuse.
25. Confirmation on next closed observation qualifies with offset `1`.
26. Confirmation on second closed observation qualifies with offset `2`.
27. Confirmation on third closed observation qualifies with offset `3`.
28. Same-bar confirmation and fourth-or-later confirmation do not qualify.
29. Bullish/bearish BOS confirmation.
30. Bullish/bearish CHOCH confirmation.
31. Earliest event selection plus same-direction duplicate/fork rejection.
32. FVG direction, event ID/type linkage, required opaque displacement hash,
    canonical GAP binding, and exact shorter-sequence positional-suffix causal
    rule; skipped, substituted, reordered, or timestamp-mismatched members are
    `INVALID`.
33. FVG formation-end moment must exactly equal structure confirmation, both
    source sequences must end there, and every event/FVG source moment must
    reconcile to supplied observations.
34. Duplicate or forked bound FVG, source-sequence mismatch, and transition/
    snapshot causal-order or mirroring mismatch are rejected without favorable
    selection.
35. Later FVG cannot backdate or enrich an earlier candidate; opaque
    `displacement_id` metadata is never treated as independently re-proved, and
    requiring stronger displacement-identity proof triggers a stop condition.
36. No outcome, target-hit, entry, exit, PnL, trade, score, or confidence field
    exists in public evidence.
37. Simultaneous valid opposing confirmation group returns `AMBIGUOUS` and
    promotes nothing from that group.
38. Same-direction independent candidates emit in exact deterministic order.
39. Determinably later malformed evidence returns final `INVALID`, preserves
    strictly prior evidence, and promotes nothing at or after failure.
40. Unknowable malformed moment claims no trustworthy prefix and leaks no
    exception.
41. Truncated one/two-position confirmation horizon returns `UNKNOWN`; complete
    three-position miss returns `NONE`.
42. `INDUCEMENT` identity exhaustive required/forbidden schema, directional
    geometry, offset, normalization, and field sensitivity.
43. `SNAPSHOT` identity exhaustive required/forbidden schema, ordered unique
    complete history, effective-moment sensitivity, and malformed hash rejection.
44. Exact analyzer/builder keyword-only signatures, parameter defaults, return
    annotations, version constant, and exports.
45. Exact public frozen dataclass fields, annotations, defaults, enum reuse, and
    mutation rejection.
46. Same-index pre-group pool-state evaluation, atomic group promotion, and
    `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence.
47. Repeatability, strictly-later complete prefix invariance, same-effective
    ineligibility, historical insertion/repair/reorder rejection, exact FVG key
    including `source_indices`, lifecycle-before-formation ordering,
    transition/snapshot one-to-one mirroring, and deterministic multi-event
    output.
48. Exception containment and forbidden import/integration/file/network/
    private-data surface.

Focused and full regression runs must use `-p no:cacheprovider`.

## 20. Exact Forbidden Scope

This record does not authorize edits to:

- `smc/smc_v2_primitives.py`;
- `smc/equal_liquidity.py`;
- `smc/dealing_range.py`;
- `smc/liquidity_map.py`;
- `smc/fair_value_gap.py`;
- `smc/order_block.py`;
- `smc/mitigation_block.py`;
- `smc/breaker_block.py`;
- `smc/kill_zones.py`;
- any existing tests or documentation;
- `smc/__init__.py`, `orderflow/__init__.py`, or package exports;
- `main.py`, core decision/context/paper flow, strategy, risk, broker, config,
  Order Flow, Sierra, exporter, report, CLI, or integration files;
- requirements or dependency manifests;
- private data, generated evidence, candidate OOS data, external APIs, or
  network resources.

This record does not authorize Volume Profile, feature flags, context adapters,
trace integration, decision integration, confidence changes, tuning, paper
trading, live trading, broker connections, or real execution.

## 21. Mandatory Pre-Implementation Gates

Before any later implementation:

1. this decision file receives an independent semantic, structural, hash, and
   exact-scope audit;
2. the one-file documentation checkpoint passes separate staging, commit,
   push, and post-push verification gates;
3. all dependency hashes are rechecked;
4. the three reserved paths remain absent;
5. exact public API, identity schemas, ordering, fail-closed boundary, and all
   `48` cases are approved explicitly;
6. focused dependency tests and the full regression suite pass;
7. a separate explicit human instruction makes the bounded three-path
   exception operationally effective.

Passing this documentation record is not implementation approval.

## 22. Implementation Stop Conditions

Stop immediately if:

- any required dependency hash or public contract drifts;
- any reserved path collides;
- any path outside the exact three-path implementation scope is needed;
- raw detector behavior must be changed to support Inducement;
- causal binding cannot be proven from supplied public evidence;
- stronger semantic proof or recomputation of opaque `displacement_id` is
  required without a separately approved public dependency contract;
- observation coverage cannot distinguish `NONE`, `UNKNOWN`, and `INVALID`;
- same-index ordering or opposing ambiguity remains unclear;
- an identity cannot be deterministic from locked inputs;
- exceptions leak beyond `TypeError`/`ValueError` or result status;
- exact `48` logical cases cannot be retained;
- focused or full regression fails;
- external fixtures, files, APIs, private data, OOS outcomes, or integration
  appear necessary.

A stop condition freezes the task. It does not authorize widened scope,
fallback semantics, silent sorting, dependency repair, tuning, or favorable
reinterpretation.

## 23. Completion, Rollback, Promotion, and Global-Freeze Gates

Later implementation completion requires:

- test-first RED/GREEN evidence;
- independent review of every changed line;
- exact three-path reconciliation;
- exact public API and frozen-dataclass reflection evidence;
- exact `48` logical-case reconciliation;
- focused Inducement tests passing;
- full regression suite passing;
- artifact SHA-256, bytes, lines, and formatting evidence;
- proof of no existing runtime import, export, registration, or integration;
- a completed Inducement checkpoint;
- separate staging, commit, push, and post-push authorization gates.

Before commit, rollback is deletion of exactly the new task paths and requires
explicit authorization. After commit, rollback must use a bounded revert of the
task commit, never history rewriting. Every rollback requires focused tests,
full regression, dependency-hash verification, and clean-scope audit.

Successful standalone implementation would not authorize Volume Profile,
context aggregation, trace integration, decision integration, strategy use,
paper use, live use, threshold selection, tuning, or claims of trading edge.

The global code freeze remains active outside the exact future task. No later
module inherits authority from this record.

## 24. Final Decision State

- `DECISION_RECORDED=True`
- `CAPABILITY=INDUCEMENT`
- `IMPLEMENTATION_ORDER_POSITION=11`
- `DOCUMENTATION_ONLY=True`
- `EXACT_DOCUMENTATION_PATHS_CHANGED=1`
- `FUTURE_IMPLEMENTATION_PATHS_RESERVED=3`
- `INLINE_SYNTHETIC_LOGICAL_CASES=48`
- `IDENTITY_KINDS=INDUCEMENT,SNAPSHOT`
- `EXTERNAL_FIXTURE_AUTHORIZED=False`
- `EXTERNAL_DATA_AUTHORIZED=False`
- `EXTERNAL_API_AUTHORIZED=False`
- `OUTCOME_DERIVED_LABELING_AUTHORIZED=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `PAPER_PROGRESSION_AUTHORIZED=False`
- `LIVE_PROGRESSION_AUTHORIZED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`

This is a documentation decision only. The next permitted action is an
independent final audit of this one file.
