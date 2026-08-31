# GC Futures Prospective Independent Development Cohort Acquisition Schema-Validator Freeze-Lift Decision

## 1. Decision record

- Decision date: `2026-08-31`.
- Repository baseline: `87f01e2b389f2d1f8c389de89a941469da3813cc`.
- Capability: deterministic public validation of prospective GC acquisition
  manifests and their immutable metadata dependencies.
- Decision version: `GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1`.
- Current task authority: this one documentation file through an audited local
  commit only.
- Private acquisition, raw-payload access, dataset/corpus build, candidate,
  feature, label, training, final-OOS, integration, and trading authority: `NONE`.
- Global code freeze: `ACTIVE` outside this exact file.

This decision may reserve a later exact source/test/checkpoint implementation.
It does not implement that validator or execute the private acquisition plan.

## 2. Selected capability and purpose

The selected capability is one pure public schema validator for the manifest
contract defined by the published prospective acquisition proposal. The future
validator will accept caller-supplied immutable metadata objects and return a
deterministic fail-closed result.

It will answer whether the supplied configuration, contract roster, source
registry, provider logs, calendar evidence, contamination registry, identities,
and authority flags form one internally valid raw-acquisition manifest.

It will not read files, download data, parse private raw rows, build a market
dataset, inspect outcomes, or decide that evidence is sufficient for research or
training.

## 3. Verified baseline and governing hashes

At drafting start:

- local `HEAD`: `87f01e2b389f2d1f8c389de89a941469da3813cc`;
- local `origin/main`: `87f01e2b389f2d1f8c389de89a941469da3813cc`;
- ahead/behind: `0/0`;
- tracked index and worktree: clean; and
- unrelated untracked drafts: exact three.

| Governing evidence | SHA-256 |
|---|---|
| Prospective acquisition manifest/schedule proposal | `FA4AF7DDD77D5E75AE82988AEBD5FE98A55B514C2D063C8012AD95CA4335F3B5` |
| Prospective acquisition-first decision | `966521B3FD0E945C8B5DC524FCE2752324D4EC968E4E09C10284851CF3E8455B` |
| Post-resolver pretraining readiness decision | `F344B32A9B3B923EC79F4F96519501D93BF00E4F67EDA1012C8F382991366296` |
| Terminal cross-segment resolver outcome | `107DF12717C0AFC60BA89D1721C02A77E1BD2631BB3C19FA5FFBEEF7330EB67D` |
| GC AI strategy and training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |

Baseline, hash, purpose, or authority drift stops rather than being normalized.

## 4. Exact documentation-only scope

The only changed path in this task is:

`docs/gc_futures_prospective_independent_development_cohort_acquisition_schema_validator_freeze_lift_decision.md`

No source, test, fixture, dependency, configuration, package export, private
artifact, provider log, calendar evidence, dataset, feature, label, model,
integration, or other documentation path may change.

The three pre-existing unrelated untracked proposal files remain untouched.
Acceptance permits exact-path staging, cached audit, one local documentation
commit, and STOP before push.

## 5. Authority and code-freeze boundary

This decision grants only future schema-validator implementation eligibility
after separate publication and exact implementation authorization. It grants no
permission to:

- connect to Sierra Chart or any data provider;
- make a payment, renew service, log in, or operate a GUI;
- create the final or worker private roots;
- read, copy, hash, decode, normalize, or summarize private market payloads;
- generate a candidate, feature, label, partition, corpus, or model;
- inspect prior or future OOS; or
- change runtime, strategy, risk, broker, paper, live, or trading behavior.

All existing runtime flags and authorities remain unchanged and false.

## 6. Version, instrument, and fixed constants

The future module must expose these exact constants:

