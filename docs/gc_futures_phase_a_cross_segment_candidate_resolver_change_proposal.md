# GC Futures Phase A Cross-Segment Candidate Resolver Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1`.
- Date: `2026-08-27`.
- Classification: documentation-only, archived Phase A diagnostic research.
- Repository baseline: `ee0fbbdd3d65278757152e62a79375dda8a91ef3`.
- Baseline subject: `fix(analysis): preserve UNKNOWN continuity manifest`.
- Decision: `PROPOSED_NOT_AUTHORIZED_FOR_IMPLEMENTATION`.
- Promotion authority: none.
- Trading authority: none.

This proposal defines a fresh, bounded, reference-only resolver for one narrow
question: whether an immutable Phase A Inducement pending horizon that ended at
one accepted development segment can be diagnostically reconciled with a
canonical Structure Event/Fair Value Gap receiving group in the immediately
adjacent segment. It does not reopen Phase A, rescue V1, or create candidate,
feature, label, model, OOS, execution, risk, or PnL evidence.

## 2. Decision summary and governance classification

The pushed continuity correction now preserves a deterministic non-null
continuity manifest on the exact historical `UNKNOWN` branch. That preservation
is a prerequisite for a fresh consumer proposal, not evidence that the old V1
hypothesis succeeded.

The resolver proposed here is an archived diagnostic consumer. A resolver
`VALID` status means only that its own immutable cross-segment reference
contract was completely reconciled. It never means that a V1 candidate is
valid, that Phase A is reopened, or that training is allowed.

## 3. Binding repository baseline and artifact evidence

The following committed artifacts are binding inputs to this proposal:

| Artifact | SHA-256 | Bytes | Lines |
| --- | --- | ---: | ---: |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` | 50,867 | 1,202 |
| `analysis/gc_cross_segment_continuity.py` | `FD7688D88930A86CA005DF89A750B94D4A5748EE50F7EC95A288B9B4987AA826` | 58,414 | 1,132 |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` | 110,108 | 2,590 |
| `docs/gc_futures_phase_a_cross_segment_continuity_unknown_manifest_preservation_change_proposal.md` | `8FDDE1B108F2D5987DB699E7A94C3BF0816FDA2F0411A95AA1CE905F653D38F6` | 21,614 | 437 |
| `docs/gc_futures_phase_a_cross_segment_continuity_feasibility_negative_outcome_decision.md` | `624E615255019A5F5B6C2F5D11B77594B62493D6ED1E636941B178B29F27704F` | 16,565 | 374 |

The baseline correction passed `48` focused tests and the full regression suite
with `2581 passed`. These counts describe the pushed baseline only; this
documentation proposal adds no executable test.

## 4. Exact documentation-only scope

This change is limited to this exact file:

- `docs/gc_futures_phase_a_cross_segment_candidate_resolver_change_proposal.md`

No Python, test, fixture, private-data, calendar, configuration, requirement,
package export, integration, training, OOS, stage wiring, or runtime file is in
scope. The proposal does not authorize its reserved implementation paths.

## 5. Authority and global freeze

All existing files remain frozen. Existing detector results, histories,
identities, manifests, negative outcomes, and Phase B/pretraining artifacts are
immutable inputs or out of scope. The resolver has no authority to:

- mutate, enrich, recompute, replace, repair, or silently sort detector output;
- manufacture missing source moments or foreign identities;
- access raw Sierra Chart files, private corpora, final OOS payloads, or network
  resources;
- produce `BUY`, `SELL`, confidence, entry, exit, stop, target, risk, PnL, or
  order instructions; or
- change the status of any upstream result.

## 6. Phase A closure and compatibility boundary

`docs/gc_futures_phase_a_closure_and_phase_b_research_direction_decision.md`
remains controlling:

- Phase A state is `CLOSED_NEGATIVE`;
- Phase A V1 state is `RETIRED_NO_RESCUE`;
- the historical V1 output remains zero candidates; and
- no continuity diagnostic may be promoted into candidate or training evidence.

The resolver is additive and does not replace or wrap
`build_gc_candidate_evidence()`. It cannot create or return
`GCSegmentCandidateEvidence`, `GCCandidateEvidenceManifest`, or
`GCCandidateEvidenceResult`. Existing public APIs and serialized identities stay
byte-for-byte unchanged.

