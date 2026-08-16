# GC Futures Phase B NY-AM Sweep-Reclaim Private-Run Correction Proposal

## 1. Correction record

- Proposal ID: `GC-PHASE-B-NY-AM-SWEEP-RECLAIM-PRIVATE-RUN-CORRECTION-V1`.
- Decision date: `2026-08-17`.
- Binding repository baseline: `c7a9fc0f18fc305f2f55addc3f42f1ab530454f7`.
- Affected private-run proposal commit: `c7a9fc0f18fc305f2f55addc3f42f1ab530454f7`.
- Binding implementation commit: `c16065b3149454c4b71585573a1f731507336aef`.
- Classification: documentation-only fail-closed correction proposal.
- Current decision: `PRIVATE_RUN_BLOCKED_PENDING_GRAIN_CORRECTION_AND_COMPLETE_KILL_ZONE_EVIDENCE`.

This record authorizes no source change, test change, private execution, private
artifact write, training, OOS access, integration, push, or trading action by
itself. It records the exact defect and the only admissible repair sequence.

## 2. Decision summary

The proposed Phase B private run cannot execute safely against the accepted
development bundle. Two independently material defects exist:

1. the committed analyzer and private-run reconstruction contract require one
   observation for every requested full-session dataset bar while every such
   observation must reference a canonical `NEW_YORK_AM` context; and
2. the accepted Candidate Evidence contains Kill-zone results for only the
   strictly prior `113` of `133` canonical segments because upstream analysis
   stopped fail-closed at its first `UNKNOWN` group.

The first requirement is internally unsatisfiable for non-NY-AM bars. The
second cannot support the locked `64`-trade-date run without inventing or
repairing missing evidence. Both are critical data-integrity blockers. The
previous private-run proposal is therefore non-executable until the exact
sequence in Section 22 is completed.

## 3. Verified repository and worktree baseline

At this correction baseline:

- `HEAD` and local `origin/main` equal
  `c7a9fc0f18fc305f2f55addc3f42f1ab530454f7`;
- the tracked index and tracked worktree are clean;
- the prospective private-run final and temporary roots are absent;
- no Phase B sweep-reclaim private run has executed;
- fresh cache-disabled focused regression is `59 passed in 7.37s`;
- fresh cache-disabled full explicit `tests` regression is
  `2453 passed in 22.27s`;
- no feature, label, PnL, model, training, OOS, integration, or trading action
  has occurred; and
- three unrelated untracked documents remain pre-existing, outside scope, and
  untouched:
  `docs/gc_futures_phase_a_real_data_feature_label_build_change_proposal.md`,
  `docs/gc_futures_real_data_input_binding_change_proposal.md`, and
  `docs/smc_v2_diagnostic_context_integration_change_proposal.md`.

Any tracked baseline drift before acceptance requires a new read-only audit.

## 4. Exact documentation-only scope

