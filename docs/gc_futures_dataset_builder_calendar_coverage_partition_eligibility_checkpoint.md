# GC Futures Dataset Builder Calendar Coverage/Partition Eligibility Checkpoint

## 1. Checkpoint Identity

- Date: `2026-08-25`.
- Governing proposal commit:
  `cff665257832004fe4467308f239e0f0bf51f50d`.
- Governing proposal SHA-256:
  `0E007FAB1EA278AA4142F426195479B7562E0563F8237F59FB9C1DDDAEF9633E`.
- Builder version: `GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`.
- Implementation status: `LOCAL_IMPLEMENTATION_COMPLETE_NOT_STAGED`.
- Private rerun, corpus build, feature/label build, training, final-OOS access, integration,
  commit, push, and trading status: `NOT_PERFORMED`.
- Global freeze outside the exact three-path task: `ACTIVE`.

## 2. Exact Authorized Scope

Only these paths changed:

- `analysis/gc_dataset_builder.py`
- `tests/test_gc_dataset_builder.py`
- `docs/gc_futures_dataset_builder_calendar_coverage_partition_eligibility_checkpoint.md`

No private source, normalized calendar, external fixture, package export, downstream builder,
detector, strategy, engine, configuration, OOS artifact, integration file, or other documentation
changed. The three pre-existing user-owned untracked proposals remained untouched.

## 3. Test-First and Regression Evidence

The source correction began only after public-builder tests reproduced the defect. The initial
targeted RED run was:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py -k "calendar_coverage_does_not or roll_confirmation_crosses or v2_manifest_binds or exact_public_surface" --tb=short
5 failed, 248 deselected in 0.75s
```

The failures proved that covered gap rows were silently promoted, no `PARTITION_EMBARGO` evidence
was emitted, and the algorithm version was still V4. One roll test also exposed incomplete
post-roll adjacent coverage in its synthetic fixture; the fixture was completed without changing
the locked production semantics. The implementation then changed only the authorized behavior.

Final focused evidence:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
253 passed in 1.13s
```

