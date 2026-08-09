# GC Futures Split-Session Calendar Bounded Implementation Checkpoint

## 1. Checkpoint Identity

- Checkpoint ID:
  `GC-FUTURES-SPLIT-SESSION-MANIFEST-COMPATIBILITY-CORRECTION-2026-08-09`.
- Original governing proposal:
  `docs/gc_futures_split_session_calendar_change_proposal.md`.
- Original governing proposal SHA-256:
  `8E1DC59F84C9699BD57C5397667AEC630C5182CF11D6CB667DFEB3CDBA73445D`.
- Identity-correction governing proposal:
  `docs/gc_futures_phase_a_pilot_v3_split_session_rebuild_change_proposal.md`.
- Identity-correction proposal SHA-256:
  `FEF0D8E96C37B261ACF2B252B59FE7F6ACD9B635E1C9A4656117509DCD73E0AD`.
- Governing proposal structure: exact `24` numbered sections and `48`
  sequential logical cases.
- Builder version: `GC-DATASET-BUILDER-V3-SPLIT-SESSION`.
- Task classification: bounded offline dataset-builder calendar correction.
- Private-data build status: `NOT_PERFORMED`.
- Training status: `NOT_STARTED`.
- Integration status: `NOT_STARTED`.
- Global code freeze outside the exact task: `ACTIVE`.

## 2. Exact Authorized Scope

Exactly these three paths are in scope:

- `analysis/gc_dataset_builder.py`
- `tests/test_gc_dataset_builder.py`
- `docs/gc_futures_split_session_calendar_checkpoint.md`

The governing proposal and all other existing tracked or untracked paths remain
outside this implementation scope. No external fixture, calendar, holiday,
timezone, market-data, manifest, generated dataset, model, or training artifact
was created.

## 3. Immutable Split-Session Input Contract

The implementation adds these frozen public value objects without mutating the
committed single-session calendar type:

- `GCDatasetSessionInterval(start_timestamp, end_timestamp)`;
- `GCSplitSessionCalendarEntry(calendar_version, trade_date, intervals,
  source_artifact_ids, source_artifact_sha256s)`.

Every interval endpoint is timezone-aware, normalized to UTC, and strictly
positive in duration. The interval tuple must be nonempty, strictly ordered,
nonoverlapping, and globally nonoverlapping with all other supplied calendar
entries. Source artifact ID and SHA-256 tuples must be nonempty, equal length,
strictly ordered, unique, and canonical; SHA-256 text is normalized to lowercase
before identity construction.

## 4. Calendar Compatibility and Type Boundary

`build_gc_futures_dataset()` accepts an immutable tuple whose members are either
the committed `KillZoneCalendarEntry` type or the new
`GCSplitSessionCalendarEntry` type. A mixed tuple is valid only when every member
is canonical and the combined chronology is deterministic.

The legacy single-session path retains its committed semantics. Split-session
calendar kind, ordered interval topology, and provenance are identity-bearing,
so an equivalent outer open/close span cannot collide with a split schedule.

## 5. Exact Interval Membership

A positive Sierra row belongs to a trade date only when its normalized bar-close
moment lies inside exactly one start-inclusive/end-exclusive calendar interval.
A positive row inside an official gap is `INVALID`. A zero-activity row inside
an official gap is excluded and cannot become a canonical bar, affect volume,
or bridge the gap.

Rows outside every supplied session remain subject to the existing fail-closed
unrequested-evidence boundary. No silent sorting, timestamp repair, inferred
interval, or fabricated bar is permitted.

## 6. Completed-Session and Acquisition Semantics

Split-session completion requires acquisition coverage strictly later than the
final interval close. Equality with the final close is not completion proof and
therefore remains `UNKNOWN`. The committed single-session compatibility rule is
unchanged.

For a completed split session, every required 5-minute slot across every active
interval must be covered. An incomplete split session cannot contribute
completed-session roll-confirmation volume. Official gaps contribute zero
volume and zero required slots; they never receive fabricated bars.

