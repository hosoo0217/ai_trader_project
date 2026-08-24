# GC Futures Independent Pretraining Corpus Freeze-Lift Decision

## 1. Decision Record

- Record type: documentation-only bounded freeze-lift decision.
- Capability: deterministic independent GC Futures pretraining-corpus validation,
  chronological partitioning, purge/embargo enforcement, and immutable manifest publication.
- Decision version: `GC-PRETRAINING-CORPUS-DECISION-V1`.
- Future implementation version: `GC-PRETRAINING-CORPUS-V1`.
- Instrument/timeframe/tick size: exactly `GC` / `5M` / `Decimal("0.1")`.
- Feature schema: exactly `GC_AI_FEATURE_SCHEMA_V1`.
- Label schema: exactly `GC_AI_LABEL_SCHEMA_V1`.
- Label horizon: exactly `12` fully closed five-minute bars.
- Current authority: this one documentation file through an audited local commit only.

This record does not authorize a private corpus run, feature or label generation, training,
preprocessing fit, validation, calibration, OOS access, strategy integration, staging of future
implementation, a later commit, or a later push. All files outside Section 21 remain frozen.

## 2. Selected Direction and Purpose

The next correct capability is a narrow corpus boundary, not a model. It accepts already immutable
dataset, candidate-evidence, and feature/label results; verifies their canonical identities and
lineage; applies one preregistered chronological partition plan; removes contaminated or
boundary-crossing evidence atomically; and publishes deterministic research records and manifests.

The builder is reference-only with respect to upstream evidence. It must not rerun detectors,
recompute features or labels, repair incomplete evidence, change dates or thresholds, infer missing
lineage, or open the sealed final-OOS payload. Its output is a research corpus candidate, not proof
of profitability or authority to train or trade.

## 3. Verified Baseline

The immutable baseline is:

- proposal commit: `8cd30817290a54d944ed79e790e2d99bd363909b`;
- `docs/gc_futures_independent_pretraining_corpus_acquisition_and_partition_change_proposal.md`
  SHA-256 `A9AC9A55D0C24E6825CCD6E0B56C09AD4F5370CBF3D9092D6E7048F30F2C4DF9`;
- `docs/gc_futures_ai_strategy_training_decision.md` SHA-256
  `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688`;
- `docs/gc_futures_post_phase_b_pretraining_data_partition_readiness_decision.md` SHA-256
  `2B4A2D1A660A65995D8C0A1189152A010EE219F259B4B6606E8550B04D2CD4BF`;
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_closure_decision.md`
  SHA-256 `5166E0D14BAA65A2AAFC8E17BE2E1740EC92AFCFCCC4CCED4B60CFF964E36F75`;
- `analysis/gc_dataset_builder.py` SHA-256
  `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`;
- `analysis/gc_candidate_evidence_builder.py` SHA-256
  `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F`;
- `analysis/gc_feature_label_builder.py` SHA-256
  `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`;
- dataset checkpoint SHA-256
  `8A93D3A81E21DF83ACC4A781C65BC2E77959B80226DD844899E3598889D180D2`;
- feature/label checkpoint SHA-256
  `B4A49A80ED52B6B4E1636BC3342BA18F03A16859F16ACB0152086498598DFD48`.

The accepted Phase A and Phase B experiments remain closed negative/insufficient-evidence research.
Their reviewed evidence cannot be relabeled as independent pretraining evidence.

## 4. Exact Documentation-Only Scope

This bounded task may create or correct only:

- `docs/gc_futures_independent_pretraining_corpus_freeze_lift_decision.md`.

The pre-existing untracked files below are outside scope and must remain byte-for-byte unchanged:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`;
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

No Python, test, fixture, private data, calendar, manifest, requirement, configuration, package
export, integration, or other documentation file may change in this task.

## 5. Authority and Global Freeze Boundary

The future builder may only validate caller-supplied immutable objects and return immutable objects.
It has no authority to:

