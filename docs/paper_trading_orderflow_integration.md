# PaperTradingFlow Order Flow Integration v1

This document explains the optional Order Flow Context integration in `PaperTradingFlow`.

This is paper-trading and backtesting logic only.
It does not connect to a broker, Sierra Chart live feed, CME live feed, or any external API.
It does not create real orders.

## Why Order Flow Is Optional In v1

Order Flow Context depends on footprint-style bid/ask volume data.

Most current demo and backtest flows only have normal OHLC candles, so requiring Order Flow would break existing research workflows.

For v1:

- missing Order Flow does not crash the flow
- SMC + CRT alignment still works as before
- the trace records that Order Flow was not provided
- `require_orderflow_alignment` remains `False` by default

This keeps the system backward-compatible while making room for richer data later.

## How It Connects With SMC And CRT

`PaperTradingFlow` can now accept an optional `OrderFlowContextResult`.

When provided, the flow passes it into the existing context alignment gate along with:

- SMC context
- CRT context
- Order Flow context

The alignment gate compares the three bias values:

- `BULLISH`
- `BEARISH`
- `NEUTRAL`
- `UNKNOWN`

If SMC and CRT agree and Order Flow confirms them, alignment confidence improves.

## Why Missing Order Flow Should Not Break The System

Order Flow is not available unless footprint data has been imported or built.

If no Order Flow context is provided, `PaperTradingFlow` records:

- `orderflow_bias = UNKNOWN`
- `orderflow_confidence = 0.0`
- reason: `Order Flow context not provided`

With default config, SMC + CRT alignment can still pass when Order Flow is missing, neutral, or unknown.

## Why Conflict Can Block Bad Trades

Even though Order Flow is optional, a strong conflict is useful information.

Example:

- SMC is `BULLISH`
- CRT is `BULLISH`
- Order Flow is `BEARISH`

In that case, the alignment gate blocks the setup and returns a neutral final bias. This helps prevent the paper flow from continuing when structure and participation disagree.

## Decision Trace

When tracing is enabled, the flow adds an `ORDER_FLOW_CONTEXT` step.

The trace includes:

- orderflow bias
- orderflow confidence
- orderflow reasons
- blocking reasons, if any

This keeps the decision path readable for beginners and for later debugging.

## Future Plan

The planned offline workflow is:

1. Export historical footprint data from Sierra Chart as CSV.
2. Import CSV rows into `FootprintCandle` objects.
3. Run Delta/CVD, Imbalance, and Absorption analyzers.
4. Combine those outputs into `OrderFlowContextResult`.
5. Pass that result into `PaperTradingFlow`.
6. Use the result only for research, paper trading, and backtesting.

Live trading integration is not part of this v1 feature.
