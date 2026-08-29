# GC Futures Phase-A Cross-Segment Candidate Resolver Private-Run Change Proposal

## 1. Proposal record

- Proposal ID: `GC-PHASE-A-CROSS-SEGMENT-CANDIDATE-RESOLVER-PRIVATE-RUN-PROPOSAL-V1`.
- Decision date: `2026-08-29`.
- Binding source commit: `432767dcb2cc3e49c4602b4ed7052729274e93c8`.
- Binding resolver proposal commit: `422c816f619a4ab0a41724b3aeac75c7e87b2b60`.
- Classification: documentation-only private diagnostic readiness record.
- Current decision: `READY_FOR_SEPARATE_EXPLICIT_PRIVATE_RUN_AUTHORIZATION`.

This record specifies one archived, reference-only private diagnostic transaction.
It does not authorize that transaction, private-data access, feature or label
construction, training, final-OOS access, integration, execution, or trading.

## 2. Decision summary

The public cross-segment candidate resolver is implemented, regression-clean,
and deliberately non-promotional. Its only eligible continuity branch is the
preserved `UNKNOWN` / `CANONICAL_CONTROL_UNKNOWN` branch with a non-null,
canonical continuity manifest. A future private transaction may reconstruct
that branch from the already accepted development-only bundle and ask whether
the exact adjacent receiving segment completes an incomplete three-closed-bar
Inducement horizon.

The transaction is diagnostic only. A `VALID` resolver result means only that
the resolver found internally consistent archived reference evidence. It does
not create a Phase A candidate, reopen Phase A, permit corpus promotion, or
authorize training or trading.

## 3. Verified public baseline

At this proposal baseline:

- `HEAD` and local `origin/main` equal
  `432767dcb2cc3e49c4602b4ed7052729274e93c8`;
- divergence is `0/0` and the tracked worktree is clean;
- exactly three pre-existing unrelated untracked proposal documents remain
  outside this task and untouched;
- `py_compile` passes for the resolver and its focused test module;
- the focused resolver suite passes with `64 passed in 3.26s`;
- the full cache-disabled `tests/` suite passes with
  `2645 passed in 54.57s`; and
- the workspace-local pytest temporary root was removed after PASS.

Any commit, source, test, dependency, input, or identity drift before a future
private execution is a STOP condition, not authority to repair evidence.

## 4. Exact documentation-only scope

This task may create and correct only:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_private_run_change_proposal.md`

No source, test, fixture, private artifact, calendar, dataset, candidate,
feature, label, model, configuration, runtime, strategy, risk, execution,
trace, or other documentation file may change. Staging, commit, push, and
private execution remain separate later gates.

## 5. Authority and global freeze

Phase A remains `CLOSED_NEGATIVE`, and Phase A V1 remains
`RETIRED_NO_RESCUE`. This proposal grants no authority to:

- read a private payload before exact private-run authorization;
- alter, relabel, replace, normalize, repair, or delete accepted evidence;
- convert resolver output into canonical Candidate Evidence;
- create features, labels, splits, models, scores, backtests, or outcomes;
- open embargo or final-OOS payloads;
- call a local or remote language model with private market evidence;
- add package exports, runtime hooks, configuration, or integration wiring;
- generate BUY/SELL, confidence, risk, entry, exit, PnL, order, or execution
  authority; or
- stage, commit, or push under this record without the applicable later gate.

No authority is inferred from passing tests, installed code, earlier private
runs, or a prior authorization for another transaction.

## 6. Exact immutable private input root

The only admissible private source is the accepted development-only root:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

It must match the exact eight-file scope, byte lengths, SHA-256 values, member
order, and artifact-set identity
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`
already locked by
`docs/gc_futures_phase_a_cross_segment_continuity_private_run_change_proposal.md`.
That earlier record is a binding input specification, not execution authority.
Missing, extra, renamed, reordered, or hash-drifted evidence stops before
deserialization.

The transaction may deserialize only the accepted development dataset,
structural seed, canonical Candidate Evidence control, normalized calendar,
and their immutable binding metadata. It must not read the embargo interval or
the sealed final-OOS interval.

## 7. Exact public dependency bindings