- read a path, directory, environment variable, database, network resource, email, chart, or clock;
- mutate, enrich, reorder, repair, or recompute any upstream result;
- generate detector, candidate, feature, label, outcome, calendar, roll, or source evidence;
- inspect any sealed final-OOS row, bar, feature, label, outcome, or metric;
- fit preprocessing, train, tune, score, compare, calibrate, serialize, or register a model;
- create confidence, BUY/SELL, risk, entry, exit, position, order, fill, PnL, or trading authority;
- modify package exports, runtime, storage, execution, backtest, configuration, or `main.py`.

Any such need is a mandatory STOP and requires a separate accepted proposal and freeze-lift record.

## 6. Immutable Upstream Result Contracts

The three upstream arguments are exact instances, not subclasses or mutable look-alikes:

1. `dataset_result: GCDatasetBuildResult` with exact `VALID` status, non-null manifest and dataset
   ID, canonical segment ordering, zero exposed OOS bars, and locally recomputable DATASET and
   SEGMENT identities;
2. `candidate_result: GCCandidateEvidenceResult` with exact `VALID` status, non-null manifest,
   exact dataset ID, detector versions, ordered segment results, candidate references, and locally
   recomputable BUNDLE and MANIFEST identities;
3. `feature_label_result: GCFeatureLabelResult` with exact `VALID` status, non-null manifest, exact
   dataset ID, schema IDs, horizon `12`, equal ordered row/label histories, and locally recomputable
   FEATURE_ROW, LABEL, and MANIFEST identities.

Every tuple must be an exact tuple. Every public upstream dataclass must retain its frozen field
contract. Hashes are lowercase 64-hex. Timestamps are timezone-aware and normalize to UTC without
changing the represented instant. Integer fields reject booleans. Decimal fields must be finite and
canonical. Missing or malformed supplied evidence is never hidden by another missing input.

Unavailable foreign identities remain opaque only where the committed dependency contract makes
recomputation impossible. Opaque means exact shape/equality/reference validation, never invented
proof. Any locally recomputable mismatch is `INVALID`.

## 7. Exact Source Registry Contract

`source_registry` is an exact tuple of these frozen entries, in canonical order:

```python
@dataclass(frozen=True)
class GCPretrainingSourceRecord:
    source_id: str
    source_name: str
    source_sha256: str
    contract: str
    role: GCPretrainingSourceRole
    dataset_id: str
    first_trade_date: date
    last_trade_date: date
    acquisition_timestamp: datetime
    calendar_version: str
    timezone_data_version: str
    prior_run_manifest_ids: tuple[str, ...]
    contaminated_evidence_ids: tuple[str, ...]
    contamination_audit_complete: bool
    final_oos_payload_accessed: bool
```

Canonical ordering is
`(role.value, first_trade_date, last_trade_date, contract, source_name, source_id)`.
No silent sort is allowed. IDs and hashes are unique. Date coverage is inclusive in the registry;
partition intervals remain half-open. `final_oos_payload_accessed` must be exact `False` for sealed
OOS metadata and may never be normalized from a truthy value. A development entry with
`contamination_audit_complete=False` is `UNKNOWN`; the builder must not treat an empty contamination
tuple as proof of independence.

The exact roles are:

```python
class GCPretrainingSourceRole(str, Enum):
    PRETRAINING_DEVELOPMENT_CANDIDATE = "PRETRAINING_DEVELOPMENT_CANDIDATE"
    CLOSED_RESEARCH_ONLY = "CLOSED_RESEARCH_ONLY"
    SEALED_FINAL_OOS_CANDIDATE = "SEALED_FINAL_OOS_CANDIDATE"
    REFERENCE_ONLY = "REFERENCE_ONLY"
    SUPERSEDED_REFERENCE = "SUPERSEDED_REFERENCE"
```

