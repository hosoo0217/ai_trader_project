# GC Futures Phase A Feature/Label Experiment Freeze-Lift Decision

## 1. Decision Record

- Record type: documentation-only bounded freeze-lift decision.
- Capability: deterministic GC Futures Phase A feature and label extraction.
- Decision version: `GC-PHASE-A-FEATURE-LABEL-DECISION-V1`.
- Feature schema: `GC_AI_FEATURE_SCHEMA_V1`.
- Label schema: `GC_AI_LABEL_SCHEMA_V1`.
- Label horizon: exactly `12` fully closed five-minute bars strictly after candidate confirmation.
- Instrument/timeframe: `GC` / `5M` only.
- Timezone: `America/New_York`, with the runtime timezone-data version supplied and recorded.
- Current authority: documentation only. This record does not authorize source implementation,
  real-data label generation, model fitting, OOS access, strategy integration, staging, commit, or push.

The decision is accepted only as one bounded continuation of the already accepted training
architecture. All files outside the future three-path scope in Section 21 remain under the global
code freeze.

## 2. Purpose and Outcome

The next useful task is not another detector and not model training. It is a small, deterministic
bridge from already immutable detector evidence to a versioned feature row and a separately
versioned research label. The bridge must make look-ahead, lineage, collision, and incomplete-horizon
behavior executable before any model library or training loop is introduced.

Version 1 estimates one research event only: whether the locked external liquidity target is touched
before a direction-specific structural invalidation during the next twelve fully closed five-minute
bars. It does not choose entries, exits, size, leverage, stops, orders, or PnL. It cannot place or
recommend a trade.

The fixed twelve-bar horizon is an optimization-free Phase A hypothesis. It is not presented as
profitable, optimal, or production-ready and must not be searched, tuned, or selected using this
pilot.

## 3. Verified Baseline

The following repository evidence is the immutable baseline for this record:

- `docs/gc_futures_ai_strategy_training_decision.md` SHA-256
  `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688`;
- `docs/gc_futures_2026_pilot_dataset_change_proposal.md` SHA-256
  `F39D3E256153262A1584B98DFE7B6F4588A06F2EABDFFD05AA0C9996F4B5B421`;
- `analysis/gc_dataset_builder.py` SHA-256
  `9A3519DA97C0AA526EC4A5A8C867B5BF14AE514BA156F6A11ADDD410B66C1858`;
- `core/gc_chronological_backtest.py` SHA-256
  `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A`;
- `smc/inducement.py` SHA-256
  `2D99147494A74CE30757441D7BCF044A7DD403FA25432C4B654916214099D172`;
- full regression evidence: `2079 passed` with pytest cache disabled.

The private engineering pilot dataset ID is
`81e40b6bfc397caf859226ebf16328562a9b8cc148a1cafae9075dc0f82140d8`.
Its manifest records `training_allowed=false`, `promotion_allowed=false`,
`integration_allowed=false`, `profitability_claim_allowed=false`, and
`frozen_oos_outcome_accessed=false`. It contains `7,103` development bars, `0` OOS bars, and
`73` attested no-trade intervals. The exact `NEW_YORK_AM` window has 36 bars on each of 26 covered
trade dates, but this does not convert the post-hoc pilot into point-in-time research evidence.

## 4. Exact Documentation-Only Scope

This turn may create or correct only:

- `docs/gc_futures_phase_a_feature_label_experiment_freeze_lift_decision.md`.

No Python, tests, fixture, private dataset, manifest, email evidence, calendar evidence, dependency,
configuration, package export, runtime, training, integration, checkpoint, or other documentation
file may change. This decision does not stage, commit, or push itself.

The two pre-existing untracked documentation files
`docs/gc_futures_real_data_input_binding_change_proposal.md` and
`docs/smc_v2_diagnostic_context_integration_change_proposal.md` are outside scope and must remain
untouched.

## 5. Authority and Freeze Boundary

The global code freeze remains active. A future bounded implementation may only transform
caller-supplied immutable evidence into deterministic research artifacts. It has no authority to:

- run detectors, repair detector output, enrich historical evidence, or infer missing identities;
- read the private pilot directory, crawl the filesystem, call an external API, or download data;
- fit, score, calibrate, compare, promote, serialize, or serve a model;
- access any frozen OOS outcome;
- create a decision candidate, BUY/SELL order, entry, exit, risk, position-size, or PnL artifact;
- modify the chronological backtest, execution engine, strategy runtime, storage, configuration,
  `main.py`, or package exports.

Any need for broader authority is a STOP condition requiring a new decision record.

## 6. Pilot and Research Classification

The 2026 private acquisition remains a `NON_PROMOTABLE_ENGINEERING_PILOT`. This record may use its
aggregate coverage facts to test whether a contract is implementable, but it does not authorize
feature rows or labels to be generated from those private bars. Future implementation tests must use
inline synthetic fixtures only.

