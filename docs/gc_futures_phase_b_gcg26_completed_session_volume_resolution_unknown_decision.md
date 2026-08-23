# GC Futures Phase B GCG26 Completed-Session Volume Resolution UNKNOWN Decision

## 1. Decision record

- Decision ID:
  `GC-PHASE-B-GCG26-COMPLETED-SESSION-VOLUME-RESOLUTION-UNKNOWN-2026-08-24`.
- Decision date: `2026-08-24`.
- Classification: documentation-only acceptance of a bounded private diagnostic.
- Resolution status: `UNKNOWN`.
- Promotion authority: `NONE`.
- Training readiness: `NOT_READY`.
- Trading authority: `NONE`.
- Final bounded decision:
  `ACCEPT_DETERMINISTIC_VOLUME_RESOLUTION_UNKNOWN_NO_FEASIBILITY_RERUN_NOT_TRAINING_READY`.

This record accepts the private two-run diagnostic as trustworthy evidence. It does
not relabel unavailable completed-session volume as zero, rerun feasibility, select a
candidate, build a dataset, construct features or labels, inspect OOS, train a model,
integrate runtime behavior, or authorize trading.

## 2. Governing proposal

The controlling proposal is:

`docs/gc_futures_phase_b_gcg26_completed_session_volume_resolution_change_proposal.md`

Its record ID is
`GC-PHASE-B-GCG26-COMPLETED-SESSION-VOLUME-RESOLUTION-PROPOSAL-V1`, its size is
24,389 bytes, and its SHA-256 is
`DA1855827A1C024B264F5D68745A081BF13357F0B13A3CC3E408C90BF9597E98`.
Its 24 sections and exact 48-case matrix authorize only deterministic inventory of
the completed-session volume keys required by the existing 27 GCG26 candidates.

## 3. Exact documentation-only scope

This decision task may create, audit, stage, and locally commit only:

`docs/gc_futures_phase_b_gcg26_completed_session_volume_resolution_unknown_decision.md`

Source, tests, fixtures, private artifacts, acquisition files, manifests, calendars,
features, labels, models, OOS evidence, configuration, package exports, integration,
risk, execution, and unrelated untracked files remain frozen. Remote publication
requires separate exact GitHub privacy/export authorization.

## 4. Repository and dependency binding

The private execution baseline is commit
`51430324267b30893a2964487dda3f539a6efa6f`, with parent
`43a680cea980339a44e791e44d9a9dbf22a87ace` and subject
`docs: propose GCG26 completed-session volume resolution`. Local `HEAD` and local
`origin/main` reconciled to that exact commit before execution.

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| Focused builder tests | `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878` |
| Governing proposal | `DA1855827A1C024B264F5D68745A081BF13357F0B13A3CC3E408C90BF9597E98` |
| V3 UNKNOWN decision | `39D773C39953D69875C3C7BD0B7149E7A5534C93BDC69E46B79CD2A50102C912` |
| Intake manifest | `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164` |

The public builder version remains `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. No tracked
dependency byte changed during the private execution or this documentation task.

## 5. Immutable V3 input evidence

The controlling V3 root remains:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v3/`

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 19,259 | `81BA9DD414633D2E2D32641DA72E3E6399E921E17D98592E67FADC0C82052CD3` |
| `feasibility_result.json` | 336 | `D4A4C4904D92E8C0CC73E25F718E45ACA9145B10DA2AF37C5A26000693713BB8` |
| `input_binding.json` | 8,582 | `3FD72DEFD524328FED40CD8D5E2B128C5B8ED532E0EF044F67567ACB28F8779E` |
| `scope_audit.json` | 483 | `4ED0826772FE2764077A2065AB729400BE391520EB692800067A63E400CA4511` |
| `two_run_reproducibility.json` | 612 | `2DEF825810EDB84149E7080C31F542CFE13268AFE0B43A97EF9B952C1B13A5D5F` |

V3 remains `UNKNOWN`, contains 54 ordered records, selects no candidate, grants no
promotion authority, and remains `NOT_READY` for training. This diagnostic did not
overwrite, repair, or rerun V3.

## 6. Immutable five-source binding

The diagnostic read only the five previously accepted DEVELOPMENT sources in their
existing delivery order:

| Contract | Canonical file | SHA-256 |
|---|---|---|
| `GCZ25-COMEX` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` |
| `GCG26-COMEX` | `GCG26_COMEX_5m_186d_export_20260803.txt` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| `GCJ26-COMEX` | `GCJ26_COMEX_5m_186d_export_20260803.txt` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| `GCM26-COMEX` | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| `GCQ26-COMEX` | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |

No source was copied into the result root, reacquired, replaced, expanded, repaired,
re-exported, or supplemented. The observed absence of required evidence was preserved
as absence rather than manufactured proof.

## 7. Calendar, timezone, and parser binding

The diagnostic bound the exact accepted 109-row calendar with:

- 2025 component identity
  `56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`;
- 2026 component identity
  `394eb3584f317ac781b87fd0177ef6ae4462b6989deef67141d1c6e9aada3d25`;
- merged identity
  `dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f`.

Source timezone is `Asia/Tokyo`, exchange timezone is `America/New_York`, runtime
tzdata version is `2026.2`, parser rule is
`SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2`, and normalized New York cutoff is
`2026-05-22`. No fixed-offset conversion, calendar repair, or inferred session row was
used.

## 8. Exact private execution root

The accepted Git-ignored final root is:

`private_data/sierra_chart/gc_phase_b_gcg26_completed_session_volume_resolution_v1/`

It contains exactly five allowed files. The two temporary execution roots and both
ephemeral runner/auditor files are absent. No source, calendar, candidate copy,
dataset, feature, label, model, OOS payload, screenshot, or log remains in the root.

## 9. Immutable private artifact set

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `completed_session_volume_evidence.jsonl` | 3,609,925 | 5,130 | `7C90DE56ACEF51FF13CA4D819BB479DA743B9B938F195528D58CF67456A29AA3` |
| `input_binding.json` | 12,002 | 1 | `3509DD918E36C68934C1FE50953DED7378281607D2D1FC7932118145BD8FED49` |
| `resolution_result.json` | 595 | 1 | `630BBED4AB94B98930B3C2F5F43C6FCA705C74F9573E8F322B9D51A8A48FED10` |
| `scope_audit.json` | 547 | 1 | `3E78053C4EFC8FDCDD7F16E411797FD5C64923DE24B5192292798E2ED8AADE5B` |
| `two_run_reproducibility.json` | 815 | 1 | `91355FC18FDEA86AE4BADC42A99F3DFD507E97B26D951ED70471A24F52D4B605` |

These artifacts are immutable private research evidence. A later task may cite their
identities but must not edit, overwrite, merge, move, or remotely publish them.

## 10. Input-binding correction and final reconciliation

The first independent audit correctly rejected an incomplete manifest path in the
ephemeral binding. The incomplete final root was deleted only after exact-path and
exact-five-file verification. The runner was corrected to bind:

`private_data/sierra_chart/gc_20260803_raw_intake/intake_manifest.csv`

The bound manifest reconciles to SHA-256
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
A new fresh run A and run B were then created from absent roots. Only that corrected,
independently audited execution was atomically promoted. The rejected output is not
accepted evidence and left no residue.

## 11. Deterministic two-run evidence

Run A and run B were independent fresh reconstructions. The four core artifacts are
object-equal, ordered-record-equal, identity-equal, and byte-equal. The
reproducibility status is `PASS` and `independent_run_count=2`.

The reproducibility record binds exact bytes and hashes for `input_binding.json`,
`completed_session_volume_evidence.jsonl`, `resolution_result.json`, and
`scope_audit.json`. Atomic publication occurred only after equality and exact-scope
checks passed.

## 12. Exact terminal result

`resolution_result.json` records:

- `status: UNKNOWN`;
- `authorized_candidate_count: 27`;
- `required_key_record_count: 5,130`;
- `admitted_record_count: 4,972`;
- `unknown_record_count: 158`;
- `ambiguous_record_count: 0`;
- `invalid_record_count: 0`;
- `promotion_authority: NONE`;
- `training_readiness: NOT_READY`;
- `oos_contact_count: 0`; and
- `feature_label_model_training_integration_contact_count: 0`.

The deterministic resolution ID is
`78e4d2ff5bf7191804f3c1bade05bd29e6668b363406f7dcafa4dfef35a2b864`.

## 13. Exact status and reason reconciliation

The 158 non-admitted record occurrences comprise:

- 66 `INITIAL_CONFIRMATION` occurrences;
- 92 `ROLL_COMPARISON` occurrences;
- 63 `GCZ25-COMEX`, 22 `GCG26-COMEX`, 46 `GCJ26-COMEX`, and 27
  `GCM26-COMEX` occurrences.

The exact stable reason occurrence counts are:

- `SPLIT_SESSION_REQUIRED_SLOT_MISSING`: 98;
- `EXPECTED_SLOT_COVERAGE_MISSING`: 63.

Three records carry both reasons, so reason occurrences total 161 while non-admitted
records total 158. The exact ordered reason-set distribution is 95 split-only, 60
coverage-only, and 3 coverage-then-split. No malformed or contradictory evidence was
found.

## 14. GCZ25 coverage boundary

`GCZ25-COMEX` accounts for all 63 coverage-missing occurrences. They span 21 unique
eligible trade dates from `2025-12-29` through `2026-01-29`. On `2025-12-29`, only
187 of 276 expected slots are covered and one required-role slot is observed. Later
affected normal sessions have zero covered and observed slots. Trade date
`2026-01-20` additionally carries the split-session missing-slot reason.

This is deterministic unavailability inside the exact accepted source binding. The
diagnostic does not infer that missing slots had zero volume and does not acquire a
new predecessor source, substitute a delivery, shift a candidate date, or change
`_previous_contract()`.

## 15. Split-session boundary

The split-session reason occurs only on trade dates `2026-01-20` and `2026-02-17`.
Each expected split session has 522 five-minute slots. The affected GCG26 and GCJ26
records on `2026-01-20` contain 276 observed required-role slots and 246 missing
slots. The affected GCJ26 records on `2026-02-17` have the same 276/246 split, while
GCM26 has 249 observed and 273 missing slots.

Coverage eligibility alone cannot admit a split session with missing required rows
under the unchanged public builder contract. Missing rows are therefore not filled,
reassigned, synthesized, or normalized away.

## 16. Candidate-level consequence

All 27 authorized GCG26 candidates depend on at least one unavailable volume-key
record. Consequently no candidate has complete evidence for the locked feasibility
question. This does not prove that the underlying market hypothesis is false; it
proves that the exact immutable inputs cannot establish a qualifying result under the
unchanged contract.

The diagnostic did not compute a roll plan, dataset segment, score, ranking, selected
candidate, performance statistic, or economic conclusion. A feasibility rerun from
this `UNKNOWN` inventory would merely reproduce unavailable prerequisites and is not
authorized.

## 17. Status interpretation and precedence

The locked precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

Execution integrity and two-run reproducibility are `PASS`, but the evidence result
is `UNKNOWN`. These are different claims. `UNKNOWN` means required proof is unavailable
within the authorized immutable inputs; it is not dataset `PASS`, candidate `PASS`,
`NONE`, failure of the software, or proof of no market edge.

## 18. Atomicity and immutable prior evidence

All 5,130 records retain candidate/use/contract/date chronology and deterministic
identities. Repeated candidate/key dependencies remain explicit rather than hidden by
deduplication. No unresolved key promotes an admitted volume.

The V1, V2, V3, calendar-resolution, source, manifest, and calendar evidence remains
separate and byte-immutable. The correction described in Section 10 replaced only a
rejected task-local output before acceptance; it did not alter any prior evidence.

## 19. Scope-audit conclusion

`scope_audit.json` is `PASS` with exactly 27 candidates, 109 calendar entries, five
sources, zero unexpected outputs, and zero tracked-file modifications. Every private
artifact is ignored by the existing `.gitignore` `private_data/` rule.

OOS contact, feature/label/model/training/integration contact, source copying, network
acquisition, private-output publication, and trading authority are all zero. The three
pre-existing unrelated untracked documentation files remain untouched.

## 20. Training, OOS, integration, and trading boundary

No AI or statistical model training has begun from this evidence. The following
remain prohibited:

- feature or label construction;
- model installation, fine-tuning, training, selection, or inference;
- OOS/embargo opening, repartitioning, rehashing, parsing, or inspection;
- backtest, PnL, win-rate, confidence, or economic-edge claims;
- detector, context, strategy, risk, trace, engine, paper, broker, or live integration;
- entry, exit, BUY, SELL, position sizing, or trading authority; and
- local-LLM exposure to private raw market payloads.

The project remains in pre-training evidence-resolution research.

## 21. Anti-rescue and research-direction boundary

This result may not be rescued by changing candidate dates, end date, cutoff,
contracts, predecessor mapping, calendar semantics, split-session admission,
confirmation count, roll rule, source order, source role, status precedence, or
missing-volume interpretation after observing the outcome.

The evidence identifies two different limitations: predecessor coverage and exact
split-session row completeness. Any future work must either accept them as terminal
for this hypothesis or address exactly one limitation under a new documentation-only
proposal with independently sourced evidence. It must not expand both boundaries,
tune toward `PASS`, or reopen OOS. Given that all 27 candidates are affected, the
recommended direction is closure review rather than another immediate private rerun.

## 22. Exact 48-case acceptance matrix

1. Exact baseline commit, parent, subject, and local remote-tracking ref reconcile.
2. Governing proposal path, bytes, SHA-256, 24 sections, and 48 cases reconcile.
3. Builder version/hash and focused-test hash reconcile.
4. V3 decision hash and exact five V3 artifact hashes reconcile.
5. V3 remains UNKNOWN with 54 records, null selection, and NOT_READY.
6. Exact five canonical source identities and delivery order reconcile.
7. Intake-manifest path and SHA-256 reconcile before parsing.
8. Source replacement, reacquisition, expansion, repair, or synthesis is absent.
9. Exact 109 calendar rows and three component/merged identities reconcile.
10. Timezones, tzdata 2026.2, parser rule, and cutoff reconcile.
11. Exactly 27 existing GCG26 candidates and their order are retained.
12. Exact final root is ignored and contains only five allowed artifacts.
13. Temporary A/B roots and runner/auditor files are absent.
14. Exact artifact bytes, lines, and hashes reconcile.
15. Run A and B are fresh independent reconstructions.
16. Core artifacts are object-, order-, identity-, and byte-equal.
17. Reproducibility status is PASS with independent run count two.
18. Resolution ID recomputes from exact result payload and ordered evidence IDs.
19. Exactly 5,130 evidence records exist in deterministic chronology.
20. Exactly 4,972 records are ADMITTED with non-null integer volume.
21. Exactly 158 records are UNKNOWN with null volume and stable reasons.
22. AMBIGUOUS and INVALID record counts are both zero.
23. Exact 66/92 initial/roll UNKNOWN occurrence split reconciles.
24. Exact 63/22/46/27 contract occurrence split reconciles.
25. Exact 98 split-missing reason occurrences reconcile.
26. Exact 63 coverage-missing reason occurrences reconcile.
27. Three dual-reason records explain the 161/158 count difference.
28. All 27 candidate IDs depend on at least one unavailable key.
29. GCZ25 coverage missing spans the exact 21 eligible dates.
30. GCZ25 December 29 exact expected/covered/observed counts reconcile.
31. GCZ25 later affected normal sessions have zero proven coverage.
32. January 20 split intervals contain exactly 522 expected slots.
33. January 20 GCG26/GCJ26 exact 276 observed and 246 missing reconcile.
34. February 17 GCJ26 exact 276 observed and 246 missing reconcile.
35. February 17 GCM26 exact 249 observed and 273 missing reconcile.
36. Missing rows and uncovered intervals are never synthesized as zero volume.
37. No candidate, date, delivery, predecessor, calendar, or roll rule is changed.
38. No feasibility rerun, dataset build, score, ranking, or selection occurs.
39. INVALID-over-AMBIGUOUS-over-UNKNOWN precedence remains unchanged.
40. Execution PASS is not relabeled as evidence or feasibility PASS.
41. Prior V1/V2/V3/calendar/source evidence remains immutable.
42. Exact scope audit is PASS with zero unexpected outputs.
43. OOS payload contact remains exactly zero.
44. Feature/label/model/training/integration contact remains exactly zero.
45. Git-ignored private artifacts are not staged or remotely published.
46. Unrelated untracked files remain unchanged and outside scope.
47. Fresh focused/full regression evidence and exact one-file diff reconcile.
48. Rollback, promotion, global freeze, remote-push, and STOP rules reconcile.

## 23. Regression, rollback, promotion, and STOP conditions

Independent acceptance must reconcile all 24 sections, all 48 sequential cases, the
five private artifact hashes, 5,130 ordered records, exact counts/reasons, two-run
equality, scope audit, ignored-root boundary, exact one-file Git diff, and unchanged
unrelated files.

Fresh cache-disabled regression evidence is recorded after this decision is audited:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 1.07s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 23.68s
```

