# Human Approval Decision Log

Human Approval Decision Log v1 saves human approval decisions to a local JSON
file for audit and review.

This is logging only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically change strategy rules.

## Why The Log Exists

Strategy improvement suggestions can become human approval requests. After a
human reviews a request, the decision should be saved so there is a clear record
of what happened and why.

The log helps answer:

- which request was reviewed
- what suggestion it came from
- whether it was approved, rejected, or marked as needing more review
- who reviewed it, when available
- what notes, reasons, or blocking reasons were attached

## What Records Mean

`APPROVE` means a human approved the request as permission for a future reviewed
change proposal.

`REJECT` means a human rejected the request, so it should not move forward.

`NEEDS_REVIEW` means the request needs more study before any future proposal is
considered.

Each record is audit data. It is not a trade signal and it is not a strategy
change.

## Why Logging Protects Capital

The log protects capital by making review decisions traceable. A strategy idea
should not quietly move from suggestion to behavior without a human-readable
record.

Keeping a decision history makes it easier to find unsafe assumptions, repeated
rejections, missing review notes, or approved ideas that still need testing.

## Logged Approval Is Not Automatic Application

Saving an approved decision does not apply the suggestion. The log does not edit
configuration, change filters, modify decision logic, create orders, or connect
to live systems.

Approval should lead only to a future reviewed change proposal, followed by
testing and documentation before any strategy behavior changes.

## Future Plan

Future versions can add:

- main.py approval decision commands
- approval history summaries
- filters by decision, reviewer, category, or priority
- links from decision records back to approval requests
- reviewed change proposal records for approved decisions
