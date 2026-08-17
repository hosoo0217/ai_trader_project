# GC Futures Phase B Complete Kill-zone Evidence Alignment Correction Proposal

## 1. Correction record

- Record date: `2026-08-17`.
- Repository baseline: exact local `HEAD`
  `22182d5ae8a6c36e804a4f38c88a8f1b43d7c330`.
- Decision state: `FAIL_CLOSED / DOCUMENTATION-ONLY SEMANTIC CORRECTION`.
- Affected capability: `GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V1`.
- Accepted upstream dependency:
  `gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1`.
- This record authorizes no source change, private execution, feature or label
  build, model training, OOS access, integration, trading, or push.

## 2. Decision summary

The accepted complete Kill-zone dependency is canonical, internally
recomputable, and complete, but the current Phase B analyzer interprets five
parts of that evidence incorrectly:

1. it compares canonical fully-closed Kill-zone moments with the Phase B bar
   **open** instead of the bar **close**;
2. it requires a singleton snapshot history although the public Kill-zone
   contract emits an ordered cumulative history;
3. it requires global index-first ordering although public dataset indices are
   segment-local and reset at canonical segment boundaries; and
4. it requires the complete dependency member sets to equal the NY-AM
   observation-reference subset; and
5. it admits a canonical bar opened at `09:55` even though that fully closed
   bar's `10:00` evidence moment is outside the public Kill-zone
   start-inclusive/end-exclusive `NEW_YORK_AM` window.

These are analyzer-contract defects, not failed market evidence and not defects
in the accepted dependency. The private hypothesis run remains blocked until a
separately authorized exact three-path, test-first correction passes independent
audit.

## 3. Verified repository and evidence baseline

The tracked worktree and index were clean at audit start. The following
pre-existing unrelated untracked documents were present and are outside this
record:

- `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`;
- `docs/gc_futures_real_data_input_binding_change_proposal.md`; and
- `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

They must remain untouched. Neither temporary nor final Phase B private-run
output roots exist.

The accepted dependency contains exactly:

- `133` ordered segment results;
- `101 VALID` and `32 NONE` segment statuses;
- `17,404` fully closed source bars across `64` requested trade dates;
- `9,839` contexts and `9,839` snapshots;
- `2,276` `NEW_YORK_AM` contexts; and
- `9,839` unique context IDs and `9,839` unique snapshot IDs.

All public context and snapshot identities recompute exactly and no snapshot
history contains a dangling context ID.

## 4. Exact documentation-only scope

This semantic correction amends only:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_complete_kill_zone_alignment_correction_proposal.md`

No other existing file is edited. No private artifact is created, deleted,
repaired, or renamed. Broad staging is forbidden. The global code freeze
remains active.

## 5. Reproduced fully-closed moment defect

The public Kill-zone dependency was constructed from each canonical source bar
as `KillZoneObservation(index=bar.index, timestamp=bar.timestamp,
is_closed=True)`. Phase B independently and correctly defines that same dataset
`bar.timestamp` as `bar_close_timestamp`, with
`bar_open_timestamp = bar.timestamp - 5 minutes`.

For all `2,276` accepted `NEW_YORK_AM` contexts:

- `2,276` context moments exactly equal their source dataset bar timestamp and
  therefore the Phase B bar-close moment;
- `0` equal the Phase B bar-open moment; and
- the corresponding snapshot moment equals the context moment.

The current comparison to `bar_open_timestamp` therefore rejects every
canonical projected dependency object. The correction must compare context and
snapshot effective moments to `bar_close_timestamp`. It must not shift,
relabel, or recreate upstream evidence.

The public Kill-zone detector also classifies its fully closed observation
timestamp using the fixed start-inclusive/end-exclusive interval
`[07:00, 10:00)` New York. Phase B may therefore project a canonical five-minute
bar only when both its open-time structural membership and its close-time
Kill-zone evidence membership are true. Their exact intersection is bar-open
`[07:00, 09:55)`: `07:00` through `09:50` at five-minute spacing. A canonical
bar opened at `09:55` and closed at `10:00` remains immutable dataset evidence,
but it cannot carry a canonical `NEW_YORK_AM` context and must not become a
Phase B observation. Timestamp shifting, a synthetic `09:55` context, or an
upstream Kill-zone contract change is forbidden.

## 6. Reproduced cumulative-history defect