The manifest's `attested_no_trade_interval_count` preserves the committed V2
single-session acquisition evidence and extends it without reclassification:
it is the exact sum of acquisition-attested missing slots and represented
official gaps between ordered split-session intervals. Consequently, the
accepted single-session pilot retains `73`, while a complete two-interval
synthetic session with one represented official gap contributes exactly `1`.
Neither component fabricates a bar or changes `missing_bar_count`.

## 7. Conservation and Roll Semantics

Completed-session volume is the sum of covered canonical rows from all active
intervals for the trade date. Interval boundaries reset slot adjacency, so
official gaps cannot merge observed segments or create cross-gap state.

Adjacent-contract roll comparison remains prospective, chronological, and
deterministic. Only complete eligible sessions contribute comparable volume.
The existing confirmation count, no-skip, no-reverse, and immutable prior
segment rules remain unchanged.

## 8. Deterministic Identity Binding

The bounded correction preserves the accepted V2 identity-version payload for
`SOURCE` and `COVERAGE` only. Their exact six pilot vectors (three source and
three coverage identities for GCG26, GCJ26, and GCM26) are locked by public
`make_gc_dataset_id()` tests. `SEGMENT` and `DATASET` remain bound to
`GC-DATASET-BUILDER-V3-SPLIT-SESSION`; exact synthetic anchor tests prove that
their V3 identities did not drift during the correction. The private identity
version selector is not exported and does not alter the public builder version,
signature, dataclasses, or 23-name export surface.

The DATASET and manifest digest bind:

- calendar representation kind (`SINGLE_SESSION` or `SPLIT_SESSION`);
- normalized trade date and calendar status;
- every ordered normalized interval endpoint;
- every ordered source artifact ID;
- every normalized source artifact SHA-256;
- all previously committed export, coverage, segment, and config evidence.

Changing interval order, topology, provenance, hash, calendar kind, effective
moment, or source evidence changes the deterministic identity or fails closed.
Repeated equivalent inputs, including equivalent uppercase/lowercase SHA-256
text, produce the same canonical identity.

## 9. Fail-Closed and Atomic-Cutoff Evidence

Malformed type, naive timestamp, empty interval tuple, nonpositive duration,
out-of-order interval, overlap, global overlap, provenance length mismatch,
duplicate provenance, malformed hash, positive gap row, incomplete completed
session, or identity mismatch is contained without exception leakage from the
public analyzer.

Determinably later malformed evidence returns `INVALID` while preserving only
strictly prior immutable manifest/segment evidence. The failing effective group
and everything after it are not promoted. Evidence with no trustworthy effective
moment does not require preservation of an otherwise unverifiable prefix.

## 10. Exact Public Surface

The module exports exactly `23` names: the committed `21` V2 exports plus
`GCDatasetSessionInterval` and `GCSplitSessionCalendarEntry`. All public
dataclasses are frozen with exact tested field order and annotations. The three
public functions remain exact keyword-only APIs:

- `parse_sierra_chart_gc_export()`;
- `make_gc_dataset_id()`;
- `build_gc_futures_dataset()`.

No filesystem, network, wall-clock, model, training, prediction, signal, order,
risk, PnL, broker, execution, or trace-wiring authority was added.

## 11. Exact 48-Case Matrix Reconciliation

The focused test module retains exactly one named logical marker for every case
from `test_case_01` through `test_case_48`. Parameterization expands execution
coverage without changing the logical count.

Coverage includes:

- immutable split types, normalization, provenance, ordering, overlap, and
  compatibility boundaries;
- exact 2024/2025 authoritative split moments and official gaps;
- positive/zero gap-row behavior and exact interval membership;
- completion, required-slot coverage, conservation, and roll eligibility;
- V2 single-session acquisition-gap count preservation plus additive represented
  split-session official-gap evidence;
- calendar-kind and provenance identity sensitivity and normalized hash
  equivalence;
- accepted GCG26/GCJ26/GCM26 V2 SOURCE/COVERAGE vectors under the V3 builder,
  plus unchanged V3 SEGMENT/DATASET anchors;
