# GC Futures Phase A Cross-Segment Continuity Feasibility Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CONTINUITY-FEASIBILITY-V1`.
- Proposal date: `2026-08-16`.
- Proposal status: `DOCUMENTATION_ONLY_CORRECTED`.
- Selected arm: `SHADOW_CONTINUITY_V1`.
- Canonical control arm: `CANONICAL_SEGMENT_LOCAL`.
- Candidate, feature, label, model, OOS, integration, paper, broker, and live
  authority: `NOT GRANTED`.

This proposal specifies one bounded feasibility layer. It does not change any
detector, create a promotable candidate, rerun private data, or claim strategy
edge.

## 2. Decision summary

The proposed layer answers only this question:

> Can complete canonical state at the end of one complete GC development
> session be represented as immutable, auditable references at the boundary of
> the immediately following complete same-contract session, while preserving
> chronology, identity, no-look-ahead, and the accepted segment-local control?

The answer is evidence about representability, not trading usefulness. The
layer may emit boundary assessments and later receiving-segment reference
groups. It may not emit `GCFeatureLabelCandidateEvidence`, features, labels,
orders, scores, or PnL.

## 3. Binding repository baseline

This proposal binds to these accepted bytes:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_structural_seed_evidence.py` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `F2D6754A7456D39C6BCC5EE312024F8C538CFDBD43474BC76957D44B62EBCE0E` |
| `smc/liquidity_map.py` | `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `smc/inducement.py` | `57DA49BE7C99DF9385610749446566323865676817FF8C44D8F8D3868C8C633F` |
| accepted negative-outcome decision | `75DB65DADB89368EE600ED2E59C967136313E5973CF91505CA58F2F8399C0D0B` |
| next-hypothesis selection decision | `77554406D75B81E279409D1D46F3AC44C89FAD6FC08D010D98DA543016B4181E` |

The repository baseline is commit
`1fd50dc661128a5157c6c7399dd236072e82a667`; local `origin/main` matched it
when this proposal began. Any dependency or baseline drift is a STOP condition.

## 4. Intended use and data-quality gate

The intended use is a development-only feasibility decision. The evidence
grain is one ordered adjacent canonical segment pair plus zero or more strictly
later complete receiving effective groups.

The quality gate is:

- completeness: both segments, the calendar boundary, source closure, and each
  emitted receiving group are complete;
- uniqueness: segment IDs, canonical object IDs, histories, and group IDs are
  unique in their exact owning scope;
- validity: canonical identities, lifecycle edges, source moments, and calendar
  versions reconcile;
- integrity: every reference resolves to the exact immutable object already in
  accepted detector evidence;
- timeliness: eligibility is decided at the boundary without future receiving
  observations; and
- leakage: OOS, outcomes, labels, MFE/MAE, returns, and human or LLM judgment
  are unavailable to the decision.

A failed quality dimension is reported explicitly; it is never repaired or
silently excluded to improve the result.

## 5. Exact documentation-only scope

This change creates only:

`docs/gc_futures_phase_a_cross_segment_continuity_feasibility_change_proposal.md`

No Python, test, fixture, private artifact, dataset, dependency, configuration,
package export, runtime, trace, strategy, risk, execution, or integration file
is changed by this proposal. The three pre-existing unrelated untracked
proposal files remain outside scope and untouched.

## 6. Authority and global freeze

Global code freeze remains active. This proposal grants authority only to
describe a future synthetic implementation and its acceptance gate. It grants
no authority to:

- inspect or write private source/result directories;
- execute a continuity run;
- change existing detector or orchestration semantics;
- access OOS bars or alter partitions;
- construct candidate, feature, or label evidence;
- install a model dependency or train/calibrate a model;
- connect local or hosted AI to trading authority; or
- integrate, stage, commit, or push any later implementation without a new
  exact authorization.

## 7. Immutable accepted input contracts

The future analyzer accepts only exact frozen public objects already defined by
the accepted modules:

- one `GCDatasetBuildConfig`;
- one `GCDatasetBuildResult | None`;
- one exact `tuple[GCSplitSessionCalendarEntry, ...] | None` authoritative
  boundary-calendar stream;
- one separate exact `tuple[KillZoneCalendarEntry, ...] | None` candidate
  control-calendar stream;
- one `GCCanonicalSeedEvidence | None`;
- one `GCCandidateEvidenceResult | None`; and
- the exact default `GCCandidateEvidenceConfig()` unless a separately accepted
  candidate configuration is supplied.

