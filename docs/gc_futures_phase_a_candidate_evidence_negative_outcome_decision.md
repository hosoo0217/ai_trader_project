# GC Futures Phase A Candidate Evidence Negative-Outcome Decision

## 1. Decision status

- Record ID: `GC-PHASE-A-CANDIDATE-EVIDENCE-NEGATIVE-OUTCOME-V1`.
- Decision date: `2026-08-15`.
- Classification: documentation-only development-evidence decision.
- Evidence result: `VALID_NEGATIVE_DEVELOPMENT_OUTCOME`.
- Promotion decision: `REJECTED`.
- Training readiness: `NOT_READY`.
- Global code freeze: active outside this exact file.

The expanded development run is deterministic and internally consistent, but
it produced no canonical Candidate Evidence. It is accepted only as negative
engineering evidence for the current locked hypothesis. It does not establish
that GC Futures has no tradable edge, and it does not authorize a rule change,
feature or label construction, model fitting, OOS access, integration, or
trading.

## 2. Objective and non-objective

This record answers one question: whether the accepted expanded Candidate
Evidence run is sufficiently trustworthy and nonempty to advance into the
feature/label and training pipeline. The answer is `NO`.

The record does not optimize detector thresholds, reinterpret rejected
sequences, carry state across segments, select a strategy from outcomes, or
compare trading performance. Candidate count is treated as an observed result,
not a target to be increased.

## 3. Exact evidence scope