Development candidates are canonical GCJ25, GCM25, GCQ25, GCV25, and GCZ25 only within selected
dates. GCG26, GCJ26, GCM26, all closed Phase A/B evidence, and any reviewed/evaluated overlap are
`CLOSED_RESEARCH_ONLY`. The exact frozen GCQ26 30-day source SHA-256
`15E2F672457176749C4143BAA4BB00C30D1AE913C82333CB8E8E8F79592FF46E` is metadata-only
`SEALED_FINAL_OOS_CANDIDATE`. Full GCQ26 and superseded artifacts cannot substitute for it.

## 8. Exact Partition Plan Contract

The caller supplies an exact frozen plan:

```python
@dataclass(frozen=True)
class GCPretrainingPartitionPlan:
    train_start_trade_date: date
    train_end_trade_date: date
    validation_start_trade_date: date
    validation_end_trade_date: date
    calibration_start_trade_date: date
    calibration_end_trade_date: date
    final_oos_start_trade_date: date
    final_oos_end_trade_date: date
    label_horizon_bars: int = 12
    minimum_embargo_bars: int = 12
```

The exact accepted values are:

- TRAIN `[2024-11-04, 2025-06-02)`;
- VALIDATION `[2025-06-16, 2025-08-25)`;
- CALIBRATION `[2025-09-08, 2025-11-24)`;
- FINAL_OOS `[2026-07-06, 2026-08-01)`;
- label horizon `12`; minimum embargo `12` bars.

No date, horizon, or embargo value is configurable in version 1. A different value is `INVALID`,
not a new experiment hidden behind the same version.

## 9. Exact Exclusion, Purge, and Embargo Semantics

The following intervals are excluded:

- all trade dates before `2024-11-04`, except non-emitted burn-in/predecessor context;
- `[2025-06-02, 2025-06-16)`;
- `[2025-08-25, 2025-09-08)`;
- `[2025-11-24, 2026-07-06)`;
- `[2026-08-01, +infinity)`.

One atomic grain is a candidate plus its exact feature row, label, full 12-bar outcome horizon,
source lineage, and calendar/session/contract evidence. If any component or horizon bar touches an
excluded interval or a later partition, the whole grain is excluded. It is never shortened,
split, moved, or relabeled. The explicit date gaps are controlling embargoes; each also exceeds the
minimum 12-bar embargo. A group ending exactly at a half-open boundary remains on the earlier side
only if every required moment is strictly before that boundary.

Same-effective candidates and candidates with overlapping 12-bar label horizons must remain in one
partition or be purged together. They cannot be separated to inflate independent samples or evade a
boundary.

## 10. Exact Partition Uses and Final-OOS Quarantine

The partition enum is:

```python
class GCPretrainingPartition(str, Enum):
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    CALIBRATION = "CALIBRATION"
    FINAL_OOS = "FINAL_OOS"
```

TRAIN may later fit preprocessing and one model only after separate training authority. VALIDATION
may later select a preregistered model family/fixed hyperparameters. CALIBRATION may later make one
frozen threshold/calibration decision. Those future uses do not occur here.

FINAL_OOS contributes metadata only: source hash, fixed date interval, access count zero, and sealed
status. No FINAL_OOS corpus record, feature, label, outcome, count derived from payload, metric, or
debug evidence may be emitted. Any payload access or use of full GCQ26 as a replacement is
`INVALID` and a STOP.

## 11. Calendar, Session, Contract, and Roll Integrity

Every emitted record must reconcile one canonical trade date, contract-specific segment, exact
calendar version, runtime timezone-data version, source ID tuple, and complete session evidence.
Calendar or timezone mismatch, unexplained expected slot, duplicate moment, invalid OHLC/volume,
maintenance bridging, session-closed evidence, or cross-contract horizon is `INVALID`.

GCV25 is eligible only when the supplied canonical dataset's prior-completed-session
three-confirmation roll evidence selects it without future information. The builder validates that
existing roll result and does not recompute or override it. Every other contract switch obeys the
same immutable segment/roll evidence. Hash lexical order is identity order only, never chronology.

## 12. Candidate, Feature, Label, and Outcome Reconciliation

Each accepted record has exact positional correspondence among:

- one `GCSegmentCandidateEvidence` and its referenced upstream candidate;
- one `GCFeatureRow` whose `candidate_id`, dataset, contract, trade date, effective moment, source
  IDs, lineage IDs, detector versions, schema, and 17-value tuple are canonical;
- one `GCResearchLabel` with the same candidate/dataset/contract/effective moment, schema, horizon,
  target/invalidation geometry, and complete outcome evidence.

Only `TARGET_FIRST`, `INVALIDATION_FIRST`, and `TIMEOUT` are corpus-eligible. `SAME_BAR_AMBIGUOUS`,
`INCOMPLETE`, and `INVALID` are excluded and reported; they cannot become a negative class. Row and
label tuples must have equal length, unique IDs, exact manifest histories, and no orphan or dangling
reference. No outcome or post-confirmation value enters the 17 feature values.

## 13. Contamination and Independence Audit

Every selected grain is joined by exact identity against all supplied immutable prior-run manifest
IDs and `contaminated_evidence_ids`. A grain is contaminated if its candidate, feature, label,
outcome horizon, source moment, chart/manual review, or derived metric participated in a closed run,
evaluation, threshold discussion, debugging decision, or human outcome review.

Contaminated grains are atomically classified `CLOSED_RESEARCH_ONLY` and excluded before adequacy
counts. Absence of required overlap evidence is `UNKNOWN`; contradictory or malformed overlap
evidence is `INVALID`. Contamination exclusion cannot move dates, reduce thresholds, select a new
contract, or rescue a partition. Independent sources with distinct identities and no overlap remain
eligible. Exact duplicates collapse deterministically; contradictory forks are `INVALID`.

## 14. Data-Quality and Minimum Evidence Gates

All of the following must pass before `VALID` publication:

- 100% source-name/hash/role/contract/dataset reconciliation;
- 100% calendar and timezone-data coverage;
- zero unexplained expected slots, duplicate effective moments, cross-partition grains, orphan
  identities, invalid numeric values, OHLC/volume contradictions, or OOS payload accesses;
- exact raw-to-eligible-to-excluded record and volume conservation;
- exact deterministic ordering and byte-identical two-run result under an external rerun audit;
- at least `100 / 40 / 40` complete sessions in TRAIN / VALIDATION / CALIBRATION;
- at least four selected contract months overall, with at least `2 / 1 / 1` contracts in those
  partitions;
- at least `150 / 50 / 50` accepted complete-label candidates;
- at least `30 / 10 / 10` bullish and `30 / 10 / 10` bearish candidates;
- at least `30 / 10 / 10` `TARGET_FIRST` positives and `30 / 10 / 10` combined
  `INVALIDATION_FIRST|TIMEOUT` negatives.

These are adequacy gates, not performance claims. A failed gate yields `UNKNOWN` with exact
shortfall evidence. Dates, setup semantics, labels, class mapping, or thresholds must not be tuned to
make a failed corpus pass.

## 15. Immutable Output Record and Summary Contracts

The future immutable record is:

```python
@dataclass(frozen=True)
class GCPretrainingCorpusRecord:
    record_id: str
    partition: GCPretrainingPartition
    direction: SMCV2Direction
    contract: str
    trade_date: date
    effective_index: int
    effective_timestamp: datetime
    dataset_id: str
    candidate_id: str
    feature_row_id: str
    label_id: str
    outcome: GCLabelOutcome
    feature_values: tuple[object, ...]
    source_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
```

Canonical record order is
`(partition_order, trade_date, effective_index, normalized_effective_timestamp, contract,
direction.value, candidate_id, feature_row_id, label_id)`, where partition order is TRAIN,
VALIDATION, CALIBRATION.
FINAL_OOS records are forbidden.

```python
@dataclass(frozen=True)
class GCPretrainingPartitionSummary:
    partition_id: str
    partition: GCPretrainingPartition
    start_trade_date: date
    end_trade_date: date
    record_ids: tuple[str, ...]
    contracts: tuple[str, ...]
    session_count: int
    candidate_count: int
    bullish_count: int
    bearish_count: int
    target_first_count: int
    invalidation_first_count: int
    timeout_count: int
```

