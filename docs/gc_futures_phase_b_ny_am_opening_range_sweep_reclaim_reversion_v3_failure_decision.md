# GC Futures Phase B NY-AM Sweep/Reclaim V3 Failure Decision

## 1. Decision record

- Decision ID: `GC-PHASE-B-NY-AM-SWEEP-RECLAIM-V3-FAILURE-2026-08-17`.
- Decision date: `2026-08-17`.
- Classification: documentation-only private-feasibility failure record.
- Repository execution baseline and proposal commit:
  `a59fc98cc5d513345fe681f93aa98f290b1ce345`.
- Corrected analyzer baseline:
  `d72e80eaea77af7449dc07db90a374a0ca7af6b0`.
- Implementation version:
  `GC-NY-AM-OPENING-RANGE-SWEEP-RECLAIM-REVERSION-V2`.
- Final decision: `HYPOTHESIS_FAIL_NO_PUBLICATION_NO_CORRECTION`.

This record preserves the terminal result of the authorized V3 private
feasibility rerun. It grants no authority to modify the analyzer, inputs,
thresholds, calendars, private evidence, training pipeline, integration, risk,
execution, or trading behavior.

## 2. Governing proposal

The governing execution contract is:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_attested_no_trade_private_rerun_change_proposal.md`

Its proposal ID is
`GC-PHASE-B-NY-AM-SWEEP-RECLAIM-ATTESTED-NO-TRADE-PRIVATE-RERUN-V4`,
its committed SHA-256 is
`B694C0938C2F49383BF88F597C6C3BA292262292D4532FDCEFD5EF1B6F51E5CB`,
and its commit is
`a59fc98cc5d513345fe681f93aa98f290b1ce345`.

Sections 15, 19, 22, and 23 of that contract require `AMBIGUOUS` to publish no
final root, classify the hypothesis as `FAIL`, preserve inputs, forbid rescue
or tuning, and stop for a separately reviewed next proposal.

## 3. Exact documentation-only scope

This decision task may create, audit, stage, and locally commit only:

`docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_v3_failure_decision.md`

Source, tests, private artifacts, input manifests, calendars, fixtures,
features, labels, models, training outputs, OOS evidence, integration,
configuration, package exports, and unrelated untracked files remain frozen.
Remote publication requires separate explicit GitHub privacy/export authority.

## 4. Immutable Phase A input binding

The executed Phase A root remained:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

Its ordered artifact-set identity was
`8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`.
The dataset-result SHA-256 was
`11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E`.
The immutable development partition contained `17,404` bars in `133` ordered
segments, exactly `64` requested trade dates from `2026-02-23` through
`2026-05-22`, contracts `GCJ26-COMEX` and `GCM26-COMEX`, and roll date
`2026-04-01`. OOS membership and access were zero.

## 5. Immutable Kill-zone dependency binding

The complete dependency root remained:

`private_data/sierra_chart/gc_2026_phase_b_ny_am_sweep_reclaim_complete_kill_zone_dependency_v1/`

Its ordered artifact-set identity was
`089e38c945f679674853282b6b730a038d936f3ed2eeaa2f23fe123636df6f05`.
The dependency JSON SHA-256 was
`8E3494BEE9BEBB8EA42E8880F87DED9603D6011AC84719867F21CC5974720112`.
It remained `COMPLETED_NON_PROMOTABLE`, `complete=true`, with `101 VALID` and
`32 NONE` segment results, `9,839` contexts, `9,839` snapshots, and `2,276`
`NEW_YORK_AM` contexts.

## 6. Tracked implementation binding

Execution and diagnosis bound these tracked bytes:

| Path | SHA-256 |
|---|---|
| `analysis/gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `75FFD671FE09FB3BF91D31658E3D990BAA0418578AD3EB503BC417ED4601AF28` |
| `tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py` | `578A2F0E733ADDE0698E6782621A89B6644C3AC4B66486EA3C205D10440DAF91` |
| `docs/gc_futures_phase_b_ny_am_opening_range_sweep_reclaim_reversion_checkpoint.md` | `5F5E340CAC396A4053F0D3231F1ABB931F748C3E24F068EF655B803DE589EE96` |
| `smc/kill_zones.py` | `6655415F82B85D42D20088676A12D4F3883B992CE17B67EAF784188E1CD27D21` |
| `smc/smc_v2_primitives.py` | `091EDFEA9A05E128EED573932C3C98D261E463E828B82C15B28B87FF56A464FD` |

No implementation byte changed during execution, diagnosis, or this decision
record.

## 7. Authorized execution method