Real-data feature/label extraction, training, validation, and performance reporting remain frozen
until all of the following exist in a later accepted record:

1. point-in-time acquisition and dataset-promotion evidence;
2. a pre-registered development/OOS partition with nonzero sealed OOS data;
3. exact commission, exchange fee, spread, and slippage assumptions for any execution metric;
4. numerical model-selection, calibration, and promotion thresholds;
5. an explicit authorization to run the builder on the private dataset.

## 7. Canonical Source and Grain

One output row represents exactly one canonical `Inducement` first known at its confirmation close.
The source grain is one contract-specific, fully closed, integer-tick, five-minute bar stream. The
instrument is exactly `GC`; the normalized timeframe is exactly `5M`; the tick size is exactly
`Decimal("0.1")`; the canonical acquisition source timezone is exactly `Asia/Tokyo`; the exchange
timezone is exactly `America/New_York`; timestamps are timezone-aware and normalized to UTC for
identity and ordering.

The candidate confirmation must occur inside `NEW_YORK_AM`, defined by existing canonical Kill Zone
evidence as `07:00` inclusive to `10:00` exclusive in `America/New_York`. The label horizon may extend
beyond `10:00`, but every horizon bar must remain in one continuous, calendar-verified GC trading
session and the same exact futures contract. A maintenance break, contract boundary, unavailable
calendar interval, missing expected bar, non-closed bar, or discontinuity makes the label
`INCOMPLETE`; it must not be skipped or bridged.

## 8. Immutable Input Contracts

Every collection input accepted by the future builder is a tuple or `None`. Every supplied dataclass
must be the exact canonical frozen public type from its owning module. Subclasses, dictionaries,
mutable look-alikes, boolean integers, naive timestamps, non-UTC-normalizable timestamps, malformed
hashes, duplicate identities, and silent tuple sorting are rejected fail-closed.

The immutable top-level inputs are:

- one canonical `GCDatasetBuildConfig` used to construct and bind the dataset;
- one canonical `GCDatasetBuildResult` with exact dataset manifest/segment evidence;
- canonical `KillZoneCalendarEntry` coverage;
- a tuple of `GCFeatureLabelCandidateEvidence` records;
- one exact `GCFeatureLabelConfig`.

Confirmation and label-horizon `GCChronologicalBar` observations are selected only from the immutable
bars already contained in the matched canonical dataset segment. A separate loose bar stream is not
accepted.

The dataset config must normalize exactly to the locked `GC`, `5M`, `Asia/Tokyo`,
`America/New_York`, runtime timezone-data version, and `Decimal("0.1")` contract. The dataset result
must have exact status `VALID`, a non-null manifest, a non-null lowercase 64-hex dataset ID equal to
`manifest.dataset_id`, and a nonempty canonical segment tuple. The supplied calendar version and
timezone-data version must exactly equal their manifest and dataset-config values. Manifest counts,
volumes, ordered segment IDs, segment partitions, segment bar histories, source-ID membership, and
all locally checkable conservation rules must reconcile exactly.

The future builder recomputes each SEGMENT bar digest from the exact ordered public bar fields
`index/timestamp/open_tick/high_tick/low_tick/close_tick/volume/is_closed`, recomputes the calendar
digest from the exact normalized public calendar fields
`calendar_version/trade_date/session_status/opening/closing`, and reconstructs the DATASET evidence
digest from every exact public manifest field in canonical manifest order. It then calls the public
`make_gc_dataset_id()` contract for each SEGMENT and for the DATASET using the supplied dataset config,
manifest source/coverage/segment histories, manifest coverage digest, recomputed calendar/evidence
digests, and roll dates. Canonical JSON uses sorted keys, compact separators, normalized UTC timestamp
text, ISO dates, and tuple order exactly as locked by `GC-DATASET-BUILDER-V2`.

SOURCE and COVERAGE identities whose original objects are not present remain opaque lowercase 64-hex
provenance references; they are never claimed as recomputed. Their ordered IDs and the manifest
coverage digest remain identity-bearing DATASET inputs. If stronger SOURCE/COVERAGE proof is required,
processing must STOP for a separate upstream contract proposal rather than silently broaden this API.
A manifest's source-derived raw counts, raw volumes, capture facts, and coverage facts are therefore
identity-bound and checked for every locally determinable arithmetic/conservation invariant, but are
not falsely described as re-measured from unavailable raw source or coverage objects.
A status mismatch, manifest mismatch, segment/history mismatch, conservation mismatch, digest
mismatch, or recomputed SEGMENT/DATASET identity mismatch is `INVALID`.

Supplied tuples must be ordered by their locked composite keys and independently nondecreasing
effective moment. The analyzer validates caller order and never silently sorts it. Missing top-level
input produces `UNKNOWN` only after every supplied counterpart has passed all independently
determinable type, field, enum, identity, ordering, and history checks. Determinable malformed
evidence always produces `INVALID` and cannot be hidden by a missing counterpart.

