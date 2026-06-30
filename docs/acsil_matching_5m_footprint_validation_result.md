# ACSIL Matching 5m Footprint Validation Result

This document records the Sierra ACSIL full footprint matching 5-minute validation result.

It is documentation only. It does not change strategy rules, implement Order Flow confirmation, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record validation using matching 5-minute market OHLC data and matching ACSIL full price-level footprint data.

This validation checks whether the project can safely use aligned 5-minute market candles and full footprint Order Flow data for research-only backtests.

## 2. Private Local Files

Private market OHLC CSV:

```text
private_data/sierra_chart/gc_market_ohlc_session2_5m.csv
```

Private Order Flow CSV:

```text
private_data/sierra_chart/gc_full_footprint_acsil_session2_5m.csv
```

Both files are private local data and must not be committed.

## 3. ACSIL Footprint Import Result

Observed ACSIL full footprint import result:

- Source: `ACSIL_FULL_FOOTPRINT`
- Time range: `2026-06-28 18:00:00 -> 2026-06-30 11:20:00`
- Candles: `443`
- Levels: `23751`
- Invalid levels: `0`
- Data quality: `PASSED`
- Order Flow bias: `NEUTRAL`
- Confidence: `30.0`
- Minimum required confidence: `50.0`
- Blocking reason: `Confidence 30.0 is below minimum 50.0`

This confirms that matching 5-minute ACSIL full footprint data imports successfully and passes data quality checks.

## 4. Bullish 50-Iteration Result

Observed bullish result:

- Executed trades: `4`
- Blocked trades: `46`
- Final balance: `49960.00`
- Total PnL: `-40.00`
- Wins: `0`
- Losses: `4`
- Win rate: `0.00%`
- Max drawdown: `40.00`
- Backtest quality: `INSUFFICIENT_DATA`

The bullish run still allowed some trades while Order Flow was `NEUTRAL` and confidence was below the minimum threshold.

All executed trades were losses in this validation.

## 5. Bullish A/B Diagnostic

Observed bullish A/B diagnostic:

- Current A executed trades: `4`
- Current A PnL: `-40.00`
- Simulated B executed trades: `0`
- Simulated B blocked trades: `50`
- B would block `4` trades by Order Flow confirmation.
- B would block all `4` because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

The simulated Order Flow confirmation rule would have blocked the 4 losing bullish A trades.

## 6. Bearish 50-Iteration Result

Observed bearish result:

- Executed trades: `4`
- Blocked trades: `46`
- Final balance: `49960.00`
- Total PnL: `-40.00`
- Wins: `0`
- Losses: `4`
- Win rate: `0.00%`
- Max drawdown: `40.00`
- Backtest quality: `INSUFFICIENT_DATA`

The bearish run also allowed some trades while Order Flow was `NEUTRAL` and confidence was below the minimum threshold.

All executed trades were losses in this validation.

## 7. Bearish A/B Diagnostic

Observed bearish A/B diagnostic:

- Current A executed trades: `4`
- Current A PnL: `-40.00`
- Simulated B executed trades: `0`
- Simulated B blocked trades: `50`
- B would block `4` trades by Order Flow confirmation.
- B would block all `4` because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

The simulated Order Flow confirmation rule would also have blocked the 4 losing bearish A trades.

## 8. What This Supports

This validation supports these conclusions:

- Matching 5-minute market OHLC plus ACSIL full footprint validation works.
- Data quality passes with real ACSIL price-level footprint data.
- Current behavior can still allow trades when Order Flow is `NEUTRAL` and confidence is below the minimum.
- Those trades were all losing trades in both bullish and bearish scenarios.
- The simulated Order Flow confirmation rule would have blocked those losing trades.
- This adds evidence that Order Flow confirmation may improve safety.

This is useful validation evidence.

It is not implementation approval.

## 9. What Remains Unproven

This validation does not prove:

- The strategy is profitable.
- The Order Flow confirmation rule is profitable.
- The Order Flow confirmation rule should be implemented.
- B can find winning trades.
- B will preserve enough valid trade opportunities.
- One matching 5-minute Sierra session is enough evidence.
- The system is ready for paper trading.
- The system is ready for live trading.

More matching sessions and timeframes are required before implementation approval.

## 10. Main Warning

Main warning:

```text
B simulated behavior blocks every A executed trade
```

This warning remains important.

B avoided the losing trades in this validation, but it also left zero simulated executed trades. The project still needs evidence that B can preserve valid trades when Order Flow becomes directional and confidence is strong enough.

## 11. Safety Confirmation

- No live trading.
- No broker connection.
- No MT5 login.
- No Sierra live order connection.
- No CME live execution.
- No real orders.
- No external APIs.
- No `private_data` committed.
- No generated report files committed.
- No strategy rule implemented.

The validation stayed local, offline, and research-only.

## 12. Next Validation Steps

1. Test more matching Sierra weekday sessions.
2. Test additional matching timeframes.
3. Run bullish and bearish A/B diagnostics on more matching OHLC plus footprint exports.
4. Track whether Order Flow remains neutral or becomes directional on richer sessions.
5. Track whether confidence can exceed the minimum threshold on valid setups.
6. Confirm B does not block every trade across broader data.
7. Only after enough evidence, create an implementation plan.
8. Do not implement Order Flow confirmation yet.
9. Do not start paper trading from this result.
10. Do not start live trading from this result.

The next phase should collect broader matching full footprint evidence before any strategy rule change.

## 13. Beginner Summary

This test used matching 5-minute market candles and matching full footprint Order Flow data from Sierra Chart.

The data import worked and quality passed. That is good.

The current strategy still took 4 trades in both bullish and bearish runs while Order Flow was neutral and confidence was below the minimum. All of those trades lost.

The simulated Order Flow confirmation rule would have blocked those losing trades, which supports more research. But the simulated rule also blocked every executed trade, so it still has not proven it can find good trades.

This is a positive safety and validation result, not permission to implement the rule or start paper/live trading.