The only path authorized in this correction task is:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_private_run_correction_proposal.md`

Only this file may be created, audited, corrected, staged by exact path, and
committed locally. Broad pathspecs, source/test/private-data writes, external
fixtures, run outputs, integration, and push are forbidden. All other tracked
and untracked paths remain frozen.

## 5. Reproduced observation-grain defect

The committed analyzer constructs its positional expected-observation stream
from every canonical bar in every requested trade date. It then requires every
validated observation to reconcile to a canonical Kill-zone context whose zone
is exactly `NEW_YORK_AM`, status is `OPEN` or `EARLY_CLOSE`, and quality is
`VERIFIED`. Exact reference equality also requires the supplied context and
snapshot sets to equal the observation references.

The accepted dataset contains complete Globex-session bars, not only NY-AM
bars. A bar outside `07:00` inclusive through `10:00` exclusive in
`America/New_York` cannot truthfully carry a `NEW_YORK_AM` identity. Relabeling
such a bar would corrupt canonical detector evidence; omitting it under the
current all-bar positional contract yields missing top-level context. The
locked private reconstruction is therefore impossible without an unauthorized
false label, exclusion, or contract change.

## 6. Why public tests did not expose the defect

The exact 48-case public suite uses an inline synthetic segment whose bars all
begin within the NY-AM window. Its fixture constructs a `NEW_YORK_AM` context
and mirrored snapshot for every synthetic bar. This correctly tests pattern
geometry but does not discriminate a full-session canonical segment containing
pre-NY-AM, NY-AM, and post-NY-AM bars.

Passing `59` focused executions and the committed full public regression is not
evidence that the real reconstruction grain is correct. A new full-session
discriminator is mandatory while the exact `48` logical-case count remains
unchanged.

## 7. Manifest-level private evidence finding

The immutable accepted root remains:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Read-only manifest-level reconciliation proves:

| Evidence | Status / count |
|---|---:|
| dataset status | `VALID` |
| canonical segments | `133` |
| canonical bars | `17,404` |
| distinct development trade dates | `64` |
| dataset date span | `2026-02-23` through `2026-05-22` |
| Candidate Evidence status | `UNKNOWN` |
| promoted Candidate Evidence segment results | `113` |
| represented trade dates | `44` |
| represented date span | `2026-02-23` through `2026-04-24` |
| missing suffix segments | `20` |
| missing suffix bars | `5,520` |
| missing suffix date span | `2026-04-27` through `2026-05-22` |
| retained Kill-zone contexts / snapshots | `6,719` / `6,719` |
| retained `NEW_YORK_AM` contexts | `1,556` |

The bound dataset artifact SHA-256 is
`11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E`.
The bound Candidate Evidence artifact SHA-256 is
`7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD`.
No raw private row is reproduced in this record.

## 8. Exact cause of dependency truncation

The Candidate Evidence builder processes canonical segments in order. After
each detector call it returns immediately when the detector status is
`INVALID`, `AMBIGUOUS`, or `UNKNOWN`, preserving only previously promoted
segment results. The accepted Candidate Evidence reached an upstream truncated
confirmation horizon and correctly returned `UNKNOWN` after `113` segments.

This is valid chronological-cutoff behavior for Candidate Evidence. It is not
a complete Kill-zone evidence bundle and must not be relabeled as one. The
remaining `20` segments cannot be recovered by deserializing nonexistent
results, copying prior identities, inferring fixed windows, or silently
rerunning only a convenient suffix inside the Phase B runner.

## 9. Corrected canonical observation grain

The future corrected analyzer accepts exactly one
`GCNYAMSweepReclaimObservation` per canonical bar whose normalized bar-open
moment is inside the fixed `NEW_YORK_AM` interval:

`[07:00:00, 10:00:00) America/New_York`.

Membership is derived from the immutable bar-open timestamp using runtime IANA
timezone conversion, the exact accepted timezone-data version, requested trade
date, and canonical calendar eligibility. Start equality is included; end
equality is excluded. DST offset is database-derived, never hard-coded.

Non-NY-AM dataset bars remain fully validated canonical dataset evidence but
require no sweep-reclaim observation and no NY-AM context reference. They may
not be emitted, relabeled, or used as pattern or outcome evidence.

## 10. Exact one-to-one reconciliation

For every expected NY-AM bar, exactly one observation, one canonical
`KillZoneContext`, and one canonical `KillZoneSnapshot` are required. They must
match exactly on:

- segment ordinal, segment ID, contract, and derived trade date;
- bar index and normalized bar-open/effective timestamp;
- context and snapshot identities;
- instrument, timeframe, calendar version, timezone name, and normalized
  timezone-data version; and
- `NEW_YORK_AM`, `OPEN` or `EARLY_CLOSE`, and `VERIFIED` semantics.

The snapshot must contain only the corresponding context ID. The observation
must preserve canonical integer-tick OHLC, nonnegative integer volume, exact
five-minute open/close interval, and fully closed state. Missing, extra,
duplicate, reordered, forked, cross-segment, cross-contract, cross-date, or
unreconciled evidence is fail-closed.

## 11. Deterministic expected-order contract

The expected NY-AM membership and all three supplied streams use canonical
dataset order:

`(segment_ordinal, bar.index, normalized_bar_open_timestamp)`.

No direction, identity hash, filesystem order, or caller order can replace
chronology. Contexts and snapshots are a deterministic projection of complete
upstream evidence into the same order; filtering to `NEW_YORK_AM` preserves
existing immutable identities and creates no new detector output.

All non-NY-AM contexts remain available in the upstream dependency artifact for
audit but are not analyzer inputs. Supplying them to the exact NY-AM projection
is unrequested evidence and `INVALID`.

## 12. Complete Kill-zone dependency requirement

The Phase B run requires independently generated canonical Kill-zone evidence
for all `133` dataset segments and all `64` requested development trade dates.
Completeness requires every segment to have a recorded result, including an
explicit `NONE` result when no context is emitted. A prefix ending at `113`
segments is not complete even though every retained object is canonical.

The dependency artifact must preserve per-segment input binding, status,
reasons, ordered contexts, ordered snapshots, and public identities. Aggregate
counts must reconcile to the dataset segment/date manifests. Missing suffix,
silent exclusion, status coercion, or identity reconstruction outside the
public Kill-zone analyzer is forbidden.

## 13. Separate dependency-build authority boundary

Complete Kill-zone evidence may be produced only under a later documentation
proposal that binds:

- the exact accepted dataset and calendar hashes;
- committed `smc/kill_zones.py` and dependency hashes;
- the exact per-segment public analyzer call;
- two fresh independent executions;
- an absent temporary and final private output root;
- atomic temporary-to-final publication only after equality and audit; and
- zero OOS, network, feature, label, model, PnL, integration, or trading access.

This correction record does not authorize that build. The existing Candidate
Evidence artifact remains immutable and is neither overwritten nor enriched.

## 14. Opening-range and formation invariance

The setup geometry remains unchanged. The opening range uses exactly the six
NY-AM observations opened at `07:00`, `07:05`, `07:10`, `07:15`, `07:20`, and
`07:25 America/New_York`; it becomes first-known at the `07:25` bar close.
Candidate opens remain start-inclusive/end-exclusive `[07:30, 09:00)`.

One-tick sweep, same-bar reclaim, midpoint equality, earliest qualifying
candidate, bullish/bearish mirror, both-boundary ambiguity, and immutable
range/candidate geometry remain exactly as committed. The grain correction may
not alter a threshold, select a date, or rescue a candidate.

## 15. Outcome-horizon invariance

The formation observation is excluded. Outcome evidence remains the next exact
twelve later observations in the same segment, contract, trade date, and
canonical NY-AM context grain. Because formation opens before `09:00`, a full
twelve-bar five-minute horizon ends before or at the exclusive `10:00` boundary.

Earliest midpoint reach, earliest close-through invalidation, same-bar terminal
ambiguity, exact timeout, and truncated-horizon `UNKNOWN` remain unchanged. A
post-`10:00` bar cannot repair a truncated NY-AM horizon.

## 16. Public API and identity invariance

The exact keyword-only analyzer and identity-builder signatures, parameter
names, defaults, version constant, enums, frozen public dataclasses, exports,
identity kinds, payload fields, canonical Decimal serialization, and reason
vocabulary remain unchanged.

No optional bypass, grain selector, caller threshold, filesystem input,
dependency root, or repair flag may be added. Corrected expected membership may
change a future private manifest hash, but it does not change any public
identity schema.

## 17. Status, atomicity, and prior evidence

Final precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Independently determinable malformed supplied evidence outranks missing context.
An unavailable complete Kill-zone dependency is `UNKNOWN` before private
publication, not permission to infer evidence. One complete trade-date group
promotes atomically; a failing group promotes no opening range, candidate,
outcome, or manifest from that group or later. Strictly prior complete public
objects remain immutable under chronological cutoff.

## 18. Prefix invariance

Prefix invariance applies only to a valid prefix ending at a complete requested
trade-date boundary and an append containing strictly later complete dataset,
calendar, observation, context, and snapshot groups. Prior promoted bytes and
identities must remain equal.

Same-effective append, partial NY-AM window, partial horizon, missing segment
result, historical insertion, calendar repair, reorder, roll change,
timezone-version mutation, or dependency replacement is not an eligible prefix
comparison and must not be used to claim invariance.

## 19. Reserved exact implementation scope

Only a later explicit implementation authorization may change exactly:

- `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py`
- `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py`
- `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md`

The correction must be test-first and use inline synthetic fixtures only. No
other source, dependency, package export, configuration, requirements, private
artifact, or integration path may change. Implementation does not authorize a
private dependency build or Phase B run.

## 20. Required implementation behavior

The future source correction must:

1. validate the complete dataset and calendars before observation projection;
2. compute canonical expected NY-AM membership from immutable bar-open moments;
3. validate the supplied Kill-zone projection and public identities;
4. reconcile observations, contexts, and snapshots one-to-one against that
   membership;
5. reject non-NY-AM supplied projection members without rejecting valid
   non-NY-AM dataset bars;
6. preserve exact opening-range, formation, horizon, identity, status, and
   atomic-cutoff behavior; and
7. contain all malformed nested values within the locked fail-closed result or
   builder `TypeError`/`ValueError` contracts.

The implementation cannot read private files or invoke the upstream Kill-zone
analyzer internally.

## 21. Inline synthetic exact 48-case correction matrix

The exact logical case count remains `48`. Parameterization may increase
collected executions but may not create or remove a logical case.

1. Missing dataset and calendars remain fail-closed with no promotion.
2. Malformed supplied counterpart still outranks missing-context `UNKNOWN`.
3. Non-tuple, duplicate, reordered, and same-effective forked observation fails.
4. Boolean, fractional, negative, non-finite, or unclosed values fail closed.
5. Naive timestamps and timezone/version mismatch fail closed.
6. Non-GC, spot, CFD, option, micro, or ambiguous contract fails.
7. Non-5m, OOS, cross-contract, or malformed canonical segment fails.
8. Missing, closed, holiday, or malformed calendar evidence fails exactly.
9. Early close preventing a complete NY-AM analysis window is ineligible.
10. Six exact `07:00` through `07:25` observations form one range.
11. Five observations are insufficient and a seventh cannot enter the range.
12. Missing middle member or timestamp/index substitution is invalid.
13. Cross-date, cross-segment, and cross-contract membership is invalid.
14. Positive one-tick width passes and zero width fails.
15. Exact midpoint stays Decimal-context and signed-zero independent.
16. Full-session dataset bars before `07:00` remain valid but are not expected observations.
17. Exact `[07:00, 10:00)` NY-AM bars reconcile one-to-one and `10:00` is excluded.
18. Missing, extra, duplicate, or reordered NY-AM observation/context/snapshot is invalid.
19. Non-NY-AM context in the analyzer projection is invalid without relabeling its dataset bar.
20. Exact `07:30` formation start is eligible and earlier evidence is not.
21. Exact `09:00` formation open is ineligible.
22. Upper one-tick sweep and upper-half reclaim creates bearish.
23. Lower one-tick sweep and lower-half reclaim creates bullish.
24. Sub-one-tick excursion, boundary miss, or midpoint equality is noncandidate.
25. Swept-boundary close qualifies and outside-range close does not.
26. Later reclaim cannot relabel an earlier outside-range close.
27. Both-boundary sweep is `AMBIGUOUS` with no candidate.
28. Earliest canonical candidate wins without replacement.
29. Bullish/bearish boundary and invalidation geometry mirrors exactly.
30. Formation is excluded and the next twelve NY-AM observations are the horizon.
31. Earliest bearish midpoint equality produces `MIDPOINT_REACHED`.
32. Earliest bullish midpoint equality produces `MIDPOINT_REACHED`.
33. Exact adverse one-tick close-through produces `INVALIDATED`.
34. Same-bar target/invalidation produces `SAME_BAR_AMBIGUOUS`.
35. Twelve complete no-hit observations produce `TIMEOUT`.
36. Truncated pre-`10:00` horizon is `UNKNOWN` and post-window evidence cannot repair it.
37. Later malformed evidence preserves strictly prior complete objects only.
38. Final precedence remains `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
39. Every identity kind exhausts required, forbidden, nested, and sensitive fields.
40. Ordered horizon/history, exact reasons, and malformed hashes fail closed.
41. Exact keyword-only signatures/defaults, frozen dataclasses, enums, version, and exports pass.
42. Two fresh public executions reproduce objects, counts, status, reasons, and manifest bytes.
43. Complete-date strictly-later append preserves all prior public bytes and identities.
44. Same-effective append, partial group, insertion, repair, reorder, or version mutation is ineligible.
45. `133`-segment dependency completeness rejects the retained `113`-segment prefix.
46. Complete dependency retains explicit per-segment `VALID`/`NONE` results without status coercion.
47. Exact three-path implementation scope and existing private-root immutability pass.
48. Private run, feature, label, PnL, model, training, OOS, integration, push, and trading remain unused.

