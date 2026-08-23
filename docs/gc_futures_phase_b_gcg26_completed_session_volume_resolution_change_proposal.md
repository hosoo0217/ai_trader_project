# GC Futures Phase B GCG26 Completed-Session Volume Evidence-Resolution Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-B-GCG26-COMPLETED-SESSION-VOLUME-RESOLUTION-PROPOSAL-V1`.
- Classification: documentation-only, bounded, fail-closed evidence-resolution proposal.
- Decision: `READY_FOR_DOCUMENTATION_ACCEPTANCE_ONLY`.
- Training readiness: `NOT_READY`.
- Current task scope: this one proposal file only.

This record defines the next minimum question raised by the accepted V3 feasibility
`UNKNOWN` result. It does not execute a private diagnostic, rebuild feasibility,
select a configuration, create a canonical dataset, build features or labels, inspect
OOS, train a model, integrate runtime behavior, or authorize trading.

## 2. Controlling repository baseline

The immutable repository baseline is commit
`43a680cea980339a44e791e44d9a9dbf22a87ace`, with parent
`c24f3e60f57f84cd5693e2f47886b9f14d2cc07b` and subject
`docs: record V3 feasibility UNKNOWN decision`.

The controlling decision document is
`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v3_unknown_decision.md`,
SHA-256
`39D773C39953D69875C3C7BD0B7149E7A5534C93BDC69E46B79CD2A50102C912`.
Its final decision remains
`V3_EXECUTION_ACCEPTED_RESEARCH_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

The public builder is `analysis/gc_dataset_builder.py`, version
`GC-DATASET-BUILDER-V3-SPLIT-SESSION`, SHA-256
`79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`.
Its focused test SHA-256 is
`3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878`.
Any baseline, decision, builder, test, source, calendar, or V3 artifact drift is a
STOP requiring a new reviewed proposal.

## 3. Exact current scope and global freeze

This task may create only:

`docs/gc_futures_phase_b_gcg26_completed_session_volume_resolution_change_proposal.md`

It must not modify source, tests, fixtures, private evidence, manifests, acquisition
files, calendar artifacts, package exports, configuration, engines, integration,
models, or training outputs. The three pre-existing unrelated untracked documentation
files remain outside scope and untouched. The global code freeze remains active
everywhere else.

## 4. Exact minimum-resolution question

The sole future question is:

> Using only the already accepted five canonical Sierra Chart sources, the accepted
> 109-row merged calendar, and the unchanged public builder contract, can every
> completed-session volume key required by the 27 GCG26 feasibility candidates be
> deterministically classified as admitted or unavailable, with the exact reason for
> every unavailable key?

The answer may be `INVALID`, `AMBIGUOUS`, `UNKNOWN`, `PASS`, or `NONE`. `PASS` requires
every required key to be builder-admissible and exactly reproducible; `UNKNOWN`
preserves any deterministically unavailable key. Even `PASS` means only that this
bounded evidence inventory is complete. It does not mean that any candidate, dataset,
hypothesis, or strategy passes.

## 5. Explicitly excluded GCZ25 predecessor expansion

The 27 GCZ25 candidates remain exactly
`INITIAL_PREDECESSOR_COVERAGE_MISSING`. This proposal must not acquire or add GCV25,
change the five-source binding, replace a predecessor, reuse GCZ25 as its own
predecessor, move search dates, or alter `_previous_contract()`.

GCZ25 may be inspected only where the unchanged GCG26 initial-confirmation rule
requires it as GCG26's already-bound predecessor. That limited use does not resolve,
reclassify, or rescue the separate GCZ25 candidate family.

## 6. Immutable V3 private evidence

The accepted Git-ignored root remains:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v3/`

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 19,259 | `81BA9DD414633D2E2D32641DA72E3E6399E921E17D98592E67FADC0C82052CD3` |
| `feasibility_result.json` | 336 | `D4A4C4904D92E8C0CC73E25F718E45ACA9145B10DA2AF37C5A26000693713BB8` |
| `input_binding.json` | 8,582 | `3FD72DEFD524328FED40CD8D5E2B128C5B8ED532E0EF044F67567ACB28F8779E` |
| `scope_audit.json` | 483 | `4ED0826772FE2764077A2065AB729400BE391520EB692800067A63E400CA4511` |
| `two_run_reproducibility.json` | 612 | `2DEF825810EDB84149E708C31F542CFE13268AFE0B43A97EF9B952C1B13A5D5F` |

All five artifacts remain byte-for-byte immutable. A later diagnostic may cite and
read them but must not overwrite, repair, merge, relabel, or promote them.

## 7. Exact V3 terminal evidence

