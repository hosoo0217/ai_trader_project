# GC Futures Post-Phase B Pre-Training Data and Partition Readiness Decision

## 1. Decision Record

- Record date: `2026-08-24`.
- Repository baseline: `c86f01af7b98ec3eec17ca366ac7964960b1eedb`.
- Capability: project-level GC Futures pre-training data and partition readiness.
- Phase A state: `CLOSED_NEGATIVE`.
- Phase B state: `CLOSED_INSUFFICIENT_EVIDENCE`.
- Readiness state: `NOT_READY`.
- Training, OOS, integration, and trading authority: `NONE`.
- Change classification: documentation-only decision record.

This record distinguishes acquired raw evidence from a promoted training corpus.
It does not reopen Phase A or Phase B, select a setup, build data, generate features
or labels, inspect OOS, fit a model, or authorize runtime behavior.

## 2. Exact Readiness Question

The only question is whether the accepted repository and immutable private evidence
are sufficient, now, to begin model training under
`docs/gc_futures_ai_strategy_training_decision.md`.

Readiness requires all of the following at the same time: an accepted canonical
corpus, immutable lineage, sufficient independent contract coverage, an approved
feature table, an approved label table, pre-registered chronological partitions,
executed purge and embargo controls, and an untouched final OOS boundary. A file's
existence, a detector's availability, or a synthetic unit test is not a substitute.

## 3. Exact Documentation-Only Scope

The only changed path is:

- `docs/gc_futures_post_phase_b_pretraining_data_partition_readiness_decision.md`.

No source, test, fixture, dependency, configuration, private artifact, manifest,
calendar, dataset, feature, label, model, integration, or other documentation file
may change. The three unrelated pre-existing untracked documents remain untouched.

## 4. Repository and Freeze Baseline

At audit start, `HEAD` and local `origin/main` both equal
`c86f01af7b98ec3eec17ca366ac7964960b1eedb`, with ahead/behind `0/0`. The tracked
worktree is clean. `private_data/` remains ignored by `.gitignore` and is evidence,
not a tracked product surface.

Global code freeze remains active. Acceptance of this record permits only exact-path
staging, cached-content audit, one-file local documentation commit, and post-commit
verification. It does not imply push authority.

## 5. Governing Tracked Records

The following hashes were recomputed from the baseline:

| Record | SHA-256 |
|---|---|
| `docs/gc_futures_ai_strategy_training_decision.md` | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| `docs/gc_futures_phase_a_closure_and_phase_b_research_direction_decision.md` | `B3F2FCAEAC3C2FA87CFFF8D85ED43A9DE883033FDF242389FF17BDD2DD59B0CE` |
| `docs/gc_futures_dataset_checkpoint.md` | `8A93D3A81E21DF83ACC4A781C65BC2E77959B80226DD844899E3598889D180D2` |
| `docs/gc_futures_feature_label_checkpoint.md` | `B4A49A80ED52B6B4E1636BC3342BA18F03A16859F16ACB0152086498598DFD48` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_closure_decision.md` | `5166E0D14BAA65A2AAFC8E17BE2E1740EC92AFCFCCC4CCED4B60CFF964E36F75` |

The training record is a design contract only. The dataset checkpoint states that
its real private-data build was not performed. The feature/label checkpoint states
that training was not started and OOS opening was not authorized.

## 6. Intended Use and Evidence Grain

The intended future use is offline GC Futures research with chronological model
development. The atomic analytical grain is one fully reconciled candidate and its
complete source and label interval. Same-effective candidate groups are indivisible.

Contract-month files, five-minute bars, calendar rows, completed-session volume,
candidate evidence, feature rows, labels, partitions, and model outputs are distinct
layers. Passing validation at one layer never promotes a later layer implicitly.

## 7. Closed Research Evidence

Phase A is immutable `CLOSED_NEGATIVE`. Phase B is immutable
`CLOSED_INSUFFICIENT_EVIDENCE`, which is not a universal no-edge claim. Phase B V3
reported `54` candidates, `UNKNOWN`, null selected candidate/configuration, zero OOS
contact, zero feature/label/model/training/integration contact, and `NOT_READY`.

No threshold, contract, date, direction, outcome, or subset may be adjusted to rescue
either phase. Neither closed phase may supply a promoted training sample.

## 8. Private Raw Acquisition Inventory

The ignored acquisition manifest exists and has SHA-256
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
It contains `12` rows: nine canonical contract-month raw exports from `GCJ25`
through `GCQ26`, two superseded exports, and one frozen OOS snapshot. Canonical raw
row counts are `25,126`, `25,712`, `26,093`, `23,472`, `29,100`, `26,431`,
`25,470`, `27,369`, and `27,528` in contract order.

This is meaningful acquisition evidence. It proves that raw files are not absent.
It does not prove canonical session completeness, usable candidate coverage,
partition eligibility, absence of duplicated underlying periods, or training
promotion. The `GCV25` source is explicitly diagnostic, two files are superseded,
and the `GCQ26` OOS snapshot remains frozen.

## 9. Canonical Source and Lineage Readiness

Source lineage is partially ready: exact filenames, roles, trust states, byte counts,
row counts, ranges, and hashes are recorded. Superseded sources are distinguishable
from canonical sources and the OOS role is explicit.

Corpus-level lineage is not ready. No accepted promoted dataset manifest binds the
chosen sources, canonical bars, segments, roll evidence, calendar evidence,
exclusions, and a final serialized corpus hash for training. Raw-manifest lineage
must not be relabelled as dataset promotion.

## 10. Contract Continuity and Completeness

There are enough acquired contract months to make a future independent-corpus plan
plausible, but usable continuity has not been promoted. Phase B V3 left all `27`
`GCZ25` candidate configurations predecessor-blocked and all `27` `GCG26`
configurations completed-session-volume-blocked.

The exact gaps are evidence availability failures, not permission to synthesize
bars, fill missing volume with zero, infer predecessor sessions, or silently choose
a more favorable contract interval. Continuity readiness is therefore `BLOCKED`.

## 11. Calendar, Session, and Completed-Volume Readiness

The GCG26 required-calendar resolver passed for exactly ten trade dates from
`2025-12-17` through `2025-12-30`, with result SHA-256
`9B9AE65882B497ACA05645B3FAC2D82198CA89C47BE0B03B3002F247E58E4958`.
That resolution left feasibility `UNCHANGED_UNKNOWN` and training `NOT_READY`.

The completed-session-volume resolver required `5,130` records, admitted `4,972`,
left `158 UNKNOWN`, and produced zero ambiguous and zero invalid records. Its result
SHA-256 is `630BBED4AB94B98930B3C2F5F43C6FCA705C74F9573E8F322B9D51A8A48FED10`.
All `27` GCG26 candidates remain affected. Missing slots are not data values.

## 12. Dataset Promotion Readiness

No current artifact is an accepted training dataset. The canonical dataset builder
has synthetic code/test acceptance, but its checkpoint explicitly records
`Real private-data build status: NOT_PERFORMED`. Phase B private artifacts have
`promotion_authority: NONE`.

A separate Phase A private engineering pilot did contain `7,103` development bars
and zero OOS bars. Its manifest explicitly locked `training_allowed=false` and
`promotion_allowed=false`, and the research phase that consumed it is now closed.
That historical pilot is preserved evidence, not a current promotable corpus.

Dataset promotion is blocked until a separate, precommitted process selects an
independent development corpus, validates complete canonical sessions and rolls,
conserves rows and volume, emits a sanitized immutable manifest, and passes an
independent audit without touching sealed OOS.

## 13. Feature Readiness

The tracked feature builder defines deterministic mechanics and a locked 17-field
schema. That is implementation readiness, not data readiness. There is no approved
real-data feature table, feature-table hash, candidate-to-feature conservation
record, or accepted fitting subset after incomplete/invalid exclusions.

No feature may contain future bars, label outcome, OOS membership, PnL, source
filename, or later repair information. Feature readiness is `NOT_READY`.

## 14. Label Readiness

The label contract fixes horizon `H=12` closed five-minute bars and deterministic
collision/precedence rules. There is no approved real-data label table, label-table
hash, complete-horizon count, class distribution, or candidate/label positional
reconciliation for a promoted corpus.

Incomplete horizons remain `UNKNOWN`; a later repair cannot retroactively relabel a
previous research result. Label readiness is `NOT_READY`.

## 15. Chronological Partition Readiness

The only permitted order is training, model-selection validation, optional
calibration/threshold, then one final sealed OOS. Random row splitting is forbidden.
At present there are no accepted dates or immutable IDs for any of those partitions.

The frozen OOS snapshot is quarantined evidence, not automatically an accepted final
OOS partition. The previously failed OOS evidence cannot become training data or be
renamed as a new untouched OOS. Partition readiness is `NOT_READY`.

## 16. Purge, Embargo, and Leakage Readiness

The design requires complete source and label intervals inside one partition,
purging boundary-crossing labels, an embargo of at least `12` bars after each fitting
boundary, and grouping or purging overlapping labels. Duplicate or resampled views
of the same underlying period may not cross partitions.

These controls are specified but have not been executed or audited on a promoted
corpus. No-look-ahead design readiness is strong; operational leakage readiness is
not yet proven.

## 17. OOS Preservation Boundary

The frozen `GCQ26` OOS source has `5,263` rows and remains unread for outcome-based
selection under the accepted runs. Its contents must remain sealed. This record does
not inspect, copy, score, reclassify, or promote it.

The next corpus proposal must define development, validation, calibration, and final
OOS boundaries without using this snapshot's outcomes. If uncontaminated final OOS
cannot be proved, work stops rather than assigning a convenient replacement.

## 18. Data-Quality Findings and Severity

| Dimension | Evidence-backed assessment | Severity |
|---|---|---|
| Acquisition provenance | Raw files, roles, hashes, ranges, and row counts exist | ready input, not promotion |
| Lineage integrity | Source lineage exists; promoted corpus lineage does not | high blocker |
| Contract continuity | Candidate-required predecessor evidence remains unavailable | critical blocker |
| Session completeness | `158/5,130` required volume records remain unknown | critical blocker |
| Calendar coverage | Ten-row repair passed but did not resolve feasibility | high blocker |
| Uniqueness/order | Builder rules exist; no promoted-corpus audit exists | high blocker |
| Partition definition | No accepted chronological boundaries or IDs | critical blocker |
| Leakage control | Rules are locked; execution evidence is absent | critical blocker |
| OOS integrity | Quarantine is preserved; final-OOS authority is absent | critical blocker |

No uninspected raw payload is declared corrupt. Unknown evidence is not converted to
zero, valid, negative, or absent evidence.

## 19. Training and Model Readiness

Training readiness is exactly `NOT_READY`. No accepted feature matrix, target vector,
partition assignment, preprocessing fit, baseline score, model artifact, calibration,
or promotion metric exists. AI training has not started.

When data readiness eventually passes, the permitted hierarchy remains constant
baseline, deterministic rule baseline, regularized logistic regression, and at most
one separately approved gradient-boosted tree. Neural networks, reinforcement
learning, online learning, automatic retraining, and local-LLM trading authority
remain forbidden.

## 20. Integration and Trading Boundary

This decision grants no detector aggregation, package export, strategy runtime,
decision trace, engine, risk, broker, paper, or live integration. It creates no
confidence, BUY/SELL direction, entry, exit, stop, size, order, PnL, or execution
authority. Existing runtime behavior remains unchanged.

Local or remote AI may assist with bounded research review only. It may not mutate
the dataset, manufacture evidence, inspect sealed OOS, select trades, or override
deterministic safety controls.

## 21. Minimum Remediation and Next Exact Scope

The minimum next work is not training and not another strategy. It is one
documentation-only proposal at exactly:

`docs/gc_futures_independent_pretraining_corpus_acquisition_and_partition_change_proposal.md`

That proposal must pre-register one independent corpus plan, canonical source roles,
minimum contract/session completeness, chronological partition dates, atomic-group
rules, `H=12` purge/embargo, OOS quarantine, immutable manifest fields, data-quality
thresholds, rollback, promotion, and stop conditions. It must not run the plan or
alter private evidence. Any future implementation requires a later exact scope.

## 22. Exact Sequential 48-Case Acceptance Matrix

1. Baseline `HEAD` equals the published Phase B closure commit.
2. Local `origin/main` equals the same baseline with ahead/behind `0/0`.
3. Exact changed scope contains one documentation file only.
4. The three unrelated untracked documents remain unchanged.
5. The training-decision hash reconciles.
6. The Phase A/B direction-decision hash reconciles.
7. The dataset-checkpoint hash reconciles.
8. The feature/label-checkpoint hash reconciles.
9. The Phase B closure hash reconciles.
10. Phase A remains exactly `CLOSED_NEGATIVE`.
11. Phase B remains exactly `CLOSED_INSUFFICIENT_EVIDENCE`.
12. Phase B closure is not generalized into universal no-edge evidence.
13. Raw acquisition evidence is acknowledged as present.
14. Twelve manifest rows reconcile without opening frozen OOS payloads.
15. Nine canonical raw contract rows reconcile.
16. Two superseded rows remain excluded from canonical promotion.
17. The frozen OOS row remains quarantined and unread for outcomes.
18. Raw acquisition is not mislabelled as an accepted dataset.
19. Dataset private-build status remains `NOT_PERFORMED`.
20. Phase B V3 candidate count remains exactly `54`.
21. Phase B V3 status remains `UNKNOWN` with null selection.
22. All `27` GCZ25 configurations retain predecessor blockage.
23. All `27` GCG26 configurations retain volume blockage.
24. Ten-row calendar resolution remains PASS but feasibility unchanged UNKNOWN.
25. Completed-volume required count remains exactly `5,130`.
26. Completed-volume admitted count remains exactly `4,972`.
27. Completed-volume UNKNOWN count remains exactly `158`.
28. Missing volume is never synthesized or treated as zero.
29. No promoted canonical training corpus exists.
30. No approved real-data feature table exists.
31. No approved real-data label table exists.
32. Label horizon remains exactly `H=12` closed five-minute bars.
33. No chronological partition boundaries or immutable partition IDs exist.
34. Random splitting remains forbidden.
35. Same-effective candidate groups remain atomic.
36. Boundary-crossing labels require purge, never truncation.
37. Embargo remains at least `12` bars after fitting boundaries.
38. Overlapping labels and duplicated periods cannot cross partitions.
39. Frozen and previously failed OOS evidence cannot become training data.
40. OOS outcome contact remains zero under this task.
41. Training/model/feature/label/private-run contact remains zero under this task.
42. No integration or trading authority is created.
43. Final readiness is exactly `NOT_READY`.
44. The next task is one documentation-only independent-corpus proposal.
45. Fresh focused regression passes with cache disabled.
46. Fresh canonical full regression passes with cache disabled.
47. Exactly 24 numbered sections and 48 sequential cases reconcile.
48. Exact staging, cached audit, one-file local commit, and STOP-before-push pass.

## 23. Audit, Promotion, Rollback, and Stop Conditions

Independent acceptance must verify all governing hashes, private summary hashes and
counts without reading OOS outcomes, exactly `24` numbered sections, exactly `48`
sequential cases, one-file scope, formatting, cached full contents, cached
`diff --check`, artifact SHA-256/byte/line counts, and unchanged unrelated state.

Fresh cache-disabled regression after drafting produced:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py tests/test_gc_feature_label_builder.py tests/test_gc_candidate_evidence_builder.py tests/test_gc_cross_segment_continuity.py
402 passed in 2.40s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 22.57s
```

