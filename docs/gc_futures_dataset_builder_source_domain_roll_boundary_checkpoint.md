# GC Futures Dataset Builder Source-Domain Roll-Boundary Checkpoint

## 1. Checkpoint Identity

- Date: `2026-08-25`.
- Governing proposal commit:
  `f079a012df2a697904a353e2e015e2b576df93b7`.
- Governing proposal SHA-256:
  `C88C3D0A04A9160FD81EC01E8FE6F36595E90307A45000DFE843FB68D191A7DB`.
- Builder version: `GC-DATASET-BUILDER-V4-SOURCE-DOMAIN`.
- Implementation status: `LOCAL_IMPLEMENTATION_COMPLETE_NOT_STAGED`.
- Private rerun, corpus build, feature/label build, training, final-OOS access, integration,
  commit, and push status: `NOT_PERFORMED`.
- Global freeze outside the exact three-path task: `ACTIVE`.

## 2. Exact Authorized Scope

Only these paths changed:

- `analysis/gc_dataset_builder.py`
- `tests/test_gc_dataset_builder.py`
- `docs/gc_futures_dataset_builder_source_domain_roll_boundary_checkpoint.md`

No private source, normalized calendar, fixture, package export, downstream builder, detector,
strategy, engine, configuration, OOS artifact, integration file, or other documentation changed.
The three pre-existing user-owned untracked proposals remained untouched.

## 3. Test-First Evidence

The source correction began only after public-builder tests reproduced the defect. The initial RED
run was:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
4 failed, 246 passed in 1.46s
```

The failures proved the missing empty-domain rejection, before/after-domain exclusions, strict
boundary-straddle rejection, and preservation of in-domain missing-calendar semantics. Source
changes then implemented only the locked behavior. Stale deterministic version/identity fixtures
and a synthetic closed-session fixture were reconciled to the new algorithm and finite domain.

Final focused evidence:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
250 passed in 1.17s
```

Final full-regression evidence:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2524 passed in 24.47s
```

## 4. Exact Source-Domain Semantics

The builder now derives one immutable outer domain only from validated trading intervals:

- start is the minimum inclusive interval start;
- end is the maximum exclusive interval end;
- session-closed rows contribute no endpoint;
- a nonempty source with no derivable interval is `INVALID` with
  `CALENDAR_OUTER_DOMAIN_EMPTY`;
- a row closing at or before the start is conserved as `BEFORE_CALENDAR_DOMAIN`;
- a row starting at or after the end is conserved as `AFTER_CALENDAR_DOMAIN`;
- a row strictly straddling either endpoint is `INVALID` with
  `CALENDAR_DOMAIN_BOUNDARY_STRADDLE`;
- every other row continues through the existing exact calendar/session reconciliation.

In-domain missing coverage remains `UNKNOWN` with `CALENDAR_COVERAGE_MISSING`. Maintenance,
session-closed, malformed, overlapping, version-conflicting, or otherwise invalid evidence is not
converted into an outer-domain exclusion.

## 5. Conservation and Identity Evidence

Complete raw parsing remains mandatory. The manifest still proves:

- `parsed_row_count = eligible_row_count + excluded_row_count`;
- `raw_volume = eligible_volume + excluded_volume`;
- promoted development/OOS counts and volumes reconcile exactly;
- exclusion counts reconcile to the exact excluded-row count.

The internal evidence digest now additionally binds the exact calendar-domain endpoints and an
ordered exclusion ledger containing source ID, source row number, contract, start/close timestamps,
integer volume, and reason. Duplicate reconciliations and outer-domain exclusions therefore remain
source-row-sensitive identity evidence rather than silent deletion. The dataset algorithm/version
increment propagates through the existing `evidence_digest` and deterministic DATASET identity.

## 6. Preserved Roll and Public Contracts

The correction does not alter the canonical predecessor proof, exact three-session initial
dominance requirement, adjacent-contract comparison, consecutive roll confirmation, monotonic
delivery order, coverage rules, partition isolation, or no-right-censor policy.

No public function signature, keyword-only parameter/default, frozen public dataclass field,
identity payload field name, enum value, constant export, or result precedence changed. Public
precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Admissible-start selection, registry expansion, and terminal-end shortening remain later private
transaction preflight responsibilities. This implementation does not add a hidden bootstrap,
infer missing contracts, filter source files externally, or suppress roll diagnostics.

## 7. Exact 48-Case Reconciliation

The test module retains exactly one sequential marker for logical Cases `1` through `48` and no
missing or duplicate logical case number. Parameterization and additional public-builder tests
produce `250` focused executions. The matrix continues covering strict parsing, calendar/session
validation, initial/adjacent roll evidence, deterministic identities, public API/frozen models,
atomic cutoff, prefix invariance, and forbidden integration surface. The source-domain additions
are contained within the existing logical cases and do not change the exact logical-case count.

## 8. Artifact Evidence

| Artifact | SHA-256 | Bytes | Lines |
| --- | --- | ---: | ---: |
| `analysis/gc_dataset_builder.py` | `5B41BEAC0A2867DC398C7D1488A84E5191D2BFEBC499F7A79DC0B805800128DE` | 108583 | 2802 |
| `tests/test_gc_dataset_builder.py` | `3FC36A80F4F6A7E3A48C4D6217A339235C5B6E4E957A80A65D67C6CABC3041CD` | 102856 | 2825 |

These hashes bind the final tested source and test bytes before staging. The checkpoint's own hash
is reported by the final independent scope/hash audit because embedding it here would be recursive.

## 9. Scope and Worktree Evidence

Before this checkpoint was created, `HEAD` and local `origin/main` both resolved to
`f079a012df2a697904a353e2e015e2b576df93b7`. The only tracked modifications were the source and test
paths above. This checkpoint is the only newly created task file. No task artifact was staged.

The following user-owned untracked files pre-existed and remain out of scope and untouched:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`
- `docs/gc_futures_real_data_input_binding_change_proposal.md`
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`

## 10. Promotion, Rollback, and STOP Conditions

Promotion requires an independent exact-scope/hash/diff audit, fresh cached-content audit after
explicit staging authority, a local commit under separate authority, and a later separately
authorized push. A corrected private transaction additionally requires a clean pushed checkpoint,
exact immutable private inputs, and separate explicit run authority.

Rollback before staging is deletion of only this checkpoint plus reversal of only the two bounded
working-tree edits. After commit, rollback requires an explicit later revert. Private inputs and
user-owned files are never rollback targets.

STOP on any test failure, conservation mismatch, public API drift, unexpected tracked path,
dependency/hash drift, boundary-straddling private row, unresolved roll proof, need to inspect final
OOS payload, or request to weaken fail-closed semantics. This checkpoint grants no training,
integration, execution, signal, order, risk, PnL, or trading authority.
