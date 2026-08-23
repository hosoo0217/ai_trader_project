# GC Futures Phase B Prospective Three-Contract Partition Feasibility V3 UNKNOWN Decision

## 1. Decision record

- Decision ID:
  `GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-V3-UNKNOWN-2026-08-24`.
- Decision date: `2026-08-24`.
- Classification: documentation-only private-feasibility outcome record.
- Repository execution baseline:
  `c24f3e60f57f84cd5693e2f47886b9f14d2cc07b`.
- Public builder version: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`.
- Final bounded decision:
  `ACCEPT_V3_DETERMINISTIC_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

This record accepts the V3 merged-calendar execution as trustworthy private
feasibility evidence. It does not classify the research hypothesis as a pass
or failure, select a configuration, authorize training, open OOS, or grant
integration or trading authority.

## 2. Governing proposal

The controlling proposal is:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v3_merged_calendar_rerun_change_proposal.md`

Its proposal ID is
`GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-V3-MERGED-CALENDAR-RERUN-PROPOSAL-V1`,
its SHA-256 is
`73AA3FE23F614ED21AC0D376A0FB452CD556EE449A17833BAF92E3F3F3AE0271`,
and its committed baseline is
`c24f3e60f57f84cd5693e2f47886b9f14d2cc07b`.

The proposal authorizes one atomic V3 private rerun, preserves all 27
predecessor-blocked GCZ25 candidates as `UNKNOWN`, and permits the 27 GCG26
candidates to receive only the merged-calendar reevaluation. It forbids
source rescue, calendar inference, tuning, OOS contact, or result promotion.

## 3. Exact documentation-only scope

This decision task may create, audit, stage, and locally commit only:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v3_unknown_decision.md`

Source, tests, fixtures, private artifacts, calendars, raw acquisition files,
manifests, features, labels, models, training outputs, OOS evidence,
integration, configuration, package exports, runtime, risk, execution, and
unrelated untracked files remain frozen. Remote publication requires separate
explicit GitHub privacy/export authority.

## 4. Repository and dependency binding

The private execution began with local `HEAD`, local `origin/main`, and live
remote `main` reconciled to
`c24f3e60f57f84cd5693e2f47886b9f14d2cc07b`.

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| Corrected V2 rerun proposal | `C096248B05B552DB6CF9445F408AB20956798AD406D26F57FD8E0DFF3C92C377` |
| V2 UNKNOWN decision | `4D9CBC66AF764A669DA78F7F63C8F96FC647C85F4163147454A67FD4C11804D9` |
| GCG26 calendar-resolution proposal | `0BC17667041E9D30560795B5FF49168A3BA69A039CD23D5495C0B8F87B2462C9` |
| GCG26 calendar-resolution PASS decision | `C21C593724DBA10E33AF872FC3BC5CE027993DA9161B8D28972BEA8ADA493CAD` |
| V3 merged-calendar proposal | `73AA3FE23F614ED21AC0D376A0FB452CD556EE449A17833BAF92E3F3F3AE0271` |

No tracked dependency byte changed during private execution or this
documentation task.

## 5. Immutable source binding

The run bound exactly five canonical Sierra Chart acquisition sources in
delivery order:

| Contract | Canonical file | Full-source SHA-256 | Builder rows after NY cutoff |
|---|---|---|---:|
| `GCZ25-COMEX` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` | 87 |
| `GCG26-COMEX` | `GCG26_COMEX_5m_186d_export_20260803.txt` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` | 8,778 |
| `GCJ26-COMEX` | `GCJ26_COMEX_5m_186d_export_20260803.txt` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` | 19,567 |
| `GCM26-COMEX` | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` | 25,718 |
| `GCQ26-COMEX` | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` | 14,085 |

The intake-manifest SHA-256 is
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
The source timezone is `Asia/Tokyo`, exchange timezone is
`America/New_York`, runtime tzdata version is `2026.2`, structural parser rule
is `SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2`, and normalized New York cutoff is
`2026-05-22`.

## 6. Frozen OOS boundary

The expected frozen OOS identity remains file name
`GCQ26_COMEX_5m_30d_export_20260803.txt` and SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.

The run records `frozen_oos_contact_count=0` and `oos_contact_count=0`. The
OOS payload was not opened, read, hashed again, parsed, sampled, summarized,
or used to choose a configuration.

## 7. Merged-calendar binding

V3 independently validated and joined:

1. the accepted ten-row 2025 calendar identity
   `56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`;
2. the accepted 99-row 2026 calendar identity
   `394eb3584f317ac781b87fd0177ef6ae4462b6989deef67141d1c6e9aada3d25`.

The components are disjoint, join exactly at `2025-12-30` / `2025-12-31`,
and produce exactly 109 ordered entries. The derived merged identity is
`dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f`
and the common builder-entry version is
`GC-PHASE-B-MERGED-CALENDAR-V1-dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f`.

Only ephemeral builder-entry calendar versions changed. Original component
artifacts, rows, identities, versions, and evidence remained immutable.

## 8. Execution method

The run used coarse JST bounds `2025-12-17..2026-05-23`, normalized New York
trade-date cutoff `2026-05-22`, and the unchanged public keyword-only builder
boundary. It did not sort, rewrite, synthesize, or broaden any source.

Run A and Run B each performed a fresh reconstruction. The final publication
occurred only after exact object, ordered-record, identity, and byte equality
were established. Temporary roots were removed only after resolved-path and
exact-scope verification.

## 9. Exact private artifact set

The accepted Git-ignored root is:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v3/`

