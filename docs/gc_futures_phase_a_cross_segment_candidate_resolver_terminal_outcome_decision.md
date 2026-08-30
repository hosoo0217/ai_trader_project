# GC Futures Phase-A Cross-Segment Candidate Resolver Terminal-Outcome Decision

## 1. Decision status

- Record type: documentation-only private-run outcome decision.
- Decision date: `2026-08-31`.
- Decision:
  `ACCEPT_DETERMINISTIC_UNKNOWN_AND_CLOSE_CROSS_SEGMENT_RESOLVER_INVESTIGATION`.
- Promotion decision: `REJECTED`.
- Source/test correction required: `NO`.
- Additional private rerun authorized: `NO`.
- Training, final-OOS, dataset/corpus, feature/label, integration, execution,
  and trading authority: `NOT GRANTED`.
- Global code freeze: `ACTIVE`.

The completed private transaction is accepted as deterministic,
non-promotable diagnostic evidence. It does not create a candidate, resolve
the canonical Phase-A control, reopen Phase A, or justify another rescue run.

## 2. Exact evidence binding

This decision binds the following immutable evidence:

- proposal commit:
  `d39fe7e8b478a4ab0a51c78248052dc0d38d7fed`;
- proposal SHA-256:
  `294F412CCCCE07AEC0FDF56086585673221109AA83EE95BE0E4AD0281196B240`;
- implementation commit:
  `2711e87bc19662408e66cf890b9ba2a1fdfe863a`;
- accepted input artifact-set identity:
  `8dd9eaaf9839a773a93059605e885d153beea81a8ad26712941df27d89270702`;
- output artifact-set identity:
  `149212b76336e77f9c8a8a4d9b48c13a88d8a22e74575585b24bccc2aa438a98`;
- object-graph digest:
  `d89abdbdfe0ef5cafbb9270ff4884005eff5e5ae430561b110d4e57f53c799f1`;
- dataset ID:
  `2303f0f61b12f1c7a743492fe407276dfdda9852f6c6f76be19f3c7ce352b543`;
- structural seed ID:
  `73e4c28a0208531cce2a77d4ecab3cd590ff5929e21fcd3392894442dc4a5c16`;
- calendar version:
  `GC-2026-DEVELOPMENT-COVERAGE-V1-355DD67B4AB605B77F33BB908E1DB48D076E2612611F986FA560F7C3EC4DFFBA`;
  and
- timezone-data version: `2026.2`.

The accepted input remains under:

`private_data/sierra_chart/gc_2026_phase_a_development_candidate_coverage_expansion_v1/`

The immutable diagnostic output remains under:

`private_data/sierra_chart/gc_2026_phase_a_cross_segment_candidate_resolution_v1/`

Both roots remain private. This decision changes neither root.

## 3. Exact completed transaction

The authorized transaction used two independent fresh workers. Each worker
made exactly one direct call to each public stage:

| Public stage | Calls per worker |
|---|---:|
| Candidate Evidence rebuild | 1 |
| Candidate frontier analyzer | 1 |
| Cross-segment continuity analyzer | 1 |
| Cross-segment candidate resolver | 1 |

The complete object graphs and all five output byte streams were identical
between workers before one worker directory was atomically published. Both
worker roots and the ephemeral harness were removed. The accepted eight input
files retained their exact byte lengths and SHA-256 values.

## 4. Exact result

The accepted result is:

- run status: `COMPLETED_NON_PROMOTABLE`;
- frontier ID:
  `13b07cffaf45a2383fb5efd6f6393b9e7b92f5a79e96ee41e9d5fca74a751a5f`;
- continuity status: `UNKNOWN`;
- continuity reason and blocker: `CANONICAL_CONTROL_UNKNOWN`;
- continuity manifest ID:
  `05ccb616b26fa9114bef787fc3a78c66258eab5cd2bebae010e292b1ea81bd0d`;
- resolver status: `UNKNOWN`;
- resolver reason and blocker: `CROSS_SEGMENT_CONFIRMATION_UNRESOLVED`;
- resolution count: `0`;
- candidate promoted: `false`;
- Phase A reopened: `false`;
- training allowed: `false`;
- feature/label allowed: `false`;
- integration allowed: `false`;
- final-OOS outcome accessed: `false`; and
- trading authority: `false`.

`UNKNOWN` is an admissible completed diagnostic status under the locked
transaction. It is not a process exception, artifact failure, or soft warning.

## 5. Read-only result diagnosis

The public resolver accepts only the preserved exact
`CANONICAL_CONTROL_UNKNOWN` continuity branch and the pending
`NEXT_THREE_CLOSED_BARS_INCOMPLETE` horizon contract. It considers only the
immediately adjacent eligible receiving segment and only the exact remaining
prefix of the next-three-closed-bar confirmation window.

For each pending horizon, a resolution candidate exists only when:

1. a receiving group belongs to the exact eligible boundary;
2. its canonical Structure Event confirmation moment occurs in the allowed
   remaining prefix after the source-segment end; and
3. both the Structure Event and Fair Value Gap directions equal the pending
   horizon direction.

The completed result has zero resolutions and the exact resolver status
`UNKNOWN`. Therefore no canonical receiving group survived all locked
confirmation predicates. The compact diagnostic schema intentionally does not
publish a per-rejection subreason that distinguishes a confirmation-moment
miss from a direction miss. That distinction is unnecessary for this terminal
non-promotion decision and must not be reconstructed through another private
run, wider output, manual chart reading, or criteria change.

## 6. Data-quality finding

