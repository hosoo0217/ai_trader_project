# GC Futures Phase B Next-Hypothesis Selection Decision

## 1. Decision record

- Record ID: `GC-PHASE-B-NEXT-HYPOTHESIS-SELECTION-V1`.
- Decision date: `2026-08-16`.
- Classification: documentation-only research-governance decision.
- Current decision: `SELECT_ONE_FINAL_DEVELOPMENT_HYPOTHESIS_NOT_IMPLEMENTED`.
- Selected hypothesis:
  `GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_V1`.
- Feature, label, model, training, OOS, integration, paper, broker, live, and
  execution authority: `NOT_GRANTED`.
- Global code freeze: active outside this exact file.

This record selects exactly one prospective hypothesis after the deterministic
preflight retirement of the opening-range breakout-continuation V1. It does not
implement an analyzer, inspect private payload rows, create a private result,
change a detector, or claim a trading edge.

## 2. Decision summary

The accepted Phase B continuation analyzer is deterministic and regression
tested, but its immutable feasibility gate requires complete candidates from at
least three canonical GC contracts. The accepted dataset contains segments from
exactly two contracts. That conjunctive gate is false before execution, so the
private run was correctly stopped and V1 was retired without changing its
threshold, window, geometry, horizon, or gate.

The next research question must not rescue V1, count raw-only contracts, or add
another detector stack. This decision selects one simpler and mutually exclusive
price-action hypothesis: a one-tick opening-range boundary sweep whose formation
bar closes back inside the immutable range. It is a reversion hypothesis, not a
continuation candidate under a new name.

This is the final new setup hypothesis permitted on the currently accepted
development evidence. If its separately proposed feasibility gate fails, the
project must stop adding setup families on this dataset and move to prospective
data-coverage expansion before any further strategy selection.

## 3. Binding repository baseline

This decision binds to local repository baseline:

`cd498d874db21f457555f9b5d7136dc5aae877e8`

The exact evidence bindings are:

| Evidence | SHA-256 |
|---|---|
| Phase B continuation private-run STOP record | `5A22CA6DFABD0722B71643FE6E9470D7AB10030CA3C117246E0A67739C6B2A52` |
| Phase B continuation feasibility proposal | `75A049329783501E779AFBA1F198A7BA2BA7C25C7986C601F9D64A7A5BDCA291` |
| Phase B continuation implementation | `6515964B6F8A0C76CD48D9F8E6071947600FA939DC6FAFBD85C000C9A2B478F8` |
| Phase B continuation tests | `654ED7080B0F07FF16FAE38366C0C2274EEC24C6EA3C20368D6D831EAE606BD0` |
| Phase B continuation checkpoint | `D6C61940A2FA5AA8993A75A6E0580C570B591432983CFE161DF91C133C554025` |
| Phase A closure and Phase B direction decision | `B3F2FCAEAC3C2FA87CFFF8D85ED43A9DE883033FDF242389FF17BDD2DD59B0CE` |
| GC AI strategy and training decision | `237655D31C54133E6E3AE49DB59CD3EC32D5B5D3FC436EE476FA00DCD4629688` |

Any baseline, identity, source, test, checkpoint, or decision drift before this
record is accepted is a STOP condition. The local baseline is one commit ahead
of `origin/main`; this record grants no push authority.

## 4. Accepted immutable evidence

The already accepted development evidence remains:

- dataset ID
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- `17,404` fully closed GC five-minute development bars;
- `133` canonical development segments;
- `64` unique accepted development trade dates;
- coverage from `2026-02-23` through `2026-05-22`;
- exact canonical segment contract set
  `{GCJ26-COMEX, GCM26-COMEX}`;
- zero opened OOS bars; and
- no accepted feature table, label table, model, or training artifact.

The retired continuation feasibility result is a predetermined scope failure,
not price-performance evidence. No continuation candidates or outcomes were run,
so their unseen values cannot influence this selection.

## 5. Multiple-hypothesis and research-budget boundary

Repeatedly trying setup families on the same development sample can create
selection bias even when OOS remains sealed. Therefore:

1. this record selects exactly one new hypothesis;
2. its rules and feasibility gates are fixed before any implementation or run;
3. it may be run only after a separate proposal, implementation, audit, and
   explicit private-run authorization;
