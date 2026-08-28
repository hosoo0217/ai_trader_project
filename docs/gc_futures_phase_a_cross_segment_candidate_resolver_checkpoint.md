# GC Futures Phase A Cross-Segment Candidate Resolver Checkpoint

## 1. Checkpoint identity

- Checkpoint ID:
  `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-2026-08-28`.
- Governing proposal:
  `docs/gc_futures_phase_a_cross_segment_candidate_resolver_change_proposal.md`.
- Governing proposal commit:
  `422c816f619a4ab0a41724b3aeac75c7e87b2b60`.
- Governing proposal SHA-256:
  `C1FB850B29BAC10FAE466A52FC5D9F22EFDC5EEA139D980C9260AFD7E0A8EB84`.
- Implementation version:
  `GC-CROSS-SEGMENT-CANDIDATE-RESOLVER-V1`.
- Independent implementation audit: `PASS`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact authorized scope

Only these three paths were created:

- `analysis/gc_cross_segment_candidate_resolver.py`;
- `tests/test_gc_cross_segment_candidate_resolver.py`; and
- `docs/gc_futures_phase_a_cross_segment_candidate_resolver_checkpoint.md`.

No existing source, test, detector, candidate builder, continuity analyzer,
package export, private-data root, fixture, calendar, dataset, corpus, feature,
label, model, final-OOS payload, configuration, runtime, strategy, risk,
execution, trace, or integration path was changed.

## 3. Archived diagnostic boundary

The resolver consumes only the exact preserved
`CANONICAL_CONTROL_UNKNOWN` continuity branch with its canonical non-null
manifest. A resolver `VALID` result means only that an immutable pending
Inducement horizon was reconciled with canonical Structure Event and Fair
Value Gap evidence in the immediately adjacent segment.

The output is archived research diagnostic evidence. It cannot reopen or
rescue Phase A V1, create a candidate, feature, label, score, confidence,
model input, risk instruction, execution instruction, PnL claim, or trading
authority. Upstream results, manifests, histories, and opaque digests remain
immutable.

## 4. Exact public surface

The new module exports exactly these nine names:

- `GC_CROSS_SEGMENT_CANDIDATE_RESOLVER_VERSION`;
- `GCCrossSegmentCandidateResolverIdentityKind`;
- `GCSegmentPendingHorizonEvidence`;
- `GCSegmentReceivingGroupEvidence`;
- `GCCrossSegmentCandidateResolution`;
- `GCCrossSegmentCandidateResolverManifest`;
- `GCCrossSegmentCandidateResolverResult`;
- `make_gc_cross_segment_candidate_resolver_id`; and
- `resolve_gc_cross_segment_candidates`.

Both public functions are keyword-only with the exact names, annotations, and
defaults locked by proposal Section 18. Every public dataclass is frozen with
the exact Section 17 fields, annotations, order, and defaults. Identity kinds
are exactly `RESOLUTION` and `MANIFEST`.

## 5. Applicable continuity and pending-horizon validation

The analyzer accepts only a canonical continuity result whose status, reason,
blocking reason, boundaries, receiving groups, and manifest reconcile with
the public continuity identity builder. Null manifests, non-adjacent,
duplicate, reordered, or mismatched boundaries and groups fail closed.

Pending wrappers are strict tuples in canonical owner order. Every nested
pending result and horizon is exact-type validated, identity-recomputed, and
required to carry the exact `NEXT_THREE_CLOSED_BARS_INCOMPLETE` reason and
blocking token. Sweep and first-known moments cannot exceed the source end.
The exact eligible states are `(available, missing) = (0,3), (1,2), (2,1)`;
three available confirmation bars are no longer a pending cross-segment
horizon.

## 6. Receiving proof and causal binding

Only the immediately adjacent receiving segment may resolve a horizon.
Evidence must be strictly later than the source end and occupy the exact
remaining positional prefix of the next-three-closed-bar window. Same-moment,
second-boundary, skipped, substituted, or wider-horizon evidence is not used.

The canonical receiving group contains exact Structure Event then Fair Value
Gap references. Observation ownership/order, canonical foreign identities,
FVG transition/snapshot histories, direction, effective moments, observation
source reconciliation, and the exact shorter-sequence positional-suffix rule
are validated fail closed. The canonical-control digest is copied as opaque
manifest evidence and is never decoded or recomputed.

## 7. Determinism, atomicity, and precedence

The earliest complete canonical match is selected for each pending horizon.
Exact duplicates collapse only when their full immutable payload is equal;
forked IDs are invalid. Independent resolutions use deterministic canonical
ordering. Same-effective opposing valid resolutions are ambiguous.

Each pending horizon has an independent candidate accumulator. This prevents
an earlier valid match from suppressing a later unresolved horizon. Promotion
is atomic: strictly prior valid resolution bytes survive a determinably later
failure, while the failing group and every later group promote nothing.

Final status precedence is exactly:

```text
INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE
```

## 8. Exact statuses and reason tokens

- resolution reason:
  `NEXT_THREE_CLOSED_BARS_CONFIRMED_ACROSS_ADJACENT_SEGMENT`;
