# GC Futures Phase A Development Candidate Coverage Expansion Change Proposal

## 1. Proposal status

- Record ID: `GC-PHASE-A-DEVELOPMENT-CANDIDATE-COVERAGE-EXPANSION-PROPOSAL-V1`.
- Classification: documentation-only bounded change proposal.
- Decision: `READY_FOR_SEPARATE_PRIVATE_BUILD_AUTHORIZATION`.
- Training readiness: `NOT_READY`.
- Current task scope: this one proposal file only.

This proposal pre-registers a larger development-only Candidate Evidence run. It
does not authorize the run itself, Python or test changes, feature or label
construction, model fitting, OOS access, integration, trading, or remote
publication.

## 2. Objective and non-objective

The objective is to increase deterministic development coverage after Candidate
V4 produced a valid `NONE` result on a small engineering sample. The expansion
must preserve every accepted detector criterion and causal boundary.

The objective is not to force a nonempty candidate bundle, tune a rule against
observed outcomes, infer a trading edge, or train an AI model. A repeated
`NONE`, `UNKNOWN`, `AMBIGUOUS`, or `INVALID` result remains admissible evidence
and must not be rewritten into success.

## 3. Immutable accepted baseline

This proposal is based on repository commit
`1b71dfdb9181d247ce20db2ed146ccff53569809` and the following immutable private
evidence:

- accepted dataset ID
  `a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`;
- corrected structural seed ID
  `d0940d67677a15124b44fdb4d91f00614cf0ebed27b3d1168e593ee9758f90aa`;
- corrected structural artifact-set identity
  `1be011a6179eda0629b97f0aa371379e09eba78d5654d23b934f121344d5d618`;
- corrected candidate artifact-set identity
  `579ad45043b50dedb58a518ea2bbc9705d99481db89729652879ed3b08400317`.

The accepted V4 dataset contains `54` development segments, `7103`
development bars, and `0` opened OOS bars. Baseline Candidate Evidence is
deterministic `NONE` with `0` candidates and exact reason
`NO_QUALIFYING_CANDIDATE_EVIDENCE`.

## 4. Exact proposal scope and global freeze

This task may create only:

`docs/gc_futures_phase_a_development_candidate_coverage_expansion_change_proposal.md`

It must not modify source, tests, fixtures, private input/output artifacts,
calendar evidence, manifests, configuration, package exports, integration,
models, or training outputs. The pre-existing unrelated untracked documents
remain untouched. Global code freeze remains active everywhere else.

## 5. Evidence-quality interpretation

Candidate V4 is accepted negative engineering evidence, not a failed run. All
six detector stages completed for all `54` segments, while Inducement emitted
no evidence. The exact funnel was:

| Gate | Passed | Rejected at gate |
|---|---:|---:|
| Equal-liquidity `SWEPT` pool revisions | 66 | - |
| Latest directional external range present and `ACTIVE` | 20 | 46 |
| Pre-group map reconciles internal pool and external target | 10 | 10 |
| Strictly later same-direction event in next three closed bars | 2 | 8 |
| Exact causally linked displacement FVG | 1 | 1 |
| External range remains active through confirmation | 0 | 1 |

No implementation defect was proved. Expansion therefore changes coverage,
not method.

## 6. Exact immutable raw development acquisition set

Only these four canonical full-contract exports may supply the proposed private
development derivative:

| Contract | Canonical file | Rows | Bytes | Observed JST range | SHA-256 |
|---|---|---:|---:|---|---|
| GCG26 | `GCG26_COMEX_5m_186d_export_20260803.txt` | 26,431 | 2,662,983 | `2025-08-27 09:45:00` through `2026-02-25 20:40:00` | `FA3F7F5913E597E09A5003702CF89D2D2D12FC2DC25AC800A6E76FE6F78D8719` |
| GCJ26 | `GCJ26_COMEX_5m_186d_export_20260803.txt` | 25,470 | 2,557,873 | `2025-10-27 09:00:00` through `2026-04-28 14:00:00` | `B7DE3247DB71F4C60602ED7E543E249ABC5D2549B3F454E9DB5868AD61B01E85` |
| GCM26 | `GCM26_COMEX_5m_186d_reacquired_20260804.txt` | 27,369 | 2,732,247 | `2025-12-29 08:00:00` through `2026-06-25 22:30:00` | `E28FE800736F0367611790BDD7E3C4CB5924D1569876D1D3371078AFB795CBB2` |
| GCQ26 | `GCQ26_COMEX_5m_186d_reacquired_20260804.txt` | 27,528 | 2,741,164 | `2026-02-02 08:00:00` through `2026-08-04 01:15:00` | `9BB79F5FB115F09FB6A716136EC1D652D280EB914DFB8FEDB95376A6299C3401` |