## 9. Candidate Evidence Binding

`GCFeatureLabelCandidateEvidence` binds, by exact identity and lineage, all evidence required for one
row:

- one canonical `Inducement` and corresponding `InducementSnapshot` containing its ID;
- the canonical ACTIVE EXTERNAL `DealingRangeSnapshot` selected as the latest compatible revision
  effective at or before the sweep moment, and the matching `LiquidityMapSnapshot` selected as the
  latest compatible map strictly before that sweep moment;
- the referenced EXTERNAL target `LiquidityClassification`;
- the referenced INTERNAL opposite-side pool `LiquidityClassification` and canonical
  `EqualLiquidityPool` snapshot;
- the referenced confirmed `DealingRangeStructureEvent`;
- the referenced qualifying `FairValueGap` with complete transition/snapshot history through the
  confirmation moment;
- the matching `KillZoneContext` and containing `KillZoneSnapshot`;
- the exact confirmation `GCChronologicalBar`.

Every ID stored by `Inducement` must match the supplied object. Direction, side, scope, lineage,
source kind, source indices, effective moments, event type, causal suffix, lifecycle state, and
snapshot membership must reconcile. The builder does not recompute or retroactively enrich detector
outputs. `displacement_id` remains opaque formation-time metadata: exact non-null equality is checked,
but an unavailable foreign displacement identity is not claimed as re-proven.

`candidate_id` is exactly `inducement.inducement_id`; no second candidate identity is invented. The
confirmation bar must byte-equal exactly one bar in exactly one canonical dataset segment. That
segment must have equal first/last trade date, which becomes the output `trade_date`; its contract and
ordered source IDs become the output contract/source provenance. Zero or multiple matching segments,
a confirmation-bar mismatch, or a segment whose trade-date bounds differ is `INVALID`.

Foreign identities are recomputed only through the existing public
`make_equal_liquidity_id()`, `make_dealing_range_id()`, `make_liquidity_map_id()`,
`make_fair_value_gap_id()`, `make_inducement_id()`, and `make_kill_zone_id()` contracts using fields
present in the supplied canonical objects. The feature/label builder may import those public builders
and immutable types, but it may not call any detector analyzer. If a stronger proof requires a
missing foreign object or an expanded dependency API, processing must STOP rather than infer it.
The active-range and liquidity-map IDs must exactly equal the references already frozen into the
canonical `Inducement`. Their local snapshot identities and membership are recomputed, but the
upstream analyzers' complete-history claim that they were the latest eligible revisions is inherited
and is not falsely re-proven from these single supplied snapshots.

Bullish candidates require a SELL_SIDE INTERNAL pool and BUY_SIDE EXTERNAL target. Bearish candidates
require a BUY_SIDE INTERNAL pool and SELL_SIDE EXTERNAL target. Multiple distinct valid candidates at
one confirmation moment in opposite directions produce `AMBIGUOUS` for that atomic group; exact
duplicates are deduplicated only after byte-equivalent canonical identity validation.

## 10. First-Known Moment, Ordering, and Atomicity

The candidate first-known moment is exactly
`(inducement.confirmation_index, normalized inducement.confirmation_timestamp)`. It must equal the
confirmation bar moment, structure-event confirmation moment, causally linked FVG formation-end
moment, inducement snapshot moment, and the final source moment of the event/FVG positional suffix.

Candidate evidence is ordered by:

`(confirmation_index, normalized confirmation_timestamp, direction.value, inducement_id)`.

Horizon bars are strictly increasing by both index and normalized timestamp. They start with the
first closed five-minute bar strictly after confirmation; neither the confirmation bar nor an FVG
formation bar can satisfy a future outcome. Same-effective candidate evidence is processed as one
complete atomic group. Nothing from an ambiguous or invalid group is promoted.

## 11. Exact Feature Schema

The learned feature schema is exactly `GC_AI_FEATURE_SCHEMA_V1` with these 17 ordered fields:

1. `candidate_direction`: `BULLISH` or `BEARISH`;
2. `structure_event_type`: canonical `BOS` or `CHOCH` value;
3. `confirmation_offset_bars`: exact inducement value in `[1, 3]`;
4. `pool_side`: canonical internal-pool side;
5. `pool_width_ticks`: `upper_tick - lower_tick`;
6. `pool_member_count`: length of `member_swing_ids`;
7. `sweep_penetration_ticks`: direction-specific excursion beyond the swept pool boundary;
8. `reclaim_boundary_distance_ticks`: direction-specific close distance back inside the pool boundary;
9. `target_source_kind`: canonical external-target source kind;
10. `external_target_distance_ticks`: direction-specific distance from reclaim close to the
    nearest external target boundary;