Before local commit, rollback is deletion of only this decision file. After commit,
rollback requires a bounded revert, never history rewriting. Documentation promotion
requires exact-path staging, full cached-content review, cached `diff --check`,
artifact hash audit, and a one-file local commit. Remote publication requires separate
exact GitHub privacy/export authorization.

STOP on any baseline, proposal, builder, source, calendar, private-artifact, count,
reason, identity, reproducibility, test, Git-scope, or status drift; unexpected files;
temporary-root residue; evidence inference; source expansion; result rescue; OOS
contact; feature/label work; training; integration; trading dependency; broad staging;
or remote push without exact authorization.

## 24. Final bounded decision and next single task

The exact private diagnostic is accepted as deterministic `UNKNOWN`. It establishes
that the immutable five-source evidence cannot fully resolve the completed-session
volume prerequisites for any of the 27 locked GCG26 candidates. No feasibility rerun,
candidate selection, dataset promotion, or training is justified.

After independent acceptance and local commit of this exact document, work must STOP
before push. The next single task is push preflight/publication of the one-file
decision commit under separate GitHub privacy/export authority.

Only after that publication may one documentation-only closure review decide whether
to retire this Phase B hypothesis under current evidence or authorize one genuinely
independent minimum evidence acquisition. It may not combine both limitations, tune
the hypothesis, inspect OOS, build features/labels, train, integrate, or trade. Global
code freeze remains active.