## 7. Exact applicable preserved branch

The resolver may evaluate only a `GCCrossSegmentContinuityResult` satisfying all
of the following:

1. exact type and frozen nested object graph;
2. status `SMCV2PrimitiveStatus.UNKNOWN`;
3. exact reasons and blockers containing only the committed
   `CANONICAL_CONTROL_UNKNOWN` branch required by the preservation contract;
4. non-empty canonical boundaries and receiving groups when present in the
   preserved result;
5. non-null canonical continuity manifest; and
6. exact one-to-one manifest lists for boundary and receiving-group identities.

`INVALID`, `AMBIGUOUS`, `VALID`, `NONE`, null-manifest UNKNOWN, or any other
UNKNOWN reason branch is ineligible and fail-closed. The resolver must not
generalize beyond this exact branch.

## 8. Immutable public input contracts

The proposed analyzer accepts only:

- normalized non-empty `instrument: str` and `timeframe: str`;
- `continuity_result: GCCrossSegmentContinuityResult | None`; and
- `pending_horizon_evidence: tuple[GCSegmentPendingHorizonEvidence, ...] | None`;
  and
- `receiving_group_evidence: tuple[GCSegmentReceivingGroupEvidence, ...] | None`.

`GCSegmentPendingHorizonEvidence` is a new frozen wrapper with exact fields:

- `segment_ordinal: int`;
- `segment_id: str`; and
- `result: InducementPendingHorizonResult`.

The wrapper does not alter `InducementPendingHorizonResult`. Every supplied
pending result, pending horizon, reason token, enum, timestamp, tuple, integer,
and hash must pass exact public-shape validation without exception leakage.

`GCSegmentReceivingGroupEvidence` is a second new frozen wrapper with exact
fields:

- `segment_ordinal: int`;
- `segment_id: str`;
- `receiving_group_id: str`;
- `observations: tuple[InducementObservation, ...]`;
- `structure_event: DealingRangeStructureEvent`;
- `fair_value_gap: FairValueGap`;
- `fair_value_gap_transitions: tuple[FairValueGapTransition, ...] = ()`; and
- `fair_value_gap_snapshots: tuple[FairValueGapSnapshot, ...] = ()`.

This wrapper is canonical public evidence, not raw/private data. Observations
must be fully closed, exact `InducementObservation` instances, timezone-aware
and normalized to UTC, strictly increasing by `(index, normalized timestamp)`,
unique, and internally valid integer-tick OHLC. Boolean integers and naive
timestamps are invalid.

## 9. Continuity manifest and reference validation

The analyzer validates the continuity result as a complete immutable public
object graph. It recomputes only public continuity IDs through
`make_gc_cross_segment_continuity_id()` using supplied public fields. It does
not call private helpers or reproduce opaque upstream object digests.

Every boundary must be adjacent (`receiving_segment_ordinal ==
source_segment_ordinal + 1`), ordered, unique, and mirrored by the manifest.
Every receiving group must reference one supplied boundary, belong to its exact
receiving segment, and be mirrored by the manifest in canonical order.

## 10. Canonical-control opacity and no-revalidation boundary

The continuity manifest fields `dataset_id`, `calendar_version`,
`boundary_calendar_digest`, `candidate_calendar_digest`,
`timezone_data_version`, `seed_id`, and `canonical_control_digest` are copied
only into the new resolver manifest identity.

`canonical_control_digest` is opaque. The resolver must not reconstruct it,
claim it proves candidate sufficiency, or use it to revalidate the historical
candidate control. Any stronger proof would require a separate public contract
and is a STOP condition.

## 11. Pending-horizon ownership and lineage reconciliation

Each pending wrapper must identify exactly one source segment. Wrapper segment
ordinals and IDs are unique, strictly increasing, and must equal an exact
eligible boundary's source ownership. No hidden caller registry is trusted.

Each receiving wrapper must identify exactly one continuity receiving group.
Its segment ordinal and ID must equal both that group's ownership and its
boundary's receiving ownership. Receiving wrappers are unique by group ID and
must already follow the continuity receiving-group order. When multiple groups
belong to one receiving segment, their observation tuples must be byte-equal;
caller-supplied divergent views of one segment are `INVALID`.