The two reacquired files supersede their retained 2026-08-03 exports. A
superseded file, the frozen 30-day GCQ26 OOS snapshot, chart image, email body,
local-LLM output, or manually edited row must not enter the derivative.

## 7. Source immutability and private derivative boundary

The four raw files are immutable inputs. The future run may read them but must
not move, rename, edit, delete, append, normalize in place, or replace them.
Every output must live under a new Git-ignored private directory and carry the
exact source file name, byte count, row count, observed range, and SHA-256 from
Section 6.

The derivative must contain only rows eligible under the accepted public
dataset builder. Copying raw rows into a new file does not make them canonical;
parser, calendar, roll, coverage, and identity validation remain mandatory.

## 8. Authoritative calendar evidence

Calendar construction is bound to:

- `America/New_York` and runtime tzdata `2026.2`;
- the canonical standard GC session, prior calendar day `18:00` inclusive to
  trade date `17:00` exclusive, with the daily maintenance boundary preserved;
- official CME President's Day workbook `Trading-Hours-Holiday (2).xlsx`,
  SHA-256
  `233216F95930FF51599857CEDA05F1BBEBCD5687D37E210B5C68A253CED9FD11`;
- official CME Good Friday workbook `Trading-Hours-Holiday (3).xlsx`, SHA-256
  `CF34ECE770A399F704D754D72735345F4DEB21EE6E6F8DDE1B388DD9CBA0D5D7`;
- the accepted CME GCC closed-date rule in the final clarification EML,
  SHA-256
  `8964183FDD4F9A2D64EB53C7BD9D13CA1CF6FA9C0066226BFABC3C4F6CD02EF2`:
  no trading after the stated close, reopen at `18:00` ET, and assign the next
  eligible business trade date.

Workbook cells must be read as typed values. Shared-string index values must
not be mistaken for trading-hour numbers.

## 9. Exact development interval

The proposed calendar-input interval is `2026-02-18` through `2026-05-22`
inclusive. The proposed emitted development interval is `2026-02-23` through
`2026-05-22` inclusive. Earlier calendar entries are warm-up and initial-roll
proof only.

No source row, session, segment, volume, detector call, candidate, or derived
identity after the `2026-05-22` completed trade date may enter this run. The end
date is deliberately before Memorial Day because accepted evidence does not yet
provide an unambiguous executable production interval for the holiday halt.

## 10. Calendar uncertainty and hard stop

The official Memorial workbook records pre-open/open events but does not itself
express the full production halt interval required by the current immutable
calendar contract. The Juneteenth workbook also contains Saturday events while
the website labels Saturday hours internal-testing-only; that website notice is
not accepted manifest-bound raw evidence.

Therefore this proposal does not normalize or use Memorial, Juneteenth,
Independence Day, or any later 2026 session. Missing exact production semantics
must cause a stop, never an inferred interval, silent discard, or ordinary
standard-session substitution.

## 11. Prospective OOS quarantine

The prospective untouched OOS interval is `2026-07-06` through `2026-07-31`
inclusive. It is outside the proposed development interval and must remain
unopened for bars, outcomes, labels, candidates, summary statistics, charts,
or model evaluation.

The interval `2026-05-23` through `2026-07-05` is an embargo/evidence gap, not
development and not OOS. Neither that gap nor the OOS interval may be used to
decide detector criteria, roll rules, features, labels, hyperparameters, or
model selection. Existing knowledge that raw GCQ26 coverage exists does not
authorize reading its quarantined rows.

