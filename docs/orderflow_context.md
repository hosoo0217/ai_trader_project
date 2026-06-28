# Order Flow Context Combiner v1

This document explains the first unified order flow context combiner.

This module is research-only.
It does not connect to live trading systems, brokers, Sierra Chart live feeds, CME live feeds, or external APIs.
It does not create entries or trades.

## Why OrderFlowContext Exists

Delta/CVD, imbalance, and absorption each describe one part of order flow.

The decision framework expects each analysis domain to eventually contribute one structured context. `OrderFlowContext` is the future bridge between raw order flow tools and the broader `DecisionContext`.

The combiner answers a simple research question:

- Does current order flow evidence lean bullish, bearish, neutral, or unknown?

It does not decide whether to trade.

## Combined Inputs

### Delta / CVD

Delta/CVD describes aggressive buying or selling pressure.

In v1:

- `BUYING_PRESSURE` adds bullish evidence
- `SELLING_PRESSURE` adds bearish evidence
- `NEUTRAL` adds no directional evidence

The combiner also carries forward `final_cvd` for later research.

### Imbalance

Imbalance describes one-sided bid or ask volume at footprint price levels.

In v1:

- `BULLISH` imbalance adds bullish evidence
- `BEARISH` imbalance adds bearish evidence
- `NEUTRAL` or `UNKNOWN` adds no directional evidence

### Absorption

Absorption describes possible passive liquidity absorbing aggressive buyers or sellers.

In v1:

- `BULLISH` absorption adds bullish evidence
- `BEARISH` absorption adds bearish evidence
- `NEUTRAL` or `UNKNOWN` adds no directional evidence

## Bias and Confidence

The combiner counts bullish and bearish evidence.

Bias rules:

- more bullish evidence than bearish evidence -> `BULLISH`
- more bearish evidence than bullish evidence -> `BEARISH`
- equal directional evidence -> `NEUTRAL`
- no inputs at all -> `UNKNOWN`

Confidence is intentionally simple in v1:

- aligned evidence increases confidence
- conflicting evidence reduces confidence
- confidence is always clamped between 0 and 100

This keeps the context explainable while the project is still building the order flow foundation.

## Optional Alignment Requirements

The config can require specific confirmation before allowing a directional context to remain directional:

- require delta alignment
- require imbalance alignment
- require absorption confirmation

When a requirement fails, the combiner returns `NEUTRAL` and records a blocking reason.

This is still not a trade block. It is only an order flow context rule.

## Why This Is Not an Entry Signal

Order flow context does not include full trade validation.

It does not check:

- market structure
- SMC liquidity context
- CRT range context
- risk limits
- stop loss quality
- take profit quality
- session rules
- spread rules

Because of that, this context should never be treated as a standalone entry signal.

## Later Connection to SMC and CRT

Future versions can place this order flow context into the broader `DecisionContext`.

The decision engine can then compare:

- order flow pressure
- SMC structure and liquidity
- CRT candle/range behavior
- market context
- risk context

That keeps each module independent while allowing the final decision layer to reconcile the evidence.

## Future Plan: Sierra Chart Exported Footprint Data

The future data workflow remains offline and file-based:

1. Export historical footprint data from Sierra Chart.
2. Import the exported CSV into footprint candle models.
3. Run Delta/CVD, imbalance, and absorption analyzers.
4. Combine those outputs into `OrderFlowContext`.
5. Use the context in research and backtesting.

Live Sierra Chart, CME, broker, or external API integrations are not part of this v1 module.