4. feasibility failure ends new-setup exploration on this accepted dataset;
5. no candidate count, direction balance, outcome, return, chart appearance,
   PnL, or model score may revise this selection; and
6. all retired and failed records remain immutable negative governance evidence.

This is a bounded research budget, not permission to search until a positive
result appears.

## 6. Choices considered

Exactly three choices were considered:

| Choice | Benefit | Principal risk | Decision |
|---|---|---|---|
| Stop all Phase B research now | Eliminates further development-sample selection. | Leaves one simple, mutually exclusive price-action question untested. | Deferred; becomes mandatory if the selected hypothesis fails feasibility. |
| Acquire broader canonical data before another setup | Improves contract breadth and eventual validation strength. | Requires a new acquisition/partition decision and does not answer the already bounded development question. | Required before training; deferred for this one feasibility question. |
| NY-AM opening-range sweep/reclaim reversion | Uses only immutable range and bar evidence and is formation-exclusive from continuation. | Can still be sparse and must not become another rescue loop. | `SELECTED_ONCE`. |

No SMC, CRT, Order Flow, Volume Profile, local-LLM, or indicator ensemble was
considered as a substitute entry signal.

## 7. Deterministic selection criteria

Choices were ranked, in order, by:

1. zero OOS contact and strict no-look-ahead behavior;
2. mutual exclusivity from the retired continuation formation rule;
3. minimum dependency and implementation surface;
4. exact integer-tick and closed-bar semantics;
5. deterministic first-known candidate selection;
6. falsifiability before feature, label, or model work; and
7. an explicit terminal STOP path after one failed feasibility attempt.

Expected profitability, candidate abundance, visual appeal, parameter
flexibility, and ease of obtaining a PASS are forbidden selection criteria.

## 8. Selected prospective hypothesis

The selected hypothesis is:

> After the first six fully closed five-minute bars of the verified New York AM
> window define an immutable opening range, the earliest later bar before
> `09:00 America/New_York` that trades at least one tick beyond exactly one range
> boundary but closes back inside the swept half of the range may identify a short-horizon
> reversion toward the exact range midpoint.

An upper-boundary sweep with an inside close is bearish. A lower-boundary sweep
with an inside close is bullish. This statement is a prospective falsifiable
question, not evidence of an edge or authority to trade.

## 9. Independence from retired continuation V1

The hypotheses are formation-exclusive:

- retired bullish continuation required a close at least one tick above the
  range high;
- retired bearish continuation required a close at least one tick below the
  range low;
- selected upper-sweep reversion requires the formation close inside the range;
- selected lower-sweep reversion requires the formation close inside the range.

The same formation bar cannot satisfy both contracts. A close outside followed
by a later reclaim is not eligible for this selected V1. That exclusion prevents
the new hypothesis from relabelling a failed or retired continuation candidate.

The selected V1 may not inherit, reinterpret, rerun, or replace any private
continuation output. None exists.

## 10. Exact instrument, time, and session scope

Prospective scope is restricted to:

- COMEX Gold Futures `GC` outright contract evidence only;
- exact canonical contract identity, never a spot, CFD, option, micro,
  continuous, synthetic, or back-adjusted symbol;
- fully closed five-minute bars only;
- integer price ticks at exact `Decimal("0.1")` tick size;
- timezone-aware UTC source moments converted with fixed IANA
  `America/New_York` and the accepted runtime tzdata version;
- verified Monday-Friday eligible trade dates from the immutable split-session
  calendar; and
- the accepted `NEW_YORK_AM` Kill-zone context only.

Holiday-closed, early-close-ineligible, unverified-calendar, OOS, partial,
cross-contract, and cross-segment evidence fails closed.

## 11. Immutable required input boundary

A future feasibility proposal may reference only:

- the immutable accepted development dataset and manifest;
- canonical fully closed GC five-minute bars;
- accepted split-session calendar entries;
- canonical Kill-zone calendar entries, contexts, and snapshots;
- exact requested development trade dates; and
- deterministic configuration and dependency identities.

No raw-file rediscovery, filesystem-selected date, external calendar API,
screen image, chart annotation, local LLM judgment, future bar, OOS row, feature,
label, outcome aggregate, PnL, or execution state may determine eligibility.

## 12. Exact opening-range construction

