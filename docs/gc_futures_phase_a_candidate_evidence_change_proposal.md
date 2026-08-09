# GC Futures Phase-A Candidate-Evidence Change Proposal

## 1. Proposal Record

- Proposal ID: `GC-PHASE-A-CANDIDATE-EVIDENCE-PROPOSAL-V1`.
- Date: `2026-08-08`.
- Baseline commit: `0dcff0d94284a543bed04085dc62fa2de8c9d051`.
- Baseline subject: `docs: accept GC split-session calendar change`.
- Classification: documentation-only orchestration and prerequisite-boundary record.
- Current decision: `CONTRACT_LOCKED_IMPLEMENTATION_STOPPED`.

This proposal defines one deterministic boundary for converting an accepted immutable GC Phase-A
dataset plus separately accepted canonical seed evidence into segment-qualified
`GCFeatureLabelCandidateEvidence` references. It does not claim that canonical real-data seed
evidence or a candidate bundle currently exists, and it does not authorize passing a flattened
multi-segment tuple to the currently committed feature/label builder.

## 2. Decision Summary

The accepted `GCChronologicalBar` evidence can be projected without information loss into every
bar-shaped public detector input. The repository also contains the required standalone Equal
Liquidity, Dealing Range, Liquidity Map, Fair Value Gap, Inducement, and Kill Zone analyzers.

The accepted dataset contains `54` canonical segments, and `GCChronologicalBar.index` restarts at
zero inside every segment. Every standalone analyzer requires one internally coherent local-index
stream. A dataset-global analyzer call would therefore reject valid input or conflate unrelated
segment-local moments. The committed feature/label builder also orders a flattened candidate tuple
by unqualified local index, so direct downstream execution remains prohibited.

The analyzers additionally require caller-supplied confirmed swings, confirmed BOS/CHOCH structure
events, and formation-time FVG context linkage. A separate structural-seed proposal now locks a
deterministic contract for those values, but no production implementation or accepted private seed
exists. Legacy pandas/float market-structure code is not an admissible substitute.

Therefore this proposal locks per-segment orchestration, segment-aware public results, identities,
ordering, private output, and test contracts, but fail-closed stops before Python implementation or
private execution. The structural-seed proposal and this corrected proposal must pass one final
cross-document acceptance audit first.

## 3. Verified Repository Baseline

At the baseline:

- `HEAD` and local `origin/main` both equal
  `0dcff0d94284a543bed04085dc62fa2de8c9d051`;
- the Git index and tracked worktree are clean;
- other untracked documentation proposals exist and are outside this exact one-file scope;
- `smc/smc_v2_context.py` is absent;
- no non-test production caller invokes the six required standalone analyzers as an end-to-end
  chain;
- no production builder creates canonical `DealingRangeSwing`, `EqualLiquiditySwing`,
  `DealingRangeStructureEvent`, or formation-time `FairValueGapContextLink` tuples from immutable GC
  dataset bars;
- `GCChronologicalBar.index` is assigned by `enumerate(members)` separately for each canonical
  segment, so the accepted dataset contains recurring local indices;
- the committed feature/label builder's candidate-order key begins with unqualified local
  `confirmation_index`, so a flattened multi-segment candidate tuple is not a safe downstream API;
- no candidate-evidence bundle, feature-label private output, training split, fitted model, or OOS
  result exists for the accepted pilot.

Historical checkpoint claims are evidence only and are not rerun by this documentation task. The
accepted private readiness audit records `NOT_READY_TRAINING_PROHIBITED`.

## 4. Exact Documentation-Only Scope

This change may create or correct only:

`docs/gc_futures_phase_a_candidate_evidence_change_proposal.md`

It may read committed source, tests, documentation, Git metadata, and private immutable manifest
metadata. It must not modify Python, tests, fixtures, private market data, manifests, calendars,
requirements, configuration, package exports, other documentation, the Git index, commits, remotes,
or integration wiring.

## 5. Authority and Global Freeze

The global code freeze remains active. This record grants no authority to:

- implement or execute the proposed candidate builder;
- derive, repair, infer, label, or enrich swing, event, displacement, or context-link evidence;
- run standalone analyzers on private pilot data;
- create candidate, feature, label, split, training, model, backtest, or OOS artifacts;
- alter strategy, risk, execution, broker, trace, or runtime behavior;
- stage, commit, push, or export private evidence.

