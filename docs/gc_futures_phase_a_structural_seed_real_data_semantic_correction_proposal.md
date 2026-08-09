# GC Futures Phase A Structural Seed Real-Data Semantic Correction Proposal

## 1. Decision record

This document is a documentation-only proposed correction to the bounded GC
Phase A structural-seed contract. It is not operationally effective until an
independent semantic and structural audit passes and a separate implementation
authorization is granted.

The proposal corrects a real-data discriminator that the existing inline
synthetic matrix did not exercise. It does not authorize Python changes, test
changes, private-data mutation, dataset rebuilding, candidate-evidence work,
training, OOS access, integration, staging, commit, or push.

The global code freeze remains active outside this single documentation file.

## 2. Bounded objective

The objective is to distinguish three causally different observations without
look-ahead:

1. a close breaks an unretired swing but does not break the exact active
   protected swing;
2. one close breaks the exact active protected swing and one or more other
   same-side swings;
3. a close occurs before enough two-sided confirmed swing context exists to
   initialize the first structural event.

The corrected contract must derive a deterministic non-event, exact protected
CHOCH, or pre-eligibility non-event respectively. These conditions must not be
collapsed into a dataset-wide `STRUCTURE_UNKNOWN` result.

## 3. Exact scope and freeze boundary

The only file authorized by the present documentation task is:

- `docs/gc_futures_phase_a_structural_seed_real_data_semantic_correction_proposal.md`.

A future implementation exception, if separately authorized after this proposal
passes audit, is reserved to exactly:

- `analysis/gc_structural_seed_evidence.py`;
- `tests/test_gc_structural_seed_evidence.py`;
- `docs/gc_futures_phase_a_structural_seed_evidence_checkpoint.md`.

No external fixture is allowed. The accepted private dataset, private manifests,
candidate-evidence implementation, Dealing Range implementation, shared SMC
primitives, configuration, package exports, engines, runtime, storage, training,
and integration surfaces remain frozen.

## 4. Verified repository baseline

The read-only audit baseline is:

- repository `HEAD`: `41e6e02bd8a2b1f5f81b49702c707c046417d7c2`;
- local `origin/main`: the same commit;
- structural source SHA-256:
  `B799EE739ECE289A57680007D85566645EE1615B0E20F87C99A4278217AE9AAE`;
- structural tests SHA-256:
  `CFD789AE272B621EC04CC463A5EE506C22B3221A3F18EA6C737999042420958E`;
- structural checkpoint SHA-256:
  `75C0D52D58BF2C8168806893FF68B0F567F19401FFA0DABE3EC0DB8A970094E1`;
- parent structural proposal SHA-256:
  `04DEF7C51D884CC64B9C3B89AD3A41492AAE53371B0DE937B7AAAEE4633E6A1E`;
- private-run proposal SHA-256:
  `77631A804BE6A3C0532B3708E3FC0727ABCFC0746B4598F53832F81DBC4A6018`.

The three pre-existing user-owned untracked proposal files are outside this
scope and must remain untouched.

## 5. Accepted V3 input evidence

The exact accepted V3 dataset reconstructed as `VALID` with dataset ID:

`a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`.

Build and independent validation of structural evidence were object-equal and
both failed closed as:

- status: `UNKNOWN`;
- reasons: `("STRUCTURE_UNKNOWN",)`;
- blocking reasons: `("STRUCTURE_UNKNOWN",)`;
- seed: `None`.

No accepted structural output directory was published. The accepted V3 dataset
and its acquisition artifacts remain immutable and are not evidence of data
corruption merely because downstream structure derivation returned `UNKNOWN`.

## 6. Exact real-data audit findings

Production helpers were applied segment by segment without changing source or
private data. The exact profile was:

- 54 development segments;
- 7,103 development bars;
- 28 failed segments and 26 locally completed segments;
- 6,974 bars in failed segments and 129 bars in completed segments;
- 22 failures with reason `a reversal did not break the active protected swing`;
- 6 failures with reason `a required protected swing is not yet confirmed`;
- only 5 events in all 26 locally completed segments.

