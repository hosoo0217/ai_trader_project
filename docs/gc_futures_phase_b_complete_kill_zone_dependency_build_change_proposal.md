# GC Futures Phase B Complete Kill-zone Dependency Build Change Proposal

## 1. Decision metadata

- Decision state: `PROPOSED`.
- Scope class: documentation-only freeze-lift proposal for one private, development-only dependency build.
- Target capability: complete canonical Kill-zone evidence for the already accepted GC Phase A development dataset.
- Governing correction record: `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md` with SHA-256 `FEDBE60FFC5E984692EEDA41BAB5C131377E7578EC7E9EB56063D35B0A80883D`.
- This record is not implementation authority, run authority, training authority, OOS authority, integration authority, staging authority, commit authority, or push authority.
- No later step is implied by acceptance of this proposal.

## 2. Problem statement and accepted evidence

The immutable Candidate Evidence artifact is `UNKNOWN`, not corrupt. It contains canonical Kill-zone output for only `113` of the dataset's `133` canonical segments because the existing Candidate Evidence pipeline correctly stopped when an upstream dependency became `UNKNOWN`. The retained prefix represents `44` trade dates and contains `6,719` Kill-zone contexts, `6,719` snapshots, and `1,556` `NEW_YORK_AM` contexts. The unrepresented suffix contains `20` segments, `5,520` bars, and trade dates from `2026-04-27` through `2026-05-22`.

The accepted dataset itself remains `VALID`: `17,404` bars, `133` canonical segments, `64` distinct requested development trade dates, and date coverage from `2026-02-23` through `2026-05-22`. Phase B private execution remains blocked until a separate dependency artifact accounts for every canonical segment, including explicit `NONE` results.

## 3. Authorized objective and non-authority boundary

The only future operation this proposal may authorize after a separate explicit approval is:

1. read the exact accepted private development bundle;
2. reconstruct its already bound dataset and calendar inputs without modification;
3. invoke the committed public Kill-zone analyzer once for every canonical segment;
4. validate and serialize the complete ordered results twice independently;
5. atomically publish one byte-identical private dependency bundle after all gates pass.

It must not build features or labels, train or evaluate a model, access OOS data, calculate entries/exits/risk/PnL, alter a detector, change Candidate Evidence, integrate with strategy/runtime/execution, use a network service, or place an order.

## 4. Exact accepted private input root and file set

The only allowed input root is:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

The exact eight-file set is locked:

| File | Bytes | SHA-256 |
|---|---:|---|
| `artifact_manifest_DEVELOPMENT_ONLY.json` | 2,337 | `D0774ACB1ECBB1D99F6BCFA4532447859886925D4FB8332BAC67B522BF862B1D` |
| `candidate_evidence_DEVELOPMENT_ONLY.json` | 74,660,911 | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | 2,802,555 | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| `input_binding_DEVELOPMENT_ONLY.json` | 5,179 | `E7982293EDB42CC784B85C5047D06FEC86BCDBB5992C5E847171DD78252A43E4` |
| `normalized_calendar_DEVELOPMENT_ONLY.json` | 4,149 | `CCB8BC4034BBC02922278F560BF1AFAC8282A05D3B26611A7EECF6202686F5FC` |
| `README_DEVELOPMENT_ONLY.md` | 344 | `7260B5DE117EB845758CC908DF5B40AC553AC9F6BBF7535F57A5B6D4733AD559` |
| `structural_seed_DEVELOPMENT_ONLY.json` | 3,080,278 | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |
| `validation_report_DEVELOPMENT_ONLY.md` | 858 | `28AE9108A9A6801FF9634E1FDF95121CADC1AEBA32F9CE225ACC12D15FA15ECB` |

The ordered input artifact-set identity is `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`. Any path, file-set, byte-count, hash, or artifact-set mismatch is a hard `STOP`.

## 5. Immutable dataset binding

The input binding must match all of the following exactly:

- binding version: `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-INPUT-BINDING-V1`;
- dataset ID: `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural-seed ID: `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- continuity artifact-set identity: `5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`;
- instrument/timeframe/tick size: `GC`, `5M`, exact `Decimal("0.1")`;
- contracts: exact set `{GCJ26-COMEX, GCM26-COMEX}`;
- roll trade date: `2026-04-01`;
- dataset status: `VALID`;
- bars/segments/trade dates: `17,404` / `133` / `64`;
- first/last requested development trade date: `2026-02-23` / `2026-05-22`;
- OOS membership and access count: zero.

The builder must not rewrite bar values, indices, timestamps, source IDs, segment boundaries, contract assignments, trade dates, or roll metadata.

## 6. Immutable calendar and timezone binding

The only calendar input is the normalized calendar artifact named in Section 4. Its binding is:

- calendar version: `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`;
- split-session digest: `5f70052e27655a95fdad6aa69f546a6c84a28743bb6635ca4f55d015c39cad6d`;
- Kill-zone digest: `dd16b5734f4dfe54a54c47aa1889302abf92102e6478459b98a8e642732f88f3`;
- exchange timezone: `America/New_York`;
- presentation/source timezone: `Asia/Tokyo` where already bound;
- runtime timezone-data version: exact normalized `2026.2`;
- official evidence hashes: `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`, `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`, and `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

The normalized artifact has `68` entries: `67 OPEN` and `1 SESSION_CLOSED`, from `2026-02-18` through `2026-05-22`. No alternate calendar, live API, inferred holiday list, or later calendar repair may enter this build.

## 7. Committed code and dependency hash binding

The future private build must execute only after `HEAD` contains the accepted corrected Phase B implementation and the following tracked bytes match exactly:

| Path | SHA-256 |
|---|---|
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |
| `analysis/gc_dataset_builder.py` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_candidate_evidence_builder.py` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| `core/gc_chronological_backtest.py` | `07ACAC43DB9D74079F9699EFA60F7E5E4212E2D12AA88D9F14B7B055B165DB6A` |
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `270F9350C1CAAEB69DE87DD1079C876DAF0ADDF00C459F0CDDCE968BF208E39D` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `CAF35F41DBA99D4977A5E6827104A5BB961DA754408FA3CEC8156887AA4713FD` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md` | `A21DA53852CBCC29ED12E5AA36D1D6E4A6C976438CBDC6FEB6C8ECB8639320C4` |

Detector version must be `SMC-V2-KILL-ZONE-1`; timezone constant must be `America/New_York`. A hash/version mismatch requires a new reviewed proposal, not an in-place accommodation.

## 8. Exact public API contract

Only these existing public constructors/functions may define Kill-zone semantics:

```python
KillZoneObservation(index: int, timestamp: datetime, is_closed: bool)

KillZoneCalendarEntry(
    calendar_version: str,
    trade_date: date,
    session_status: KillZoneSessionStatus,
    session_open_timestamp: datetime | None,
    session_close_timestamp: datetime | None,
)