V3 contains 54 ordered `UNKNOWN` records, no selected candidate, promotion authority
`NONE`, and training readiness `NOT_READY`. The 27 GCG26 records reached the public
builder and have these exact distinct ordered reason sets:

| Distinct ordered reason set | Candidate count |
|---|---:|
| `COMPARABLE_COMPLETED_VOLUME_MISSING` | 4 |
| `INITIAL_CONFIRMATION_VOLUME_MISSING`, `COMPARABLE_COMPLETED_VOLUME_MISSING` | 23 |

Builder reason count is 2 for 12 candidates and 3 for 15. Every GCG26 builder dataset
ID is null; no complete eligible trade-date count was promoted. These observations
are immutable inputs, not conclusions that the missing evidence can be repaired.

## 8. Immutable five-source binding

The future diagnostic may read only these five already accepted source bytes in this
delivery order:

| Contract | Canonical file | SHA-256 | Builder rows after cutoff |
|---|---|---|---:|
| `GCZ25-COMEX` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` | 87 |
| `GCG26-COMEX` | `GCG26_COMEX_5m_186d_export_20260803.txt` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` | 8,778 |
| `GCJ26-COMEX` | `GCJ26_COMEX_5m_186d_export_20260803.txt` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` | 19,567 |
| `GCM26-COMEX` | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` | 25,718 |
| `GCQ26-COMEX` | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` | 14,085 |

The intake-manifest SHA-256 is
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
No source may be reacquired, replaced, expanded, truncated differently, re-exported,
rewritten, or supplemented. Observed price continuity, screenshots, an LLM, or a
different market-data provider cannot substitute for these exact bytes.

## 9. Frozen calendar and timezone binding

The accepted 109-row calendar is the disjoint deterministic join of:

- 2025 component identity
  `56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`;
- 2026 component identity
  `394eb3584f317ac781b87fd0177ef6ae4462b6989deef67141d1c6e9aada3d25`;
- merged identity
  `dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f`.

Source timezone is `Asia/Tokyo`, exchange timezone is `America/New_York`, runtime
tzdata version is `2026.2`, parser rule is
`SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2`, and normalized New York cutoff is
`2026-05-22`. Fixed-offset conversion, inferred calendar repair, or calendar-row
mutation is forbidden.

## 10. Exact 27-candidate boundary

The authorized candidate subset is exactly the 27 V3 records with
`initial_contract=GCG26-COMEX`, ordered by their existing candidate order over eligible
initial trade dates `2025-12-22..2026-01-30`, with common result end trade date
`2026-05-22` and roll confirmation count 3.

The diagnostic must not create, omit, reorder, score, rank, select, or modify a
candidate. It may derive only the completed-volume keys that the unchanged builder
would request for those exact configurations. Any different candidate count, date,
contract, end date, or ordering is `INVALID`.

## 11. Public completed-session admission contract

For each contract and calendar trade date, the unchanged public builder admits a
completed-session volume only when:

1. the calendar row has non-null opening and closing boundaries;
2. the source role equals the partition-required role;
3. every expected five-minute slot is spanned by at least one accepted bound coverage
   item, allowing the accepted coverage union to prove the complete interval;
4. capture timestamp is strictly after session close;
5. acquisition completion is at or after close for a normal session and strictly
   after close for `SPLIT_SESSION`;
6. every observed required-role row start belongs to the expected-slot set; and
7. a split session has zero missing expected rows.

For a non-split session, missing observed rows are counted but do not by themselves
prevent volume admission once exact coverage is proved. The admitted volume is the
integer sum of selected required-role row volumes. This proposal must not strengthen,
weaken, reinterpret, or silently repair that contract.

## 12. Initial-confirmation volume contract

For each GCG26 candidate, the diagnostic must identify the three eligible completed
calendar sessions immediately preceding its initial trade date. For every such date,
both `GCZ25-COMEX` and `GCG26-COMEX` completed-session volumes must be admitted under
Section 11.

A missing volume on either side is exactly
`INITIAL_CONFIRMATION_VOLUME_MISSING`. If both volumes exist but GCG26 volume is not
strictly greater than GCZ25 volume for every one of the three sessions, the unchanged
builder semantics are `INITIAL_CONTRACT_DOMINANCE_CONTRADICTION`, an `INVALID`
finding. The diagnostic may report this fact but may not choose a different initial
date or contract to avoid it.

## 13. Comparable roll-volume contract

From each candidate's initial trade date through `2026-05-22`, every eligible calendar
date follows the unchanged active-contract and exact adjacent-delivery sequence.
Current and adjacent completed-session volumes must both be admitted before comparison.
A missing side is exactly `COMPARABLE_COMPLETED_VOLUME_MISSING` and resets the
three-session dominance counter.

Adjacent dominance requires `adjacent_volume > current_volume` for three consecutive
eligible sessions; equality or lower adjacent volume resets the counter. A qualifying
roll becomes effective only on the next eligible session. Farther deliveries cannot
skip the exact adjacent delivery. The diagnostic records required evidence but must
not publish a roll plan, dataset segment, or alternative selection.

## 14. Exact per-key diagnostic record

Each future `completed_session_volume_evidence.jsonl` record has exactly:

- `evidence_id: str`;
- `candidate_id: str`;
- `evidence_use: str` (`INITIAL_CONFIRMATION` or `ROLL_COMPARISON`);
- `contract: str`;
- `trade_date: date`;
- `required_role: str`;
- `calendar_kind: str`;
- `intervals_utc: tuple[tuple[datetime, datetime], ...]`;
- `expected_slot_count: int`;
- `covered_slot_count: int`;
- `observed_required_role_slot_count: int`;
- `missing_observed_slot_count: int`;
- `unexpected_observed_slot_count: int`;
- `eligible_coverage_ids: tuple[str, ...]`;
- `admitted_volume: int | None`;
- `status: str`; and
- `reasons: tuple[str, ...]`.

All fields are required and immutable. Candidate, use, date, and canonical contract
order define chronology; hash order is never a chronology tie-break. `calendar_kind`
is exactly `SINGLE_INTERVAL` or `SPLIT_SESSION`. Duplicates, missing
fields, booleans as integers, negative counts or volume, malformed timestamps, or
unordered records are `INVALID`. Per-key status is exactly `ADMITTED`, `UNKNOWN`,
`AMBIGUOUS`, or `INVALID`; `ADMITTED` requires non-null integer volume and an empty
reason tuple, while every non-admitted status requires null volume and at least one
exact stable reason token.

The exhaustive per-key reason vocabulary is
`EXPECTED_SLOT_COVERAGE_MISSING`, `CAPTURE_NOT_STRICTLY_POST_CLOSE`,
`ACQUISITION_COMPLETION_INELIGIBLE`, `UNEXPECTED_REQUIRED_ROLE_SLOT`,
`SPLIT_SESSION_REQUIRED_SLOT_MISSING`, `BOUND_EVIDENCE_INVALID`, and
`CONTRADICTORY_CANONICAL_INTERPRETATION`. These diagnostic tokens explain evidence
availability only; they do not replace the public builder's exact
`INITIAL_CONFIRMATION_VOLUME_MISSING`, `COMPARABLE_COMPLETED_VOLUME_MISSING`, or
`INITIAL_CONTRACT_DOMINANCE_CONTRADICTION` semantics.

`evidence_id` is SHA-256 of canonical JSON containing every field above except the ID
itself, with aware timestamps normalized to UTC and tuple order preserved. The result
record has exactly `resolution_id`, `schema_version`, `status`,
`authorized_candidate_count`, `required_key_record_count`, `admitted_record_count`,
`unknown_record_count`, `ambiguous_record_count`, `invalid_record_count`,
`distinct_reasons_ordered`, `promotion_authority`, `training_readiness`,
`oos_contact_count`, and
`feature_label_model_training_integration_contact_count`. `resolution_id` hashes the
canonical result payload without its own ID plus the ordered evidence-ID tuple.
Unknown or extra fields, malformed hashes, count disagreement, nonzero contact count,
promotion authority other than `NONE`, or training readiness other than `NOT_READY`
is `INVALID`.

## 15. Evidence availability versus manufactured proof

`covered_slot_count` is established only by canonical coverage evidence, never by the
presence of a row. A missing bar cannot be synthesized as zero volume. A coverage
interval cannot be extended to the nearest session boundary. A source ending inside a
session cannot attest its remainder. Later acquisition cannot retroactively alter the
source's first or last covered timestamp.

An unavailable required key is `UNKNOWN`, not zero. An exact contradiction or
malformed bound input is `INVALID`. Distinct canonical coverage interpretations for
the same key are `AMBIGUOUS`. The diagnostic must preserve the public builder's
separate notions of expected coverage, observed rows, and admitted integer volume.

## 16. Exact future private artifact set

A separately authorized diagnostic must use fresh absent roots:

- run A: `private_data/sierra_chart/.tmp-gc_phase_b_gcg26_completed_session_volume_resolution_v1-run-a/`;
- run B: `private_data/sierra_chart/.tmp-gc_phase_b_gcg26_completed_session_volume_resolution_v1-run-b/`;
- final: `private_data/sierra_chart/gc_phase_b_gcg26_completed_session_volume_resolution_v1/`.

The final root may contain exactly:

- `input_binding.json`;
- `completed_session_volume_evidence.jsonl`;
- `resolution_result.json`;
- `scope_audit.json`;
- `two_run_reproducibility.json`.

No source copy, calendar copy, canonical bars, candidate output copy, dataset, segment,
feature, label, model, OOS payload, screenshot, or log may remain there.

## 17. Input binding and authentication

`input_binding.json` must bind the repository baseline, controlling V3 decision,
builder path/version/hash, focused-test hash, exact V3 artifacts, five source
path/name/bytes/hash/role/capture/acquisition/coverage identities, merged-calendar
components and identity, exact 27 candidate IDs, timezone/tzdata/parser/cutoff, future
proposal identity/hash, and forbidden operations.

Every path must resolve within an expected root and every byte/hash must reconcile
before content parsing. Missing inputs, path escape, symlink/reparse ambiguity,
duplicate identity, hash drift, unsupported encoding, role mismatch, timestamp drift,
or candidate mismatch is `INVALID`. No network access or source refresh is allowed.

## 18. Deterministic resolution algorithm

The future diagnostic must:

1. validate complete top-level binding and exact hashes before promotion;
2. reconstruct the accepted five source/coverage records without changing bytes;
3. reconstruct and validate the 109-row merged calendar;
4. read the exact 27 GCG26 candidate identities in existing order;
5. derive every initial-confirmation and roll-comparison volume key using the unchanged
   builder rules;
6. classify each key under Sections 11 through 15;
7. preserve every repeated candidate/key dependency rather than hiding it in a set;
8. compute deterministic record and result identities;
9. compare two fresh independent executions at object, order, identity, and byte level;
10. atomically publish only after exact scope and reproducibility PASS.

It must not invoke an alternative roll algorithm, tune dates, silently sort, fill,
deduplicate, normalize away a failure, or execute the feasibility builder as a rescue
rerun.

## 19. Atomic processing and immutable evidence

Processing is atomic by candidate and then volume-key group. A determinably later
malformed group returns `INVALID` while preserving only strictly prior diagnostic
records. Nothing from the failing group or any later group promotes. An unresolved
group returns `UNKNOWN`; no inferred admitted volume is promoted for that group.

Run A and run B are fresh reconstructions. The four core artifacts must be object-,
ordered-record-, identity-, and byte-equal before run A may be renamed atomically to
the absent final root. Existing V1, V2, V3, calendar-resolution, source, and calendar
evidence remains immutable. Cleanup uncertainty or a pre-existing output root is a
STOP without overwrite.

## 20. Status precedence and terminal meanings

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`