`dataset` must be `VALID`, bind zero OOS bars in its manifest, expose only
`DEVELOPMENT` segments to this layer, and reconcile instrument `GC`, timeframe
`5M`, tick size `Decimal("0.1")`, dataset ID, calendar version, timezone-data
version, and segment order. The structural seed and candidate evidence must
bind that same dataset ID and seed ID. Missing top-level context is `UNKNOWN`
only after every supplied counterpart passes independently determinable
validation. Malformed supplied evidence is `INVALID`.

The two calendar streams have distinct, non-interchangeable authority. The
split-session stream alone proves exact tradable intervals and boundary
eligibility. The Kill Zone stream is supplied only to reproduce the already
accepted candidate control through its unchanged public API. Neither stream is
derived from, widened by, collapsed into, or treated as a lossless substitute
for the other. Their normalized calendar versions and overlapping trade-date
session status/open/close facts must not contradict; contradiction is
`INVALID`, and genuinely unavailable control or boundary coverage is
`UNKNOWN` after all supplied evidence validates.

## 8. Exact adjacent-boundary eligibility

Only `dataset.segments[i]` and `dataset.segments[i + 1]` may form a pair. An
eligible pair must satisfy all of the following:

1. both partitions are exactly `DEVELOPMENT`;
2. both contracts are equal;
3. source and receiving segment IDs recompute under the accepted dataset
   contract;
4. both segments contain nonempty, strictly increasing, fully closed 5-minute
   bars with local indices starting at zero;
5. each segment covers one complete authoritative trade-date session and has
   `preceding_missing_bar_count == 0`;
6. the receiving trade date is the next eligible business trade date according
   to the supplied canonical split-session boundary calendar;
7. the source final bar and receiving first bar exactly reconcile to the
   calendar-defined close, next open, and 5-minute bar-close convention; and
8. instrument, timeframe, source role, calendar version, timezone-data version,
   and source-capture lineage are unchanged.

The expected gap is derived from the exact caller-supplied
`GCSplitSessionCalendarEntry.intervals`, not from an assumed fixed duration or
the coarser Kill Zone calendar. Observed source close and receiving open must
match those interval boundaries exactly after UTC normalization. Artifact ID
and SHA-256 tuple lengths, hashes, ordering, uniqueness, and provenance are
validated before eligibility; the dataset ID already binds the accepted
calendar digest.

## 9. Exact ineligibility boundary

A boundary is deterministically `INELIGIBLE` and carries no state when it is:

- a contract roll or expiry;
- a development/OOS, purge, embargo, validation, or final-OOS boundary;
- a weekend or holiday-closed interval;
- an early-close or split-session boundary in V1;
- an unscheduled outage or unresolved calendar interval;
- preceded or followed by a partial, missing, duplicate, reordered, repaired,
  or contradictory bar interval;
- a source ID, coverage ID, timezone-data version, or calendar-version change;
  or
- non-adjacent in accepted dataset order.

Expected maintenance alone does not make a pair eligible; every Section 8
condition is still required. `INELIGIBLE` is a valid assessed outcome, not an
invitation to infer or repair continuity.

## 10. Canonical control-arm reproduction

The implementation calls `build_gc_candidate_evidence()` exactly once with the
supplied dataset config, dataset, exact caller-supplied
`candidate_calendar_entries`, structural seed, and candidate config. The
separate `boundary_calendar_entries` are never passed to that builder. The
continuity module may not synthesize, reinterpret, collapse, or infer either
calendar stream from the other. Absence of either required accepted stream is
`UNKNOWN` after supplied counterparts validate; malformed or contradictory
evidence is `INVALID`.

The reproduced result must be object-equal to `canonical_candidate_evidence`.
Its optional manifest, ordered promoted segment results, candidate references,
statuses, reasons, and blocking reasons must match byte-for-byte. The exact
canonical control digest binds the complete canonical result, not only foreign
IDs. It is the common identity-bearing control value even when the accepted
result is `NONE` or `UNKNOWN` and therefore has no candidate manifest or bundle
ID. A `VALID` control must carry its canonical manifest; a `NONE` or `UNKNOWN`
control must not be rejected merely because its canonical public result has no
manifest. Any object drift stops before boundary promotion.