The future transaction stops unless these committed artifacts match exactly:

| Artifact | SHA-256 |
|---|---|
| `analysis/gc_cross_segment_continuity.py` | `FD7688D88930A86CA005DF89A750B94D4A5748EE50F7EC95A288B9B4987AA826` |
| `analysis/gc_cross_segment_candidate_resolver.py` | `62766E2984181B2CF04D0BA6F3354679F121704EEBD2DADC0F6F5242BC282E46` |
| `smc/inducement.py` | `ABC7D21037D3399B125A7556AA56EFE6168FBCD17F0C97A360CD038455991215` |
| resolver proposal | `C1FB850B29BAC10FAE466A52FC5D9F22EFDC5EEA139D980C9260AFD7E0A8EB84` |
| resolver checkpoint | `9DD09AD60A7230634127B09ED50CAC0FDE03A5DF2841487B651CFF3ABED41366` |
| UNKNOWN-manifest checkpoint | `2E9F0CAD687D7100E8C749C232B007752CAD58A45664195FF5EE215BB1016D78` |
| resolver focused tests | `47BE9A0A0E0126F58A01C623197D043C2E35E4A975B9654501FC8498C5933D0A` |

The final SHA-256 of this proposal is computed after its bytes pass independent
audit and is bound by any later private-run input binding.

## 8. Exact reconstruction boundary

Each independent execution starts again from the immutable eight-file source
bytes and performs this fixed order:

1. verify exact root, scope, lengths, hashes, member order, and artifact-set ID;
2. verify Section 7, Git-ignore state, repository baseline, runtime timezone,
   and accepted calendar bindings;
3. deserialize fresh frozen dataset, seed, canonical control, and public SMC
   evidence without mutation;
4. reconstruct the two independently proven boundary and candidate calendar
   tuples under the accepted continuity contract;
5. call `analyze_gc_cross_segment_continuity()` exactly once;
6. require the exact eligible preserved branch from Section 9;
7. construct public pending-horizon and receiving-group wrapper tuples from
   the same immutable development evidence;
8. call `resolve_gc_cross_segment_candidates()` exactly once; and
9. validate the complete result before serializing any final artifact.

No partial output may be published after an exception or higher-precedence
failure. The second execution shares no mutable reconstructed object with the
first.

## 9. Continuity eligibility gate

The reconstructed continuity result must satisfy all of the following:

- exact `GCCrossSegmentContinuityResult` type and frozen nested graph;
- status `UNKNOWN`;
- exact reason and blocker `CANONICAL_CONTROL_UNKNOWN`;
- non-null canonical continuity manifest;
- exact manifest identity bound to all boundary and receiving-group IDs;
- ordered, unique, adjacent boundaries and canonical receiving groups; and
- zero candidate, feature, label, model, outcome, or integration authority.

`INVALID`, `AMBIGUOUS`, `VALID`, `NONE`, a null manifest, a different UNKNOWN
reason, or an identity mismatch stops before the resolver call and publishes
nothing. The older immutable private continuity output with a null manifest is
historical evidence only and is not an admissible resolver input.

## 10. Pending-horizon evidence gate

Only exact `InducementPendingHorizonResult` evidence owned by an eligible
boundary's source segment may be wrapped as
`GCSegmentPendingHorizonEvidence`. The horizon must retain the exact
`NEXT_THREE_CLOSED_BARS_INCOMPLETE` reason, original direction and lineage,
`0 <= available_count < 3`, and
`missing_confirmation_bar_count == 3 - available_count`.

Wrapper segment ordinals and IDs must be unique, strictly increasing, and
match the continuity boundary source. No horizon may be synthesized from a
price pattern, inferred from elapsed time, widened beyond three bars, or moved
across more than one adjacent boundary.

## 11. Receiving-group evidence gate

Every wrapper must identify exactly one canonical continuity receiving group
and contain only exact public observations, one matching Structure Event, one
matching Fair Value Gap, and their canonical public transition/snapshot
histories. Ownership, direction, IDs, first-known/effective moments, histories,
and source-moment references must reconcile under the committed public APIs.

