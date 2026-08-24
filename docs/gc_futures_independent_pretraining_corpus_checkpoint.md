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

A post-push independent audit found that the sealed FINAL_OOS source hash constant did not match
the accepted private raw-intake manifest. A public-builder regression was added first: the actual
normalized manifest hash `15e2b3cb47e96988a1a623712e3347438e47b19d8d154d213aecc81c52a50111`
must pass independently determinable source validation, while the previously encoded nonexistent
`15e2f672457176749c4143baa4bb00c30d1ae913c82333cb8e8e8f79592ff46e`
must fail closed. The regression failed before the source correction and passed after the constant
was reconciled. No sealed payload was opened; the test and correction use manifest metadata only.

Focused command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 0.55s
```

Accepted repository regression command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2519 passed in 24.28s
```

A root-wide invocation was also attempted and stopped during collection on two ACL-protected
private evidence directories with Windows `PermissionError`. This is not reported as test evidence;
the decision record explicitly identifies `tests/` as the accepted suite when inaccessible private
directories prevent root-wide collection.

`py_compile` passed for both Python artifacts. `git diff --check` passed with no formatting errors.

## 5. Artifact Evidence

| Artifact | SHA-256 | Bytes | Lines |
|---|---:|---:|---:|
| `analysis/gc_pretraining_corpus.py` | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` | 53,683 | 1,069 |
| `tests/test_gc_pretraining_corpus.py` | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` | 14,339 | 342 |

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
