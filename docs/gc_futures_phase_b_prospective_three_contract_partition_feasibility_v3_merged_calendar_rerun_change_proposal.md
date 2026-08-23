# GC Futures Phase B Prospective Three-Contract Partition Feasibility V3 Merged-Calendar Rerun Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-B-THREE-CONTRACT-FEASIBILITY-V3-MERGED-CALENDAR-RERUN-PROPOSAL-V1`.
- Classification: documentation-only, bounded, fail-closed private-rerun proposal.
- Decision: `READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_EXPLICIT_V3_PRIVATE_RERUN_AUTHORIZATION`.
- Feasibility status: `UNCHANGED_UNKNOWN`.
- Training readiness: `NOT_READY`.
- Trading authority: `NONE`.
- Current task scope: this one proposal file only.

This record specifies one future V3 private feasibility rerun. It does not execute
that rerun, select a configuration, promote a dataset, inspect OOS, construct
features or labels, train a model, change integration, or authorize a trade.

## 2. Objective and non-objective

The sole objective is to rerun the unchanged prospective three-contract
feasibility question after deterministically combining the accepted ten-row
GCG26-required 2025 calendar with the accepted 99-row 2026 calendar.

The objective is not to force `PASS`, rescue the 27 GCZ25 predecessor-blocked
configurations, add a predecessor source, change dates, tune the hypothesis,
weaken validation, alter the public builder, or reinterpret V2. A separately
authorized run may end `INVALID`, `AMBIGUOUS`, `UNKNOWN`, `PASS`, or `NONE`.

## 3. Repository baseline and exact current scope

The immutable repository baseline is commit
`500ed209baffd2431dd23f314f4dcf651a0d2814`, parent
`7ad605d0f0cd0a9da242a8bbf2627b9a7b2ffa0c`, subject
`docs: record GCG26 calendar resolution PASS`. Local `HEAD`, local
`origin/main`, and live remote `main` were reconciled to that exact commit
before this proposal was created.

This documentation task may create, audit, stage, and locally commit only:

`docs/gc_futures_phase_b_prospective_three_contract_partition_feasibility_v3_merged_calendar_rerun_change_proposal.md`

The three pre-existing unrelated untracked documentation files remain outside
scope and untouched. Source, tests, fixtures, private data, raw acquisition,
calendar evidence, manifests, configuration, requirements, package exports,
integration, models, and training outputs remain frozen.

## 4. Controlling tracked dependencies

| Dependency | SHA-256 |
|---|---|
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| Corrected V2 rerun proposal | `C096248B05B552DB6CF9445F408AB20956798AD406D26F57FD8E0DFF3C92C377` |
| V2 UNKNOWN decision | `4D9CBC66AF764A669DA78F7F63C8F96FC647C85F4163147454A67FD4C11804D9` |
| GCG26 calendar-resolution proposal | `0BC17667041E9D30560795B5FF49168A3BA69A039CD23D5495C0B8F87B2462C9` |
| GCG26 calendar-resolution PASS decision | `C21C593724DBA10E33AF872FC3BC5CE027993DA9161B8D28972BEA8ADA493CAD` |
| Next-hypothesis selection decision | `889CB2DA4FB107AC05A6D9B2395A9FB7E03595C40162339000731B5BAE113AC7` |
| AI strategy training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |
| Split-session calendar checkpoint | `730332BD2CE71BA9E6FEB2DD29F9100CD6125300E3563B700734CEE3F2BC6087` |

Any dependency, API, version, identity, or baseline drift is a STOP requiring a
new reviewed proposal.

## 5. Immutable V2 feasibility evidence

The accepted V2 root remains:

`private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v2/`

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `candidate_configurations.jsonl` | 3,101,510 | `A2CF163A1ADF681B261B13C4CC194E1A18F03FBB6F533E237DC1696DE9288B5C` |
| `feasibility_result.json` | 333 | `B8C26C77E1F3DFC3E47161AB924A4B330E19A171DCE1F903E6993A746B46D368` |
| `input_binding.json` | 6,069 | `E9165216B809BBA0D65010E7927382C62EEADEFF5187198250B593C55D63F03E` |
| `scope_audit.json` | 566 | `3995384742BBD15352D8715D1A5F663FE6A8E04B3775723E4D7A14A9F868B3C5` |
| `two_run_reproducibility.json` | 601 | `2073D81045FCAE4F1F8E2513AFCA695709BCB7BEF43BFE706EB9FD44EFCB5A73` |