The accepted negative control is specifically `UNKNOWN`, contains `113`
strictly prior promoted complete segment results, contains `0` candidates, and
has no candidate manifest. The continuity layer may assess only those promoted
complete segment results. It preserves any strictly prior complete boundary or
receiving-group evidence, promotes nothing from the terminal truncated group,
and returns final `UNKNOWN` under Section 18 precedence. It never invents a
candidate bundle ID.

The control arm remains `CANONICAL_SEGMENT_LOCAL`; it is never overwritten by
shadow output.

## 11. Complete source dependency closure

For an eligible source segment, the boundary closure contains every canonical
object that is still usable under its own unchanged lifecycle at the source
session end:

- each `SMCV2LifecycleState.ACTIVE` Equal Liquidity pool, its complete ordered
  transition/snapshot history, source members, first-known provenance, and
  containing result;
- each `DealingRangeState.ACTIVE` range, its complete ordered transitions and
  snapshots, protected/target swing provenance, boundaries, direction, and
  version;
- each exact latest Liquidity Map snapshot for those active range/pool
  identities, including complete ordered classifications and
  reclassifications; and
- every exact structural-seed and dataset bar moment required to validate those
  objects.

Pool-only, range-only, map-only, terminal, forked, incomplete, dangling, or
foreign-ID-only closure is forbidden. An ACTIVE object whose construction or
history is incomplete at the source boundary makes that boundary `INVALID`.
Terminal `SWEPT`, `BROKEN`, `SUPERSEDED`, or `INVALIDATED` state is recorded by
the canonical control but is never carried or reactivated.

## 12. Immutable dependency references

Each carried member is represented by a `GCContinuityDependencyReference`.
The reference binds the owning detector and object kind, canonical object ID,
source segment ordinal and ID, first-known and final effective moments, final
state, complete ordered history IDs, source-moment digest, and full canonical
object digest.

The source-moment digest binds ordered normalized source indices/timestamps and
their exact owning `GCChronologicalBar` payloads. It is validation material,
not a replacement identity. The full object remains in the accepted canonical
input and must resolve exactly once.

References are immutable. The receiving segment may not recompute, mutate,
enrich, repair, renumber, merge, replace, reactivate, or backdate them. No
transition is invented at the boundary and no concatenated-series object ID is
created.

## 13. Receiving Structure Event and FVG groups

Later `DealingRangeStructureEvent` and `FairValueGap` evidence is never carried
from the source segment. It remains exact canonical evidence owned by the
receiving segment and becomes visible only at its original effective moment.

For every strictly later complete receiving group that contains relevant
Structure Event or FVG evidence, a `GCContinuityReceivingGroup` may reference:

- the exact event identity and complete provenance;
- the exact canonical FVG identity, non-null opaque `displacement_id`, and
  complete transition/snapshot history through that moment; and
- the exact receiving-segment source bars needed to reconcile both source
  sequences.

All source moments must reconcile to the receiving segment. Event and FVG
sequences must end at the same confirmation moment and the shorter sequence
must be the exact positional suffix of the longer. Opaque `displacement_id` is
preserved, not independently proved. A stronger unavailable proof is STOP.

Boundary eligibility never depends on a future receiving group. Receiving
groups are appended prospectively and cannot change the immutable boundary ID
or retroactively make an ineligible boundary eligible.

## 14. Exact proposed public API

The future module constant is exactly:

```python
GC_CROSS_SEGMENT_CONTINUITY_VERSION = "GC-CROSS-SEGMENT-CONTINUITY-V1"
```

The module may expose only these keyword-only functions:

```python
make_gc_cross_segment_continuity_id(
    *,
    identity_kind: GCCrossSegmentContinuityIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    boundary_calendar_digest: str,
    candidate_calendar_digest: str,
    timezone_data_version: str,
    seed_id: str,
    canonical_control_digest: str,
    source_segment_ordinal: int | None = None,
    source_segment_id: str | None = None,
    receiving_segment_ordinal: int | None = None,
    receiving_segment_id: str | None = None,
    contract: str | None = None,
    source_trade_date: date | None = None,
    receiving_trade_date: date | None = None,
    source_end_timestamp: datetime | None = None,
    receiving_start_timestamp: datetime | None = None,
    decision: GCCrossSegmentContinuityDecision | None = None,
    reason_tokens: tuple[str, ...] = (),
    dependency_references: tuple[GCContinuityDependencyReference, ...] = (),
    boundary_id: str | None = None,
    effective_index: int | None = None,
    effective_timestamp: datetime | None = None,
    receiving_references: tuple[GCContinuityReceivingReference, ...] = (),
    boundary_ids: tuple[str, ...] = (),
    receiving_group_ids: tuple[str, ...] = (),
) -> str

analyze_gc_cross_segment_continuity(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    boundary_calendar_entries: tuple[GCSplitSessionCalendarEntry, ...] | None,
    candidate_calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    canonical_candidate_evidence: GCCandidateEvidenceResult | None,
    candidate_config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCrossSegmentContinuityResult
```

