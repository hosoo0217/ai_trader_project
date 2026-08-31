# GC Futures Prospective Independent Development Cohort Acquisition Manifest and Schedule Proposal

## 1. Proposal record

- Proposal date: `2026-08-31`.
- Repository baseline: `5bec446d3545b16ea6b325d34e6800da5424a097`.
- Program ID: `GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1`.
- Capability: prospective raw GC Futures acquisition manifest, schedule,
  immutable lineage, and atomic private intake publication.
- Proposal state: `DOCUMENTATION_ONLY_NOT_EXECUTED`.
- Private acquisition, source/test implementation, candidate, feature, label,
  corpus, training, final-OOS, integration, and trading authority: `NONE`.
- Global code freeze: `ACTIVE`.

This proposal defines the exact contract for a later private acquisition. It
does not create the private root, download market data, make a provider payment,
read outcomes, or alter any accepted evidence.

## 2. Exact purpose and non-authority

The published acquisition-first decision requires a prospective development
cohort to be frozen before any new hypothesis is selected. The purpose here is
to make that future acquisition deterministic, auditable, private, and
fail-closed.

The proposal answers only:

1. which metadata and evidence a future intake must preserve;
2. how the contract roster is derived without outcome selection;
3. when acquisition may occur;
4. how two independent workers prove deterministic publication; and
5. which conditions stop without producing a final root.

It does not decide that evidence will be sufficient or that any model should be
trained.

## 3. Exact documentation-only scope

The only changed path in this task is:

`docs/gc_futures_prospective_independent_development_cohort_acquisition_manifest_schedule_change_proposal.md`

No Python, test, fixture, dependency, configuration, private file, raw source,
calendar artifact, dataset, feature, label, model, report, integration, or other
documentation path may change. The three unrelated pre-existing untracked
proposal files remain outside scope and untouched.

Acceptance permits exact-path staging, cached audit, one local documentation
commit, and STOP before push. It does not imply private execution or GitHub
export authority.

## 4. Governing baseline and hashes

At proposal start, local `HEAD` and `origin/main` both equal:

`5bec446d3545b16ea6b325d34e6800da5424a097`.

The ahead/behind count is `0/0`, the tracked index/worktree is clean, and only
the three unrelated untracked drafts exist.

| Governing evidence | SHA-256 |
|---|---|
| Prospective acquisition-first decision | `966521B3FD0E945C8B5DC524FCE2752324D4EC968E4E09C10284851CF3E8455B` |
| Post-resolver pretraining readiness decision | `F344B32A9B3B923EC79F4F96519501D93BF00E4F67EDA1012C8F382991366296` |
| Terminal cross-segment resolver outcome | `107DF12717C0AFC60BA89D1721C02A77E1BD2631BB3C19FA5FFBEEF7330EB67D` |
| Phase-B closure decision | `5166E0D14BAA65A2AAFC8E17BE2E1740EC92AFCFCCC4CCED4B60CFF964E36F75` |
| GC AI strategy and training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |

Any baseline, hash, purpose, date, or authority drift stops rather than being
treated as a harmless refresh.

## 5. Prospective cohort identity and clock

The cohort ID is:

`GC_PROSPECTIVE_INDEPENDENT_DEVELOPMENT_COHORT_V1_20260901_20270301`

The immutable canonical GC trade-date interval is:

`[2026-09-01, 2027-03-01)`.

The acquisition-first decision timestamp `2026-08-31T08:17:34Z` precedes the
first eligible Globex session. The end is exclusive. Neither boundary may move
after any candidate, outcome, chart pattern, label, PnL, class count, or model
metric is observed.

Every historical source or derivative predating this interval remains
`PRIOR_RESEARCH_ONLY`. The previous GCQ26 OOS snapshot remains quarantined and
cannot become part of this cohort.

## 6. Reserved private root and exact layout

The future final root is reserved as:

`private_data/sierra_chart/gc_prospective_independent_development_cohort_v1/`

It must be absent before execution. The exact final members are:

```text
README.md
intake_manifest.json
acquisition_checkpoint.json
contract_roster.json
source_registry.jsonl
calendar_evidence_manifest.json
provider_log_manifest.json
contamination_registry.json
audit_report.json
raw/
provider_logs/
calendar_evidence/
```

