# ACSIL Matching Day2 Multi-Timeframe Validation Result

This document records the day2 Sierra ACSIL full footprint validation result across matching 1-minute, 5-minute, and 10-minute market OHLC datasets.

It is documentation only. It does not change strategy rules, implement Order Flow confirmation, change risk rules, connect live systems, create real orders, or approve paper/live trading.

## 1. Purpose

The purpose of this document is to record the day2 multi-timeframe validation checkpoint using matching Sierra Chart market OHLC exports and matching ACSIL full price-level footprint exports.

This validation extends the earlier matching validation phase by checking the same data path across another day/session set:

- matching market OHLC candles,
- matching ACSIL full footprint Order Flow data,
- 1m, 5m, and 10m timeframes,
- bullish and bearish 50-iteration diagnostics.

## 2. Private Local Files

Private day2 files used for validation:

```text
private_data/sierra_chart/day2/day2_session1_1m_market.csv
private_data/sierra_chart/day2/day2_session1_1m_footprint.csv
private_data/sierra_chart/day2/day2_session2_5m_market.csv
private_data/sierra_chart/day2/day2_session2_5m_footprint.csv
private_data/sierra_chart/day2/day2_session3_10m_market.csv
private_data/sierra_chart/day2/day2_session3_10m_footprint.csv
private_data/sierra_chart/day2/orderflow_ab_day2_session2_5m_bullish.txt
private_data/sierra_chart/day2/orderflow_ab_day2_session2_5m_bearish.txt
private_data/sierra_chart/day2/orderflow_ab_day2_session3_10m_bullish.txt
private_data/sierra_chart/day2/orderflow_ab_day2_session3_10m_bearish.txt
```

These files are private local data and generated diagnostics. They must not be committed.

## 3. Day2 1m Result

Observed 1-minute ACSIL full footprint import result:

- Source: `ACSIL_FULL_FOOTPRINT`
- Time range: `2026-06-28 18:00:00 -> 2026-07-01 06:19:00`
- Candles: `3078`
- Levels: `56753`
- Invalid levels: `0`
- Data quality: `PASSED`
- Order Flow: `NEUTRAL`
- Confidence: `0.0`
- Active: `False`
- Final CVD: `-2566.00`

Observed 1-minute bullish result:

- Total iterations: `50`
- Executed trades: `0`
- Blocked trades: `50`
- Total PnL: `0.00`
- Backtest quality: `INSUFFICIENT_DATA`

Observed 1-minute bearish result:

- Total iterations: `50`
- Executed trades: `0`
- Blocked trades: `50`
- Total PnL: `0.00`
- Backtest quality: `INSUFFICIENT_DATA`

The 1m day2 validation remained safe with zero executions while Order Flow was neutral and inactive.

## 4. Day2 5m Result

Observed 5-minute ACSIL full footprint import result:

- Source: `ACSIL_FULL_FOOTPRINT`
- Time range: `2026-06-28 18:00:00 -> 2026-07-01 06:25:00`
- Candles: `618`
- Levels: `30784`
- Invalid levels: `0`
- Data quality: `PASSED`
- Order Flow: `NEUTRAL`
- Confidence: `0.0`
- Active: `False`
- Final CVD: `-2554.00`

Observed 5-minute bullish result:

- Total iterations: `50`
- Executed trades: `4`
- Blocked trades: `46`
- Losses: `4`
- Total PnL: `-40.00`

Observed 5-minute bearish result:

- Total iterations: `50`
- Executed trades: `4`
- Blocked trades: `46`
- Losses: `4`
- Total PnL: `-40.00`

Observed 5-minute A/B diagnostic for both bullish and bearish:

- Current A executed trades: `4`
- Current A PnL: `-40.00`
- Simulated B executed trades: `0`
- Simulated B blocked trades: `50`
- B would block `4` trades by Order Flow confirmation.
- B would block all `4` because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

The 5m day2 validation allowed losing trades while Order Flow was neutral. The simulated Order Flow confirmation diagnostic would have blocked all observed losing 5m trades.

## 5. Day2 10m Result

Observed 10-minute ACSIL full footprint import result:

- Source: `ACSIL_FULL_FOOTPRINT`
- Time range: `2026-06-28 18:00:00 -> 2026-07-01 06:30:00`
- Candles: `310`
- Levels: `22897`
- Invalid levels: `0`
- Data quality: `PASSED`
- Order Flow: `NEUTRAL`
- Confidence: `30.0`
- Minimum required confidence: `50.0`
- Active: `True`
- Imbalance bias: `BULLISH`
- Final CVD: `-2444.00`