V2 is immutable deterministic `UNKNOWN`: 54 ordered candidates, null selection,
promotion `NONE`, training `NOT_READY`, and zero OOS/feature/label/model/training/
integration contact. V3 may cite V2 but may not overwrite, repair, merge, relabel,
or use V2 candidate payloads as market input.

## 6. Immutable calendar-resolution evidence

The accepted calendar-resolution root remains:

`private_data/sierra_chart/gc_phase_b_gcg26_required_2025_calendar_resolution_v1/`

| Artifact | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `calendar_entries.jsonl` | 4,843 | 10 | `9808145FAA305FD7F4FC12ACEC6F4C3802CE7919ABF2801CAC35F0C7EBC26617` |
| `input_binding.json` | 13,619 | 1 | `21DA5F63C0BE1FD392CFB8C52B972CD6F506E96ADF1A2102B6D92442E4513CB8` |
| `resolution_result.json` | 1,422 | 1 | `9B9AE65882B497ACA05645B3FAC2D82198CA89C47BE0B03B3002F247E58E4958` |
| `scope_audit.json` | 597 | 1 | `F060DC41FD1BC08D75C052E7975DA5DEA512D939E7645C92B1C57A855BB7F362` |
| `two_run_reproducibility.json` | 602 | 1 | `1B30BEBFDEF5F5234CB38159DE7080E378AC9E53AD102F6B200AEF3B4EDBE13E` |

Its accepted identity is
`56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`
and its version is
`GC-GCG26-REQUIRED-2025-CALENDAR-V1-56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c`.
The result is calendar-only `PASS`; feasibility remains `UNCHANGED_UNKNOWN`.

## 7. Exact ten-row 2025 calendar boundary

The ordered trade-date tuple is exactly:

`2025-12-17`, `2025-12-18`, `2025-12-19`, `2025-12-22`, `2025-12-23`,
`2025-12-24`, `2025-12-25`, `2025-12-26`, `2025-12-29`, `2025-12-30`.

Eight rows are standard `OPEN`, `2025-12-24` is `EARLY_CLOSE` at 13:45 ET,
and `2025-12-25` is `SESSION_CLOSED`. The `2025-12-26` session opens at
18:00 ET on `2025-12-25`. All row fields, source ID/hash tuples, UTC moments,
ordered row IDs, and original calendar version remain byte-bound to Section 6.

## 8. Exact accepted 2026 calendar boundary

The V2 input binds exactly 99 ordered calendar entries under version:

`GC-2026-PROSPECTIVE-FEASIBILITY-V1-394EB3584F317AC781B87FD0177EF6AE4462B6989DEEF67141D1C6E9AADA3D25`.

The evidence map contains exactly the four accepted CME holiday workbooks and
final CME GCC case `04687271` EML recorded by V2. The 99-row calendar begins at
trade date `2025-12-31`; no trade date overlaps the ten-row tuple. V3 must
reconstruct this input by the same accepted V2 rule and verify its exact version,
entry count, order, row identities, evidence map, and content before union.

## 9. Deterministic merged-calendar construction

The future V3 runner must:

1. validate both accepted component calendars independently;
2. require exact component identities, versions, counts, order, and hashes;
3. require disjoint trade-date sets and strict adjacency from `2025-12-30` to
   the 99-row calendar's first date `2025-12-31`;
4. concatenate by increasing trade date without sorting either component;
5. preserve every status, interval, and source ID/hash tuple exactly; and
6. reject any overlap, gap at the join, duplicate, reorder, mutation, or
   calendar-coverage expansion as `INVALID`.

The merged entry count is exactly 109. It is an ephemeral derived builder input,
not a new authoritative calendar source and not a mutation of either accepted
component.

## 10. Exact merged calendar identity and version

The V3 runner must create a common derived `calendar_version` because the public
builder rejects mixed calendar versions. The merged identity is lowercase
SHA-256 of UTF-8 canonical JSON with sorted keys, separators `,` and `:`, ASCII
escaping enabled, and this exact object shape:

```json
{"component_calendar_identities":["56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c","394eb3584f317ac781b87fd0177ef6ae4462b6989deef67141d1c6e9aada3d25"],"component_calendar_versions":["GC-GCG26-REQUIRED-2025-CALENDAR-V1-56d4a0f103ac57d6b4c50e60d0779925fa963e6d6f462ec5c4760d2beb67af0c","GC-2026-PROSPECTIVE-FEASIBILITY-V1-394EB3584F317AC781B87FD0177EF6AE4462B6989DEEF67141D1C6E9AADA3D25"],"entry_count":109,"schema_version":"GC-PHASE-B-MERGED-CALENDAR-V1"}
```

The exact derived identity is
`dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f` and the
common version is
`GC-PHASE-B-MERGED-CALENDAR-V1-dafe7652c8c5de365f6bfe1c3da4c4272d02e1b0beccb0a83833299d2b3f375f`.
Only the ephemeral copies passed to the builder receive this common version;
all other fields remain exact. Run A and run B must independently reproduce
this exact identity and version.

## 11. Immutable source and OOS boundary

The five canonical sources and accepted full-source hashes remain exactly those
bound in V2, in delivery order: GCZ25, GCG26, GCJ26, GCM26, GCQ26. Intake
manifest SHA-256 remains
`AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164`.

The frozen OOS file is identity-only: expected name
`GCQ26_COMEX_5m_30d_export_20260803.txt`, SHA-256
`15E2B3CB47E96988A1A623712E3347438E47B19D8D154D213AECC81C52A50111`.
Its payload must not be opened, read, hashed again, parsed, copied, sampled, or
contacted. V3 must record zero OOS and post-cutoff calculation contact.

## 12. Unchanged parsing, cutoff, and public builder boundary

The source timezone remains `Asia/Tokyo`, exchange timezone
`America/New_York`, runtime tzdata `2026.2`, structural parser rule
`SIERRA-ASCII-Y-M-D-STRUCTURAL-DATE-V2`, coarse JST bounds
`2025-12-17..2026-05-23`, and normalized New York cutoff `2026-05-22`.

The only public call remains:

```python
build_gc_futures_dataset(
    *,
    exports,
    coverage_evidence,
    calendar_entries,
    config,
)
```

Builder version remains `GC-DATASET-BUILDER-V3-SPLIT-SESSION`. No public
source, test, signature, dataclass, constant, identity, or behavior change is
authorized.

## 13. Unchanged feasibility question

V3 asks exactly:

> Does one deterministic configuration exist, using only the locked evidence,
> that yields a `VALID` public builder result ending `2026-05-22`, contains at
> least three canonical delivery-contract segment values, and gives every
> counted contract at least ten complete eligible trade dates without OOS
> contact?

Warm-up starts `2025-12-17`; initial dates are the same 27 eligible dates from
`2025-12-22` through `2026-01-30`; every result ends `2026-05-22`.

## 14. Exact candidate matrix and anti-rescue rule

The matrix remains exactly 54 candidates: 27 `GCZ25-COMEX` and 27
`GCG26-COMEX`, ordered by increasing initial trade date then canonical delivery
order. Candidate IDs and configuration payloads must equal a fresh derivation
under the unchanged proposal, not be copied from V2.

The 27 GCZ25 candidates remain terminal `UNKNOWN` with exact reason
`INITIAL_PREDECESSOR_COVERAGE_MISSING`. V3 must preserve them and must not add,
infer, substitute, or synthesize predecessor coverage. Only the 27 GCG26
candidates are eligible for fresh builder evaluation with the merged calendar.

## 15. Roll, selection, and coverage invariants

Roll policy remains `PRIOR_SESSION_VOLUME_DOMINANCE_3`: completed prior-session
integer volume, adjacent deliveries, three strict consecutive eligible-session
confirmations, reset on non-dominance, no reset on closed dates, next-eligible-
session effectiveness, and monotonic non-reversing unadjusted segments.

Every counted contract needs at least ten complete eligible emitted trade dates.
At the earliest initial date with valid configurations, exactly one byte-distinct
configuration may be selected; multiple distinct valid configurations are
`AMBIGUOUS`. Later dates cannot rescue or outrank the earliest date.

## 16. Exact status precedence and result truthfulness

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

`PASS` requires one exact valid selected configuration, at least three distinct
monotonic canonical segment contracts, at least ten complete eligible dates per
counted contract, full source/calendar/coverage/roll reconciliation, two-run
byte equality, and zero forbidden contact. Blocked proof is `UNKNOWN`; malformed
or contradictory evidence is `INVALID`; no valid configuration is `NONE`.

