# GC Futures Canonical Dataset Builder Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `GC-FUTURES-DATASET-BUILDER-CHECKPOINT-2026-08-03`.
- Formal decision commit:
  `bf28046423d9fc5c6a7b5565df1c21f027879758`.
- Formal decision record SHA-256:
  `6C6E323D4327377D007219F3E5A5877DD076BB947FFA002BC30184684277A466`.
- V2 compatibility proposal commit:
  `a2884c67e2e82a46f3bc52e1b0ce2fbc3b80a238`.
- V2 compatibility proposal SHA-256:
  `950FE6EA853099ACAB3CA46A80CD4D17CFA5F0800453ED6080636B3198522077`.
- Builder version: `GC-DATASET-BUILDER-V2`.
- Task classification: bounded offline canonical-dataset implementation.
- Real private-data build status: `NOT_PERFORMED`.
- Integration status: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three existing paths are in scope for the bounded V2 correction:

- `analysis/gc_dataset_builder.py`
- `tests/test_gc_dataset_builder.py`
- `docs/gc_futures_dataset_checkpoint.md`

No external fixture, calendar, holiday, timezone, market-data, manifest, or
generated dataset file was created. No importer, footprint model, backtest,
feature, label, model, strategy, risk, execution, configuration, dependency,
package export, runtime, or integration file changed.

The pre-existing untracked
`docs/smc_v2_diagnostic_context_integration_change_proposal.md` remains outside
this task and was not read, edited, staged, or otherwise promoted by this work.

## 3. Test-First and Correction Evidence

The committed V1 suite remained the baseline. V2 tests were added before each
bounded source correction while preserving one sequential marker for each of
the exact `48` logical cases.

The first V2 RED result was an import failure for the new immutable coverage
model. After the coverage contract and identity surface were introduced, the
focused baseline reached `144 passed`. The expanded V2 audit then added direct
public coverage, predecessor, adjacent-roll, manifest, identity, atomic-cutoff,
and prefix tests.

One additional test-first defect was found: a Sierra-style row with zero trades,
zero total volume, zero bid volume, and zero ask volume was accepted as an
observed bar. The focused RED result was `1 failed, 30 passed`; both the byte
parser and internal dataclass validation now reject it as a synthetic no-data
row through only `TypeError` or `ValueError`.

The final V2 suite also proves that absent covered intervals add zero only to
completed-session volume, never emit bars, split observed segments, and remain
separately counted in the manifest. Missing coverage stays `UNKNOWN`; malformed,
forked, out-of-order, overlapping, or source-mismatched coverage is `INVALID`.

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`
- `218 passed in 1.06s`
- exact logical cases: `48`
- additional parameterized executions: `170`

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`
- `2079 passed in 13.54s`
- committed V1 checkpoint baseline: `2004 passed`
- net new V2 collected executions: `75`

## 4. Exact Public Surface

The module exports exactly these `21` names:

- `GC_DATASET_BUILDER_VERSION`
- `GC_DATASET_INSTRUMENT`
- `GC_DATASET_TIMEFRAME`
- `GC_DATASET_SOURCE_TIMEZONE`
- `GC_DATASET_EXCHANGE_TIMEZONE`
- `GC_DATASET_TICK_SIZE`
- `GC_ROLL_CONFIRMATION_SESSIONS`
- `GC_DELIVERY_MONTH_CODES`
- `GCDatasetBuildStatus`
- `GCSourceRole`
- `GCSegmentPartition`
- `GCSierraChartBarRow`
- `GCSierraChartExport`
- `GCSierraChartCoverageEvidence`
- `GCCanonicalContractSegment`
- `GCDatasetManifest`
- `GCDatasetBuildConfig`
- `GCDatasetBuildResult`
- `parse_sierra_chart_gc_export`
- `make_gc_dataset_id`
- `build_gc_futures_dataset`

All three functions are exact keyword-only APIs. Every public dataclass is
frozen and has the exact locked field order, annotations, and result defaults.
No feature, label, target, model, strategy, signal, order, risk, PnL, filesystem,
network, wall-clock, or runtime integration surface exists.

## 5. Immutable Sierra Export Boundary

`parse_sierra_chart_gc_export()` accepts exact caller-supplied bytes and immutable
provenance. It enforces:

- exact GC delivery tokens using only `G/J/M/Q/V/Z`;
- exact `Asia/Tokyo`, `5M`, explicit role, aware capture time, and basename-only
  source name;
- strict UTF-8 with optional leading BOM;
- exact ordered 13-column Sierra Chart export schema;
- naive chart-local bar-start parsing and database-backed conversion to aware UTC
  close time by adding exactly five minutes;
- strictly increasing local timestamps and source row numbers;
- finite Decimal OHLC on exact `0.1` ticks with canonical geometry;
- exact nonnegative integer trade and volume fields, with
  `volume == bid_volume + ask_volume`;
- exact rejection of zero-trade/zero-volume synthetic no-data rows;
- completed-bar capture boundary and exact raw-byte SHA-256 binding.