Positional arguments, alternate names/defaults, convenience overloads, hidden
filesystem inputs, or an `as_of` supplied after evidence selection are
forbidden.

## 15. Exact enums, frozen dataclasses, and exports

The exact enum values are:

```text
GCCrossSegmentContinuityIdentityKind: BOUNDARY, RECEIVING_GROUP, MANIFEST
GCCrossSegmentContinuityDecision: ELIGIBLE, INELIGIBLE
```

All public dataclasses are frozen and have exactly these fields:

```text
GCContinuityDependencyReference:
  detector_name: str
  object_kind: str
  object_id: str
  owning_segment_ordinal: int
  owning_segment_id: str
  first_known_index: int
  first_known_timestamp: datetime
  effective_index: int
  effective_timestamp: datetime
  state: str
  history_ids: tuple[str, ...]
  source_moment_digest: str
  object_digest: str

GCCrossSegmentBoundary:
  boundary_id: str
  source_segment_ordinal: int
  source_segment_id: str
  receiving_segment_ordinal: int
  receiving_segment_id: str
  contract: str
  source_trade_date: date
  receiving_trade_date: date
  source_end_timestamp: datetime
  receiving_start_timestamp: datetime
  decision: GCCrossSegmentContinuityDecision
  reason_tokens: tuple[str, ...]
  dependency_references: tuple[GCContinuityDependencyReference, ...]

GCContinuityReceivingReference:
  detector_name: str
  object_kind: str
  object_id: str
  owning_segment_ordinal: int
  owning_segment_id: str
  first_known_index: int
  first_known_timestamp: datetime
  effective_index: int
  effective_timestamp: datetime
  semantic_discriminator: str
  history_ids: tuple[str, ...]
  source_moment_digest: str
  object_digest: str

GCContinuityReceivingGroup:
  group_id: str
  boundary_id: str
  receiving_segment_ordinal: int
  receiving_segment_id: str
  effective_index: int
  effective_timestamp: datetime
  references: tuple[GCContinuityReceivingReference, ...]

GCCrossSegmentContinuityManifest:
  manifest_id: str
  version: str
  instrument: str
  timeframe: str
  dataset_id: str
  calendar_version: str
  boundary_calendar_digest: str
  candidate_calendar_digest: str
  timezone_data_version: str
  seed_id: str
  canonical_control_digest: str
  boundary_ids: tuple[str, ...]
  receiving_group_ids: tuple[str, ...]

GCCrossSegmentContinuityResult:
  status: SMCV2PrimitiveStatus
  boundaries: tuple[GCCrossSegmentBoundary, ...] = ()
  receiving_groups: tuple[GCContinuityReceivingGroup, ...] = ()
  manifest: GCCrossSegmentContinuityManifest | None = None
  reasons: tuple[str, ...] = ()
  blocking_reasons: tuple[str, ...] = ()
```

The exact public export list is:

```python
__all__ = (
    "GC_CROSS_SEGMENT_CONTINUITY_VERSION",
    "GCCrossSegmentContinuityIdentityKind",
    "GCCrossSegmentContinuityDecision",
    "GCContinuityDependencyReference",
    "GCContinuityReceivingReference",
    "GCCrossSegmentBoundary",
    "GCContinuityReceivingGroup",
    "GCCrossSegmentContinuityManifest",
    "GCCrossSegmentContinuityResult",
    "make_gc_cross_segment_continuity_id",
    "analyze_gc_cross_segment_continuity",
)
```

Imported dependency types are not re-exported. There is no package-root export
or compatibility alias in this phase.

## 16. Exact identity schemas

All IDs are lowercase SHA-256 over canonical typed JSON with sorted object
keys, compact separators, UTC-normalized timestamps, canonical dates, ordered
arrays, and no float coercion.

