# GC Futures Independent Pretraining GCG26 Source Binding and Corrected Corpus Rebuild Change Proposal

## 1. Proposal record

- Proposal ID:
  `GC-INDEPENDENT-PRETRAINING-GCG26-SOURCE-BINDING-CORRECTED-CORPUS-REBUILD-V1`.
- Proposal date: `2026-08-26`.
- Classification: documentation-only private-source binding and corrected-rebuild proposal.
- Repository baseline: `1bf9d1dfac672db3ef87080405c328204bb79f77`.
- Current upstream acquisition status: `PASS`.
- Dataset/corpus status: `NOT_REBUILT`.
- Training readiness: `NOT_READY`.
- Trading authority: `NONE`.
- Final proposal state:
  `GCG26_SOURCE_BINDING_CORRECTED_REBUILD_PROPOSED_NO_BUILD_NO_TRAINING_NO_OOS`.

This proposal binds the accepted GCG26 extended-history acquisition as a second immutable
development source and defines one later, separately authorized, atomic corrected corpus rebuild.
It does not execute that rebuild, access final OOS, build features or labels, train a model,
integrate runtime behavior, or authorize trading.

## 2. Exact documentation-only scope

This task may create, audit, stage, and locally commit only:

`docs/gc_futures_independent_pretraining_gcg26_source_binding_and_corrected_corpus_rebuild_change_proposal.md`