Any later authority must name an exact bounded scope. No permission is inherited merely because an
API or private output location is reserved below.

## 6. Accepted Private Dataset Binding

The only future private dataset input is the immutable engineering pilot under:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

Its locked identity is:

- purpose: `NON_PROMOTABLE_ENGINEERING_PILOT`;
- dataset ID: `81e40b6bfc397caf859226ebf16328562a9b8cc148a1cafae9075dc0f82140d8`;
- build-manifest SHA-256:
  `55CA87E55988F9FF27C7C177DBB16813ACFD9096DCB37C370F70A936EDBA4F4C`;
- calendar SHA-256:
  `F137AFA016B4796575EFBC340D48590E6620E1E75837855F0A48C15BE9B3B0ED`;
- calendar version:
  `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`;
- timezone: `America/New_York`;
- timezone-data version: `2026.2`;
- development bars: `7103`;
- OOS bars: `0`;
- canonical segments: `54`;
- acquisition-attested missing parent slots: `73`;
- roll trade dates: `()`.

The pilot is engineering evidence only. It cannot support training promotion, profitability,
generalization, roll robustness, or OOS claims.

## 7. Dataset-Result Reconstruction Boundary

The candidate builder accepts the exact runtime `GCDatasetBuildResult`, not a JSON path or a manually
instantiated approximation. Before any future candidate run, the accepted source, provenance,
coverage, calendar, and configuration bytes must reconstruct the accepted result once through public
dataset APIs and must match the serialized manifest, dataset ID, segments, bars, histories, reasons,
blocking reasons, and counts exactly.

The exact `GCDatasetBuildConfig` remains:

```text
instrument="GC"
timeframe="5M"
tick_size=Decimal("0.1")
source_timezone="Asia/Tokyo"
exchange_timezone="America/New_York"
timezone_data_version="2026.2"
initial_contract="GCJ26-COMEX"
initial_trade_date=date(2026, 2, 23)
roll_confirmation_sessions=3
oos_start_trade_date=date(2026, 3, 31)
oos_end_trade_date=date(2026, 3, 31)
```

Direct JSON-to-dataclass construction, pickle, `eval`, private helpers, partial equality, silent
repair, filesystem-order inference, or a matching dataset ID with differing evidence is forbidden.
Failure to reconstruct exactly stops before seed validation or analyzer calls.

## 8. Accepted Dependency Bytes

Any future implementation or run must stop on dependency drift from these audited bytes:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `DEBD341B3E8CDE3F27E1FAD5DE048E1EF1735F3B4694BC9574A3244255660121` |
| `analysis/gc_feature_label_builder.py` | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `smc/equal_liquidity.py` | `505FAB8F00FC4DDDE73042E5D9CA7764B023565CB6854398C054F9354012BF7B` |
| `smc/dealing_range.py` | `A0178008AF94A9BBC8928AA917FB8C50179E6AAE413E34748DF624E183793E7A` |
| `smc/liquidity_map.py` | `592F79275A2945328969D727946B88361676F0568C0A5A2D0010CE0F9C3F2321` |
| `smc/fair_value_gap.py` | `AC8E9B8123AF6CA233C27CE2AC14A41F41EC87CE43E9807785C12D1619AFDBC1` |
| `smc/inducement.py` | `2D99147494A74CE30757441D7BCF044A7DD403FA25432C4B654916214099D172` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `docs/gc_futures_feature_label_checkpoint.md` | `B4A49A80ED52B6B4E1636BC3342BA18F03A16859F16ACB0152086498598DFD48` |
| `docs/gc_futures_phase_a_structural_seed_evidence_change_proposal.md` | `04DEF7C51D884CC64B9C3B89AD3A41492AAE53371B0DE937B7AAAEE4633E6A1E` |

Hash equality is necessary but not sufficient; exact public signatures, frozen dataclasses, enum
values, detector versions, and identity builders must also pass the future tests.

The structural-proposal hash is bound only in this downstream direction and identifies the
independently re-audited corrected artifact. The structural proposal must not content-hash-bind this
candidate proposal; introducing a mutual document hash dependency is a circular-identity STOP
condition.

## 9. Lossless Bar Projection Contract

Each exact fully closed `GCChronologicalBar` may be projected inside its owning canonical segment,
in original segment tuple order, as follows:

| Target | Exact field projection |
|---|---|
| `EqualLiquidityObservation` | `index`, `timestamp`, `high_tick`, `low_tick`, `close_tick` |
| `DealingRangeObservation` | `index`, `timestamp`, `high_tick`, `low_tick`, `close_tick` |
| `FairValueGapCandle` | `index`, `timestamp`, `open_tick`, `high_tick`, `low_tick`, `close_tick` |
| `InducementObservation` | exact OHLC fields plus `is_closed` |
| `KillZoneObservation` | `index`, `timestamp`, `is_closed` |

No dataframe, float price, resampling, timezone replacement, additional index reset, cross-segment
concatenation, row filtering, gap fill, duplicate collapse, or silent sort is permitted. The locked
zero-based index restart at each accepted segment boundary is preserved exactly. A non-closed bar,
boolean tick, malformed timestamp, OHLC contradiction, non-integer volume, segment mismatch, or
missing canonical bar is `INVALID`.

## 10. Missing Canonical Seed Evidence

The bar projection in Section 9 cannot create these caller-supplied contracts:

- confirmed `DealingRangeSwing` values;
- their exact one-to-one `EqualLiquiditySwing` counterparts;
- confirmed `DealingRangeStructureEvent` BOS/CHOCH values;
- formation-time `FairValueGapContextLink` values, including the opaque non-null
  `displacement_id` required by a qualifying Inducement FVG.

Those values encode confirmation, provenance, identity, and causal decisions that are not fields of
`GCChronologicalBar`. The standalone analyzers validate them but do not derive them. The absence is a
real prerequisite, not missing serialization glue.

## 11. Legacy and Synthetic-Evidence Prohibition

`smc/market_structure.py` and `smc/bos_choch.py` consume mutable pandas dataframes and float prices and
return legacy mutable structures. They are baseline-only code and do not satisfy the canonical V1
integer-tick, immutable provenance, identity, chronology, or fail-closed contracts. They may not be
adapted, rounded, wrapped, or relabeled inside the candidate builder.

Tests, hand-authored IDs, chart drawings, a local or remote language model, future bars, feature
labels, PnL, or a successful downstream match may not invent seed evidence. If a stronger
`displacement_id` proof is required than formation-time opaque metadata, execution stops for a new
public contract; the candidate API is not silently widened.

## 12. Required Canonical Seed Contract

The separately proposed structural-seed implementation must produce one exact immutable
`GCCanonicalSeedEvidence` with these fields and no defaults:

```text
seed_id: str
seed_version: str
instrument: str
timeframe: str
dataset_id: str
source_bar_digest: str
dealing_range_swings: tuple[DealingRangeSwing, ...]
equal_liquidity_swings: tuple[EqualLiquiditySwing, ...]
structure_events: tuple[DealingRangeStructureEvent, ...]
fair_value_gap_context_links: tuple[FairValueGapContextLink, ...]
```

Every source and confirmation moment must reconcile to one exact canonical dataset bar and therefore
one exact canonical segment. Each Equal Liquidity swing must mirror one Dealing Range swing in that
same segment by side, price, provenance, and swing ID. Structure events must bind canonical broken
swings inside one segment, contiguous provenance, exact close-break geometry, confirmation delay,
event identity, and causal order. FVG context links must bind exact same-segment formation-end bars
and matching events; `displacement_id` remains opaque formation-time metadata.

The combined seed tuples are ordered by accepted segment ordinal and then by the locked local causal
order. The candidate builder partitions them by full source and confirmation moments, never by a
foreign hash alone. A public swing, event, or link ID may validly recur in different segments because
its foreign schema can omit segment identity; recurrence is not duplication when the segment-qualified
moments differ. No hash or direction lexical order is a chronology tie-break. Seed identity ownership
belongs to the separately accepted structural-seed contract; this candidate builder validates and
references it without recomputing unavailable foreign formation identities.

After exact dataset reconstruction and before any segment projection or analyzer call, the builder
calls `validate_gc_structural_seed_evidence()` exactly once with the supplied `dataset_config`, exact
runtime `dataset`, supplied `structural_seed`, and exact default `GCStructuralSeedConfig()`. The
returned seed must be object-equal to the supplied value. `VALID` with a nonempty canonical seed and
`NONE` with the canonical dataset-bound empty seed are admissible; `INVALID`, `AMBIGUOUS`, `UNKNOWN`,
`NONE` without a bound seed, or any unequal/replaced value stops without analyzer calls. The
candidate builder never implements a weaker parallel seed validator.