Common required fields for all three kinds are normalized instrument,
timeframe, dataset ID, calendar version, the SHA-256 digest of the complete
canonical split-session boundary-calendar tuple, the SHA-256 digest of the
complete canonical Kill Zone control-calendar tuple, timezone-data version,
seed ID, and the digest of the complete object-equal canonical candidate
control result. The control digest is required even when the canonical result
is `NONE` or `UNKNOWN` and legitimately has no manifest or bundle ID. Calendar
digests preserve exact
caller order and bind every normalized field; duplicate, reordered, inserted,
removed, repaired, or provenance-mutated entries therefore change identity
and are never silently normalized away.

`BOUNDARY` additionally requires source/receiving ordinals and IDs, contract,
trade dates, source end, receiving start, decision, exact reason tokens, and
ordered dependency references. It forbids `boundary_id`, group effective
fields, receiving references, and manifest ID arrays.

`RECEIVING_GROUP` requires `boundary_id`, receiving ordinal/ID, effective index
and timestamp, and nonempty ordered `GCContinuityReceivingReference` values.
Structure Event references use the exact event type as
`semantic_discriminator` and an empty history; FVG references use the exact
FVG lifecycle state and complete ordered transition/snapshot history. It
forbids source fields, contract/trade dates, boundary
decision/reasons/dependencies, and manifest arrays. Its boundary ID must
recompute from the supplied input boundary.

`MANIFEST` requires exact ordered boundary and receiving-group ID arrays in
addition to the common canonical control digest. It forbids all
boundary/group-specific fields. Every
supplied ID must recompute from an exact public object and appear once in output
order.

Unknown kinds, missing required fields, present forbidden fields, malformed
hashes, bool-as-int values, naive timestamps, duplicate history IDs, unordered
history, or nested malformed values raise only `TypeError` or `ValueError`.

## 17. Deterministic ordering and atomic processing

Boundary assessments preserve accepted dataset adjacency order and use exact
key:

```text
(source_segment_ordinal, receiving_segment_ordinal)
```

Dependency reference order is detector dependency order
`EQUAL_LIQUIDITY`, `DEALING_RANGE`, `LIQUIDITY_MAP`, then the owning canonical
tuple order. No direction, state text, or hash lexical order is a chronology
tie-break.

Receiving groups are ordered by receiving segment ordinal, effective index,
normalized effective timestamp, and exact upstream causal tuple order. All
references at the same effective moment form one atomic group. A group is
promoted only after every nested reference validates. Independent boundaries
at the same normalized moment preserve dataset order.

No supplied tuple is silently sorted, deduplicated, repaired, or truncated.

## 18. Status, cutoff, and immutable prior evidence

Final precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

- `INVALID`: determinable malformed, contradictory, forked, identity-invalid,
  calendar-invalid, control-drift, or incomplete closure evidence;
- `AMBIGUOUS`: multiple distinct canonical objects claim the same required
  identity/causal role at one atomic group and cannot be resolved by accepted
  ordering;
- `UNKNOWN`: required top-level or authoritative coverage is genuinely absent
  after supplied counterparts validate;
- `VALID`: at least one `ELIGIBLE` boundary with complete closure exists and no
  higher condition exists; and
- `NONE`: complete valid input contains no eligible boundary.

A determinably later failure preserves byte-exact strictly prior complete
boundaries and receiving groups, promotes nothing from the failing group or
after it, and returns the higher status. An unknowable effective moment
requires no trusted prefix. `INELIGIBLE` assessments may be retained in a
complete result but have empty carried references.

## 19. No-look-ahead and prefix invariance

Boundary decision and source closure use only evidence known at the source
session close. Receiving observations, event/FVG formation, target result,
future state, label horizon, MFE/MAE, return, PnL, model output, OOS membership,
filename, wall clock, chart annotation, or human/LLM judgment are forbidden.

Receiving groups are emitted only when their complete canonical effective
moment is reached. They cannot mutate the boundary or prior group.

Prefix invariance applies only to a valid prefix ending on a complete boundary
or receiving effective group and extended by strictly later complete evidence.
Same-effective append, partial group, historical insertion, calendar repair,
tuple reorder, source replacement, version mutation, boundary
reclassification, or changed dataset/seed/control identity is prefix-ineligible.

Identical inputs produce object-equal results and byte-identical separately
authorized serialization.

## 20. Canonical-versus-shadow reporting

The manifest binds one canonical control digest and the complete shadow
assessment order. A feasibility report may state only:

- number of assessed, eligible, ineligible, unknown, ambiguous, and invalid
  boundaries;