Observations must be fully closed, timezone-aware, strictly ordered, unique,
and integer-tick valid. Multiple groups for the same receiving segment must
carry object-equal observations. Missing otherwise well-formed evidence may
produce `UNKNOWN`; malformed, contradictory, forked, or identity-drifted
evidence produces `INVALID` and stops publication.

## 12. Exact resolver invocation

Each execution calls exactly:

```python
resolve_gc_cross_segment_candidates(
    instrument="GC",
    timeframe="5M",
    continuity_result=continuity_result,
    pending_horizon_evidence=pending_horizon_evidence,
    receiving_group_evidence=receiving_group_evidence,
)
```

All arguments are keyword-only. The harness must not call a private helper,
fabricate an ID, decode an opaque digest, alter an observation, or retry with a
different subset after observing a result.

## 13. Outcome acceptance boundary

The transaction is observational and must not optimize for a desired status.
After complete input validation:

- `VALID` records one or more deterministic diagnostic resolutions;
- `NONE` records that no applicable preserved horizon resolved;
- `UNKNOWN` records complete but insufficient public receiving evidence; and
- `AMBIGUOUS` records exact opposing same-effective diagnostic evidence.

These four statuses are admissible negative/non-promotional observations when
their exact reason tokens, blocking reasons, identities, order, and manifest
semantics reconcile under the committed implementation. `INVALID`, exception
leakage, nondeterminism, or any status/reason mismatch is a failed transaction:
the final root remains absent.

No admissible status changes the canonical Candidate Evidence control, Phase A
closure, corpus readiness, training readiness, or trading authority.

## 14. Exact future private output root

After separate exact execution authorization, the only final root is:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

It must be absent before execution and Git-ignored. It must not overwrite,
nest inside, rename, or modify an accepted input or earlier diagnostic root.

## 15. Exact future output scope

The final root may contain only five files:

1. `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json`;
2. `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json`;
3. `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json`;
4. `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md`; and
5. `README_NON_PROMOTABLE_DIAGNOSTIC.md`.

No raw bar duplication, source export, chart, notebook, prompt, cache,
candidate payload, feature, label, outcome, model, backtest, strategy, risk,
or execution material is allowed.

## 16. Deterministic serialization

Machine-readable artifacts use UTF-8 without BOM, LF endings, one terminal
newline, sorted JSON object keys, compact separators `(",", ":")`, and
`ensure_ascii=True`. Ordered tuples serialize as ordered arrays.

Timestamps normalize to UTC ISO-8601 microseconds ending in `Z`; dates use
`YYYY-MM-DD`; finite Decimals use canonical fixed text; enums use `.value`;
identity hashes use lowercase 64-hex; outer artifact hashes use uppercase
64-hex; and zero is written as `0.0`. Host paths, object addresses, clock time,
filesystem timestamps, locale, random values, pickle, and Python `repr` are
forbidden content and identity inputs.

## 17. Input binding and artifact manifest

The input binding records at least:

- this proposal ID and final proposal SHA-256;
- source and governing proposal commits;
- exact private input scope, hashes, artifact-set ID, dataset ID, seed ID,
  calendar version/digests, timezone data version, and canonical-control digest;
- exact Section 7 dependency hashes;
- exact continuity and resolver public versions/signatures;
- one continuity call and one resolver call per execution; and
- explicit `phase_a_reopened=false`, `candidate_promoted=false`,
  `feature_label_run_performed=false`, `training_started=false`,
  `oos_outcome_accessed=false`, `integration_started=false`, and
  `trading_authority=false`.

The artifact manifest binds every other final artifact's name, byte length,
SHA-256, aggregate statuses/reasons, counts, IDs, call counts, independent-run
equality, and deterministic artifact-set identity. It excludes itself from its
member list and records exact total scope `5`.

## 18. Atomic two-run publication

Two executions build bytes in separate new task-specific temporary directories
under the private parent. Only after object equality, byte equality, identity
recomputation, exact output-scope validation, unchanged accepted input hashes,
and all STOP gates pass may one validated directory be atomically moved to the
exact Section 14 root.

On failure, remove only the two new task-specific temporary directories. Never
delete, overwrite, or repair an accepted private root. If the final root
already exists, stop without opening or modifying it.

## 19. Independent audit