It contains exactly these five files:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 19,259 | `81BA9DD414633D2E2D32641DA72E3E6399E921E17D98592E67FADC0C82052CD3` |
| `feasibility_result.json` | 336 | `D4A4C4904D92E8C0CC73E25F718E45ACA9145B10DA2AF37C5A26000693713BB8` |
| `input_binding.json` | 8,582 | `3FD72DEFD524328FED40CD8D5E2B128C5B8ED532E0EF044F67567ACB28F8779E` |
| `scope_audit.json` | 483 | `4ED0826772FE2764077A2065AB729400BE391520EB692800067A63E400CA4511` |
| `two_run_reproducibility.json` | 612 | `2DEF825810EDB84149E708C31F542CFE13268AFE0B43A97EF9B952C1B13A5D5F` |

No source copy, canonical bars, candidate setups, features, labels, models, or
OOS payloads were published.

## 10. Deterministic two-run evidence

`two_run_reproducibility.json` records:

- `fresh_reconstruction_count=2`;
- `object_equality=true`;
- `ordered_record_equality=true`;
- `identity_equality=true`; and
- `byte_equality=true`.

The recorded core-artifact hashes exactly match the four
non-reproducibility artifacts in Section 9. Only the exact final V3 root
remains; no task temporary root is present.

## 11. Exact terminal result

The terminal feasibility result is:

- status: `UNKNOWN`;
- evaluated or reported candidate count: `54`;
- selected candidate ID: `null`;
- selected configuration: `null`;
- promotion authority: `NONE`;
- training readiness: `NOT_READY`;
- OOS contact count: `0`; and
- feature/label/model/training/integration contact count: `0`.

This is a valid terminal feasibility output under the governing contract. It
is not `PASS`, `NONE`, `INVALID`, or `AMBIGUOUS`.

## 12. Candidate matrix reconciliation

The exact matrix is the Cartesian product of:

- two initial contracts: `GCZ25-COMEX` and `GCG26-COMEX`; and
- 27 eligible search dates from `2025-12-22` through `2026-01-30`.

It contains 27 records for each contract and 54 records total. Every record is
`UNKNOWN`; every candidate ID is present and deterministic; no record was
omitted, selected, reordered, or copied from V2 after observing its result.

## 13. GCZ25 predecessor boundary

All 27 `GCZ25-COMEX` configurations returned exactly:

`INITIAL_PREDECESSOR_COVERAGE_MISSING`.

This is the proposal's locked anti-rescue result. The five-source acquisition
set cannot prove the required earlier adjacent delivery. V3 correctly did not
fabricate a predecessor, reuse GCZ25 as its own predecessor, alter the search
dates, or broaden the source set.

## 14. GCG26 volume-evidence boundary

All 27 `GCG26-COMEX` configurations reached the public builder with
`builder_status=UNKNOWN`, a null builder dataset ID, no segments, and no
complete eligible trade-date counts.

The exact distinct-reason sets are:

| Distinct ordered reason set | Candidate count |
|---|---:|
| `COMPARABLE_COMPLETED_VOLUME_MISSING` | 4 |
| `INITIAL_CONFIRMATION_VOLUME_MISSING`, then `COMPARABLE_COMPLETED_VOLUME_MISSING` | 23 |

Builder reason count is 2 for 12 candidates and 3 for 15 candidates. Repeated
reason instances are preserved by the public builder count while the V3
record stores the deterministic distinct order separately.

## 15. Calendar correction outcome

The V2 reason `UNRESOLVED_REQUIRED_2025_CALENDAR_BINDING` and public-builder
reason `CALENDAR_COVERAGE_MISSING` no longer occur in V3. This proves only
that the accepted 2025 component and deterministic merged-calendar mechanism
resolved the authorized calendar boundary.

It does not prove roll dominance, completed-session volume, a valid
three-contract partition, training readiness, or economic edge. Calendar
resolution therefore cannot be relabeled as feasibility `PASS`.

## 16. Status interpretation

The locked precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

