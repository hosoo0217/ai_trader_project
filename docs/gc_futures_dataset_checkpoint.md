# GC Futures Canonical Dataset Builder Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID: `GC-FUTURES-DATASET-BUILDER-CHECKPOINT-2026-08-03`.
- Formal decision commit:
  `bf28046423d9fc5c6a7b5565df1c21f027879758`.
- Formal decision record SHA-256:
  `6C6E323D4327377D007219F3E5A5877DD076BB947FFA002BC30184684277A466`.
- Builder version: `GC-DATASET-BUILDER-V1`.
- Task classification: bounded offline canonical-dataset implementation.
- Real private-data build status: `NOT_PERFORMED`.
- Integration status: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three new paths are in scope:

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

The exact `48` numbered logical cases and inline synthetic evidence were created
before the production module. The intended RED run produced:

- `ModuleNotFoundError: No module named 'analysis.gc_dataset_builder'`
- `1 error in 0.27s`

The first implementation pass exposed and corrected only bounded defects:

- Sierra's non-zero-padded `YYYY-M-D` raw date required component-based strict
  parsing instead of `datetime.fromisoformat`;
- completed-session volume triples required an explicit `(contract, date)` map;
- two test helpers incorrectly substituted a default for an explicit empty
  source name and reused byte-identical synthetic content across distinct
  contracts;
- the public dataclass field-count assertions were reconciled to the exact
  formal contracts.

The initial focused GREEN result was:

- `71 passed in 0.69s`

The initial full regression result was:

- `1932 passed in 11.20s`

An independent semantic and coverage audit then found one public fail-closed
gap. A later export with determinable row time but malformed export-level
required fields returned a generic invalid result without retaining the
strictly prior canonical segment. Case 47 tests were added first for malformed
row, source name, contract, and capture timestamp evidence. The RED result was
`3 failed, 1 passed`; the source now records a moment-bound `MALFORMED_EXPORT`,
preserves only strictly prior segments, emits no manifest, and leaks no
exception.

The audit also expanded existing Cases 43-47 without changing the logical case
count. Coverage now includes every required and forbidden identity field,
payload-axis sensitivity, exact function names/defaults, complete strictly-later
prefix invariance, and historical-repair ineligibility.

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`
- `143 passed in 0.83s`
- exact logical cases: `48`
- additional parameterized executions: `95`

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`
- `2004 passed in 13.31s`
- decision-checkpoint baseline: `1861 passed`
- net new collected executions: `143`

## 4. Exact Public Surface

The module exports exactly these `20` names:

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
source row. No missing bar is filled or synthesized. A roll, calendar,
partition, or missing-timestamp boundary ends a segment.

## 7. Roll and Partition Invariants

The implementation uses only the locked prospective
`PRIOR_SESSION_VOLUME_DOMINANCE_3` policy:

1. caller supplies the initial contract and trade date;
2. only exact completed comparable session volumes participate;
3. a later contract must dominate for three consecutive eligible calendar
   sessions;
4. a closed session neither counts nor breaks confirmation;
5. multiple third-day qualifiers use greatest volume, then nearer delivery;
6. the roll becomes effective only at the next eligible session;
7. roll order is monotonic and never reverses.

Missing initial/intermediate contract coverage, incomplete comparable volume,
or absent effective-session evidence is `UNKNOWN`. There is no filename-order,
same-session/future-price, back-adjustment, ratio-adjustment, synthetic spread,
or cross-contract OHLC decision.

Development and OOS roles are immutable. A development segment cannot consume
an OOS-only source and an OOS segment cannot consume development-only evidence.
Overlapping identical rows reconcile once; conflicting overlap is `INVALID`.

## 8. Deterministic Identities and Manifest Conservation

`make_gc_dataset_id()` implements exhaustive kind-specific schemas:

- `SOURCE` binds source basename, raw SHA-256, contract, role, capture moment,
  source timezone, and timeframe;