## 12. Exact roll contract

Roll policy remains exact `PRIOR_SESSION_VOLUME_DOMINANCE_3`:

1. compare completed prior-session volumes for the active and exact adjacent
   next contract;
2. require strict adjacent-contract dominance for three consecutive eligible
   trade dates;
3. closed dates neither count nor break the streak;
4. make the roll effective only on the next eligible session;
5. permit only monotonic adjacent rolls, never skips or reversals;
6. use no back-adjustment; and
7. prohibit a feature, label, candidate, trade, position, or segment from
   crossing a roll boundary.

The observed third GCM26 dominance on `2026-03-31` may make `2026-04-01` the
first roll-effective date. That date is not hard-coded: the public builder must
derive it from exact completed-session volumes. GCQ26 is supplied only so the
same adjacent comparison remains possible after GCM26 becomes active.

## 13. Exact build configuration

The future private run must use:

```text
instrument="GC"
timeframe="5M"
source_timezone="Asia/Tokyo"
exchange_timezone="America/New_York"
timezone_data_version="2026.2"
tick_size=0.1
initial_contract="GCJ26-COMEX"
initial_trade_date=2026-02-23
roll_confirmation_sessions=3
oos_start_trade_date=2026-07-06
oos_end_trade_date=2026-08-01
```

OOS is represented as the half-open interval `[2026-07-06, 2026-08-01)`. The
private development derivative must end at `2026-05-22`; the gap before OOS is
intentional. Any API or contract unable to represent this without exposing OOS
must stop for a separate proposal.

## 14. Dataset identity and provenance

The expanded dataset must receive a new deterministic dataset ID. It must not
reuse, overwrite, mutate, or claim prefix identity with
`a10f39ba08a86e15bd1696752c762d55456e4bcc65954143d4e1addf1ec7f3a2`.

Identity must bind the exact builder version, normalized configuration,
calendar version and rows, timezone-data version, ordered source IDs, coverage
IDs, completed-session volumes, roll dates, ordered segment identities, and
development/OOS partition. Repeated execution from identical bytes must be
byte-identical. A changed byte, calendar entry, version, order, or boundary must
change the relevant identity or fail closed.

## 15. Detector and candidate semantics remain unchanged

The accepted structural-seed and Candidate Evidence public builders, versions,
keyword-only APIs, reason tokens, identity payloads, and detector configurations
remain unchanged. The future run must use the same deterministic chain:

| Dependency | Locked version | Source SHA-256 |
|---|---|---|
| `analysis/gc_dataset_builder.py` | `GC-DATASET-BUILDER-V3-SPLIT-SESSION` | `79EF499D0010674E7FF194D5CB1415F98E76E60AA3696CAE618AF824AF850843` |
| `analysis/gc_structural_seed_evidence.py` | `GC-STRUCTURAL-SEED-V1` | `B60D7BE3203EB54D6DA7EF0DAC324FCECB0547CEDF08364F8A3881ADC48794A2` |
| `analysis/gc_candidate_evidence_builder.py` | `GC-CANDIDATE-EVIDENCE-V1` | `0599B1C32DA89FB17CDE1F5441273B34EDDCF18AB6077986319CBA16B8B9022F` |

Version or source-hash drift is a STOP condition, not permission to substitute
an unreviewed implementation.

1. Equal Liquidity;
2. Dealing Range;
3. Liquidity Map;
4. Fair Value Gap;
5. Inducement;
6. Kill Zone;
7. Candidate Evidence assembly.

No window widening, tolerance relaxation, terminal-range reuse, invented map
classification, unlinked FVG, manual candidate, synthetic event, weak label,
LLM label, or chart interpretation is permitted.

## 16. Segment-local state and continuity boundary

Canonical detector state remains segment-local. Every segment starts from the
accepted empty detector state, and no active pool, range, FVG, event, snapshot,
or pending horizon may cross a session or roll segment boundary.

The five previously observed geometric cross-segment pool interactions remain
non-promoting research observations. A continuity study would require its own
proposal, identity version, expiry/maintenance/session rules, prefix contract,
and side-by-side shadow output. It must not be mixed into this expansion.