For an eligible boundary, a pending horizon can originate only in the exact
source segment. Its `first_known` moment and sweep moment must be at or before
the source segment end. Direction, active range lineage, active range snapshot,
liquidity-map snapshot, external target, internal classification, pool, sweep,
reclaim, available confirmation moments, missing count, and reason token remain
immutable. The exact pending reason is
`NEXT_THREE_CLOSED_BARS_INCOMPLETE`.

## 12. Exact adjacent-boundary next-three-bar mechanics

The Inducement rule remains exactly the next `3` strictly later closed bars.
Let `a` be the length of the pending horizon's available confirmation indices.
The wrapper is eligible only when `0 <= a < 3` and
`missing_confirmation_bar_count == 3 - a`.

Only the immediately adjacent receiving segment may supply the missing
positional suffix. From its canonical observation tuple, take in order only
fully closed observations strictly later than the boundary source-end moment.
The receiving Structure Event confirmation moment must equal one of the first
`3 - a` such observations and therefore occupy one of the remaining positions
`a + 1` through `3`. An event after that exact prefix is ineligible. No second
boundary, wider horizon, elapsed-time substitute, skipped position,
same-effective append, historical insertion, or manual bar repair is allowed.

## 13. Structure Event and Fair Value Gap causal binding

A canonical receiving group and its supplied receiving wrapper contain exactly
one pair in this order:

1. `DEALING_RANGE / STRUCTURE_EVENT`; and
2. `FAIR_VALUE_GAP / GAP`.

Both references must share the receiving segment and exact effective moment.
Their IDs, object digests, source-moment digests, semantic discriminators, and
history tuples must be valid and non-empty where required.

The resolver recomputes the supplied Structure Event ID with
`make_dealing_range_id()` and the supplied GAP, TRANSITION, and SNAPSHOT IDs
with `make_fair_value_gap_id()`. The recomputed event and gap IDs must equal the
two continuity reference IDs. Event and gap directions must match exactly.
FVG transition/snapshot streams must be canonical prefixes complete through
the group effective moment, independently ordered, and one-to-one mirrored.
The exact concatenation of transition IDs followed by snapshot IDs through
that moment must equal the GAP reference `history_ids`. Their state at that
moment must reconcile with the GAP reference semantic discriminator; the
Structure Event type must reconcile with the event reference discriminator.

Every normalized Structure Event provenance source/confirmation moment and
every FVG source moment must match an exact supplied receiving observation.
Both sequences end at the group effective moment, and the shorter normalized
sequence must be the longer sequence's exact positional suffix. The event
confirmation and FVG formation-end moments must each equal that same moment.
Any direction, identity, observation, history, effective-moment, or suffix
mismatch is `INVALID`.

The resolver never reverses, reproduces, or decodes continuity-private object
or source-moment digests. Those digests remain opaque evidence already
validated by the continuity analyzer; supplied public objects add only the
direction, observation-position, canonical identity, and history proof needed
by this resolver. Missing required public receiving evidence is `UNKNOWN`;
independently malformed or contradictory supplied evidence is `INVALID`.
Nothing is inferred from price proximity or a hash lexical order.

## 14. Deterministic matching, selection, and opposing evidence

Matching uses exact direction and source lineage semantics. A pending bullish
sequence requires supplied canonical bullish Structure Event and FVG objects;
a pending bearish sequence requires the exact mirrored bearish objects. The
direction is never inferred from a continuity semantic discriminator, opaque
digest, object ID text, or caller label.

Eligible matches are ordered by:

1. boundary source segment ordinal;
2. pending first-known normalized timestamp;
3. pending sweep index;
4. pending horizon ID;
5. receiving effective index;
6. receiving normalized effective timestamp; and
7. receiving group ID.

The earliest complete match per pending horizon is selected. Exact duplicates
collapse only when all identity-bearing fields match. Same-effective valid
opposing resolutions from distinct canonical receiving groups are
`AMBIGUOUS`; one canonical group cannot carry opposing directions. Forked,
contradictory, or duplicate IDs with different payloads are `INVALID`.
Independent non-opposing source sequences produce deterministic multiple
diagnostic resolutions.

## 15. Atomic processing, status precedence, and prior evidence

Effective groups are processed atomically. No resolution or resolver manifest
is promoted until the complete group validates. A determinably later malformed
group yields final `INVALID`, preserves byte-for-byte every strictly prior
resolution, and promotes nothing from the failing group or later groups.

