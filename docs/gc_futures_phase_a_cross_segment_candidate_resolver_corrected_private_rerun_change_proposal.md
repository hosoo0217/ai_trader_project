# GC Futures Phase-A Cross-Segment Candidate Resolver Corrected Private-Rerun Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-CORRECTED-PRIVATE-RERUN-PROPOSAL-V1`.
- Decision date: `2026-08-30`.
- Binding implementation commit: `1544f6b021e9d443affb163a02b0e83e98e7a910`.
- Governing correction proposal commit: `53bed99a909e1bad6983b8c8640691124fba6efb`.
- Superseded execution contract: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-PRIVATE-RUN-PROPOSAL-V1`.
- Classification: documentation-only, fail-closed corrected private diagnostic proposal.
- Current decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_RERUN`.

This record replaces only the stale dependency and reconstruction bindings of
the earlier failed private-run contract. It does not authorize private-data
access, a private rerun, dataset or corpus construction, feature or label
construction, training, final-OOS access, integration, execution, or trading.

## 2. Decision summary

The earlier authorized private diagnostic stopped deterministically before
meaningful continuity or resolver evaluation. The continuity consumer rejected
the accepted archived V3 segment identities through the current V5 identity
path, and the resolver separately expected a synthetic token-only pending
reason instead of the authentic public Inducement producer contract.

Commit `1544f6b021e9d443affb163a02b0e83e98e7a910` corrected both consumer-side
contracts without mutating accepted evidence, the current dataset builder, the
Inducement producer, or any public API. A future corrected rerun is therefore
permissible only under a new exact transaction contract that binds the corrected
implementation and independently re-verifies every private input and output
gate. The prior failed authorization is not reusable execution authority.

## 3. Verified public baseline

At this proposal baseline:

- `HEAD` and local `origin/main` both equal
  `1544f6b021e9d443affb163a02b0e83e98e7a910`;
- divergence is `0/0` and the tracked worktree is clean;
- exactly three pre-existing unrelated untracked proposal documents remain
  outside this task and untouched;
- continuity plus resolver focused tests passed with `126 passed`;
- Inducement producer plus continuity plus resolver tests passed with
  `344 passed`; and
- the full cache-disabled public suite passed with `2659 passed`.

Any baseline, dependency, input, or identity drift before a separately
authorized execution is a STOP condition, not authority to repair evidence.

## 4. Exact documentation-only scope

This task may create and correct only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_corrected_private_rerun_change_proposal.md`

No source, test, fixture, private artifact, calendar, dataset, candidate,
feature, label, model, configuration, runtime, strategy, risk, execution,
trace, or other documentation file may change. Staging, local commit, push,
and private execution remain separate later gates.

## 5. Authority and global freeze

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. This proposal grants no authority to:

- open or deserialize a private payload before exact rerun authorization;
- alter, relabel, replace, normalize, repair, or delete accepted evidence;
- convert a diagnostic resolver output into canonical Candidate Evidence;
- build a dataset, corpus, feature, label, target, split, model, or outcome;
- access the embargo interval or sealed final-OOS payload;
- add exports, configuration, runtime hooks, or integration wiring;
- call a local or remote language model with private market evidence;
- produce a signal, risk decision, order, position, or execution; or
- stage, commit, push, or execute under this record without the applicable
  later exact authorization.

Passing tests or a later diagnostic status cannot lift these restrictions.

## 6. Binding correction evidence

The corrected implementation is governed by:

- correction proposal SHA-256
  `8475FA14319A59517296596861BED61151B125C3C411CE6F871FD92FD85B3305`;
- correction checkpoint SHA-256
  `8A7B28E34E55F649C7D8030AF3D0A8D9BD8FD0FF1AE2B7736F6D7A132C86E78B`;
- earlier resolver private-run proposal SHA-256
  `3FBD5B30A16253B44DF28F446792E52F18B3C7A48CB688F6B819733E997F883D`;
- resolver checkpoint SHA-256
  `9DD09AD60A7230634127B09ED50CAC0FDE03A5DF2841487B651CFF3ABED41366`;
  and
- UNKNOWN-manifest preservation checkpoint SHA-256
  `2E9F0CAD687D7100E8C749C232B007752CAD58A45664195FF5EE215BB1016D78`.

The earlier private-run proposal remains a reference for input scope,
serialization, non-promotion, and atomic transaction shape. Its pre-correction
source/test hashes and its prior execution authority are expressly superseded.

## 7. Exact corrected public dependency bindings

A future private transaction must stop unless these committed artifacts match
exactly:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `analysis/gc_cross_segment_continuity.py` | `0E832CE800AF7F771239E2982693B23AB0B5C665CE38C9326A9A8499BC1131F6` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `FF2D8E01C64BF535F92A9879EFCC4A8D028889B4D72C1788CDEDE53946D52040` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| `tests/test_gc_cross_segment_continuity.py` | `13FDFC924E6ED906C53C6B300464FE5F058A8DA45BA4366DC37B174AF6CAE3C7` |
| `tests/test_gc_cross_segment_candidate_resolver.py` | `E69BE23B048BF5C57D2DBC2F795691867D487282B51F2103B5E9AB4E0B880826` |

The final SHA-256 of this proposal is computed after its exact bytes pass
independent audit and must be bound by any later execution preflight.

## 8. Exact immutable private input binding

The only admissible private source remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

At future execution preflight it must match the exact eight-file scope, names,
byte lengths, SHA-256 values, member order, and artifact-set identity
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`
locked by the continuity private-run proposal. Missing, extra, renamed,
reordered, or hash-drifted evidence stops before deserialization.