Of the 22 reversal mismatches:

- 19 did not cross the active protected swing at all; a different same-side
  swing was crossed;
- 3 crossed the active protected swing, but the global price-extreme selector
  chose a different crossed swing.

All 6 missing-protected failures happened during the initial event attempt at
early segment-local indices 7 through 11. Twenty-four of the 28 failed segments
were full 276-bar sessions. Only two failed segments were preceded by a missing
bar gap. Therefore fragmentation and source gaps are not the primary root cause.

## 7. Confirmed semantic root cause

The current implementation first selects the highest crossed HIGH or lowest
crossed LOW from every unretired same-side swing. It retires the complete crossed
group and only afterward checks whether a reversal selected the exact active
protected swing.

That ordering turns a deterministic non-CHOCH observation into `UNKNOWN` and can
also hide an actually crossed protected swing behind a more extreme unrelated
swing. The top-level all-or-nothing containment then discards all segment evidence
and returns no seed.

This is a semantic coverage defect, not exception leakage or nondeterminism.
The existing focused and full suites pass because they lock current behavior but
do not discriminate the 19 non-protected-only, 3 protected-plus-other, and 6
pre-eligibility patterns observed in the accepted V3 data.

## 8. Normative interpretation boundary

A raw one-tick close-through is necessary but not sufficient to emit a public
`DealingRangeStructureEvent`. Event qualification also requires the causal state
needed to type the event and bind its protected role.

After this correction is independently accepted, it supersedes only the parent
structural proposal's Section 11 statements that require generic price-extreme
selection before reversal reconciliation, its blanket missing-protected
`UNKNOWN` treatment, and the corresponding logical Cases 21 through 30 to the
extent they conflict with Sections 10 through 20 here. Every non-conflicting
parent contract remains normative. Until acceptance, the committed parent
proposal remains the operational freeze boundary.

Accordingly:

- a broken swing is not automatically a structural event;
- a non-event is not missing evidence and is not `UNKNOWN`;
- a supplied public Structure Event without its required protected relationship
  remains invalid or unknown under the downstream Dealing Range contract;
- this builder avoids supplying such a non-qualifying event in the first place;
- no future bar may retroactively relabel a past pre-eligibility close as an
  event.

## 9. Unchanged swing and close-break contracts

Swing discovery remains exact two-left/two-right strict confirmation. Only a
swing confirmed strictly before the fully closed current bar is eligible.

The one-tick rules remain:

- bullish: `close_tick >= HIGH price_tick + 1`;
- bearish: `close_tick <= LOW price_tick - 1`.

Wick-only contact, equality, an unconfirmed swing, and a break on the swing's own
confirmation moment remain non-qualifying. No future bars may participate in
current-bar swing, break, event, or retirement decisions.

## 10. Exact atomic group construction

At each complete bar moment, derive two immutable tuples from the valid segment
prefix:

- every newly crossed, previously unconsumed confirmed HIGH;
- every newly crossed, previously unconsumed confirmed LOW.

If both tuples are non-empty at the same effective moment, the group remains
`INVALID` as contradictory opposing structural breaks. No swing consumption,
event, state change, or later evidence from that group may be promoted.

If exactly one tuple is non-empty, the group is reconciled under Sections 11
through 15 before any event or state mutation is promoted.

## 11. First-event eligibility

When `active_direction is None`, a first BOS candidate is eligible only if the
latest opposite-side protected swing for the candidate direction is confirmed
strictly before the current bar.

If that protected context does not yet exist:

- the current close is a deterministic pre-eligibility non-event;
- no Structure Event, direction, protected state, FVG context link, or public
  evidence is emitted from the group;
- every crossed swing in the single crossed tuple is consumed at this exact
  moment so the historical close cannot be relabeled later;
- processing continues with strictly later complete bars;
- the result is not changed to `UNKNOWN` solely for this condition.

