# GC Futures Phase A Cross-Segment Continuity Feasibility Negative-Outcome Decision

## 1. Decision status

- Record type: documentation-only private-run outcome decision.
- Evidence date: `2026-08-16`.
- Decision: `ACCEPT_FEASIBILITY_EVIDENCE_AND_RETIRE_V1_CANDIDATE_HYPOTHESIS`.
- Candidate, feature/label, model, training, OOS, integration, execution, paper,
  broker, and live authority: `NOT GRANTED`.
- Global code freeze: `ACTIVE`.

The corrected private run is accepted as deterministic, non-promotable
engineering evidence. It does not produce admissible candidate evidence and it
does not reopen the rejected Version-1 Candidate Evidence hypothesis.

## 2. Objective and non-objective

This record answers one question: whether the single deferred segmentation
blind-spot investigation produced evidence sufficient to keep the current V1
Candidate Evidence hypothesis open for another rescue or for training. The
answer is `NO`.

The record does not optimize criteria, reinterpret rejected sequences, invent
a candidate, rank setups, inspect OOS outcomes, compare profitability, or
select a model. Boundary and receiving-group counts are observations, not
targets.

## 3. Exact decision scope

The only authorized changed path is:

- `docs/gc_futures_phase_a_cross_segment_continuity_feasibility_negative_outcome_decision.md`.

The Git-ignored private output root is read-only evidence:

- `private_data/sierra_chart/gc_2026_phase_a_cross_segment_continuity_feasibility_v1/`.

No private artifact, source, test, fixture, dependency, configuration,
integration, runtime, training, or OOS path is changed by this decision. The
three pre-existing unrelated untracked proposal files remain outside scope.

## 4. Repository and proposal binding

The decision was prepared against local `HEAD` and local `origin/main` at:

`897579e846e664d2cf0fcb1d50531d05b4861abc`.

| Evidence | SHA-256 |
|---|---|
| Feasibility proposal | `90130C122C1D07C861B24E350BA8D294E79287E0FE02C4D1ADC01EC49CD15F82` |
| Private-run proposal | `5B53BD06F6C8955F516AF838BE28BC2150122C982B4D79E06B6BD204DC4030ED` |
| Public implementation | `1F59432FD738699015DDD92DC8AEB437D1B3DADE7EF96B1BB816245F05DB34D7` |
| Public tests | `9E666DE295F7F538E81CFE772A1B436E625F5D9644E5136C045C049E458205C4` |
| Implementation checkpoint | `2DD1B7753566C5F3E61D241089254341174A4B4459CDCAAFBE036D98CC69E397` |
| Prior negative-outcome decision | `75DB65DADB89368EE600ED2E59C967136313E5973CF91505CA58F2F8399C0D0B` |
| Prior next-hypothesis selection | `77554406D75B81E279409D1D46F3AC44C89FAD6FC08D010D98DA543016B4181E` |

Identity drift is a STOP condition. This decision preserves every earlier
result and does not rewrite history.

## 5. Immutable private input binding

The private run binds:

- purpose `NON_PROMOTABLE_CROSS_SEGMENT_CONTINUITY_FEASIBILITY`;
- source commit `9d0fb1b2aa477abe2ba7a42f939957f3da73caf2`;
- proposal commit `897579e846e664d2cf0fcb1d50531d05b4861abc`;
- parent proposal commit `ad70be419a5dfc361be06d512e6d8fe8749b2a56`;
- input artifact-set identity
  `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`;
- dataset ID
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural seed ID
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- analyzer version `GC-CROSS-SEGMENT-CONTINUITY-V1`; and
- exact `America/New_York` timezone-data version `2026.2`.

The accepted development dataset is `VALID`, contains `17,404` bars in `133`
segments, and contains no OOS bars.

## 6. Calendar evidence binding

The run binds exactly `68` calendar entries: `67` open and `1`
session-closed. Its calendar version is:

`GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`.

The exact source hashes are:

- `Trading-Hours-Holiday (2).xlsx`:
  `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`;
- `Trading-Hours-Holiday (3).xlsx`:
  `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`;
- `CME_GCC_case_04687271_final_clarification_20260807.eml`:
  `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`.

The boundary-calendar digest is
`5f70052e27655a95fdad6aa69f546a6c84a28743bb6635ca4f55d015c39cad6d`;
the independent canonical-control calendar digest is
`dd16b5734f4dfe54a54c47aa1889302abf92102e6478459b98a8e642732f88f3`.

## 7. Exact private artifact-set identity

The accepted output artifact-set identity is:

`5cd06615f5ec7a55816945b105e442f048cea80e3a63f25018b5a8b6036804bc`.

It contains exactly five files including its self-manifest:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `input_binding_NON_PROMOTABLE_FEASIBILITY.json` | `6,191` | `5CEA6A0124F726C663980E4EBC31D6CD2C5256F49E409ECB7FB4AF3C86595E1A` |
| `continuity_result_NON_PROMOTABLE_FEASIBILITY.json` | `1,186,454` | `347564415B12B1ABFCF24CFA6024BC78F504725FFFE876963926ABBCB56351FD` |
| `validation_report_NON_PROMOTABLE_FEASIBILITY.md` | `589` | `AAAFD0204C34DD2F61043EB7F0131C21E55790A2F18E14FB3FB47B080D659067` |
| `README_NON_PROMOTABLE_FEASIBILITY.md` | `266` | `52B809FC5ACAE7A964FC05AA53621CE4E6EC95C3B38571BD37F4432A71EC85F0` |
| `artifact_manifest_NON_PROMOTABLE_FEASIBILITY.json` | `1,301` | `589F9E3267AB43C04E3104BD2D82CFE2C31D2B2E00DA27C2C6C498E616BBFA6B` |

## 8. Deterministic execution result

The analyzer was called exactly once in each of two fresh independent
executions. The complete results were object-equal and every machine-readable
artifact was byte-equal before atomic publication.

The exact final result is:

- status `UNKNOWN`;
- reason `CANONICAL_CONTROL_UNKNOWN`;
- blocking reason `CANONICAL_CONTROL_UNKNOWN`;
- public continuity manifest `null`;
- `promotion_allowed=false`;
- `feature_label_allowed=false`;
- `training_allowed=false`; and
- `integration_allowed=false`.

No partial output root is accepted.

## 9. Canonical-control result

The canonical Candidate Evidence control is exact and unchanged:

- status `UNKNOWN`;
- `113` promoted complete segment results;
- candidate count `0`;
- no candidate manifest; and
- complete-result digest
  `08effd85e83637b0f0c514ceef7967648aaa774490605a7814be1154d6fef13d`.

The continuity layer did not convert `UNKNOWN` to `NONE` or `VALID`, did not
fabricate a bundle ID, and did not promote the terminal truncated group.

## 10. Boundary population

The deterministic result contains exactly `112` adjacent boundary assessments:

| Decision/reason | Count |
|---|---:|
| `ELIGIBLE` / `ELIGIBLE_STANDARD_BOUNDARY` | `40` |
| `INELIGIBLE` / `PARTIAL_SEGMENT_BOUNDARY` | `71` |
| `INELIGIBLE` / `CONTRACT_BOUNDARY` | `1` |

Contract distribution is `96` `GCJ26-COMEX` assessments and `16`
`GCM26-COMEX` assessments. The contract boundary remains ineligible and no
cross-roll state is carried.

## 11. Receiving-group population

The result contains exactly `162` receiving groups across the `40` eligible
standard boundaries. Each observed group contains one immutable
`DEALING_RANGE` `STRUCTURE_EVENT` reference and one immutable
`FAIR_VALUE_GAP` `GAP` reference at its effective moment.

The references preserve their canonical IDs, histories, first-known moments,
source-moment digests, segment ownership, and public causal order. They are
reference-only diagnostic evidence; they are not candidates or labels.