For one canonical segment and trade date, the source range is formed by exactly
six consecutive closed bars whose New York opens are:

`07:00, 07:05, 07:10, 07:15, 07:20, 07:25`.

The immutable range low is the minimum source low and the range high is the
maximum source high. The range must have positive integer-tick width. Its exact
midpoint is `(low_tick + high_tick) / 2` represented canonically as an integer
or half tick without Decimal-context dependence.

Missing, duplicate, reordered, nonconsecutive, substituted, cross-date,
cross-contract, cross-segment, malformed, or unverified-context source evidence
promotes no range.

## 13. Exact sweep and reclaim formation

Eligible formation bars open in the start-inclusive/end-exclusive interval
`[07:30, 09:00) America/New_York` and occur strictly after all six source bars.

An upper sweep requires:

- `high_tick >= range_high_tick + 1`; and
- `midpoint_tick < close_tick <= range_high_tick`.

A lower sweep requires:

- `low_tick <= range_low_tick - 1`; and
- `range_low_tick <= close_tick < midpoint_tick`.

Boundary equality without a one-tick excursion does not sweep. A wick beyond
the boundary with a formation close outside the range does not qualify. The
reclaim is established only by the formation bar's own fully closed evidence;
later-bar reclaim is forbidden in V1. A close exactly at the midpoint is already
at the prospective target and therefore does not form a candidate.

## 14. Direction, ambiguity, and candidate selection

- exact upper-only sweep/reclaim -> `BEARISH`;
- exact lower-only sweep/reclaim -> `BULLISH`;
- both boundaries swept by the same formation bar -> `AMBIGUOUS` group with no
  candidate promotion;
- neither exact sequence -> `NONE` for that bar.

The earliest canonical qualifying formation moment wins within a segment/date.
Equal-moment exact duplicates collapse only after complete identity equality;
forked or contradictory evidence is `INVALID`. Direction or lexical hash order
is never a chronology tie-break.

## 15. Immutable candidate geometry

Candidate identity must bind the immutable range, six source observations,
formation observation, segment, contract, trade date, direction, swept boundary,
sweep extreme, inside close, midpoint, instrument, timeframe, calendar version,
timezone-data version, and first-known formation moment.

For bearish reversion, the known sweep extreme is formation `high_tick`; for
bullish reversion it is formation `low_tick`. No later observation may mutate
the extreme, range boundaries, midpoint, direction, or first-known provenance.

The candidate is analytical point evidence only. It defines no entry fill,
position size, stop order, take-profit order, fee, slippage, PnL, or trading
instruction.

## 16. Prospective outcome and falsification contract

If a later feasibility proposal is independently accepted, outcome assessment
must use only the next exact `12` strictly later closed bars in the same segment,
contract, and trade date. The formation bar is never an outcome bar.

- bearish target: first bar with `low_tick <= midpoint_tick`;
- bearish invalidation: first bar with
  `close_tick >= formation_high_tick + 1`;
- bullish target: first bar with `high_tick >= midpoint_tick`;
- bullish invalidation: first bar with
  `close_tick <= formation_low_tick - 1`;
- target first -> `MIDPOINT_REACHED`;
- invalidation first -> `INVALIDATED`;
- both first occur in one bar -> `SAME_BAR_AMBIGUOUS`;
- neither after all twelve bars -> `TIMEOUT`; and
- fewer than twelve available later bars without an earlier terminal hit ->
  `UNKNOWN` with no outcome promotion.

These outcomes are feasibility diagnostics, not labels or returns.

## 17. Deterministic identity and future API boundary

A later documentation proposal must exhaustively lock versioned identities for
at least `OBSERVATION`, `OPENING_RANGE`, `SWEEP_RECLAIM_CANDIDATE`, `OUTCOME`,
and `MANIFEST`. Every identity must be recomputable from supplied immutable
fields, canonical UTC timestamps, fixed enum values, and ordered causal tuples.

Any future public dataclass must be frozen. Any future analyzer and identity
builder must be exact keyword-only APIs. Filesystem paths, wall clock, random
values, Python object addresses, mutable dictionaries, exception text, chart
drawings, and hidden defaults are forbidden identity inputs.

This selection decision reserves no Python, test, checkpoint, package-export,
configuration, or integration path. Exact contracts belong to the next
documentation-only proposal.