```python
GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION = (
    "GC-PROSPECTIVE-ACQUISITION-SCHEMA-VALIDATOR-V1"
)
GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID = (
    "GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1"
)
GC_PROSPECTIVE_ACQUISITION_COHORT_ID = (
    "GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1_20260901_20270301"
)
GC_PROSPECTIVE_ACQUISITION_INSTRUMENT = "GC"
GC_PROSPECTIVE_ACQUISITION_VENUE = "COMEX"
GC_PROSPECTIVE_ACQUISITION_TIMEFRAME = "5M"
GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT = "1 Tick"
GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE = "Asia/Tokyo"
GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE = "America/New_York"
GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD = 220
```

The canonical trade-date interval is exact
`[2026-09-01, 2027-03-01)`. The capture interval is exact
`[2027-03-02T00:00:00Z, 2027-03-09T00:00:00Z)`.

## 7. Pure-input and no-I/O contract

The future validator receives only frozen dataclass/enum/date/datetime/integer/
string/tuple values supplied by its caller. The public API has no path, bytes,
file object, environment, URL, session, credential, payment, dataframe, chart,
model, or arbitrary mapping parameter.

It performs no filesystem enumeration, file opening, hashing of private files,
network request, subprocess, current-clock read, timezone database discovery,
randomness, logging side effect, cache write, serialization, model call, or
runtime integration.

The later private transaction remains responsible for producing verified
metadata from private evidence. Passing metadata to this validator does not
prove that the private transaction was authorized.

## 8. Exact configuration contract

```python
@dataclass(frozen=True)
class GCProspectiveAcquisitionConfig:
    decision_timestamp: datetime
    cohort_start_trade_date: date
    cohort_end_trade_date: date
    capture_window_start_timestamp: datetime
    capture_window_end_timestamp: datetime
    provider: str
    instrument: str
    venue: str
    timeframe: str
    storage_time_unit: str
    maximum_historical_days_to_download: int
    chart_timezone: str
    exchange_timezone: str
    timezone_data_version: str
    governing_proposal_sha256: str
```

Every field is exact and independently validated. Timestamps must be aware and
UTC. Dates are half-open and fixed to Section 6. The governing proposal hash is
exactly the first Section 3 hash. A nonpositive retention setting, different
timezone, changed date, naive datetime, or malformed hash is `INVALID`.

## 9. Contract-roster role and record contract

```python
class GCProspectiveAcquisitionSourceRole(str, Enum):
    PREDECESSOR_CONTEXT = "PREDECESSOR_CONTEXT"
    COHORT_CANDIDATE = "COHORT_CANDIDATE"
    SUCCESSOR_CONTEXT = "SUCCESSOR_CONTEXT"
    EXCLUDED = "EXCLUDED"

@dataclass(frozen=True)
class GCProspectiveContractRosterRecord:
    roster_record_id: str
    contract: str
    role: GCProspectiveAcquisitionSourceRole
    delivery_order: int
    listing_source_id: str
    listing_source_sha256: str
    inclusion_reason: str
```

Contracts must match `GC([GJMQVZ])(\d{2})-COMEX`. Delivery order must equal the
canonical year/month-code order, be unique, and be strictly increasing. A valid
roster contains at least one predecessor, one cohort candidate, and one successor.
Excluded records remain ordered evidence but cannot have an admitted source.

Every record ID is recomputed from its identity fields. Caller-supplied order or
ID drift is `INVALID`; a structurally valid roster missing a required comparison
role is `UNKNOWN`.

## 10. Exact source metadata record

```python
@dataclass(frozen=True)
class GCProspectiveAcquisitionSourceRecord:
    source_id: str
    source_name: str
    source_sha256: str
    byte_count: int
    row_count: int
    contract: str
    role: GCProspectiveAcquisitionSourceRole
    capture_timestamp: datetime
    acquisition_completed_timestamp: datetime
    completed_data_cutoff_timestamp: datetime
    first_source_timestamp: datetime
    last_source_timestamp: datetime
    first_trade_date: date
    last_trade_date: date
    provider_log_id: str
    calendar_evidence_ids: tuple[str, ...]
    chart_timezone: str
    timeframe: str
    storage_time_unit: str
    schema_id: str
    ordering_digest: str
    validation_status: SMCV2PrimitiveStatus
    reasons: tuple[str, ...]
```

