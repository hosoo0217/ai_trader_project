# AI Order Flow Replay Coach

The Order Flow Replay Coach reviews `OrderFlowReplayReport` objects in plain,
beginner-friendly language.

It is local and rule-based. It does not call OpenAI, use external APIs, connect
to Sierra Chart live data, connect to CME, connect to brokers, or place orders.

## Why It Exists

Replay reports contain useful context, but raw counts and confidence numbers can
be hard to learn from. The coach explains what the replay suggests and what the
user should review next.

## Dominant Bias

Dominant bias is the bias with the highest replay step count.

- `BULLISH`: more steps supported bullish Order Flow context.
- `BEARISH`: more steps supported bearish Order Flow context.
- `NEUTRAL` or `UNKNOWN`: Order Flow was unclear, balanced, or not usable.

Dominant bias is not a trade entry.

## Confidence

Average confidence shows how strong the replay context was across all steps.

- High confidence means the replay context was more consistent.
- Low confidence means the replay should be treated cautiously.
- Mixed steps can reduce the coach grade even when the final bias looks clear.

## CVD

CVD means cumulative volume delta. It tracks whether ask volume or bid volume
was stronger through the replay.

Positive CVD can support bullish context. Negative CVD can support bearish
context. CVD still needs confirmation from the rest of the trading framework.

## No Trade Signals

The coach does not say to take a trade. It may say Order Flow supports bullish
context or bearish context, but SMC, CRT, risk, session, spread, and news filters
still matter.

## Future Plan

Later, this coach can help review replay/backtesting sessions by explaining:

- when Order Flow agreed with SMC and CRT
- when Order Flow was mixed
- when confidence was too low
- what the user should study before the next replay