The public Kill-zone snapshot is an immutable point-in-time snapshot carrying
the complete ordered context history of its own analyzer invocation. It is not
a one-context delta.

Across the accepted dependency:

- exactly `101` first snapshots have singleton history;
- exactly `9,738` later snapshots have non-singleton history; and
- every nonempty segment history restarts at length `1` and grows cumulatively.

Within the `2,276` referenced `NEW_YORK_AM` snapshots, only `6` are singleton
and `2,270` are non-singleton. The current singleton requirement is therefore
invalid. The terminal history member, not the whole tuple, must identify the
same-moment context referenced by the Phase B observation.

## 7. Reproduced segment-local chronology defect

Dataset bar indices and Kill-zone observation indices are local to each
canonical dataset segment. They restart at segment boundaries. Every accepted
nonempty segment context stream and snapshot stream is independently strictly
increasing by local `(index, normalized timestamp)`, but concatenating the
canonical segment-major streams is not globally index-first increasing.

The audit found `79` canonical cross-segment boundaries at which the previous
segment's final local index is greater than or equal to the next segment's
first local index. There are no duplicate normalized timestamps and no
duplicate `(index, timestamp)` pairs across the accepted member set, but that
does not make a global index-first rule valid.

The correction must use exact segment-aware order:

`(segment_ordinal, local_index, normalized timestamp)`.

Within one segment, local index and normalized timestamp are independently
strictly increasing. Across segments, canonical `segment_ordinal` is the first
ordering component. No silent sort is permitted.

## 8. Reproduced complete-evidence versus reference-subset defect

The complete dependency contains every emitted Kill-zone context required to
prove cumulative snapshot histories. Phase B observations intentionally
reference only the `NEW_YORK_AM` subset. Therefore:

- every observation reference must resolve to exactly one supplied context and
  one supplied snapshot;
- referenced IDs must be subsets of the complete supplied ID sets;
- extra canonical non-NY-AM contexts and their snapshots are required history,
  not unrequested evidence; and
- missing, duplicate, forked, reordered, or malformed complete members remain
  fail-closed `INVALID` even when no Phase B observation directly references
  them.

Exact equality between complete member sets and observation-reference sets is
forbidden.

## 9. Exact canonical observation alignment

For one projected `GCNYAMSweepReclaimObservation`:

1. `segment_ordinal`, `segment_id`, `contract`, `trade_date`, and local `index`
   must match one exact canonical dataset bar;
2. `bar_close_timestamp` must equal the dataset bar timestamp;
3. `bar_open_timestamp` must equal that timestamp minus exactly five minutes;
4. OHLC ticks, integer volume, and `is_closed=True` must match the same bar;
5. structural New York membership requires normalized `bar_open_timestamp` in
   start-inclusive/end-exclusive `[07:00, 10:00)` and canonical Kill-zone
   evidence membership independently requires normalized
   `bar_close_timestamp` in `[07:00, 10:00)`;
6. the referenced context observation index must equal the local bar index;
7. the referenced context and snapshot moments must equal
   `bar_close_timestamp`; and
8. the referenced context must be `NEW_YORK_AM`, `VERIFIED`, and have `OPEN` or
   `EARLY_CLOSE` session status with exact calendar/timezone provenance.

Using the fully closed bar-close moment for evidence reconciliation does not
move the trading window and does not introduce look-ahead. Candidate formation
still begins only after all required source bars are closed.

For the locked five-minute timeframe, the two membership requirements make
`07:00` through `09:50` the only admissible bar-open sequence. The
`09:55`-open/`10:00`-close bar is retained in the canonical dataset result but
is excluded from `GCNYAMSweepReclaimObservation`; it is never relabeled,
silently dropped from the dataset, or represented by synthesized Kill-zone
evidence.

## 10. Exact segment ownership and ordering

Kill-zone public objects do not carry a segment ID. Their segment ownership is
therefore locally recomputable only by exact reconciliation against the
canonical dataset result:

- a context must match exactly one dataset segment and bar by local index,
  normalized timestamp, and calendar-assigned trade date;
- zero matches or more than one match is `INVALID`;
- a snapshot belongs to the unique segment owning every context ID in its
  history;
- all history IDs in one snapshot must belong to that same segment; and
- the flattened public member tuples must be in canonical segment-major order,
  with independently strict local chronology inside each segment.

Direction or hash lexical order is never a chronology tie-break. Historical
insertion, cross-segment movement, repair, or silent sorting is forbidden.

