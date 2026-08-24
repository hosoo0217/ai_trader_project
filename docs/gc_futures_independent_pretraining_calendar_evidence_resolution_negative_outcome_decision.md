# GC Futures Independent Pretraining Calendar Evidence Resolution Negative Outcome Decision

## 1. Decision Record

- Decision date: `2026-08-25`.
- Repository baseline: `0aa93e5cc3e4ef726fbde811fc48e49055157b85`.
- Governing proposal:
  `docs/gc_futures_independent_pretraining_calendar_evidence_resolution_change_proposal.md`.
- Governing proposal SHA-256:
  `E51DBD41F77C221B68D0F3DF0E4C3209149A0571F75F16F7E264A30BA13601EC`.
- Final decision:
  `OFFICIAL_REFERENCE_GUIDE_BYTES_NOT_ACQUIRED_NO_NORMALIZATION_NO_DOWNSTREAM_AUTHORITY`.

The separately authorized acquisition-and-normalization attempt stopped before private mutation.
The exact official PDF candidate could not be acquired as accepted PDF bytes, so the governing
proposal's acquisition gate did not pass and calendar normalization was not attempted.

## 2. Exact Scope

This task creates only:

- `docs/gc_futures_independent_pretraining_calendar_evidence_resolution_negative_outcome_decision.md`.

No Python, tests, fixtures, private artifacts, manifests, normalized rows, datasets, features,
labels, models, configuration, integration, or other documentation changes are authorized. The
three pre-existing unrelated untracked documents remain untouched and outside scope.

## 3. Authorized Operation Boundary

The governing proposal authorized a later private operation only if the official Reference Guide
could first be acquired as deterministic accepted bytes. Its atomic order was:

1. acquire and manifest-bind the official guide;
2. audit its bytes and required proposition;
3. normalize the exact 2024-2025 development calendar;
4. audit every normalized row;
5. stop before dataset build.

Failure at step 1 therefore forbids steps 2-5. A search excerpt, cached index text, redirect page,
or semantically adjacent advisory cannot be promoted into the missing artifact.

## 4. Canonical Candidate Result

The proposal-locked candidate was:

`https://www.cmegroup.com/content/dam/cmegroup/globex/files/GlobexRefGd.pdf`

On `2026-08-25`, direct retrieval did not produce accepted PDF bytes. The interactive CME page
resolved to a CME `404: Page Not Found` response. The attempted response was not stored, hashed,
manifested, or treated as evidence.

## 5. Alternate Official Path Result

An official-domain search index exposed the historical alternate path:

`https://www.cmegroup.com/globex/files/GlobexRefGd.pdf`

Opening that path redirected to:

`https://www.cmegroup.com/solutions/market-access/globex.html#overview`

The resolved content was an HTML Globex overview page, not PDF bytes. It therefore failed the
governing media-type, byte-integrity, and exact-artifact requirements and was not acquired.

## 6. Current CME Resource-Page Finding

The current official Globex overview identifies CME Globex, links the Client Systems Wiki, iLink
Session Policy, and Trading Hours, and supplies GCC contact details. The fetched current page did
not expose downloadable Reference Guide bytes.

Historical search-index text that still labels a `CME Globex Reference Guide (PDF)` is discovery
evidence only. Search-engine cached text has no immutable response bytes, resolved media type,
byte count, or acquisition SHA-256 and cannot satisfy the proposal.

## 7. Adjacent Official Advisory Boundary

The official CME notice at:

`https://www.cmegroup.com/notices/reference-data-api/2023/20230202.html`

states that the Reference Data API exchange business date changes from the current exchange
business date to the next exchange business date after `16:00 America/Chicago`. This is useful
corroboration, but it is not accepted as an equivalent replacement for the proposal's required
GC Globex trading-day proposition.

The notice concerns the `exchBusinessDate` API attribute and does not independently prove the
complete GC session-to-trade-date mapping required for the 2024-2025 normalized rows. Treating it
as equivalent without a separate reviewed contract would silently weaken the source boundary.

## 8. Anti-Bypass Decision

The following are explicitly forbidden resolutions:

- guessing additional URL variants until an unreviewed object responds;
- using a non-CME mirror or third-party copy;
- saving a 404, access-denied, authentication, or anti-automation HTML body as a PDF;
- reconstructing the guide from a search excerpt;
- substituting a product page or advisory whose proposition is narrower or different;
- inferring ordinary trade dates solely from observed bars, neighboring rows, or weekdays;
- modifying the proposal after execution to make a failed acquisition appear successful.

## 9. Private Intake Preservation Evidence

The private intake remains at:

`private_data/sierra_chart/gc_calendar_20260804_raw_intake/`

