# GC Futures Prospective Acquisition Manifest Validator Checkpoint

## 1. Outcome

The bounded public prospective-acquisition metadata validator implementation is
`PASS` at local verification. It validates only caller-supplied immutable
metadata for the locked raw-acquisition purpose. It does not acquire data,
inspect raw market payloads, build a dataset/corpus, construct features or
labels, train, access final OOS, integrate runtime behavior, or trade.

## 2. Governing decision

- Decision commit: `076d134785695b3b36f88910dbcdd5ea77866d5d`.
- Decision SHA-256:
  `80915CD80E4D9F6A6850FE728807BCA12C0A2BFAC4D8C3018C223EF9FAF95082`.
- Validator version:
  `GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1`.
- Program ID: `GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1`.
- Purpose: `PROSPECTIVE_RAW_ACQUISITION_ONLY`.
- Implementation authority: exact public schema validation only.

The decision commit was published and verified at `origin/main` before this
implementation began.

## 3. Exact scope

Only these three reserved paths changed:

- `analysis/gc_prospective_acquisition_manifest.py`;
- `tests/test_gc_prospective_acquisition_manifest.py`; and
- `docs/gc_futures_prospective_independent_development_cohort_acquisition_manifest_checkpoint.md`.

`analysis/__init__.py`, dependencies, fixtures, configuration, private
artifacts, acquisition roots, provider state, datasets, models, runtime, and
integration paths were unchanged. The three unrelated pre-existing untracked
drafts remained untouched.

## 4. Pure validation boundary

The new module uses only Python standard-library value types and the existing
`SMCV2PrimitiveStatus`. Its public validator is required-keyword-only and
accepts seven immutable metadata objects or tuples. It has no path, bytes,
file, environment, URL, session, credential, dataframe, chart, model, or
arbitrary mapping parameter.

The module performs no filesystem, network, subprocess, current-clock,
timezone-discovery, randomness, logging, cache, serialization, model, training,
OOS, integration, or trading operation. Identity generation is deterministic
canonical JSON plus namespaced lowercase SHA-256 over public metadata values.

## 5. Locked validation semantics

- Cohort trade dates remain exact `[2026-09-01, 2027-03-01)`.
- Capture remains exact
  `[2027-03-02T00:00:00Z, 2027-03-09T00:00:00Z)`.
- Provider/settings remain Sierra historical intraday metadata, `GC`, `COMEX`,
  `5M`, `1 Tick`, `220`, `Asia/Tokyo`, and `America/New_York`.
- Contract syntax is exact `GC([GJMQVZ])(\d{2})-COMEX` with canonical
  year/month delivery order.
- Required predecessor, candidate, and successor roles fail closed when absent.
- Every admitted source binds exact roster, provider-log, and authoritative
  official-calendar metadata.
- Clarification-only or gapped calendar coverage remains `UNKNOWN`.
- Conflicting valid calendar identity remains `AMBIGUOUS`.
- Prior outcome contact overlapping the cohort remains `INVALID`.
- Manifest counts, member order, config identity, artifact-set identity, and
  manifest identity are recomputed.
- Both access counts are zero and all seven authority flags remain false.

Terminal precedence is exact `INVALID > AMBIGUOUS > UNKNOWN > VALID`. A manifest
is returned only with `VALID`, whose sole reason is
`VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY`.

## 6. Test-first evidence

The exact 48-case synthetic test module was created before the source module.
The initial focused collection failed as expected with:

```text
ModuleNotFoundError: No module named 'analysis.gc_prospective_acquisition_manifest'
1 error during collection
```

After the first implementation, the focused run returned:

```text
46 passed, 2 failed
```

One failure identified missing `INVALID_ROSTER_EVIDENCE` classification when an
admitted source occupied an `EXCLUDED` roster record. The source validator was
tightened without relaxing any other boundary. The second failure was the
intentional exact-scope assertion for this checkpoint before the checkpoint
existed.

## 7. Exact 48-case matrix

The test module contains exactly 48 sequential functions named
`test_case_01` through `test_case_48`. It covers constants and boundaries;
frozen records; config, roster, source, provider, calendar, contamination, and
manifest validation; deterministic identities; count/order conservation;
invalid/ambiguous/unknown precedence; semantic input reordering; no-I/O and
privacy boundaries; exact exports; and zero research/training/OOS/integration/
trading authority.

All fixtures are synthetic public metadata. They contain no private filename
and hash pair, account data, provider message body, raw row, price, volume,
candidate, label, outcome, PnL, model output, or trading signal.

## 8. Verification evidence

Focused validator command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_prospective_acquisition_manifest.py
48 passed in 0.67s
```

Focused validator plus accepted pretraining-corpus dependency command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py tests/test_gc_prospective_acquisition_manifest.py
114 passed in 0.76s
```

Accepted full public regression command:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2722 passed in 39.65s
```

Both Python files passed `py_compile`. `git diff --check` passed. The exact
logical-case count is `48`, and focused collection is exactly `48` executions.

| Artifact | SHA-256 | Bytes | Physical lines |
|---|---:|---:|---:|
| `analysis/gc_prospective_acquisition_manifest.py` | `5714A1FCCCB4516C5D729DAE4C52AAED8279A999466FDA7043547DB288FB4596` | 42,123 | 848 |
| `tests/test_gc_prospective_acquisition_manifest.py` | `072DFCFB479A8803BA68BD2D404B1A4C15B4BE82AE95B1231E07BC2A20BC281A` | 37,779 | 731 |

Repository scope inspection found only the exact three authorized new paths
plus the same three unrelated pre-existing untracked drafts. No private root,
provider, final-OOS payload, dataset/corpus, feature/label, training,
integration, or trading resource was contacted.

## 9. Promotion and STOP boundary

Promotion requires exact three-path staging, cached-content inspection, cached
`git diff --check`, artifact reconciliation, and one local commit. No broad
pathspec is authorized.

After that local commit, work stops. This checkpoint grants no private
acquisition, provider operation, dataset/corpus build, candidate/feature/label
build, training, final-OOS access, model evaluation, integration, paper/live
trading, or GitHub push authority.