## 13. Exact Proposed Public API

The future module constant is exactly:

```python
GC_CANDIDATE_EVIDENCE_VERSION = "GC-CANDIDATE-EVIDENCE-V1"
```

The future candidate module may expose only this keyword-only function surface:

```python
make_gc_candidate_evidence_id(
    *,
    identity_kind: GCCandidateEvidenceIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    calendar_version: str,
    timezone_data_version: str,
    seed_id: str,
    config: GCCandidateEvidenceConfig,
    detector_versions: tuple[tuple[str, str], ...],
    segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...],
    candidate_references: tuple[tuple[str, str], ...],
    bundle_id: str | None = None,
) -> str

build_gc_candidate_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCCandidateEvidenceConfig = GCCandidateEvidenceConfig(),
) -> GCCandidateEvidenceResult
```

`identity_kind` has exact values `BUNDLE` and `MANIFEST`. `BUNDLE` forbids `bundle_id`;
`MANIFEST` requires it and requires exact recomputation of the referenced bundle identity.
`segment_result_ids` and `candidate_references` are required, ordered, segment-qualified arrays;
flat `result_ids` or `candidate_ids` parameters are forbidden. Unknown kinds, positional arguments,
extra parameters, alternate defaults, or convenience overloads are forbidden.

## 14. Exact Proposed Frozen Dataclasses

The future public dataclasses are frozen and have exactly these fields:

```text
GCCandidateEvidenceConfig:
  equal_liquidity_config: EqualLiquidityConfig = EqualLiquidityConfig()
  dealing_range_config: DealingRangeConfig = DealingRangeConfig()

GCSegmentCandidateEvidence:
  segment_ordinal: int
  segment_id: str
  evidence: GCFeatureLabelCandidateEvidence

GCCandidateEvidenceSegmentResult:
  segment_ordinal: int
  segment_id: str
  equal_liquidity_result: EqualLiquidityResult
  dealing_range_result: DealingRangeResult
  liquidity_map_result: LiquidityMapResult
  fair_value_gap_result: FairValueGapResult
  inducement_result: InducementResult
  kill_zone_result: KillZoneResult
  result_ids: tuple[str, ...]

GCCandidateEvidenceManifest:
  manifest_id: str
  bundle_id: str
  version: str
  instrument: str
  timeframe: str
  tick_size: Decimal
  dataset_id: str
  calendar_version: str
  timezone_data_version: str
  seed_id: str
  config: GCCandidateEvidenceConfig
  detector_versions: tuple[tuple[str, str], ...]
  segment_result_ids: tuple[tuple[str, tuple[str, ...]], ...]
  candidate_references: tuple[tuple[str, str], ...]

GCCandidateEvidenceResult:
  status: SMCV2PrimitiveStatus
  candidates: tuple[GCSegmentCandidateEvidence, ...] = ()
  segment_results: tuple[GCCandidateEvidenceSegmentResult, ...] = ()
  manifest: GCCandidateEvidenceManifest | None = None
  reasons: tuple[str, ...] = ()
  blocking_reasons: tuple[str, ...] = ()
```

`GCCanonicalSeedEvidence` is the exact immutable dependency contract in Section 12; its defining
module and identity builder remain blocked on the structural-seed proposal. The candidate module may
import that accepted type but may not redefine a lookalike.

The exact public export list is:

```python
__all__ = (
    "GC_CANDIDATE_EVIDENCE_VERSION",
    "GCCandidateEvidenceIdentityKind",
    "GCCandidateEvidenceConfig",
    "GCSegmentCandidateEvidence",
    "GCCandidateEvidenceSegmentResult",
    "GCCandidateEvidenceManifest",
    "GCCandidateEvidenceResult",
    "make_gc_candidate_evidence_id",
    "build_gc_candidate_evidence",
)
```

`GCCanonicalSeedEvidence`, `GCStructuralSeedConfig`, and
`validate_gc_structural_seed_evidence` are imported for dependency validation but are not
re-exported. The two segment-qualified wrappers are aggregation records, not detector mutations. No
detector input, convenience alias, private helper, training type, or integration type is public.

## 15. Exact Standalone Analyzer Calls