- `VALID`: `CROSS_SEGMENT_CONFIRMATION_RESOLVED`;
- `NONE`: `NO_APPLICABLE_CROSS_SEGMENT_HORIZON`;
- `UNKNOWN`: `CROSS_SEGMENT_CONFIRMATION_UNRESOLVED`;
- `AMBIGUOUS`: `OPPOSING_CROSS_SEGMENT_CONFIRMATIONS`;
- `INVALID`: `INVALID_CROSS_SEGMENT_RESOLVER_EVIDENCE`.

Aliases, casing changes, missing required tokens, extra prose, malformed
nested values, unsupported identity kinds, and identity-schema violations are
contained as the exact fail-closed outcome required by the relevant public
boundary.

## 9. Deterministic identities

The `RESOLUTION` identity validates all common fields plus the complete source
boundary, receiving group, pending horizon, direction, contract, segment,
event, FVG, sweep, confirmation, first-known, ordered reference, and exact
reason payload. Every resolution-only field is forbidden for `MANIFEST`.

The `MANIFEST` identity validates all common continuity provenance and the
ordered non-empty resolution history. Every resolution field is forbidden.
All SHA-256 evidence is lowercase canonical input and every generated ID is a
deterministic lowercase SHA-256 digest.

## 10. Test-first correction evidence

The first focused run after the complete synthetic matrix and before source
correction returned:

```text
14 failed, 50 passed in 1.73s
```

That RED run exposed two production defects: pending-result reasons were not
validated exactly, and a candidate accumulator leaked across independent
pending horizons so an earlier valid match could suppress a later `UNKNOWN`.
The remaining failures identified invalid malformed-fixture construction and
identity-kind assertions in the new tests. Those tests were corrected to
exercise the locked public boundary without weakening production semantics.

After the minimal source corrections and fixture audit, the focused suite
returned `64 passed in 1.40s`. A final source cleanup was followed by the final
focused result in Section 12.

## 11. Exact logical-case reconciliation

The test module contains exactly 48 sequential logical functions named
`test_case_01` through `test_case_48`. No logical case is missing or duplicated.
Parameterization expands collection to 64 executions without changing the
logical count.

Cases 1-12 cover top-level/applicable-branch, manifest, boundary, wrapper,
token, and nested fail-closed validation. Cases 13-24 cover exact available/
missing arithmetic, temporal eligibility, adjacency, and positional windows.
Cases 25-33 cover receiving references, ownership, foreign identities,
event/FVG causal binding, histories, opaque digest, direction mirrors, and the
UNKNOWN/INVALID evidence boundary. Cases 34-43 cover earliest selection,
duplicate/fork/opposition behavior, deterministic multi-resolution ordering,
status precedence, immutable prior evidence, and atomic no-promotion. Cases
44-48 cover exhaustive identity schemas/sensitivity, exact API and frozen
contracts, prefix invariance, repeatability, byte equality, and forbidden
integration surfaces.

## 12. Focused regression evidence

- Command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_cross_segment_candidate_resolver.py`.
- Result: `64 passed in 1.34s`.
- Exact logical cases: `48`.
- Collected focused executions: `64`.

## 13. Full regression evidence

- Command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`.
- Result: `2645 passed in 52.61s`.
- Accepted pre-task public-suite total: `2581`.
- Added focused executions: `64`.
- Reconciled total: `2581 + 64 = 2645`.

Explicit `tests` collection is the canonical full public regression command in
this workspace. A repository-root collection attempt produced three
collection permission errors only because pytest traversed ACL-protected
private acquisition roots outside this bounded task; it did not collect a
source or test failure. No private root was opened, modified, or used by this
implementation.

## 14. Artifact evidence

- `analysis/gc_cross_segment_candidate_resolver.py`
  - SHA-256:
    `62766E2984181B2CF04D0BA6F3354679F121704EEBD2DADC0F6F5242BC282E46`;
  - bytes: `59529`;
  - physical lines: `1267`.
- `tests/test_gc_cross_segment_candidate_resolver.py`
  - SHA-256:
    `47BE9A0A0E0126F58A01C623197D043C2E35E4A975B9654501FC8498C5933D0A`;
  - bytes: `39475`;
  - physical lines: `1052`.

The checkpoint SHA-256, byte count, and physical-line count are computed only
after its final bytes are fixed and are verified during cached and committed
artifact audits.

## 15. Scope, formatting, and compatibility audit

- `py_compile`: `PASS` for source and focused test module.
- `git diff --check`: required `PASS` before staging and again on the cache.
- Exact logical-case count: `48`; collected executions: `64`.
- No existing public API, identity payload, detector result, package export,
  candidate builder, or continuity implementation changed.
- Three pre-existing unrelated untracked proposal documents remain outside
  scope and untouched.
- No broad pathspec is authorized for staging.

## 16. Rollback, promotion, and STOP conditions

Rollback before commit is exact deletion of these three new files. Promotion
to local commit requires exact three-path staging, full cached-content audit,
cached `diff --check`, staged artifact SHA-256 verification, focused/full PASS,
exact parent/scope verification, and no tracked change outside scope.

This implementation is `PASS` for exact three-path local staging and commit.
STOP remains mandatory before push, private execution, training, final-OOS
payload access, dataset/corpus/feature/label build, package/runtime
integration, strategy, risk, execution, trace, or any scope expansion. Those
actions remain separately gated and are not authorized by this checkpoint.