Summary counts derive only from emitted records and exact canonical session evidence. Contract and
record histories are ordered and unique.

## 16. Immutable Corpus Manifest and Result

```python
@dataclass(frozen=True)
class GCPretrainingCorpusManifest:
    manifest_id: str
    corpus_id: str
    version: str
    instrument: str
    timeframe: str
    tick_size: Decimal
    dataset_id: str
    candidate_manifest_id: str
    feature_label_manifest_id: str
    feature_schema_id: str
    label_schema_id: str
    label_horizon_bars: int
    calendar_version: str
    timezone_data_version: str
    partition_plan_id: str
    source_ids: tuple[str, ...]
    prior_run_manifest_ids: tuple[str, ...]
    partition_ids: tuple[str, ...]
    record_ids: tuple[str, ...]
    exclusion_counts: tuple[tuple[str, int], ...]
    excluded_record_count: int
    contaminated_record_count: int
    admitted_record_count: int
    final_oos_source_sha256: str
    final_oos_start_trade_date: date
    final_oos_end_trade_date: date
    final_oos_payload_access_count: int
    training_allowed: bool
    oos_evaluation_allowed: bool
    integration_allowed: bool
    trading_allowed: bool

@dataclass(frozen=True)
class GCPretrainingCorpusResult:
    status: SMCV2PrimitiveStatus
    records: tuple[GCPretrainingCorpusRecord, ...] = ()
    partitions: tuple[GCPretrainingPartitionSummary, ...] = ()
    manifest: GCPretrainingCorpusManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

All four authority booleans are exact `False`. `final_oos_payload_access_count` is exact zero.
Manifest counts conserve accepted, excluded, and contaminated supplied grains. No dataframe,
mutable mapping, model object, path, callback, free-form metadata, or performance metric is allowed.

## 17. Deterministic Identity Schemas

All identities are lowercase SHA-256 of canonical JSON with sorted keys, compact separators, UTC
timestamps with microseconds and `Z`, ISO dates, exact enum values, `.0`/`.5` Decimal text, and
ordered tuples encoded as arrays. Identity exceptions are contained as `TypeError` or `ValueError`.

`PARTITION_PLAN` requires version; all eight date bounds; horizon; embargo. It forbids source,
record, count, metric, feature, label, and OOS payload fields.

`RECORD` requires version; partition; contract; trade date; effective index/timestamp; dataset,
candidate, feature-row, and label IDs; exact direction; outcome; exact feature values; ordered
source and lineage IDs. It forbids target/invalidation/outcome moments, future bars, metrics, and
authority flags.

`PARTITION` requires version; plan ID; partition; start/end; ordered record IDs; ordered contracts;
all exact Section 15 counts. It forbids feature values, labels, source payload, metrics, and other
partition histories.

`CORPUS` requires version; dataset/candidate/feature-label manifest IDs; plan ID; ordered source,
prior-run, partition, and record IDs; exclusion counts; admitted/excluded/contaminated counts; sealed
OOS metadata; authority flags. It forbids final-OOS payload IDs, outcomes, metrics, model fields,
thresholds, trades, and PnL.

`MANIFEST` requires every Section 16 field plus the exact `corpus_id`; it forbids records' feature
values, labels, source payload, model/performance/trading fields, and unordered histories.

Missing required fields, supplied forbidden fields, duplicate/reordered histories, malformed
hashes, wrong enums, impossible counts, unknown identity kinds, or field sensitivity mismatches are
`INVALID`. There is no public generic identity builder; identities are internal outputs of the only
public operation.

## 18. Exact Keyword-Only Public API and Exports

The future module may export exactly:

```python
GC_PRETRAINING_CORPUS_VERSION = "GC-PRETRAINING-CORPUS-V1"
GC_PRETRAINING_INSTRUMENT = "GC"
GC_PRETRAINING_TIMEFRAME = "5M"
GC_PRETRAINING_TICK_SIZE = Decimal("0.1")
GC_PRETRAINING_LABEL_HORIZON_BARS = 12
GC_PRETRAINING_MINIMUM_EMBARGO_BARS = 12