After complete input validation, including the exact one-time public structural-seed validation in
Section 12, the implementation iterates exact `dataset.segments` tuple order. For each segment that
is reached before a fail-closed cutoff, it partitions seed members by exact full
source/confirmation moments, projects only that segment's bars, and calls each analyzer exactly once
in this order:

1. `analyze_equal_liquidity()` with seed Equal Liquidity swings and projected observations;
2. `analyze_dealing_ranges()` with seed Dealing Range swings, projected observations, and seed events;
3. `analyze_liquidity_map()` with canonical Dealing Range swings, Equal Liquidity pools, and range
   snapshots;
4. `analyze_fair_value_gaps()` with projected candles and seed context links;
5. `analyze_inducements()` with complete outputs and projected Inducement observations;
6. `analyze_kill_zones()` with projected observations and the exact canonical calendar entries whose
   trade dates fall within that segment's inclusive first/last trade-date bounds.

All six calls for one complete segment finish before the next segment begins. No analyzer receives
bars, seed members, detector outputs, or lifecycle state from another segment. An `INVALID`,
`AMBIGUOUS`, or `UNKNOWN` analyzer result stops the current chain and every later segment without
creating a partial segment result. `VALID` and `NONE` are complete detector results and do not by
themselves skip a downstream call.

The default `EqualLiquidityConfig(tolerance_ticks=2, minimum_members=2,
minimum_separation_bars=3)` and `DealingRangeConfig(swing_confirmation_bars=2,
break_buffer_ticks=1)` are explicit identity-bearing configuration. `detector_versions` is exactly,
in Section 15 analyzer order:

```text
(('EQUAL_LIQUIDITY', 'SMC-V2-EQUAL-LIQUIDITY-1'),
 ('DEALING_RANGE', 'SMC-V2-DEALING-RANGE-1'),
 ('LIQUIDITY_MAP', 'SMC-V2-LIQUIDITY-MAP-1'),
 ('FAIR_VALUE_GAP', 'SMC-V2-FAIR-VALUE-GAP-1'),
 ('INDUCEMENT', 'SMC-V2-INDUCEMENT-1'),
 ('KILL_ZONE', 'SMC-V2-KILL-ZONE-1'))
```

No missing, extra, duplicate, reordered, aliased, or version-drifted member is accepted. No analyzer
is recursively recalled, bypassed, monkey-patched, replaced by a legacy analyzer, or run only on a
favorable subset.

## 16. Candidate Assembly Contract

For each canonical Inducement and matching snapshot inside one complete segment result, the builder
selects only exact referenced objects already present in that same segment's complete detector
outputs:

- the latest valid ACTIVE external `DealingRangeSnapshot` strictly before the sweep group;
- the exact matching `LiquidityMapSnapshot`, external target classification, internal-pool
  classification, and swept `EqualLiquidityPool`;
- the confirmed `DealingRangeStructureEvent` and causally linked `FairValueGap` with complete ordered
  transition/snapshot history through confirmation;
- the exact `KillZoneContext` and containing snapshot at confirmation;
- the exact fully closed `GCChronologicalBar` at confirmation.

The event and FVG normalized source-moment sequences must end at the confirmation moment and the
shorter must be an exact positional suffix of the longer. Only verified `NEW_YORK_AM` context in an
OPEN or EARLY_CLOSE session is feature-eligible. The builder references detector outputs; it does not
recompute, mutate, enrich, repair, or reinterpret them.

Every selected candidate is wrapped as `GCSegmentCandidateEvidence` with the exact accepted segment
ordinal and segment ID. Its confirmation bar must occur exactly once in that segment and in no other
segment-qualified candidate context. No cross-segment reference match is allowed. The raw evidence
object remains byte-identical to the downstream dataclass; the wrapper supplies orchestration-owned
segment provenance that the foreign detector identities do not contain.

## 17. Deterministic Ordering and Same-Moment Atomicity

Dataset segments and bars preserve accepted canonical order. Every supplied seed and analyzer tuple
must already satisfy its public no-silent-sort contract. Candidate output is the concatenation of
each complete segment's exact `InducementResult.inducements` order. Its exact ordinal key is:

```text
(segment_ordinal,
 inducement_tuple_ordinal)
```

