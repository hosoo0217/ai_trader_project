# GC Futures Phase B NY-AM Opening-Range Sweep/Reclaim Reversion Attested-No-Trade Coverage Correction Proposal

## 1. Proposal record

This documentation-only proposal records one bounded semantic correction for
the GC NY-AM opening-range sweep/reclaim reversion diagnostic. It is based on
the immutable Phase A development dataset and the completed Kill-zone
dependency used by the V2 private feasibility procedure. It grants no source,
private-data, training, OOS, feature/label, integration, push, or trading
authority.

The observed defect is narrow: a calendar-eligible trade date with canonical
attested no-trade gaps inside the six-member opening range is currently
classified as malformed `INVALID_OPENING_RANGE`. Known absence and malformed
evidence must not share one status.

## 2. Repository and execution baseline

The accepted repository baseline is commit
`3a1ca1fa22062d861cadcdef60b14b8c5268e8a4`, equal to local `origin/main` when
this proposal was prepared. The preceding exact V2 private two-run execution
was deterministic and byte-identical but returned:

- status `INVALID`;
- `63` complete opening ranges from `64` requested trade dates;
- `54` candidates and `54` outcomes;
- reasons `INVALID_OPENING_RANGE`, `NO_SWEEP_RECLAIM`, and
  `AMBIGUOUS_SWEEP_RECLAIM`.

No output from that failed feasibility run is promoted or rewritten by this
proposal.

## 3. Exact documentation-only scope