11. `range_direction`: mandatory non-signal ACTIVE range direction;
12. `range_width_ticks`: `high_tick - low_tick`;
13. `range_midpoint_offset_half_ticks`: exact signed half-tick offset from range midpoint;
14. `fvg_width_ticks`: `upper_tick - lower_tick`;
15. `fvg_midpoint_offset_half_ticks`: exact signed half-tick offset from FVG midpoint;
16. `minutes_from_ny_am_start`: exact integer minutes from `07:00` local;
17. `minutes_to_ny_am_end`: exact integer minutes to `10:00` local.

No feature may contain future bars, label outcome, target-hit time, invalidation-hit time, horizon end,
future return, MFE/MAE, exit, PnL, OOS membership, source filename, row number, capture timestamp, model
score, or post-confirmation detector state. Lineage IDs are retained as audit metadata, never learned
columns.

## 12. Exact Feature Geometry

All prices are integer ticks. Canonical detector midpoints remain exact `Decimal` integer/half-tick
values, but both learned midpoint offsets are represented as integers in half-tick units. No float or
ambient Decimal-context operation is permitted.

For bullish evidence:

- sweep penetration = `internal_pool.lower_tick - inducement.sweep_extreme_tick`;
- reclaim distance = `inducement.reclaim_close_tick - internal_pool.lower_tick`;
- target distance = `external_target.boundaries.lower_tick - inducement.reclaim_close_tick`;
- range midpoint offset =
  `2 * confirmation_bar.close_tick - active_range.low_tick - active_range.high_tick`;
- FVG midpoint offset =
  `2 * confirmation_bar.close_tick - fair_value_gap.lower_tick - fair_value_gap.upper_tick`.

For bearish evidence:

- sweep penetration = `inducement.sweep_extreme_tick - internal_pool.upper_tick`;
- reclaim distance = `internal_pool.upper_tick - inducement.reclaim_close_tick`;
- target distance = `inducement.reclaim_close_tick - external_target.boundaries.upper_tick`;
- range midpoint offset =
  `active_range.low_tick + active_range.high_tick - 2 * confirmation_bar.close_tick`;
- FVG midpoint offset =
  `fair_value_gap.lower_tick + fair_value_gap.upper_tick - 2 * confirmation_bar.close_tick`.

Each value must be nonnegative and must reconcile with canonical detector boundaries. A target already
reached at or before confirmation, impossible direction geometry, mutated boundary, or inconsistent
midpoint is `INVALID`; the builder does not repair it.

## 13. Exact Label Horizon and Clock

The label schema is exactly `GC_AI_LABEL_SCHEMA_V1`. `horizon_bars` is required to equal `12`; any
other value is `INVALID`. The horizon is the next 12 expected, fully closed, exact five-minute bars
after candidate confirmation. It is positional, not wall-clock sampling, and is never shortened,
extended, optimized, or filled from a later bar.

The label outcomes are exactly:

- `TARGET_FIRST`;
- `INVALIDATION_FIRST`;
- `TIMEOUT`;
- `SAME_BAR_AMBIGUOUS`;
- `INCOMPLETE`;
- `INVALID`.

`TARGET_FIRST` is the positive class. `INVALIDATION_FIRST` and `TIMEOUT` are negative classes.
`SAME_BAR_AMBIGUOUS`, `INCOMPLETE`, and `INVALID` are excluded from fitting and score metrics.

## 14. Target, Invalidation, and Same-Bar Precedence

The immutable label thresholds are derived only from confirmation-time evidence:

- bullish target tick = EXTERNAL BUY_SIDE target `boundaries.lower_tick`;
- bearish target tick = EXTERNAL SELL_SIDE target `boundaries.upper_tick`;
- bullish invalidation tick = INTERNAL SELL_SIDE pool `lower_tick - 1`;
- bearish invalidation tick = INTERNAL BUY_SIDE pool `upper_tick + 1`.

Target uses wick touch:

- bullish target when `bar.high_tick >= target_tick`;
- bearish target when `bar.low_tick <= target_tick`.

Invalidation uses close-through:

- bullish invalidation when `bar.close_tick <= invalidation_tick`;
- bearish invalidation when `bar.close_tick >= invalidation_tick`.

Pool-boundary equality without the adverse one-tick close-through is not invalidation. Bars are
scanned chronologically. The first target-only bar yields `TARGET_FIRST`; the first
invalidation-only bar yields `INVALIDATION_FIRST`. If both are true in the same bar before either has
occurred, the outcome is `SAME_BAR_AMBIGUOUS`. No OHLC path assumption resolves the collision. If
neither occurs in all 12 bars, the outcome is `TIMEOUT`.

## 15. Incomplete Coverage and Calendar Boundary

Expected horizon moments are derived from the canonical five-minute stream and versioned calendar,
not from whatever bars happen to be supplied. A missing expected bar, duplicate moment, timestamp
substitution, non-five-minute interval, non-closed bar, session-closed interval, maintenance break,
contract roll, trade-date mismatch, or unavailable calendar coverage yields `INCOMPLETE` when the
evidence is otherwise well formed. Malformed evidence yields `INVALID`, which has higher precedence.

