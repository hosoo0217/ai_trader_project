# GC Futures 2026 Pilot Dataset Change Proposal

## 1. Proposal Record

- Proposal type: documentation-only bounded change proposal.
- Decision date: 2026-08-05.
- Status: `READY_FOR_INDEPENDENT_AUDIT`.
- Purpose: authorize a non-promotable 2026 engineering pilot while preserving an explicit unresolved-historical-calendar quarantine for the final 2024–2025-inclusive dataset and every training promotion.
- This record does not claim that a dataset has been built, validated, trained on, staged, committed, pushed, or integrated.

## 2. Selected Decision

The selected decision is to continue only a bounded 2026 pilot dataset path using the accepted raw Sierra Chart acquisition evidence and the acquired 2026 CME holiday workbooks. The pilot exists to exercise parsing, provenance, standard-session calendar construction, initial-contract selection, deterministic assembly, and validation reporting.

The pilot is an engineering artifact. It is not the final research dataset, an out-of-sample result, strategy evidence, model-training evidence, or a promotion candidate.

## 3. Exact Documentation-Only Scope

This proposal changes only:

- `docs/gc_futures_2026_pilot_dataset_change_proposal.md`

No Python, test, fixture, raw intake, derived dataset, manifest, calendar normalization, training artifact, package export, configuration, integration, Git index, commit, or remote state is changed by this proposal.

The existing untracked documents `docs/gc_futures_real_data_input_binding_change_proposal.md` and `docs/smc_v2_diagnostic_context_integration_change_proposal.md` remain untouched.

## 4. Global Freeze and Final-Dataset Gate

The global code freeze remains active outside a separately approved exact scope.

CME case `04687271` has supplied historical COMEX Gold calendar evidence and a clarification response, and both have been independently reviewed. Receipt and review do not lift the final-dataset gate because the supplied statements do not fully reconcile these exact start-inclusive/end-exclusive intervals:

- `[2024-11-27 18:00 America/New_York, 2024-12-01 18:00 America/New_York)`;
- `[2025-11-26 18:00 America/New_York, 2025-11-30 18:00 America/New_York)`.

The following remain blocked until both intervals are reconciled by internally consistent authoritative evidence and a later formal decision explicitly lifts this quarantine:

- any final dataset spanning any part of 2024 or 2025;
- any training, fine-tuning, model fitting, feature selection, threshold selection, or hyperparameter search using the acquired market data;
- any OOS evaluation, strategy promotion, execution integration, or profitability claim;
- any replacement of the preserved failed-OOS evidence;
- any claim that the currently acquired 2026 calendar files establish historical calendar truth for 2024–2025.

## 5. Pilot Evidence Classification

The pilot calendar has two evidence classes and they must never be conflated:

1. `AUTHORITATIVE_SPECIAL_SESSION_BOUNDARY`: exact information read from acquired official CME 2026 holiday workbooks.
2. `DERIVED_STANDARD_SESSION`: an ordinary Monday–Friday session instantiated from the already locked GC rule, prior New York calendar day 18:00 inclusive through trade date 17:00 exclusive in `America/New_York`.

Every pilot output and checkpoint must state `NON_PROMOTABLE_ENGINEERING_PILOT`. Derived standard-session entries are sufficient only for the bounded pilot window and are not a substitute for fully reconciled historical 2024–2025 calendar evidence. Receipt of a response alone does not lift the quarantine in Section 4.

## 6. Accepted Raw Market Sources

Only the following canonical full-contract artifacts are eligible for the Phase-A pilot input derivation:

| Contract | Canonical artifact SHA-256 | Canonical rows | Role |
|---|---|---:|---|
| GCG26 | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` | 26,431 | initial-predecessor evidence |
| GCJ26 | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` | 25,470 | selected pilot contract |
| GCM26 | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` | 27,369 | adjacent-contract roll evidence |

The two superseded raw exports, the diagnostic-only GCV25 selection, all other contract files, and the frozen GCQ26 OOS artifact are forbidden in Phase A.

Every bounded derivative produced from these three artifacts has exact `GCSourceRole.DEVELOPMENT`. The descriptive roles in the table explain contract purpose only; they do not replace the public source-role enum.

## 7. Accepted Official Calendar Artifacts

The pilot boundary is supported by exactly these accepted official CME artifacts:

| Evidence | SHA-256 | Use |
|---|---|---|
| 2026 Presidents Day schedule | `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11` | prove that the pilot starts after the February special-session group |
| 2026 Good Friday schedule | `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7` | prove the later special-session boundary and prohibit accidental extension into it |

The official workbooks remain immutable private evidence. The pilot must not rewrite or normalize them in place.

## 8. Exact Phase-A Calendar Window

Calendar-support window:

- first trade date: `2026-02-18`;
- last trade date: `2026-03-30`;
- exactly 29 Monday–Friday trade dates;
- no weekend entry;
- no holiday, split, early-close, or session-closed date inside the window.

Every one of these 29 entries is `DERIVED_STANDARD_SESSION` using the exact America/New_York standard bounds. The first three dates exist solely to prove the initial-contract selection and are excluded from dataset output.

## 9. Exact Phase-A Dataset Window

The Phase-A dataset window is:

- first eligible output trade date: `2026-02-23`;
- last eligible output trade date: `2026-03-30`;
- exactly 26 ordinary Monday–Friday trade dates;
- selected canonical builder contract: `GCJ26-COMEX` only;
- partition: development engineering pilot only;
- OOS rows: exactly zero.

No bar before `2026-02-23` or after `2026-03-30` may be promoted into a pilot segment.

## 10. Calendar Version and Deterministic Digest

The exact canonical calendar-evidence payload is:

```json
{"artifacts":[["CME_HOLIDAY_PRESIDENTS_DAY_2026_20260804","233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11"],["CME_HOLIDAY_GOOD_FRIDAY_2026_20260804","CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7"]],"normal_session_rule":["America/New_York","D-1T18:00:00","DT17:00:00","start-inclusive","end-exclusive"],"pilot_trade_date_range":["2026-02-23","2026-03-30"],"purpose":"NON_PROMOTABLE_ENGINEERING_PILOT","schema":"GC-2026-PILOT-CALENDAR-V1","window":["2026-02-18","2026-03-30"]}
```

Its UTF-8 SHA-256 is `ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`.

The proposed pilot-only calendar version is `GC-2026-PILOT-V1-ACE75CFEC60473FCA13CB681C588B5DDE268E691EF37ACC4BE66208C4C470345`. This name must never be represented as an authoritative full-history calendar version.

## 11. Timezone and Bar Boundary Contract

- Raw chart timezone: exact `Asia/Tokyo`.
- Exchange timezone: exact IANA `America/New_York`.
- Runtime timezone-data version: exact installed runtime version, expected `2026.2`; mismatch or unavailability is fail-closed.
- Timeframe: exact `5M`.
- Tick size: exact Decimal `0.1`.
- Each raw timestamp is a bar-start timestamp; the immutable bar-close moment is start plus five minutes.
- Session membership is checked in UTC after database-backed timezone conversion.
- Start is inclusive and end is exclusive at the session definition; the builder's closed-bar boundary validation remains authoritative.

## 12. Initial-Contract Proof

Canonical builder contract `GCJ26-COMEX` is eligible to become the initial contract on `2026-02-23` only because it strictly exceeds predecessor `GCG26-COMEX` completed-session volume on all three immediately preceding eligible trade dates:

| Trade date | GCG26 volume | GCJ26 volume | Result |
|---|---:|---:|---|
| 2026-02-18 | 53 | 89,152 | GCJ26 strictly greater |
| 2026-02-19 | 6 | 80,714 | GCJ26 strictly greater |
| 2026-02-20 | 82 | 122,265 | GCJ26 strictly greater |

Missing, incomplete, contradictory, or non-consecutive proof is `UNKNOWN` or `INVALID` under the existing builder contract and stops the pilot.

## 13. Adjacent-Contract Evidence and Phase-A Stop

GCM26 remains present only as adjacent-contract volume evidence. The pilot intentionally stops on `2026-03-30`, after two consecutive observed GCM26 dominance sessions but before a three-session confirmation can schedule a roll:

| Trade date | GCJ26 volume | GCM26 volume | Consecutive dominance count |
|---|---:|---:|---:|
| 2026-03-27 | 21,186 | 149,437 | 1 |
| 2026-03-30 | 3,547 | 145,613 | 2 |

The observed `2026-03-31` third dominance and the potential `2026-04-01` effective roll are deliberately outside Phase A. They require a separate Phase-B proposal because the existing builder then requires comparable GCQ26 adjacent-contract coverage that is unavailable for that moment. Phase A must not hide that `UNKNOWN` by weakening the builder.

## 14. Existing Builder Compatibility Boundary

The current public builder, exact version `GC-DATASET-BUILDER-V2`, is retained unchanged. It:

- validates every supplied parsed row against supplied calendar coverage before applying dataset bounds;
- requires exact source-role coverage;
- requires predecessor evidence for initial selection;
- requires adjacent-contract completed volume throughout the active range;
- partitions dates at the configured OOS boundary;
- fails closed when calendar or adjacent-contract coverage is absent.

Therefore full raw exports may not be handed directly to the Phase-A build with only the 29-entry pilot calendar. Doing so would correctly emit missing-calendar findings for out-of-window rows.

## 15. Deterministic Bounded-Derivative Input Contract

Before any builder call, a future approved private pilot step must create deterministic bounded derivative bytes for GCG26, GCJ26, and GCM26:

- retain the exact original 13-column header;
- bind their public `contract` fields respectively to exact `GCG26-COMEX`, `GCJ26-COMEX`, and `GCM26-COMEX`; bare delivery tokens are descriptive source labels only and are invalid public builder contract values;
- retain only rows whose normalized New York trade date is between `2026-02-18` and `2026-03-30`, inclusive;
- preserve original row text, field order, and chronological order byte-for-byte apart from the removed out-of-window lines;
- do not aggregate, interpolate, forward-fill, sort, repair, relabel, or change prices or volumes;
- do not create a synthetic zero-volume or no-data bar for a five-minute slot in which the parent acquisition contains no trade record;
- bind each derivative hash to its parent canonical artifact hash, exact predicate, source row-number range, retained-row count, byte count, and derivation-tool hash;
- parse the derivative bytes through the existing public `parse_sierra_chart_gc_export()` API.

An ad hoc unrecorded slice is forbidden. A derivative that cannot be independently reproduced exactly is invalid and cannot reach the builder.

## 16. Proposed Phase-A Build Configuration

The exact proposed configuration is:

| Field | Value |
|---|---|
| instrument | `GC` |
| timeframe | `5M` |
| source_timezone | `Asia/Tokyo` |
| exchange_timezone | `America/New_York` |
| timezone_data_version | exact runtime version, expected `2026.2` |
| tick_size | Decimal `0.1` |
| initial_contract | `GCJ26-COMEX` |
| initial_trade_date | `2026-02-23` |
| roll_confirmation_sessions | `3` |
| oos_start_trade_date | `2026-03-31` |
| oos_end_trade_date | `2026-03-31` |

The pilot calendar ends on `2026-03-30`, so the configured OOS sentinel contains no calendar entry and no row. A public-API test must prove that this exact zero-OOS engineering configuration remains `VALID`; otherwise implementation stops and returns to proposal review.

## 17. Coverage Evidence Contract

Each bounded derivative requires new immutable coverage evidence that:

- references the derivative source ID and derivative SHA-256, not only its parent;
- records exact observed first-bar start and last-bar close timestamps in its private provenance sidecar;
- records the original acquisition completion and capture timestamps;
- proves acquisition completed after every retained bar close;
- carries a sidecar provenance link to the parent raw artifact and acquisition checkpoint;
- uses the public `GCSierraChartCoverageEvidence.coverage_start_timestamp` and `coverage_end_timestamp` only for an interval whose market-data availability is established by the immutable parent acquisition evidence.

The default rule is exact observed-bar coverage: public coverage start equals the first retained bar start, and public coverage end equals the last retained bar close. A leading or trailing interval containing no parent price row may extend the public coverage interval beyond those observed bounds only when every condition below is true:

1. the interval lies wholly inside an exact `DERIVED_STANDARD_SESSION` that is already inside the bounded derivative predicate window;
2. the canonical parent raw artifact contains zero rows in the interval, and the derivative contains every parent row selected by the locked predicate;
3. the immutable Sierra acquisition message log proves that the historical request covered the interval and completed before export;
4. the interval remains inside both the exact server-reported acquisition range and the declared session bounds;
5. the private sidecar labels it `ACQUISITION_ATTESTED_NO_TRADE_INTERVAL` and records the contract, trade date, start-inclusive/end-exclusive bounds, parent filename and SHA-256, acquisition-log filename and SHA-256, historical-request ID, server-reported range, download-completion moment, export-completion moment, observed first-bar start, and observed last-bar close;
6. no bar, volume, trade, price, or timestamp is synthesized, inferred, or inserted.

Phase A authorizes exactly one such interval:

| Contract | Trade date | Attested interval (UTC) | America/New_York interval | Exact evidence |
|---|---|---|---|---|
| `GCG26-COMEX` | `2026-02-18` | `[2026-02-17T23:00:00Z, 2026-02-17T23:20:00Z)` | `[2026-02-17 18:00, 2026-02-17 18:20)` | parent `GCG26_COMEX_5m_186d_export_20260803.txt` SHA-256 `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719`; message log `Sierra_Message_Log_20260803_full.txt` SHA-256 `19FFA3B0C8459455D6F7D546770E802B5FB902A7C1FCFA47128640F62BE584E0`; HD Request `13`, server-reported range `2025-08-27 09:45:19.094000` through `2026-02-25 20:41:04.199000`, completed `2026-08-03 20:27:13.925`, export completed `2026-08-03 20:29:40.822` |

The exact server-reported range, download-completion moment, and export-completion moment in the table are interpreted in the acquisition's locked `Asia/Tokyo` chart/host timezone; public coverage bounds are timezone-aware UTC values with the equivalent America/New_York interval shown separately.

For that derivative only, public coverage start is `2026-02-17T23:00:00Z` while observed first-bar start remains `2026-02-17T23:20:00Z`. The observed last bar starts `2026-02-25T11:40:00Z`, so public coverage end and observed last-bar close both remain `2026-02-25T11:45:00Z`. This interval is an acquisition-proven absence of trade rows, not a price bar and not evidence of a historical point-in-time decision feed. No other observed-bound expansion is authorized by this proposal. Naturally empty slots between observed first and last bars remain subject to exact parent-row absence and acquisition/session/predicate containment checks, but they are not additional observed-bound expansion exceptions.

Coverage mismatch, dangling source ID, timestamp inconsistency, a parent row inside an attested no-trade interval, an interval outside the exact acquisition/session/predicate intersection, or any observed-bound expansion other than the single interval above is `INVALID`.

## 18. Atomicity, Status Precedence, and Prior Evidence

The existing fail-closed precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

No manifest or dataset ID is promoted when blocking findings exist. A determinably later malformed group may preserve strictly prior immutable segments only under the existing chronological-cutoff contract. A failing group and everything after it must not be promoted.

## 19. No-Look-Ahead and Acquisition-Time Limits

- Calendar, source, and roll evidence are evaluated only at their locked effective moments.
- The selected contract for a trade date may use only completed sessions strictly before that trade date.
- The `2026-03-31` third dominance must not influence any Phase-A contract choice because it is outside the pilot window.
- Post-hoc acquisition is disclosed. This pilot can test deterministic mechanics but cannot prove historical point-in-time availability for model evaluation.
- `ACQUISITION_ATTESTED_NO_TRADE_INTERVAL` proves only that the completed parent acquisition contained no trade row in the declared slot; it does not convert post-hoc acquisition into point-in-time evidence and cannot be used as a feature or signal.
- No future bar, outcome, entry, exit, PnL, or frozen OOS observation may influence slicing, validation, or selection.

## 20. Output Classification and Private Location

All future outputs remain under a private, Git-excluded intake/build directory. The exact future private root is reserved as:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

It may contain only immutable derivative inputs, provenance sidecars, a build manifest, a validation report, and a README. No output is copied into tracked fixtures, training directories, model artifacts, or integration paths.

Every output filename and manifest must include `NON_PROMOTABLE_ENGINEERING_PILOT` or an equivalent locked machine-readable purpose field.

## 21. Exact Future First Execution Scope

After this proposal passes independent audit and receives explicit execution authorization, the first execution scope is limited to private files under:

`private_data/sierra_chart/gc_2026_phase_a_pilot/`

It may read the three accepted raw market sources, the two accepted 2026 CME workbooks, the existing builder source, and its existing tests. It may not modify tracked source or tests. If the deterministic bounded-derivative contract cannot be implemented and verified without changing tracked code, execution stops and a separate exact code-change proposal is required.

## 22. Verification Matrix

The private checkpoint must record and independently verify at least:

1. exact parent and derivative hashes, sizes, line counts, and retained-row counts;
2. strict 13-column schema and UTF-8 decoding;
3. strictly increasing timestamps per derivative;
4. exact five-minute grid;
5. finite tick-aligned OHLC and valid geometry;
6. nonnegative integer volume and trades;
7. exact `volume = bid_volume + ask_volume`;
8. no synthetic no-data row;
9. exact one authorized observed-bound expansion labeled `ACQUISITION_ATTESTED_NO_TRADE_INTERVAL`, zero parent rows in it, and exact acquisition/session/predicate containment;
10. exact GCG26 observed-versus-coverage bounds and completed-session volume `53` for trade date `2026-02-18` without any inserted bar;
11. exact 29-entry calendar sequence and standard bounds;
12. exact initial `GCJ26-COMEX` three-session dominance proof;
13. no scheduled roll through `2026-03-30`;
14. zero OOS rows and no access to frozen OOS data;
15. deterministic repeat build identity and byte-for-byte output;
16. no unaccounted missing slot, duplicated or reordered row, silent sort, or off-session promoted bar; every recorded missing slot must have zero parent rows and remain inside exact acquisition/session/predicate coverage, and only the Section 17 interval may expand an observed bound;
17. `VALID` result with no blocking reason;
18. unchanged repository source, tests, staged state, HEAD, and origin/main.

## 23. Rollback, Promotion, and Stop Conditions

Rollback is deletion of the private Phase-A pilot directory only. Raw acquisition and calendar artifacts remain immutable and recoverable.

There is no automatic promotion path. Phase A remains non-promotable even when every check passes.

Stop immediately on any of the following:

- parent hash, calendar hash, timezone version, or schema mismatch;
- any need to edit a canonical raw artifact;
- any special-session date inside the chosen window;
- any inability to reproduce bounded derivative bytes exactly;
- any parent row inside the authorized no-trade interval, any failure to reproduce its zero-row proof, or any attempt to attest another interval;
- any coverage boundary outside the exact parent-acquisition, session, and derivative-predicate intersection;
- any builder result other than `VALID`;
- any nonzero OOS row count;
- any accidental read of the frozen OOS outcome artifact;
- any request to train, tune, backtest for promotion, integrate, or make profitability claims;
- any attempt to use this pilot as final evidence for 2024–2025;
- any required tracked-code change without a new bounded proposal.

## 24. Decision and Next Single Task

This proposal authorizes no execution by itself. If independent semantic and structural audit passes, the next single task is:

> Create the private Phase-A pilot directory, deterministically derive and hash the exact bounded GCG26/GCJ26/GCM26 inputs, construct the exact 29-entry pilot calendar and coverage sidecars including the single locked GCG26 acquisition-attested no-trade interval, then run the existing public builder once and produce a private validation checkpoint. Do not train, inspect OOS outcomes, integrate, stage, commit, or push.

The CME response has been received and independently reviewed. The 2024–2025 final dataset and all training promotion nevertheless remain frozen until both Section 4 quarantine intervals are fully reconciled and a later formal decision explicitly lifts the quarantine.