- `SEGMENT` binds complete config, contract, partition, date range, ordered unique
  source IDs, canonical bar digest, and exact preceding missing-bar count;
- `DATASET` binds complete config, ordered unique source and segment IDs, calendar
  digest, complete manifest evidence digest, and ordered roll dates.

Unknown kinds, absent required fields, supplied forbidden fields, malformed or
duplicate hashes, invalid dates, config drift, and nested malformed values raise
only `TypeError` or `ValueError` from the identity builder.

The immutable manifest reconciles exactly:

- parsed = eligible + excluded row count;
- eligible = development + OOS bar count;
- raw = eligible + excluded volume;
- completed-session volumes, exclusion reasons, missing bars, roll dates,
  ordered source IDs, and ordered segment IDs;
- every manifest field except `dataset_id` through `evidence_digest`.

Invalid or unknown evidence produces no partial manifest or dataset identity.

## 9. Atomicity, Status, and Prefix Invariance

Final precedence is exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

`AMBIGUOUS` remains in the vocabulary but has no reachable V1 branch because
valid roll candidates are totally ordered and forked evidence is invalid.

Processing is atomic by complete canonical trade-date group. A determinably
failing group and every later group promote no bars, segments, roll, manifest,
or dataset identity. Strictly prior complete segments remain byte-for-byte
unchanged. If the malformed effective moment is unknowable, no trustworthy
prefix is claimed.

A valid complete prefix with no pending roll, partial session, or partition
boundary is invariant under strictly later complete source/calendar append.
Same-effective append, historical insertion, source replacement, calendar
repair, role/config/timezone mutation, OOS-boundary change, and added missing
intermediate contract are explicitly not prefix extensions.

## 10. Exact 48-Case Reconciliation

The test file contains one and only one sequential marker for every logical
Case `1` through `48`. Parameterization expands them to `143` collected tests.
The matrix covers:

- Cases 1-18: missing/malformed context precedence, empty scope, contracts,
  timezone/config constants, exact parser, Decimal/integer validation, source
  hash/name/order/identity, and duplicate conflicts;
- Cases 19-27: DST conversion, standard/early/closed session semantics,
  trade-date mapping, completed volume, overlap reconciliation, and explicit
  missing-bar segmentation;
- Cases 28-41: initial and intermediate coverage, exact three-session roll,
  closed-date/reset/tie/effective-session behavior, skipped lineage, unadjusted
  bars, all segment boundaries, development/OOS isolation, and capture/OOS proof;
- Cases 42-46: manifest conservation, exhaustive SOURCE/SEGMENT/DATASET schemas,
  exact signatures/defaults, frozen models, enums, constants, and exports;
- Cases 47-48: chronological malformed cutoff, immutable prior evidence,
  complete-prefix invariance, historical-repair ineligibility, deterministic
  repeatability, dependency/import allowlist, and no I/O surface.

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
accepted dataset. Real-data construction remains stopped because the formal
intake audit has not supplied an accepted versioned historical GC calendar and
has not independently proved the initial adjacent delivery boundary, including
the earlier missing `GCJ25-COMEX` and `GCM25-COMEX` coverage.

No model training, feature extraction, label construction, OOS opening, strategy
selection, backtest, validation, paper trading, or live action is authorized by
this checkpoint.

## 13. Artifact Evidence

- `analysis/gc_dataset_builder.py`
  - SHA-256:
    `C7A30ADEC64F55FAA887AB121FD20EFFE0BA726C1D32525D664354640FCA2D80`
  - bytes: `68527`
  - physical lines: `1740`
- `tests/test_gc_dataset_builder.py`
  - SHA-256:
    `343B4CA4D6CC256840FB7331BC6D7EF56682482431F45844C071E6B495203A8D`
  - bytes: `41846`
  - physical lines: `1143`
- `docs/gc_futures_dataset_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded
  - bytes: `14537`
  - physical lines: `337`

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
- `FOCUSED_TESTS_COLLECTED=143`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=2004`
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