For every wrapper, `segment_id` must match `dataset.segments[segment_ordinal].segment_id`, and the
wrapped confirmation `(index, normalized timestamp)` must equal that exact Inducement tuple member's
moment. The public Inducement tuple has already applied its locked local causal ordering and
same-effective atomicity; the candidate builder must not re-sort it. `segment_id`, direction, and
hashes validate identity and grouping but are never chronology tie-breaks.

Equal effective moments inside one segment form one complete atomic group. Exact duplicates may
collapse only when all referenced objects are byte-equivalent and the downstream contract permits
it. Opposing valid directions at one local effective group are `AMBIGUOUS` and promote no candidate
from that group. Same local index values in different segments are independent, not one atomic group.

## 18. Status, Cutoff, and Immutable Prior Evidence

Final status precedence is exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Missing dataset, calendar, or structural seed is `UNKNOWN` only after every supplied counterpart has
passed independently determinable validation. Malformed supplied evidence is `INVALID` and is never
masked by missing context. A determinably later failing group preserves complete strictly prior
immutable candidates and complete prior `GCCandidateEvidenceSegmentResult` values, promotes no
partial result or candidate from the failing segment or after it, and returns `INVALID`. Unknowable
segment/effective moment requires no trustworthy prefix.

`VALID` requires at least one complete candidate and no higher-precedence condition. A complete
valid run with no candidate is `NONE`. Analyzer-specific `UNKNOWN`, `AMBIGUOUS`, and `INVALID`
conditions retain their higher aggregate precedence; the orchestrator may not downgrade them.

## 19. Identity and Manifest Contract

`BUNDLE` identity binds normalized instrument/timeframe, exact `Decimal("0.1")`, dataset ID,
calendar version, timezone-data version, seed ID, the exact full frozen candidate config, the exact
Section 15 detector name/version tuple, ordered `segment_result_ids`, and ordered
`candidate_references`. `MANIFEST` additionally binds the exact recomputed bundle ID. All IDs are
lowercase SHA-256 over canonical typed JSON with sorted object keys, compact separators, normalized
UTC timestamps, canonical Decimal text, and ordered arrays.

Each `GCCandidateEvidenceSegmentResult.result_ids` contains exactly six deterministic full-result
digests in Section 15 analyzer order. A digest binds segment ordinal/ID, detector name/version, the
applicable exact candidate configuration, exact public result status, full ordered outputs, reasons,
blocking reasons, and all nested immutable fields; it is not a digest of foreign IDs alone.
`segment_result_ids` is exactly the dataset-order tuple `(segment_id, result_ids)` for every complete
promoted segment and is never hash-sorted.

`candidate_references` is exactly `(segment_id, inducement_id)` one-to-one in candidate output order.
The same foreign result or Inducement ID may recur in different segments and remains distinct because
every reference is segment-qualified. Repetition inside the same segment is permitted only under the
public detector's exact-duplicate rule. `segment_result_ids` contains each complete promoted segment
exactly once, uses that segment's exact ID, and contains no missing, extra, empty, reordered, or
duplicate segment member. A `VALID` bundle has nonempty `candidate_references`; every reference must
resolve to exactly one wrapper and to that wrapper's same-segment canonical Inducement. A non-VALID
aggregate may expose immutable complete prior segment results and candidates but must not synthesize
a bundle or manifest. A manifest is created only after every segment result and candidate wrapper
validates in memory.

## 20. Point-in-Time, Prefix, and Side-Effect Boundaries

Candidate eligibility uses only evidence known at the confirmation close. Future target hits, label
outcomes, horizon data, feature values, trades, entry/exit, risk, PnL, model scores, LLM output, OOS
roles, filenames, current time, and filesystem enumeration order are forbidden inputs.

Within one validated run, complete earlier segment results and candidate wrappers are immutable when
strictly later complete segments are processed. Candidate discovery inside the current segment is
provisional and promotes no public wrapper or segment result until all six analyzer calls and the
whole segment validate. Public prefix invariance therefore applies only at complete segment
boundaries. Cross-run byte-prefix comparison is eligible only when dataset, seed, calendar,
configuration, and dependency identities are unchanged; appending bars that changes dataset or seed
identity is not an eligible byte-prefix claim. Same-effective append, partial segment, historical
insertion, repair, reorder, segment mutation, calendar mutation, dataset/seed identity change, or
dependency drift is ineligible and fails closed.

