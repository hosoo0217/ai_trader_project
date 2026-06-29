# Implementation Plan Workflow

Implementation Plan Workflow v1 converts accepted change proposal reviews into
future implementation plans.

This is planning only. It does not connect to a broker, Sierra Chart, CME,
OpenAI, or any external API. It does not create real orders, generate trade
signals, write strategy changes, or automatically implement anything.

## Why Implementation Plans Exist

An accepted proposal review means a human agreed the proposal can move into
future work. The next safe step is an implementation plan, not an implementation.

The plan gathers:

- the objective
- safe proposed steps
- required tests
- risk checks
- rollback notes
- final human approval requirements

## Accepted Proposals Still Do Not Change Strategy

An accepted review does not edit strategy code or configuration. The plan only
describes future work that a human may choose to do later.

`auto_implementation_allowed` remains `False`.

## Backtesting And Final Approval Are Required

Backtesting is required before implementation because a change can look useful in
one review and still fail under broader conditions.

Final human approval is required before any implementation work because the plan
must still be checked for risk, test coverage, rollback safety, and capital
protection.

## Status Meanings

- `PLANNED`: A safe implementation plan was created.
- `BLOCKED`: Plan creation was blocked by safety or missing requirements.
- `NEEDS_BACKTEST`: More backtesting is required before planning can move
  forward.
- `NEEDS_REVIEW`: More human review is required.
- `UNKNOWN`: The proposal or review could not be read safely.

The result status may also report:

- `PLAN_CREATED`: A plan was created.
- `NO_ACCEPTED_REVIEW`: The review was not accepted, so no plan was created.

## How Plans Protect Capital

Implementation plans protect capital by keeping proposal acceptance separate from
actual implementation. They force the work to list tests, risk checks, and
rollback steps before any human-controlled code or rule change is considered.

The default plan includes:

- unit tests
- regression tests
- backtest comparison
- safety gate tests
- drawdown check
- capital protection check
- session/news/spread filter check
- no live trading confirmation

## Future Plan

Future versions can add:

- implementation plan storage
- main.py implementation plan output
- backtest evidence links
- final approval records
- human-controlled implementation workflow