If protected context exists, the existing price-extreme and recency selector is
used for the first BOS. All crossed swings in that direction are consumed
atomically, and the event plus post-event direction/protected state are promoted
as one group.

## 12. Same-direction BOS continuation

When the crossed direction equals `active_direction`, the existing deterministic
selection remains unchanged:

- bullish continuation selects the highest crossed HIGH, then locked recency
  ties;
- bearish continuation selects the lowest crossed LOW, then locked recency
  ties.

The selected event is BOS. All same-direction crossed swings are consumed
atomically. Event emission and post-event protected-state update occur only after
the complete group reconciles.

## 13. Reversal non-event when protected swing is not crossed

When the crossed direction opposes `active_direction`, the exact active
`protected_swing` is the sole eligible CHOCH role.

If its `swing_id` is absent from the crossed tuple:

- no reversal event exists at that moment;
- every actually crossed non-protected swing in the tuple is consumed atomically;
- the active direction and active protected swing remain byte-for-byte unchanged;
- no event, link, or state transition is promoted;
- processing continues with the strictly later prefix;
- this deterministic outcome must not raise `_StructuralUnknown` or return
  `STRUCTURE_UNKNOWN`.

This rule covers the 19 observed real-data mismatches where the protected swing
was known and not crossed.

## 14. Protected-swing precedence when multiple levels cross

If the crossed reversal tuple contains the exact active protected swing, that
swing is selected as `broken_swing_id` for CHOCH regardless of whether another
crossed swing has a higher bullish price, lower bearish price, later source
index, later confirmation moment, or lexically different hash.

All swings crossed in that direction at the same close are still consumed
atomically. Price-extreme selection remains authoritative only for first BOS and
same-direction BOS groups; it is not a reversal chronology tie-break.

This rule covers the 3 observed real-data groups where the protected swing was
crossed but the generic selector chose another member.

## 15. Consumption, retirement, and no-retroactivity

`Consumed` in this proposal means excluded from every strictly later raw-event
candidate within the same segment. It is an internal causal fact and does not
create a new public dataclass, identity kind, transition, or output field.

Consumption occurs only after the complete current group is classified as one of:

- pre-eligibility non-event;
- protected-not-crossed reversal non-event;
- accepted BOS;
- accepted CHOCH.

Contradictory or malformed groups consume nothing and promote nothing.
Consumption is segment-local and may not cross a contract segment boundary.
This prevents repeated attempts and prevents a past close from being assigned a
later first-known event moment.

## 16. Post-event protected-state reconciliation

Before an accepted BOS or CHOCH is promoted, derive the latest required
opposite-side protected swing confirmed strictly before that event moment.

For an initialized active state, absence of a required post-event protected
swing is genuinely indeterminable state and remains `UNKNOWN`. The failing group
and later groups promote nothing, and the top-level result retains the existing
all-or-nothing no-seed behavior.

This exception does not restore the old initial behavior: Section 11 explicitly
classifies an uninitialized break without two-sided protected context as a
pre-eligibility non-event.

## 17. Exact status and atomic-promotion rules

Existing external precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

For valid complete raw structural derivation:

- contradictory or malformed evidence is `INVALID`;
- genuinely unreconcilable initialized state is `UNKNOWN`;
- Sections 11 and 13 produce deterministic non-events, not `UNKNOWN`;
- a seed containing any valid structural member is `VALID`;
- a canonically bound seed with no structural members is `NONE` under the
  existing contract.

No partial seed is returned for `INVALID`, `AMBIGUOUS`, or `UNKNOWN`. Atomic
promotion remains per complete bar group and the public result surface remains
unchanged.

## 18. Segment isolation and prefix invariance

All swing confirmation, consumption, active direction, protected state, event,
and FVG linkage state resets at every canonical contract-segment boundary.

A strictly later complete-segment append may deterministically rebind dataset,
source, displacement, segment-evidence, and seed identities while preserving the
byte-equivalent foreign facts and causal classification of every earlier segment.

