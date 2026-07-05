# Backtest Quality Loss Cluster Diagnostic Plan

## Safety scope

This is a research-only diagnostic plan.

No strategy rule is changed.
No risk rule is changed.
No broker code is changed.
No live trading code is changed.
No paper trading, live trading, broker connection, MT5 login, Sierra live connection, CME live data connection, external API, or real order is approved.

Generated reports must remain under ignored `private_data`.

## Decision

The next research direction should be backtest-quality and losing-trade cluster diagnosis before any strategy code change.

Do not enforce Order Flow confirmation.

Keep Order Flow as diagnostic-only context.

## Why this is the next step

The incremental Order Flow replay optimization is complete and the larger/full 5m diagnostic export finished successfully.

The full 5m bullish run produced:
- Backtest iterations: 1,014.
- A executed trades: 188.
- A PnL: +95.00.
- Win rate: 42.02%.
- Profit factor: 1.09.
- Max drawdown: 335.00.
- Backtest quality: `FAILED`.

The per-entry Order Flow replay diagnostic did not support enforcement:
- Non-neutral replay snapshot behavior: 28 kept trades, -5.00 PnL.
- Direction-aligned replay snapshot behavior: 17 kept trades, -20.00 PnL.
- Missing replay snapshots: 0.

This means the highest-value question is no longer whether Order Flow confirmation should be enforced. The better question is why the current backtest quality fails even though full-run PnL is positive.

## Initial loss-cluster observations

Source report:

`private_data/sierra_chart/bulk_30d_sc_delayed/per_entry_orderflow_5m_bullish_full_incremental/per_entry_orderflow_replay_diagnostic.json`

Initial observations from the full 5m bullish diagnostic:
- Executed trades: 188.
- Wins: 79.
- Losses: 109.
- BUY losses: 48.
- SELL losses: 61.
- Losses with `NEUTRAL` replay Order Flow: 92.
- Losses with `BEARISH` replay Order Flow: 11.
- Losses with `BULLISH` replay Order Flow: 6.
- Non-neutral losses: 17.
- Direction-aligned losses: 11.

Largest nearby-loss clusters using a five-iteration gap:

| Iteration range | Losses | PnL | Actions | Replay Order Flow | Aligned losses |
|---|---:|---:|---|---|---:|
| 917-931 | 13 | -130.00 | BUY:7, SELL:6 | NEUTRAL:12, BEARISH:1 | 0 |
| 726-736 | 7 | -70.00 | BUY:7 | NEUTRAL:6, BULLISH:1 | 1 |
| 364-371 | 7 | -70.00 | SELL:7 | NEUTRAL:7 | 0 |
| 450-459 | 6 | -60.00 | BUY:4, SELL:2 | NEUTRAL:5, BULLISH:1 | 1 |
| 489-494 | 6 | -60.00 | SELL:6 | NEUTRAL:6 | 0 |
| 272-279 | 6 | -60.00 | BUY:6 | NEUTRAL:6 | 0 |

These clusters suggest that quality failure is probably driven by repeated entries during unfavorable local regimes, not by one isolated bad trade and not by an Order Flow enforcement gap alone.

## Diagnostic questions

Answer these before changing strategy code:

1. Are losing clusters concentrated in specific session times or day boundaries?
2. Are losses repeated after recent losses, suggesting a cooldown or re-entry problem?
3. Do clusters happen when SMC, CRT, market context, and replay Order Flow disagree?
4. Are BUY and SELL losses symmetric, or does one side fail in specific regimes?
5. Are stop losses clustered after volatility expansion, narrow ranges, or poor reward-to-risk conditions?
6. Do winners and losses differ by pre-entry volatility, candle range, trend state, or recent PnL streak?
7. Would any proposed filter preserve enough winners to improve drawdown and profit factor, rather than merely blocking activity?

## Proposed diagnostic workflow

Stage 1: Export or reuse full-run trade traces.
- Prefer existing diagnostic JSON where it already contains executed trade snapshots.
- If needed, run a research-only full 5m export with trade traces enabled.
- Keep all generated files under `private_data`.

Stage 2: Build a loss-cluster table.
- Group executed losses by nearby iteration index.
- Record cluster start, end, size, PnL, action mix, Order Flow replay state, and whether losses were aligned or non-neutral.
- Identify the largest drawdown contributors.

Stage 3: Add context columns.
- Add session timestamp if available.
- Add recent trade streak and recent PnL before entry.
- Add market/SMC/CRT trace reasons if available.
- Add volatility/range information if available.

Stage 4: Compare winners against losses.
- Compare action side.
- Compare replay Order Flow state.
- Compare recent PnL streak.
- Compare volatility/range and session timing.
- Compare cluster membership.

Stage 5: Produce a no-code recommendation.
- Summarize which failure mode is most likely.
- List candidate filters as research proposals only.
- Require an A/B diagnostic before any implementation.

## Candidate research proposals

These are not approved changes:
- Post-loss cooldown diagnostic.
- Maximum consecutive same-direction entries diagnostic.
- Volatility/range quality diagnostic.
- Session-time quality diagnostic.
- Context disagreement diagnostic.
- Drawdown-aware pause diagnostic.

Each candidate must be evaluated as a diagnostic first and rejected if it only improves metrics by deleting too much sample size or blocking winners.

## Acceptance criteria before code changes

Before implementation, the project should have:
- A documented loss-cluster report for the full 5m run.
- Evidence that the proposed diagnostic explains drawdown better than Order Flow alignment alone.
- A candidate rule with clear non-goals and safety limits.
- A research-only A/B plan.
- Explicit confirmation that no live, paper, broker, or external API path is touched.

## Current recommendation

Do not change strategy code yet.

Next concrete task: create a loss-cluster diagnostic report for the full 5m run and identify the largest drawdown contributors.
