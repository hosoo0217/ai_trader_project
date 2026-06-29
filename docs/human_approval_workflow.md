# Human Approval Workflow

Human Approval Workflow v1 records human review decisions for AI strategy
improvement suggestions.

This is not live trading. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## Why Human Approval Exists

AI strategy improvement suggestions are research notes. They can help point to
patterns in saved session history, such as repeated blockers, weak data quality,
or risk settings that deserve review.

Those suggestions still need human judgment. A suggestion can be incomplete,
based on too little history, or correct in one test sample but unsafe in another.
Human approval keeps a person responsible for deciding what deserves more
testing.

## Why Suggestions Must Not Change Strategy Automatically

Automatic strategy changes can create hidden risk. A small rule change can alter
which sessions pass, how often a setup appears, and how much capital would be
exposed in future tests.

For that reason, this workflow only records whether a suggestion was approved,
rejected, or marked for more review. It does not edit code, change configuration,
modify filters, place orders, or produce trade commands.

## Status Meanings

- `PENDING`: The suggestion has been converted into an approval request and is
  waiting for human review.
- `APPROVED`: A human approved the suggestion as permission for a future reviewed
  change proposal.
- `REJECTED`: A human rejected the suggestion. It should not move forward.
- `NEEDS_REVIEW`: A human decided the suggestion needs more study before any
  future proposal can be approved.
- `UNKNOWN`: The request or decision could not be read safely.

## Approval Is Not Automatic Application

Approval means only that a human has allowed a future reviewed change proposal to
move forward. It does not mean the system may automatically change strategy rules.

A later version may create approved change proposals, but those proposals should
still be reviewed, tested, and documented before they affect any paper/demo or
backtest decision logic.

## How This Protects Capital

The workflow protects capital by keeping AI suggestions separated from execution
logic. Suggestions can inform research, but they cannot bypass risk controls,
session filters, spread checks, news filters, SMC, CRT, Order Flow, or human
review.

This separation reduces the chance that one attractive-sounding idea becomes an
untested rule change.

## Future Plan

Future versions can add:

- approval history logs
- searchable review records
- approved change proposals
- links from approvals back to session history and strategy improvement reports
- review notes that explain why a change was approved or rejected