- malformed chronology, atomic cutoff, prior-evidence preservation, complete
  prefix invariance, historical mutation ineligibility, exact API, frozen
  dataclasses, constants, version, and exports.

## 12. Test and Regression Evidence

Final focused evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py`
- result: `245 passed in 0.91s`;
- exact logical cases: `48`;
- pre-correction split-session checkpoint: `239 passed`;
- identity-correction executions added inside Cases 41 and 42: `6`.

Test-first defect evidence:

- before the source edit, the six accepted V2 SOURCE/COVERAGE vectors failed
  while both V3 SEGMENT/DATASET anchors passed: `6 failed, 2 passed in 1.01s`;
- after the source edit, the same targeted selection passed:
  `8 passed in 0.51s`.
- the later private V3 prepublication audit exposed manifest drift: accepted V2
  `attested_no_trade_interval_count=73` versus attempted V3 `0`; no V3 root was
  published;
- Cases 6, 25, and 40 were first changed to require preservation of their one
  acquisition-attested missing slot and failed before the source correction:
  `3 failed, 242 deselected in 0.75s`;
- after the additive compatibility correction, Cases 6, 20, 25, and 40 passed:
  `4 passed, 241 deselected in 0.50s`.

Final full-regression evidence:

- command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`
- result: `2276 passed in 12.08s`;
- prior split-session checkpoint: `2156 passed`;
- the higher repository-wide total includes later committed suites as well as
  the six new identity-vector executions; no attribution beyond the exact
  focused delta is claimed.

Both commands ran after the final source correction. `git diff --check` passed
for the source and test changes.

## 13. Artifact Evidence

- `analysis/gc_dataset_builder.py`
  - SHA-256:
    `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843`
  - bytes: `105463`
  - physical lines: `2716`
- `tests/test_gc_dataset_builder.py`
  - SHA-256:
    `3D470CC13BEDDB93B2212C9A7B97B4B1B9AAB3DABF208355534B5ADD9401B878`
  - bytes: `96557`
  - physical lines: `2656`
- `docs/gc_futures_split_session_calendar_checkpoint.md`
  - SHA-256: self-referential and therefore intentionally not embedded;
  - byte and physical-line counts are reported by the final external audit.

All three task artifacts must be UTF-8 without BOM, use LF line endings, contain
no tabs or trailing whitespace, and pass final exact-scope diff checking before
any staging authorization.

## 14. Promotion, Rollback, Stop, and Freeze State

This checkpoint does not authorize staging, commit, push, private-data build,
feature/label generation, model training, OOS inspection, strategy selection,
backtest promotion, paper trading, live execution, or integration.

Promotion requires a fresh independent exact-scope source/test/checkpoint audit
and explicit staging authorization. Before commit, rollback is restoration or
deletion of only the exact three task paths and requires explicit authorization.
After a later commit, rollback must use a bounded revert rather than history
rewriting.

Stop immediately on scope expansion, dependency drift, calendar/provenance
uncertainty, incomplete authoritative evidence, conservation failure, identity
or public-API drift, nondeterminism, exact 48-case mismatch, focused/full test
failure, formatting/hash mismatch, private-data mutation, training request, or
integration outside a separately approved freeze-lift scope.

Final checkpoint state:

- `IMPLEMENTATION_COMPLETE_FOR_AUDIT=True`
- `EXACT_AUTHORIZED_PATHS=3`
- `LOGICAL_CASES=48`
- `FOCUSED_TESTS_PASS=True`
- `FOCUSED_TESTS_COLLECTED=245`
- `FULL_REGRESSION_PASS=True`
- `FULL_REGRESSION_COLLECTED=2276`
- `PRIVATE_DATA_BUILD_PERFORMED=False`
- `TRAINING_PERFORMED=False`
- `INTEGRATION_PERFORMED=False`
- `STAGING_PERFORMED=False`
- `COMMIT_PERFORMED=False`
- `PUSH_PERFORMED=False`
- `GLOBAL_CODE_FREEZE_REMAINS_ACTIVE=True`