Final status precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

- `VALID`: at least one complete diagnostic resolution and no higher status;
- `NONE`: complete eligible inputs contain no applicable pending horizon;
- `UNKNOWN`: an eligible horizon cannot be completed from available public
  references, or required top-level context is genuinely unavailable;
- `AMBIGUOUS`: valid same-effective opposing resolutions exist; and
- `INVALID`: independently determinable malformed or contradictory evidence.

## 16. Exact proposed frozen public dataclasses and enums

All proposed dataclasses are `@dataclass(frozen=True)`.

`GCCrossSegmentCandidateResolverIdentityKind(str, Enum)` has exact values:

- `RESOLUTION = "RESOLUTION"`;
- `MANIFEST = "MANIFEST"`.

`GCSegmentPendingHorizonEvidence` fields are locked in Section 8.

`GCSegmentReceivingGroupEvidence` fields and defaults are locked in Section 8.

`GCCrossSegmentCandidateResolution` exact fields are:

- `resolution_id: str`;
- `boundary_id: str`;
- `receiving_group_id: str`;
- `pending_horizon_id: str`;
- `direction: SMCV2Direction`;
- `contract: str`;
- `source_segment_ordinal: int`;
- `source_segment_id: str`;
- `receiving_segment_ordinal: int`;
- `receiving_segment_id: str`;
- `structure_event_id: str`;
- `fair_value_gap_id: str`;
- `sweep_index: int`;
- `sweep_timestamp: datetime`;
- `confirmation_index: int`;
- `confirmation_timestamp: datetime`;
- `first_known_index: int`;
- `first_known_timestamp: datetime`;
- `source_reference_ids: tuple[str, ...]`;
- `receiving_reference_ids: tuple[str, ...]`; and
- `reason_token: str`.

`GCCrossSegmentCandidateResolverManifest` exact fields are:

- `manifest_id: str`;
- `version: str`;
- `instrument: str`;
- `timeframe: str`;
- `dataset_id: str`;
- `calendar_version: str`;
- `boundary_calendar_digest: str`;
- `candidate_calendar_digest: str`;
- `timezone_data_version: str`;
- `seed_id: str`;
- `canonical_control_digest: str`;
- `continuity_manifest_id: str`; and
- `resolution_ids: tuple[str, ...]`.

`GCCrossSegmentCandidateResolverResult` exact fields and defaults are:

- `status: SMCV2PrimitiveStatus`;
- `resolutions: tuple[GCCrossSegmentCandidateResolution, ...] = ()`;
- `manifest: GCCrossSegmentCandidateResolverManifest | None = None`;
- `reasons: tuple[str, ...] = ()`; and
- `blocking_reasons: tuple[str, ...] = ()`.

## 17. Deterministic RESOLUTION and MANIFEST identities

The version is exactly `GC-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1`. Identity
payloads use canonical JSON, normalized UTC timestamps, exact enum values,
ordered tuples, and uppercase SHA-256 hex output.

`RESOLUTION` requires every common field plus every resolution field in Section
16 and forbids `resolution_ids`. `MANIFEST` requires every common provenance
field, `continuity_manifest_id`, and ordered unique `resolution_ids`; it forbids
all resolution-only fields. Unknown identity kinds, Boolean integers, naive
timestamps, malformed hashes, missing required values, or supplied forbidden
values raise only `TypeError` or `ValueError`.

## 18. Exact keyword-only public API

The future module exposes only:

```python
make_gc_cross_segment_candidate_resolver_id(
    *,
    identity_kind: GCCrossSegmentCandidateResolverIdentityKind,
    instrument: str,
    timeframe: str,
    dataset_id: str,
    calendar_version: str,
    boundary_calendar_digest: str,
    candidate_calendar_digest: str,
    timezone_data_version: str,
    seed_id: str,
    canonical_control_digest: str,
    continuity_manifest_id: str,
    boundary_id: str | None = None,
    receiving_group_id: str | None = None,
    pending_horizon_id: str | None = None,
    direction: SMCV2Direction | None = None,
    contract: str | None = None,
    source_segment_ordinal: int | None = None,
    source_segment_id: str | None = None,
    receiving_segment_ordinal: int | None = None,
    receiving_segment_id: str | None = None,
    structure_event_id: str | None = None,
    fair_value_gap_id: str | None = None,
    sweep_index: int | None = None,
    sweep_timestamp: datetime | None = None,
    confirmation_index: int | None = None,
    confirmation_timestamp: datetime | None = None,
    first_known_index: int | None = None,
    first_known_timestamp: datetime | None = None,
    source_reference_ids: tuple[str, ...] = (),
    receiving_reference_ids: tuple[str, ...] = (),
    reason_token: str | None = None,
    resolution_ids: tuple[str, ...] = (),
) -> str

resolve_gc_cross_segment_candidates(
    *,
    instrument: str,
    timeframe: str,
    continuity_result: GCCrossSegmentContinuityResult | None,
    pending_horizon_evidence: tuple[GCSegmentPendingHorizonEvidence, ...] | None,
    receiving_group_evidence: tuple[GCSegmentReceivingGroupEvidence, ...] | None,
) -> GCCrossSegmentCandidateResolverResult
```

No positional parameters, hidden environment input, mutable default, package
export, CLI, configuration flag, runtime hook, or integration wiring is allowed.

The module's exact `__all__` is:

- `GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION`;
- `GCCrossSegmentCandidateResolverIdentityKind`;
- `GCSegmentPendingHorizonEvidence`;
- `GCSegmentReceivingGroupEvidence`;
- `GCCrossSegmentCandidateResolution`;
- `GCCrossSegmentCandidateResolverManifest`;
- `GCCrossSegmentCandidateResolverResult`;
- `make_gc_cross_segment_candidate_resolver_id`; and
- `resolve_gc_cross_segment_candidates`.

## 19. Ordering, no-silent-sort, and prefix invariance

Input boundary, group, pending-wrapper, receiving-wrapper, observation,
pending-horizon, transition, snapshot, and nested history tuples must already
satisfy their canonical order. The analyzer validates but does not silently
sort input.

Outputs use the exact selection key in Section 14. A strictly later complete
append may add later resolutions while preserving all prior resolution
identities byte-for-byte. The earlier manifest remains auditable as the exact
resolution-ID prefix, while the extended manifest receives a new ID because
its ordered `resolution_ids` payload changed. A same-effective append,
historical insertion, reorder, repair, deletion, digest mutation, calendar
mutation, or source segment mutation is not prefix-eligible and must be
rejected or recomputed as a fresh unrelated analysis.

## 20. Exact reason tokens and non-authority semantics

The resolver emits only these exact tokens:

- resolution: `NEXT_THREE_CLOSED_BARS_CONFIRMED_ACROSS_ADJACENT_SEGMENT`;
- valid result: `CROSS_SEGMENT_CONFIRMATION_RESOLVED`;
- none result: `NO_APPLICABLE_CROSS_SEGMENT_HORIZON`;
- unknown result: `CROSS_SEGMENT_CONFIRMATION_UNRESOLVED`;
- ambiguous result: `OPPOSING_CROSS_SEGMENT_CONFIRMATIONS`; and
- invalid result: `INVALID_CROSS_SEGMENT_RESOLVER_EVIDENCE`.

Exact-token near misses, aliases, lowercase variants, or extra prose are
rejected. A resolution is an archived research diagnostic only. It has no
candidate, feature, label, model, score, risk, decision, execution, or trading
authority.

## 21. Inline synthetic exact 48-case future unit-test matrix

The future implementation must preserve exactly `48` logical cases; test
parameterization may increase collected tests without changing this count.