An outcome found after a gap cannot rescue or relabel an incomplete horizon. A later calendar repair,
historical insertion, tuple reorder, version mutation, or changed detector snapshot makes prefix
comparison ineligible and requires a new dataset/manifest identity.

## 16. Deterministic Identity Schemas

Identity hashes are lowercase SHA-256 over a versioned canonical JSON payload with normalized UTC
timestamps, normalized instrument/timeframe, canonical Decimal text, ordered tuples, explicit nulls,
and no ambient state. Every identity requires `instrument`, `timeframe`, `tick_size`,
`timezone_data_version`, `calendar_version`, and `dataset_id`.
`make_gc_feature_label_id()` accepts exactly three identity kinds:

### `FEATURE_ROW`

Additionally required: `candidate_id`, `contract`, `trade_date`, `source_ids`, `lineage_ids`,
`detector_versions`, `feature_schema_id`, `effective_index`, `effective_timestamp`, and all 17 ordered
`feature_values`.

Forbidden: `label_schema_id`, `horizon_bars`, `target_tick`, `invalidation_tick`, `outcome`,
`first_outcome_index`, `first_outcome_timestamp`, `horizon_end_index`, `horizon_end_timestamp`,
`feature_row_ids`, and `label_ids`.

### `LABEL`

Additionally required: `candidate_id`, `contract`, `trade_date`, `label_schema_id`, `horizon_bars`, `target_tick`,
`invalidation_tick`, `outcome`, `effective_index`, `effective_timestamp`,
`first_outcome_index`, `first_outcome_timestamp`, `horizon_end_index`, and
`horizon_end_timestamp`. The two first-outcome fields are both non-null for `TARGET_FIRST`,
`INVALIDATION_FIRST`, and `SAME_BAR_AMBIGUOUS`, and both null for `TIMEOUT`, `INCOMPLETE`, or
`INVALID`. The two horizon-end fields are non-null for complete outcomes and may both be null for
`INCOMPLETE` only when the missing calendar/continuity evidence prevents the expected end from being
derived; they are both null for `INVALID`. `effective_index/effective_timestamp` always equal the
candidate confirmation moment.

The identity builder retains `INVALID` because it is part of the accepted label vocabulary and permits
deterministic audit of a rejected label attempt. The analyzer never promotes a failing group's
`INVALID` label into `GCFeatureLabelResult.labels` or a manifest.

Forbidden: `source_ids`, `lineage_ids`, `detector_versions`, `feature_schema_id`, `feature_values`,
`feature_row_ids`, and `label_ids`.

### `MANIFEST`

Additionally required: `feature_schema_id`, `label_schema_id`, `horizon_bars`, ordered
`feature_row_ids`, and ordered `label_ids`. The two ID tuples must have equal length and positional
candidate correspondence.

Forbidden: `candidate_id`, `contract`, `trade_date`, `source_ids`, `lineage_ids`,
`detector_versions`, `feature_values`, `target_tick`, `invalidation_tick`, `outcome`,
`effective_index`, `effective_timestamp`, `first_outcome_index`, `first_outcome_timestamp`,
`horizon_end_index`, and `horizon_end_timestamp`.

Unknown kinds, missing required fields, supplied forbidden fields, malformed hashes, invalid enum
values, duplicate IDs, reordered histories, or identity mismatches raise only `TypeError` or
`ValueError`; internal hashing/Decimal exceptions must not leak.

## 17. Exact Public API and Frozen Outputs

The future implementation may export exactly:

```python
GC_FEATURE_LABEL_VERSION = "GC-FEATURE-LABEL-V1"
GC_AI_FEATURE_SCHEMA_ID = "GC_AI_FEATURE_SCHEMA_V1"
GC_AI_LABEL_SCHEMA_ID = "GC_AI_LABEL_SCHEMA_V1"
GC_AI_LABEL_HORIZON_BARS = 12

class GCLabelOutcome(str, Enum):
    TARGET_FIRST = "TARGET_FIRST"
    INVALIDATION_FIRST = "INVALIDATION_FIRST"
    TIMEOUT = "TIMEOUT"
    SAME_BAR_AMBIGUOUS = "SAME_BAR_AMBIGUOUS"
    INCOMPLETE = "INCOMPLETE"
    INVALID = "INVALID"

class GCFeatureLabelIdentityKind(str, Enum):
    FEATURE_ROW = "FEATURE_ROW"
    LABEL = "LABEL"
    MANIFEST = "MANIFEST"

@dataclass(frozen=True)
class GCFeatureLabelConfig:
    feature_schema_id: str = GC_AI_FEATURE_SCHEMA_ID
    label_schema_id: str = GC_AI_LABEL_SCHEMA_ID
    horizon_bars: int = GC_AI_LABEL_HORIZON_BARS

@dataclass(frozen=True)
class GCFeatureLabelCandidateEvidence:
    inducement: Inducement
    inducement_snapshot: InducementSnapshot
    active_range: DealingRangeSnapshot
    liquidity_map_snapshot: LiquidityMapSnapshot
    external_target: LiquidityClassification
    internal_pool_classification: LiquidityClassification
    internal_pool: EqualLiquidityPool
    structure_event: DealingRangeStructureEvent
    fair_value_gap: FairValueGap
    fair_value_gap_transitions: tuple[FairValueGapTransition, ...]
    fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...]
    kill_zone_context: KillZoneContext
    kill_zone_snapshot: KillZoneSnapshot
    confirmation_bar: GCChronologicalBar

@dataclass(frozen=True)
class GCFeatureRow:
    row_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_id: str
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    source_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    detector_versions: tuple[tuple[str, str], ...]
    feature_schema_id: str
    feature_values: tuple[object, ...]

@dataclass(frozen=True)
class GCResearchLabel:
    label_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_id: str
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    label_schema_id: str
    horizon_bars: int
    target_tick: int
    invalidation_tick: int
    outcome: GCLabelOutcome
    first_outcome_index: int | None
    first_outcome_timestamp: datetime | None
    horizon_end_index: int | None
    horizon_end_timestamp: datetime | None

@dataclass(frozen=True)
class GCFeatureLabelManifest:
    manifest_id: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    timezone_data_version: str
    calendar_version: str
    dataset_id: str
    feature_schema_id: str
    label_schema_id: str
    horizon_bars: int
    feature_row_ids: tuple[str, ...]
    label_ids: tuple[str, ...]

@dataclass(frozen=True)
class GCFeatureLabelResult:
    status: SMCV2PrimitiveStatus
    rows: tuple[GCFeatureRow, ...] = ()
    labels: tuple[GCResearchLabel, ...] = ()
    manifest: GCFeatureLabelManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()

def make_gc_feature_label_id(
    *,
    identity_kind: GCFeatureLabelIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    timezone_data_version: str,
    calendar_version: str,
    dataset_id: str,
    candidate_id: str | None = None,
    contract: str | None = None,
    trade_date: date | None = None,
    source_ids: tuple[str, ...] = (),
    lineage_ids: tuple[str, ...] = (),
    detector_versions: tuple[tuple[str, str], ...] = (),
    feature_schema_id: str | None = None,
    label_schema_id: str | None = None,
    horizon_bars: int | None = None,
    feature_values: tuple[object, ...] = (),
    target_tick: int | None = None,
    invalidation_tick: int | None = None,
    outcome: GCLabelOutcome | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    first_outcome_index: int | None = None,
    first_outcome_timestamp: datetime | None = None,
    horizon_end_index: int | None = None,
    horizon_end_timestamp: datetime | None = None,
    feature_row_ids: tuple[str, ...] = (),
    label_ids: tuple[str, ...] = (),
) -> str: ...

def build_gc_feature_labels(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    candidates: tuple[GCFeatureLabelCandidateEvidence, ...] | None,
    config: GCFeatureLabelConfig = GCFeatureLabelConfig(),
) -> GCFeatureLabelResult: ...
```

Every parameter is keyword-only. No additional public symbol, convenience overload, dataframe,
filesystem path, model object, scorer, or hidden default is permitted.

`detector_versions` is ordered exactly as:

1. `("gc_dataset_builder", "GC-DATASET-BUILDER-V2")`;
2. `("equal_liquidity", "SMC-V2-EQUAL-LIQUIDITY-1")`;
3. `("dealing_range", "SMC-V2-DEALING-RANGE-1")`;
4. `("liquidity_map", "SMC-V2-LIQUIDITY-MAP-1")`;
5. `("fair_value_gap", "SMC-V2-FAIR-VALUE-GAP-1")`;
6. `("inducement", "SMC-V2-INDUCEMENT-1")`;
7. `("kill_zones", "SMC-V2-KILL-ZONE-1")`.

`lineage_ids` is ordered exactly as inducement, inducement snapshot, active range, liquidity-map
snapshot, external classification, internal classification, internal pool, structure event, FVG,
Kill Zone context, and Kill Zone snapshot IDs. `source_ids` is the exact ordered source-ID tuple of
the matched canonical contract segment. A model version is intentionally absent because this module
cannot fit or reference a model.

## 18. Fail-Closed Status and Chronological Cutoff

The final precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

- `INVALID`: determinably malformed, contradictory, impossible, identity-invalid, or out-of-order
  evidence;
- `AMBIGUOUS`: multiple distinct opposing valid candidates in one atomic effective group;
- `UNKNOWN`: required top-level evidence is unavailable or a well-formed label horizon is incomplete;
- `VALID`: at least one fully reconciled feature row and complete label exists, with no higher status;
- `NONE`: complete valid inputs contain no eligible candidate.