No Python, test, fixture, private artifact, raw intake, manifest, calendar, requirement,
configuration, package export, integration file, or other documentation file may change. These
pre-existing unrelated untracked documentation files remain user-owned and untouched:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`; and
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Remote publication requires separate exact GitHub privacy/export authorization.

## 3. Governing repository baseline

This proposal is bound to:

- `HEAD`: `1bf9d1dfac672db3ef87080405c328204bb79f77`;
- local `origin/main`: `1bf9d1dfac672db3ef87080405c328204bb79f77`;
- subject: `docs: propose GCG26 completed-volume coverage acquisition`; and
- absent private transaction root:
  `private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`.

| Exact tracked dependency | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `analysis/gc_dataset_builder.py` | 109,258 | 2,820 | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `tests/test_gc_dataset_builder.py` | 106,345 | 2,934 | `4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971` |
| `analysis/gc_candidate_evidence_builder.py` | 50,867 | 1,202 | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `tests/test_gc_candidate_evidence_builder.py` | 41,189 | 1,159 | `F5B9F03E8CD4BA049C706619918BE542FEEE8BC27A84B853120A63E1A490D22F` |
| `analysis/gc_feature_label_builder.py` | 71,477 | 1,287 | `7B13C40802BB4FA24063041CA1D32817D3654F0F20A2A1928639F45CC75B3153` |
| `tests/test_gc_feature_label_builder.py` | 81,401 | 2,011 | `EC4CDF9D42489048DC588BA8284CD64DA44B2CA0FFC61353F1ADED5B2BA8A42B` |
| `analysis/gc_pretraining_corpus.py` | 53,683 | 1,069 | `84B56393A2C8406EAFF451E04D685992037D8ED99519CE710954D9C401C0A46B` |
| `tests/test_gc_pretraining_corpus.py` | 14,339 | 342 | `AA758ED9E935947419B46E88808E1E65966FF8C1E1BA13A37505A7D9927C5B36` |

Any dependency, HEAD, or transaction-root drift requires a fresh read-only audit before execution.

## 4. Governing decisions and immutable semantics

This proposal preserves without reinterpretation:

- `docs/gc_futures_independent_pretraining_atomic_upstream_build_change_proposal.md`,
  SHA-256 `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44`;
- `docs/gc_futures_independent_pretraining_source_domain_roll_boundary_correction_change_proposal.md`,
  SHA-256 `C88C3D0A04A9160FD81EC01E8FE6F36595E90307A45000DFE843FB68D191A7DB`;
- `docs/gc_futures_independent_pretraining_gcg26_completed_volume_coverage_acquisition_change_proposal.md`,
  SHA-256 `3579157ED51FF4A6EC9894E4E92A2AA5E31103C84E4D4F84DF7E2C83C6C5E5D5`.

The current dataset builder remains version
`GC-DATASET-BUILDER-V5-CALENDAR-PARTITION`. Its public API, roll rule, calendar rule,
partition rule, identity payloads, and status precedence remain unchanged. This proposal permits
only additional immutable source and coverage objects through the existing API.

## 5. Accepted acquisition PASS evidence

The private acquisition root is:

`private_data/sierra_chart/gc_gcg26_completed_volume_coverage_acquisition_v1/`

Its exact final six-file allowlist and independent audit results are:

| File | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `GCG26_COMEX_5m_extended_history_acquisition_v1.txt` | 2,881,472 | 28,710 | `D2B43A0DCC3FFE996A2DEFEADB98A1FC5971FFBCC1B7FB951AD57A3BB6D2ABF1` |
| `sierra_request_evidence_v1.txt` | 2,684 | 31 | `1075AFB4B7850E0EE97800427E6714C165542349118A7192C13115A5E98E4AA2` |
| `acquisition_binding_v1.json` | 4,039 | 69 | `CA79BD71CF6EB1A5B4FC595B40B5DC7CC1F1F42AB59022E667A070CC02624C5D` |
| `coverage_result_v1.json` | 1,237 | 29 | `AB218D2F2A9BCF58ED90CE73D310C0D53C904A262A8F9811EB28FF1BC4874BA2` |
| `scope_audit_v1.json` | 1,828 | 35 | `D7F3D4427FA7CF9DF0A4F169737169A1C9694242BF6AC6F55D49DCF44406AB85` |
| `two_run_reproducibility_v1.json` | 1,945 | 37 | `0572DD2C07C69A372E99406E9924517FF36055C809A09E32BDFF3E42A1B37480` |

The acquisition status is `PASS`, is private upstream coverage evidence only, and grants no
training or trading authority.

## 6. Exact acquisition provenance and coverage

The raw source is exact `GCG26-COMEX`, COMEX Gold Futures February 2026, five-minute Sierra
Chart historical intraday data with the accepted 13-column schema. It contains `28,709` rows.

- source timezone: `Asia/Tokyo`;
- exchange timezone: `America/New_York`;
- runtime tzdata version: `2026.2`;
- acquisition completion: `2026-08-25T15:30:16.721Z`;
- export capture: `2026-08-25T15:46:44.406Z`;
- first source moment: `2025-07-24T00:10:00Z`;
- last completed bar close: `2026-02-25T11:45:00Z`;
- requested minimum interval:
  `[2025-08-06T22:00:00Z, 2025-08-28T21:00:00Z)`;
- rows inside that minimum interval: `1,585`;
- duplicate, non-increasing, off-grid, price-grid, and volume-conservation failures: `0`; and
- final-OOS payload access count: `0`.

The Sierra request reported request ID `13`, `7,797,596` received intraday records, exact symbol
`GCG26-COMEX`, and successful completion. Request evidence is research provenance; it is not
market-time knowledge and cannot become a feature.

## 7. Corrected blocker diagnosis

The prior fail-closed transaction reported `COMPARABLE_COMPLETED_VOLUME_MISSING` for exactly
15 sessions from trade date `2025-08-07` through `2025-08-27`. In each group, active
`GCZ25-COMEX` had a completed-session integer volume while adjacent `GCG26-COMEX` lacked
covered source rows under the old source boundary.

The accepted acquisition adds `2,278` source rows outside the old source while reproducing all
`26,431` old rows exactly. It therefore supplies the missing upstream observation domain without
changing the completed-volume rule. It does not prove in advance that the corrected dataset,
candidate evidence, labels, or corpus will pass their later gates.

## 8. Existing source registry remains immutable

The later transaction parses these existing development sources as separate immutable exports:

| Contract | Exact source name | Rows | SHA-256 |
| --- | --- | ---: | --- |
| `GCJ25-COMEX` | `GCJ25_COMEX_5m_186d_reacquired_20260804.txt` | 25,126 | `19A05B41A6EA9F9F59F7A6937A38C5EF68C618C4A3BE8727AE702B980BDBD759` |
| `GCM25-COMEX` | `GCM25_COMEX_5m_186d_reacquired_20260804.txt` | 25,712 | `E72DE09B55D46AF2774DE9582FFF457584A298C7725B21339D21ACCC0ED2D12B` |
| `GCQ25-COMEX` | `GCQ25_COMEX_5m_186d_export_20260803.txt` | 26,093 | `1FECFD8C97C6346EEB62BBC302E677FA52C2A3D8F3D40AA5C578E87F1F3B6F23` |
| `GCV25-COMEX` | `GCV25_COMEX_5m_186d_export_20260803.txt` | 23,472 | `B1C3F8691D9256AB02112ACF7FF61D1CD5AD60DEAC60B685F795C0F072DE70D5` |
| `GCZ25-COMEX` | `GCZ25_COMEX_5m_186d_export_20260803.txt` | 29,100 | `7B61056D0CA36DB2FE315D7ECE915E343E40E99A4C148340C980826726C856E6` |
| `GCG26-COMEX` | `GCG26_COMEX_5m_186d_export_20260803.txt` | 26,431 | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| `GCJ26-COMEX` | `GCJ26_COMEX_5m_186d_export_20260803.txt` | parser-verified | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |

`GCV25-COMEX` remains conditional under the unchanged roll rule. The old GCG26 source is not
replaced, overwritten, appended, renamed, or silently repaired.

## 9. New source exact binding

The new file is parsed independently through `parse_sierra_chart_gc_export()` with exactly:

```text
source_name       = GCG26_COMEX_5m_extended_history_acquisition_v1.txt
contract          = GCG26-COMEX
role              = DEVELOPMENT
capture_timestamp = 2026-08-25T15:46:44.406Z
chart_timezone    = Asia/Tokyo
timeframe         = 5m
raw_sha256        = D2B43A0DCC3FFE996A2DEFEADB98A1FC5971FFBCC1B7FB951AD57A3BB6D2ABF1
```

Its canonical SOURCE identity is:

`a0d67cd818fb6a1a8b7a7bcb41375246e98aa104f88a82455775e4fc1794a3a9`.

Any metadata, hash, schema, timezone, timeframe, role, contract, or canonical-identity mismatch is
`INVALID`; it cannot fall back to the old source or infer equivalent evidence.

## 10. New coverage exact binding

The new coverage evidence is bound independently with:

```text
coverage_start_utc          = 2025-07-24T00:10:00Z
coverage_end_utc            = 2026-02-25T11:45:00Z
acquisition_completed_at    = 2026-08-25T15:30:16.721Z
acquisition_evidence_sha256 = 1075AFB4B7850E0EE97800427E6714C165542349118A7192C13115A5E98E4AA2
```

Its canonical COVERAGE identity is:

`170a8cf602de158707993145fe08b459f40b18d60442c736d6f4bbc071710170`.

Coverage end is the exclusive close of the last completed five-minute bar, not the last row's
start. Evidence cannot attest a moment before its first row or after that close.

## 11. Old GCG26 source and coverage identities

The immutable old GCG26 source remains separately represented:

- SOURCE identity:
  `f3d872476ac7fa23fa9aa0bdef6687d90c25715c0e187eb23c6e3ffd0824f809`;
- capture: `2026-08-03T11:29:40.822Z`;
- coverage: `[2025-08-27T00:45:00Z, 2026-02-25T11:45:00Z)`;
- acquisition completion: `2026-08-03T11:27:13.925Z`;
- acquisition evidence SHA-256:
  `19FFA3B0C8459455D6F7D546770E802B5FB902A7C1FCFA47128640F62BE584E0`; and
- COVERAGE identity:
  `005be13680dd29fc55a072db077efa2dcef52cc98cca1a7031cb4ccff7270cd9`.

The transaction must retain both old and new identities in the source/coverage registries. It may
not manufacture a third identity from concatenated bytes.

## 12. Exact overlap reconciliation

The accepted audit found exactly `26,431` overlapping normalized timestamps and `0` mismatches.
The overlap comparison includes normalized timestamp, Open, High, Low, Last, Volume, number of
trades, Bid Volume, and Ask Volume. The new source adds exactly `2,278` distinct earlier rows.

The later builder independently revalidates this equality. Any field mismatch, duplicate conflict,
missing formerly overlapping row, or normalized-time disagreement is `INVALID` and aborts the
entire transaction before promotion. Lexical hash order may not select between conflicting rows.

## 13. Deterministic source and coverage ordering

No silent sorting of caller input is permitted. The exact accepted source tuple order is the
current canonical export order:

`(_contract_key(contract), role.value, source_sha256)`.

For the two GCG26 development sources, the new SHA `D2B4...BF1` sorts before the old SHA
`FA3F...719`; therefore the new source precedes the old source. The exact coverage tuple order is:

`(coverage_start_utc, coverage_end_utc, _contract_key(contract), role.value, coverage_id)`.

The new coverage starts earlier and therefore precedes the old coverage. Direction, filename,
capture time, or hash lexical order cannot substitute for the locked key. Reorder, insertion, or
same-effective repair makes a previous prefix comparison ineligible.

## 14. Completed-volume and source-domain semantics

The existing builder must continue to require completed integer session volume for the active and
adjacent contract on every eligible comparison session. Missing bars are not zero volume. Coverage
is not eligibility, and calendar completeness is not source observation.

The new source may resolve the 15 previously missing adjacent GCG26 completed volumes only from
observed and coverage-attested rows. It cannot alter the prior-completed-session roll rule, invent
an initial-contract bootstrap, silently right-censor the development interval, or promote an
incomplete terminal group. Final status precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

## 15. Calendar and partition locks

The accepted dual calendar, official CME evidence, session normalization, maintenance interval,
holiday/early-close rules, and locked chronological partitions remain byte-immutable. Calendar
coverage and partition eligibility remain separate decisions. This source binding grants no
calendar repair, date shift, session relabel, partition change, OOS movement, or timezone override.

Any newly observed row outside the independently valid session/calendar domain is retained only as
source evidence and handled by existing classification rules; it is not silently forced into a
partition.

## 16. Future private transaction topology

A later explicit private-run authorization may use only:

```text
private_data/sierra_chart/gc_independent_pretraining_corpus_v1/
  .run_a/
    dataset/
    candidate_evidence/
    feature_labels/
    corpus/
  .run_b/
    dataset/
    candidate_evidence/
    feature_labels/
    corpus/
  .accepted_pending/
    dataset/
    candidate_evidence/
    feature_labels/
    corpus/
  accepted/
