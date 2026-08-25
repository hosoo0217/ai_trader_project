# GC Futures Independent Pretraining GCG26 Completed-Volume Coverage Acquisition Change Proposal

## 1. Proposal record

- Proposal ID:
  `GC-INDEPENDENT-PRETRAINING-GCG26-COMPLETED-VOLUME-COVERAGE-ACQUISITION-V1`.
- Proposal date: `2026-08-25`.
- Classification: documentation-only upstream evidence-acquisition proposal.
- Current evidence status: `UNKNOWN`.
- Promotion authority: `NONE`.
- Training readiness: `NOT_READY`.
- Trading authority: `NONE`.
- Final proposal state:
  `GCG26_MINIMUM_COVERAGE_ACQUISITION_PROPOSED_NO_ACQUISITION_NO_BUILD_NO_TRAINING_NO_OOS`.

This proposal freezes the smallest independent upstream acquisition that can address
the remaining `COMPARABLE_COMPLETED_VOLUME_MISSING` condition. It does not acquire
data, reinterpret missing bars as zero volume, rebuild the private corpus, construct
features or labels, inspect final OOS, train a model, integrate runtime behavior, or
authorize trading.

## 2. Exact documentation-only scope

This task may create, audit, stage, and locally commit only:

`docs/gc_futures_independent_pretraining_gcg26_completed_volume_coverage_acquisition_change_proposal.md`

No Python, test, fixture, private artifact, raw acquisition, manifest, calendar,
requirement, configuration, package export, integration file, or other documentation
file may change. The three pre-existing unrelated untracked documentation files remain
user-owned and untouched:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`; and
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Remote publication requires separate exact GitHub privacy/export authorization.

## 3. Governing repository baseline

This proposal is bound to:

- `HEAD`: `1761637c6604784e53ac9037af19729bc6511409`;
- parent: `cff665257832004fe4467308f239e0f0bf51f50d`;
- local `origin/main`: `1761637c6604784e53ac9037af19729bc6511409`;
- subject: `fix(data): separate calendar coverage from partition eligibility`.

| Exact dependency path | Bytes | SHA-256 |
| --- | ---: | --- |
| `analysis/gc_dataset_builder.py` | 109,258 | `26B2E028CCE33A415E1B60D66EF261E1B3AD48C028DA5531159451C68D9572ED` |
| `tests/test_gc_dataset_builder.py` | 106,345 | `4BD6D3309D625AD84361A617AA8E791DBBF33884C1D9DFFA23280C2AAA5EE971` |
| `docs/gc_futures_independent_pretraining_atomic_upstream_build_change_proposal.md` | 22,083 | `3D1902805081BEED918B237DECB06F8D63BC4821064E1A5E3618EDC23DF55C44` |
| `docs/gc_futures_independent_pretraining_source_domain_roll_boundary_correction_change_proposal.md` | 21,923 | `C88C3D0A04A9160FD81EC01E8FE6F36595E90307A45000DFE843FB68D191A7DB` |
| `docs/gc_futures_independent_pretraining_calendar_coverage_partition_eligibility_correction_change_proposal.md` | 20,528 | `0E007FAB1EA278AA4142F426195479B7562E0563F8237F59FB9C1DDDAEF9633E` |
| `docs/gc_futures_dataset_builder_calendar_coverage_partition_eligibility_checkpoint.md` | 8,429 | `6B2B52D5B8F062CBB8C05E2F84A831C14648F1A9276D3A148D65D7CC31C81AD1` |
| `private_data/sierra_chart/gc_20260803_raw_intake/intake_manifest.csv` | 3,226 | `AC8FAC02B4250E42386DD77599529C7159B8D896BD0E3D4553757226EF402164` |

Any dependency drift requires a fresh read-only audit before acquisition.

## 4. Verified remaining blocker

The corrected private preflight remains fail-closed and did not create
`private_data/sierra_chart/gc_independent_pretraining_corpus_v1/`. Its terminal
evidence contains 55 partition rows blocked by 15 unique
`COMPARABLE_COMPLETED_VOLUME_MISSING` trade dates:

```text
2025-08-07  2025-08-08  2025-08-11  2025-08-12  2025-08-13
2025-08-14  2025-08-15  2025-08-18  2025-08-19  2025-08-20
2025-08-21  2025-08-22  2025-08-25  2025-08-26  2025-08-27
```

For every date, active `GCZ25-COMEX` has a completed-session integer volume and
adjacent `GCG26-COMEX` does not. No calendar, parser, roll-selection, partition, or
ordinary sparse-bar defect was found.

## 5. Exact source-boundary diagnosis

The immutable current source is:

- path:
  `private_data/sierra_chart/gc_20260803_raw_intake/GCG26_COMEX_5m_186d_export_20260803.txt`;
- bytes: `2,662,983`;
- SHA-256:
  `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719`;
- parsed row count: `26,431`;
- first row: `2025-08-27 09:45:00 Asia/Tokyo` =
  `2025-08-27T00:45:00Z`;
- last row: `2026-02-25 20:40:00 Asia/Tokyo` =
  `2026-02-25T11:40:00Z`;
- exact full-file `Bid Volume + Ask Volume == Volume` failures: `0`; and
- canonical header:
  `Date, Time, Open, High, Low, Last, Volume, # of Trades, OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume`.