The only file authorized in the present task is:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_attested_no_trade_coverage_correction_proposal.md`

The proposal may be independently audited, staged by this exact path, cached-
audited, and locally committed. All other tracked and untracked paths remain
untouched. Push requires separate explicit privacy/export authorization.

## 4. Immutable input roots and bindings

The correction is bound to these immutable private roots:

- Phase A dataset root:
  `private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1`;
- complete Kill-zone root:
  `private_data/sierra_chart/gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1`;
- source intake root:
  `private_data/sierra_chart/gc_20260803_raw_intake`.

The dataset ID is
`2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`.
The dataset input artifact-set ID is
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
The complete Kill-zone artifact-set ID is
`089e38c945f679674853282b6b730a038d936f3ed2eeaa2f23fe123636df6f05`.

## 5. Immutable dataset and partition facts

The accepted dataset remains `VALID`, development-only, and contains exactly
`17,404` bars in `133` ordered segments for `64` strictly increasing requested
trade dates from `2026-02-23` through `2026-05-22`. OOS membership is zero.
Contracts remain exactly `GCJ26-COMEX` and `GCM26-COMEX`; the deterministic
roll-effective trade date remains `2026-04-01`.

The dataset manifest records exactly `260` missing bars and `260` attested
no-trade intervals. This correction does not add synthetic bars, forward-fill,
interpolate, change a contract, move the roll date, or exclude a requested
date.

## 6. Exact defect evidence

Trade date `2026-03-31` is the only requested date without all six NY-AM
opening-range members. It contains only the `07:20` local bar from the exact
`07:00`, `07:05`, `07:10`, `07:15`, `07:20`, `07:25` set. Later canonical
evidence exists, so the current implementation enters the
`INVALID_OPENING_RANGE` branch.

The affected canonical segment is ordinal `74`, segment ID
`09c8048907719ffe99a3de7c6402dcf36e88561eff20a6589b7fc8384b591b6b`,
contract `GCJ26-COMEX`, source ID
`fafcb9cd47ca240f9a366ed035255ae6e57e7ca4de6ec968663b6e2e4ea51e3c`,
and `preceding_missing_bar_count=5`. Its single bar closes at
`2026-03-31T11:25:00Z` and carries OHLC ticks `45739/45740/45739/45740`
with volume `26`.

## 7. Raw-source and lineage proof

The bound raw file is
`GCJ26_COMEX_5m_186d_export_20260803.txt`, SHA-256
`B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85`.
Its authorized parser prefix covers the target moment. At the corresponding
Tokyo-local source times, `20:20` exists while `20:00`, `20:05`, `20:10`,
`20:15`, and `20:25` do not. Adjacent later rows exist.

Therefore the gap is present in the immutable acquisition itself. It is not a
JSON omission, parser truncation, Kill-zone projection loss, or silent sort.
The dataset segment gap metadata deterministically preserves the same absence.

## 8. Kill-zone reconciliation proof

The complete Kill-zone dependency has one result for every one of the `133`
dataset segments. Segment ordinal `74` is `VALID` with one context and one
snapshot for its one supplied bar. Thus Kill-zone evidence exactly mirrors the
canonical dataset and does not invent the five absent opening-range members.

Missing bars cannot be reconstructed from context or snapshot identities. A
valid one-bar Kill-zone segment is not proof that a complete six-bar opening
range exists.

## 9. Root-cause decision

The root cause is an analyzer status-boundary defect. The implementation treats
every short opening-range tuple followed by later evidence as malformed. It
does not distinguish:

1. canonical, provenance-backed attested no-trade slots; and
2. duplicate, reordered, substituted, mixed-lineage, or otherwise malformed
   supplied evidence.

The dataset, calendar, roll plan, raw parser, and Kill-zone dependency are not
to be repaired for this finding.

## 10. Exact attested-no-trade qualification

A requested, calendar-eligible trade date qualifies as
`ATTESTED_NO_TRADE_OPENING_RANGE` only when all of the following hold:

1. the dataset, manifest, ordered segments, and raw-source bindings are
   canonical and `VALID`;
2. the six expected local open moments are computed from
   `America/New_York` and runtime-bound tzdata without silent sorting;
3. every supplied opening-range bar exactly reconciles to its canonical
   dataset bar, Kill-zone context, and snapshot;
4. every absent member is explained by canonical segment-gap lineage and the
   ordered adjacent canonical bar moments;
5. no duplicate, fork, timestamp substitution, contract/date mismatch,
   malformed OHLCV, or contradictory member exists; and
6. the evidence needed to prove the gap is available without OOS contact.

Failure of any qualification does not fall through to this reason.

## 11. Corrected status semantics

An attested-no-trade opening-range group is known non-evaluable. It emits no
opening range, candidate, or outcome. In isolation it returns `NONE` with
non-blocking reason `ATTESTED_NO_TRADE_OPENING_RANGE`.

Malformed or contradictory opening-range evidence remains `INVALID` with
`INVALID_OPENING_RANGE`. Genuinely unavailable, truncated, or unprovable
coverage remains `UNKNOWN` with `INCOMPLETE_OPENING_RANGE`. The aggregate
precedence remains exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

The non-blocking attested-no-trade reason cannot lower or override a status
earned by another complete independent group.

## 12. Atomicity and no-promotion boundary

An attested-no-trade group promotes nothing from itself. It does not prevent
strictly prior or later independent complete groups from being analyzed.
Malformed evidence still establishes a chronological cutoff: its group and all
later evidence promote nothing, while strictly prior complete immutable
evidence is preserved byte-for-byte.

No partial opening range, synthetic range, candidate, outcome, or manifest
reference may be fabricated for an attested-no-trade date.

## 13. Count funnel and reason contract

The ordered count funnel adds exactly one identity-bearing key immediately
after `CALENDAR_ELIGIBLE_TRADE_DATES`:

`ATTESTED_NO_TRADE_OPENING_RANGE_TRADE_DATES`

The ordered reason vocabulary adds exactly one token immediately after
`SESSION_INELIGIBLE`:

`ATTESTED_NO_TRADE_OPENING_RANGE`

Its manifest occurrence count equals the exact number of qualifying requested
trade dates. `CALENDAR_ELIGIBLE_TRADE_DATES` remains a calendar measure and is
not silently reduced. `COMPLETE_OPENING_RANGES` remains the count of actual
six-member ranges.

## 14. Version and deterministic identity effect

Because the ordered funnel and reason counts are manifest identity payload,
the version constant changes exactly from
`GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1` to
`GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V2`.

All OBSERVATION, OPENING_RANGE, CANDIDATE, OUTCOME, and MANIFEST required and
forbidden fields remain unchanged. Existing objects cannot be silently
relabelled. V1 and V2 manifests are distinct deterministic identities even
when their emitted evidence tuples otherwise match.

## 15. Exact public API boundary

The exact keyword-only parameter names, annotations, and defaults of
`make_gc_ny_am_sweep_reclaim_id()` and
`analyze_gc_ny_am_opening_range_sweep_reclaim_reversion()` remain unchanged.
All public enums and frozen dataclass fields/defaults remain unchanged. Only
the exported version value and identity-bearing ordered funnel/reason contents
change as specified in Sections 13–14.

No new loader, repair flag, exclusion parameter, threshold, or caller-supplied
attestation override is permitted.

## 16. Deterministic ordering and prefix invariance

Requested dates, dataset segments, observations, contexts, and snapshots retain
their locked canonical ordering. Hash lexical order is never a chronology
tie-break. Same-effective append, historical insertion, repair, reorder,
contract replacement, calendar/tzdata mutation, or gap-lineage mutation is
ineligible for prefix comparison.

A strictly later complete append preserves every pre-existing V2 evidence and
identity byte-for-byte. An attested-no-trade date remains non-evaluable under a
strictly later append and cannot be retroactively filled.

## 17. Feasibility-gate effect

All `64` requested dates remain in the audit denominator. The correction may
produce `63` complete opening ranges and one counted attested-no-trade date; it
does not pretend there were `64` tradable setups. Existing minimum candidate,
eligible-date, direction, and contract gates remain numerically unchanged.

The previous private-run `INVALID` result is not converted to `PASS` by
documentation. A corrected rerun is separately required. Based only on the
already observed reasons, the next aggregate status may be `AMBIGUOUS`; this is
an inference, not an accepted result.

## 18. Future implementation exact three-path scope

Any later implementation exception is reserved to exactly:

- `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py`;
- `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py`;
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md`.

