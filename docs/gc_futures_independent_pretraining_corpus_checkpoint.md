# GC Futures Independent Pretraining Corpus Implementation Checkpoint

## 1. Outcome

The bounded independent pretraining-corpus implementation is **PASS** at local verification.
It assembles and validates caller-supplied immutable upstream evidence only. It does not read
private data, build features or labels, access final OOS payloads, train a model, integrate with
runtime execution, or authorize trading.

## 2. Exact Scope

Only these implementation artifacts were created:

- `analysis/gc_pretraining_corpus.py`;
- `tests/test_gc_pretraining_corpus.py`;
- `docs/gc_futures_independent_pretraining_corpus_checkpoint.md`.

The three pre-existing untracked proposal documents remained outside this task and were not
modified. No package export, fixture, private-data, calendar, requirement, configuration,
integration, model, training, OOS, execution, storage, stage, push, or remote mutation occurred
during implementation verification.

## 3. Locked Contract Evidence

- Version: `GC-PRETRAINING-CORPUS-V1`.
- Fixed contract: `GC`, `5M`, tick size `0.1`, label horizon 12 bars, minimum embargo 12 bars.
- Exact partitions: TRAIN `[2024-11-04, 2025-06-02)`, VALIDATION
  `[2025-06-16, 2025-08-25)`, CALIBRATION `[2025-09-08, 2025-11-24)`, sealed
  FINAL_OOS metadata `[2026-07-06, 2026-08-01)`.
- Final status precedence: `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
- Exact public surface: six constants, two enums, six frozen dataclasses, and one required
  seven-argument keyword-only builder.
- Deterministic identities cover PARTITION_PLAN, RECORD, PARTITION, CORPUS, and MANIFEST.
- Result authority flags are fixed false; no training, OOS evaluation, integration, or trading
  authority is emitted.
- Caller-supplied dataset, candidate-evidence, feature/label, calendar, source-registry, plan,
  lineage, contamination, partition, and sealed-OOS metadata are reconciled fail closed.
- No filesystem, network, wall-clock, locale, randomness, mutable-global, trainer, predictor, or
  execution dependency is used by the implementation.

## 4. Test-First and Correction Evidence

The initial focused test intentionally failed with `ModuleNotFoundError` before the module existed.
The completed inline matrix contains exactly 48 sequential logical cases. Parameterization expands
it to 66 collected focused tests. Coverage locks missing-context validation, malformed-counterpart
precedence, empty-evidence NONE behavior, plan boundaries, immutable contracts, exact API/exports,
status containment, no-promotion behavior, repeatability, Decimal-context independence, and the
forbidden IO/training surface.

Focused command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 0.55s
```

Accepted repository regression command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2519 passed in 22.80s
```

A root-wide invocation was also attempted and stopped during collection on two ACL-protected
private evidence directories with Windows `PermissionError`. This is not reported as test evidence;
the decision record explicitly identifies `tests/` as the accepted suite when inaccessible private
directories prevent root-wide collection.

`py_compile` passed for both Python artifacts. `git diff --check` passed with no formatting errors.

## 5. Artifact Evidence

| Artifact | SHA-256 | Bytes | Lines |
|---|---:|---:|---:|
| `analysis/gc_pretraining_corpus.py` | `F7D11ADBD7BC4FFCC9574B338D95AB52301BA3C3BA730BCFD0DF1CAC217D9FE5` | 53,683 | 1,069 |
| `tests/test_gc_pretraining_corpus.py` | `7BC68E0F73544E1EB8F9DA13C56F5F94D426C066B8B7572FACA7E7CA36C65CEE` | 12,862 | 307 |

Decision dependency SHA-256:
`556EC81E093117DFB2F710D7A7B00DB731BEA299B65BE47ACA585D8FE9421303`.

Immutable upstream source hashes remain:

- dataset builder: `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`;
- candidate-evidence builder: `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F`;
- feature/label builder: `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153`.

## 6. Promotion and Stop Boundary

Local promotion requires exact three-file staging, cached-content audit, clean cached diff-check,
artifact-hash reconciliation, and a local commit. This checkpoint grants no push authority.

After local commit, stop before any push, private corpus run, feature/label build, training, final
OOS access, model evaluation, integration, execution, or trading. Any artifact/hash mismatch,
scope expansion, regression failure, private-evidence access, authority-field change, or inability
to prove deterministic lineage is a STOP condition.