## 18. Chronology, no-look-ahead, and atomicity

Processing must follow supplied canonical order without silent sorting. One
segment/date/moment is an atomic group. A candidate becomes first known only at
the fully closed formation bar. An outcome becomes first known only at its
terminal bar or at completion of the exact twelve-bar horizon.

Later malformed evidence with a determinable moment may preserve only strictly
prior immutable complete objects. The failing group and everything after it
promote nothing. Evidence whose effective moment cannot be trusted returns
`INVALID` without claiming a trustworthy prefix.

Future confirmation, outcome, return, candidate abundance, model score, OOS
membership, or human/LLM opinion may not alter an earlier range or candidate.

## 19. Status precedence and prefix invariance

Aggregate status precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Missing top-level context is `UNKNOWN` only after every independently
determinable supplied counterpart validates. Malformed supplied evidence remains
`INVALID` and cannot be hidden by a missing tuple.

Prefix invariance applies only to a valid prefix ending at a complete atomic
group and a strictly later complete append. Same-effective append, historical
insertion, partial horizon, calendar repair, reorder, contract remap, version
mutation, or OOS append is ineligible for a prefix comparison.

## 20. Prospective feasibility and promotion gates

Before any private run, the next proposal must lock this conjunctive feasibility
PASS gate:

1. at least `30` complete candidates;
2. at least `24` distinct eligible development trade dates;
3. at least `10` bullish and `10` bearish complete candidates;
4. both accepted canonical contracts represented, with at least `8` complete
   candidates from each contract;
5. `100%` identity/count/status/reason/byte reproducibility across two fresh
   runs;
6. zero silent exclusion and a complete requested-date funnel; and
7. zero OOS contact, feature/label creation, PnL calculation, or model use.

The two-contract gate is for development feasibility only and is not training
authority. Model fitting remains forbidden until a later prospective data and
partition decision provides at least three canonical contract months,
chronological training/validation/calibration partitions, purge/embargo, and a
genuinely untouched final OOS period.

FAIL retires this selected V1 without threshold, range, window, formation,
horizon, target, invalidation, or gate rescue. It also ends new-setup selection
on the current accepted dataset.

## 21. Inline synthetic exact 48-case future matrix

The next proposal must preserve exactly these sequential logical cases; test
parameterization may expand assertions without changing the count of `48`:

1. Missing dataset stops before observation construction.
2. Dataset/manifest identity drift is `INVALID`.
3. OOS contact is `INVALID` and promotes nothing.
4. Non-GC, spot, CFD, option, micro, continuous, or ambiguous contract is rejected.
5. Non-five-minute, open, fractional-tick, boolean-tick, or malformed bar is rejected.
6. Calendar and runtime tzdata versions reconcile exactly.
7. Missing calendar coverage is `UNKNOWN` only after supplied evidence validates.
8. Holiday/session-ineligible evidence promotes no range or candidate.
9. Exact six bars at `07:00` through `07:25` form one immutable range.
10. Missing, duplicate, reordered, nonconsecutive, or substituted source bars fail closed.
11. Cross-date, cross-segment, and cross-contract range construction is rejected.
12. Zero-width range promotes nothing.
13. Even-width midpoint is exact integer-tick Decimal text.
14. Odd-width midpoint is exact half-tick Decimal text.
15. Signed zero and arbitrary magnitude remain context-independent.
16. Formation interval is exactly start-inclusive/end-exclusive `[07:30, 09:00)`.
17. Upper one-tick sweep plus inside close forms bearish evidence.
18. Lower one-tick sweep plus inside close forms bullish evidence.
19. Boundary equality without one-tick excursion and midpoint-close equality are `NONE`.
20. Wick excursion with outside close is `NONE`, not a delayed reclaim.
21. Range-low close equality qualifies only for an exact lower sweep.
22. Range-high close equality qualifies only for an exact upper sweep.
23. Both-boundary same-bar sweep is `AMBIGUOUS` with no candidate.
24. Earliest canonical qualifying formation wins.
25. Later qualifying formation cannot replace the first candidate.
26. Exact duplicate collapses; forked same-moment evidence is `INVALID`.
27. Candidate direction and swept-boundary geometry reconcile.
28. Range, source, formation, extreme, close, midpoint, and first-known provenance are immutable.
29. Formation bar is excluded from outcome evaluation.
30. Outcome horizon uses only the next exact twelve same-segment bars.
31. Bearish midpoint-first produces `MIDPOINT_REACHED`.
32. Bullish midpoint-first produces `MIDPOINT_REACHED`.
33. Bearish adverse close-through produces `INVALIDATED`.
34. Bullish adverse close-through produces `INVALIDATED`.
35. Same-bar target/invalidation hit produces `SAME_BAR_AMBIGUOUS`.
36. Twelve-bar no-hit produces `TIMEOUT`.
37. Truncated horizon without earlier terminal hit is `UNKNOWN`.
38. Later malformed evidence preserves only strictly prior immutable evidence.
39. Status precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
40. All five identity kinds reject missing, forbidden, malformed, and sensitive-field drift.
41. Ordered source and outcome history cannot be lexically resorted.
42. Exact keyword-only signatures, defaults, exports, enum values, and frozen fields reconcile.
43. Repeat execution produces byte-identical public evidence.
44. Complete-group strictly-later prefix invariance holds.
45. Same-effective append, repair, reorder, remap, and version mutation are prefix-ineligible.
46. Exact feasibility count/date/direction/two-contract gates reconcile before promotion.
47. Feasibility FAIL creates no private final or temporary artifact and retires V1.
48. Feature, label, PnL, model, training, OOS, integration, execution, push, and trading surfaces remain unused.

