# Change Proposal Store

Change Proposal Store v1 saves approved change proposals to a local JSON file
for future review.

This is storage only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## Why Proposal Storage Exists

Approved human decisions can become change proposals. Those proposals should be
saved so the team can review them later with the original request ID, category,
priority, reason, risk, and safety notes.

The store creates a simple audit trail between:

- strategy improvement suggestions
- human approval decisions
- future change proposals
- final human review

## Why Proposals Are Saved For Future Review

A saved proposal is a planning record. It preserves the idea without turning it
into behavior.

This gives humans time to compare the proposal with more backtest sessions, risk
reports, drawdown, data quality, and capital protection rules before anything is
implemented.

## Stored Proposals Do Not Change Strategy

Saving a proposal does not edit strategy code, change configuration, update
filters, or modify decision logic. The store writes JSON records only.

Each stored proposal keeps:

- `human_review_required`
- `auto_implementation_allowed`
- `implementation_allowed`
- `doc_path`, when registered from a markdown proposal document
- `reasons`
- `blocking_reasons`

`auto_implementation_allowed` should remain `False`.

`implementation_allowed` should remain `False` until the proposal has separate
human review, required backtest evidence, and an approved implementation plan.

## Final Human Review Is Required

Final human review is still required before implementation. A saved proposal can
help organize future work, but it cannot approve itself and cannot apply itself.

This protects the system from silently turning research notes into strategy
behavior.

## File Location

By default, proposals are saved to:

```text
reports/change_proposals.json
```

Use `ChangeProposalStoreConfig(output_dir=...)` to choose another folder.

Markdown proposal documents can be registered through the CLI:

```powershell
.\venv\Scripts\python.exe main.py --register-change-proposal-doc docs/orderflow_confirmation_change_proposal.md
```

This registration step only stores the proposal. It is not approval, not
implementation, and not permission to change strategy code. A `NEEDS_BACKTEST`
review is required before any strategy rule change is considered.

## Future Plan

Future versions can add:

- main.py proposal output
- proposal review workflow
- final approval and rejection records
- proposal search by category, priority, or status
- links from proposal records back to approval logs
