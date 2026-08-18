# GC Futures Phase B Prospective Three-Contract Partition Feasibility V2 UNKNOWN Decision

## 1. Decision record

- Decision ID:
  `GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-V2-UNKNOWN-2026-08-19`.
- Decision date: `2026-08-19`.
- Classification: documentation-only private-feasibility outcome record.
- Repository execution and documentation baseline:
  `3f296840b3463161b05c1556d50cc768c29c28dd`.
- Public builder version: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`.
- Final bounded decision:
  `ACCEPT_DETERMINISTIC_UNKNOWN_EVIDENCE_NO_SELECTION_NOT_TRAINING_READY`.

This record accepts the corrected V2 execution as trustworthy private
feasibility evidence. It does not classify the research hypothesis as a pass
or failure, select a configuration, authorize training, or grant integration
or trading authority.

## 2. Governing proposals

The original feasibility contract is:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_change_proposal.md`

Its SHA-256 is
`531798D43DE6112EB1D743865A8E6BA24EEF794DC29CA09FA9E96811B5606DD9`.

The controlling corrected-rerun contract is:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_corrected_private_rerun_change_proposal.md`

Its proposal ID is
`GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-CORRECTED-PRIVATE-RERUN-PROPOSAL-V2`,
its SHA-256 is
`C096248B05B552DB6CF9445F408AB20956798AD406D26F57FD8E0DFF3C92C377`,
and its commit is
`3f296840b3463161b05c1556d50cc768c29c28dd`.

The corrected proposal authorizes one atomic private rerun and preserves
`UNKNOWN` whenever required predecessor, calendar, source, or coverage proof is
not available. It forbids treating blocked proof as `PASS` or `NONE`.

## 3. Exact documentation-only scope

This decision task may create, audit, stage, and locally commit only:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v2_unknown_decision.md`

Source, tests, fixtures, private artifacts, calendars, raw acquisition files,
manifests, features, labels, models, training outputs, OOS evidence,
integration, configuration, package exports, runtime, risk, execution, and
unrelated untracked files remain frozen. Remote publication requires separate
explicit GitHub privacy/export authority.

## 4. Repository and dependency binding

The execution baseline, local `HEAD`, and local `origin/main` were all
`3f296840b3463161b05c1556d50cc768c29c28dd` before this decision task.

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_v3_failure_decision.md` | `853E8A472C5EEEBC131411999DE1AF05D059C15D7943F98CB309B8EE9228DD91` |
| `docs/gc_futures_phase_b_next_hypothesis_selection_decision.md` | `889CB2DA4FB107AC05A6D9B2395A9FB7E03595C40162339000731B5BAE113AC7` |
| `docs/gc_futures_ai_strategy_training_decision.md` | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| `docs/gc_futures_split_session_calendar_checkpoint.md` | `730332BD2CE71BA9E6FEB2DD29F9100CD6125300E3563B700734CEE3F2BC6087` |

No tracked dependency byte changed during the private execution or this
documentation task.

## 5. Immutable private input binding

The corrected run bound exactly five canonical Sierra Chart acquisition
sources in delivery order:

| Contract | Canonical file | Full-source SHA-256 |
|---|---|---|
| `GCZ25-COMEX` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` |
| `GCG26-COMEX` | `GCG26_COMEX_5m_186d_export_20260803.txt` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| `GCJ26-COMEX` | `GCJ26_COMEX_5m_186d_export_20260803.txt` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| `GCM26-COMEX` | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| `GCQ26-COMEX` | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |

The intake-manifest SHA-256 was
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.
The source timezone was `Asia/Tokyo`, the exchange timezone was
`America/New_York`, the normalized tzdata version was `2026.2`, and the exact
New York trade-date cutoff was `2026-05-22`.

## 6. Frozen OOS boundary

The expected frozen OOS identity remained name
`GCQ26_COMEX_5m_30d_export_20260803.txt` and SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.

The run recorded `frozen_oos_contact_count=0`,
`post_cutoff_row_in_calculation_count=0`, and `oos_contact_count=0`. The OOS
payload was not opened, parsed, sampled, summarized, or used to choose a
configuration. This decision does not change that boundary.

## 7. Calendar binding

The run bound calendar version
`GC-2026-PROSPECTIVE-FEASIBILITY-V1-394EB3584F317AC781B87FD0177EF6AE4462B6989DEEF67141D1C6E9AADA3D25`
with exactly `99` entries and the five official evidence identities preserved
in `input_binding.json`.

The calendar contract covers accepted 2026 prospective feasibility evidence.
It does not silently infer unresolved required 2025 sessions. Missing exact
calendar coverage remains `UNKNOWN`; a standard-day assumption cannot replace
the versioned calendar input.