GCPretrainingSourceRole
GCPretrainingPartition
GCPretrainingSourceRecord
GCPretrainingPartitionPlan
GCPretrainingCorpusRecord
GCPretrainingPartitionSummary
GCPretrainingCorpusManifest
GCPretrainingCorpusResult

def build_gc_pretraining_corpus(
    *,
    dataset_result: GCDatasetBuildResult | None,
    candidate_result: GCCandidateEvidenceResult | None,
    feature_label_result: GCFeatureLabelResult | None,
    source_registry: tuple[GCPretrainingSourceRecord, ...] | None,
    partition_plan: GCPretrainingPartitionPlan,
) -> GCPretrainingCorpusResult: ...
```

All five parameters are required and keyword-only; none has a default. `None` is accepted only on
the four context inputs shown and is handled under Section 19. There is no config object, convenience
overload, path input, parser, serializer, identity builder, scorer, trainer, or alternate partition
API. Module `__all__` contains exactly the six constants, two enums, six dataclasses, and one builder
listed above. Package-level exports remain unchanged.

## 19. Status Precedence, Reason Tokens, and Missing Context

Final precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Exact ordered reason tokens are:

1. `INVALID_PRETRAINING_CORPUS_EVIDENCE`;
2. `AMBIGUOUS_PRETRAINING_CORPUS_EVIDENCE`;
3. `MISSING_TOP_LEVEL_CONTEXT`;
4. `INDEPENDENCE_UNVERIFIED`;
5. `INSUFFICIENT_PARTITION_EVIDENCE`;
6. `PRETRAINING_CORPUS_VALID`;
7. `NO_ELIGIBLE_PRETRAINING_EVIDENCE`.

Supplied counterparts are independently validated before a missing-input result. Determinable
malformed evidence yields `INVALID` even when another top-level input is `None`. Missing evidence is
not invented: cross-reference checks requiring the absent input are deferred and return `UNKNOWN`.
Complete empty valid development evidence returns `NONE`; incomplete adequacy or independence proof
returns `UNKNOWN`; contradictory independent evidence returns `AMBIGUOUS`; malformed evidence or OOS
contact returns `INVALID`.

An invalid or ambiguous same-effective group promotes nothing. Determinably later failure preserves
only strictly prior immutable records and summaries; no manifest is published for a non-`VALID`
result. Pending/unknown grains promote nothing, although strictly prior confirmed records may remain
in the result for audit.

## 20. Atomic Processing, Ordering, Conservation, and Prefix Invariance

Input streams are validated in their locked upstream orders; no silent sort occurs. Processing
groups by exact `(trade_date, effective_index, normalized effective_timestamp)`. Zero, one, exact
duplicate, or multiple distinct grains are reconciled atomically. Opposing or forked distinct
canonical evidence that cannot both be true is `AMBIGUOUS` or `INVALID` according to whether each is
independently valid or one is malformed.

Complete strictly-later append with unchanged source registry, versions, plan, and historical
evidence preserves every prior eligible record ID byte-for-byte. Same-effective append, historical
insertion, repair, reorder, source-role mutation, contamination mutation, calendar/tzdata mutation,
schema/version mutation, or partition-plan mutation is not a prefix-invariance comparison and must
fail closed or create a separately authorized corpus version.

For a `VALID` result:

`supplied complete grains = admitted + excluded + contaminated`,

and ordered manifest IDs exactly mirror records and partition summaries. Two identical calls are
byte-for-byte equal and exception-free. The builder uses no wall clock, randomness, filesystem,
network, locale, mutable global, or Decimal-context-dependent arithmetic.

## 21. Reserved Future Exact Three-Path Scope

Only after this decision is independently audited, locally committed, separately push-authorized,
pushed, and post-push readiness-audited may a future test-first implementation modify:

- `analysis/gc_pretraining_corpus.py`;
- `tests/test_gc_pretraining_corpus.py`;
- `docs/gc_futures_independent_pretraining_corpus_checkpoint.md`.

Tests use inline synthetic fixtures only. Existing builders, SMC/orderflow modules, shared
primitives, package exports, private manifests/data, training, model, OOS, integration, execution,
storage, requirements, configuration, and all other files remain frozen. Stage, commit, push, and
any private run require their own later authority.

## 22. Inline Synthetic Exact 48-Case Unit-Test Matrix

The logical case count is exactly 48; parameterization may expand collected tests without changing
this matrix:

1. All four context inputs absent with a valid exact plan returns `UNKNOWN` and publishes nothing.
2. Complete valid empty upstream evidence and empty registry returns `NONE`.
3. Missing one top-level input still fully validates independently determinable supplied evidence.
4. Malformed supplied counterpart outranks missing-context `UNKNOWN` and returns `INVALID`.
5. Exact VALID dataset result and canonical DATASET/SEGMENT identities reconcile.
6. Dataset status, manifest, count, volume, source, segment, calendar, tzdata, or identity mismatch
   is `INVALID`; exposed OOS bars are forbidden.
7. Exact VALID candidate result, detector versions, segment-result order, references, BUNDLE, and
   MANIFEST reconcile.
8. Exact VALID feature/label result, schemas, horizon, equal histories, FEATURE_ROW, LABEL, and
   MANIFEST reconcile.
9. Wrong type/subclass, non-tuple, mutable look-alike, boolean integer, naive timestamp, malformed
   Decimal, enum, hash, nested value, or contained exception is `INVALID`.
10. Source registry exact fields, frozen state, ordering, uniqueness, audit-completeness, and
    dataset/calendar/tzdata reconciliation pass; no silent sort occurs.
11. All five source roles are exact; unknown roles and role/source contradictions are `INVALID`.
12. Development contracts are limited to GCJ25/GCM25/GCQ25/GCV25/GCZ25 in selected dates.
13. GCV25 requires exact prior-completed-session three-confirmation roll evidence.
14. Closed Phase A/B, GCG26/GCJ26/GCM26, reviewed, metric-used, or outcome-accessed evidence is
    `CLOSED_RESEARCH_ONLY` and never admitted.
15. Exact frozen GCQ26 30-day hash is sealed metadata; full/superseded GCQ26 cannot substitute.
16. Any final-OOS payload access or nonzero access count is `INVALID` with no promotion.
17. Exact plan fields/defaults and all eight date boundaries are enforced.
18. TRAIN exact half-open interval and boundary equality behavior pass.
19. VALIDATION exact half-open interval and boundary equality behavior pass.
20. CALIBRATION exact half-open interval and boundary equality behavior pass.
21. FINAL_OOS remains metadata-only across its exact half-open interval.
22. All five excluded/quarantine intervals and pre-start burn-in non-emission pass.
23. A 12-bar horizon wholly inside one partition is eligible; any boundary crossing excludes the
    atomic grain, and overlapping horizons stay together or purge together.
24. Minimum 12-bar embargo and longer controlling date gaps are exact and cannot be shortened.
25. Candidate/feature/label positional one-to-one reconciliation passes for bullish evidence.
26. Mirrored bearish evidence reconciles without changing locked feature or label semantics.
27. `SAME_BAR_AMBIGUOUS`, `INCOMPLETE`, and `INVALID` labels are excluded and never recoded.
28. Exact `TARGET_FIRST`, `INVALIDATION_FIRST`, and `TIMEOUT` class mapping and counts pass.
29. Candidate, row, label, source, lineage, detector, contract, date, moment, and outcome mismatch is
    `INVALID`.
30. Contamination join excludes exact overlaps atomically before adequacy counts.
31. Missing contamination proof returns `UNKNOWN`; contradictory proof returns `INVALID`.
32. Exact duplicates are deterministic; contradictory forks enforce precedence and atomicity.
33. TRAIN session/contract/candidate/direction/class thresholds enforce exact values.
34. VALIDATION thresholds enforce exact values without borrowing TRAIN or CALIBRATION evidence.
35. CALIBRATION thresholds enforce exact values without borrowing earlier or OOS evidence.
36. Threshold failure is `UNKNOWN` and cannot change dates, setup, labels, classes, or thresholds.
37. RECORD identity exhaustively enforces every required/forbidden field and sensitivity.
38. PARTITION identity enforces ordered unique records, contracts, interval, and every count.
39. PARTITION_PLAN identity enforces all bounds, horizon, embargo, and forbidden fields.
40. CORPUS identity enforces all lineage, exclusion, count, authority, and sealed-OOS metadata.
41. MANIFEST identity mirrors corpus/partition/record histories and rejects malformed hashes.
42. Exact keyword-only builder parameter names/kinds/defaults, constants, enums, frozen dataclass
    fields/annotations/defaults, exports, and unknown identity behavior pass.
43. Exact reason tokens and `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` precedence pass.
44. Determinably later invalid/ambiguous/unknown group preserves only strictly prior immutable
    evidence and promotes no failing-or-later group.
45. Strictly-later complete append is prefix-invariant and deterministic multi-contract output uses
    exact canonical order.
46. Same-effective append, insertion, repair, reorder, role/contamination/version/plan mutation is
    prefix-ineligible and fail-closed.
47. Conservation, byte-repeatability, Decimal-context independence, zero filesystem/network/clock/
    randomness, and nested exception containment pass.
48. Exact three-path implementation scope, inline fixtures, no package export, no private run,
    training, OOS, model, integration, trading, stage, commit, or push surface pass.

## 23. Verification, Promotion, Rollback, and Stop Conditions

Before future implementation promotion, independent audit must verify exact semantics, 24 numbered
sections, 48 sequential cases, five identity schemas, exact API/exports, frozen contracts, baseline
hashes, formatting, tests, diff, artifact hashes, and exact scope. Focused and full tests use
`-p no:cacheprovider`. Root-wide collection outside `tests` is not substituted for the repository's
accepted test command when ignored private directories are inaccessible.

Fresh cache-disabled regression evidence for this decision is:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py tests/test_gc_feature_label_builder.py tests/test_gc_candidate_evidence_builder.py tests/test_gc_cross_segment_continuity.py
402 passed in 2.37s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 23.60s
```