| Dimension | Finding | Fitness decision |
|---|---|---|
| Completeness | Exact accepted input scope, literal manifest order, calendar evidence, public bindings, and five-file output scope reconcile. | Complete for the bounded diagnostic question. |
| Consistency | Two fresh workers produced equal object graphs and byte streams. | Pass. |
| Integrity | Proposal, implementation, dataset, seed, calendars, dependency hashes, and artifact identities remain bound. | Pass. |
| Validity | All fail-closed gates passed and the resolver returned an allowed `UNKNOWN` result rather than `INVALID`. | Pass for diagnostic use only. |
| Promotion fitness | No cross-segment confirmation resolution exists. | Not fit for candidates, features, labels, training, OOS evaluation, or integration. |

The evidence is trustworthy enough to close the diagnostic question. It is
not evidence of setup frequency, edge, profitability, or model learnability.

## 7. No source correction finding

No public source or test correction is justified by this outcome. The resolver
returned the exact precedence-preserving status specified by its public
contract. Changing any of the following to force a resolution is prohibited:

- the next-three-closed-bar horizon;
- immediate adjacency;
- session or segment boundaries;
- confirmation-moment membership;
- direction equality;
- event/FVG identities or histories;
- pending-horizon identity;
- canonical ordering or status precedence; or
- accepted input bytes, calendars, manifests, or purpose.

The earlier harness corrections addressed transaction plumbing and immutable
binding defects. They do not imply that an authentic `VALID` result must
exist.

## 8. Exact private artifact scope

The final root contains exactly five files including its self-manifest:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `input_binding_NON_PROMOTABLE_DIAGNOSTIC.json` | 6,665 | `BB72D0F919C525A1B448BCF69B1501E1B99BA24C98B01F54DFFB50A8A55068C3` |
| `resolver_result_NON_PROMOTABLE_DIAGNOSTIC.json` | 19,681 | `CEB7902A1A01ADDFD716027D76E52F16826A2DBFC38A19195178F2D0876329A3` |
| `validation_report_NON_PROMOTABLE_DIAGNOSTIC.md` | 1,110 | `354E5943B1F6E0BD56F147368557A11CBACC5EFFEDE6704661CE18926D1B0262` |
| `README_NON_PROMOTABLE_DIAGNOSTIC.md` | 262 | `8E328588927C8F2D78C87CDB815E5F5DCB04AAEADF2D320066C2FCA796C0664B` |
| `artifact_manifest_NON_PROMOTABLE_DIAGNOSTIC.json` | 1,793 | `2CF25F18D33B71ADB4B0B352C66AB15C6864E109DA1E2538933C2F36136C4A00` |

Every self-manifest member hash and byte count independently reconciles with
the published file. The root is Git-ignored and permanently
`NON_PROMOTABLE_DIAGNOSTIC`.

## 9. Phase and research boundary

Phase A remains closed as trustworthy negative development evidence. The V1
Candidate Evidence hypothesis remains retired and may not be rescued through
this resolver, another harness, a wider horizon, manual classification, or a
new serialization.

This archived resolver investigation is now complete. It does not alter the
separately governed Phase-B closure or independent pretraining-corpus records.
Those workstreams must be assessed from their own accepted decisions and
immutable evidence, not from this diagnostic status.

## 10. Training, OOS, integration, and trading boundary

This record does not authorize:

- creation or promotion of candidate evidence;
- dataset or corpus rebuilding;
- feature, label, or target construction;
- model training, tuning, inference, or serialization;
- final-OOS, embargo, PnL, win-rate, or profitability access;
- strategy, runtime, SMC-context, risk, trace, paper, broker, or live wiring;
- local-LLM exposure to raw private market payloads;
- staging or remote publication of private evidence; or
- order creation, modification, cancellation, or execution.

No AI training is started by this decision.

## 11. Repository scope and rollback

The only new path in this documentation task is:

`docs/gc_futures_phase_a_cross_segment_candidate_resolver_terminal_outcome_decision.md`

The three pre-existing unrelated untracked proposal files remain outside
scope and untouched. No public source, test, fixture, accepted private input,
diagnostic output, configuration, dependency, integration, or other document
may change in this task.

Independent acceptance evidence for this record is:

- exact one-file task scope: `PASS`;
- `git diff --check`: `PASS`;
- focused resolver regression:
  `70 passed in 1.25s` with the pytest cache disabled;
- full explicit public regression:
  `2674 passed in 38.31s` with the pytest cache disabled;
- accepted input eight-member byte/hash audit: `PASS`;
- final exact five-file manifest member byte/hash audit: `PASS`;
- public dependency byte audit: `PASS`;
- tracked worktree and Git index: `CLEAN`; and
- local `HEAD` and `origin/main`:
  `d39fe7e8b478a4ab0a51c78248052dc0d38d7fed`.

Before any future commit, rollback is deletion of only this decision file.
After a future bounded commit, rollback requires a normal revert; history
rewriting and private-evidence deletion remain forbidden.

## 12. Next bounded task and STOP

The next safe task is a read-only, repository-level pretraining-readiness
reconciliation. It may compare the accepted Phase-B closure, independent
pretraining corpus, calendar/partition decisions, and this terminal archived
diagnostic only at their published metadata boundaries. It may not inspect
final OOS, rebuild private evidence, train a model, or integrate runtime code.

This outcome record itself stops before staging, commit, push, private rerun,
source/test change, dataset/corpus build, feature/label build, training,
final-OOS access, integration, prediction, strategy, risk, execution, or
trading action.