Fourteen blocked sessions precede this coverage. Trade date `2025-08-27` begins at
`2025-08-26T22:00:00Z`, so its first 33 five-minute slots also precede coverage.
Trade date `2025-08-28` is the first ordinary comparison session fully enclosed by
the current coverage and therefore acts as the positive boundary control.

## 6. Intended use and exact grain

The intended use is only to establish whether accepted source-service coverage exists
for each expected five-minute slot required by the current completed-session volume
rule. The grain is:

`(contract, trade_date, expected_5m_slot_start_utc)`.

The acquisition may prove observed five-minute bars or a provider-attested no-trade
interval. It may not create synthetic bars, assign volume to an unobserved slot, infer
coverage from a later row, or assert an economic result.

## 7. Exact minimum acquisition interval

The required half-open source-service coverage interval is:

`[2025-08-06T22:00:00Z, 2025-08-28T21:00:00Z)`.

In the locked source timezone `Asia/Tokyo`, this is:

`[2025-08-07 07:00:00, 2025-08-29 06:00:00)`.

The start is the exact open of GC trade date `2025-08-07`. The end includes the full
trade date `2025-08-28` positive-control session and provides deterministic overlap
with the current source. An acquisition beginning later, ending earlier, or expressed
with an unbound timezone is insufficient and returns `UNKNOWN` or `INVALID` as
specified below.

## 8. Canonical instrument and chart contract

The acquisition is restricted to `GCG26-COMEX`, COMEX Gold Futures February 2026,
five-minute intraday bars. Required settings are:

- source service: Sierra Chart historical intraday service used by the accepted raw
  intake;
- symbol: exact `GCG26-COMEX` service symbol, with `[M]` display suffix treated only
  as chart metadata;
- source timezone: `Asia/Tokyo`;
- exchange timezone: `America/New_York`;
- runtime tzdata version: `2026.2`;
- bar period: exact five minutes;
- volume filters: disabled;
- incomplete current bar: excluded;
- export schema: exact 13-column header in Section 5.

Continuous-contract, adjusted, back-adjusted, spot, CFD, daily-summary,
`BAR_SUMMARY`, study-derived, broker-substituted, or manually edited data is forbidden.

## 9. Accepted acquisition evidence

A future separately authorized private acquisition must preserve all of:

1. the raw Sierra Chart export bytes;
2. the exact chart/request settings and requested interval;
3. the copied Sierra Message Log lines identifying request completion and symbol;
4. acquisition timestamp and local timezone;
5. source path, bytes, SHA-256, first/last parsed moment, and row count;
6. the current immutable source identity from Section 5; and
7. an independently generated scope and overlap audit.