The module performs no file, network, environment, clock, model, training, strategy, risk, execution,
trace, or broker I/O. Private serialization, if separately authorized, occurs outside the public
builder only after exact result validation.

## 21. Exact 48-Case Future Acceptance Matrix

The future implementation gate contains exactly these numbered logical cases:

1. Exact accepted dataset reconstruction and manifest equality pass.
2. Dataset byte, identity, segment, bar, source, count, or role mutation is `INVALID`.
3. Exact calendar, timezone, version, and runtime tzdata reconciliation pass.
4. Missing dataset/calendar/seed is `UNKNOWN` only after supplied counterparts validate.
5. Malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
6. Nonzero or exposed OOS evidence stops before analyzer calls.
7. Every fully closed bar projects losslessly inside its exact owning segment to all five bar-shaped input types.
8. Segment-local zero reset passes; cross-segment concatenation, added reset, malformed, reordered, duplicated, or contradictory bars are `INVALID`.
9. Exact one-time public seed validation proves type, version, config, dataset binding, source-bar digest, seed ID, object equality, and segment-qualified source moments before analyzers.
10. Seed missing, higher-status, unequal, unbound-empty, and canonical bound-empty semantics are distinct and promote no synthetic evidence.
11. Dealing Range swing source/confirmation moments reconcile to exact bars in exactly one segment.
12. Equal Liquidity swings mirror Dealing Range swings one-to-one inside that same segment.
13. Structure-event provenance, broken swing, close-break, delay, identity, and local order reconcile without cross-segment hash matching.
14. FVG context links reconcile same-segment formation moments and structure-event references.
15. Opaque `displacement_id` is preserved; unavailable stronger proof triggers STOP.
16. Seed segment/member reorder, fork, same-segment duplicate, historical repair, or hash-order chronology is rejected while valid foreign-ID recurrence across segments remains distinct.
17. Exact per-segment Equal Liquidity call, defaults, status, pools, and reason tokens reconcile.
18. Exact per-segment Dealing Range call, defaults, ranges, transitions, and reasons reconcile.
19. Exact per-segment Liquidity Map call, snapshots, classifications, reclassifications, and reasons reconcile.
20. Exact per-segment FVG call, gaps, complete transitions/snapshots, and reasons reconcile.
21. Exact per-segment Inducement call, observation/source suffix binding, outputs, and reasons reconcile.
22. Exact per-segment Kill Zone call, bounded calendar slice, verified context, snapshots, and reasons reconcile.
23. Each analyzer is called exactly once per reached segment in fixed dependency order; no state crosses a segment boundary.
24. Analyzer exceptions and higher statuses stop the current chain/later segments, preserve complete prior segments, and never promote a partial segment result.
25. Bullish external target, internal pool, sweep, reclaim, event, and FVG roles reconcile.
26. Bearish mirror roles and geometry reconcile.
27. Latest pre-sweep ACTIVE range and map snapshot selection is deterministic.
28. FVG history is complete through confirmation and mirrors transitions one-to-one.
29. Kill Zone context is exact verified `NEW_YORK_AM` OPEN/EARLY_CLOSE evidence.
30. Confirmation bar matches Inducement, event, FVG, Kill Zone, exact segment ordinal/ID, and trade date.
31. Wrapped candidate contains exact segment provenance plus the byte-identical fourteen-field downstream evidence object.
32. Candidate ordering is segment ordinal then exact public Inducement tuple order, with no global local-index or hash sort.
33. Exact duplicate same-group evidence follows the locked collapse rule; recurring foreign IDs in different segments do not collapse.
34. Opposing valid same-group candidates inside one segment are atomic `AMBIGUOUS`; equal local moments across segments are independent.
35. Independent valid candidates across and within segments retain deterministic segment-qualified order.
36. Final precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
37. Determinably later invalid evidence preserves only complete prior segment results and strictly prior immutable candidates.
38. Pending/uncertain later evidence and partial analyzer chains cannot be promoted as a candidate or segment result.
39. `BUNDLE` exhaustively validates config, exact detector-version order, ordered segment-result IDs, segment-qualified candidate references, recurrence, and every required/forbidden field sensitivity.
40. `MANIFEST` mirrors config, detector versions, segment-result/candidate-reference arrays, and recomputes the exact bundle identity.
41. Malformed segment ordinal/ID, hashes, enums, timestamps, Decimals, nested tuples, result digests, and histories fail closed.
42. Builder and identity builder have exact corrected keyword-only names, kinds, annotations, and defaults; flat result/candidate ID parameters are rejected.
43. Every public dataclass, including both segment wrappers, has exact fields, annotations, defaults, and frozen state.
44. Exact enum values, detector versions, module version, corrected exports, and foreign-ID recurrence boundary reconcile.
45. Complete earlier segment results and candidate wrappers remain byte-exact during later-segment processing; no current-segment provisional candidate is publicly promoted.
46. Same-effective append, partial segment, insertion, repair, reorder, segment/calendar/seed/version mutation, or changed dataset identity is prefix-ineligible.
47. Repeat execution preserves object equality, segment/result/candidate order, and any separately authorized serialization bytes.
48. Exact code/private scope, downstream feature-builder global-index incompatibility STOP, no training/OOS/model/runtime/Git side effect, and rollback pass.

