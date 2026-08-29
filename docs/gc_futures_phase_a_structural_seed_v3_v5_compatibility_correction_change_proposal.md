# GC Futures Phase-A Structural Seed V3/V5 Compatibility Correction Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-STRUCTURAL-SEED-V3-V5-COMPATIBILITY-CORRECTION-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Binding baseline commit: `23898b0940c1f737b7200763197f549b3551f33e`.
- Classification: documentation-first, fail-closed compatibility correction.
- Current decision: `PROPOSED_FOR_BOUNDED_TEST_FIRST_IMPLEMENTATION`.

This proposal records the earliest failure found by the authorized read-only
diagnosis of the corrected cross-segment private rerun. It reserves a narrow
consumer-side correction. It does not authorize private execution, dataset or
corpus construction, training, final-OOS access, feature or label generation,
integration, prediction, execution, or trading.

## 2. Verified diagnosis

The accepted development-only evidence is internally bound to exact dataset
manifest version `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. Its accepted structural
seed was produced with the same current structural-seed implementation bytes
that are present at this proposal baseline.

The current continuity consumer correctly accepts exact V3 and current V5
segment identities. The canonical Candidate Evidence rebuild then calls
`validate_gc_structural_seed_evidence()`. That validator re-derives the seed
through `build_gc_structural_seed_evidence()`, whose manifest validator requires
`manifest.version == GC_DATASET_BUILDER_VERSION`. The current builder version is
`GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`, so the exact accepted V3 manifest is
rejected before structural discovery.

The public result chain is therefore:

1. dataset, boundary calendar, candidate calendar, supplied seed type, and
   accepted candidate shape validate;
2. structural revalidation rejects the exact V3 manifest version;
3. canonical Candidate Evidence rebuild returns `INVALID` with
   `INVALID_STRUCTURAL_EVIDENCE` and zero segment results;
4. that rebuilt result differs from the accepted `UNKNOWN` control with 113
   segment results; and
5. continuity returns `INVALID` through `CANONICAL_CONTROL_DRIFT` before any
   resolver call.

This is a consumer compatibility defect. The diagnosis does not establish that
all later gates will pass after correction. A later failure must remain a STOP
condition and must not trigger an automatic rescue branch.

## 3. Failure-run safety evidence

The authorized failed transaction and the read-only diagnosis established:

- no second private worker or resolver call occurred;
- no final output root was published;
- no task temporary directory remained;
- all eight accepted input artifacts retained their exact bytes and hashes;
- repository tracked and staged diffs remained empty;
- local `HEAD` equaled `origin/main`; and
- no training, OOS access, feature/label build, integration, commit, or push
  occurred as part of diagnosis.

Private row content is not copied into this proposal. Only contract metadata
required to identify the failing public gate is recorded.

## 4. Exact proposal scope

This proposal creates only:

`docs/gc_futures_phase_a_structural_seed_v3_v5_compatibility_correction_change_proposal.md`

The separately bounded implementation is reserved to exactly three paths:

1. `analysis/gc_structural_seed_evidence.py`;
2. `tests/test_gc_structural_seed_evidence.py`; and
3. `docs/gc_futures_phase_a_structural_seed_v3_v5_compatibility_correction_checkpoint.md`.

No other source, test, fixture, private artifact, accepted evidence, dataset,
calendar, candidate, feature, label, model, configuration, export, runtime,
strategy, risk, or execution path is implicitly authorized.

## 5. Correction contract

The structural-seed consumer must select exactly one segment-identity verifier
from the manifest version before iterating segments:

- exact `GC-DATASET-BUILDER-V3-SPLIT-SESSION` selects a local, pure verifier
  reproducing the historical V3 `SEGMENT` identity payload;
- exact current `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION` selects the existing
  public `make_gc_dataset_id(identity_kind="SEGMENT", ...)` path; and
- every other blank, malformed, aliased, future, or unrecognized version fails
  closed as invalid structural evidence.

The selected branch applies to every segment in the dataset. The consumer must
not retry another version after a mismatch, mix identity versions, infer a
version from a hash match, or choose a branch from the desired downstream
status.

## 6. Exact historical V3 identity

The local V3 helper must reproduce only the historical segment identity with
this canonical payload:

- `version`: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- `identity_kind`: `SEGMENT`;
- the exact canonical dataset configuration fields and encodings;
- uppercase canonical contract;
- canonical partition enum value;
- first and last trade dates in ISO `YYYY-MM-DD` form;
- ordered, nonempty canonical source-ID tuple;
- exact canonical bar digest; and
- nonnegative `preceding_missing_bar_count`.

The payload must use the module's existing canonical JSON and lowercase SHA-256
path. The helper remains private, pure, deterministic, and unavailable as a new
construction API.

## 7. Preserved outer validation

The correction must preserve every existing structural validation invariant,
including:

- exact dataset and manifest identity equality;
- exact manifest segment order;
- canonical source and coverage identifiers;
- runtime timezone-data equality;
- strict global segment chronology and non-overlap;
- contiguous local bar indexes and valid bar geometry;
- exact row, partition, volume, and timestamp reconciliation;
- immutable tuples and frozen evidence objects;
- zero silent mutation, normalization, repair, or replacement; and
- exception containment into existing public statuses.

Accepting V3 identity does not convert the archived dataset to V5 and does not
change its stored IDs, provenance, status, or promotional authority.

## 8. Explicit non-goals

The implementation must not:

- modify `analysis/gc_dataset_builder.py` or its current V5 behavior;
- modify Candidate Evidence, continuity, or resolver public APIs;
- change `GC_DATASET_BUILDER_VERSION`;
- export the V3 helper;
- accept V1, V2, V4, arbitrary, inferred, or partially matching versions;
- regenerate or replace archived dataset, segment, seed, or candidate IDs;
- use a fallback branch after a failed identity comparison;
- weaken OOS, calendar, chronology, volume, or provenance checks;
- read private evidence from source or tests;
- initiate another private run; or
- grant training, integration, prediction, execution, or trading authority.

## 9. Exact dependency bindings

Implementation may proceed only from these exact baseline bytes:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_structural_seed_evidence.py` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `tests/test_gc_structural_seed_evidence.py` | `26AA31863AD07B71D0480F0789199D7791BD16FA736E6D2A86B060B928509B35` |
| `tests/test_gc_candidate_evidence_builder.py` | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `tests/test_gc_cross_segment_continuity.py` | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |
| corrected private-rerun proposal | `5041330476D3D663C2F20F00FE796801B4FCAE6B6DFB2B7CE46BD045D9D63F80` |

