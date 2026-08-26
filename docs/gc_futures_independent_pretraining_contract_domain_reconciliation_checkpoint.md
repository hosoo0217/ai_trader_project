# GC Futures Independent Pretraining Contract-Domain Reconciliation Checkpoint

## 1. Outcome

The bounded contract-domain reconciliation is **PASS** at local verification. The corpus builder now
compares immutable source-registry contracts such as `GCG26` with canonical upstream feature-row
contracts such as `GCG26-COMEX` through an exact private comparison adapter. Raw evidence, public
outputs, identity preimages, and public contracts remain unchanged.

No private run, private-data mutation, training, final-OOS payload access, feature/label build,
integration, stage, push, remote mutation, or trading action occurred during implementation and
verification.

## 2. Exact Scope

The bounded exception covers exactly:

- `analysis/gc_pretraining_corpus.py`;
- `tests/test_gc_pretraining_corpus.py`;
- `docs/gc_futures_independent_pretraining_contract_domain_reconciliation_checkpoint.md`.

Three unrelated pre-existing untracked proposal documents remained outside the task and were not
modified. No package export, dependency module, fixture, private-data root, calendar artifact,
requirement, configuration, runtime, execution, storage, or integration path was changed.

## 3. Locked Reconciliation

- Source-domain syntax is exact and case-sensitive: `^GC([GJMQVZ])(\d{2})$`.
- Upstream-domain syntax is exact and case-sensitive: `^GC([GJMQVZ])(\d{2})-COMEX$`.
- A valid source comparison key is formed only by appending the literal `-COMEX`.
- Upstream evidence is validated and retained unchanged.
- Whitespace, case folding, aliases, continuous symbols, composites, cross-month mapping, arbitrary
  suffixes, boolean values, non-strings, and year-width variations fail closed.
- The adapter is private and applies only at the source-to-row coverage boundary. It does not rewrite
  source records, upstream rows, labels, emitted records, manifests, lineage, or identity material.
- Nonparticipating reference metadata is not subjected to a new global contract restriction.
- Source date coverage, role eligibility, contamination, independence, partition, sealed-OOS, and
  deterministic ordering rules remain enforced.
- Malformed first-group evidence promotes nothing. A determinably later malformed group returns
  `INVALID` while preserving only strictly prior immutable records, partitions, and manifest evidence.

## 4. Public Compatibility Evidence

- Version remains `GC-PRETRAINING-CORPUS-V1`.
- `__all__` remains the exact existing 15-name export tuple.
- All existing public frozen dataclass contracts and identity schemas remain unchanged.
- `build_gc_pretraining_corpus` remains a seven-parameter, required, keyword-only API:
  `dataset_config`, `dataset_calendar_entries`, `dataset_result`, `candidate_result`,
  `feature_label_result`, `source_registry`, and `partition_plan`.
- The fail-closed public reason remains `INVALID_PRETRAINING_CORPUS_EVIDENCE`.
- Result authority remains corpus-diagnostic only; no training, OOS evaluation, integration,
  execution, or trading authority was added.

## 5. Test-First Correction Evidence

Public-builder tests were added first. The initial RED run produced `4 failed, 63 passed in 0.80s`:
canonical `GCG26`/`GCG26-COMEX` evidence was rejected by raw-string comparison, and unsuffixed
upstream evidence was not rejected at the intended boundary. The minimal private adapter correction
then passed the completed corpus matrix.

The test module retains exactly 48 sequential logical cases. Parameterization expands the module to
66 collected tests. Coverage includes exact syntax acceptance/rejection, month/year discrimination,
source and upstream raw-evidence preservation, identity stability, source-registry ordering/forks,
date coverage, malformed-counterpart precedence, sealed final OOS, contamination/independence,
atomic no-promotion, immutable prior evidence, prefix invariance, nested exception containment,
public API/exports/version stability, and forbidden I/O/training/integration authority.

Corpus-only command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 0.60s
```

Focused dependency command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py tests/test_gc_feature_label_builder.py tests/test_gc_pretraining_corpus.py
375 passed in 2.71s
```

Accepted full repository command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2527 passed in 36.88s
```

Both Python artifacts passed `py_compile`. `git diff --check` passed. Repository-root pytest was not
used because the governing proposal records ACL-protected private roots and locks `tests/` as the
accepted full regression target.

## 6. Artifact Evidence

| Artifact | SHA-256 | Bytes | Lines |
|---|---:|---:|---:|
| `analysis/gc_pretraining_corpus.py` | `F1D2454BD62C339CC6ED2BAAC1BE3BFFA3ED1E8D8A150D77BEE29F0A52F48400` | 55,398 | 1,115 |
| `tests/test_gc_pretraining_corpus.py` | `122A4BEC229C708942A9374688390B43616ACCC4DA534C2510322AD4AA5BF046` | 34,203 | 820 |

Governing proposal SHA-256:
`2F55CA62E482DC6EF44D85B512B7DCC31EB0E5464E216FCC630CC058FF1EFF27`.

Immutable focused dependency SHA-256 values remain:

- `analysis/gc_dataset_builder.py`: `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED`;
- `tests/test_gc_dataset_builder.py`: `4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971`;
- `analysis/gc_feature_label_builder.py`: `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`;
- `tests/test_gc_feature_label_builder.py`: `EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B`.

## 7. Promotion, Rollback, and STOP Boundary

Local promotion requires exact three-path staging, full cached-content inspection, cached
`diff --check`, staged SHA-256 reconciliation, and a local commit. Rollback is limited to these exact
three paths; broad reset, checkout, clean, or deletion is forbidden.

After the local commit, STOP before any push, private corpus run, private-data mutation,
feature/label build, training, final-OOS payload access, model evaluation, integration, execution, or
trading. Any hash/scope mismatch, fourth path, regression failure, public contract or identity
change, permissive normalization, private evidence access, or inability to prove deterministic
lineage is a STOP condition.