V3 must report actual results. The calendar resolution removes one known proof
blocker but is not evidence that any GCG26 candidate will pass. A different
`UNKNOWN`, `INVALID`, `AMBIGUOUS`, or `NONE` result is legitimate and must not be
rescued.

## 17. Exact V3 private roots and artifact scope

A separately authorized run must use only:

- run A: `private_data/sierra_chart/.tmp-gc_phase_b_three_contract_partition_feasibility_v3-run-a/`;
- run B: `private_data/sierra_chart/.tmp-gc_phase_b_three_contract_partition_feasibility_v3-run-b/`;
- final: `private_data/sierra_chart/gc_phase_b_three_contract_partition_feasibility_v3/`.

All must be absent before execution. Each temporary root and the final root may
contain only:

- `input_binding.json`;
- `candidate_configurations.jsonl`;
- `feasibility_result.json`;
- `scope_audit.json`; and
- `two_run_reproducibility.json`.

No source copy, canonical bar, calendar export, candidate setup, feature, label,
model input, outcome, PnL, chart, screenshot, log, or OOS content may remain.

## 18. Exact V3 input-binding requirements

`input_binding.json` must bind the V3 schema/proposal ID and SHA-256, execution
baseline, builder hash/version, V2 decision and five artifacts, calendar PASS
decision and five artifacts, five canonical sources, intake manifest, OOS
identity-only tuple, timezone values, parser rule, search/cutoff bounds, candidate
matrix definition, both component calendars, and the derived merged identity.

It must record component entry counts `10` and `99`, merged count `109`, exact
trade-date join, zero overlaps, common derived version, exact provenance rule,
and the fact that no component row other than ephemeral `calendar_version` was
changed. No field may claim feasibility PASS before result computation.

## 19. Atomic execution and chronological cutoff

Every source, proposal, hash, V2 artifact, calendar artifact, and root absence
must validate before candidate processing. A determinably malformed later
candidate makes the final status `INVALID` under precedence while preserving
strictly prior completed diagnostic records byte-for-byte. The failing candidate
and all later candidates promote nothing.

Candidate groups are processed atomically in canonical order. No partial dataset,
segment, candidate selection, or final result may be promoted from an incomplete,
ambiguous, unknown, or invalid group.

## 20. Two-run reproducibility and publication

Run A and run B are fresh independent reconstructions. The four core artifacts
must be object-, ordered-record-, identity-, and byte-equal. Each root must pass
the exact allowed-file and scope audit before publication.

Only after full equality may run A be atomically renamed to the absent final V3
root. Run B must then be deleted after its resolved path is verified. Any
pre-existing root, cleanup uncertainty, hash drift, nondeterminism, output escape,
or partial publication is a STOP without overwrite.

## 21. Prefix invariance and immutable evidence

Strictly later complete source/calendar evidence after `2026-05-22` must not
change any V3 candidate diagnostic, identity, selection, or final result.
Same-effective append, historical insertion, calendar repair, component reorder,
version mutation, source replacement, parser change, or roll-rule change is not a
prefix comparison and requires a new proposal.

V1, V2, and the calendar-resolution root remain separate immutable provenance
layers. V3 may cite them but may not rewrite or merge their stored artifacts.
GCZ25 predecessor `UNKNOWN` evidence is immutable and cannot be relabeled by the
GCG26 calendar correction.

## 22. Exact 48-case future acceptance matrix