Any dependency drift or path expansion is a STOP condition requiring a fresh
proposal, not permission to improvise.

## 10. Required test-first matrix

Public in-memory tests must be added before source correction and must prove:

1. an exact V3 segment ID under an exact V3 manifest validates and preserves
   the supplied canonical seed byte-for-byte;
2. every segment in a multi-segment V3 fixture is independently verified;
3. exact current V5 validation remains unchanged;
4. a V3 manifest carrying a V5 segment ID is invalid;
5. a V5 manifest carrying a V3 segment ID is invalid;
6. one altered V3 segment ID is invalid;
7. mixed V3/V5 IDs under one manifest are invalid;
8. blank, arbitrary, aliased, and unsupported versions are invalid;
9. manifest/dataset identity and segment-order drift remain invalid;
10. accepted objects are not mutated;
11. repeated in-memory execution is object-equal; and
12. invalid evidence never publishes a partial seed.

Tests must construct synthetic public fixtures. They must not open, enumerate,
hash, deserialize, or copy the private accepted bundle.

## 11. Implementation and audit order

The exact local sequence is:

1. verify baseline commit, dependency hashes, clean tracked/staged state, and
   the exact reserved paths;
2. add the focused failing public tests;
3. prove they fail for the expected manifest-version/segment-identity reason;
4. implement the minimal version-selected verifier inside the structural module;
5. run focused structural tests with cache disabled;
6. run candidate and continuity regression suites with cache disabled;
7. run the complete public test suite with cache disabled;
8. run `py_compile` on the changed source and test;
9. create the exact checkpoint recording hashes, tests, scope, and freezes;
10. independently audit working and cached diffs; and
11. create one local commit only if every gate passes.

No private rerun is included in this sequence.

## 12. Commit and export boundary

The bounded implementation may be committed locally only after exact path and
test audits pass. GitHub push is a separate external export gate requiring the
exact resulting commit identifier and explicit privacy/export authorization.

A successful local or pushed implementation still does not authorize private
execution. A later private rerun requires separate exact authority binding the
implementation commit, unchanged private inputs, absent final root, two fresh
workers, atomic publication, independent audit, and mandatory STOP.

## 13. Outcome boundary

This correction restores version-aware validation only. It does not assert that
continuity or the resolver will return an admissible status. Any later
`INVALID`, exception, nondeterminism, identity drift, unexpected reason, output
scope drift, or residue remains a hard failure.

Phase A remains closed and non-promotional. No output from this correction or a
future diagnostic may become training, OOS, prediction, integration, order, or
trading authority without a separate governance decision.