```

The root must be absent before execution. Run A, Run B, and pending roots are fresh. No earlier
failed output, current private acquisition artifact, or downstream output may be overwritten.
Temporary scripts must be outside the final root and absent after audit.

## 17. Run A exact build order

Run A must follow this exact ordered sequence:

- Step A: verify the tracked baseline and all private input hashes without touching final OOS;
- Step B: parse each immutable source separately, including both GCG26 sources;
- Step C: bind each coverage object separately with the exact identities above;
- Step D: build the dataset through the existing source-domain API;
- Step E: require the dataset acceptance gate before candidate construction;
- Step F: build candidate evidence only from accepted dataset artifacts;
- Step G: require the candidate gate before feature/label construction;
- Step H: build feature/label evidence using the locked `H=12` rule;
- Step I: require the feature/label gate before corpus construction; and
- Step J: construct a non-training-authorized corpus candidate only after every upstream gate
  passes.

Any failed stage atomically prevents that stage and every downstream stage from promotion.

## 18. Run B and two-run reproducibility

Run B begins from a separate clean root and the same immutable inputs. It cannot consume, copy,
repair, or infer from Run A outputs. Run A and Run B must match on ordered canonical objects,
canonical bytes, manifests, status/reasons, source/coverage registries, row counts, roll decisions,
partition membership, candidate objects, label objects, corpus objects, and every SHA-256.

Any nondeterminism, ordering drift, differing source winner, or differing status is `INVALID` and
promotes nothing.

## 19. Exact acceptance gates

Dataset acceptance requires `VALID`, exact source and coverage registries, zero overlap conflict,
zero unowned row, exact volume conservation, no unresolved required calendar/session evidence, no
unresolved comparable completed volume, deterministic rolls, and valid chronological partitions.

Candidate acceptance requires at least `150/50/50` total Train/Validation/Test candidates and at
least `30/10/10` candidates in each direction, with deterministic IDs and no OOS dependency.

Feature/label acceptance requires horizon `H=12`, at least `30/10/10` positive labels and
`30/10/10` negative labels, immutable candidate linkage, exact availability time, and no look-ahead.

Corpus acceptance requires every upstream gate, exact partition lineage, two-run equality, and
explicit flags `training_authorized=False`, `oos_accessed=False`, `integration_authorized=False`,
and `trading_authorized=False`.

## 20. Atomic promotion, prior evidence, and prefix invariance

Only a complete PASS bundle may be copied from Run A to `.accepted_pending` and published by one
same-volume atomic rename to `accepted/`. Partial stage output is never an accepted corpus.

Strictly prior immutable evidence remains byte-for-byte preserved when a determinably later group
fails. The failing group and every later group promote nothing. Unknown effective moment does not
require a trustworthy prefix. A strictly later complete append may be prefix-invariant; a
same-effective append, historical insertion, repair, reorder, source replacement, hash drift,
calendar mutation, or version mutation is not eligible for that claim.

## 21. Inline synthetic exact 48-case verification matrix

1. HEAD, origin/main, subject, and absent transaction root equal Section 3.
2. Exact documentation-only one-file scope holds.
3. All tracked dependency bytes, lines, and hashes reconcile.
4. Governing decision hashes reconcile without semantic override.
5. Private acquisition final scope is exactly the six-file allowlist.
6. Every acquisition artifact byte count, line count, and SHA-256 reconciles.
7. Raw source is exact GCG26-COMEX February 2026 five-minute data.
8. Source/exchange timezone and tzdata version reconcile.
9. Acquisition completion and export capture moments reconcile exactly.
10. Required interval contains exactly 1,585 accepted rows.
11. Raw export contains exactly 28,709 data rows and no malformed conservation evidence.
12. Final-OOS payload access remains exactly zero.
13. Existing seven-source registry remains byte-immutable.
14. New source parses independently with exact metadata and raw hash.
15. New SOURCE identity recomputes to the locked ID.
16. New coverage fields and exclusive end reconcile.
17. New COVERAGE identity recomputes to the locked ID.
18. Old GCG26 SOURCE and COVERAGE identities remain unchanged.
19. Both GCG26 sources coexist; concatenated replacement identity rejects.
20. Overlap count is exactly 26,431 and mismatch count is zero.
21. New distinct earlier-row count is exactly 2,278.
22. Any overlapping economic-field mismatch returns INVALID.
23. Missing overlap member, duplicate conflict, or timestamp disagreement returns INVALID.
24. Canonical export ordering places new GCG26 before old GCG26.
25. Canonical coverage ordering places new GCG26 coverage before old coverage.
26. Caller reorder, silent sort, or hash chronology substitution rejects.
27. Exact 15 prior `COMPARABLE_COMPLETED_VOLUME_MISSING` dates reconcile.
28. New coverage may resolve only observed/attested completed volume.
29. Missing rows never become synthetic zero volume.
30. Active/adjacent completed-volume rule remains unchanged.
31. Calendar coverage and partition eligibility remain separate.
32. Roll, initial-bootstrap, right-censor, and partition semantics remain unchanged.
33. INVALID outranks AMBIGUOUS, UNKNOWN, VALID, and NONE.
34. AMBIGUOUS outranks UNKNOWN, VALID, and NONE.
35. Well-formed unresolved evidence returns UNKNOWN without downstream promotion.
36. Correct source binding does not predetermine dataset PASS.
37. Transaction root must be absent and exact topology must reconcile.
38. Run A executes dataset, candidate, feature/label, and corpus gates in order.
39. Run B is clean and independent of Run A artifacts.
40. Run A and B canonical bytes, identities, counts, rolls, and partitions match.
41. Dataset gate requires no unresolved comparable completed volume.
42. Candidate minimum totals and per-direction thresholds reconcile.
43. H=12 label availability, positive/negative thresholds, and no-look-ahead reconcile.
44. Corpus remains explicitly unauthorized for training, OOS, integration, and trading.
45. Failed stage and every downstream stage promote nothing.
46. Strictly prior immutable evidence survives a determinably later failure byte-for-byte.
47. Same-effective append, repair, reorder, hash/version/calendar mutation are prefix-ineligible.
48. Scope, tests, rollback, privacy, global freeze, and STOP conditions reconcile.

The logical case count is exactly `48`; future parameterized pytest collection may be higher.

## 22. Independent verification and promotion gates

Before local proposal commit, independent audit must verify exactly 24 numbered sections, cases
`1` through `48`, dependency hashes, acquisition hashes, source/coverage identity recomputation,
exact one-file diff, formatting, and unchanged user-owned files. Required cache-disabled tests are:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py tests/test_gc_candidate_evidence_builder.py tests/test_gc_feature_label_builder.py tests/test_gc_pretraining_corpus.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest_tmp_full tests
```