Promotion means publication of this readiness decision only. Before commit, rollback
is deletion of this one new file. After commit, rollback requires a bounded revert;
history and evidence are never rewritten.

Stop on evidence/hash drift, source-role ambiguity, missing candidate-required
coverage, corpus conservation failure, calendar/session uncertainty, partition or
roll overlap, OOS contact, leakage, insufficient independent sample, changed closed
research evidence, regression failure, scope expansion, or any request for training,
integration, paper, broker, or live authority.

## 24. Final Decision and Resume Boundary

The exact decision is:

`PRETRAINING_DATA_PARTITION_NOT_READY_REQUIRE_INDEPENDENT_CORPUS_PROPOSAL_NO_TRAINING_NO_OOS`

The project has substantial deterministic diagnostic infrastructure and acquired raw
GC evidence, but it is still in pre-training data-readiness work. AI training has not
started. The blocking facts are the absence of a promoted canonical corpus, resolved
candidate-required continuity and completed-session coverage, approved real-data
feature/label tables, chronological partitions, executed purge/embargo, and final
OOS authority.

After independent audit and one-file local commit, work must STOP before push. Only
after separate exact GitHub privacy/export authorization may this record be
published. The next single task after publication is the documentation-only proposal
named in Section 21; no private run, implementation, training, OOS, integration, or
trading is implied.