analyze_kill_zones(
    *,
    instrument: str,
    timeframe: str,
    observations: tuple[KillZoneObservation, ...] | None,
    calendar_entries: tuple[KillZoneCalendarEntry, ...] | None,
    calendar_version: str,
    timezone_data_version: str,
) -> KillZoneResult
```

Identity verification may use only the existing keyword-only `make_kill_zone_id()` parameters: `identity_kind`, `instrument`, `timeframe`, `calendar_version`, `timezone_name`, `timezone_data_version`, optional context fields `observation_index`, `observation_timestamp`, `trade_date`, `zone`, `session_status`, `quality`, and optional snapshot fields `effective_index`, `effective_timestamp`, `context_ids` with default `()`.

No private detector helper, copied identity algorithm, signature extension, default change, wrapper-side classification, or reconstructed replacement identity is allowed.

## 9. Exact deserialization and reconstruction boundary

The dataset JSON wrapper must contain `prefix_audit`, `purpose`, and `result`; only its immutable `result` payload is reconstructed through the accepted dataset contract. Each canonical segment must expose `bars`, `contract`, `first_trade_date`, `last_trade_date`, `partition`, `preceding_missing_bar_count`, `segment_id`, and `source_ids`. Each bar must expose `open_tick`, `high_tick`, `low_tick`, `close_tick`, `volume`, `index`, `timestamp`, and `is_closed`.

The normalized calendar contains only `calendar_version`, `trade_date`, and `session_status` evidence for each entry. For an `OPEN` entry, the caller reconstructs the canonical session open as the previous calendar day at `18:00:00 America/New_York` and close as the trade date at `17:00:00 America/New_York`, using runtime tzdata `2026.2`. A `SESSION_CLOSED` entry must reconstruct both timestamps as `None`. The accepted span contains no `EARLY_CLOSE`; one appearing is a binding mismatch and `STOP`, not an inferred timestamp.

All datetime inputs must be timezone-aware and normalized only through the committed public/shared normalization contracts. No bar/calendar evidence may be synthesized to fill a missing record.

## 10. Canonical segment order and observation construction

Canonical segment ordinal is the zero-based position in the immutable `result.segments` tuple. Filesystem order, dictionary order, lexical hash order, or contract-only sorting must not replace it. All `133` segments must be visited in that order.

For each segment, construct exactly:

```python
tuple(
    KillZoneObservation(item.index, item.timestamp, True)
    for item in segment.bars
)
```

Every source bar must already be fully closed. Observation indices and normalized timestamps must be independently strictly increasing inside the segment. Duplicate, reordered, naive, boolean-indexed, or malformed observations block the entire build without publishing a partial final root.

## 11. Exact per-segment calendar slice

For each segment, calendar evidence is the tuple, in canonical calendar order, satisfying:

```python
tuple(
    item
    for item in calendar_entries
    if segment.first_trade_date <= item.trade_date <= segment.last_trade_date
)
```

The slice must not be expanded with neighboring dates, reduced to observed local dates, silently sorted, deduplicated, or repaired. Its ordered trade-date list and canonical content digest are recorded per segment. Any required in-horizon absence remains visible to the public analyzer and may not be masked by wrapper logic.

## 12. Exact per-segment public analyzer invocation

Every segment must use exactly one semantic call:

```python
kill_result = analyze_kill_zones(
    instrument="GC",
    timeframe="5M",
    observations=observations,
    calendar_entries=calendar_slice,
    calendar_version=(
        "GC-2026-DEVELOPMENT-COVERAGE-V1-"
        "355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA"
    ),
    timezone_data_version="2026.2",
)
```

The exact values may be passed from the verified immutable manifest but must equal the literals above. The existing Candidate Evidence builder is not invoked, modified, resumed, or used as a source of missing outputs.

## 13. Complete processing and status gate

The dependency build must process all `133` segments even when a segment produces no context. A segment result is publishable only when its public status is `VALID` or `NONE`. `NONE` is stored explicitly with its exact reasons, blocking reasons, empty/non-empty public tuples as returned, and result digest.

Any `INVALID`, `AMBIGUOUS`, or `UNKNOWN` status, exception, missing segment result, duplicate ordinal/ID, or unexpected enum value blocks final publication. Statuses must never be coerced, downgraded, combined, or replaced with wrapper-specific success. Results computed before a failure may exist only under the temporary root and confer no partial promotion authority.

## 14. Public result and identity reconciliation

The serializer must preserve every public field and original tuple order:

- `KillZoneContext`: `context_id`, `observation_index`, `observation_timestamp`, `trade_date`, `zone`, `session_status`, `quality`, `calendar_version`, `timezone_name`, `timezone_data_version`;
- `KillZoneSnapshot`: `snapshot_id`, `index`, `timestamp`, `context_ids`;
- `KillZoneResult`: `status`, `contexts`, `snapshots`, `reasons`, `blocking_reasons`.

Every `context_id` and `snapshot_id` must be recomputed with the public `make_kill_zone_id()` from the supplied public fields and match exactly. Snapshot `context_ids` must preserve the analyzer's ordered cumulative history within that segment; every referenced context must exist earlier or at that causal point in the same result. Foreign, malformed, duplicate, reordered, or mismatched identities block publication.

## 15. Exact private output roots and preconditions

The only future temporary root is:

`private_data/sierra_chart/.tmp-gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1/`

The only future final root is:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1/`

