# Approved Change Proposal

Approved Change Proposal v1 converts approved human approval decision records
into future change proposals.

This is planning only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## Why Approved Decisions Become Proposals

An approved human approval decision means a person has allowed an idea to move
forward for more careful review. The next safe step is a change proposal, not an
implementation.

A proposal keeps the original request ID, category, priority, suggestion text,
reason, risk, and safety notes together so the work can be reviewed later.

## Proposals Do Not Change Strategy Automatically

A proposal is not executable code. It is not a configuration change and it is not
a trading instruction.

The proposal text is safe planning language only. It exists to describe what a
human may review, test, and document in the future.

## Final Human Review Is Required

Even when a decision record is approved, the proposal still requires final human
review before implementation. The proposal has:

- `human_review_required=True`
- `auto_implementation_allowed=False`

This keeps approval separate from implementation.

## Status Meanings

- `PROPOSED`: A safe proposal was created from an approved decision record.
- `BLOCKED`: Proposal creation was blocked by safety or configuration.
- `NEEDS_REVIEW`: More review is needed before a proposal can move forward.
- `UNKNOWN`: The approval record could not be read safely.

The result status may also report:

- `PROPOSAL_CREATED`: A proposal was created.
- `NO_APPROVED_DECISION`: The record was not approved, so no proposal was
  created.

## Why This Protects Capital

This protects capital by keeping a clean separation between ideas, approval,
proposal, testing, and implementation. A strategy suggestion cannot jump straight
from approval into behavior.

The proposal step gives humans a place to review risk, data quality, sample size,
and possible unintended effects before anything changes.

## Future Plan

Future versions can add:

- proposal storage
- proposal history output
- main.py output for approved change proposals
- final-review decisions
- links from proposals back to approval logs and strategy improvement reports