## 8. Corrected execution method

The V2 runner used the structural date parser rule
`SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2`. It proved unpadded and zero-padded
source-date chronology equivalent, bounded each canonical source without
sorting or rewriting it, rejected post-cutoff rows before calculation, and
passed exactly five non-empty source records to the public builder boundary.

Run A and Run B each performed a fresh reconstruction. The final publication
occurred only after exact object, ordered-record, identity, and byte equality
were established.

## 9. Exact private artifact set

The accepted Git-ignored root is:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v2/`

It contains exactly these five files:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | `3,101,510` | `A2CF163A1ADF681B261B13C4CC194E1A18F03FBB6F533E237DC1696DE9288B5C` |
| `feasibility_result.json` | `333` | `B8C26C77E1F3DFC3E47161AB924A4B330E19A171DCE1F903E6993A746B46D368` |
| `input_binding.json` | `6,069` | `E9165216B809BBA0D65010E7927382C62EEADEFF5187198250B593C55D63F03E` |
| `scope_audit.json` | `566` | `3995384742BBD15352D8715D1A5F663FE6A8E04B3775723E4D7A14A9F868B3C5` |
| `two_run_reproducibility.json` | `601` | `2073D81045FCAE4F1F8E2513AFCA695709BCB7BEF43BFE706EB9FD44EFCB5A73` |

No canonical bars, bounded source copies, candidate setups, features, labels,
models, or OOS payloads were published.

## 10. Deterministic two-run evidence

`two_run_reproducibility.json` records:

- `fresh_reconstruction_count=2`;
- `object_equality=true`;
- `ordered_record_equality=true`;
- `identity_equality=true`; and
- `byte_equality=true`.

The recorded core-artifact hashes exactly match the four non-reproducibility
artifacts in Section 9. The Run A temporary root and Run B temporary root were
absent after atomic publication; no stale temporary output was accepted.

## 11. Exact terminal result

The terminal feasibility result is:

- status: `UNKNOWN`;
- evaluated or reported configuration count: `54`;
- selected candidate ID: `null`;
- selected configuration: `null`;
- promotion authority: `NONE`;
- training readiness: `NOT_READY`;
- OOS contact count: `0`; and
- feature/label/model/training/integration contact count: `0`.

This is a valid terminal feasibility output under the governing contract. It
is not a `PASS`, `NONE`, `INVALID`, or `AMBIGUOUS` result.

## 12. Candidate matrix reconciliation

The exact matrix is the Cartesian product of:

- two initial contracts: `GCZ25-COMEX` and `GCG26-COMEX`; and
- twenty-seven eligible search dates from `2025-12-22` through `2026-01-30`.

It contains `27` records for each contract and `54` records total. Every record
has status `UNKNOWN`; every candidate ID is present and deterministic; no
record was omitted, selected, or reordered after observing its result.

## 13. Initial predecessor coverage boundary

All `27` `GCZ25-COMEX` configurations returned:

`INITIAL_PREDECESSOR_COVERAGE_MISSING`.

The governing proposal permits `GCZ25-COMEX` only when public-builder
predecessor semantics prove its required earlier contract coverage. The exact
five-source acquisition set does not provide that proof. The runner correctly
did not fabricate a predecessor, treat the first acquired contract as
self-starting, or broaden the source set.

## 14. Unresolved required 2025 calendar boundary

The six `GCG26-COMEX` configurations dated `2025-12-22`, `2025-12-23`,
`2025-12-24`, `2025-12-26`, `2025-12-29`, and `2025-12-30` returned:

`UNRESOLVED_REQUIRED_2025_CALENDAR_BINDING`.

This is an explicit proof boundary. The V2 run did not synthesize OPEN,
EARLY_CLOSE, or SESSION_CLOSED facts for these candidate dates and did not use
the 2026 calendar version as authority for unresolved 2025 evidence.

## 15. Public-builder calendar coverage boundary

The remaining `21` `GCG26-COMEX` configurations, dated `2025-12-31` and the
twenty eligible search dates from `2026-01-02` through `2026-01-30`, reached
the public builder and returned `CALENDAR_COVERAGE_MISSING`.

Across these records, builder reason counts were `5,222` for eight
configurations and `5,223` for thirteen configurations. The aggregated public
reason population was:

| Reason | Count |
|---|---:|
| `CALENDAR_COVERAGE_MISSING` | `108,318` |
| `COMPARABLE_COMPLETED_VOLUME_MISSING` | `1,336` |
| `INITIAL_CONFIRMATION_CALENDAR_MISSING` | `3` |
| `INITIAL_CONFIRMATION_VOLUME_MISSING` | `18` |

These are public-builder diagnostics, not permission to drop rows, shorten
warm-up, invent calendar entries, weaken dominance history, or select a
favorable date.

## 16. Status interpretation

The locked precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

`UNKNOWN` means required proof is unavailable within the authorized immutable
inputs. It does not prove that a qualifying three-contract partition exists,
and it does not prove that none can exist. Reclassifying it as `PASS` would
invent evidence; reclassifying it as `NONE` would overstate a negative result.

## 17. Feasibility and hypothesis decision

The execution mechanism passes its technical reproducibility and scope
contract. The research feasibility question remains unresolved.

Therefore:

- the corrected parser/source-binding defect from V1 is resolved;
- the exact V2 result is accepted as trustworthy `UNKNOWN` evidence;
- no configuration is selected;
- the prospective three-contract partition hypothesis is neither promoted nor
  retired by this record; and
- no result may be represented as a setup, trade, edge, or profitability
  finding.

## 18. Immutable V1 preservation

The original V1 root remains:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v1/`

