# Change Proposal Review Log

Change Proposal Review Log v1 saves review decisions for change proposals to a
local JSON file.

This is logging only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically implement strategy changes.

## Why The Review Log Exists

Saved change proposals need a review trail. The review log records what a human
decided, who reviewed it when available, and why the proposal is accepted,
rejected, or waiting for more evidence.

The log helps keep proposal review separate from implementation.

## Record Meanings

`ACCEPT` means the proposal is accepted for future reviewed work only.

`REJECT` means the proposal should not move forward.

`NEEDS_MORE_DATA` means more saved history, context, or evidence is needed before
the proposal can move forward.

`NEEDS_BACKTEST` means backtesting is required before the proposal can move
forward.

Each record is audit data. It is not a trade signal and it is not an
implementation step.

## ACCEPT Does Not Implement Strategy Changes

An accepted review does not edit code, change configuration, update filters,
place orders, or generate trade signals.

`implementation_allowed` remains `False`. ACCEPT means future work only.

## Why Logging Protects Capital

The review log protects capital by preserving a clear record of final proposal
review decisions. It helps prevent ideas from quietly moving from proposal to
implementation without evidence, backtesting, and human control.

## File Location

By default, review decisions are saved to:

```text
reports/change_proposal_reviews.json
```

Use `ChangeProposalReviewLogConfig(output_dir=...)` to choose another folder.

## Future Plan

Future versions can add:

- main.py proposal review output
- proposal review history summaries
- implementation plan workflow
- links from review records back to saved proposals
- required backtest evidence records
