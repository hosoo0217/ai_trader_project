# Strategy Approval Pipeline

Strategy Approval Pipeline v1 connects Strategy Improvement Suggestions to the
Human Approval Workflow.

This is not live trading. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## Why Strategy Suggestions Need Human Approval

Strategy improvement suggestions are research notes from saved session history
and trend reviews. They can point to useful areas for study, such as repeated
blockers, risk settings, or data quality issues.

Those notes still need human review. A suggestion can be based on a small sample,
an unusual backtest condition, or a pattern that needs more proof before it
becomes a future change proposal.

## How Suggestions Become Approval Requests

The pipeline reads a strategy improvement result and creates one `PENDING` human
approval request for each included suggestion.

Each request keeps the suggestion category, priority, text, reason, risk, and the
human approval requirement. The request is a review item only. It is not a trade
signal and it is not a rule change.

Low priority suggestions can be skipped when the pipeline config sets
`include_low_priority_suggestions` to `False`.

## No Automatic Strategy Change

The pipeline never applies strategy changes automatically. It does not use
`allowed_to_apply`, does not change configuration, does not edit filters, and
does not modify decision logic.

Human approval is required before any future strategy change can even be
considered. Approval should lead to a reviewed proposal, testing, and
documentation before any strategy behavior changes.

## Status Meanings

- `REQUESTS_CREATED`: One or more strategy suggestions became `PENDING` approval
  requests.
- `NO_SUGGESTIONS`: The strategy improvement result had no suggestions to review.
- `SKIPPED`: Suggestions existed, but the pipeline skipped them because of
  configuration.
- `UNKNOWN`: The improvement result could not be read safely.

## How This Protects Capital

The pipeline protects capital by separating research suggestions from strategy
execution. Suggestions can enter a human review queue, but they cannot bypass
risk controls, session filters, spread checks, news filters, SMC, CRT, Order
Flow, or the decision framework.

This keeps the platform conservative: ideas are collected for review, not turned
into automatic behavior.

## Future Plan

Future versions can add:

- approval history logs
- main.py output that summarizes created approval requests
- links from approval requests back to strategy improvement reports
- reviewed change proposals for approved requests
- clearer reporting for skipped suggestions