## 11. Exact cumulative snapshot-history validation

For each nonempty canonical segment:

1. its first snapshot history contains exactly its first context ID;
2. every later snapshot history equals the immediately prior history plus the
   current context ID appended once;
3. all history IDs are ordered, unique, already supplied, and owned by the same
   segment;
4. `snapshot.context_ids[-1]` is the context at the snapshot's exact local
   index and normalized timestamp;
5. the snapshot index/timestamp equal that terminal context's effective moment;
6. the snapshot ID is recomputed over the complete ordered cumulative tuple;
   and
7. a skipped, duplicated, substituted, reordered, truncated, cross-segment, or
   future context ID is `INVALID`.

The analyzer must never trim a canonical history down to its terminal member.

## 12. Complete dependency and reference boundary

All `133` dependency segment envelopes must first be verified in canonical
segment order against their immutable segment ID, contract, date bounds, bar
count, observation digest, calendar slice digest, status, reasons, blocking
reasons, result digest, contexts, and snapshots. The exact `101 VALID` / `32
NONE` vector is preserved and is not replaced by an aggregate status claim.

After that preflight, immutable public context and snapshot members may be
placed in a transport-only aggregate `KillZoneResult` required by the unchanged
Phase B public API. This envelope has no identity, does not claim to be a new
upstream detector run, and may not alter any member. Its context and snapshot
tuples must be byte-for-byte identical to the separately supplied complete
tuples. A nonempty envelope is `VALID`; `NONE` is allowed only when both tuples
are empty. Per-segment statuses and digests remain separately authoritative.

## 13. Exact public API boundary

The existing keyword-only public call remains unchanged:

```python
analyze_gc_ny_am_opening_range_sweep_reclaim_reversion(
    *,
    instrument,
    timeframe,
    dataset_config,
    dataset_result,
    requested_trade_dates,
    split_session_calendar,
    kill_zone_calendar,
    observations,
    kill_zone_contexts,
    kill_zone_snapshots,
    kill_zone_result,
)
```

`make_gc_ny_am_sweep_reclaim_id()` parameter names, keyword-only kinds,
identity payload fields, version, enums, frozen dataclasses, and exports remain
unchanged. If the correction cannot be implemented without public API or
identity-payload expansion, work must STOP for a new documentation-only
proposal.

## 14. Segment-aware chronological cutoff and prior evidence

All failure positions must use the exact causal key
`(segment_ordinal, local_index, normalized effective timestamp)`. Comparing
only a local index across segments is forbidden.

When malformed evidence has a determinable causal key:

- final status is `INVALID`;
- strictly prior complete public ranges, candidates, and outcomes remain
  byte-for-byte unchanged;
- the failing effective group and every later group promote nothing; and
- all supplied later evidence is still validated sufficiently to preserve the
  locked final status precedence.

When a trustworthy segment or effective moment cannot be determined, the
result remains fail-closed `INVALID` without a trustworthy-prefix requirement.
Same-effective evidence is one atomic group.

## 15. Status and missing-context precedence

The final precedence remains exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Missing top-level context is `UNKNOWN` only after every independently
determinable supplied counterpart has passed shape, identity, chronology, and
history validation. Missing referenced evidence inside an otherwise complete
accepted segment, member mismatch, cross-segment history, or malformed
unreferenced complete member is `INVALID`. A genuinely truncated strictly
later horizon may be `UNKNOWN` and may not erase strictly prior confirmed
evidence.

## 16. Identity, version, and evidence immutability

Every Kill-zone context identity must be recomputed using the public
`make_kill_zone_id(identity_kind="CONTEXT", ...)` contract and every snapshot
identity using the full cumulative `context_ids` tuple. Phase B observation,
opening-range, candidate, outcome, and manifest identities remain exactly as
committed.

No timestamp shift, index renumbering, context relabeling, history truncation,
member synthesis, foreign hash substitution, timezone fallback, calendar
enrichment, or post-hoc status repair is allowed. The accepted dependency bytes
remain immutable evidence.

The analyzer may filter canonical dataset bars into Phase B observations only
by the exact Section 9 intersection. That deterministic projection is not an
upstream mutation: the terminal `09:55`-open bar remains present in the dataset
and absent only from the Phase B observation tuple because its canonical close
moment cannot produce a `NEW_YORK_AM` identity.

## 17. Unchanged structural hypothesis semantics