The decision is bound to tracked source commit
`07ee48dcb5bf61da623467f4f495e0bdeaf020f9` and the Git-ignored private bundle:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1`

The bundle contains exactly eight files. Its manifest is
`artifact_manifest_DEVELOPMENT_ONLY.json`, with SHA-256
`D0774ACB1ECBB1D99F6BCFA4532447859886925D4FB8332BAC67B522BF862B1D`.
No private bytes were changed by the diagnosis or by this decision record.

## 4. Immutable raw and calendar sources

The exact accepted acquisition hashes are:

| Source | SHA-256 |
|---|---|
| `GCG26` raw export | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| `GCJ26` raw export | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| `GCM26` raw export | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| `GCQ26` raw export | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |
| Presidents Day workbook | `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11` |
| Good Friday workbook | `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7` |
| Final CME GCC email evidence | `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2` |

These hashes identify evidence; they do not make the private sources eligible
for Git, remote upload, local-model ingestion, or redistribution.

## 5. Builder and proposal binding

| Bound component | SHA-256 |
|---|---|
| dataset builder | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| structural-seed builder | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| Candidate Evidence builder | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |
| accepted coverage-expansion proposal | `91E6E2A4983B1A1075FF5ED4AB6A5C05F312F4197F2A4FE52841922DA578FC07` |

The governing proposal is
`docs/gc_futures_phase_a_development_candidate_coverage_expansion_change_proposal.md`.
Its segment-local detector state, exact status precedence, no-look-ahead,
minimum evidence gate, and STOP conditions remain authoritative.

## 6. Private artifact-set identity

The manifest records:

- artifact-set identity
  `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`;
- dataset ID
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural seed ID
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- exactly seven artifacts plus the self-manifest;
- two independent reconstructions; and
- byte equality for dataset, structural seed, and candidate result.

The seven manifest-member hashes are:

| Artifact | SHA-256 |
|---|---|
| `candidate_evidence_DEVELOPMENT_ONLY.json` | `7150C8BE9633DD215C367EFD78D24A39ADAFE432E12D1A8964E5D7F299E343CD` |
| `dataset_build_result_DEVELOPMENT_ONLY.json` | `11A51387AA7ABC595735742CE85BA862FF4F38F33A1BE867D2AFFB020765489E` |
| `input_binding_DEVELOPMENT_ONLY.json` | `E7982293EDB42CC784B85C5047D06FEC86BCDBB5992C5E847171DD78252A43E4` |
| `normalized_calendar_DEVELOPMENT_ONLY.json` | `CCB8BC4034BBC02922278F560BF1AFAC8282A05D3B26611A7EECF6202686F5FC` |
| `README_DEVELOPMENT_ONLY.md` | `7260B5DE117EB845758CC908DF5B40AC553AC9F6BBF7535F57A5B6D4733AD559` |
| `structural_seed_DEVELOPMENT_ONLY.json` | `6D28F3A246A001E1666333D63E0FDB581961D90D92C85224769C5E1E0F2C87D8` |
| `validation_report_DEVELOPMENT_ONLY.md` | `28AE9108A9A6801FF9634E1FDF95121CADC1AEBA32F9CE225ACC12D15FA15ECB` |

## 7. Dataset population and denominator

The dataset is `VALID` and contains:

- `17,404` development bars;
- `133` immutable session/roll segments;
- trade dates `2026-02-23` through `2026-05-22`;
- one roll effective on trade date `2026-04-01`; and
- exactly `0` opened OOS bars.

All rates and counts in this record use the exact `133` supplied development
segments as their denominator unless another denominator is stated. No
successful-only subset replaces the full population.

## 8. Structural-seed coverage

The accepted structural seed contains:

| Member kind | Count |
|---|---:|
| Dealing Range swings | 4,392 |
| Equal Liquidity swings | 4,392 |
| confirmed structure events | 1,410 |
| Fair Value Gap context links | 263 |

An independent in-memory reconstruction reproduced the exact seed ID and all
four member counts. This supports structural reproducibility; it does not by
itself establish candidate sufficiency or market edge.

## 9. Canonical Candidate Evidence result

The accepted build result is:

- run status `COMPLETED_NON_PROMOTABLE`;
- final Candidate Evidence status `UNKNOWN`;
- `113` promoted complete segment results;
- `0` candidates;
- reason `a swept pool has a truncated confirmation horizon`;
- blocking reason `a swept pool has a truncated confirmation horizon`;
- training, feature/label, promotion, and integration flags all `false`.

The run completed without a partial private write. `UNKNOWN` is not silently
converted to `NONE`, `VALID`, or a synthetic candidate.

## 10. Promoted detector-stage profile

Across the `113` promoted complete segment results:

| Detector | `VALID` | `NONE` | Emitted immutable members |
|---|---:|---:|---:|
| Equal Liquidity | 43 | 70 | 544 pool revisions |
| Dealing Range | 48 | 65 | 2,134 range revisions |
| Liquidity Map | 48 | 65 | 2,251 snapshots |
| Fair Value Gap | 58 | 55 | 1,664 gaps and 4,201 transitions/snapshots |
| Kill Zone | 81 | 32 | 6,719 contexts/snapshots |
| Inducement | 0 | 113 | 0 inducements/snapshots |

Inducement reasons are `96` instances of
`no qualifying internal-liquidity sweep was supplied` and `17` instances of
`complete evidence contains no confirmed inducement sequence`.

## 11. Full 133-segment shadow audit

A read-only, non-promoting shadow reconstruction evaluated all `133` segments
with the same locked public semantics and no file writes. The exact funnel was:

| Gate or observation | Count |
|---|---:|
| segment final status `NONE` | 131 |
| segment final status `UNKNOWN` | 2 |
| Equal Liquidity `SWEPT` revisions | 190 |
| segments with any `SWEPT` revision | 57 |
| role-qualified sweeps | 38 |
| segments with a role-qualified sweep | 26 |
| next-three-bar same-direction structure events | 6 |
| exact event plus causally linked FVG sequences | 2 |
| sequences passing active-range retention | 0 |
| truncated confirmation horizons | 2 |
| complete canonical Inducement sequences | 0 |

This shadow result is diagnostic evidence only. It did not replace or mutate
the accepted private artifact.

## 12. Terminal `UNKNOWN` diagnosis

The accepted terminal `UNKNOWN` occurs at segment ordinal `113`, trade date
`2026-04-27`, segment ID
`d26efed86441a98dc505694f8f35a5ad09087df91079e0618ee6f04656d13aa7`.
The segment contains `276` bars from `2026-04-26T22:05:00Z` through
`2026-04-27T21:00:00Z`.

A bullish LOW pool is swept at index `274` (`20:55Z`). Only one strictly later
closed bar is supplied, so the locked next-three-closed-bar horizon cannot be
completed. The exact `UNKNOWN` reason and `next three closed bars are
incomplete` blocking condition are therefore fail-closed expected behavior,
not data corruption or an exception.

## 13. Exact retention failures

The two event-plus-FVG sequences both fail the unchanged rule that the external
range must remain active through confirmation:

| Segment | Direction | Sweep | Confirmation | Active range terminal moment | Reason |
|---:|---|---|---|---|---|
| `0` / `2026-02-23` | bullish | index `161`, `12:30Z` | index `164`, `12:45Z` | superseded index `163`, `12:40Z` | `BOS_PULLBACK_REPLACEMENT` |
| `102` / `2026-04-10` | bearish | index `94`, `05:55Z` | index `97`, `06:10Z` | superseded index `97`, `06:10Z` | `BOS_PULLBACK_REPLACEMENT` |

Both exact internal retention calls produced
`active external range terminated before confirmation`. Accepting either
sequence would change the locked method; it would not repair a source defect.

## 14. Data-quality assessment

| Dimension | Finding | Fitness decision |
|---|---|---|
| Completeness | Development interval and `133` segment population are explicit; two terminal horizons are incomplete by contract. | Adequate for negative engineering evidence; inadequate for candidate training data. |
| Uniqueness | Source order, identities, histories, and manifest members reconcile deterministically. | Pass for replay. |
| Validity | Dataset and seed are canonical; no malformed group or exception leakage was observed. | Pass for the current bounded run. |
| Integrity | Source, calendar, dataset, seed, detector, and candidate lineage are hash-bound. | Pass within the private bundle. |
| Timeliness | Evidence is historical development data through `2026-05-22`; it is not a live-production claim. | Fit only for bounded development research. |
| Leakage | OOS contact is zero; outcomes, entry/exit, PnL, model scores, and future-segment state do not determine candidates. | Pass for this run; OOS remains quarantined. |

No material data-integrity defect was found. The high-severity blocker is
evidence insufficiency: zero canonical candidates and a final higher-precedence
`UNKNOWN` condition.

## 15. Negative-result interpretation

The result means only that no supplied development sequence satisfied every
locked Candidate Evidence condition. It is strong evidence against promoting
the current bounded hypothesis on this development sample.

It does not prove that the market has no edge, that all SMC detectors are
useless, or that a different prospectively specified hypothesis would fail.
The distinction between “no qualifying candidate under this contract” and “no
profitable trading opportunity exists” is mandatory.

## 16. Prohibited interpretations and repairs

The following are forbidden responses to the zero-candidate result:

- widening the next-three-bar window after observing the outcome;
- accepting a terminated external range;
- inventing a map classification, event, FVG link, or candidate;
- carrying detector state across a segment without a new versioned contract;
- weakening identities, atomicity, chronology, or status precedence;
- inserting manual, chart-derived, LLM-derived, or weak labels;
- opening OOS to search for examples; or
- claiming strategy performance from detector counts.

Any such change would be a new research hypothesis and must not overwrite this
negative result.

## 17. Segment-local and continuity boundary

Canonical state remains segment-local. Pools, ranges, maps, FVGs, events,
pending horizons, and snapshots do not cross session or roll segment
boundaries. The full shadow audit did not relax this rule.

Cross-segment continuity may be studied only under a separate prospective,
versioned, documentation-first proposal with explicit session and maintenance
gaps, roll behavior, expiry, identity versioning, prefix invariance, and
side-by-side non-promoting output. It is not authorized here.

## 18. Atomicity and status precedence

Same-effective evidence remains one atomic group. A failing or unresolved group
promotes no partial candidate evidence and preserves strictly prior immutable
evidence. The exact final status precedence remains:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Accordingly, the terminal unresolved horizon is not suppressed by earlier
complete `NONE` results, and no pending sequence is relabelled as a negative
candidate row.

## 19. Promotion decision

Candidate promotion is closed because:

1. canonical candidate count is `0`;
2. final status is `UNKNOWN`, not a fully resolved promotable result;
3. no eligible immutable candidate bundle exists for feature/label input; and
4. the governing proposal explicitly requires at least one canonical candidate
   and no blocking reason before feature/label construction may be considered.

This is a `HIGH`-severity promotion blocker with `HIGH` confidence. It is not a
software-defect finding.

## 20. Training, OOS, integration, and trading boundary

Training must not start. Feature/label construction, model fitting, local-LLM
labelling, hyperparameter search, backtest selection, and OOS opening remain
prohibited. Existing inspected development evidence can never be relabelled as
untouched OOS.

No detector output is wired into execution by this record. No BUY/SELL,
confidence, risk, entry, exit, PnL, order, position, or trading authority is
created. Integration remains unchanged and unauthorized.

## 21. Exact future research choices

Only prospective, separately accepted choices are legitimate:

1. retire the current Candidate Evidence hypothesis as non-promotable on the
   accepted development coverage;
2. specify a new, shadow-only cross-segment continuity hypothesis before
   implementation; or
3. specify a different candidate hypothesis prospectively, preserving the
   accepted acquisition, OOS quarantine, and no-look-ahead boundary.

None may be selected because it recovers the two rejected sequences or
increases candidate count. The current result remains immutable baseline
evidence for comparison.

## 22. Audit and regression evidence

Before this decision was drafted, the private manifest, all member hashes,
source hashes, builder hashes, dataset/seed identities, counts, status fields,
and zero-OOS claim were reconciled read-only. An in-memory reconstruction
matched the stored seed identity and structural counts. Exact retention tracing
produced only the two deterministic failures in section 13 and wrote no files.

Fresh canonical regression evidence for this documentation acceptance is:

- focused dataset, structural-seed, candidate, and Inducement collection:
  `531 passed in 2.12s` using `pytest -q -p no:cacheprovider`;
- full public regression collection: `2298 passed in 12.81s` using
  `pytest -q -p no:cacheprovider tests`.

Fresh acceptance tests, file hash, byte/line counts, cached scope, and diff
checks are recorded by the local commit workflow rather than embedded as a
self-referential document hash.

## 23. Rollback, promotion, and STOP conditions

Before local commit, rollback is deletion of only this new file. After commit,
rollback requires a bounded revert; history rewriting is forbidden. Private
artifacts and the three pre-existing unrelated untracked proposals must remain
untouched.

Stop on source, calendar, proposal, builder, manifest, or identity drift;
non-determinism; test failure; scope drift; private-artifact mutation; criterion
change; cross-segment promotion; feature/label construction; training; OOS
access; integration; trading dependency; or remote publication without a new
exact authorization.

## 24. Final decision and next single task

The expanded Candidate Evidence run is accepted as reproducible negative
development evidence and rejected for promotion. The current canonical rules
remain unchanged. Dataset integrity is not the blocker; candidate sufficiency
is.

After independent audit and local acceptance of this exact document, the next
single task is a separately authorized, documentation-only prospective research
choice record at:

`docs/gc_futures_phase_a_next_hypothesis_selection_decision.md`

That future task may choose one research direction and its stop conditions. It
must not implement code, build features or labels, train a model, inspect OOS,
integrate execution, or reinterpret this negative outcome.