## 22. Deferred and rejected work

The following remain stopped:

- continuation V1 rescue or rerun;
- delayed reclaim, multi-bar confirmation, alternate range, wider session, or
  parameter sweep;
- a third setup hypothesis on the same accepted development dataset;
- SMC, CRT, Order Flow, Volume Profile, indicator, or LLM entry voting;
- raw-data repair, synthetic contract creation, continuous-contract stitching,
  or OOS reclassification;
- feature/label generation, PnL backtest, model dependency installation,
  training, calibration, or hyperparameter search; and
- runtime, risk, execution, paper, broker, live, package-export, configuration,
  or decision-trace integration.

The three pre-existing unrelated untracked documentation files are outside this
record and must remain untouched.

## 23. Audit, rollback, promotion, and STOP conditions

Acceptance requires exact one-file scope, exact 24 sequential numbered sections,
exact 48 sequential cases, verified baseline hashes, no formatting error,
cache-disabled focused/full regression PASS, and independent semantic,
structural, scope, and diff audit.

Fresh regression evidence collected for this documentation-only decision is:

- focused retired-V1 analyzer suite:
  `48 passed in 5.51s`; and
- full explicit public test suite:
  `2394 passed in 22.55s`.

Both commands used `-p no:cacheprovider`, completed with exit code `0`, and did
not authorize or execute any private-data analyzer, feature/label builder,
training process, OOS reader, integration, or trading surface.

Before local commit, rollback is deletion of only this file. After local commit,
rollback requires a bounded revert; history rewriting and negative-evidence
deletion are forbidden.

STOP on baseline/hash drift, private-data or OOS access, contradiction with the
retired V1, formation overlap, ambiguous rule, post-result threshold change,
more than one new setup, test failure, nondeterminism, scope drift, unrelated
staging, feature/label/PnL/model/training work, integration, execution, or remote
publication without exact later authority.

Promotion from this record authorizes only the next documentation proposal. It
does not authorize implementation or a private run.

## 24. Final decision and next single task

The exact decision is:

`SELECT_GC_NY_AM_OPENING_RANGE_SWEEP_RECLAIM_REVERSION_V1_FOR_DOCUMENTATION_ONLY_FEASIBILITY_DESIGN`

The hypothesis is distinct from retired continuation because its formation bar
must close inside the range. It is the final new setup permitted on the accepted
development sample. Current training readiness remains `NOT_READY`.

After this exact record passes independent audit and is committed locally, STOP
before push and before implementation. The next single task, only after later
exact direction, is documentation-only preparation of:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_feasibility_change_proposal.md`

That future task may specify deterministic contracts, APIs, identities, tests,
private-run design, rollback, promotion, and STOP conditions. It may not create
Python, tests, fixtures, private artifacts, features, labels, models, training,
OOS results, integration, stage, commit, or push without separately bounded
authority.