A determinably later invalid group produces final `INVALID` while preserving byte-for-byte only rows
and labels from strictly prior complete groups. The failing group and every later group promote
nothing. An unknowable malformed effective moment requires no trustworthy prefix. A valid feature
row whose label is `INCOMPLETE` may be returned only as auditable evidence under overall `UNKNOWN`; it
is excluded from the fitting subset and does not create a promotable manifest.

The complete reason-token vocabulary and deterministic order are exactly:

1. `INVALID_FEATURE_LABEL_EVIDENCE`;
2. `AMBIGUOUS_OPPOSING_CANDIDATES`;
3. `MISSING_TOP_LEVEL_CONTEXT`;
4. `INCOMPLETE_LABEL_HORIZON`;
5. `FEATURE_LABEL_VALID`;
6. `NO_ELIGIBLE_CANDIDATES`.

`reasons` contains each condition actually observed at most once, in that order. A success/no-op
token appears only when no higher-precedence condition exists. `blocking_reasons` is the ordered
subtuple containing only the first four tokens. Free-form messages, exception text, and unversioned
aliases are forbidden.

## 19. No-Look-Ahead and Prefix Invariance

Feature extraction may read only evidence first known at or before candidate confirmation. Label
extraction is the only operation allowed to read the next twelve bars, and those bars may influence
only the label object. Feature code and label code must be separate pure functions internally, with
tests proving that mutating bars after confirmation cannot change a feature row.

For a valid prefix ending at a complete effective-group boundary, appending strictly later complete
candidate groups and their strictly later horizon evidence preserves every prior row, label, and ID
byte-for-byte. Same-effective append, partial group, historical insertion, repair, reordering,
timezone-data mutation, calendar-version mutation, detector-version mutation, schema mutation, or
horizon mutation is not a prefix-invariance comparison and must fail closed or create a new manifest.

No random split, shuffled CV, global normalization, future-filled missing value, full-sample category
encoding, or target-derived preprocessing is permitted.

## 20. Manifest, Cost, and Private-Data Boundary

The manifest binds the source dataset ID, exact feature and label schemas, fixed horizon, and ordered
row/label identities. It does not contain a trained model or performance metric. Synthetic mechanics
tests use `NOT_APPLICABLE_NON_EXECUTION_LABEL` as the cost boundary because the label is a market-event
research target, not an executable return.

This does not waive the accepted requirement for commission, exchange fee, spread, slippage, and
fill assumptions before any backtest return, model-selection metric tied to execution, or promotion.
The future implementation must not read or write the private pilot directory. A later private-run
authorization must name its input manifest, output directory, immutable hashes, and sealed OOS
boundary explicitly.

## 21. Reserved Future Implementation Scope

After this decision is independently audited, accepted, committed, and pushed, the first future
implementation exception may modify only:

- `analysis/gc_feature_label_builder.py`;
- `tests/test_gc_feature_label_builder.py`;
- `docs/gc_futures_feature_label_checkpoint.md`.

Tests must use inline synthetic fixtures; no external fixture may be created. Package exports,
dependency manifests, dataset builder, chronological backtest, detectors, execution, storage,
configuration, training, model registry, and integration remain frozen. Stage, commit, and push each
require their own audited authorization.

## 22. Inline Synthetic Exact 48-Case Unit-Test Matrix

The logical case count is exactly 48; parameterization may expand collected test count without
changing this matrix:

1. With a valid required dataset config, absent dataset, calendar, and candidate collections return
   `UNKNOWN` with no row, label, or manifest.
2. No candidates with otherwise complete valid inputs returns `NONE`.
3. Exact canonical bullish candidate produces one deterministic feature row.
4. Exact canonical bearish candidate produces the mirrored deterministic feature row.
5. Candidate outside `NEW_YORK_AM` is ineligible and complete no-candidate evidence is `NONE`.
6. Exact `07:00` local is eligible; exact `10:00` local is ineligible.
7. Candidate confirmation, confirmation bar, event, FVG, and snapshot moment must match exactly.
8. Non-tuple collection, wrong dataset-config type, subclass, mutable look-alike, boolean integer, or
   naive timestamp is `INVALID`.
9. Dataset config, result, manifest, segment, calendar/timezone version, tick-size, count, volume, and
   locally recomputable identity mismatches are `INVALID`; unavailable foreign SOURCE/COVERAGE proof
   is not invented, and malformed supplied counterpart outranks missing top-level context.