The final decision-file SHA-256, byte count, and line count are reported after exact-path cached
audit rather than embedded as a self-referential field.

Promotion to a private corpus run requires another committed proposal naming exact input manifests,
source registry, output directory, two-run procedure, hashes, access counters, and STOP conditions.
Training requires a later accepted record after a valid independent corpus exists. Final OOS access,
integration, and trading each remain separately frozen.

STOP immediately and preserve the last valid evidence if:

- a required identity, contamination status, calendar/session, roll, partition, purge, embargo, or
  conservation fact cannot be proved from supplied evidence;
- any final-OOS payload is touched or a sealed source must be replaced;
- a threshold fails or would need tuning;
- a feature/label must be recomputed, repaired, or enriched;
- implementation needs a new dependency, a broader API, or any fourth path;
- regression, determinism, formatting, hash, diff, or scope audit fails.

Before staging, rollback is deletion of the three newly created future implementation files only.
After a local implementation commit, rollback is a normal forward revert of that exact commit,
never a destructive reset. Existing upstream artifacts remain immutable in all cases.

## 24. Final Decision and Resume Boundary

Decision: the independent pretraining-corpus implementation contract is sufficiently explicit for
an independent final audit of this one documentation file. This document does not itself start
implementation.

If this documentation passes independent audit, only this exact file may be staged and committed in
the current bounded task. A future implementation may begin only after this decision commit receives
separate push authorization, is pushed, and post-push readiness confirms the exact three-path scope.
Until then, private runs, Python, tests, fixtures, training, OOS, model work, integration, and all
other files remain frozen.