Boolean-as-integer, float, NaN, infinity, locale-formatted, fractional-tick,
malformed timestamp, off-order, duplicate, short, long, reordered, and extra
column evidence fails closed through only `TypeError` or `ValueError` at the
parser/builder boundary.

## 6. Calendar, Session, and Canonical Bar Semantics

The builder requires version-consistent caller-supplied
`KillZoneCalendarEntry` evidence. Runtime `tzdata`, `Asia/Tokyo`, and
`America/New_York` availability are bound before construction.

Canonical GC session truth is:

- standard open: prior calendar day America/New_York `18:00`, inclusive;
- standard close: trade date America/New_York `17:00`, exclusive;
- `EARLY_CLOSE`: exact standard open and a strictly earlier valid close;
- `SESSION_CLOSED`: absent boundaries and no positive-volume bar;
- maintenance/outside-session positive-volume evidence: `INVALID`;
- missing required calendar coverage: `UNKNOWN`.

Each source row maps to exactly one trade date and one immutable
`GCChronologicalBar`. Bar index is zero-based within its exact-contract segment;
timestamp is the aware UTC close; OHLC and volume reconcile exactly to the
source row. No missing bar is filled or synthesized.

Every source requires separately supplied immutable
`GCSierraChartCoverageEvidence`. Its canonical identity binds the exact SOURCE
identity, start-inclusive/end-exclusive aware UTC range, acquisition completion,
capture boundary, and immutable acquisition-evidence SHA-256. Coverage cannot
enlarge capture, silently sort, overlap, fork, or cover a row outside its range.
An attested missing interval adds zero to completed-session volume but remains
an observed-stream gap. A coverage, roll, calendar, partition, or missing-slot
boundary ends a segment.

## 7. Roll and Partition Invariants

The implementation uses only the locked prospective adjacent-delivery
`PRIOR_SESSION_VOLUME_DOMINANCE_3` policy:

1. caller supplies the initial contract and trade date;
2. the initial contract requires its exact predecessor and strict dominance on
   the three immediately preceding eligible completed sessions;
3. only the exact next delivery contract is compared with the active contract;
4. only exact coverage-attested completed comparable session volumes participate;
5. the adjacent contract must dominate for three consecutive eligible calendar
   sessions;
6. a closed session neither counts nor breaks confirmation;
7. non-dominance resets confirmation;
8. the roll becomes effective only at the next eligible session;
9. roll order is monotonic, never reverses, and cannot skip a delivery.

Missing predecessor, active/adjacent coverage, comparable completed volume, or
effective-session evidence is `UNKNOWN`. Farther-contract absence or larger
volume is irrelevant until it becomes the exact adjacent successor. There is no
greatest-volume candidate set, filename/hash chronology, same-session/future-
price decision, back-adjustment, ratio-adjustment, synthetic spread, or cross-
contract OHLC decision.

Development and OOS roles are immutable. A development segment cannot consume
an OOS-only source and an OOS segment cannot consume development-only evidence.
Overlapping identical rows reconcile once; conflicting overlap is `INVALID`.

## 8. Deterministic Identities and Manifest Conservation

`make_gc_dataset_id()` implements exhaustive kind-specific schemas:

- `SOURCE` binds source basename, raw SHA-256, contract, role, capture moment,
  source timezone, and timeframe;
- `COVERAGE` recomputes SOURCE and binds its exact range, acquisition completion,
  and acquisition-evidence SHA-256;
- `SEGMENT` binds complete config, contract, partition, date range, ordered unique
  source IDs, canonical bar digest, and exact preceding missing-bar count;
- `DATASET` binds complete config, ordered unique source, coverage, and segment
  IDs, calendar and coverage digests, complete manifest evidence digest, and
  ordered roll dates.

Unknown kinds, absent required fields, supplied forbidden fields, malformed or
duplicate hashes, invalid dates, config drift, and nested malformed values raise
only `TypeError` or `ValueError` from the identity builder.

The immutable manifest reconciles exactly:

- parsed = eligible + excluded row count;
- eligible = development + OOS bar count;
- raw = eligible + excluded volume;
- completed-session volumes, exclusion reasons, missing bars, roll dates,
  ordered source/coverage/segment IDs, and coverage digest;
- attested-no-trade count is an exact subset of missing slots;
- every manifest field except `dataset_id` through `evidence_digest`.

Invalid or unknown evidence produces no partial manifest or dataset identity.

## 9. Atomicity, Status, and Prefix Invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

`AMBIGUOUS` remains in the vocabulary but has no reachable V2 branch because
exact adjacent selection is total and forked evidence is invalid.

Processing is atomic by complete canonical trade-date group. A determinably
failing group and every later group promote no bars, segments, roll, manifest,
or dataset identity. Strictly prior complete segments remain byte-for-byte
unchanged. If the malformed effective moment is unknowable, no trustworthy
prefix is claimed.

A valid complete prefix with no pending roll, partial session, coverage, or
partition boundary is invariant under strictly later complete source/calendar/
coverage append. Same-effective append, historical insertion, acquisition
repair, source replacement, calendar repair, role/config/timezone mutation,
initial/OOS-boundary change, and added predecessor/adjacent evidence are
explicitly not prefix extensions.

