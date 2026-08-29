# GC Futures Phase-A Cross-Segment Private Diagnostic Dual-Contract Correction Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-PRIVATE-DIAGNOSTIC-DUAL-CONTRACT-CORRECTION-PROPOSAL-V1`.
- Decision date: `2026-08-29`.
- Binding baseline commit: `0bf0e5108d26998f2917cc9ebed985b6a8c4258e`.
- Classification: documentation-only, fail-closed correction proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_IMPLEMENTATION`.

This record proposes two bounded consumer-side contract corrections discovered
by the authorized cross-segment private diagnostic. It does not authorize an
implementation, a private rerun, private payload access, dataset or corpus
construction, training, final-OOS access, integration, execution, or trading.

## 2. Decision summary

The private diagnostic did not reach meaningful continuity or resolver
evaluation. It stopped while the current continuity consumer validated the
accepted archived dataset. The archived development-only bundle is internally
consistent under the exact identity version that created it,
`GC-DATASET-BUILDER-V3-SPLIT-SESSION`, while the current consumer recomputes
each segment identity through
`GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`.

A second independent public contract mismatch exists after that validation
barrier. The public Inducement producer emits a human-readable UNKNOWN reason
and a machine blocker token, while the cross-segment resolver currently
requires the blocker token in both fields.

The proposed correction is deliberately narrow:

1. add exact archived V3 segment-identity verification only inside the
   continuity consumer, without changing the archived bundle or current V5
   dataset builder; and
2. make the resolver validate the exact public Inducement producer contract,
   without changing the producer or accepting aliases.

Both corrections remain diagnostic infrastructure. They grant no candidate,
promotion, training, prediction, or trading authority.

## 3. Verified failure evidence

The authorized two-run diagnostic failed closed and deterministically:

- both independent runs were equal;
- continuity status was `INVALID`;
- the continuity manifest was absent;
- boundary, receiving-group, pending-wrapper, horizon, and resolution counts
  were all zero;
- the resolver result was `INVALID`;
- no final private output root was published;
- temporary roots and the ephemeral harness were removed;
- accepted input bytes remained unchanged; and
- repository `HEAD` and tracked state remained unchanged.

Read-only identity diagnosis established that all `133` accepted segment IDs
match exact V3 recomputation and all `133` mismatch current V5 recomputation.
The first failure therefore occurs before canonical candidate reconstruction,
boundary discovery, pending-evidence construction, or resolver semantics.

These counts and statuses are diagnostic metadata only. This proposal does not
copy, expose, deserialize, or authorize access to private market payloads.

## 4. Exact documentation-only scope

This proposal task may create and correct only:

`docs/gc_futures_phase_a_cross_segment_private_diagnostic_dual_contract_correction_change_proposal.md`

No source, test, fixture, accepted evidence, private artifact, calendar,
dataset, candidate, feature, label, model, configuration, runtime, strategy,
risk, execution, trace, or other documentation file may change. Staging,
commit, push, implementation, and private execution are separate later gates.

## 5. Authority and global freeze

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. This proposal grants no authority to:

- mutate, relabel, rewrite, normalize, replace, or delete accepted evidence;
- rebuild a dataset, corpus, feature, label, split, model, or outcome;
- read the embargo interval or sealed final-OOS payload;
- create or promote canonical Candidate Evidence;
- add package exports, runtime hooks, configuration, or integration wiring;
- call a local or remote language model with private market evidence;
- produce BUY/SELL, confidence, risk, entry, exit, PnL, order, or execution
  authority; or
- stage, commit, push, implement, or execute a private transaction without its
  later exact authorization.

Passing tests or a future diagnostic PASS cannot lift these restrictions.

## 6. Defect A: archived V3 segment identity incompatibility

`analysis/gc_cross_segment_continuity.py` currently validates every accepted
`GCCanonicalContractSegment` by calling the current public
`make_gc_dataset_id(identity_kind="SEGMENT", ...)`. That public function uses
the current builder version `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`.

The accepted bundle predates that identity-version transition. Its segment IDs
were created by `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. The stored IDs are not
corrupt and must not be replaced. They bind the accepted evidence graph that
was audited at acquisition and build time.

The current validation therefore conflates two different questions:

- whether an archived segment still matches the exact historical identity
  contract that created it; and