- reason-token counts;
- complete-closure object counts by detector/object kind;
- number of prospectively emitted receiving event/FVG groups; and
- exact canonical-control equality.

It may not rank, score, optimize, select, or promote boundaries. It may not
report candidate count as a performance target or infer profitability.

The two previously rejected exact event/FVG sequences must remain byte-exact in
the canonical control. Shadow rules may not special-case their dates,
directions, indices, hashes, reasons, or range lifecycle.

## 21. Exact 48-case future acceptance matrix

The future implementation gate contains exactly these numbered logical cases:

1. Exact accepted dataset/config/manifest binding with zero OOS exposure passes.
2. Missing dataset, either exact calendar stream, seed, or canonical control is `UNKNOWN` only after supplied counterparts validate.
3. Malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
4. Dataset, seed, complete canonical control result/digest, dependency version, either complete calendar digest, or tzdata identity drift is `INVALID`.
5. Exact canonical candidate rebuild is object-equal and yields the locked complete control digest whether its optional manifest is present or absent.
6. Canonical status, reason, result, candidate, rejected-sequence, or ordering drift stops before boundary promotion.
7. Exact adjacent dataset ordinals and strictly increasing segment moments pass.
8. Non-adjacent, reordered, duplicated, missing, or replaced segment evidence is rejected without silent sort.
9. Same-contract, DEVELOPMENT-only, source-lineage-stable boundary passes.
10. Contract roll, expiry, partition, source-role, purge, embargo, validation, or OOS boundary is ineligible.
11. Two exact complete standard trade-date sessions with zero preceding missing bars pass.
12. Partial source/receiver session, missing first/last bar, malformed closure, or non-closed bar is `INVALID`.
13. Exact split-session interval close/open, source-artifact provenance, and 5-minute observed gap reconcile.
14. Observed gap mismatch, unresolved outage, duplicate interval, or contradiction between boundary and control calendar evidence is `INVALID`.
15. Weekend and holiday-closed boundaries are deterministically ineligible.
16. Early-close and split-session boundaries are deterministically ineligible in V1.
17. Routine maintenance is eligible only when all exact Section 8 conditions pass.
18. Calendar/runtime timezone normalization handles DST without fixed-offset substitution.
19. Every ACTIVE Equal Liquidity pool resolves exact identity, source members, first-known moment, and full lifecycle history.
20. SWEPT/BROKEN pools remain terminal, are not carried, and cannot reactivate.
21. Every ACTIVE Dealing Range resolves exact identity, version, boundaries, direction, swings, transitions, and snapshots.
22. SUPERSEDED/INVALIDATED ranges remain terminal, are not carried, and cannot reactivate.
23. Latest exact Liquidity Map snapshot/classifications/reclassifications reconcile every carried active range/pool role.
24. Pool-only, range-only, map-only, stale-map, dangling, forked, or incomplete closure is `INVALID` and promotes no partial carry.
25. Every source provenance moment resolves to the exact source-segment bar and source-moment digest.
26. Source observation from another segment, future receiver bar, replaced bar, or backdated provenance is `INVALID`.
27. Dependency and receiving-reference fields, object/history/source digests, state/discriminator, owning segment, and effective moments are sensitive and deterministic.
28. Reference-only carry leaves all canonical dataclasses and foreign identities byte-exact.
29. No boundary transition, renumber, merge, concatenated identity, enrichment, repair, or recomputation occurs.
30. Receiving Structure Event source moments reconcile exactly inside the receiving segment at their original moment.
31. Receiving FVG identity, opaque displacement metadata, transitions, snapshots, and source bars reconcile completely.
32. Event/FVG sequences co-terminate and satisfy the exact positional-suffix rule; mismatch is `INVALID`.
33. Boundary eligibility is unchanged by strictly later receiving evidence and no event/FVG evidence is backdated.
34. Same-effective receiving references are one complete atomic group; partial/forked/contradictory group promotes nothing.
35. Boundary, dependency, and receiving-group ordering follows exact dataset/upstream causal order without hash tie-breaks.
36. Independent eligible/ineligible boundaries remain deterministic under repeated execution.
37. Final precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
38. Determinably later invalid/ambiguous/unknown evidence preserves only byte-exact strictly prior complete evidence.
39. `BOUNDARY` identity exhaustively validates every common/required/forbidden field, both calendar digests, and field sensitivity.
40. `RECEIVING_GROUP` identity exhaustively validates boundary recomputation, effective moment, ordered references, and schemas.
41. `MANIFEST` identity exhaustively validates both calendar digests, the common complete control digest, ordered unique boundary/group histories, and schemas.
42. Malformed hashes, enums, dates, Decimals, bool indices, naive timestamps, calendar artifact provenance, nested references, histories, and exception containment fail closed.
43. Analyzer and identity builder have exact keyword-only parameter names, annotations, kinds, and defaults.
44. Every public dataclass has exact fields, annotations, defaults, and frozen state; enums, version, and exports are exact.
45. Strictly later complete boundary/group append satisfies eligible prefix invariance and repeatability.
46. Same-effective append, insertion, repair, reorder, source/calendar/version mutation, or boundary reclassification is prefix-ineligible.
47. Exact assessed/eligible/ineligible/status/reason/closure/group reporting is deterministic and does not rank or promote evidence.
48. Exact three-path scope, no private run/OOS/candidate/feature/label/model/training/integration/Git side effect, rollback, and STOP pass.