Two isolated future worker roots are reserved beside it:

```text
private_data/sierra_chart/.gc_prospective_independent_development_cohort_v1.worker_a/
private_data/sierra_chart/.gc_prospective_independent_development_cohort_v1.worker_b/
```

No final member may be written incrementally. Only a successful two-run
transaction may publish one complete final root through atomic rename.

## 7. Top-level intake manifest contract

`intake_manifest.json` must contain exactly versioned, JSON-serializable fields
for:

- `schema_version` and `manifest_id`;
- `program_id`, `cohort_id`, and `purpose`;
- governing commit and five Section 4 hashes;
- decision timestamp and exact half-open trade-date interval;
- provider, service, timeframe, storage-unit, chart-timezone, canonical-timezone,
  and pinned tzdata identities;
- contract-roster rule ID, roster artifact ID, and roster digest;
- ordered source, provider-log, calendar-evidence, and contamination-record IDs;
- requested/admitted/excluded source counts and exact reason counts;
- worker identity, generation timestamp, and deterministic artifact-set identity;
- `outcome_contact_count=0` and `final_oos_payload_access_count=0`; and
- all candidate, feature, label, corpus, training, inference, integration,
  execution, and trading authority flags exact `false`.

Unknown fields, unordered maps used as identities, local secrets, account
credentials, payment details, and derived outcomes are forbidden.

## 8. Source registry record contract

Each ordered `source_registry.jsonl` record must bind:

- immutable source ID and relative private member path;
- original export filename and exchange-qualified Sierra symbol;
- product `GC`, venue `COMEX`, outright-futures instrument type, and contract
  year/month identity;
- exact role: `PREDECESSOR_CONTEXT`, `COHORT_CANDIDATE`,
  `SUCCESSOR_CONTEXT`, or `EXCLUDED`;
- SHA-256, byte count, decoded row count, first/last source timestamps, and
  first/last canonical trade dates;
- provider capture timestamp, completed-data cutoff, and download-log ID;
- timeframe `5M`, Sierra storage unit `1 Tick`, chart timezone, UTC conversion,
  and tzdata version;
- strict schema identity, numeric/tick-size contract, and ordering digest;
- roster membership proof and calendar-evidence IDs; and
- validation status plus an ordered tuple of exact reason tokens.

Raw bytes are never embedded in the registry. A duplicate byte hash under two
roles is `INVALID`, not two independent sources.

## 9. Contract-roster derivation

The exact contract roster is not chosen from observed price, volume, candidate,
or outcome behavior. A future `contract_roster.json` must be frozen before any
raw row is decoded by applying this rule:

1. begin with the official exchange listing snapshot for standard COMEX GC
   outright futures whose listed life intersects Section 5;
2. include every contract required by the accepted prior-completed-session
   volume rule to determine the effective contract for any eligible trade date;
3. include at least one valid predecessor context contract before cohort open;
4. include at least one valid successor context contract after cohort close;
5. retain low-volume listed comparison contracts when they are required to
   prove a roll decision; and
6. order by contract year, delivery-month ordinal, then exchange-qualified
   symbol.

The roster artifact must preserve the official listing source, acquisition
timestamp, content hash, derivation version, full ordered roster, role, and
reason for every inclusion/exclusion. Missing listing or comparison evidence is
`UNKNOWN`; manual winner selection is `INVALID`.

## 10. Exact acquisition schedule

| Gate | Exact time/boundary | Allowed action |
|---|---|---|
| `PROGRAM_LOCK` | `2026-08-31T08:17:34Z` | Governing decision only; complete. |
| `COHORT_OPEN` | canonical trade date `2026-09-01` | Begin prospective eligibility; no outcome inspection. |
| `METADATA_CHECKPOINT` | `2026-12-01T00:00:00Z` | Provider retention/connectivity and official-source availability metadata only. |
| `COHORT_CLOSE` | exclusive canonical trade date `2027-03-01` | Stop cohort eligibility exactly. |
| `CAPTURE_WINDOW` | `[2027-03-02T00:00:00Z, 2027-03-09T00:00:00Z)` | One complete contract-roster export transaction may be attempted. |
| `HASH_FREEZE` | immediately after each export | Hash, size, log, and immutable member registration before decoding. |
| `TWO_RUN_AUDIT` | only after all required sources and calendars are frozen | Build both isolated metadata/validation roots and compare. |