- whether a newly built segment matches the current V5 identity contract.

Using only the current builder answers the second question and incorrectly
rejects the first.

## 7. Correction A: exact legacy verifier boundary

A future implementation may add one private helper inside
`analysis/gc_cross_segment_continuity.py` that reproduces only the historical
V3 `SEGMENT` identity calculation. The helper must use this exact payload:

- `version`: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`;
- `identity_kind`: `SEGMENT`;
- the exact historical `_config_payload` fields and canonical encodings;
- canonical contract;
- canonical partition enum value;
- first and last trade dates in `YYYY-MM-DD` form;
- ordered, nonempty lowercase source-ID tuple;
- exact canonical bar digest; and
- nonnegative `preceding_missing_bar_count`.

The payload must serialize with sorted JSON keys, compact separators, and
`ensure_ascii=True`, then use lowercase SHA-256 exactly as V3 did. No private
bytes or host paths may enter the identity.

The compatibility decision must be driven by the accepted manifest's exact
version, never by whether a candidate hash happens to match:

- exact V3 manifest version uses the exact local V3 segment verifier;
- exact current V5 manifest version uses the existing public
  `make_gc_dataset_id` path; and
- every other version fails closed before downstream work.

All segment IDs must reconcile under one and only one version branch. Mixing
V3 and V5 segments, retrying another branch after failure, or selecting a
branch from the desired result is forbidden.

## 8. Correction A non-goals

The future correction must not:

- modify `analysis/gc_dataset_builder.py`;
- change `GC_DATASET_BUILDER_VERSION`;
- change the public `make_gc_dataset_id` API or current V5 behavior;
- export the compatibility helper as a public API;
- rewrite stored segment IDs, dataset IDs, manifest versions, or provenance;
- make V3 the default for new construction;
- accept V1, V2, V4, arbitrary, blank, inferred, or aliased versions;
- use loose JSON, whitespace normalization, case folding, substring matching,
  or a hash-only rescue branch; or
- recover from a mismatch by falling back to the other version.

The existing outer safeguards remain mandatory: exact dataset/manifest ID
equality, manifest segment order, timezone binding, zero OOS bars, and
development-only segment partitions. The outer archived dataset ID remains an
opaque accepted binding because the continuity input does not contain every
original dataset-build identity input needed for independent reconstruction.
It must never be regenerated or silently promoted.

## 9. Defect B: pending-result reason contract mismatch

The public producer in `smc/inducement.py` emits incomplete confirmation
horizons with:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

The resolver in `analysis/gc_cross_segment_candidate_resolver.py` currently
requires `reasons == ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)`. That synthetic
token-only reason is not the producer's public output, so an authentic pending
result would fail even after continuity validation succeeds.

## 10. Correction B: exact producer-consumer alignment

A future implementation may change only the resolver consumer and its focused
tests so that `_validate_pending` requires all of the following exactly:

- status is `SMCV2PrimitiveStatus.UNKNOWN`;
- `reasons` equals
  `("one or more confirmation horizons are incomplete",)`;
- `blocking_reasons` equals
  `("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)`;
- each pending horizon's `reason_token` equals
  `NEXT_THREE_CLOSED_BARS_INCOMPLETE`; and
- all existing type, order, count, lineage, direction, identity, and
  three-closed-bar invariants continue to pass.

The resolver must reject the old token-only synthetic `reasons` tuple. It must
not accept both forms, normalize prose, use substring matching, infer a reason
from the blocker, or supply a missing value.

## 11. Correction B non-goals

The future correction must not:

- modify `smc/inducement.py`;
- change any Inducement dataclass, enum, public function, identity, or producer
  serialization;
- weaken the exact three-closed-bar horizon;
- extend resolution beyond the adjacent receiving segment;
- synthesize pending evidence from price geometry or elapsed time;
- reinterpret `NONE`, `VALID`, `AMBIGUOUS`, or `INVALID` as eligible UNKNOWN;
- accept missing, extra, reordered, duplicated, or aliased reasons; or
- grant resolution output any promotion, training, or trading meaning.

## 12. Exact public dependency bindings

Any future implementation must start from these exact committed artifacts or
STOP for a new proposal:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | `FD7688D88930A86CA005DF89A750B94D4A5748EE50F7EC95A288B9B4987AA826` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `62766E2984181B2CF04D0BA6F3354679F121704EEBD2DADC0F6F5242BC282E46` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_cross_segment_continuity.py` | `70C307AAC85FD242950A3D56C66A35AEDA5D62EABCBB2A7A6515AA700B533FC5` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `47BE9A0A0E0126F58A01C623197D043C2E35E4A975B9654501FC8498C5933D0A` |
| resolver private-run proposal | `3FBD5B30A16253B44DF28F446792E52F18B3C7A48CB688F6B819733E997F883D` |
| resolver checkpoint | `9DD09AD60A7230634127B09ED50CAC0FDE03A5DF2841487B651CFF3ABED41366` |
| UNKNOWN-manifest checkpoint | `2E9F0CAD687D7100E8C749C232B007752CAD58A45664195FF5EE215BB1016D78` |

The final SHA-256 of this proposal is computed only after its exact bytes pass
independent audit. Dependency drift is a STOP condition, not authority to
expand or improvise the correction.

## 13. Reserved exact future implementation scope

If separately authorized, the correction is reserved to exactly five paths:

1. `analysis/gc_cross_segment_continuity.py`;
2. `tests/test_gc_cross_segment_continuity.py`;
3. `analysis/gc_cross_segment_candidate_resolver.py`;
4. `tests/test_gc_cross_segment_candidate_resolver.py`; and
5. `docs/gc_futures_phase_a_cross_segment_private_diagnostic_dual_contract_correction_checkpoint.md`.

The source implementation must be test-first and atomic across both contract
corrections. A partial implementation of only one defect must not be committed
as a completed correction. No other path is implicitly authorized.

## 14. Required test-first matrix for V3 compatibility

Focused continuity tests must prove at least:

1. an exact V3 archived segment identity is accepted under an exact V3
   manifest;
2. every segment in a multi-segment V3 fixture is independently reconciled;
3. a one-byte or one-field segment identity drift is `INVALID`;
4. an arbitrary or blank legacy version is `INVALID`;
5. a V3 payload carrying a V5 segment ID is `INVALID`;
6. a V5 payload carrying a V3 segment ID is `INVALID`;
7. mixed V3/V5 segment identities are `INVALID`;
8. the existing current V5 validation path remains unchanged;
9. the accepted objects are frozen and never mutated;
10. dataset/manifest equality and exact segment order remain mandatory;
11. any OOS segment or nonzero OOS bar count remains forbidden; and
12. failure returns the existing containment status without partial manifest
    publication.

Tests must construct public in-memory fixtures. They must not read the private
accepted bundle.

## 15. Required test-first matrix for pending reasons

Focused resolver tests must prove at least:

1. the exact producer human reason plus exact blocker token is accepted;
2. token-only `reasons` is rejected;
3. a wrong, normalized, case-shifted, or extra human reason is rejected;
4. a missing, wrong, duplicated, or reordered blocker is rejected;
5. any pending-horizon reason-token mismatch is rejected;
6. an otherwise exact result with a non-UNKNOWN status is rejected;
7. pending counts and `3 - available_count` conservation remain exact;
8. lineage, direction, chronology, identity, and canonical ordering checks
   remain exact;
9. the three-closed-bar boundary is not widened; and
10. the adjacent receiving-segment boundary is not widened.

The fixture must be produced through the public Inducement API where practical,
so the test cannot preserve the earlier synthetic contract by construction.

## 16. Cross-contract regression requirements

The combined public regression must prove:

- exact V3 compatibility can advance only to the already permitted continuity
  analysis boundary;
- resolver invocation still requires preserved `UNKNOWN` /
  `CANONICAL_CONTROL_UNKNOWN` continuity with a non-null canonical manifest;
- authentic pending producer output is accepted only after all continuity,
  ownership, lineage, and receiving-group gates pass;
- malformed identity evidence has precedence over missing downstream evidence;
- malformed pending evidence has precedence over resolution semantics;
- two public in-memory executions produce object-equal results and identities;
- no private root, candidate, feature, label, model, or integration artifact is
  created; and
- Phase A remains closed and non-promotional for every result status.

## 17. Implementation invariants

The future code must preserve:

- frozen dataclasses and tuples;
- keyword-only public APIs;
- deterministic lowercase internal SHA-256 identities;
- timezone-aware timestamps and canonical integer-tick geometry;
- explicit exception containment into existing public statuses;
- canonical ordering and duplicate rejection;
- no import-time I/O, clock, randomness, network, environment, or filesystem
  dependence;
- no package export or runtime wiring changes; and
- no private-data-specific filenames, hashes, values, or branch shortcuts in
  source or tests.

The legacy helper must be local, pure, deterministic, and unreachable as a new
construction API.

## 18. Public verification gate

Before any later implementation commit, an independent audit must require:

1. exact baseline and dependency hashes from Section 12;
2. exactly the five reserved paths from Section 13 changed;
3. test-first evidence for both defects;
4. `py_compile` PASS for both source modules and focused tests;
5. focused continuity and resolver suites PASS with cache disabled;
6. the full cache-disabled public `tests/` suite PASS;
7. no new ignored or untracked runtime residue from tests;
8. no private root access or private artifact change;
9. no forbidden token, trading, model, or integration expansion; and
10. cached diff and exact staged-path audit before a separately authorized
    local commit.

A test failure, path drift, dependency drift, unexplained residue, or partial
correction is a STOP condition.

## 19. Later private rerun boundary

Even after a correct public implementation and checkpoint are committed and
separately pushed, no private diagnostic may run automatically. A later exact
private-run proposal or governing proposal must bind:

- the new implementation commit and dependency hashes;
- the unchanged accepted private input root and artifact-set identity;
- the absent final output root;
- exact temporary and final roots;
- two independent fresh reconstructions;
- atomic publish-after-complete-validation semantics;
- deterministic artifact comparison;
- independent post-run audit and cleanup; and
- explicit STOP before training, OOS, integration, or promotion.

The prior failed diagnostic is evidence of the defect, not reusable execution
authority.

## 20. Outcome semantics remain non-promotional

If a separately authorized future diagnostic reaches the resolver:

- `VALID` means only that internally consistent archived diagnostic evidence
  resolved under the exact contract;
- `NONE` means no applicable preserved horizon resolved;
- `UNKNOWN` means complete but insufficient receiving evidence;
- `AMBIGUOUS` means exact opposing same-effective diagnostic evidence; and
- `INVALID`, an exception, nondeterminism, or contract drift means transaction
  failure and no publication.

No status creates a candidate, changes the canonical negative control, opens
training or final OOS, or authorizes a trade.

## 21. Rollback rule

Before commit, rollback is deletion of only the five reserved future paths'
task-owned changes. After a separately authorized commit, rollback must be a
new reviewed commit; history rewriting, reset, checkout discard, evidence
replacement, and private-root cleanup outside an exact transaction contract
are forbidden.

If only one correction passes, both source changes must be returned to the
pre-implementation baseline. A half-corrected consumer is not an admissible
checkpoint.

## 22. Promotion and trading boundary

This proposal and any later implementation are diagnostic plumbing only. They
cannot by themselves support:

- dataset or corpus promotion;
- feature or label construction;
- model training, tuning, scoring, or comparison;
- embargo or final-OOS access;
- backtesting or outcome attribution;
- signal generation, position sizing, risk, routing, orders, or execution; or
- human or automated live-trading authority.

Those remain separate governed projects with separate evidence and explicit
authorization.

## 23. Acceptance criteria for this proposal task

This documentation-only task is complete only when:

- exactly the file in Section 4 is newly created;
- baseline and hashes reconcile;
- the diagnosis separates the two independent defects;
- both corrections are exact, consumer-side, and fail closed;
- prohibited source, test, private, training, OOS, integration, Git staging,
  commit, and push actions did not occur;
- Markdown/diff hygiene passes; and
- the worktree reports this proposal as unstaged while unrelated pre-existing
  untracked documents remain untouched.

## 24. Final decision and mandatory STOP

Decision: `PROPOSED_NOT_AUTHORIZED_FOR_IMPLEMENTATION`.

After this exact one-file proposal is written and audited, STOP. The next
single permissible action requires explicit authorization to stage this exact
proposal file and, only after cached audit PASS, create a local documentation
commit. That later action still does not authorize source or test changes,
private execution, training, OOS, integration, or push.