1. All required top-level inputs absent produces genuine `UNKNOWN` without output.
2. Complete inputs with no applicable pending horizon produce `NONE`.
3. Exact preserved canonical-control UNKNOWN branch is accepted.
4. Any other continuity status or UNKNOWN reason branch is rejected fail-closed.
5. Null continuity manifest on the applicable branch is `INVALID`.
6. Boundary and receiving-group manifest lists reconcile exactly.
7. Adjacent source/receiving ordinals are required.
8. Non-adjacent, duplicate, or reordered boundaries are `INVALID`.
9. Pending wrapper exact segment ownership reconciles.
10. Duplicate, reordered, or mismatched pending wrappers are `INVALID`.
11. Exact pending reason token is required.
12. Malformed pending result or nested horizon is contained as `INVALID`.
13. Zero available bars plus three missing bars is eligible.
14. One available bar plus two missing bars is eligible.
15. Two available bars plus one missing bar is eligible.
16. Three available bars is not a pending cross-segment horizon.
17. Missing-count mismatch is `INVALID`.
18. Sweep and first-known moments must not exceed the source end.
19. Receiving evidence must be strictly later than the source end.
20. Same-effective receiving evidence is ineligible.
21. Only the immediately adjacent receiving segment is eligible.
22. A second-boundary confirmation is never used.
23. Exact remaining positional slots complete the three-bar horizon.
24. Skipped, substituted, or wider-horizon positions are rejected.
25. Canonical receiving group has exact Structure Event then FVG references.
26. Receiving wrapper ownership, group ID, and observation order reconcile exactly.
27. Structure Event and GAP canonical IDs recompute and equal their references.
28. Event/FVG directions, effective moments, and exact source suffix reconcile.
29. FVG transition/snapshot history, discriminators, hashes, and mirroring are exhaustive.
30. Opaque canonical-control digest is copied but never recomputed.
31. Exact bullish direction and remaining-bar-position reconciliation resolves deterministically.
32. Exact bearish mirror and remaining-bar-position reconciliation resolves deterministically.
33. Missing receiving proof remains `UNKNOWN`; malformed direction/position proof is `INVALID`.
34. Earliest complete match wins for one pending horizon.
35. Exact duplicates collapse only on full payload equality.
36. Forked duplicate IDs with different payloads are `INVALID`.
37. Same-effective opposing valid resolutions are `AMBIGUOUS`.
38. Deterministic independent multi-resolution ordering is stable.
39. `INVALID` takes precedence over `AMBIGUOUS` and `UNKNOWN`.
40. `AMBIGUOUS` takes precedence over `UNKNOWN` and `VALID`.
41. `UNKNOWN` takes precedence over emitted `VALID` evidence.
42. A later malformed group preserves strictly prior resolution bytes.
43. A failing group and every later group promote nothing.
44. RESOLUTION required/forbidden schema and every field sensitivity are exhaustive.
45. MANIFEST required/forbidden schema and ordered history sensitivity are exhaustive.
46. Exact keyword-only signatures, defaults, frozen fields, enum values, and exports hold.
47. Strictly later resolution-prefix invariance, extended-manifest ID change, and same-effective ineligibility hold.
48. Repeat executions are object-equal and byte-equal; forbidden integration surfaces remain absent.

## 22. Reserved future implementation exact 3-path scope

Only a separate explicit authorization may create or modify exactly:

- `analysis/gc_cross_segment_candidate_resolver.py`;
- `tests/test_gc_cross_segment_candidate_resolver.py`; and
- `docs/gc_futures_phase_a_cross_segment_candidate_resolver_checkpoint.md`.

These paths are reserved, not authorized by this proposal. Package exports,
candidate builder, continuity analyzer, SMC detectors, private-data roots,
training, OOS, engines, configuration, main entry points, and integration files
remain frozen.

## 23. Rollback, promotion, and STOP conditions

Rollback is exact deletion of this documentation-only proposal before commit,
or a later explicit documentation revert. No code or private data requires
rollback because none is authorized here.

Future implementation promotion requires all of the following: independent
semantic audit of this proposal, explicit exact-3-path authorization, test-first
implementation, exact `48`-case reconciliation, focused and full regression
PASS, deterministic identity evidence, cached-diff audit, and a new explicit
commit authorization.

STOP immediately if any of the following is required:

- reopening or rescuing Phase A V1;
- changing an existing public API or identity;
- decoding opaque digests or requiring unavailable raw provenance;
- accessing private data, final OOS, features, labels, training, or outcomes;
- crossing more than one adjacent boundary or widening the three-bar rule;
- introducing candidate, score, risk, execution, or trading authority; or
- modifying any file outside the reserved future exact three paths.

## 24. Final decision and next single task

The fresh cross-segment resolver is formally specified as a non-promotional,
archived, reference-only diagnostic. It is structurally compatible with the
pushed UNKNOWN-manifest preservation and does not contradict the binding Phase
A negative closure.

This proposal alone does not lift the implementation freeze. After this exact
one-file local commit, the task must STOP. The next possible task is an
independent final audit of this proposal; implementation, private execution,
training, OOS, integration, and push require separate explicit authorization.