Only the accepted development dataset, structural seed, canonical Candidate
Evidence control, normalized calendar, and immutable binding metadata may be
deserialized. The embargo interval and sealed final-OOS payload must not be
opened, listed for payload selection, copied, summarized, or hashed anew.

This documentation task does not inspect the private input root.

## 9. Corrected continuity reconstruction gate

Each future run must deserialize fresh immutable objects and validate the
accepted manifest version before any segment identity reconciliation:

- exact `GC-DATASET-BUILDER-V3-SPLIT-SESSION` selects the committed local V3
  segment verifier;
- exact `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION` selects the unchanged
  current public V5 verifier; and
- every other version stops with no downstream call or output.

All accepted archived segments must reconcile through exactly one selected
branch. There is no retry, mixed-version rescue, hash-success branch selection,
segment-ID rewrite, outer dataset-ID regeneration, or mutation. The corrected
run must record that the accepted V3 graph is verified, not converted to V5.

## 10. Corrected pending-result contract gate

Only the authentic public Inducement incomplete-horizon contract is eligible:

```text
status = UNKNOWN
reasons = ("one or more confirmation horizons are incomplete",)
blocking_reasons = ("NEXT_THREE_CLOSED_BARS_INCOMPLETE",)
pending_horizon.reason_token = "NEXT_THREE_CLOSED_BARS_INCOMPLETE"
```

The earlier token-only synthetic `reasons` tuple must be rejected. No alias,
normalization, substring match, reason inference, dual acceptance, or fixture
repair is allowed. All existing ownership, count, lineage, direction,
chronology, identity, three-closed-bar, and one-adjacent-segment invariants
remain mandatory.

## 11. Exact corrected two-run transaction

After a separate exact private-rerun authorization, each of two independent
executions must perform this fixed order:

1. verify the exact repository commit, proposal/checkpoint hashes, Git-ignore
   state, runtime timezone, and Section 7 dependencies;
2. verify the exact private root, eight-file scope, hashes, member order, and
   artifact-set identity before deserialization;
3. deserialize fresh frozen development objects with no mutable sharing between
   runs;
4. reconstruct the two independently proven boundary and candidate calendar
   tuples under the corrected continuity contract;
5. call `analyze_gc_cross_segment_continuity()` exactly once;
6. require exact `UNKNOWN` / `CANONICAL_CONTROL_UNKNOWN` with a non-null,
   canonical continuity manifest;
7. construct pending-horizon and receiving-group wrappers only from the same
   immutable development evidence and authentic producer contract;
8. call `resolve_gc_cross_segment_candidates()` exactly once;
9. validate complete object identity, status/reason precedence, counts, order,
   and non-promotion flags; and
10. compare both complete object graphs and serialized byte sets before any
    final publication.

An `INVALID` continuity result, null manifest, ineligible status/reason,
malformed wrapper, exception, nondeterminism, hash drift, or unexpected file
is a transaction failure. No subset retry or evidence repair is permitted.

## 12. Exact output root and scope

The only future final root remains:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

At execution preflight it must be absent and Git-ignored. If it exists, stop
without opening, replacing, or modifying it. This documentation task does not
inspect that root.

The final root may contain only:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw rows, source export, candidate payload, feature, label, outcome, model,
backtest, prompt, cache, strategy, risk, or execution artifact is allowed.

## 13. Determinism and atomic publication

Machine-readable artifacts use UTF-8 without BOM, LF endings, one terminal
newline, sorted keys, compact JSON separators, and `ensure_ascii=True`.
Timestamps, dates, decimals, enums, tuple order, identities, and outer hashes
follow the earlier private-run proposal's exact canonical rules.

Both executions build in distinct, newly created task-specific temporary
directories under the private parent. Only after object equality, byte
equality, identity recomputation, exact five-file scope, unchanged accepted
input hashes, and all STOP gates pass may one validated directory be atomically
moved to the final root.