## 17. Causality, atomicity, and failure precedence

Only fully closed bars available at an effective moment may influence that
moment. Same-effective records form one atomic group. A group promotes either
all reconciled detector evidence or none. A later malformed or unresolved group
must preserve strictly prior immutable evidence and promote nothing from the
failing group or after it.

Status precedence remains exact:

`INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`

Missing or uncertain evidence must never be converted to `NONE`, and prior
`VALID` evidence must not suppress a later higher-precedence status.

## 18. No-look-ahead and outcome isolation

Candidate creation must depend only on the immutable detector histories
available at confirmation time. The future run must not read future bars beyond
the locked next-three-closed-bar horizon, candidate outcomes, entry/exit,
stops/targets, PnL, strategy results, model scores, or OOS evidence.

No candidate rule may be selected because it produces more examples. Candidate
count is an output, not an optimization objective.

## 19. Minimum evidence-sufficiency gate

Private feature/label construction remains blocked unless the expanded run:

- is deterministic and independently reconstructable;
- has exact immutable source, calendar, roll, segment, and detector lineage;
- has zero OOS contact and zero embargo contact;
- contains at least one canonical candidate;
- contains no blocking reason, scope drift, partial promotion, or identity
  mismatch; and
- passes an independent code/data/scope audit.

A nonempty candidate bundle is necessary but not sufficient for training. No
minimum class count, performance threshold, or market-edge claim is introduced
here.

## 20. Reserved future private execution scope

A separately authorized build may create only a new Git-ignored private bundle
under an exact path reserved by that later authorization. It must contain:

- immutable input binding;
- normalized calendar evidence used by the run;
- dataset manifest and validation report;
- structural-seed bundle and manifest;
- Candidate Evidence bundle and manifest when promotable;
- deterministic reconstruction and scope-audit records.

It may not modify the existing Phase A/V3/V4 private directories. No private
artifact may be staged, committed, pushed, emailed, or supplied to a local or
remote model.

## 21. Exact 48-case future acceptance matrix

1. Exact four-file canonical acquisition set and all four SHA-256 values pass.
2. Superseded GCM26/GCQ26 exports are rejected as build inputs.
3. Frozen 30-day GCQ26 OOS snapshot is rejected as development input.
4. Raw input byte mutation, rename, move, deletion, or in-place normalization stops.
5. Exact source column/schema/type validation passes without exception leakage.
6. Source timestamp awareness, strict order, uniqueness, and closed-bar rules pass.
7. Runtime `America/New_York` and tzdata `2026.2` reconciliation pass.
8. Standard prior-day `18:00` to trade-date `17:00` session semantics pass.
9. Daily maintenance interval is excluded and conservation evidence reconciles.
10. Presidents Day workbook rows reconcile by product row and typed cell value.
11. Good Friday workbook empty shared-string cells are not interpreted as hour `12`.
12. Closed-date EML rule maps reopen to the next eligible business trade date.
13. Calendar input begins exactly `2026-02-18` and warm-up is non-development.
14. Development output begins exactly `2026-02-23`.
15. Development output ends exactly `2026-05-22`.
16. Any row or session after `2026-05-22` is rejected from this run.
17. Memorial interval is not inferred from incomplete accepted production evidence.
18. Juneteenth Saturday events are neither promoted nor silently discarded.
19. OOS interval is exact half-open `[2026-07-06, 2026-08-01)`.
20. OOS bars, outcomes, summaries, charts, labels, and model access all remain zero.
21. Embargo interval `2026-05-23` through `2026-07-05` is not development or OOS.
22. Exact initial contract and three preceding eligible-session proof reconcile.
23. Completed prior-session volume conservation and adjacent comparison pass.
24. Three consecutive strict dominance sessions are required for a roll.
25. Closed dates neither increment nor reset the roll streak.
26. Roll becomes effective only on the next eligible session.
27. Roll is monotonic, adjacent-only, non-reversing, and unadjusted.
28. `2026-03-31` third dominance is derived, not hard-coded.
29. GCQ26 supplies comparable adjacent coverage after any GCM26 roll.
30. No segment, feature, label, candidate, trade, or position crosses a roll.
31. Expanded dataset receives a new identity and never overwrites V4.
32. Identity sensitivity covers source, calendar, config, coverage, roll, and order.
33. Exact repeat run is byte-identical and ordered deterministically.
34. All detector public versions/configurations and causal criteria remain unchanged.
35. Every segment runs Equal Liquidity through Candidate assembly in fixed order.
36. Segment-local state resets exactly; cross-segment state promotion is rejected.
37. Same-effective evidence is one complete atomic group.
38. Later failure preserves strictly prior immutable evidence and stops promotion.
39. Final status precedence is `INVALID > AMBIGUOUS > UNKNOWN > VALID > NONE`.
40. Missing or truncated evidence remains `UNKNOWN`, never optimized to `NONE`.
41. Candidate confirmation uses only point-in-time closed-bar evidence.
42. Outcome, PnL, entry/exit, model, LLM, and OOS dependencies are forbidden.
43. Zero candidates remains a valid deterministic negative result.
44. Nonempty candidates require exact detector and source lineage.
45. Candidate presence alone does not authorize feature/label construction.
46. Feature/label presence alone does not authorize training or OOS opening.
47. Exact private output scope, no side effects, rollback, and audit evidence pass.
48. Any hash drift, calendar ambiguity, test failure, OOS contact, or scope drift stops.