No dataset builder, raw intake, Kill-zone module, calendar, runner, feature,
label, model, integration, configuration, export, or package-init path may be
changed under this correction.

## 19. Test-first correction requirements

Tests must fail first on V1 behavior and lock at least:

- the exact 2026-03-31-shaped attested gap as known non-evaluable `NONE`;
- malformed short evidence with later bars as `INVALID`;
- unprovable/truncated short evidence as `UNKNOWN`;
- mixed complete and attested groups without loss of complete evidence;
- exact new ordered funnel/reason and V2 manifest identity;
- repeatability, exception containment, atomic cutoff, and prefix invariance.

Parameterization may add collected tests while preserving exactly `48` logical
case numbers.

## 20. Independent audit requirements

Implementation acceptance requires an independent audit of grain,
completeness, validity, temporal alignment, lineage, status precedence,
identity schemas, exact API, formatting, scope, focused tests, and full
regression. The audit must recompute hashes and compare outputs without reusing
the implementation run's in-memory conclusions.

The audit must explicitly prove that no raw data, private artifact, requested
date, or failed historical evidence was deleted or rewritten.

## 21. Inline synthetic exact 48-case matrix

The correction preserves exactly these sequential logical cases:

1. Missing top-level context remains `UNKNOWN` after independent supplied-evidence validation.
2. Malformed supplied counterpart outranks missing-context `UNKNOWN` as `INVALID`.
3. Observation duplicate, reorder, and fork remain `INVALID`.
4. Boolean, fractional, non-finite, malformed OHLCV, or non-closed evidence remains `INVALID`.
5. Naive timestamps and timezone-version mismatch remain `INVALID`.
6. Only unambiguous GC outright contract evidence is accepted.
7. Only closed five-minute single-contract source evidence is accepted.
8. Calendar missing, closed, and malformed semantics remain locked.
9. Early close preventing the source or horizon remains session-ineligible.
10. Exact six `07:00`–`07:25` members form the range first known at `07:30`.
11. Five genuinely truncated members remain `UNKNOWN`; a seventh member never enters the source.
12. Missing middle timestamp substitution or unexplained nonconsecutive source remains `INVALID`.
13. Cross-date, cross-segment, cross-contract, or cross-session source remains `INVALID`.
14. Positive one-tick width is valid and zero width remains `INVALID`.
15. Midpoint, signed zero, and arbitrary magnitude remain Decimal-context independent.
16. Valid non-NY-AM bars remain dataset evidence but are not projected observations.
17. NY-AM membership remains exact `07:00` inclusive and `10:00` exclusive.
18. Missing, extra, reordered, or mismatched NY-AM projection remains fail-closed.
19. Complete non-NY-AM members do not become Phase B observations.
20. Sweep boundary misses, midpoint equality, and outside closes retain locked candidate semantics.
21. Close exactly at the swept boundary qualifies; outside close does not.
22. Later reclaim cannot retroactively relabel an earlier outside close.
23. Both-boundary formation remains atomic `AMBIGUOUS`.
24. Earliest qualifying formation wins; later bars are outcome-only.
25. Exact duplicates collapse; forked same-effective evidence remains `INVALID`.
26. Bullish and bearish geometry remain exact mirrors.
27. Bearish candidate provenance, identity, fields, and immutability remain exhaustive.
28. Bullish identity remains exhaustive and impossible geometry fails closed.
29. Formation observation remains excluded from outcome evaluation.
30. Outcome horizon remains the next exact twelve compatible observations.
31. Bearish low at midpoint remains target equality.
32. Bullish high at midpoint remains target equality.
33. Bearish close at formation-high plus one remains invalidation equality.
34. Bullish close at formation-low minus one remains invalidation equality.
35. Same first bar target and invalidation remains `SAME_BAR_AMBIGUOUS`.
36. Twelve complete no-event observations remain `TIMEOUT`.
37. Truncated horizon remains `UNKNOWN` without later relabelling.
38. Later malformed group preserves only strictly prior complete evidence.
39. Final precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
40. Every identity kind retains exhaustive required and forbidden schemas.
41. Ordered history, effective moments, exact reasons, and malformed hashes remain contained.
42. Exact public APIs/defaults, frozen dataclasses, enums, V2 version, and exports are locked.
43. Repeatability, ordered counts/reasons, manifest identity, and bytes include the new attestation fields.
44. Strictly later complete append is prefix-invariant; same-effective repair is ineligible.
45. Retained incomplete dependency prefix remains `UNKNOWN` and preserves prior evidence only.
46. Complete dependency preserves native `VALID` and `NONE` statuses.
47. Exact three-path implementation scope, private-root immutability, and 2026-03-31 attested-gap discriminator are locked.
48. Private run, training, OOS, feature/label, integration, push, and trading authority remain unused.