Before execution, both roots must be absent, the accepted input root must be present and immutable, and the Git worktree must be clean except for already disclosed unrelated state. Existing files must never be overwritten. These private roots remain excluded from Git. Root presence, symlink/reparse ambiguity, path escape, or unexpected files cause `STOP`.

## 16. Exact five-file private output contract

The final root may contain exactly:

1. `kill_zone_dependency_DEVELOPMENT_ONLY.json`;
2. `input_binding_DEVELOPMENT_ONLY.json`;
3. `artifact_manifest_DEVELOPMENT_ONLY.json`;
4. `validation_report_NON_PROMOTABLE_ENGINEERING_PILOT.md`;
5. `README_NON_PROMOTABLE_ENGINEERING_PILOT.md`.

The dependency JSON must contain `schema_version`, `purpose`, immutable `input_binding`, immutable `detector_binding`, ordered `segment_results`, and `summary`. Each segment result must contain exactly `segment_ordinal`, `segment_id`, `contract`, `first_trade_date`, `last_trade_date`, `bar_count`, `observation_digest`, `calendar_entry_trade_dates`, `calendar_slice_digest`, `status`, `reasons`, `blocking_reasons`, `contexts`, `snapshots`, and `result_digest`.

The summary must include exact segment count, requested trade-date count/span, status counts, total context count, total snapshot count, `NEW_YORK_AM` context count, and `complete`. `complete` is true only when all `133` unique ordinals/IDs exist and every status is `VALID` or `NONE`.

## 17. Canonical serialization and artifact identity

JSON uses UTF-8, LF line endings, exactly one final newline, `ensure_ascii=True`, sorted keys, and compact separators `(",", ":")`. Dates use `YYYY-MM-DD`. Datetimes are normalized to UTC and serialized with exactly six fractional digits as `YYYY-MM-DDTHH:MM:SS.ffffffZ`. Enums use `.value`; tuples remain JSON arrays in causal order; booleans remain booleans; no platform path or runtime clock enters semantic JSON.

Per-file SHA-256 values in the manifest are uppercase hexadecimal. The manifest lists the other four output files in the exact order in Section 16 and excludes itself to avoid a circular hash. The lowercase artifact-set identity is SHA-256 over canonical JSON for the ordered array of `{name,bytes,sha256}` records. Result/digest fields are provenance digests only and must never be represented as public Kill-zone identities.

## 18. Two fresh independent executions

The temporary root contains two independently allocated child roots, `run-a` and `run-b`. Each run must reread and revalidate all immutable inputs, reconstruct all objects afresh, call the public analyzer for all `133` segments, and write the exact five-file bundle without reading the other run.

The runs must match byte-for-byte for every file, per-file hash, ordered segment result, summary, and artifact-set identity. A shared in-memory result, copy-before-comparison, cached semantic output, nondeterministic field, or difference of any kind is a hard `STOP`.

## 19. Atomic validation and publication

After run equality, an independent read-back audit must parse both bundles, recalculate every file hash/digest/identity/count, and re-run the public identity checks. Only then may `run-a` be renamed atomically, on the same filesystem, to the exact absent final root. No copy-merge, overwrite, partial file replacement, or best-effort publication is allowed.

If publication cannot be proven atomic, the final root remains absent. `run-b` and the temporary parent remain non-promoted audit evidence until a separately authorized safe cleanup; this proposal does not authorize destructive deletion.

## 20. Immutability, completeness, and prefix boundary

The existing Candidate Evidence artifact and all accepted inputs are read-only and byte-immutable. The complete dependency is a separate artifact; it does not enrich, patch, truncate, or relabel Candidate Evidence. It records every canonical segment, including explicit `NONE`, so downstream work can distinguish absence of context from absence of evidence.

Prefix invariance applies only to a complete immutable input snapshot. Any later bar/calendar append, historical insertion, repair, reorder, timezone-version change, detector-byte change, or identity change creates a different input binding and requires a new versioned proposal/run. The current final root must not be reopened or mutated.