Final canonical full-regression evidence:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2527 passed in 23.94s
```

A root-level pytest attempt was stopped during collection because three protected private-data
directories correctly returned `Access denied`. It was not a test failure and no private payload
was read. The repository's canonical `tests/` suite above completed cleanly.

## 4. Coverage and Partition Semantics

Calendar coverage and partition eligibility are now independent predicates. The unchanged
eligibility calendar remains `255` trade dates / `252` completed-session intervals. Later upstream
calendar coverage may contain `275` trade dates / `272` intervals, including these exact covered
but ineligible embargo windows:

- `[2025-06-02, 2025-06-16)`;
- `[2025-08-25, 2025-09-08)`.

Rows in either window must still pass exact source role, calendar/session, five-minute-grid, source
identity, and coverage validation. Validated rows remain available only to the internal completed-
session volume stream and can causally contribute to the existing three-session roll proof. They
never enter a promoted segment and are conserved in the exclusion ledger with the exact reason
`PARTITION_EMBARGO`.

Rows before the initial boundary remain `BEFORE_INITIAL_BOUNDARY`; rows after the OOS end remain
`AFTER_OOS_BOUNDARY`. Missing calendar evidence remains `UNKNOWN` with
`CALENDAR_COVERAGE_MISSING`, and malformed evidence remains fail-closed `INVALID`.

## 5. Partition Plan and Atomic Behavior

The locked partition plan is unchanged:

- TRAIN: `[2024-11-04, 2025-06-02)`;
- embargo gap 1: `[2025-06-02, 2025-06-16)`;
- VALIDATION: `[2025-06-16, 2025-08-25)`;
- embargo gap 2: `[2025-08-25, 2025-09-08)`;
- CALIBRATION: `[2025-09-08, 2025-11-24)`;
- final OOS: `[2026-07-06, 2026-08-01)`.

The public builder continues to expose only the existing DEVELOPMENT/OOS partitions. Embargo rows
are an internal eligibility exclusion and do not add an enum value, public partition, hidden
training split, or public API parameter. Failing groups cannot promote evidence; strictly prior
immutable evidence, atomic cutoff, deterministic ordering, and complete-prefix invariance remain
unchanged.

## 6. Conservation, Roll, and Identity Evidence

The manifest still proves:

- `parsed_row_count = eligible_row_count + excluded_row_count`;
- `raw_volume = eligible_volume + excluded_volume`;
- development/OOS counts and volumes reconcile exactly;
- exclusion counts reconcile to the exact excluded-row count;
- completed-session volume evidence remains integer and contract/trade-date exact.

Gap volume may confirm a roll, but the first promoted row after the embargo remains at the exact
later eligible trade date. The source/coverage identity version stays V2. The builder algorithm is
V5, so deterministic SEGMENT and DATASET identities intentionally changed and their exact fixtures
were updated. No source/coverage identity payload or canonical ordering changed.

## 7. Preserved Public Contracts

No public function signature, keyword-only parameter/default, frozen public dataclass field,
identity payload field name, enum value, constant export, result/reason shape, or status precedence
changed. Public precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The correction does not alter complete parsing, source-domain boundaries, predecessor proof,
initial dominance, adjacent-contract comparison, consecutive roll confirmation, delivery-month
ordering, no-right-censor policy, calendar identity validation, or final-OOS isolation.

## 8. Exact 48-Case Reconciliation

The test module retains exactly one sequential marker for logical Cases `1` through `48`, with no
missing or duplicate logical case number. Parameterization and added public-builder coverage now
produce `253` focused executions. The new Case 38 assertions distinguish coverage from eligibility,
prove exact exclusion conservation for both embargoes, and prove that completed-session gap volume
can confirm a later eligible roll without promoting any gap row. Version and exhaustive public-
surface assertions remain within Cases 40 and 46.

## 9. Artifact and Scope Evidence

| Artifact | SHA-256 | Bytes | Lines |
| --- | --- | ---: | ---: |
| `analysis/gc_dataset_builder.py` | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` | 109258 | 2820 |
| `tests/test_gc_dataset_builder.py` | `4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971` | 106345 | 2934 |

These hashes bind the final tested source and test bytes before staging. The checkpoint's own hash
is reported by the final independent scope/hash audit because embedding it here would be recursive.

Before this checkpoint was created, `HEAD` and local `origin/main` both resolved to
`cff665257832004fe4467308f239e0f0bf51f50d`. The following user-owned untracked files pre-existed,
remain out of scope, and retain their prior hashes:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`
  (`CA2C1CE2178450F4E9D20A1BEC9883805089520F93B933A374667B841B70BFD0`);
- `docs/gc_futures_real_data_input_binding_change_proposal.md`
  (`FC068B5B089CC8B5D1862C1C26454371E8C9ADFFC6120FA08541D47B6926FF13`);
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`
  (`C073117D83945CB362D8CC9C9DFFA34EE1898D533A81EB3D06DA355FB4D7D87D`).

## 10. Promotion, Rollback, and STOP Conditions

Promotion requires an independent exact-scope/hash/diff audit, exact-path staging, full cached-
content audit, and a local commit. Push requires a later explicit export-risk authorization. Any
private two-run transaction requires its own clean pushed checkpoint and separate explicit run
authority.

Rollback before staging is deletion of only this checkpoint plus reversal of only the two bounded
working-tree edits. After commit, rollback requires an explicit later revert. Private inputs and
user-owned files are never rollback targets.

STOP on any focused/full test failure, conservation mismatch, public API drift, unexpected tracked
path, dependency/hash drift, missing or malformed calendar evidence, identity instability,
requested private-data inspection, final-OOS access, training, integration, execution, signal,
order, risk, PnL, or trading request. This checkpoint grants none of those authorities.