- `INVALID`: malformed, drifted, impossible, contradictory, unordered, or
  exception-leaking bound evidence.
- `AMBIGUOUS`: two or more distinct canonical interpretations remain for one required
  key.
- `UNKNOWN`: at least one required completed-session volume key is unavailable without
  malformed evidence.
- `PASS`: every required key for all 27 GCG26 candidates is builder-admissible and its
  exact volume is reproduced in two runs.
- `NONE`: the authorized candidate set is empty; unreachable for this locked request.

PASS authorizes only a later proposal to decide whether a feasibility rerun is
warranted. It is not candidate PASS, dataset PASS, training readiness, economic edge,
or trading authority.

## 21. Prefix invariance, no OOS, and anti-rescue boundary

Strictly later source evidence after the locked `2026-05-22` boundary cannot change
the diagnostic prefix. Same-date repair, historical insertion, source replacement,
coverage expansion, acquisition-timestamp mutation, calendar revision, reorder, or
version mutation is not a valid append and requires a new proposal.

The frozen OOS file is identity-only:
`GCQ26_COMEX_5m_30d_export_20260803.txt`, SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.
Its payload must not be opened, read, rehashed, parsed, or sampled. Feature/label,
training, inference, backtest, PnL, strategy, risk, trace, execution, broker, and live
integration contact counts remain zero.