The matrix is exactly sequential `1..48`. Parameterization may expand test
instances later but must not change the `48` logical cases without a new
proposal.

## 22. Independent audit requirements

Before any private build, an independent read-only audit must confirm:

- repository HEAD and a clean tracked worktree;
- exact raw and calendar artifact hashes;
- exact date partitions and OOS zero-contact enforcement;
- public builder/API/version/hash compatibility;
- no hidden integration, feature/label, model, or trading dependency;
- exact case-matrix and rollback coverage; and
- canonical focused and full regression tests passing.

Audit failure does not authorize a repair outside a separately accepted exact
scope.

Documentation acceptance audit on `2026-08-15` recorded:

- focused dataset/structural/candidate builders: `367 passed in 1.71s` using
  `pytest -q -p no:cacheprovider` on the three exact public test modules;
- full public regression collection: `2298 passed in 13.03s` using
  `pytest -q -p no:cacheprovider tests`;
- direct repository-root collection reached no test failure but was blocked
  during discovery by Windows `PermissionError` on the immutable private V4
  candidate and structural directories. Those private directories were not
  opened or changed; `tests/` is the canonical public regression root for this
  documentation acceptance.

The document has exact `24` numbered sections and an exact sequential `48`-case
matrix. Its raw, calendar, and builder hashes were independently reconciled
against local immutable artifacts and tracked source.

## 23. Rollback, promotion, and STOP conditions

Before this proposal is committed, rollback is deletion of only this new file.
After commit, rollback requires a bounded revert; history rewriting is
forbidden. A future private run must be atomic: on failure, remove only its new
output directory and preserve all immutable sources and accepted bundles.

Stop on source/calendar/hash drift, unresolved Memorial or Juneteenth production
semantics, API/version drift, inability to represent the exact partitions,
non-determinism, exception leakage, test failure, incomplete history, candidate
criterion change, cross-segment promotion, OOS or embargo contact, outcome/PnL
inspection, private-artifact mutation, training, integration, scope drift, or
remote publication without separate explicit authorization.

Promotion from this proposal is limited to a later, separately authorized
private development build. It does not promote a dataset, candidate bundle,
feature, label, model, strategy, or trading decision.

## 24. Final decision and next single task

The proposal is semantically bounded and fail-closed. It expands development
coverage through `2026-05-22`, preserves the prospective OOS quarantine, keeps
all detector semantics unchanged, and stops before unresolved holiday
semantics.

After independent audit and local acceptance of this document, the next single
task is an exact private build proposal or authorization for this locked scope.
No private build, training, feature/label construction, OOS access, integration,
stage, commit, or push is authorized by the document itself.