## 21. Exact 48-case audit matrix

1. **Case 1 — Documentation scope:** only this proposal changes before acceptance; no Python, test, fixture, private artifact, or integration mutation.
2. **Case 2 — Eight-file binding:** all exact names, byte counts, hashes, and ordered artifact-set identity match Section 4.
3. **Case 3 — Dataset validity:** wrapper shape, `VALID` status, dataset ID, `17,404` bars, and `133` segments reconcile.
4. **Case 4 — Dataset semantics:** `64` requested dates, exact span, contracts, roll date, timeframe, and tick size reconcile.
5. **Case 5 — OOS exclusion:** no OOS file, row, partition, label, outcome, or access enters the build.
6. **Case 6 — Calendar artifact:** exact calendar file hash, version, entry count, status counts, and date span reconcile.
7. **Case 7 — Official evidence:** all three official evidence hashes and the split/Kill-zone digests match.
8. **Case 8 — Timezone binding:** runtime tzdata is exactly `2026.2` and `America/New_York` is available; otherwise `STOP`.
9. **Case 9 — Code binding:** every tracked dependency hash and detector version/constant in Section 7 matches.
10. **Case 10 — Analyzer signature:** exact keyword-only parameter names, annotations/default boundary, and return type remain unchanged.
11. **Case 11 — Public dataclasses:** exact fields/types and frozen state of observation, calendar, context, snapshot, and result reconcile.
12. **Case 12 — Public vocabulary:** exact zone/session/quality/status enum values, detector version, timezone constant, and exports reconcile.
13. **Case 13 — Dataset reconstruction:** wrapper/result/segment/bar required fields reconstruct without mutation or inferred records.
14. **Case 14 — OPEN reconstruction:** canonical previous-day `18:00` open and trade-date `17:00` close use bound NY timezone/tzdata.
15. **Case 15 — Closed reconstruction:** `SESSION_CLOSED` yields exact `None` open/close; unexpected early-close evidence blocks.
16. **Case 16 — Canonical segment order:** all ordinals/IDs follow immutable tuple position; no silent sort or duplicate exists.
17. **Case 17 — Observation construction:** every bar maps to exact index/timestamp/`True` closed observation with no price-derived mutation.
18. **Case 18 — Observation chronology:** independently strictly increasing indices/timestamps and timezone awareness are enforced.
19. **Case 19 — Calendar slicing:** inclusive segment trade-date bounds, canonical order, date list, and digest match exactly.
20. **Case 20 — Exact call:** instrument, timeframe, observations, calendar slice, versions, and single analyzer invocation match Section 12.
21. **Case 21 — Builder isolation:** Candidate Evidence builder/result is not invoked, resumed, overwritten, or used to fill output.
22. **Case 22 — Complete traversal:** every one of `133` segments is processed even after `NONE`; no early-success stop exists.
23. **Case 23 — VALID retention:** a `VALID` result preserves exact public fields, tuple order, reasons, and digest.
24. **Case 24 — NONE retention:** a `NONE` result is explicitly recorded and counted; it is never omitted or coerced.
25. **Case 25 — INVALID stop:** any public `INVALID` result blocks final publication and cannot promote partial evidence.
26. **Case 26 — AMBIGUOUS stop:** any public `AMBIGUOUS` result blocks publication without arbitrary candidate selection.
27. **Case 27 — UNKNOWN stop:** any public `UNKNOWN` result blocks publication without truncation or relabeling.
28. **Case 28 — Exception containment:** malformed/nested/runtime exceptions fail closed; no final root or partial promotion appears.
29. **Case 29 — Context schema:** every required context field is serialized; extra, missing, malformed, or reordered evidence is rejected.
30. **Case 30 — Snapshot schema:** every required snapshot field and ordered cumulative history is serialized and reconciled.
31. **Case 31 — CONTEXT identity:** every context ID is recomputed through public `make_kill_zone_id()` and exact-matched.
32. **Case 32 — SNAPSHOT identity:** every snapshot ID is recomputed through the public builder with exact ordered context history.
33. **Case 33 — Causal ordering:** result/context/snapshot tuple order is preserved; hash lexical ordering is never a tie-break.
34. **Case 34 — Count reconciliation:** segment/status/context/snapshot/NY-AM totals reconcile from leaf records through summary.
35. **Case 35 — Trade-date coverage:** represented distinct requested dates are exactly all `64` accepted development dates.
36. **Case 36 — Missing-suffix closure:** all formerly unrepresented `20` segments/`5,520` bars are accounted for without special casing.
37. **Case 37 — Prior immutability:** Candidate Evidence and all eight input files remain byte-for-byte unchanged.
38. **Case 38 — Root preconditions:** exact temp/final roots are absent and safe; reparse/path escape/unexpected-root state stops.
39. **Case 39 — Five-file scope:** each run and final publication contain exactly the five allowed files with exact schemas.
40. **Case 40 — Canonical bytes:** UTF-8/LF/final-newline/JSON/date/datetime/enum rules produce platform-independent bytes.
41. **Case 41 — Artifact identity:** all bytes, uppercase hashes, manifest records, and lowercase artifact-set identity recompute.
42. **Case 42 — Independent repeatability:** fresh run A and B reread inputs and match byte-for-byte across all five files.
43. **Case 43 — Nondeterminism rejection:** clock, random, hash seed, dictionary/filesystem order, locale, or cached output cannot affect bytes.
44. **Case 44 — Atomic publish:** complete audit precedes same-filesystem rename; final root is absent on any failure and never overwritten.
45. **Case 45 — Version boundary:** append/repair/reorder/version/hash mutation is ineligible and requires a new proposal/version.
46. **Case 46 — Status integrity:** `INVALID/AMBIGUOUS/UNKNOWN` block; only exact `VALID/NONE` are complete; no wrapper precedence rewrite.
47. **Case 47 — Forbidden surfaces:** zero network, OOS, feature/label, training/model, PnL, integration, execution, Git, or trading access.
48. **Case 48 — STOP boundary:** successful private publication authorizes only a later read-only audit, not Candidate refresh or Phase B run.