## 22. Exact 48-case future acceptance matrix

1. Exact baseline commit, parent, subject, and V3 decision hash reconcile.
2. Builder version/hash and focused-test hash reconcile.
3. Exact five V3 artifact names, bytes, and hashes reconcile.
4. V3 status UNKNOWN, 54 records, null selection, and NOT_READY reconcile.
5. Exact 27/27 contract split and GCG26 candidate order reconcile.
6. Exact GCG26 two reason-set and 12/15 builder-count distributions reconcile.
7. Only the exact five canonical source bytes are readable.
8. Source order, contract, role, capture, acquisition, and coverage identity reconcile.
9. Intake-manifest hash and source hashes reconcile before parsing.
10. Source replacement, expansion, reacquisition, or synthetic rows reject INVALID.
11. Exact 109 calendar rows and three component/merged identities reconcile.
12. America/New_York, Asia/Tokyo, tzdata 2026.2, parser, and cutoff reconcile.
13. Fixed-offset or inferred calendar conversion rejects INVALID.
14. Exactly 27 GCG26 candidates and existing IDs/order are retained.
15. Candidate date, end date, contract, or confirmation-count mutation rejects.
16. GCZ candidate rescue and GCV predecessor expansion remain forbidden.
17. Expected slots derive exactly from every declared calendar interval.
18. Every expected slot is exactly five minutes and start-inclusive/end-exclusive.
19. Required role is DEVELOPMENT or OOS_HOLDOUT only by unchanged partition logic.
20. OOS-required evidence triggers STOP without payload access.
21. Coverage, not row presence, proves every expected slot.
22. Capture timestamp must be strictly after session close.
23. Normal acquisition completion may equal close; split completion must be later.
24. Unexpected observed required-role slot rejects volume admission.
25. Split session with one missing observed slot is unavailable.
26. Normal-session missing observed slots are counted under unchanged semantics.
27. Admitted volume is an exact nonnegative integer sum.
28. Missing bar is never synthesized as zero volume.
29. Every candidate's three prior eligible confirmation dates are exact.
30. Both GCZ25 and GCG26 volumes are required for each confirmation date.
31. Missing confirmation side emits INITIAL_CONFIRMATION_VOLUME_MISSING.
32. Non-strict GCG26 dominance emits INITIAL_CONTRACT_DOMINANCE_CONTRADICTION.
33. Current and exact adjacent volume are required for each roll comparison.
34. Missing comparison side emits COMPARABLE_COMPLETED_VOLUME_MISSING.
35. Dominance is strict greater-than for three consecutive eligible sessions.
36. Equality/lower volume or missing comparison resets confirmation count.
37. Roll is effective only on the next eligible session.
38. Farther delivery cannot skip exact adjacent delivery.
39. Exact record fields, types, no-defaults, chronology, and reasons reconcile.
40. Malformed hash, timestamp, count, volume, enum, or nested value is contained.
41. INVALID outranks AMBIGUOUS, UNKNOWN, PASS, and NONE.
42. Failing group and later groups promote nothing; strictly prior diagnostics persist.
43. Fresh run A and B are object-, order-, identity-, and byte-equal.
44. Atomic publication requires absent roots and exact five-file scope.
45. Strictly later append preserves the exact prefix.
46. Historical repair/reorder/source/calendar/version mutation is ineligible.
47. OOS, feature/label, model, training, integration, and trading contact are zero.
48. Git-ignore, global freeze, rollback, promotion, and STOP evidence reconcile.