## 22. Rollback and evidence preservation

Before implementation commit, rollback is restoration of only the reserved
three implementation paths to their accepted parent bytes. After a future
commit, rollback is a bounded revert. History rewriting, private artifact
deletion, failed-run erasure, date filtering, and roll-date rewriting are
forbidden.

This documentation file itself may be reverted only by a traceable bounded
commit; its evidence findings must not be silently removed from later reports.

## 23. Promotion and STOP conditions

Promotion requires test-first proof, exact three-path scope, deterministic V2
identities, exact `48` logical cases, cache-disabled focused and full regression
PASS, artifact hashes and byte/line counts, independent final audit, exact-path
staging, cached audit, local commit, separate push authorization, and a separate
exact private-rerun authorization.

STOP on any unexplained gap; dataset/raw/calendar/roll/Kill-zone drift; public
API or dataclass drift; silent sorting, filtering, repair, interpolation, or
synthetic bars; status-precedence change; exception leakage; nondeterminism;
scope expansion; OOS access; feature/label/model/training/PnL/integration work;
private execution without exact authority; or push without explicit
privacy/export consent.

## 24. Final bounded decision and next single task

The decision is:

`READY_FOR_DOCUMENTATION_ACCEPTANCE_THEN_EXPLICIT_TEST_FIRST_CORRECTION_AUTHORIZATION`

The present task ends after independent one-file audit, exact-path staging,
cached audit, and local documentation commit. The next single task is push
preflight/publication of that exact one-file commit under separate explicit
GitHub privacy/export authorization. Source correction and private rerun remain
separately gated. Training, OOS, feature/label construction, integration, and
trading remain forbidden.
