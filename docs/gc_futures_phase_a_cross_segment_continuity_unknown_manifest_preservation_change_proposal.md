# GC Futures Phase A Cross-Segment Continuity UNKNOWN Manifest Preservation Change Proposal

## 1. Proposal record

- Proposal ID:
  `GC-PHASE-A-CROSS-SEGMENT-CONTINUITY-UNKNOWN-MANIFEST-PRESERVATION-V1`.
- Proposal date: `2026-08-27`.
- Proposal status:
  `DOCUMENTATION_ONLY / UPSTREAM_PREREQUISITE_LOCKED / IMPLEMENTATION_NOT_AUTHORIZED`.
- Existing implementation version: `GC-CROSS-SEGMENT-CONTINUITY-V1`.
- Proposed additive behavior version:
  `GC-CROSS-SEGMENT-CONTINUITY-UNKNOWN-MANIFEST-PRESERVATION-V1`.
- Candidate promotion, feature/label construction, corpus rebuild, model
  training, final-OOS payload access, integration, paper trading, broker
  routing, and live authority: `NOT GRANTED`.

This record locks the smallest upstream evidence-preservation correction needed
before a cross-session confirmation-horizon resolver can be specified safely.
It does not authorize that resolver, execute private data, or reinterpret any
accepted negative result.

## 2. Independent audit finding

The accepted continuity analyzer constructs a canonical
`GCCrossSegmentContinuityManifest` after validating the dataset, calendars,
seed, canonical Candidate Evidence control, boundaries, and receiving groups.
It then discards that manifest when the final canonical control status is
`UNKNOWN`, returning:

- status `UNKNOWN`;
- reason and blocking reason `CANONICAL_CONTROL_UNKNOWN`;
- preserved boundary and receiving-group tuples; and
- `manifest=None`.

This is internally safe for the original feasibility question, but it is not a
sufficient foreign-identity boundary for a later reference-only resolver. The
resolver cannot prove that the preserved boundary/group identities bind to the
same dataset, calendars, seed, timezone-data version, or canonical-control
digest without either rebuilding detector output or inventing a manifest.
Both shortcuts are forbidden.

The prior resolver draft therefore failed independent semantic audit and was
deleted before staging. The governing candidate-horizon proposal explicitly
classifies a stronger state-carry or foreign-identity requirement as a STOP
condition requiring a new documentation-only proposal. This record satisfies
that STOP condition; it does not bypass it.

## 3. Binding repository baseline

This proposal binds to repository commit
`1368c762af5efdb550772067efd23aed21a93b68`. Local `HEAD` and local
`origin/main` matched that commit when drafting began.