`UNKNOWN` means required proof is unavailable within the authorized immutable
inputs. It neither proves that a qualifying partition exists nor proves that
none can exist. Reclassifying it as `PASS` would invent evidence;
reclassifying it as `NONE` would overstate a negative result.

## 17. Feasibility and hypothesis decision

The execution mechanism passes technical reproducibility, calendar binding,
scope, and atomic-publication requirements. The research feasibility question
remains unresolved.

Therefore:

- the V2 calendar-coverage defect is resolved;
- the V3 result is accepted as trustworthy `UNKNOWN` evidence;
- no configuration is selected;
- the prospective three-contract partition hypothesis is neither promoted
  nor retired; and
- no result may be represented as a setup, trade, edge, or profitability
  finding.

## 18. Immutable prior-evidence preservation

V1, V2, and the GCG26 calendar-resolution roots remain separate immutable
provenance layers. V3 cites their exact hashes but does not overwrite, delete,
repair, merge, or reinterpret their stored artifacts.

The V2 `UNKNOWN` outcome remains historically true for its authorized inputs.
The 27 GCZ25 predecessor diagnostics remain unchanged. V3 adds only the
separate merged-calendar rerun evidence.

## 19. Scope-audit conclusion

`scope_audit.json` records exactly five allowed output names, one final root,
54 candidates, 109 calendar entries, and zero for source copies, OOS payload
contact, feature/label build, model training, and integration.

The private run made no Git change, used no network or AI inference, did not
contact post-cutoff/OOS evidence, and did not publish private payloads to the
repository.

## 20. Training, OOS, integration, and trading boundary

No AI or statistical model training has begun from this evidence. The
following remain prohibited:

- feature or label construction;
- model installation, fine-tuning, training, selection, or inference;
- OOS or embargo opening, repartitioning, or inspection;
- backtest, PnL, win-rate, confidence, or edge claims;
- detector, strategy, risk, trace, engine, paper, broker, or live integration;
- entry, exit, BUY, SELL, sizing, or trading authority;
- local-LLM exposure to private raw market payloads; and
- staging or remotely publishing private artifacts.

The project remains in pre-training evidence-resolution research.

## 21. Anti-rescue and minimum-resolution boundary

This result may not be rescued by changing search dates, result end date,
cutoff, candidate contracts, minimum dominance history, roll rules, threshold,
calendar semantics, source order, or status precedence after observing the
outcome.

A future documentation-only proposal may consider exactly one minimum
evidence-resolution question. It must keep distinct:

1. authoritative predecessor-source coverage for `GCZ25-COMEX`; and
2. authoritative completed-session volume proof for the GCG26 candidate
   sequence.

It may not silently expand both boundaries, add a new hypothesis, inspect OOS,
or tune for `PASS`. If the minimum evidence cannot be acquired and bound
without changing the hypothesis, this `UNKNOWN` result remains terminal.

## 22. Independent audit and regression evidence

Independent acceptance must reconcile:

- exact five-file V3 output scope, bytes, and SHA-256 values;
- exact five canonical source identities and 109 calendar entries;
- exact 54 records, 27/27 contract split, and 54 `UNKNOWN` statuses;
- exact 27 predecessor-blocked and 27 public-builder-evaluated records;
- exact GCG26 distinct-reason-set and builder-reason-count distributions;
- null selection, `NONE` promotion authority, and `NOT_READY` training state;
- two fresh byte/object/order/identity-equal executions;
- unchanged V1, V2, and calendar-resolution evidence;
- zero OOS, training, feature/label, integration, Git, network, and AI contact;
- absent task temporary roots; and
- unchanged unrelated untracked files.

Fresh cache-disabled regression evidence on `2026-08-24`:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 1.04s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 25.10s
```

The explicit `tests` path remains the canonical full regression surface;
Git-ignored private evidence is not collected by pytest.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this decision file. After a
future commit, rollback requires a bounded revert; private artifacts and Git
history must not be rewritten.

This record promotes only immutable `UNKNOWN` evidence. STOP on proposal,
builder, source, calendar, V1, V2, V3, hash, count, status, reason,
reproducibility, or test drift; unexpected files; temporary-root residue;
scope drift; private mutation; inferred evidence; source expansion; result
rescue; feature/label work; training; OOS contact; integration; trading
dependency; broad staging; or remote push without exact privacy/export
authorization.

## 24. Final bounded decision and next single task

The final bounded decision is:

`V3_EXECUTION_ACCEPTED_RESEARCH_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

After independent acceptance and local commit of this exact document, work
must STOP before push. The next single task is push preflight/publication of
the one-file decision commit under separate GitHub privacy/export authority.

Only after that publication may a new documentation-only proposal consider
one minimum evidence-resolution task. It may not implement a rerun, acquire or
modify source evidence, inspect OOS, build features or labels, train a model,
integrate runtime behavior, or authorize trading without its own bounded
approval. Global code freeze remains active.