Failure to finish the complete capture inside `CAPTURE_WINDOW` yields terminal
`UNKNOWN_ACQUISITION_WINDOW_EXPIRED`. It does not extend the interval or permit
partial publication.

## 11. Provider and service boundary

The intended provider is Sierra Chart historical intraday data. Before capture,
the provider preflight must prove:

- an active Sierra Chart service package that permits the required historical
  download;
- `Maximum Historical Intraday Days to Download` for both tick and non-tick data
  at least `220`;
- `Intraday Data Storage Time Unit = 1 Tick`;
- `Days To Load = 220` or an exact date range covering the cohort and required
  predecessor/successor context;
- exchange-qualified contract symbols, not a continuous alias; and
- a message log showing requested start, received interval, record count,
  completion, and file identity for every export.

This proposal does not authorize payment, renewal, login, account mutation, GUI
control, or download. A later private-run authorization must name the exact
account-local action boundary without exposing credentials.

## 12. Export and capture procedure

The later authorized operator must create a fresh Sierra chart per exact
contract, bind the exchange-qualified symbol, use the locked data-limit settings,
delete no existing file, and request a fresh historical download into a newly
reserved path.

After completion, the export must be saved once, closed, hashed, and registered
before any parse. Notepad or another editor is optional and has no evidentiary
role. Re-saving, manual correction, spreadsheet conversion, clipboard editing,
merging, sorting, or timezone adjustment of raw exports is forbidden.

Message-log evidence is captured as a separate immutable text/image artifact
with its own hash. A screenshot alone cannot substitute for the export or log.

## 13. Official calendar evidence contract

`calendar_evidence_manifest.json` must bind authoritative CME Globex GC trading
hours for every trade date in Section 5, including holiday, early halt/close,
pre-open, reopen, split-session, and next eligible trade-date semantics.

Primary evidence is the official CME trading-hours structured download or
official notice. GCC email clarification may supplement an ambiguous historical
state but cannot silently override a structured official source. Each item must
preserve source URL or message identity, retrieval timestamp, SHA-256, covered
dates, timezone, and normalized-row digest.

If 2027 official evidence is not available or exact at capture time, the entire
transaction is `UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE` and final publication is
forbidden.

## 14. Timezone, session, and completed-bar boundary

Source time interpretation must begin with the recorded Sierra Chart timezone,
convert under one pinned tzdata release to `America/New_York` and UTC, and assign
canonical GC trade dates only through the accepted session calendar.

Ambiguous and nonexistent local times require explicit fold/gap handling. No
calendar date, filename date, capture date, or chart display label may substitute
for a canonical trade date.

The completed-data cutoff must be independently later than every admitted 5-minute
bar. A bar that is still open, delayed beyond the attested cutoff, outside an
official session, or assigned to a later trade date is excluded with an exact
reason; it is never truncated into validity.

## 15. Data-quality and conservation gates

Every candidate source must pass:

- strict delimiter, header, row-width, type, and finite-value validation;
- exact `0.1` GC tick compatibility for OHLC;
- `low <= open/close <= high` and nonnegative integer volume/trades/bid/ask;
- exact volume conservation under the accepted source schema;
- unique ordered effective timestamps and deterministic duplicate rejection;
- complete expected-slot reconciliation against official session intervals;
- explicit gap accounting with no interpolation, forward fill, or zero synthesis;
- canonical contract/date and roster conservation; and
- byte-identical repeat validation.

The audit reports counts and reason tokens only. It may not compute candidate
returns, direction, profitability, labels, or model statistics.

## 16. Contamination registry and prior-evidence exclusion

`contamination_registry.json` must enumerate every prior research program,
accepted/failed candidate population, diagnostic output root, chart/manual review,
label/outcome contact record, and OOS artifact that could overlap the new cohort.

Every admitted atomic source group must prove no prior candidate, feature, label,
threshold, metric, or human outcome review. Mere provider or file-format testing
without row/outcome inspection is recorded but does not automatically contaminate
the cohort.