Fresh cache-disabled evidence on `2026-08-26` is:

- focused upstream suite: `428 passed in 2.37s`;
- full repository `tests/` suite: `2527 passed in 38.77s`;
- the workspace-local `.pytest_tmp_full` basetemp was confirmed absent before the run and removed
  after PASS;
- an initial repository-root collection attempt stopped before tests because three ACL-protected
  `private_data` roots could not be scanned, and an initial `tests/` attempt using the host default
  pytest temp root produced setup-only ACL errors; neither attempt exposed a source/test failure or
  accessed the sealed final-OOS payload;
- explicitly selecting `tests/` prevents pytest from treating private evidence roots as test
  packages, while the dedicated workspace-local basetemp removes the unrelated host-temp ACL
  dependency without weakening test selection.

Test PASS authorizes only proposal acceptance; it does not authorize the private transaction.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this proposal. After local commit, rollback
requires a bounded revert, never history rewriting. Documentation promotion requires exact-path
staging, full cached-content review, cached `diff --check`, staged hash audit, and an exact one-file
local commit. Remote publication requires separate exact GitHub privacy/export authorization.

STOP immediately on baseline or dependency drift, unexpected transaction root, private-source
mutation, wrong symbol/timezone/timeframe/role, identity mismatch, overlap conflict, ordering drift,
calendar or partition mutation, unresolved required volume, nondeterminism, unexpected private
file, final-OOS payload contact, look-ahead, feature/label gate bypass, training, integration,
trading dependency, broad staging, or remote push without exact authorization.

## 24. Final bounded decision

The accepted GCG26 acquisition is sufficient to propose deterministic source binding and one
corrected atomic corpus rebuild. The new source extends the old source while preserving every old
overlapping row, and the existing builder can represent both immutable identities without a public
API change.

This documentation task must STOP after independent audit and local commit. The private rebuild,
dataset/candidate/feature/label/corpus promotion, training, final-OOS access, integration, trading,
and remote push remain frozen until separately and exactly authorized.