A screenshot alone is supporting evidence, not a machine-readable coverage contract.
An email, web chart, TradingView chart, or recollection cannot replace the Sierra
request and export evidence.

## 10. Provider-attested no-trade boundary

The absence of exported rows before the first trade is not by itself proof of
coverage. A no-trade interval is admissible only when the exact successful Sierra
historical request demonstrably covered that interval and completed without truncation,
timeout, cancellation, symbol substitution, or error.

When such coverage is proven, the completed-session calculation may sum the observed
integer volumes to zero without creating bars. When request coverage is not provable,
the interval remains `UNKNOWN`. Missing rows are never silently relabeled as zero-volume
observations.

## 11. Immutable existing-source boundary

The existing GCG26 export, intake manifest, README, `.scid` cache, all accepted private
evidence, and all prior hashes remain immutable. The new acquisition must not overwrite,
append to, rename, re-export over, or repair the current source.

The existing Sierra `.scid` file is local cache, not a canonical research artifact.
It may be used by Sierra during acquisition but must not be copied into the repository,
hashed as final OOS evidence, or treated as a portable source contract.

## 12. Future private acquisition exact root

A later explicit private-acquisition authorization may create only this Git-ignored
root:

`private_data/sierra_chart/gc_gcg26_completed_volume_coverage_acquisition_v1/`

Its exact allowed final files are:

```text
GCG26_COMEX_5m_extended_history_acquisition_v1.txt
sierra_request_evidence_v1.txt
acquisition_binding_v1.json
coverage_result_v1.json
scope_audit_v1.json
two_run_reproducibility_v1.json
```

Temporary A/B roots and ephemeral scripts must be outside the final root and absent
after audit. No private artifact may be staged, committed, pushed, uploaded to an LLM,
or published.

## 13. Exact overlap reconciliation

Every new row whose normalized timestamp overlaps the immutable current source must
match the current row on normalized timestamp, Open, High, Low, Last, Volume, number
of trades, Bid Volume, and Ask Volume. Numeric text formatting may normalize only
under the existing parser; economic values may not be rounded, filled, resampled, or
revised.

Zero overlap, duplicate conflicting rows, non-monotonic timestamps, different bar
boundaries, or any value mismatch is `AMBIGUOUS` or `INVALID` and forbids promotion.
Hash or lexical ordering is not a chronology tie-break.

## 14. Volume and timestamp validation

All accepted observed rows must satisfy the current public builder contract:

- timezone-aware normalized timestamp;
- exact five-minute alignment;
- finite OHLC values on the GC tick grid;
- integer nonnegative Volume, Bid Volume, Ask Volume, and trade count;
- `Bid Volume + Ask Volume == Volume` where required by the accepted source schema;
- deterministic chronological ordering;
- no duplicate normalized moment; and
- no row outside the acquired source-service interval.

Boolean, fractional, negative, non-finite, malformed, reordered, or duplicate-conflict
values fail closed without exception leakage.

## 15. Coverage-result status and precedence

Final precedence is:

`INVALID > AMBIGUOUS > UNKNOWN > PASS > NONE`.

- `INVALID`: malformed request/source/binding, impossible timestamp, bad type, hash
  mismatch, wrong symbol/timezone/version/schema, or failed scope audit.
- `AMBIGUOUS`: multiple independently plausible canonical interpretations or
  conflicting overlap values.
- `UNKNOWN`: evidence is well formed but does not prove every required slot, request
  completion, or no-trade coverage.
- `PASS`: the minimum interval is fully attested, overlap reconciles exactly, two
  independent normalizations match, and scope audit passes.
- `NONE`: no acquisition was attempted and no evidence was supplied.

`PASS` means only upstream coverage evidence is ready for a later reviewed binding
proposal. It is not dataset, candidate, corpus, training, strategy, or economic PASS.

## 16. Atomic acquisition and two-run verification

The future transaction is atomic:

1. verify the governing tracked baseline and immutable current source;
2. create absent temporary A and B roots;
3. bind one immutable newly acquired raw export and request evidence;
4. independently normalize and audit A and B;
5. compare ordered objects, canonical bytes, counts, identities, and SHA-256 values;
6. verify the exact six-file final scope;
7. publish to the absent final private root only after equality and scope PASS; and
8. delete only task-local temporary artifacts after resolved-path validation.

Any failed or incomplete transaction promotes nothing. An existing nonempty final
root is a STOP condition, never an overwrite target.

## 17. Prefix invariance and no retroactive rescue

The acquisition may add genuinely earlier source-service coverage while preserving
all current overlapping evidence byte-for-byte. It may not rewrite the current source,
calendar, roll plan, partition plan, candidate dates, confirmation rule, source order,
or status precedence.

The later acquisition timestamp must remain explicit. It may resolve research-time
source coverage but cannot be presented as evidence known to a historical trading
agent at that earlier moment. Dataset construction remains causal by bar and session;
acquisition provenance remains separate research metadata.

## 18. Final-OOS and private-data isolation

The sealed final-OOS file and its payload are outside scope. Its exact forbidden path
is:

`private_data/sierra_chart/gc_20260803_raw_intake/GCQ26_COMEX_5m_30d_export_20260803.txt`

The acquisition runner, auditor, shell commands, glob patterns, and directory
enumeration must exclude that path explicitly. No read, parse, hash, copy, count,
schema inspection, or metadata-derived inference from that payload is permitted.

Local-LLM and remote-LLM exposure of raw private market data is forbidden. Only this
tracked proposal may later be considered for Git publication under separate explicit
privacy/export authority.

## 19. No implementation or integration authority

This proposal changes no public API, source module, test, fixture, manifest, package
export, requirement, configuration, strategy, risk, trace, engine, broker, or runtime
integration. It grants no authority for:

- corrected corpus or dataset execution;
- feature or label construction;
- training, fine-tuning, selection, inference, or model installation;
- OOS access or repartitioning;
- backtest, PnL, win-rate, confidence, or edge claims; or
- entry, exit, BUY, SELL, sizing, paper, broker, or live trading.

A successful private acquisition must STOP for an independent acceptance decision and
a separate source-binding/rebuild proposal.

## 20. Exact future resume boundary

After this proposal is independently accepted, committed, and separately authorized
for private execution, the only next operational task is the exact private acquisition
in Sections 7–16. The operator may need to use Sierra Chart manually because the
desktop data service is external to repository automation.

If Sierra cannot prove the requested interval, the task returns `UNKNOWN`; it must not
fall back to another vendor, continuous contract, inferred listing date, synthetic
zero volume, or altered builder rule. Any alternative source requires a new
documentation-only proposal and independent provenance review.

## 21. Inline synthetic exact 48-case acceptance matrix