Unverifiable overlap yields `UNKNOWN_CONTAMINATION_HISTORY`; confirmed overlap
yields `INVALID_PRIOR_OUTCOME_CONTACT`. Exclusion cannot change the Section 5
clock or lower any minimum evidence gate.

## 17. Outcome blindness and local-AI boundary

Before a later cohort-freeze decision, no process may derive or inspect:

- setup candidates or direction;
- feature values or H=12 labels;
- returns, MAE/MFE, PnL, hit rate, class balance, or favorable dates;
- validation, calibration, or model metrics; or
- final-OOS payloads or outcomes.

Local language models may review the public proposal and redacted metadata schema
only. They may not ingest private raw bytes, provider logs containing account
details, candidate evidence, labels, outcomes, or OOS. Their output cannot alter
status, manifests, data, or authority.

## 18. Two-run atomic private transaction

The future transaction must:

1. prove the final root and both worker roots are absent;
2. copy immutable inputs by verified hash into each isolated worker scope;
3. build every manifest/member independently with network disabled;
4. validate complete member order, hashes, counts, reasons, and authorities;
5. compare every non-worker-specific object and byte for equality;
6. independently audit both roots without reading outcomes;
7. remove worker-specific nondeterminism from the publishable identity;
8. atomically rename exactly one complete worker root to the final root; and
9. delete the other worker root only after final-root revalidation.

Any interruption, mismatch, unexpected member, or partial write leaves the final
root absent. Worker roots are recoverable diagnostics only until explicitly
audited and safely removed under the later authorization.

## 19. Status precedence and exact reasons