1. Baseline commit, parent, subject, and all tracked dependency hashes reconcile.
2. Exact V2 five-file artifact set, bytes, hashes, and deterministic UNKNOWN reconcile.
3. Exact calendar-resolution five-file set, bytes, hashes, and calendar-only PASS reconcile.
4. V1, V2, and calendar-resolution roots remain immutable and separate.
5. Exact five canonical raw-source identities and intake manifest reconcile.
6. Frozen OOS identity is compared without payload contact.
7. Timezones, tzdata `2026.2`, parser rule, coarse bounds, and cutoff reconcile.
8. Public builder version, keyword-only API, config, constants, and identities do not drift.
9. Ten-row 2025 component has exact accepted identity, version, dates, order, and rows.
10. Ninety-nine-row 2026 component has exact accepted identity, version, order, and evidence.
11. Component trade-date sets are disjoint and the join is exact `2025-12-30`/`2025-12-31`.
12. Overlap, duplicate, gap at the join, reorder, or component mutation rejects INVALID.
13. Merged calendar has exactly 109 increasing trade-date rows.
14. Merged identity uses the exact canonical JSON schema and serialization rule.
15. Common derived version embeds the merged identity exactly.
16. Only ephemeral builder-entry calendar versions change; all other row fields remain exact.
17. Mixed component versions are never passed directly to the public builder.
18. Run A and run B independently derive the same merged identity and entries.
19. Warm-up, candidate start/end range, and result end remain unchanged.
20. Exact 54-candidate matrix and canonical order reconcile.
21. All 27 GCZ25 candidates remain UNKNOWN for predecessor coverage.
22. No predecessor source is added, inferred, substituted, or synthesized.
23. Only the 27 GCG26 candidates receive fresh merged-calendar evaluation.
24. Candidate IDs/configurations are freshly derived, never copied from V2 output.
25. Roll uses adjacent completed-session volume and three strict confirmations.
26. Closed dates neither increment nor reset; roll is next-eligible-session effective.
27. Segments remain monotonic, adjacent, non-reversing, and unadjusted.
28. Every counted contract requires ten complete eligible emitted trade dates.
29. Earliest-date deterministic selection and ambiguity rules remain unchanged.
30. Later dates cannot rescue or outrank the earliest valid date.
31. Calendar resolution is not relabeled as feasibility or dataset PASS.
32. Actual V3 candidate and final statuses are reported without rescue.
33. Precedence is INVALID over AMBIGUOUS over UNKNOWN over PASS over NONE.
34. PASS satisfies every exact segment, coverage, identity, and reproducibility gate.
35. Blocked proof remains UNKNOWN and no valid configuration remains NONE.
36. Malformed or contradictory evidence is INVALID without exception leakage.
37. Candidate processing is same-order atomic with no failing-group promotion.
38. Strictly prior completed diagnostics remain byte-for-byte immutable.
39. Strictly later complete evidence preserves the exact V3 prefix.
40. Historical insertion, repair, reorder, replacement, or version mutation is ineligible.
41. Temporary run roots are absent before execution and exact-path bounded.
42. Each run and final root contains exactly five allowed artifacts.
43. Core artifacts are object-, order-, identity-, and byte-equal across two fresh runs.
44. Atomic promotion occurs only after equality, scope, and hash checks pass.
45. OOS, post-cutoff calculation, feature, label, model, training, integration, and trading counts are zero.
46. A V3 PASS authorizes only a later documentation decision, not dataset or training promotion.
47. Any non-PASS terminal result remains preserved honestly with null/none authority as applicable.
48. Exact scope, regressions, rollback, promotion, and STOP conditions reconcile.

## 23. Audit, rollback, promotion, and STOP conditions

Independent acceptance must reconcile all 24 sections, all 48 sequential cases,
dependency hashes, component and private artifact hashes, exact one-file Git diff,
clean formatting, absent V3 roots, and unchanged unrelated state.

Regression evidence will be recorded after this proposal is created:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
245 passed in 1.04s

.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 24.02s
```

Local promotion requires exact-path staging, full cached-content equality review,
cached `diff --check`, SHA-256 audit, commit preflight, and exact one-file local
commit. Push and the private V3 execution each require their own later explicit
authorization. Rollback is deletion before commit or bounded revert after commit;
history rewriting and private-evidence deletion are forbidden.

STOP on baseline, dependency, source, V2, calendar, identity, count, order, API,
timezone, parser, cutoff, candidate, roll, status, test, or Git-scope drift; any
pre-existing V3 root; nondeterminism; cleanup uncertainty; output escape; inferred
calendar facts; predecessor rescue; OOS access; feature/label/model/training work;
integration; execution/trading authority; or remote push without exact authorization.

## 24. Final bounded proposal decision

This documentation proposal is ready for independent audit. It reserves one
future atomic V3 private rerun using the exact merged-calendar construction and
unchanged feasibility question above. It grants no private execution authority by
itself and makes no claim that the result will pass.

After independent audit and an exact one-file local commit, work must STOP before
push and before private execution. The next single task is push preflight and
publication of this proposal under separate GitHub privacy/export authorization.
Training, OOS, feature/label build, integration, paper trading, and live trading
remain prohibited.