## 22. Audit and promotion order

The future authorized build order is immutable:

1. verify clean/disclosed repository state, committed hashes, input bytes, absence/safety of roots, and zero OOS/network access;
2. execute fresh `run-a` and `run-b` independently;
3. validate statuses, all public identities, schemas, ordering, counts, canonical bytes, and artifact identities;
4. prove byte equality of both runs;
5. atomically rename audited `run-a` to the final root;
6. perform a final read-only audit of the published root and unchanged inputs;
7. `STOP`.

Promotion means only publication of this non-promotable engineering dependency artifact. It does not mean research acceptance, Candidate Evidence promotion, strategy acceptance, model training, OOS eligibility, or trading authority.

## 23. Rollback and stop conditions

Before final publication, rollback is the absence of the final root; temporary evidence remains quarantined. After a correct atomic publication, rollback is a new explicit decision that quarantines the entire versioned final root; no file-level edit or replacement is allowed.

Immediate `STOP` conditions include any input/code/hash/version mismatch, non-absent or unsafe root, malformed input, calendar reconstruction uncertainty, public status outside `VALID/NONE`, identity/schema/order/count mismatch, run inequality, nondeterministic byte, filesystem publication uncertainty, OOS/network contact, unrelated write, or request to broaden scope. A stop must report the exact condition without improvising a fix or continuing to another stage.

## 24. Final bounded decision

This proposal locks a single future private operation: build a complete, deterministic, independently repeated, canonical Kill-zone dependency bundle for all `133` accepted GC development segments and `64` requested development trade dates, while preserving the existing Candidate Evidence artifact unchanged.

Documentation acceptance authorizes only exact-path staging, cached-diff audit, and a local documentation commit for this one file. After that local commit, a separately explicit dependency-build run authorization under Sections 3–23 may be considered; it is not implied. After any such run and its independent audit, work must stop. A refreshed Candidate Evidence proposal, refreshed Phase B private-run proposal, training, feature/label work, OOS access, integration, additional commit, push, and trading remain separately frozen.