This correction does not change:

- the six exact opening-range bars from `07:00` through `07:25` New York;
- formation eligibility from `07:30` inclusive to `09:00` exclusive;
- exact one-tick sweep and reclaim geometry;
- deterministic earliest-candidate selection and opposing ambiguity;
- bullish/bearish mirror rules;
- the strictly later twelve-observation outcome horizon;
- target, invalidation, same-bar ambiguity, timeout, or truncated-horizon
  semantics; or
- any no-outcome, no-PnL, no-training, and no-trading-authority boundary.

The correction changes dependency validation and the deterministic admissible
observation projection only.

## 18. Reserved exact implementation scope

A later, separately authorized test-first implementation may change only:

- `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py`;
- `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py`; and
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md`.

No private runner, upstream Kill-zone module, dataset builder, Candidate
Evidence builder, calendar, shared primitive, configuration, integration,
training, or execution file is included.

## 19. Required test-first implementation behavior

The later implementation must begin with failing public tests and then make the
smallest internal correction that:

1. validates observations in segment-aware canonical order;
2. reconciles context/snapshot moments to the fully closed bar close;
3. validates full segment-local cumulative snapshot histories;
4. permits exact observation-reference subsets of complete evidence;
5. validates every unreferenced complete member fail-closed;
6. derives unique segment ownership without adding public fields;
7. uses segment-aware atomic cutoff and immutable prior-evidence preservation;
8. contains nested exceptions within locked `INVALID` or builder
   `TypeError`/`ValueError` contracts; and
9. excludes the canonical `09:55`-open/`10:00`-close bar from the Phase B
   observation projection without deleting it from the dataset or synthesizing
   context evidence; and
10. preserves all existing structural, identity, public API, and status rules.

The implementation must not read private files or call the upstream Kill-zone
analyzer.

## 20. Independent audit and evidence thresholds

Acceptance of the later implementation requires:

- cache-disabled focused tests for the exact Phase B module;
- cache-disabled full tracked regression using the explicit `tests` path so
  private evidence roots are never traversed by pytest collection;
- exact logical-case reconciliation;
- source/test/checkpoint SHA-256, byte counts, line counts, and timings;
- independent schema, signature, chronology, identity, atomicity, prefix, and
  exact-scope audit;
- no external fixture; and
- no private-run root mutation.

The documentation-only audit reproduced `59 passed in 5.78s` focused and `2453
passed in 21.23s` full explicit-`tests` regression. A bare repository-root
collection was rejected by OS access controls on two private evidence
directories and is not an admissible substitute for the explicit tracked test
scope. The passing tracked tests are still insufficient proof of dependency
compatibility because their synthetic snapshots are singleton and their
observation indices do not exercise canonical cross-segment resets.

## 21. Inline synthetic exact 48-case correction matrix

The exact logical case count remains `48`. Parameterization may increase
collected executions but may not add or remove a logical case.

1. Missing dataset or calendar remains fail-closed with no promotion.
2. Malformed supplied counterpart outranks missing-context `UNKNOWN`.
3. Exact dataset timestamp remains the Phase B bar-close moment.
4. Exact five-minute subtraction remains the Phase B bar-open moment.
5. Context at exact bar close is accepted and the same context at bar open is rejected.
6. Snapshot at exact bar close is accepted and the same snapshot at bar open is rejected.
7. Structural NY-AM membership remains based on bar open while canonical
   Kill-zone membership independently remains based on the fully closed
   evidence timestamp.
8. `07:00`-open/`07:05`-close and `09:50`-open/`09:55`-close bars are admitted;
   the canonical `09:55`-open/`10:00`-close bar remains in the dataset but is
   excluded from Phase B observations, with no synthetic context identity.
9. Segment-local index reset is accepted at the next canonical segment.
10. Non-increasing local index or timestamp inside one segment is `INVALID`.
11. Reordered canonical segment ordinals are `INVALID` without silent sort.
12. Zero-match or multi-match context segment ownership is `INVALID`.
13. All `9,839` complete canonical contexts and snapshots are admissible evidence.
14. The `2,276` NY-AM observation references are an exact subset of complete evidence.
15. A missing or dangling referenced context/snapshot is `INVALID`.
16. A malformed unreferenced complete member is still `INVALID`.
17. Every context identity and common/calendar/timezone field is recomputed exactly.
18. Wrong zone, quality, session status, trade date, or local index is `INVALID`.
19. First segment snapshot singleton history is accepted.
20. Later two-member cumulative history is accepted.
21. Arbitrary later non-singleton cumulative history is accepted.
22. Snapshot terminal context must be the same-moment referenced context.
23. Skipped, substituted, truncated, or reordered history is `INVALID`.
24. Duplicate or future history member is `INVALID`.
25. Cross-segment snapshot history is `INVALID`.
26. Snapshot identity is sensitive to full ordered cumulative history.
27. Context/snapshot effective index and close moment remain exact.
28. Each supplied context has exactly one corresponding canonical snapshot.
29. Transport result tuples must exactly equal separately supplied member tuples.
30. Nonempty transport status is `VALID`; empty `NONE` cannot hide members.
31. Exact `101 VALID` / `32 NONE` per-segment status vector remains preflight evidence.
32. Missing, extra, duplicate, reordered, or digest-drifted dependency segment is rejected.
33. Canonical non-NY-AM history remains complete but creates no Phase B observation.
34. No timestamp shift, relabeling, history trimming, synthesis, or enrichment occurs.
35. Determinably later malformed segment evidence yields final `INVALID`.
36. Same-segment failing effective group and later groups promote nothing.
37. Unknowable malformed ownership requires no trustworthy prefix.
38. Strictly prior complete public evidence remains byte-for-byte immutable.
39. Final precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
40. Exact keyword-only signatures, defaults, frozen dataclasses, enums, and exports pass.
41. Existing Phase B and Kill-zone identity schemas remain exhaustive and unchanged.
42. Opening-range, sweep/reclaim, selection, and outcome semantics remain unchanged.
43. Two fresh public executions reproduce status, reasons, objects, IDs, and manifest bytes.
44. Strictly later complete-segment append preserves every prior public byte.
45. Same-effective append, partial segment, insertion, repair, reorder, or version mutation is ineligible.
46. Focused and full cache-disabled regression evidence reconciles exactly.
47. Only the reserved exact three implementation paths may change in the later task.
48. Private run, features, labels, model, training, OOS, integration, push, and trading remain unused.

## 22. Exact sequential promotion plan

Only this order is admissible:

1. independently audit and locally commit this exact one-file documentation
   record;
2. separately authorize the Section 18 exact three-path test-first correction;
3. run focused/full tests and independent final code, test, scope, hash, and
   checkpoint audit;
4. stage exact paths, perform cached audit and commit preflight, then create a
   local implementation commit;
5. separately authorize and audit any push;
6. create a refreshed documentation-only private-run proposal bound to the new
   committed hashes; and
7. only after that proposal is accepted and committed may an exact private run
   be separately considered.

No step grants authority for the next external or private action.

## 23. Acceptance, rollback, promotion, and STOP conditions

Documentation acceptance requires exactly `24` sequential numbered sections,
exactly `48` sequential logical cases, exact one-file scope, formatting PASS,
SHA-256 and cached-diff audit, and preservation of all unrelated state.

Before commit, rollback restores only this proposal to its exact
`22182d5ae8a6c36e804a4f38c88a8f1b43d7c330` committed bytes. After commit,
rollback is a bounded revert; history rewrite and evidence deletion are
forbidden. STOP on public API or identity expansion, scope drift, private-root
mutation, upstream evidence mutation, ambiguous segment ownership, silent
sorting, member synthesis, timestamp shifting, history trimming, missing
segment/status/digest proof, exception leakage, nondeterminism, test failure,
OOS contact, training, integration, trading work, broad staging, or push without
exact later authority.

Implementation promotion requires all Section 20 evidence to PASS. Private-run
promotion additionally requires a new accepted proposal bound to the corrected
committed artifact hashes.

## 24. Final bounded decision

The accepted complete Kill-zone dependency remains valid and immutable. The
current Phase B analyzer is `FAIL_CLOSED` against it because its evidence
alignment contract is too narrow, its chronology cutoff is not segment aware,
and its terminal five-minute projection does not enforce the exact intersection
of structural bar-open membership with canonical close-time Kill-zone
membership. No private hypothesis result exists, and no model training has
begun.

PASS for this record authorizes only exact-path staging and a local
documentation commit. It does not authorize the Section 18 implementation,
private execution, feature or label construction, training, OOS access,
integration, trading, or push. The next single task after local acceptance is
the exact three-path test-first implementation correction.