| Artifact | SHA-256 | Bytes | Lines |
|---|---|---:|---:|
| `analysis/gc_cross_segment_continuity.py` | `1F59432FD738699015DDD92DC8AEB437D1B3DADE7EF96B1BB816245F05DB34D7` | 58,251 | 1,124 |
| `tests/test_gc_cross_segment_continuity.py` | `9E666DE295F7F538E81CFE772A1B436E625F5D9644E5136C045C049E458205C4` | 49,354 | 1,094 |
| continuity checkpoint | `2DD1B7753566C5F3E61D241089254341174A4B4459CDCAAFBE036D98CC69E397` | 17,671 | 341 |
| negative continuity decision | `624E615255019A5F5B6C2F5D11B77594B62493D6ED1E636941B178B29F27704F` | 16,565 | 374 |
| candidate-horizon proposal | `72DBE3CD081BCF512EC54885BF5D5486715B4F64A8BAEEA7609443C70897D936` | 27,199 | 537 |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` | 110,108 | 2,590 |
| `tests/test_inducement.py` | `791567124B3ABA381A4FB84CBB4B37125E9404AF1AFE276717A3042B268EF8FE` | 85,834 | 2,493 |
| pending-horizon checkpoint | `EEA6FD573A624F9D35B6C088C970DD5B1138B355ECAEB0CC6E3FDCEA93C28466` | 7,939 | 180 |

Any dependency drift before implementation is a STOP condition unless an
independent documentation-only rebase is accepted first.

## 4. Exact documentation-only scope

This change creates only:

`docs/gc_futures_phase_a_cross_segment_continuity_unknown_manifest_preservation_change_proposal.md`

No Python, test, fixture, private artifact, dataset, calendar, manifest,
configuration, package export, runtime, trace, strategy, risk, execution, or
integration file is changed. Pre-existing unrelated untracked documents remain
outside scope and untouched.

## 5. Authority and global freeze

Global code freeze remains active. This proposal grants no implementation,
private-run, training, OOS, integration, staging, commit, or push authority
beyond its own documentation-only acceptance workflow.

The future bounded correction may preserve an already constructed continuity
manifest in one exact `UNKNOWN` result path. It may not:

- change detector logic or recompute detector outputs;
- change boundary or receiving-group construction;
- change any public signature, dataclass field, enum, identity payload, reason,
  ordering rule, or status precedence;
- convert `UNKNOWN` to `NONE` or `VALID`;
- create a candidate, feature, label, corpus row, model input, or trading
  decision; or
- modify a historic private artifact or accepted negative decision.

## 6. Governing compatibility boundary

The following accepted facts remain immutable:

1. the V1 Candidate Evidence control is `UNKNOWN` and has no candidate
   manifest;
2. the accepted continuity private result is `UNKNOWN` with a null continuity
   manifest;
3. its 112 boundary assessments, 162 receiving groups, and 40 eligible
   boundaries remain diagnostic evidence only;
4. the V1 negative decision remains correct for the exact historical code and
   private execution that produced it;
5. the additive Inducement pending-horizon evidence does not modify V1
   `InducementResult`; and
6. no existing result may be rewritten or promoted retroactively.

The proposed behavior applies only to future executions of the corrected
continuity analyzer. Historical files, hashes, decisions, and audit statements
remain byte-for-byte unchanged.

## 7. Exact defect boundary

The defect exists only after all of the following have succeeded:

- every required top-level input is present and independently valid;
- the dataset is canonical and has a non-null dataset manifest;
- seed and dataset bindings reconcile;
- the canonical Candidate Evidence control exactly equals the deterministic
  rebuild performed by the accepted continuity analyzer;
- boundary and receiving-group construction completes without missing calendar
  coverage, malformed evidence, contradiction, or exception;
- every boundary and receiving-group identity is canonical;
- a canonical continuity manifest is constructed; and
- the supplied canonical control status is exactly `UNKNOWN`.

Only then does the current terminal branch call `_blocked(...)` and discard the
already constructed manifest. No earlier failure path is part of this change.

## 8. Exact corrected result rule

For the exact terminal condition in Section 7, the future corrected result is:

```text
status = UNKNOWN
boundaries = exact validated boundary tuple
receiving_groups = exact validated receiving-group tuple
manifest = exact already constructed GCCrossSegmentContinuityManifest
reasons = ("CANONICAL_CONTROL_UNKNOWN",)
blocking_reasons = ("CANONICAL_CONTROL_UNKNOWN",)
```

The manifest is non-promotional provenance. Its presence means only that the
preserved diagnostic boundary/group evidence has a complete deterministic
identity envelope. It does not make the canonical control complete and does
not change the result status.

## 9. Null-manifest rules that remain unchanged

`manifest=None` remains mandatory for every path where the analyzer cannot
construct and validate the complete canonical manifest before failure,
including:

- invalid or missing top-level context;
- dataset `INVALID`, `AMBIGUOUS`, `UNKNOWN`, or empty segments;
- seed binding mismatch;
- canonical rebuild exception or control drift;
- boundary calendar unavailable;
- invalid boundary evidence or boundary validation exception; and
- any unknowable malformed effective moment.

The final `CANONICAL_CONTROL_INVALID` and `CANONICAL_CONTROL_AMBIGUOUS` paths
also retain `manifest=None` in this minimal correction. Extending manifest
preservation to them is outside scope and would require a separate proposal.

## 10. Exact manifest invariants

The preserved manifest is the exact object already produced by the accepted
code path. No field is added, removed, defaulted, normalized differently, or
rewritten. Its exact fields remain:

1. `manifest_id`;
2. `version`;
3. `instrument`;
4. `timeframe`;
5. `dataset_id`;
6. `calendar_version`;
7. `boundary_calendar_digest`;
8. `candidate_calendar_digest`;
9. `timezone_data_version`;
10. `seed_id`;
11. `canonical_control_digest`;
12. `boundary_ids`; and
13. `receiving_group_ids`.

`boundary_ids` and `receiving_group_ids` exactly mirror the preserved tuples in
order. The public `MANIFEST` identity is recomputed with the existing builder
and must equal `manifest_id` exactly.

## 11. Canonical-control digest boundary

The manifest continues to preserve the SHA-256 digest of the complete,
object-equal canonical Candidate Evidence control used by the continuity run.
That digest does not claim that the `UNKNOWN` Candidate Evidence result has a
candidate manifest. It is a binding digest of the complete result object, not
a candidate-bundle identity.

The correction must not expose a private hashing helper, add a new Candidate
Evidence identity kind, fabricate candidate references, or change the
Candidate Evidence public API. A later consumer may treat the digest only as
opaque immutable provenance unless a separately accepted public validation
contract proves more.

## 12. Boundary and receiving-group immutability

The correction changes no boundary or receiving-group byte. Before and after
the correction, the same valid input must produce object-equal:

- boundary IDs, ordinals, segment IDs, contracts, source/receiving moments,
  decisions, reasons, dependency references, and receiving references; and
- receiving-group IDs, boundary references, effective moments, and ordered
  reference tuples.

No sort, repair, insertion, deletion, deduplication, renumbering, concatenation,
or dependency enrichment is permitted. Hash lexical order remains forbidden as
a chronology tie-break.

## 13. Atomicity and immutable prior evidence

Existing chronological cutoff and atomic processing remain unchanged. The
manifest can be preserved only after all boundary/group evidence used by it is
validated. A failing group and everything after it promote nothing.

A determinably later malformed group may preserve strictly prior boundary or
receiving-group evidence according to the accepted analyzer contract, but it
does not receive a manifest under this proposal because the complete manifest
was not validly reached. An unknowable malformed effective moment requires no
trustworthy prefix and remains `INVALID` with a null manifest.

## 14. Status and reason-token invariants

The exact precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The corrected branch remains `UNKNOWN`. Its exact reason token and exact
blocking token remain `CANONICAL_CONTROL_UNKNOWN`. No new status, enum value,
reason synonym, warning, completeness flag, promotion flag, or fallback status
is introduced.

The existence of a non-null manifest never overrides status precedence and
never implies promotion eligibility.

## 15. Exact public API preservation

The implementation must preserve every existing public name, signature,
annotation, default, enum value/order, dataclass field/order/default, frozen
state, constant, and `__all__` entry in
`analysis.gc_cross_segment_continuity`.

In particular:

- `GCCrossSegmentContinuityResult.manifest` remains typed
  `GCCrossSegmentContinuityManifest | None` with default `None`;
- `analyze_gc_cross_segment_continuity()` keeps its exact keyword-only
  signature and return annotation;
- `make_gc_cross_segment_continuity_id()` keeps its exact keyword-only
  signature and identity schemas; and
- no new public helper, adapter, protocol, callback, or package export is
  allowed.

## 16. Internal implementation constraint

The smallest acceptable implementation is an internal return-path correction:
the already constructed `manifest` is included only in the exact
`CANONICAL_CONTROL_UNKNOWN` terminal result.

An implementation may add an optional internal-only `_blocked()` parameter if
and only if all call sites remain explicit and every non-target path retains
the exact prior output. Direct construction of the one corrected result is also
allowed. The implementation may not broaden the behavior by inference.

No filesystem, network, subprocess, model, training, strategy, risk,
execution, runtime, or private-data import may be introduced.

## 17. Deterministic identity and repeatability

Two executions with object-equal inputs must produce object-equal complete
results. For the corrected branch, the manifest and all nested IDs must be
byte-identical across runs and independent of locale, wall-clock time, Python
object address, hash randomization, and dictionary iteration order.

Changing any manifest-bearing input field must either change the appropriate
identity deterministically or fail closed. A result may not retain an old
manifest after dataset, calendar, timezone, seed, control digest, boundary, or
receiving-group mutation.

## 18. Prefix invariance

Existing complete-group prefix invariance remains authoritative. A strictly
later complete append may preserve prior boundary/group bytes only when every
canonical input prefix and identity remains unchanged. Same-effective append,
historical insertion, reorder, repair, calendar mutation, seed mutation,
control mutation, segment renumbering, or contract mutation is prefix-ineligible.

The preserved manifest is a complete-result envelope and may change when a
strictly later complete boundary or receiving group is appended. This does not
permit prior boundary/group identities to change. A later resolver must bind
to the exact manifest for the exact analyzed input horizon; it cannot mix
prefix evidence with a different complete-result manifest.

## 19. Fail-closed malformed-input behavior

All existing malformed-input containment remains exact. Non-tuples, wrong
dataclass types, boolean integers, naive timestamps, malformed hashes,
duplicate or forked evidence, noncanonical ordering, impossible references,
and nested serialization failures must return the accepted fail-closed result
without exception leakage.

This proposal does not weaken validation so that a manifest can be emitted. If
any manifest field or referenced identity is not independently valid, the
result remains blocked with `manifest=None`.

## 20. Historical evidence and migration rule

No migration, rewrite, or backfill is authorized. The accepted private
negative artifact and its decision document continue to record a null manifest
because that is what commit `1368c762af5efdb550772067efd23aed21a93b68`
actually emitted.

A future corrected private rerun, if separately authorized, must use a new
immutable output root and new artifact identities. It may not overwrite or
rename any previous root. Comparisons must identify the implementation commit
and preserve both outcomes.

## 21. Exact 48-case future unit-test matrix

The future bounded implementation keeps exactly 48 numbered logical cases.
Parameterization may increase collected tests without changing this count.

| Case | Locked coverage |
|---:|---|
| 1 | Exact canonical-control `UNKNOWN` path preserves the already constructed manifest |
| 2 | Corrected result remains `UNKNOWN` with exact reason and blocking token |
| 3 | Preserved boundaries and receiving groups are object-equal to pre-correction evidence |
| 4 | Manifest `boundary_ids` exactly mirror the boundary tuple in order |
| 5 | Manifest `receiving_group_ids` exactly mirror the receiving-group tuple in order |
| 6 | Existing MANIFEST identity builder recomputes `manifest_id` exactly |
| 7 | Dataset ID and dataset manifest binding remain exact |
| 8 | Boundary-calendar digest remains exact and sensitive |
| 9 | Candidate-calendar digest remains exact and sensitive |
| 10 | Runtime timezone-data version remains exact and sensitive |
| 11 | Structural-seed identity remains exact and sensitive |
| 12 | Canonical-control digest remains exact and sensitive without becoming a candidate manifest |
| 13 | Instrument/timeframe normalization remains unchanged |
| 14 | Boundary identity payload and reason tokens remain unchanged |
| 15 | Receiving-group identity payload and reference order remain unchanged |
| 16 | Exact duplicate evidence behavior remains unchanged |
| 17 | Missing top-level context remains `UNKNOWN` with null manifest |
| 18 | Malformed supplied counterpart remains `INVALID` with null manifest |
| 19 | Dataset `INVALID` remains `INVALID` with null manifest |
| 20 | Dataset `AMBIGUOUS` remains `AMBIGUOUS` with null manifest |
| 21 | Dataset `UNKNOWN` remains `UNKNOWN` with null manifest |
| 22 | Empty dataset remains `NONE` with null manifest |
| 23 | Seed binding mismatch remains `INVALID` with null manifest |
| 24 | Canonical rebuild exception remains `INVALID` with null manifest |
| 25 | Canonical-control drift remains `INVALID` with null manifest |
| 26 | Boundary calendar unavailable remains `UNKNOWN` with null manifest |
| 27 | Invalid boundary evidence remains `INVALID` with null manifest |
| 28 | Boundary validation exception remains `INVALID` with null manifest |
| 29 | Canonical-control `INVALID` remains `INVALID` with null manifest |
| 30 | Canonical-control `AMBIGUOUS` remains `AMBIGUOUS` with null manifest |
| 31 | Canonical-control `VALID` path remains `VALID` or `NONE` with its exact manifest |
| 32 | Status precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE` |
| 33 | A non-null manifest does not promote a candidate, feature, label, or corpus row |
| 34 | Determinably later malformed evidence preserves only accepted strict prior evidence and no manifest |
| 35 | Unknowable malformed moment remains `INVALID` without trustworthy-prefix obligation |
| 36 | No partial failing-group promotion or exception leakage occurs |
| 37 | Object-equal executions return byte-equal corrected results |
| 38 | Locale, wall clock, hash randomization, and dictionary order cannot affect identities |
| 39 | Strictly later complete append preserves prior boundary/group bytes |
| 40 | Same-effective append and historical insertion are prefix-ineligible |
| 41 | Reorder, repair, version mutation, seed mutation, and control mutation are prefix-ineligible |
| 42 | Exact public function names, keyword-only parameters, annotations, defaults, and returns are unchanged |
| 43 | Every public dataclass field/order/type/default/frozen state is unchanged |
| 44 | Every enum value/order, version constant, identity schema, and export is unchanged |
| 45 | Malformed hashes, boolean indices, naive timestamps, and nested exceptions remain contained |
| 46 | Historic negative artifact and decision hashes remain unchanged and are not backfilled |
| 47 | No detector, candidate builder, pending-horizon, package, runtime, or integration file is touched |
| 48 | Focused/full regression, exact scope, hashes, bytes/lines, formatting, and checkpoint evidence pass |