The validation report independently verifies:

- exact public baseline and dependency hashes;
- exact private root scope and immutable hashes;
- calendar, dataset, seed, canonical-control, continuity, and resolver binding;
- one continuity call and one resolver call in each fresh execution;
- every public boundary, group, horizon, resolution, and manifest identity;
- status/reason precedence and deterministic ordering;
- object equality, byte equality, five-file scope, and Git-ignore state;
- unchanged `HEAD`, index, tracked worktree, public source/tests, and accepted
  private input bytes; and
- absence of OOS, feature, label, model, integration, execution, or trading
  access.

The audit must not print or copy raw private market rows into tracked output or
send them to a language model.

## 20. Minimum future verification matrix

A future harness must demonstrate at least these cases before publication:

1. exact root/scope/hash/artifact-set acceptance;
2. missing, extra, renamed, reordered, or drifted input rejection;
3. exact repository and Section 7 hash binding;
4. no embargo or final-OOS access;
5. fresh frozen reconstruction in both executions;
6. exact UNKNOWN continuity branch with non-null manifest;
7. rejection of null-manifest or noneligible continuity status/reason;
8. exact boundary/group manifest reconciliation;
9. exact pending-horizon ownership and three-bar arithmetic;
10. exact receiving-group ownership and public-object reconciliation;
11. one-adjacent-boundary limit;
12. no elapsed-time or skipped-position substitution;
13. deterministic earliest valid match selection;
14. exact opposing same-effective ambiguity handling;
15. malformed evidence returns INVALID without exception leakage;
16. complete missing evidence records UNKNOWN without fabrication;
17. no applicable horizon records NONE;
18. valid reference resolution remains non-promotional;
19. exact identity recomputation and deterministic ordering;
20. one continuity and one resolver call per run;
21. two-run object and byte equality;
22. exact five-file final scope;
23. atomic failure leaves final root absent;
24. accepted inputs and repository bytes remain unchanged; and
25. candidate, feature, label, outcome, model, training, OOS, integration,
    Git, execution, and trading surfaces remain unused.

## 21. Failure and rollback semantics

Before proposal commit, rollback is deletion of only this proposal file. After
commit, rollback requires a bounded revert, never history rewriting. A future
private transaction fails closed on baseline drift, source or input mutation,
wrong instrument/timeframe/calendar/timezone, identity mismatch, malformed or
INVALID evidence, nondeterminism, unexpected output, existing final root,
OOS contact, feature/label/model work, integration, execution, or any scope
expansion.

No failure authorizes an in-place correction, alternative input, data repair,
threshold change, second boundary, or selective rerun.

## 22. No-promotion and no-trading contract

Every artifact produced by a future authorized transaction is permanently
`NON_PROMOTABLE_DIAGNOSTIC`. It may support only archived causal inspection and
implementation validation. It cannot become:

- canonical candidate or corpus evidence;
- a feature, label, target, split, score, model input, or OOS selector;
- a strategy or risk decision;
- an order, position, trade, alert, or execution instruction; or
- justification to reopen Phase A or weaken any existing freeze.

No component has broker credentials, network authority, order-entry authority,
or permission to alter Sierra Chart.

## 23. Proposal acceptance evidence

Before any local commit, this exact one-file proposal requires:

- full content review against the two governing public proposals;
- `git diff --check` PASS;
- exact one-path scope verification;
- final proposal SHA-256 capture;
- unchanged resolver/checkpoint/test hashes;
- focused `64`-execution PASS;
- full repository regression PASS; and
- confirmation that the three unrelated untracked proposals remain untouched.

Passing this evidence authorizes only documentation acceptance. It does not
authorize private execution.

## 24. Final bounded decision and next single task

The public resolver is ready for one separately authorized, atomic, two-run
private diagnostic under this exact contract. The run may observe only archived
reference resolution and can never promote evidence into Phase A, pretraining,
training, OOS, integration, execution, or trading.

This documentation task must STOP after independent audit. Exact-path staging,
local commit, GitHub push, and private execution each remain later gates. The
next single task after proposal acceptance is one exact authorization to stage
and locally commit this file; only after that committed contract is pushed may
an exact private-run authorization be considered.