## 10. Exact 48-Case Reconciliation

The test file contains one and only one sequential marker for every logical
Case `1` through `48`. Parameterization expands them to `218` collected tests.
The matrix covers:

- Cases 1-6: missing/malformed counterpart precedence, empty scope, V2 constants,
  preserved parser rules, synthetic-no-data rejection, and no inferred bars;
- Cases 7-16: frozen coverage contract, SOURCE recomputation, UTC range and
  completion rules, acquisition hash, causal ordering, overlap/outside-range
  rejection, sparse-attested versus unattested behavior, and conflicting
  evidence precedence;
- Cases 17-24: completed volume, early-close/closed/maintenance/calendar/tzdata
  reconciliation, exact predecessor proof, missing historical boundary, and no
  convenient later-start inference;
- Cases 25-34: exact adjacent-only comparison, farther-contract irrelevance,
  one/two/three-session confirmation, closed-date handling, reset, prospective
  effective roll, no skip, no reverse, and hash-order independence;
- Cases 35-40: all segment boundaries, exact missing count, no cross-boundary
  state, role overlap and quarantine isolation, and exhaustive V2 manifest
  conservation;
- Cases 41-45: exhaustive SOURCE/COVERAGE/SEGMENT/DATASET identity schemas,
  V1/V2 separation, required/forbidden fields, recomputation, normalization,
  and payload sensitivity;
- Cases 46-48: exact keyword-only API/defaults, frozen public models, enums,
  constants, 21 exports, chronological malformed export/coverage cutoff,
  immutable prior evidence, prefix/repair rules, deterministic repeatability,
  dependency/import allowlist, and no I/O surface.

## 11. Scope and Dependency Audit

The production module directly imports only deterministic Python standard-library
utilities, `core.gc_chronological_backtest.GCChronologicalBar`, and committed
Kill-zone calendar types. It does not import pandas, NumPy, requests, sklearn,
legacy footprint, Sierra importer, SMC analyzers, model, broker, strategy,
configuration, storage, exporter, or integration code.

The implementation performs no file read/write, directory traversal, subprocess,
socket, HTTP, database, current-time, random, training, prediction, execution, or
trace-wiring operation. All test fixtures are inline synthetic values.

## 12. Real-Data Stop State

This implementation does not convert the current private Sierra intake into an
accepted dataset. Real-data construction remains stopped because no accepted,
immutable acquisition-coverage artifact or authoritative versioned historical
GC calendar artifact has been supplied. The initial adjacent delivery boundary
also remains unproved, including the earlier missing `GCJ25-COMEX` and
`GCM25-COMEX` coverage. The screenshots and exported filenames are diagnostic
intake evidence only and are not promoted as canonical coverage proof.

No model training, feature extraction, label construction, OOS opening, strategy
selection, backtest, validation, paper trading, or live action is authorized by
this checkpoint.

## 13. Artifact Evidence

- `analysis/gc_dataset_builder.py`
  - SHA-256:
    `9A3519DA97C0AA526EC4A5A8C867B5BF14AE514BA156F6A11ADDD410B66C1858`
  - bytes: `94663`
  - physical lines: `2406`
- `tests/test_gc_dataset_builder.py`
  - SHA-256:
    `DFCE06D6C9B8EECD10504F35D092D6A0652434D7A995C846E8A797F08919F9C3`
  - bytes: `71913`
  - physical lines: `1944`
- `docs/gc_futures_dataset_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes: `16080`
  - physical lines: `353`

All three artifacts must be UTF-8 without BOM, use LF line endings, contain no
tabs or trailing whitespace, and pass exact-scope diff checking before audit.

## 14. Promotion, Rollback, Stop, and Freeze State

This checkpoint does not authorize staging, commit, push, integration, private
data processing, feature/label work, training, OOS inspection, strategy changes,
paper trading, or live progression. Promotion requires a fresh independent
exact-scope code/test/checkpoint audit and explicit staging authorization.

Before commit, rollback is deletion of exactly these three untracked task files
and requires explicit authorization. After commit, rollback must use a bounded
revert rather than history rewriting.

Stop immediately on dependency drift, scope expansion, calendar/tzdata
uncertainty, source provenance failure, raw/canonical conservation failure,
unproved initial or intermediate contract coverage, fabricated bar need,
roll-policy ambiguity, development/OOS contamination, public API or identity
drift, uncontained exception, nondeterminism, exact 48-case mismatch,
focused/full regression failure, formatting/hash mismatch, or any requested
integration outside a separately approved freeze-lift decision.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`
- `EXACT_CHANGED_PATHS=3`
- `LOGICAL_CASES=48`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_COLLECTED=218`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=2079`
- `PRIVATE_DATA_BUILD_PERFORMED=False`
- `EXTERNAL_FIXTURE_CREATED=False`
- `EXTERNAL_CALENDAR_CREATED=False`
- `IMPORTER_CHANGED=False`
- `BACKTEST_CHANGED=False`
- `REQUIREMENTS_CHANGED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_PERFORMED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`