## 12. Data-quality assessment

| Dimension | Finding | Fitness decision |
|---|---|---|
| Completeness | Exact accepted development population, calendar coverage, control, and output scope reconcile; the canonical control deliberately retains a terminal unresolved horizon. | Adequate for bounded feasibility evidence; inadequate for candidate training data. |
| Uniqueness | Boundary, group, dependency, and artifact identities recompute without duplicate publication. | Pass for deterministic replay. |
| Validity | Dataset, seed, calendars, source chronology, identities, and exact status gate validate. | Pass for the private feasibility purpose only. |
| Integrity | Eight immutable private inputs, three official calendar sources, dependencies, source commits, and proposal hashes remain bound. | Pass within the accepted private bundle. |
| Consistency | Two fresh executions are object-equal and byte-equal. | Pass. |
| Timeliness | Development evidence is frozen; no OOS or future outcome is consulted. | Appropriate for this decision. |

The data is fit to decide feasibility and non-promotion. It is not fit to train,
estimate edge, or claim profitability.

## 13. What the run proves

The run proves only that the committed analyzer can deterministically:

1. classify exact adjacent segment boundaries under authoritative calendar
   evidence;
2. reject partial and contract boundaries without silent repair;
3. preserve immutable prior detector references across eligible standard
   boundaries;
4. identify later receiving groups without backdating first-known evidence;
5. preserve canonical-control status and atomic no-promotion behavior; and
6. publish one exact Git-ignored five-file diagnostic artifact set.

This resolves the engineering feasibility question posed by the one allowed
segmentation-blind-spot investigation.

## 14. What the run does not prove

The run does not prove:

- that a valid V1 candidate exists;
- that any receiving group satisfies the complete V1 candidate contract;
- that cross-segment references improve candidate sufficiency;
- that any feature or label is usable;
- that an ML model can learn an edge;
- that backtest or OOS performance is positive;
- that general detector state may be carried across sessions; or
- that runtime, risk, execution, paper, broker, or live integration is safe.

The `40` eligible boundaries and `162` groups must not be quoted as trades,
setups, or positive samples.

## 15. Segmentation-blind-spot conclusion

The suspected blind spot was real as an engineering boundary: complete
immutable dependency references can exist on one side of an eligible standard
segment boundary and later causal event/FVG groups can exist on the other.

However, the accepted experiment was intentionally non-promotable and the
canonical V1 control remains `UNKNOWN` with zero candidates. Therefore the
blind spot does not supply evidence that the current V1 candidate hypothesis
is viable. It only demonstrates that a separately versioned diagnostic
continuity representation is possible.

## 16. V1 Candidate Evidence retirement decision

The prior next-hypothesis decision deferred immediate retirement only long
enough to run this one minimum non-retirement investigation. That investigation
is now complete. The current V1 Candidate Evidence hypothesis is therefore:

- accepted as a reproducible negative Phase A development result;
- rejected for candidate, feature/label, model, training, OOS, integration,
  execution, and trading promotion; and
- retired from further rescue on the accepted Phase A development coverage.

No third rescue attempt, criterion relaxation, wider horizon, manual repair,
or implicit continuity integration is authorized.

## 17. Continuity analyzer retention boundary

The public continuity analyzer, tests, and checkpoint remain valid engineering
assets. They may be retained for audit, reproducibility, and future separately
preregistered research.

Retention does not make the analyzer part of the current strategy runtime,
candidate builder, feature set, labeler, model, confidence score, risk rule, or
execution path. It must remain OFF and diagnostic-only unless a later formal
proposal establishes a new purpose without rewriting this negative result.

## 18. Atomicity and status precedence

Status precedence remains exactly:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.

Strictly prior complete boundary and receiving-group evidence is immutable. A
failing or incomplete effective group promotes nothing from that group or any
later group. `CANONICAL_CONTROL_UNKNOWN` is not a soft warning and cannot be
suppressed by observed eligible boundaries.