Counts are nonnegative, hashes are lowercase 64-hex, timestamps are aware, and
the capture timestamp lies inside the fixed capture window. Source/cutoff order,
contract/role roster membership, calendar IDs, exact settings, unique source
names, source IDs, and byte hashes are conserved.

No raw bar, OHLC, volume, candidate, label, return, or outcome field is allowed.

## 11. Provider-log metadata contract

```python
@dataclass(frozen=True)
class GCProspectiveProviderLogRecord:
    provider_log_id: str
    provider: str
    contract: str
    requested_start_timestamp: datetime
    requested_end_timestamp: datetime
    received_start_timestamp: datetime
    received_end_timestamp: datetime
    received_record_count: int
    completion_timestamp: datetime
    completion_status: str
    log_artifact_sha256: str
```

Status is exactly `COMPLETE`. Requested/received intervals and completion order
must be coherent, every admitted source must bind one unique provider log, and
the received record count must equal the source record count. Missing or
incomplete but well-formed log evidence is `UNKNOWN`; contradictory or malformed
evidence is `INVALID`.

The record contains no account name, balance, credential, payment identifier,
server token, or unrestricted message body.

## 12. Calendar-evidence metadata contract

```python
@dataclass(frozen=True)
class GCProspectiveCalendarEvidenceRecord:
    calendar_evidence_id: str
    calendar_version: str
    source_kind: str
    source_reference: str
    source_sha256: str
    retrieval_timestamp: datetime
    first_trade_date: date
    last_trade_date: date
    exchange_timezone: str
    normalized_row_digest: str
    authoritative: bool
```

Allowed source kinds are exact `CME_STRUCTURED_TRADING_HOURS`,
`CME_OFFICIAL_NOTICE`, and `CME_GCC_CLARIFICATION`. Every admitted source needs
authoritative structured/official coverage across its admitted trade dates.
Clarification alone is insufficient.

The union must cover every date in the cohort interval without a gap. Missing
coverage is `UNKNOWN`; overlap with conflicting version/digest/timezone or false
authority is `INVALID`.

## 13. Contamination metadata contract

```python
@dataclass(frozen=True)
class GCProspectiveContaminationRecord:
    contamination_record_id: str
    evidence_id: str
    evidence_kind: str
    first_trade_date: date
    last_trade_date: date
    outcome_contacted: bool
    overlaps_cohort: bool
    exclusion_reason: str
    evidence_sha256: str
```

The record set must cover every governing prior research and OOS identity named
by the private transaction. A prior item with outcome contact and cohort overlap
is `INVALID_PRIOR_OUTCOME_CONTACT`; unknown overlap or incomplete registry is
`UNKNOWN_CONTAMINATION_HISTORY`.

The public validator checks only supplied metadata. It cannot discover omitted
private evidence and therefore never upgrades an incomplete registry by
assumption.

## 14. Immutable acquisition manifest contract

```python
@dataclass(frozen=True)
class GCProspectiveAcquisitionManifest:
    manifest_id: str
    version: str
    program_id: str
    cohort_id: str
    purpose: str
    governing_commit: str
    governing_hashes: tuple[tuple[str, str], ...]
    config_id: str
    roster_record_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    provider_log_ids: tuple[str, ...]
    calendar_evidence_ids: tuple[str, ...]
    contamination_record_ids: tuple[str, ...]
    requested_source_count: int
    admitted_source_count: int
    excluded_source_count: int
    reason_counts: tuple[tuple[str, int], ...]
    artifact_set_identity: str
    outcome_contact_count: int
    final_oos_payload_access_count: int
    candidate_build_allowed: bool
    feature_label_build_allowed: bool
    corpus_build_allowed: bool
    training_allowed: bool
    oos_evaluation_allowed: bool
    integration_allowed: bool
    trading_allowed: bool
```