Same-segment historical insertion, deletion, repair, reorder, timestamp change,
or bar mutation is not a prefix extension. Cross-segment state, dataset-global
local indices, silent sorting, or future-bar repair remains forbidden.

## 19. Public API and identity invariance

The following remain byte-contract compatible and receive no new parameter,
field, enum value, default, or export:

- `GC_STRUCTURAL_SEED_VERSION == "GC-STRUCTURAL-SEED-V1"`;
- `GCStructuralSeedIdentityKind`;
- `GCStructuralSeedConfig`;
- `GCCanonicalSeedEvidence`;
- `GCStructuralSeedResult`;
- `make_gc_structural_seed_id(...)`;
- `build_gc_structural_seed_evidence(...)`;
- `validate_gc_structural_seed_evidence(...)`.

The exact public function signatures remain:

```python
make_gc_structural_seed_id(
    *,
    identity_kind: GCStructuralSeedIdentityKind,
    instrument: str,
    timeframe: str,
    tick_size: Decimal,
    dataset_id: str,
    seed_version: str,
    config: GCStructuralSeedConfig,
    source_bar_digest: str,
    segment_id: str | None = None,
    direction: SMCV2Direction | None = None,
    source_indices: tuple[int, ...] = (),
    source_timestamps: tuple[datetime, ...] = (),
    boundaries: SMCV2TickRange | None = None,
    structure_event_id: str | None = None,
    segment_evidence_digests: tuple[tuple[str, str], ...] = (),
) -> str

build_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult

validate_gc_structural_seed_evidence(
    *,
    dataset_config: GCDatasetBuildConfig,
    dataset: GCDatasetBuildResult | None,
    structural_seed: GCCanonicalSeedEvidence | None,
    config: GCStructuralSeedConfig = GCStructuralSeedConfig(),
) -> GCStructuralSeedResult
```

DISPLACEMENT and SEED identity payloads remain unchanged. Public swing, event,
and context-link identities remain owned by their existing dependency builders.
The corrected internal candidate choice changes an event identity only when the
previous event was semantically non-canonical or the exact protected swing must
replace a wrongly selected member.

## 20. Corrected exact 48-case test reconciliation

The parent proposal's exact sequential 48 logical cases remain exactly 48.
Parameterization may increase collected test count. Cases not named below remain
unchanged; the following cases gain or replace coverage:

1. Case 21 retains bullish highest-price selection for first/same-direction BOS
   and proves it is not used to override an active protected reversal swing.
2. Case 22 provides the exact bearish mirror.
3. Case 23 proves atomic consumption for accepted events, pre-eligibility
   non-events, and protected-not-crossed reversal non-events; contradictory
   groups consume nothing.
4. Case 24 proves the first eligible event is BOS only after strictly prior
   opposite-side protected context exists.
5. Case 25 proves, in both directions, that a crossed non-protected swing without
   a crossed active protected swing is a non-event, while a tuple containing the
   protected swing selects that swing for CHOCH even when price-extreme ordering
   prefers another member.
6. Case 26 replaces the old blanket missing-protected expectation: an initial
   pre-eligibility break is a non-event, consumes its crossed levels, does not
   relabel later, and permits a genuinely new strictly later eligible BOS. A
   missing required post-event protected state in an initialized sequence remains
   `UNKNOWN` with no seed.
7. Case 27 proves accepted BOS/CHOCH singleton provenance still equals the exact
   confirmation bar and non-events emit no provenance object.
8. Case 28 recomputes the public event ID from the exact protected swing selected
   by reversal precedence.
9. Case 29 proves causal order and consumption order cannot be replaced by hash,
   direction, or price lexical order.
10. Case 30 uses inline patterns matching all three audited discriminator classes:
    protected-not-crossed, protected-plus-other-crossed, and initial
    pre-eligibility. None may fabricate `AMBIGUOUS` or a false `UNKNOWN`.
11. Case 35 proves only accepted events may create an event/FVG context link;
    non-event groups cannot link an otherwise matching FVG.