Run A and Run B each used fresh independent deserialization and exactly one
semantic call to the committed public analyzer. The runner supplied the exact
immutable dataset, calendar, observation, Kill-zone context, snapshot, and
result contracts. It introduced no repair, exclusion, threshold, window,
attestation override, filesystem parameter, or post-result selection.

The two runs independently reached the same terminal public status. Execution
stopped before final-root publication as required by the governing contract.

## 8. Deterministic two-run terminal result

Run A and Run B each returned:

- public status: `AMBIGUOUS`;
- complete candidates: `54`;
- hypothesis decision: `FAIL`;
- terminal reason including: `AMBIGUOUS_SWEEP_RECLAIM`;
- publication eligibility: `false`.

The terminal status is ineligible even though the candidate-count and
direction/contract minimum gates were otherwise met. `AMBIGUOUS` has higher
precedence than `VALID` and `NONE`; a favorable subset cannot be selected.

## 9. Requested-date funnel

Independent raw-evidence reconciliation produced this exact funnel:

| Measure | Count |
|---|---:|
| Requested trade dates | `64` |
| Complete opening ranges | `63` |
| Attested no-trade opening-range dates | `1` |
| Complete candidates | `54` |
| No-sweep/reclaim dates | `8` |
| Ambiguous groups | `1` |
| Complete outcomes | `54` |
| Incomplete outcome horizons | `0` |

The counts exhaust the requested-date boundary without silent exclusion.

## 10. Candidate composition

The `54` complete candidates split deterministically as follows:

- direction: `29 BEARISH`, `25 BULLISH`;
- contract: `32 GCM26-COMEX`, `22 GCJ26-COMEX`;
- `GCM26-COMEX`: `19 BEARISH`, `13 BULLISH`;
- `GCJ26-COMEX`: `10 BEARISH`, `12 BULLISH`.

These counts satisfy the proposal's minimum occurrence gates but cannot
override the terminal `AMBIGUOUS` status.

## 11. Outcome composition

The `54` complete structural outcomes were:

- `30 INVALIDATED`;
- `23 MIDPOINT_REACHED`;
- `1 TIMEOUT`.

They are occurrence evidence only. They are not entries, exits, labels,
returns, PnL, confidence, strategy decisions, or trading recommendations.

## 12. Attested no-trade preservation

Trade date `2026-03-31`, segment ordinal `74`, segment ID
`09c8048907719ffe99a3de7c6402dcf36e88561eff20a6589b7fc8384b591b6`,
retained only the `07:20` opening-range member. The five absent members were
canonical acquisition-attested gaps. V2 correctly classified the date as
known non-evaluable with `ATTESTED_NO_TRADE_OPENING_RANGE`, promoted no range,
candidate, or outcome, and retained the date in the requested denominator.

This corrected coverage behavior was not the cause of V3 failure.

## 13. No-sweep/reclaim dates

The eight complete dates with no qualifying sweep/reclaim were:

`2026-03-18`, `2026-03-23`, `2026-03-27`, `2026-03-30`, `2026-04-06`,
`2026-04-20`, `2026-05-06`, and `2026-05-18`.

They remained ordinary noncandidate evidence. None was repaired, removed,
relabelled, or used to rescue the hypothesis.

## 14. Exact ambiguous group identity

The sole ambiguous group was:

- trade date: `2026-05-22`;
- contract: `GCM26-COMEX`;
- segment ordinal: `132`;
- segment ID:
  `8607a31f0638bda994e73e0aabd9ed2887ce7d93934ba90f28fd7afef99fb267`;
- source ID:
  `5a0e09eeee7a8b62278b80e54ceeb907be8a847c05b85732fc65e13b965cf435`;
- partition: `DEVELOPMENT`;
- bar count: `276`;
- unique indexes and timestamps: `276` each;
- preceding missing-bar count: `0`.

There was no duplicate, fork, missing suffix, cross-contract substitution, or
historical insertion in this group.

## 15. Opening-range geometry

The six exact opening-range observations were:

| New York open | Index | High tick | Low tick |
|---|---:|---:|---:|
| `07:00` | `156` | `45175` | `45150` |
| `07:05` | `157` | `45182` | `45165` |
| `07:10` | `158` | `45172` | `45145` |
| `07:15` | `159` | `45164` | `45125` |
| `07:20` | `160` | `45145` | `45129` |
| `07:25` | `161` | `45158` | `45123` |

The immutable range was low `45123`, high `45182`, and exact midpoint
`45152.5`.

## 16. Both-boundary formation discriminator

The first formation observation opened at `07:30 America/New_York`, index
`162`, with UTC close `2026-05-22T11:35:00Z` and exact ticks:

- open `45125`;
- high `45184`;
- low `45120`;
- close `45178`;
- volume `160`;
- fully closed: `true`.