## 22. Reserved first implementation exact 3-path scope

Only after separate explicit implementation authorization, the exact first
implementation scope is reserved to:

- `analysis/gc_cross_segment_continuity.py`;
- `tests/test_gc_cross_segment_continuity.py`; and
- `docs/gc_futures_phase_a_cross_segment_continuity_unknown_manifest_preservation_checkpoint.md`.

No external fixture is allowed. Dataset, Candidate Evidence, Inducement,
pending-horizon, calendar, seed, shared primitives, package exports, private
data, requirements, configuration, trace, strategy, risk, execution, and
integration files remain frozen.

The new checkpoint path must be absent before implementation. Any need to touch
a fourth path is a STOP condition and requires a new proposal.

## 23. Rollback, promotion, and STOP conditions

Rollback of the future implementation is exact reversion of the source/test
delta plus deletion of the new checkpoint. No accepted detector, dataset,
candidate, private artifact, manifest, checkpoint, or negative decision may be
rewritten.

Promotion from documentation to implementation requires:

- independent semantic and structural acceptance of this exact proposal;
- unchanged dependency hashes or an explicitly reviewed documentation rebase;
- test-first work inside the exact three paths in Section 22;
- all 48 logical cases and full regression passing;
- exact scope, API, identity, formatting, and checkpoint audits; and
- separate explicit user authorization.

STOP immediately if work requires a public API change, a new identity field,
preserving manifests on any non-target blocked path, detector recomputation,
private data, candidate promotion, feature/label construction, corpus rebuild,
training, final-OOS access, integration, or a fourth path.

## 24. Final decision and next single task

Decision: the previously drafted cross-session resolver is not ready for
implementation. The missing continuity manifest is a real foreign-identity
boundary, not a cosmetic omission. The correct next bounded task is the exact
three-path test-first continuity manifest-preservation correction in Section
22, after independent acceptance and explicit implementation authorization.

Only after that correction is implemented, audited, committed, and separately
pushed may a fresh documentation-only resolver proposal be drafted against the
new baseline. No resolver implementation, private rerun, candidate promotion,
feature/label build, corpus build, training, OOS, integration, stage, commit,
or push is authorized by this record.