10. Candidate tuple accepts only the exact locked composite order; no silent sort occurs.
11. Bullish SELL_SIDE internal pool and BUY_SIDE external target reconcile.
12. Bearish BUY_SIDE internal pool and SELL_SIDE external target reconcile.
13. Wrong source kind, scope, side, lineage, snapshot, or classification ID is `INVALID`.
14. Inducement/event/FVG source moments obey exact observation reconciliation and suffix binding.
15. Opaque `displacement_id` equality is enforced without foreign identity invention.
16. Exact duplicate candidate evidence is deterministic; a contradictory fork is `INVALID`.
17. Same-group distinct opposing valid candidates return `AMBIGUOUS` and promote nothing.
18. Pool width and member count use immutable canonical pool evidence.
19. Bullish sweep penetration and reclaim distance use the lower pool boundary.
20. Bearish sweep penetration and reclaim distance use the upper pool boundary.
21. Bullish external target distance uses the BUY_SIDE lower boundary.
22. Bearish external target distance uses the SELL_SIDE upper boundary.
23. Negative distance, already-reached target, or impossible direction geometry is `INVALID`.
24. Range width/direction and FVG width derive from exact referenced snapshots.
25. Integer half-tick midpoint offsets use the exact direction-normalized integer formulas.
26. Zero and arbitrary-magnitude midpoint offsets remain deterministic under low/high Decimal context.
27. NYAM minute features handle exact boundaries and DST database conversion deterministically.
28. Feature tuple has exactly the 17 locked fields in locked order and no future field.
29. Mutating any post-confirmation horizon bar cannot change a feature row or row ID.
30. Horizon begins strictly after confirmation and contains exactly twelve five-minute bars.
31. Bullish wick touch at target equality yields `TARGET_FIRST` when no earlier event exists.
32. Bearish wick touch at target equality yields `TARGET_FIRST` when no earlier event exists.
33. Bullish close one tick through the lower pool boundary yields `INVALIDATION_FIRST`.
34. Bearish close one tick through the upper pool boundary yields `INVALIDATION_FIRST`.
35. Exact pool-boundary close equality is not structural invalidation.
36. Target before invalidation yields `TARGET_FIRST`; invalidation before target yields
    `INVALIDATION_FIRST`.
37. First same-bar target/invalidation collision yields `SAME_BAR_AMBIGUOUS` without OHLC path guess.
38. No event in twelve bars yields `TIMEOUT`.
39. Missing expected bar, timestamp substitution, non-closed bar, or discontinuity yields
    `INCOMPLETE` and no later rescue.
40. Maintenance, closed-session, unavailable calendar, trade-date, or contract boundary in the
    horizon yields `INCOMPLETE`.
41. Determinably later invalid evidence preserves only strictly prior immutable rows and labels.
42. Complete-group strictly-later append preserves prior IDs byte-for-byte.
43. Same-effective append, historical insertion, repair, reorder, or version mutation is prefix
    ineligible.
44. `FEATURE_ROW` exhaustively enforces every required/forbidden field and field sensitivity.
45. `LABEL` exhaustively enforces every required/forbidden field, outcome, threshold, and moment
    sensitivity.
46. `MANIFEST` enforces equal ordered row/label histories, uniqueness, and schema/horizon sensitivity.
47. Identity-builder and feature/label-builder signatures, defaults, frozen fields, enum values,
    constants, exports, reason tokens, malformed hashes, and nested exception containment are exact.
48. Repeatability, deterministic multi-candidate output, no filesystem/network access, no private
    pilot read, no model dependency, no OOS access, exact dataset foreign-validation boundary, and
    forbidden integration/import surfaces hold.

## 23. Audit, Promotion, Rollback, and Stop Conditions

Independent audit must verify semantic consistency with the accepted training decision, exact source
types, 24 numbered sections, exact 48-case matrix, three exhaustive identity schemas, exact API,
scope, formatting, SHA-256, and repository state.

Promotion beyond synthetic feature/label mechanics is forbidden unless a later record locks data
promotion, nonzero sealed OOS, chronological purge/embargo, cost assumptions, numerical thresholds,
model hierarchy, calibration, artifact storage, and rollback. Any profitability claim remains
forbidden.

STOP immediately and preserve the last valid evidence if any of the following occurs:

- horizon, target, invalidation, touch/close, or same-bar semantics become ambiguous;
- a required canonical identity cannot be recomputed from supplied evidence;
- stronger displacement proof requires a new dependency or API field;
- feature construction requires a post-confirmation value;
- candidate grouping cannot be made atomic and deterministic;
- calendar, contract, timezone, or expected-bar continuity cannot be verified;
- an implementation needs any file outside the reserved three paths;
- private pilot execution, training, OOS access, model fitting, or integration is requested without a
  new accepted authorization;
- regression, diff, identity, or scope audit fails.

Rollback is deletion of the three future implementation files before staging; no existing module is
modified. After a local commit, rollback is a normal forward revert of that exact commit, never a
destructive reset.

## 24. Final Decision and Resume Boundary

Decision: the Phase A feature/label contract is sufficiently bounded for an independent final audit
of this one documentation file. It does not yet lift the freeze for implementation.

If the documentation independently passes, only this exact file may receive staging authorization.
Implementation may begin later only after the documentation commit is independently preflighted,
explicitly committed, push-preflighted, explicitly pushed, and post-push readiness is confirmed.
Until then, all Python, tests, fixtures, private data, training, model work, integration, staging,
commit, and push remain frozen.