Parameterization may increase collected tests without changing this exact logical-case count.

## 22. Reserved Future Scope and Private Output

After the structural-seed prerequisite is independently accepted, the first candidate implementation
scope is reserved to exactly:

- `analysis/gc_candidate_evidence_builder.py`;
- `tests/test_gc_candidate_evidence_builder.py`;
- `docs/gc_futures_phase_a_candidate_evidence_checkpoint.md`.

The separately authorized private-run root is reserved to exactly:

`private_data/sierra_chart/gc_2026_phase_a_candidate_evidence/`

It may contain only an input-binding JSON, segment-qualified candidate JSONL, per-segment
detector-result JSON, manifest JSON, validation report, and README, all marked
`NON_PROMOTABLE_ENGINEERING_PILOT`. Candidate records must contain segment ordinal/ID plus the exact
fourteen-field evidence payload. Seed bytes are referenced by ID/hash and are not duplicated. The
accepted pilot directory remains immutable. No external fixture, feature/label output, training
split, model, integration artifact, or tracked private data is allowed.

## 23. Rollback, Promotion, and Stop Conditions

Before private execution, rollback is removal of only the new candidate private-output directory;
accepted pilot and seed inputs remain immutable. A failed private run is quarantined by exact hashes
and validation evidence and is never overwritten, repaired in place, or relabeled successful.

Stop immediately on missing accepted structural seed, unavailable canonical swing/event derivation,
structural-seed validator mismatch/non-admissible status, unresolved displacement provenance,
dependency/API drift, dataset reconstruction mismatch, calendar or tzdata mismatch, malformed or
reordered evidence, incomplete history, identity mismatch,
cross-segment analyzer input/state, flat unqualified result/candidate IDs, foreign-ID-only matching,
non-determinism, exception leakage, test failure, OOS contact, scope drift, unexpected I/O, or any
request for feature/label execution, training, model selection, profitability, strategy, risk,
execution, integration, stage, commit, or push without separate authority.

The current `analysis/gc_feature_label_builder.py` local-index ordering contract is an explicit later
STOP boundary. Candidate implementation may not alter that file, silently flatten wrappers, or call
the builder. A separate documentation proposal and bounded correction are required before any
feature/label execution.

Promotion is forbidden. Passing synthetic tests or an engineering pilot cannot establish strategy
edge, model quality, generalization, production readiness, or trading authority.

## 24. Final Decision and Next Single Task

The corrected downstream candidate-evidence orchestration is now segment-safe and auditable, but
implementation readiness remains `FAIL-CLOSED STOP`. The exact bar projections and analyzer APIs
exist, and the sibling structural-seed proposal locks the missing derivation contract, but neither
production implementation nor accepted private seed evidence exists. The committed feature/label
builder also remains incompatible with a flattened multi-segment local-index tuple.

The next single task is an independent documentation-only cross-audit of exactly:

- `docs/gc_futures_phase_a_structural_seed_evidence_change_proposal.md`;
- `docs/gc_futures_phase_a_candidate_evidence_change_proposal.md`.

That audit must prove mutual consistency for segment partitioning, analyzer invocation, result and
candidate qualification, foreign-ID recurrence, no-silent-sort behavior, status cutoff, identities,
exact matrices, reserved scopes, and downstream STOP boundaries. PASS may authorize staging only
those exact documentation files; it must not begin structural-seed/candidate Python, private run,
feature/label correction, training, OOS access, integration, commit, or push. The global code freeze
remains active.