## 19. Promotion decision

Promotion result is `REJECTED`.

There is no public continuity manifest, no candidate bundle, no feature/label
manifest, no model-ready table, and no outcome evidence. The private artifact
set remains non-promotable and Git-ignored. No count, chart pattern, or local
interpretation can override this gate.

## 20. Training, OOS, integration, and trading boundary

The following remain prohibited:

- feature or label construction;
- model installation, fine-tuning, training, selection, or inference;
- OOS or embargo opening, repartitioning, or inspection;
- backtest, PnL, edge, win-rate, or profitability claims;
- local-LLM exposure to private raw market payloads;
- strategy, SMC-context, risk, trace, engine, paper, broker, or live wiring;
- staging private artifacts; and
- remote publication without exact authorization.

No AI training has begun. The project remains in pre-training research and
evidence-governance work.

## 21. Prohibited repairs and future choices

Prohibited repairs include changing segment boundaries, carrying partial
state, weakening identity or causal closure, increasing the next-three-bar
horizon, changing active-range retention, inventing missing calendar facts,
opening OOS to find examples, or selecting criteria because they create more
candidates.

After retirement, the legitimate future choices are limited to:

1. close Phase A and pause strategy research; or
2. documentation-first selection of one new, independently falsifiable GC
   research hypothesis that does not reuse V1 as a disguised rescue.

Neither choice may begin implementation or training from this record.

## 22. Independent audit and regression evidence

Read-only audit confirmed:

- exact five-file private output scope and hashes;
- exact input and artifact-set identities;
- exact `112` boundary and `162` receiving-group counts;
- exact `40` eligible, `71` partial, and `1` contract-boundary decisions;
- exact `UNKNOWN` / `CANONICAL_CONTROL_UNKNOWN` / null-manifest result;
- two independent object-equal and byte-equal executions;
- immutable accepted private inputs and absent task temporary directories;
- no raw bars, features, labels, outcomes, models, trades, or execution payloads
  in the published result; and
- clean tracked worktree and index before this documentation-only record.

Fresh regression evidence on `2026-08-16`:

- focused command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_gc_cross_segment_continuity.py`;
- focused result: `48 passed in 0.59s`;
- full command:
  `.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests`;
- full result: `2346 passed in 13.36s`.

The repo-root pytest discovery command is not the canonical full command because
Git-ignored private directories have restricted ACLs; the explicit `tests`
suite is the accepted regression surface.

## 23. Rollback, promotion, and STOP conditions

Before commit, rollback is deletion of only this decision file. After any
future commit, rollback requires a bounded revert; history rewriting is
forbidden. Private evidence is never deleted or rewritten by rollback.

STOP on source, proposal, calendar, dataset, seed, control, dependency,
artifact, or hash drift; non-determinism; identity mismatch; changed counts or
status; unexpected manifest; test failure; scope drift; private-artifact
mutation; V1 rescue; feature/label work; training; OOS contact; integration;
trading dependency; or remote publication without exact authority.

## 24. Final decision and next single task

The corrected private run passes its exact technical contract and is accepted
as trustworthy non-promotable feasibility evidence. It confirms deterministic
reference-only continuity across eligible standard segment boundaries, but it
does not create admissible Candidate Evidence and does not resolve the
canonical `UNKNOWN` control.

The V1 Candidate Evidence hypothesis is closed and retired on the accepted
Phase A development coverage. Training, OOS, integration, and trading remain
locked.

The next single task is one documentation-only Phase A closure and Phase B
research-direction decision at:

`docs/gc_futures_phase_a_closure_and_phase_b_research_direction_decision.md`

That future record may either pause strategy research or preregister exactly
one new falsifiable GC hypothesis. It may not implement code, add another
diagnostic module, rescue V1, inspect OOS, build features/labels, train a model,
integrate runtime behavior, stage, commit, or push without its own bounded
authorization.

Global code freeze remains active.