## 23. Promotion, rollback, and STOP conditions

Documentation promotion requires independent semantic and structural audit, exactly
24 numbered sections and 48 sequential cases, cache-disabled focused and full
regression PASS, exact one-file diff, staged-content/hash audit, commit preflight, and
a local documentation commit. Remote publication requires a separate exact
privacy/export authorization.

Fresh acceptance evidence on `2026-08-24` is:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 1.06s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 23.70s
```

The explicit `tests` path is the canonical full-regression surface; Git-ignored
private evidence is not collected by pytest.

A future private diagnostic requires a new explicit authorization after this proposal
is committed, pushed, and live-remote verified. Its private root may promote only when
all bindings, required-key records, statuses, hashes, two-run equality, allowed files,
Git-ignore scope, and no-contact counters reconcile.

Before commit, rollback is deletion of only this proposal. After commit, rollback is a
bounded revert, never history rewriting. STOP immediately on any hash drift, source or
calendar mutation, unsupported role/partition, OOS dependency, evidence inference,
candidate or roll-rule change, builder rescue, unexpected file, temporary-root
residue, test failure, scope expansion, private mutation, training, integration, or
trading authority.

## 24. Final bounded decision and next single task

This proposal locks exactly one minimum evidence-resolution task: deterministic
inventory of the completed-session volumes required by the 27 existing GCG26 V3
candidates using only the already accepted inputs and unchanged public semantics.

After independent audit, local commit, separately authorized push, and live-remote
verification of this one-file proposal, the next single task may be the exact private
two-run diagnostic in Section 16. It must STOP after its independent audit. It may not
rerun feasibility, select a candidate, build a dataset, access OOS, construct features
or labels, train a model, integrate runtime behavior, or authorize trading. Global
code freeze remains active.