Post-attempt evidence is:

| Artifact | SHA-256 |
|---|---|
| `raw_artifact_manifest.csv` | `684F9EAAEAB41BFC4D09C4E4FE7E4B7672D5B246A3F9F251656A8D07068A0575` |
| `README.md` | `BA537533C46E082144973FC50D2385DB5F3E374B352848BB1F650EEEF1312721` |
| `acquisition_checkpoint_20260808.md` | `8F3BBAFFE2D1A3996E597EE67745B996F5CB1FB07246332F717A067E0A12C6EA` |
| `normalization_audit_checkpoint_20260808.md` | `4BE171CA54A647EAE3DF6BD358F63319AD13AC8E17F66FC3EE0288EB3869E6AF` |
| `normalization_draft.csv` | `A68372E7D556C665F66F0C90700F15BC1AD248A05D23247F27B3F2DF15314884` |

The intake contains zero PDF files. The intended collision-safe target
`CME_Globex_Reference_Guide_20260825.pdf` does not exist. No manifest row, README statement,
checkpoint statement, or normalization row was added.

## 10. Normalization Status

The header-only `normalization_draft.csv` remains non-evidence. No 2024-2025 ordinary session,
holiday session, closed date, split session, or trade-date assignment was newly emitted or
promoted during this attempt.

Existing accepted XLSX and authenticated GCC EML evidence remains immutable. It is necessary but
does not, under the committed proposal, independently clear the missing general trade-date-rule
gate.

## 11. OOS and Contamination Result

The sealed OOS payload was not opened, read, copied, hashed, sampled, inferred from, or used to
repair calendar coverage. No 2026 session data was used to infer a 2024-2025 rule. Prior negative
Phase A/B evidence was not reused as a calendar source.

The failure occurred before any dataset, candidate, feature, label, corpus, training, evaluation,
integration, or trading surface was reached.

## 12. Repository State

At acquisition preflight and post-attempt verification:

- `HEAD` was `0aa93e5cc3e4ef726fbde811fc48e49055157b85`;
- local `origin/main` was `0aa93e5cc3e4ef726fbde811fc48e49055157b85`;
- tracked worktree state was clean;
- the three unrelated pre-existing untracked documents remained unmodified and outside scope.

This decision record does not claim a new live-remote check beyond the verified push completion
audit for the governing proposal.

Fresh cache-disabled regression evidence for this decision is:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_pretraining_corpus.py
66 passed in 0.55s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2519 passed in 23.24s
```

The exact one-file pre-stage and cached formatting checks reported no whitespace error.

## 13. Final Status Precedence

The evidence-resolution attempt is `UNKNOWN`, not `INVALID`: no contradictory accepted artifact
was introduced, but the required artifact bytes remain unavailable. No result is promoted from an
incomplete group.

The governing precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

This `UNKNOWN` blocks normalization and every downstream authority.

## 14. Exact Resume Condition

Work may resume only after one of these separately reviewed conditions is met:

1. CME or GCC supplies the official Reference Guide as immutable bytes or a working exact official
   CME download URL whose PDF body contains the required proposition; or
2. a new documentation-only proposal proves an official CME replacement source is semantically
   equivalent for the exact GC trade-date assignment, locks its immutable acquisition contract,
   and passes independent review before private execution.

A current official page merely mentioning Globex, Trading Hours, or an exchange business date is
not enough by itself.

## 15. Next Bounded Task

The only recommended next task is a read-only/manual-source resolution task:

- request or obtain from CME/GCC the current official artifact or explicit written GC-specific
  statement that the `18:00 America/New_York` open begins the next eligible trade date for the
  exact 2024-2025 scope;
- preserve the response as original bytes;
- do not add it to the private intake until a separately authorized acquisition preflight verifies
  source, media type, scope, and collision-safe destination.

Sending an email, uploading a file, or changing private intake is not authorized by this record.

## 16. Rollback and Stop Conditions

Before commit, rollback is deletion of this one new documentation file. After a local commit,
rollback is a normal forward revert of that exact commit, never a destructive reset.

STOP remains mandatory on unavailable or uncertain official bytes, non-CME resolution, ambiguous
product scope, dependency drift, private-manifest mutation before accepted acquisition, partial
normalization, OOS access, dataset build, feature/label build, training, integration, push, or any
trading authority.

## 17. Final Decision

The official-source search improved the diagnosis but did not clear the evidence gate. The correct
state is:

`CALENDAR_REFERENCE_ARTIFACT_UNAVAILABLE_PRIVATE_INTAKE_IMMUTABLE_NORMALIZATION_NOT_STARTED`.

No downstream work is safe until Section 14 is satisfied.