On failure, remove only the two task-owned temporary directories. Never delete,
overwrite, rename, or repair an accepted input or an existing final root.

## 14. Outcome boundary

The transaction observes rather than optimizes a result:

- `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` is admissible only when its exact
  public status, reason, blocker, identity, order, and manifest semantics pass;
- `INVALID`, exception leakage, nondeterminism, or contract drift fails the
  transaction and leaves the final root absent.

Every admissible output remains permanently
`NON_PROMOTABLE_DIAGNOSTIC`. It cannot reopen Phase A, alter the canonical
negative control, enter a corpus, become a feature/label/model input, expose an
OOS outcome, or authorize training, integration, prediction, or trading.

## 15. Independent post-run audit

Any later authorized execution must independently verify:

- exact commit, proposal/checkpoint, public dependency, and private input
  bindings;
- one continuity and one resolver call per fresh run;
- exact V3 identity selection with no accepted-evidence mutation;
- authentic human reason plus exact blocker-token enforcement;
- every boundary, group, horizon, resolution, and manifest identity;
- deterministic object and byte equality and exact five-file final scope;
- unchanged `HEAD`, index, tracked worktree, public source/tests, and accepted
  private input bytes;
- cleanup of only task-owned temporary roots; and
- no OOS, feature, label, corpus, model, training, integration, execution, or
  trading access.

The audit must not print, copy, or send raw private market rows to a language
model or tracked output.

## 16. Minimum corrected verification matrix

A future harness must demonstrate at least:

1. exact baseline/dependency/proposal/input acceptance and drift rejection;
2. exact archived V3 selection and all-segment reconciliation;
3. rejection of V3/V5 mismatch, mixed identities, and unsupported versions;
4. preservation of current V5 behavior without rebuilding the archive;
5. exact eligible continuity UNKNOWN branch with non-null manifest;
6. rejection of null-manifest or noneligible continuity results;
7. authentic producer reason/blocker acceptance and token-only rejection;
8. exact boundary, group, pending-horizon, lineage, direction, and three-bar
   arithmetic reconciliation;
9. no elapsed-time, skipped-position, widened-horizon, or multi-boundary
   substitution;
10. deterministic `VALID`, `NONE`, `UNKNOWN`, or `AMBIGUOUS` handling and
    fail-closed `INVALID` handling;
11. exactly one continuity and one resolver call in each run;
12. two-run object and byte equality;
13. atomic failure leaves the final root absent;
14. accepted input and repository bytes remain unchanged; and
15. no candidate promotion, corpus/feature/label/model work, training, OOS,
    integration, execution, Git mutation, or trading authority.

## 17. Failure and rollback semantics

Before proposal commit, rollback is deletion of only this new proposal file.
After a separately authorized commit, rollback requires a new reviewed commit;
history rewriting and evidence replacement are forbidden.

A future transaction fails closed on any baseline drift, hash mismatch,
unexpected root state, malformed evidence, nondeterminism, OOS contact,
forbidden artifact, or scope expansion. Failure does not authorize an in-place
correction, alternate input, threshold change, selective rerun, source edit,
or publication of partial diagnostic output.

## 18. Proposal acceptance gate

Before any local documentation commit, this exact one-file proposal requires:

- full content review against the earlier private-run proposal, correction
  proposal, and correction checkpoint;
- exact Section 7 hash recomputation;
- `git diff --check` PASS;
- exact one-path task scope verification;
- final proposal SHA-256 capture;
- focused continuity/resolver regression PASS;
- full public regression PASS; and
- confirmation that the three unrelated untracked proposals remain untouched.

Passing this gate authorizes only documentation acceptance. It does not
authorize private execution.

## 19. Required later authorization sequence

The only permitted next gates are separate and ordered:

1. exact one-path staging plus cached audit and local documentation commit;
2. separate GitHub privacy/export authorization for that exact commit;
3. post-push audit proving local `HEAD` equals `origin/main`; and
4. separate exact private-rerun authorization binding the committed proposal,
   corrected implementation, immutable input, absent output root, two fresh
   runs, atomic publication, independent audit, and mandatory STOP.

No broad trust statement, earlier failed-run authorization, implementation
authorization, test PASS, commit, or push implies the next gate.

## 20. Final decision and mandatory STOP

Decision: `PROPOSED_NOT_AUTHORIZED_FOR_PRIVATE_RERUN`.

After this exact one-file proposal is written and independently audited, STOP.
The next single permissible mutation requires exact authorization to stage and
locally commit this proposal file. Private payload access and the corrected
two-run diagnostic remain forbidden until their later exact authorization.