Purpose is exactly `PROSPECTIVE_RAW_ACQUISITION_ONLY`. Counts, ordered IDs,
reason counts, config/manifest/artifact identities, and five governing hashes are
recomputed. Both access counts are zero and all seven authority flags are false.

## 15. Result and status contract

```python
@dataclass(frozen=True)
class GCProspectiveAcquisitionResult:
    status: SMCV2PrimitiveStatus
    manifest: GCProspectiveAcquisitionManifest | None = None
    reasons: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
```

Status precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID`. `NONE` is not an
allowed terminal acquisition status. A manifest is returned only for `VALID`.

`VALID` means only that supplied raw-acquisition metadata is internally valid.
Its final reason is exact
`VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY`. It does not mean the raw
payload was independently inspected, the cohort is frozen, or research/training
may begin.

## 16. Deterministic identity contract

The future helper is:

```python
def make_gc_prospective_acquisition_id(kind: str, payload: object) -> str: ...
```

Allowed identity kinds are exact `CONFIG`, `ROSTER`, `SOURCE`, `PROVIDER_LOG`,
`CALENDAR`, `CONTAMINATION`, `MANIFEST`, and `ARTIFACT_SET`. Canonical JSON uses
sorted object keys, compact separators, UTF-8, lowercase enum values as declared,
ISO dates, UTC `Z` datetimes, decimal strings, ordered tuples, and no floats.

IDs use an exact version/kind namespace and lowercase SHA-256. Every supplied ID,
digest, count, reason order, and artifact-set identity is recomputed. Reordered
independent sets must normalize to the declared deterministic domain order;
ordered manifest fields must then match exactly.

## 17. Validation semantics and reason order

Independently determinable invalid evidence is validated before missing top-level
context. A missing input cannot hide a malformed supplied hash, naive timestamp,
invalid authority flag, duplicate identity, outcome contact, or contradictory
calendar.

The exact reason order is:

```text
INVALID_AUTHORITY_OR_PURPOSE_DRIFT
INVALID_CONFIGURATION
INVALID_ROSTER_EVIDENCE
INVALID_SOURCE_METADATA
INVALID_PROVIDER_LOG_EVIDENCE
INVALID_CALENDAR_EVIDENCE
INVALID_PRIOR_OUTCOME_CONTACT
INVALID_IDENTITY_OR_CONSERVATION
AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY
MISSING_TOP_LEVEL_CONTEXT
UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE
UNKNOWN_PROVIDER_LOG_INCOMPLETE
UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE
UNKNOWN_CONTAMINATION_HISTORY
UNKNOWN_ACQUISITION_WINDOW_EXPIRED
VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY
```

Reasons are unique and ordered. Blocking reasons are the ordered non-valid
subset. Missing or unknown evidence is never coerced to zero, false, or valid.

## 18. Exact keyword-only validator API

```python
def validate_gc_prospective_acquisition_manifest(
    *,
    config: GCProspectiveAcquisitionConfig | None,
    contract_roster: tuple[GCProspectiveContractRosterRecord, ...] | None,
    sources: tuple[GCProspectiveAcquisitionSourceRecord, ...] | None,
    provider_logs: tuple[GCProspectiveProviderLogRecord, ...] | None,
    calendar_evidence: tuple[GCProspectiveCalendarEvidenceRecord, ...] | None,
    contamination_records: tuple[GCProspectiveContaminationRecord, ...] | None,
    manifest: GCProspectiveAcquisitionManifest | None,
) -> GCProspectiveAcquisitionResult: ...
```

All arguments are keyword-only. The function performs a total validation pass,
returns immutable tuples, does not mutate caller inputs, and is deterministic
across repeated calls. Supplied tuple enumeration cannot decide semantic winner;
domain ordering and status precedence do.

No overload, convenience path/bytes loader, dataframe adapter, CLI, network
client, serializer, trainer, or runtime hook is authorized.

## 19. Exact public module surface

The future module `__all__` contains only:

```text
GC_PROSPECTIVE_ACQUISITION_VALIDATOR_VERSION
GC_PROSPECTIVE_ACQUISITION_PROGRAM_ID
GC_PROSPECTIVE_ACQUISITION_COHORT_ID
GC_PROSPECTIVE_ACQUISITION_INSTRUMENT
GC_PROSPECTIVE_ACQUISITION_VENUE
GC_PROSPECTIVE_ACQUISITION_TIMEFRAME
GC_PROSPECTIVE_ACQUISITION_STORAGE_UNIT
GC_PROSPECTIVE_ACQUISITION_CHART_TIMEZONE
GC_PROSPECTIVE_ACQUISITION_EXCHANGE_TIMEZONE
GC_PROSPECTIVE_ACQUISITION_DAYS_TO_LOAD
GCProspectiveAcquisitionSourceRole
GCProspectiveAcquisitionConfig
GCProspectiveContractRosterRecord
GCProspectiveAcquisitionSourceRecord
GCProspectiveProviderLogRecord
GCProspectiveCalendarEvidenceRecord
GCProspectiveContaminationRecord
GCProspectiveAcquisitionManifest
GCProspectiveAcquisitionResult
make_gc_prospective_acquisition_id
validate_gc_prospective_acquisition_manifest
```

`analysis/__init__.py` and every other package export remain unchanged. The new
module may import standard-library types and the existing
`SMCV2PrimitiveStatus`; it adds no dependency.

## 20. Security, privacy, and no-trading boundary

The future public module and tests use synthetic metadata only. Tests may not
enumerate or open `private_data/`, user directories, Sierra files/logs, browser
state, emails, screenshots, credentials, balances, or network resources.

No public fixture may contain a private filename/hash combination copied from an
actual future source. Synthetic hashes are generated from fixed public literals.
Error messages and results contain no local path, account, credential, provider
message body, raw row, price, volume, candidate, label, outcome, or PnL.

The validator cannot emit BUY/SELL, confidence, risk, entry, stop, target, size,
order, fill, model prediction, or execution authority.

## 21. Reserved future exact three-path scope

Only after this decision is audited, locally committed, separately push-authorized,
published, and followed by exact test-first implementation authorization may the
future implementation change exactly:

- `analysis/gc_prospective_acquisition_manifest.py`;
- `tests/test_gc_prospective_acquisition_manifest.py`;
- `docs/gc_futures_prospective_independent_development_cohort_acquisition_manifest_checkpoint.md`.

All three paths are absent at this decision baseline. No other source, test,
fixture, export, dependency, configuration, private artifact, or documentation
path is reserved.

That implementation still may not run acquisition, access private data, choose a
hypothesis, build candidates/features/labels/corpus, train, inspect OOS, or
integrate runtime behavior.

## 22. Inline synthetic exact 48-case test matrix

1. Exact public constants and fixed cohort/capture boundaries pass.
2. Config is frozen, aware-UTC, exact, deterministic, and hash-bound.
3. Missing config returns `UNKNOWN` after independently invalid inputs are detected.
4. Naive or non-UTC config timestamp is `INVALID_CONFIGURATION`.
5. Changed cohort or capture boundary is `INVALID_CONFIGURATION`.
6. Retention other than exact `220` is `INVALID_CONFIGURATION`.
7. Provider/instrument/venue/timeframe/storage/timezone drift is invalid.
8. Malformed or wrong governing proposal hash is invalid.
9. Exact contract regex and canonical delivery order pass.
10. Duplicate contract, roster ID, delivery order, or listing identity is invalid.
11. Missing predecessor context returns `UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE`.
12. Missing cohort candidate returns `UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE`.
13. Missing successor context returns `UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE`.
14. Excluded roster record cannot have an admitted source.
15. Manual/reordered roster ID drift is invalid.
16. Source metadata dataclass is frozen and contains no raw-bar field.
17. Malformed source hash, digest, count, timestamp, or ID is invalid.
18. Capture outside the exact capture window is invalid.
19. Source/acquisition/cutoff/coverage timestamp inversion is invalid.
20. Source contract/role absent from roster is invalid.
21. Duplicate source name, ID, or byte hash is invalid.
22. Exact chart timezone, timeframe, storage unit, and schema are enforced.
23. Every admitted source requires one matching provider log.
24. Provider log status other than `COMPLETE` returns unknown or invalid by form.
25. Provider/source contract and record-count contradiction is invalid.
26. Provider interval or completion-order contradiction is invalid.
27. Provider-log record excludes account, balance, credential, and message fields.
28. Allowed official calendar kinds and exact timezone pass.
29. Clarification-only coverage returns `UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE`.
30. Any cohort calendar gap returns `UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE`.
31. Conflicting overlapping calendar identity is ambiguous or invalid by form.
32. False authoritative flag for admitted coverage is invalid.
33. Complete nonoverlapping contamination registry passes.
34. Outcome-contacted overlapping prior evidence is invalid.
35. Unknown overlap or incomplete contamination coverage returns unknown.
36. Manifest purpose and seven authority flags are exact.
37. Outcome and final-OOS access counts must be zero.
38. Requested/admitted/excluded and reason counts conserve exactly.
39. Ordered roster/source/log/calendar/contamination IDs match recomputation.
40. Config, manifest, and artifact-set identities recompute exactly.
41. Malformed supplied evidence outranks missing top-level context.
42. Status precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID`.
43. Reasons and blocking reasons are unique and exact-order deterministic.
44. Valid result returns one manifest and no research/training authority.
45. Repeated calls and semantically reordered independent inputs are identical.
46. Module performs no filesystem, network, clock, randomness, or mutation work.
47. `__all__` and exact three-path scope contain no extra API or file.
48. Focused and full public regressions pass with private/OOS/trading contact zero.

