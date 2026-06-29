# Change Proposal Review Workflow

Change Proposal Review Workflow v1 records final review decisions for saved
change proposals.

This is review only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, or automatically implement strategy changes.

## Why Proposal Review Exists

Approved human approval decisions can create future change proposals. Those
proposals still need a separate review step before anyone considers
implementation.

The review workflow lets a human decide whether a proposal is ready for future
work, should be rejected, or needs more evidence first.

## Approval Versus Final Proposal Review

Approval means a suggestion was allowed to become a proposal.

Final proposal review asks a different question: is this proposal ready for
future implementation planning?

These are separate gates. Passing one gate does not skip the next one.

## Decision Meanings

- `ACCEPT`: The proposal is accepted for future reviewed work only.
- `REJECT`: The proposal should not move forward.
- `NEEDS_MORE_DATA`: More saved history, context, or evidence is needed.
- `NEEDS_BACKTEST`: Backtesting is required before the proposal can move
  forward.
- `UNKNOWN`: The decision could not be read safely.

## ACCEPT Does Not Implement Changes

`ACCEPT` does not edit strategy code, modify configuration, update filters,
create orders, or create trade signals. It only records that the proposal may be
considered for future human-controlled work.

`implementation_allowed` remains `False`.

## Why Backtesting Is Required

Backtesting helps check whether an idea survives more than one session or one
market condition. It can reveal drawdown, weak sample size, bad data, or
unintended filter behavior before capital is exposed.

## Why This Protects Capital

The review workflow protects capital by keeping proposal acceptance separate
from implementation. A strategy idea must pass through review, evidence, and
testing before any human-controlled implementation plan is considered.

## Future Plan

Future versions can add:

- review log storage
- main.py proposal review output
- implementation plan workflow
- links from review decisions back to saved proposals
- required backtest evidence summaries