Status precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > VALID`.

Minimum terminal reasons include:

- `INVALID_AUTHORITY_OR_PURPOSE_DRIFT`;
- `INVALID_SOURCE_SCHEMA_OR_CONSERVATION`;
- `INVALID_PRIOR_OUTCOME_CONTACT`;
- `INVALID_DUPLICATE_OR_CONTRACT_IDENTITY`;
- `AMBIGUOUS_CONTRACT_OR_CALENDAR_IDENTITY`;
- `UNKNOWN_ACQUISITION_WINDOW_EXPIRED`;
- `UNKNOWN_REQUIRED_SOURCE_UNAVAILABLE`;
- `UNKNOWN_CALENDAR_COVERAGE_INCOMPLETE`;
- `UNKNOWN_CONTAMINATION_HISTORY`; and
- `VALID_RAW_ACQUISITION_ONLY_NO_RESEARCH_AUTHORITY`.

`VALID` means only that raw acquisition and lineage passed. It grants no
candidate, feature, label, corpus, training, OOS, integration, or trading authority.

## 20. Privacy, Git, and export boundary

All Section 6 members and worker roots are private and Git-ignored. Private paths,
raw bytes, logs, screenshots, account identifiers, service balances, credentials,
and provider messages may not be staged, committed, pushed, uploaded, or sent to
a remote AI service.

Only public documentation, schema-only source/tests under a later freeze-lift,
and redacted aggregate audit facts may ever be considered for Git. Every future
push requires exact commit identification and separate GitHub privacy/export
authorization.

No secret scanning result can make private market payloads publishable.

## 21. Rollback, stop, and resume boundary

Before local commit, rollback is deletion of this exact proposal file. After
commit, rollback requires a bounded revert; history and private evidence are never
rewritten.

Stop on baseline/hash drift, unavailable contract listing, roster ambiguity,
retention below the locked need, missing provider logs, incomplete official
calendar, timezone uncertainty, schema/conservation failure, prior outcome
contact, nondeterminism, scope expansion, or any request to inspect candidate or
model outcomes.

After publication of this proposal, the next single task is a documentation-only
freeze-lift decision that may reserve exact schema-validator source/test paths.
It may not run acquisition. Actual provider access and private transaction require
a later exact authorization after the cohort closes and all prerequisites exist.

## 22. Exact sequential 48-case acceptance matrix

1. Local `HEAD` and `origin/main` equal the exact proposal baseline.
2. Ahead/behind is exactly `0/0` at proposal start.
3. Exact one-file documentation scope is preserved.
4. The three unrelated untracked drafts remain untouched.
5. The prospective acquisition-first decision hash reconciles.
6. The post-resolver readiness hash reconciles.
7. The terminal resolver outcome hash reconciles.
8. The Phase-B closure hash reconciles.
9. The AI strategy/training hash reconciles.
10. Program and cohort IDs are exact and new.
11. The cohort interval is exactly `[2026-09-01, 2027-03-01)`.
12. The governing decision timestamp precedes cohort open.
13. Prior historical evidence is excluded from the new cohort.
14. Existing GCQ26 OOS remains quarantined.
15. Future final root is absent before execution.
16. Final and worker paths match Section 6 exactly.
17. Final member list and order are exhaustive.
18. Top-level manifest authority flags are all false.
19. Outcome and final-OOS access counts are zero.
20. Source records bind exact symbols, hashes, counts, and cutoffs.
21. Duplicate bytes cannot become independent sources.
22. Contract roster derives without observed outcomes.
23. Predecessor and successor context are required.
24. Manual winner or continuous-symbol substitution is rejected.
25. All seven Section 10 schedule gates are exact.
26. Expired capture window returns terminal `UNKNOWN`.
27. Sierra Chart entitlement/settings preflight is complete before capture.
28. This proposal performs no payment, renewal, login, or download.
29. Raw export is never manually edited, merged, or resaved.
30. Provider message-log evidence is separately hashed.
31. Official CME calendar covers every eligible trade date.
32. 2027 calendar incompleteness blocks final publication.
33. Timezone conversion and tzdata identity are deterministic.
34. Incomplete or future bars are excluded exactly.
35. Strict schema, tick, OHLC, and numeric gates pass.
36. Expected-slot and volume conservation reconcile exactly.
37. Missing bars are never filled or synthesized.
38. Contamination registry is complete and independently audited.
39. Prior outcome contact is `INVALID`, not an exclusion repair.
40. Candidate, label, return, PnL, and model inspection remain zero.
41. Local AI receives public/redacted metadata only.
42. Both isolated workers are object- and byte-equal.
43. Publication is one atomic rename into an absent final root.
44. Failure leaves final root absent without mutating inputs.
45. Private payloads, logs, and account facts remain outside Git/remotes.
46. Fresh focused and full cache-disabled regressions pass.
47. Exactly 24 sections, 48 cases, formatting, hashes, and cached diff pass.
48. Work stops before push, freeze lift, acquisition, training, OOS, and integration.

## 23. Independent audit and local-commit acceptance

Independent acceptance must verify:

- exact baseline, five hashes, one-file scope, and untouched unrelated drafts;
- final private root remains absent and no worker root is created;
- exact `24` numbered sections and `48` sequential cases;
- no trailing whitespace and cached `git diff --check` PASS;
- complete cached file content and final file SHA-256/byte/line counts;
- focused pretraining-corpus and full explicit `tests/` regressions with cache
  disabled; and
- zero source/test/private/OOS/training/integration/trading contact.

Fresh acceptance evidence on `2026-08-31` is:

- focused pretraining-corpus regression: `66 passed in 0.77s`;
- full explicit public regression: `2674 passed in 40.22s`;
- proposal structure: exactly `24` numbered sections and `48` sequential cases;
- all five Section 4 hashes: reconciled;
- final root and both worker roots: absent;
- trailing whitespace: zero; and
- unrelated untracked drafts: exact three and unchanged.

Acceptance permits one local commit with subject:

`docs: propose prospective GC acquisition manifest schedule`

The commit does not authorize push. Post-commit audit must prove an empty index,
no tracked worktree diff, exactly one new tracked path, and only the three
unrelated untracked drafts remaining.

## 24. Final proposal decision and STOP boundary

The exact proposal decision is:

`PROPOSE_PROSPECTIVE_GC_RAW_ACQUISITION_MANIFEST_SCHEDULE_NO_EXECUTION_NO_TRAINING_NO_OOS`

This proposal converts the acquisition-first direction into one exact private
intake, schedule, contract-roster, calendar, provider-log, two-run, atomicity,
privacy, and rollback contract. It deliberately grants no permission to obtain
or inspect market data now.

After independent audit and the exact local documentation commit, work stops
before push. A separate exact GitHub privacy/export authorization is required to
publish that commit. Private acquisition remains unavailable until the cohort
closes, the proposal is published, a later freeze-lift decision passes, all
required official/provider evidence exists, and a separate exact private-run
authorization is granted.