## 23. Audit, rollback, and promotion gates

Independent acceptance of this decision requires:

- exact one-file scope and untouched unrelated drafts;
- exact baseline and all five Section 3 hashes;
- all three Section 21 paths absent;
- exact `24` numbered sections and `48` sequential cases;
- complete content, formatting, no trailing whitespace, and cached
  `git diff --check` PASS;
- focused pretraining-corpus and full explicit public regression with cache
  disabled; and
- zero private, source/test, acquisition, OOS, training, integration, or trading
  contact.

Fresh acceptance evidence on `2026-08-31` is:

- focused pretraining-corpus regression: `66 passed in 0.64s`;
- full explicit public regression: `2674 passed in 41.47s`;
- structure: exactly `24` numbered sections and `48` sequential cases;
- all five Section 3 hashes: reconciled;
- all three Section 21 implementation paths: absent;
- trailing whitespace: zero; and
- unrelated untracked drafts: exact three and unchanged.

Acceptance permits one local commit with subject:

`docs: freeze prospective GC acquisition validator contract`

Before commit, rollback is deletion of this exact new file. After commit,
rollback requires a bounded revert. Publication requires separate exact GitHub
privacy/export authorization.

## 24. Final decision and resume boundary

The exact decision is:

`FREEZE_LIFT_ELIGIBLE_PROSPECTIVE_GC_ACQUISITION_METADATA_VALIDATOR_NO_PRIVATE_EXECUTION_NO_TRAINING_NO_OOS`

This decision freezes the future validator's constants, dataclasses, identities,
status precedence, reasons, pure keyword-only API, public surface, synthetic test
matrix, privacy boundary, and exact three-path implementation reservation.

After independent audit and one local documentation commit, work stops before
push. After separate publication and exact implementation authorization, only
the Section 21 test-first implementation may proceed to a local commit. No
private acquisition, provider operation, data read, candidate/feature/label/
corpus build, training, final-OOS access, integration, paper trading, or live
trading is implied.