Parameterization may increase collected tests without changing this exact
logical-case count.

## 22. Reserved future implementation scope

If and only if this proposal receives an independent final PASS, the first
future implementation scope is reserved to exactly:

- `analysis/gc_cross_segment_continuity.py`;
- `tests/test_gc_cross_segment_continuity.py`;
- `docs/gc_futures_phase_a_cross_segment_continuity_checkpoint.md`.

No private output root is reserved by this proposal. A private feasibility run
requires a later exact documentation decision after implementation acceptance.
No package export, existing builder/detector edit, fixture, runner, requirements,
configuration, integration, or runtime file belongs to the reserved scope.

## 23. Rollback, promotion, and STOP conditions

Before commit, rollback is deletion of only this proposal. After commit,
rollback requires a bounded revert; history rewriting is forbidden.

STOP on baseline/dependency drift, canonical-control drift, unavailable exact
boundary or control calendar stream, attempted cross-calendar synthesis,
inability to validate complete closure, terminal reactivation,
cross-roll or OOS contact, chronology ambiguity, non-determinism, exception
leakage, test failure, scope drift, private-artifact mutation, or any attempt to
use future evidence for boundary eligibility.

Even a `VALID` feasibility result is non-promotable. It grants no authority for
a shadow private run, candidate creation, feature/label construction, training,
model selection, backtest, profitability claim, local-LLM labelling, runtime
context, risk, execution, paper, broker, live integration, stage, commit, or
push. Failure of feasibility returns the project to retirement of the current
V1 Candidate Evidence hypothesis; it does not authorize another rescue setup.

## 24. Final decision and next single task

The proposed boundary is semantically bounded, falsifiable, and smaller than a
new detector or setup. It preserves the accepted negative result and turns the
documented segmentation blind spot into an explicit data-integrity and
causality test.

Independent semantic/structural audit result: `PASS`. The initial audit corrected two
material issues before acceptance: boundary eligibility now uses only exact
caller-supplied split-session calendar evidence while canonical-control
reproduction uses a separate exact caller-supplied Kill Zone calendar stream;
and the complete canonical digest of each stream is now identity-bearing. The
implementation-readiness audit then corrected two additional material defects:
the accepted canonical control is `UNKNOWN` with `113` promoted complete
segment results, `0` candidates, and no candidate manifest, so the complete
object-equal canonical control digest is now the required common identity value
and no nonexistent candidate bundle ID is required; and that common control
digest is no longer simultaneously forbidden by the `BOUNDARY` and
`RECEIVING_GROUP` schemas. The final document has
exactly `24` sequential numbered sections and exactly `48`
sequential logical cases. All ten dependency hashes in Section 3 match the
accepted bytes, and all three reserved implementation paths are absent.

Fresh regression evidence on `2026-08-16`:

- focused command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py tests/test_gc_structural_seed_evidence.py tests/test_gc_candidate_evidence_builder.py tests/test_inducement.py`;
- focused result: `531 passed in 2.17s`;
- full command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`;
- full result: `2298 passed in 14.63s`; and
- formatting result: `git diff --check` clean for this exact proposal.

The next single task after this accepted proposal is a separately authorized
test-first synthetic implementation limited to the exact three paths in
Section 22. This acceptance does not start implementation, private data, OOS,
candidate, feature/label, training, integration, or remote publication.

Global code freeze remains active.