Its exact five artifact hashes remain bound in V2 `input_binding.json`. V2
does not overwrite, delete, repair, or reinterpret V1. V1 preserves the
pre-builder date-comparison failure evidence; V2 preserves the corrected
execution and its separate `UNKNOWN` outcome.

## 19. Scope-audit conclusion

`scope_audit.json` records zero for:

- raw-source mutation;
- frozen OOS reads;
- post-cutoff calculation rows;
- canonical-bar output;
- candidate-setup output;
- feature output;
- label output;
- model output;
- training runs;
- integration changes;
- Git changes during private execution; and
- network or AI contact.

The private run therefore remained within its evidence-only authority.

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

The project remains in pre-training research and evidence-governance work.

## 21. Anti-rescue and minimum-resolution boundary

This result may not be rescued by changing the search range, result end date,
cutoff, candidate contracts, minimum dominance history, roll rules, threshold,
calendar semantics, source order, or status precedence after observing the
outcome.

A future resolution proposal may investigate only a separately justified,
minimum evidence question. It must distinguish:

1. authoritative required 2025 calendar coverage for `GCG26-COMEX`; and
2. authoritative predecessor-source coverage for `GCZ25-COMEX`.

It may not silently expand both boundaries, add a new hypothesis, inspect OOS,
or tune for a `PASS`. If the minimum evidence cannot be acquired and bound
without changing the hypothesis, this `UNKNOWN` result remains terminal.

## 22. Independent audit and regression evidence

Independent read-only audit reconciled:

- exact five-file V2 output scope, bytes, and SHA-256 values;
- exact five canonical source identities and `99` calendar entries;
- exact `54` records, `27/27` contract split, and `54 UNKNOWN` statuses;
- exact `27/6/21` top-level reason split;
- exact public-builder reason population;
- null selection, `NONE` promotion authority, and `NOT_READY` training state;
- two fresh byte/object/order/identity-equal executions;
- unchanged V1 five-file hashes;
- zero OOS, training, feature/label, integration, Git, network, and AI contact;
- absent task temporary roots; and
- unchanged unrelated untracked files.

Fresh cache-disabled regression on `2026-08-19` reproduced:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 0.98s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 22.26s
```

The explicit `tests` path remains the canonical full regression surface;
Git-ignored private evidence is not collected by pytest.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this decision file. After a
future commit, rollback requires a bounded revert; private artifacts and Git
history must not be rewritten.

This record promotes only an immutable `UNKNOWN` decision. STOP on proposal,
builder, source, calendar, V1, V2, hash, count, status, or reproducibility
drift; unexpected files; temporary-root residue; test failure; scope drift;
private mutation; inferred calendar facts; source expansion; result rescue;
feature/label work; training; OOS contact; integration; trading dependency;
broad staging; or remote push without exact privacy/export authorization.

## 24. Final bounded decision and next single task

The final bounded decision is:

`V2_EXECUTION_ACCEPTED_RESEARCH_UNKNOWN_NO_SELECTION_NOT_TRAINING_READY`.

After independent acceptance and local commit of this exact document, `STOP`
before push. The next single task is push preflight/publication of the
one-file decision commit under separate GitHub privacy/export authority.

Only after that publication may a new documentation-only proposal consider
one minimum evidence-resolution task. It may not implement a rerun, modify
calendar or source evidence, inspect OOS, build features or labels, train a
model, integrate runtime behavior, or authorize trading without its own
bounded approval. Global code freeze remains active.
