# SMC v2 and Volume Profile Bounded Diagnostic Freeze-Lift Decision

## 1. Decision Record

- Decision ID: `SMC-V2-VP-BOUNDED-FREEZE-LIFT-DECISION-2026-07-19`.
- Decision date: `2026-07-19`.
- Human decision maker: `HOSOO`.
- Documentation reviewer: Codex-assisted review; final human responsibility remains with HOSOO.
- Reviewed freeze-lift review ID: `SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`.
- Repository: `https://github.com/hosoo0217/ai_trader_project.git`.
- Clean documentation parent: `c8a2332b285a66a85ac4f439eba3acf8ec4ef2bb`.
- Parent and live `origin/main` matched before this record was created: `True`.
- Worktree was clean before this record was created: `True`.
- Decision: `APPROVE_BOUNDED_DIAGNOSTIC_FREEZE_LIFT_FOR_SHARED_PRIMITIVES`.
- Decision-record action authorized now: documentation only.
- Python implementation authorized now: `False`.
- Integration authorized now: `False`.
- Commit or push authorized by this record: `False`.

This record documents HOSOO's explicit approval of a narrowly bounded future
exception to the active code freeze. HOSOO also explicitly required that the
formal decision record be prepared first and prohibited Python edits,
implementation, integration, commit, and push during this documentation task.

## 2. Exact Human Decision and Effective-State Interpretation

HOSOO explicitly approved a diagnostic-only code-freeze lift limited to
`smc/smc_v2_primitives.py` and its directly related unit tests, synthetic
fixtures, and documentation.

The governance decision is therefore approved. It does not become an
operational authorization to edit Python merely because this file exists. The
bounded exception becomes effective for code changes only after all of the
following later gates pass:

1. this decision record receives an independent final audit,
2. this decision record is checkpointed separately from code,
3. `HEAD`, local `origin/main`, and live remote identity are reconciled,
4. the worktree is clean and the full regression baseline passes,
5. an exact first-task implementation preflight passes, and
6. HOSOO separately and explicitly authorizes the Python implementation task.

Until those gates pass, the approved decision is recorded but held in a
non-operational state. This interpretation preserves both parts of HOSOO's
instruction: approve the bounded lift, but do not begin Python work now.

## 3. Locked Decision Inputs

The decision relies on the following exact documentation inputs:

- implementation plan:
  `13512D8C176BAEC9AF941583C6E1E93C5D3C2E18E824ECD7D4B0B5F72A19409D`
- recommended specification:
  `039B0A22D2BA3C972B74D27B1D96A8AA42CCB3FFA3C0D737CEAB13D61403EDB9`
- formal change proposal:
  `3089BA1CDACCC4353D16D8B3A6BC28D0D21219C1C7AFE2D88B6F0F2936D2E210`
- proposal review:
  `C94DDD8843DC849D1F3C141DAA8942F94C11F23CC189B99AFD7E45A4898762FA`
- diagnostic freeze-lift review:
  `733ADF45AE5DDC5F14E40319E443015E3FBE2375EBEF55349E110564B1E91DB4`
- independent readiness audit:
  `B61BB39E832A94BB4C1C671DBE2AF90AFAF616EC17DC564BFF5E7A68E63C5427`

The readiness audit classification was
`READY FOR EXPLICIT BOUNDED DIAGNOSTIC FREEZE-LIFT DECISION`. This record
answers that pending human decision for the narrower shared-primitives task
only. It does not approve the broader detector envelope reviewed elsewhere.

## 4. Change Authorized in the Current Documentation Task

The only repository change authorized while preparing this record is:

- `docs/smc_v2_volume_profile_diagnostic_freeze_lift_decision.md`

No existing documentation file may be silently rewritten as part of this task.
No Python, configuration, test, fixture, runner, strategy, risk, Order Flow,
exporter, or external evidence file may be created or modified now.

## 5. Reserved Exact Scope for the First Later Implementation Task

If the later implementation preflight and explicit Python authorization pass,
the first task is reserved to the following exact paths:

- production module: `smc/smc_v2_primitives.py`
- dedicated unit tests: `tests/test_smc_v2_primitives.py`
- optional synthetic fixture file, only if inline fixtures are insufficient:
  `tests/fixtures/smc_v2_primitives_cases.json`
- implementation checkpoint documentation:
  `docs/smc_v2_volume_profile_shared_primitives_checkpoint.md`

Inline synthetic fixtures in `tests/test_smc_v2_primitives.py` are preferred.
The optional JSON fixture must not be created unless the implementation
preflight records a concrete need for it. No other path is implied by the words
"directly related."

Any need to edit an additional file is a stop condition requiring a new scope
review and explicit human approval before that edit occurs.

## 6. Reserved Functional Scope of Shared Primitives

The later first module may implement only reusable, standalone foundations
required by the accepted specification:

- positive instrument-tick validation and deterministic tick normalization,
- stable chronological source-index identity,
- separate event and first-known confirmation indices and timestamps,
- shared direction, side, data-quality, and ambiguity vocabulary where needed,
- immutable zone boundaries and separately represented lifecycle transitions,
- the reviewed lifecycle vocabulary where applicable,
- deterministic identifiers derived only from reviewed stable inputs,
- validation that returns explicit invalid, unknown, none, or ambiguous states
  instead of inventing missing context,
- test-only helpers required to prove prefix invariance.

The module must remain domain-generic. It may not detect FVGs, Order Blocks,
Breaker Blocks, Mitigation Blocks, Equal Highs or Lows, liquidity maps, Dealing
Ranges, Inducement, kill zones, or Volume Profile in this first task.

## 7. Direct Test and Fixture Contract

The later dedicated tests must be deterministic and synthetic. At minimum, the
implementation preflight must map tests for:

- valid and invalid positive tick sizes,
- exact tick-boundary and floating-point normalization behavior,
- event-time versus first-known-time separation,
- insufficient and invalid input behavior,
- deterministic identifier stability and relevant tie cases,
- lifecycle transition validity and terminal-state handling,
- immutable boundary preservation,
- prefix invariance under appended future observations,
- repeatability across identical runs.

Fixtures must contain no private market data, candidate OOS rows, account data,
broker data, credentials, copied generated evidence, or outcome-derived values.
Fixture constants must be obviously synthetic and documented as such.

## 8. Exact Forbidden Scope

This decision does not authorize:

- edits to any existing Python file,
- edits to `smc/__init__.py` or any package export file,
- any detector module beyond `smc/smc_v2_primitives.py`,
- runner, CLI, `main.py`, or report-schema changes,
- DecisionContext, context-alignment, current SMC, CRT, or Order Flow integration,
- imports or calls from an existing production or execution path,
- action, allowed-status, confidence, trade-filter, or signal changes,
- risk, sizing, stop, target, entry, exit, balance, or PnL changes,
- paper, broker, live, MT5, Sierra live, CME live, or external-API work,
- parameter tuning, optimization, favorable reruns, or use of saved OOS outcomes,
- private data, generated validation reports, or external evidence changes,
- Fibonacci analysis,
- diagnostic trace wiring,
- implementation of a second phase or detector.

The existing strategy and execution behavior must remain byte-for-byte and
semantically unchanged by the later first task.

## 9. Isolation and Default-Off Requirements

The reserved module must be standalone and inert unless directly imported by its
dedicated tests. It must not be imported by current production modules. It must
not register itself, instantiate automatically, read configuration implicitly,
perform I/O, access the network, read external evidence, or mutate global state.

The first task defines no runtime feature flag because no runtime integration is
authorized. Feature flags and trace wiring remain later, separate gates. Direct
test imports do not constitute runtime integration.

## 10. Mandatory Pre-Implementation Gate

Before any Python edit, a later read-only preflight must confirm:

1. this decision record passed independent validation and is hash-locked,
2. its documentation checkpoint is present on local and live `main`,
3. the checkpoint commit contains documentation only,
4. the worktree is clean and Sierra Chart is not required,
5. the full pytest baseline passes from the clean implementation parent,
6. all reserved first-task targets are absent or match an explicitly reviewed
   continuation state,
7. no unrelated staged, unstaged, or untracked file is present,
8. exact accepted types, functions, invariants, and test cases are listed,
9. rollback commands and stop conditions are recorded, and
10. HOSOO explicitly authorizes implementation after reviewing the preflight.

Passing this documentation decision alone is insufficient to begin coding.

## 11. Implementation Stop Conditions

If implementation is later authorized, work must stop before further edits if:

- any required path collides unexpectedly,
- an additional file appears necessary,
- a requirement is ambiguous or conflicts with the accepted specification,
- a test would require private, candidate, outcome, or generated evidence,
- prefix invariance cannot be demonstrated,
- deterministic output cannot be demonstrated,
- an existing public interface or output changes,
- focused tests or the full regression suite fail,
- the worktree contains unrelated changes,
- integration appears necessary to test the primitives.

A stop condition does not authorize a workaround or scope expansion.

## 12. Completion and Promotion Gates for the First Task

Writing code would not by itself complete the later first task. Promotion would
require:

- independent review of every changed line,
- exact changed-file scope reconciliation,
- focused primitives tests passing,
- full regression suite passing,
- prefix-invariance and deterministic-ID evidence,
- confirmation of no production import or execution-path change,
- confirmation of no sensitive or external evidence inclusion,
- a completed shared-primitives checkpoint record,
- separate staging, commit, and push gates,
- explicit authorization before any second phase begins.

Successful primitives tests would prove only implementation conformance. They
would not prove trading edge, OOS improvement, readiness, or deployment safety.

## 13. Rollback and Global Freeze Boundary

The global project code freeze remains active. The approved decision is a narrow
exception reserved for one future task and does not weaken any other freeze
boundary.

If the later task fails a gate, all task changes must remain unpromoted and be
reviewed for rollback. Rollback must not use destructive Git commands without
explicit human approval. After rollback, the full regression and clean-scope
audits must pass before any new proposal is considered.

No second module inherits authorization from this decision. Every later phase
requires its own evidence review and explicit approval.

## 14. Final Decision State

Final decision classification:

`APPROVED — BOUNDED SHARED-PRIMITIVES FREEZE-LIFT DECISION RECORDED; OPERATIONAL IMPLEMENTATION AUTHORIZATION PENDING`

- `HUMAN_FREEZE_LIFT_DECISION_APPROVED=True`
- `REVIEW_ID_APPROVED=SMC-V2-VP-FREEZE-LIFT-REVIEW-2026-07-19`
- `GLOBAL_CODE_FREEZE_ACTIVE=True`
- `BOUNDED_FREEZE_LIFT_OPERATIONALLY_EFFECTIVE=False`
- `PYTHON_IMPLEMENTATION_AUTHORIZED=False`
- `INTEGRATION_AUTHORIZED=False`
- `STRATEGY_OR_EXECUTION_CHANGE_AUTHORIZED=False`
- `PAPER_PROGRESSION_AUTHORIZED=False`
- `LIVE_PROGRESSION_AUTHORIZED=False`
- `STAGING_AUTHORIZED=False`
- `COMMIT_AUTHORIZED=False`
- `PUSH_AUTHORIZED=False`
- `CURRENT_TASK_DOCUMENTATION_ONLY=True`

The next authorized action is an independent final audit of this decision record.
No Python implementation may begin from this record-creation task.