The bar swept the lower range boundary by `3` ticks and the upper boundary by
`2` ticks, then closed inside the range. It therefore satisfies both mirrored
formation predicates at the same effective moment.

## 17. Kill-zone and calendar reconciliation

The `2026-05-22` calendar entry was canonical `OPEN`. At observation index
`162`, the dependency supplied exactly one `NEW_YORK_AM`, `VERIFIED`, `OPEN`
context with trade date `2026-05-22`, timezone `America/New_York`, normalized
tzdata `2026.2`, and context ID
`7af63f47238a035cf861d0253ca2e4a42e7ddc0ea3c4aa95243ed623deebef23`.

The corresponding snapshot had ID
`2283f062dad9774d674ae49fc1dc5ebb685d22f53594d721ac44990635446908`,
the same effective moment, matching last-context ID, and ordered history count
`92`. Context and snapshot IDs were unique in the segment.

## 18. Semantic classification decision

The committed analyzer locks a same-observation upper-and-lower sweep as
atomic `AMBIGUOUS_SWEEP_RECLAIM`. Public logical Case 32 and focused test
`test_case_23_both_boundary_formation_is_ambiguous_and_atomic` protect this
boundary. Neither direction may win through enumeration, lexical order,
close proximity, later outcome, or favorable result selection.

The V3 terminal `AMBIGUOUS` is therefore the correct deterministic public
classification.

## 19. Data-quality and defect conclusion

Independent completeness, uniqueness, validity, consistency, and lineage
checks found no evidence that the terminal ambiguity came from data
corruption or a source defect. The group had complete canonical bars, unique
moments, an eligible calendar, verified Kill-zone evidence, mirrored snapshot
history, exact instrument/timeframe alignment, and no missing preceding bar.

No analyzer correction is justified. Changing the direction, dropping the
date, changing a tick threshold, selecting one boundary, or relabelling the
group as `NONE` would change the precommitted hypothesis after observing its
result.

## 20. Anti-overfit and no-rescue boundary

The following actions remain prohibited for this hypothesis:

- exclude `2026-05-22` or any other observed date;
- choose bullish or bearish after observing later price movement;
- alter the one-tick sweep, reclaim, range, window, or precedence semantics;
- use outcome composition to resolve formation ambiguity;
- create a favorable-only subset, feature, label, model, or PnL series;
- access OOS evidence to redesign or validate the failed hypothesis; or
- overwrite historical failure evidence with a new root.

Any alternative treatment requires a new, independently justified,
documentation-only hypothesis proposal before code or private execution.

## 21. Atomic non-publication and rollback state

The exact V3 Run A temporary root, Run B temporary root, and final root were
absent after the terminal result. No five-file output set was published. No
partial manifest, result, input binding, validation report, or README was
promoted.

The rollback state is therefore absence, not deletion or repair. The two
immutable input roots, tracked files, previous historical proposals, and
unrelated untracked files remained unchanged.

## 22. Independent regression and state audit

Cache-disabled focused regression reproduced:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_ny_am_opening_range_sweep_reclaim_reversion.py
59 passed in 9.48s
```

The canonical public suite reproduced:

```text
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
2453 passed in 30.38s
```

Repository-root discovery is not the accepted test surface because
ACL-protected private roots deny pytest collection. The explicit `tests`
suite passed; no ACL or private evidence was changed. HEAD and `origin/main`
were both `a59fc98cc5d513345fe681f93aa98f290b1ce345` before this documentation
task, and no Python process remained active.

## 23. Acceptance, promotion, and STOP conditions

Acceptance requires exact one-file scope, exactly `24` sequential numbered
sections, formatting PASS, full-content and cached-diff audit, SHA-256 and
byte/line evidence, cache-disabled regression PASS, exact-path staging, and a
local documentation commit. This record promotes only an immutable failure
decision; it does not promote the hypothesis or any private artifact.

STOP on scope drift, evidence mismatch, V3-root appearance, tracked-byte or
private-input mutation, semantic rescue, threshold change, OOS contact,
feature/label construction, model/training activity, PnL analysis,
integration, trading authority, broad staging, or remote push without
separate explicit privacy/export authorization.

## 24. Final bounded decision and next single task

The final bounded decision is:

`V3_HYPOTHESIS_FAIL_PRESERVED_NO_PUBLICATION_NO_CODE_CORRECTION`

After independent acceptance and local commit of this exact document, `STOP`
before push. The next single task is push preflight/publication of the
one-file failure-decision commit under separate GitHub privacy/export
authority. Any alternative hypothesis must begin later with a separate
documentation-only proposal; training, OOS, feature/label build, integration,
and trading remain forbidden.