## 22. Exact sequential promotion plan

Only this order is admissible:

1. accept and locally commit this one-file correction record;
2. separately authorize the exact three-path test-first implementation in
   Section 19, run cache-disabled focused/full tests, audit, and locally commit;
3. create and accept a documentation-only complete Kill-zone dependency-build
   proposal with exact private roots, hashes, schemas, two-run equality, and
   atomic publication;
4. separately authorize and audit that private dependency build;
5. create a refreshed documentation-only Phase B private-run proposal binding
   the corrected implementation and complete dependency artifact hashes; and
6. only then consider a separate exact private-run authorization.

No step implies authority for the next. The original private-run proposal is
retained as historical evidence but cannot be executed or partially amended at
runtime.

## 23. Acceptance, rollback, and STOP conditions

Documentation acceptance requires exactly `24` sequential numbered sections,
exactly `48` sequential logical cases, exact one-file scope, formatting PASS,
exact SHA-256, cached-diff audit, and clean tracked state apart from this file.
The pre-existing unrelated untracked documents remain untouched.

Before commit, rollback is deletion of this exact new file. After commit,
rollback is a bounded revert; history rewrite and evidence deletion are
forbidden. STOP on scope drift, hash drift, private mutation, missing segment or
date, false NY-AM relabeling, silent exclusion/sort/repair, status coercion,
nondeterminism, exception leakage, output-root existence, OOS contact,
feature/label/model/training/PnL/integration/trading work, broad staging, or
push without exact later authority.

## 24. Final bounded decision

The independent pre-run audit is `FAIL_CLOSED`, not a failed hypothesis. No
market hypothesis result exists because execution correctly stopped before
creating output. The accepted dataset, calendars, Candidate Evidence prefix,
public analyzer, and all prior commits remain immutable evidence.

PASS for this documentation record authorizes only its exact-path staging and
local documentation commit. It does not authorize implementation, dependency
construction, private execution, training, integration, or push. The next
single task after local acceptance is the exact three-path test-first
observation-grain correction in Section 19.