1. HEAD, parent, origin/main, and subject equal the Section 3 baseline.
2. Exact documentation-only one-file scope holds.
3. All dependency bytes and hashes reconcile.
4. Existing intake manifest and current GCG26 source remain byte-immutable.
5. Existing final private corpus root remains absent.
6. Exact 15 blocked trade dates reconcile.
7. All 15 active GCZ25 completed volumes are available.
8. All 15 adjacent GCG26 completed volumes are unavailable.
9. Current GCG26 first moment is exact `2025-08-27T00:45:00Z`.
10. Fourteen blocked sessions are wholly before current coverage.
11. Trade date 2025-08-27 has exactly 33 uncovered leading five-minute slots.
12. Trade date 2025-08-28 is the positive fully covered boundary control.
13. Minimum acquisition start is exact `2025-08-06T22:00:00Z` inclusive.
14. Minimum acquisition end is exact `2025-08-28T21:00:00Z` exclusive.
15. Tokyo equivalents are exact and DST conversion is database-backed.
16. Instrument is exact GCG26-COMEX outright February 2026 futures.
17. Five-minute bar period and exact 13-column schema reconcile.
18. Continuous, adjusted, spot, CFD, daily, and BAR_SUMMARY sources reject.
19. Raw export, request evidence, settings, completion, and acquisition timestamp are required.
20. Screenshot-only evidence cannot independently prove coverage.
21. Missing rows alone cannot prove a no-trade interval.
22. Successful exact request coverage may attest a no-trade interval without synthetic bars.
23. Truncated, cancelled, timed-out, or errored request remains UNKNOWN or INVALID.
24. Existing source and manifest cannot be overwritten, appended, renamed, or repaired.
25. Sierra `.scid` cache is not promoted as a canonical portable artifact.
26. Exact future private root and six-file allowlist reconcile.
27. Temporary A/B roots and ephemeral scripts are absent after audit.
28. Every overlapping timestamp matches all required economic fields.
29. Conflicting overlap is AMBIGUOUS or INVALID, never silently selected.
30. Zero overlap is insufficient for PASS.
31. Timestamp ordering, uniqueness, and exact five-minute alignment validate.
32. OHLC and volume/trade fields validate without exception leakage.
33. Boolean, negative, fractional, non-finite, and malformed values reject.
34. INVALID outranks AMBIGUOUS, UNKNOWN, PASS, and NONE.
35. AMBIGUOUS outranks UNKNOWN, PASS, and NONE.
36. Incomplete but well-formed coverage returns UNKNOWN.
37. No attempted acquisition returns NONE.
38. PASS requires complete interval, exact overlap, reproducibility, and scope audit.
39. PASS grants no dataset, corpus, training, strategy, or trading authority.
40. Run A and B are fresh independent normalizations from immutable acquired bytes.
41. Ordered objects, canonical bytes, counts, IDs, and hashes match across runs.
42. Failing transaction promotes no file or partial evidence.
43. Existing nonempty final root causes STOP without overwrite.
44. Earlier coverage preserves current overlap and all prior evidence byte-for-byte.
45. Acquisition-time metadata remains distinct from historical market-time knowledge.
46. Final-OOS payload contact remains exactly zero.
47. Focused/full cache-disabled regressions and exact Git scope audit pass.
48. Rollback, promotion, privacy, global freeze, and STOP conditions reconcile.

## 22. Independent verification gates

Before local proposal commit, an independent audit must verify all 24 sections, all 48
sequential cases, dependency hashes, exact source boundary, exact one-file diff,
formatting, and unchanged unrelated files. Required tests are:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_dataset_builder.py
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
```

Fresh results and timings must be recorded here before staging. The tests authorize
only documentation acceptance; they do not authorize acquisition or rebuild.

Fresh documentation-only baseline evidence captured on `2026-08-25`:

- focused builder suite: `253 passed in 1.07s`;
- full regression suite: `2527 passed in 23.29s`;
- both commands used `-p no:cacheprovider` exactly; and
- no source, test, private-data, OOS, integration, or training artifact was changed or
  created by the test run.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this proposal file. After commit,
rollback requires a bounded revert, never history rewriting. Documentation promotion
requires exact-path staging, full cached-content review, cached `diff --check`, hash
audit, and a one-file local commit. Remote publication requires separate exact GitHub
privacy/export authorization.

STOP immediately on baseline or hash drift, current-source mutation, manifest change,
wrong instrument or timezone, insufficient request coverage, schema mismatch,
overlap conflict, nondeterminism, unexpected private file, final-OOS contact, source
substitution, synthetic data, feature/label work, training, integration, trading
dependency, broad staging, or remote push without exact authorization.

## 24. Final bounded decision

The remaining `COMPARABLE_COMPLETED_VOLUME_MISSING` condition is an upstream
GCG26 source-service coverage gap, not a verified calendar or builder defect. The
smallest admissible next operation is one independent private Sierra Chart acquisition
covering the exact interval in Section 7 and preserving deterministic overlap with the
current source.

This documentation task must STOP after independent audit and local commit. The private
acquisition, corrected corpus rebuild, training, final-OOS access, implementation,
integration, trading, and remote push remain frozen until separately authorized.
