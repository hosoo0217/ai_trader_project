# Safety Gate

## Purpose
The Pre-Trade Safety Gate is a unified safety checkpoint used before a trade can continue.

It combines all major protection and filter outcomes into one final decision:
- allow trade flow to continue
- or block trade flow safely

## Why a Safety Gate Exists
As the platform grows, many safety checks exist at the same time:
- capital protection
- session filter
- news filter
- volatility filter
- spread filter

Without one central gate, it is easy to miss a condition and accidentally continue to risk sizing or execution.

The Safety Gate prevents this by producing one clear decision from all provided checks.

## Why Filters Should Be Centralized
Centralization gives several benefits:
- one place for safety decision logic
- consistent blocked or passed status reporting
- easier testing of safety behavior
- easier audit of why a trade was blocked

This is especially important for research and backtesting workflows where repeatable behavior matters.

## Safety-First Philosophy
The platform follows conservative rules:
- if no checks are provided, block by default
- if any provided check fails, block
- if all provided checks pass, allow continuation

Capital protection has highest authority.
If capital protection blocks, the final gate must block regardless of other checks.

## How This Prevents Accidental Trades
The Safety Gate prevents accidental trades by:
- requiring explicit safety evidence before continuation
- aggregating all blocking reasons in one result
- exposing passed and failed checks clearly
- returning a readable explanation for logs and console output

This reduces the chance that a trade reaches risk or order stages under unsafe conditions.

## Decision Output
The Safety Gate returns:
- allowed: True or False
- status: SAFETY_PASSED, SAFETY_BLOCKED, or NO_CHECKS_PROVIDED
- reasons from all checks
- blocking reasons from failed checks
- passed check names
- failed check names

## Scope
This module is research-only and simulation-only.

It does not:
- place live orders
- connect to a broker
- call external APIs
- use MT5 or Sierra live connections

## Future Plan for Live Trading Protection
If live trading is ever considered in the future, the same safety gate concept can be extended with:
- broker-side account state validation
- exchange session calendar validation
- connectivity and latency safety checks
- hard kill-switch and emergency state propagation
- stricter pre-order compliance validation

Even then, the same principle should remain:
no trade proceeds unless the unified safety gate allows it.