12. Case 40 proves the source-bar digest remains sensitive while internal
    consumption is deterministically re-derived and is not a new identity field.
13. Case 41 proves segment evidence digests contain only promoted public members,
    not hidden consumption state.
14. Case 45 proves a valid complete dataset containing only non-event structural
    attempts returns the existing bound empty-seed outcome without false
    `UNKNOWN`.
15. Case 46 proves `INVALID` and genuine initialized-state `UNKNOWN` retain
    precedence and no partial seed; deterministic non-events do not raise status.
16. Case 47 proves repeatability and strictly later complete-segment prefix
    invariance across the corrected consumption and selection semantics.
17. Case 48 proves downstream orchestration receives only canonical accepted
    events and that no downstream module is modified to compensate for an
    upstream false event.

The focused suite must also contain a parameterized real-data-shape discriminator
with counts independent of private files. Private V3 rows may not become fixtures.

## 21. Future implementation and private rerun gates

Implementation promotion requires all of the following:

- this single correction proposal passes independent semantic, structural, hash,
  scope, and diff audit;
- a separately authorized exact three-path test-first implementation changes only
  the reserved paths in Section 3;
- the corrected exact 48 logical cases reconcile;
- focused and full regression suites pass with cache provider disabled;
- checkpoint claims, hashes, bytes, lines, totals, timings, and scope reconcile;
- independent final code/test/checkpoint audit passes;
- any downstream candidate-evidence contract affected by the new structural
  semantics receives a separate read-only cross-audit before private execution;
- the accepted V3 dataset reconstructs to the same dataset ID and input hashes;
- build and validate results are object-equal and no longer fail for the audited
  19/3/6 discriminator classes.

The corrected private run may publish only under a separately authorized private
run scope. A non-`VALID`/`NONE` result publishes nothing and stops the workflow.

## 22. Downstream compatibility boundary

Candidate Evidence, labels, OOS, training, execution, and integration remain
consumers of immutable accepted structural output only. They may not:

- recompute or repair structural events;
- reinterpret a non-event as BOS or CHOCH;
- select a different protected swing;
- infer hidden consumption state;
- accept a partial seed from a blocked result.

The existing Candidate Evidence proposal binds the parent structural-proposal
hash. This new correction artifact therefore requires a future documentation-only
cross-audit and explicit one-way correction binding before Candidate Evidence or
private candidate work can be promoted. This document does not mutate that
proposal or its implementation.

## 23. Rollback and immediate STOP conditions

Before commit, rollback is deletion of only this new documentation file. After a
future commit, rollback must use a new explicit revert commit; history rewriting
is forbidden.

Immediate STOP conditions include:

- inability to reproduce the accepted V3 dataset identity and input hashes;
- any need to inspect OOS bars to choose the correction;
- any use of future bars or cross-segment state;
- retroactive event timing or reactivation of consumed swings;
- public API, dataclass, enum, version, export, or identity-payload expansion;
- mutation of Dealing Range, Candidate Evidence, private data, configuration,
  runtime, execution, or integration surfaces;
- creation of external fixtures or copying private rows into tests;
- any label, prediction, confidence, risk, entry, exit, PnL, model-training, or
  trading-authority dependency;
- any result that remains `UNKNOWN` for the audited deterministic non-event or
  protected-precedence patterns;
- any scope drift, hash drift, test regression, nondeterminism, or incomplete
  checkpoint evidence.

## 24. Final bounded conclusion and next single task

The accepted V3 data exposed an upstream structural candidate-classification
defect: non-protected breaks were treated as indeterminable reversals, and generic
price selection could override an actually crossed protected swing. The exact
correction is now specified without changing public APIs, identities, segment
isolation, no-look-ahead, or all-or-nothing blocked-result behavior.

The next and only task after this document is an independent documentation-only
semantic and structural re-audit of exactly this file. PASS may authorize the
separate exact three-path test-first implementation reserved in Section 3. It does
not authorize staging, commit, push, private execution, Candidate Evidence work,
training, OOS access, or integration. The global code freeze remains active.