Observed 10-minute bullish result:

- Total iterations: `50`
- Executed trades: `15`
- Blocked trades: `35`
- Losses: `15`
- Total PnL: `-150.00`

Observed 10-minute bearish result:

- Total iterations: `50`
- Executed trades: `15`
- Blocked trades: `35`
- Losses: `15`
- Total PnL: `-150.00`

Observed 10-minute A/B diagnostic for both bullish and bearish:

- Current A executed trades: `15`
- Current A PnL: `-150.00`
- Simulated B executed trades: `0`
- Simulated B blocked trades: `50`
- B would block `15` trades by Order Flow confirmation.
- B would block all `15` because Order Flow was `NEUTRAL`.
- Simulated B PnL: `0.00`
- Warning: `B simulated behavior blocks every A executed trade`

The 10m day2 validation allowed more losing trades while Order Flow was neutral and confidence remained below the minimum required threshold. The simulated Order Flow confirmation diagnostic would have blocked all observed losing 10m trades.

## 6. Cross-Timeframe Pattern

Day2 confirms the same pattern seen in the earlier matching validation phase:

- ACSIL full footprint plus matching OHLC pipeline works across 1m, 5m, and 10m.
- Data quality passed across all day2 timeframes.
- 1m remained safe with zero executions.
- 5m and 10m allowed losing trades while Order Flow was `NEUTRAL`.
- Simulated Order Flow confirmation would have blocked all observed losing trades in 5m and 10m.
- This strengthens the safety evidence for the Order Flow confirmation proposal.

This is meaningful safety evidence, but it remains research-only.

## 7. What This Supports

This validation supports these conclusions:

- Matching ACSIL full footprint imports are working across multiple day2 timeframes.
- The importer handled tens of thousands of price levels per timeframe with zero invalid levels.
- The data quality gate passed on all tested day2 timeframes.
- The same neutral-Order-Flow losing-trade pattern repeated in day2 5m and 10m diagnostics.
- The simulated Order Flow confirmation diagnostic would have blocked every observed losing trade in those 5m and 10m runs.

This strengthens the safety case for continuing Order Flow confirmation research.

## 8. What This Does Not Prove

This validation does not prove:

- The strategy is profitable.
- The Order Flow confirmation rule is profitable.
- The Order Flow confirmation rule should be implemented.
- Simulated B can find winning trades.
- Simulated B will preserve enough valid trade opportunities.
- Day2 plus earlier matching validation is enough evidence for implementation approval.
- The system is ready for paper trading.
- The system is ready for live trading.

More independent days and sessions are still needed before implementation approval.

## 9. Current Implementation Status

Current status:

- Strategy rule changed: `false`
- Order Flow confirmation implemented: `false`
- Implementation approved: `false`
- Paper trading ready: `false`
- Live trading ready: `false`

No strategy rule should be changed yet.

## 10. Safety Confirmation

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

All validation stayed local, offline, and research-only.

## 11. Next Validation Steps

1. Test more independent Sierra days and sessions.
2. Continue validating matching OHLC plus ACSIL full footprint exports across 1m, 5m, and 10m.
3. Track whether Order Flow becomes directional instead of neutral.
4. Track whether confidence can exceed the minimum threshold on valid setups.
5. Confirm simulated B does not block every trade across broader data.
6. Compare executed trades, blocked trades, PnL, drawdown, and quality grade across independent sessions.
7. Only after enough evidence, create an implementation plan.
8. Do not implement Order Flow confirmation yet.
9. Do not start paper trading from this result.
10. Do not start live trading from this result.

The next phase should expand the independent dataset before any strategy rule change is considered.

## 12. Beginner Summary

Day2 used matching Sierra market candles and matching ACSIL full footprint data across 1m, 5m, and 10m.

The data path worked, and data quality passed on every timeframe. The 1m test stayed safe with zero trades. The 5m and 10m tests still allowed trades while Order Flow was neutral, and every observed executed trade lost.

The simulated Order Flow confirmation rule would have blocked those losing 5m and 10m trades. That strengthens the safety evidence for the proposal, but it still does not prove profitability and does not approve implementation.

More independent days and sessions are required before changing strategy logic.
