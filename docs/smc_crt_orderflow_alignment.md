# SMC + CRT + Order Flow Alignment Gate v1

This document explains the first alignment gate that can compare SMC, CRT, and Order Flow context.

This module is research-only.
It does not connect to a broker, live trading system, Sierra Chart live feed, CME live feed, or external API.
It does not create trade entries or orders.

## Why The Alignment Gate Exists

SMC, CRT, and Order Flow describe different views of the same market.

- SMC describes structure, liquidity, and directional intent.
- CRT describes candle range behavior and confirmation quality.
- Order Flow describes buying and selling pressure behind price movement.

The alignment gate gives the system one simple answer:

- do these contexts agree enough to continue research evaluation?

It is a quality gate, not a trading strategy.

## Why SMC And CRT Need Order Flow Confirmation

SMC and CRT can describe where price might want to go, but they do not fully describe participation inside the move.

Order Flow can help answer:

- are buyers actually active?
- are sellers actually active?
- is pressure confirming the structure?
- is pressure conflicting with the setup?

When all three contexts agree, the alignment quality is stronger.

## When Order Flow Can Block A Setup

In v1, Order Flow can block alignment when it directly conflicts with SMC and CRT.

Examples:

- SMC is `BULLISH`
- CRT is `BULLISH`
- Order Flow is `BEARISH`

That conflict returns a neutral final bias and a blocking reason.

If `require_orderflow_alignment` is enabled, Order Flow must match the SMC/CRT direction. Missing, neutral, unknown, or conflicting Order Flow will block alignment.

If `require_orderflow_alignment` is disabled, SMC and CRT can still pass when Order Flow is neutral or unknown.

## Why This Is Not A Trade Signal Yet

Alignment only says that contexts agree or conflict.

It does not check:

- capital protection
- risk sizing
- stop loss validity
- take profit validity
- spread filters
- volatility filters
- session filters
- journal state
- paper broker state

Because of that, this gate must not be treated as a standalone entry signal.

## Future PaperTradingFlow Integration

A future version can feed `OrderFlowContextResult` into the existing `ContextAlignmentGate` inside `PaperTradingFlow`.

The planned flow is:

1. Build SMC context.
2. Build CRT context.
3. Build Order Flow context from exported footprint data.
4. Run the alignment gate.
5. Continue only if the broader paper-trading safety checks also pass.

That future integration should remain paper-trading and backtesting only until a separate live-trading design is explicitly approved.
