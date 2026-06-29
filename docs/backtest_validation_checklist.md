# Backtest Validation Checklist

This document is a safety checklist for future backtest validation in `ai_trader_project`.

It is documentation only. It does not add strategy logic, change risk logic, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

Backtest validation protects capital by checking whether a strategy worked across enough historical data before moving into serious paper trading or any future live consideration.

A backtest should answer basic safety questions:

- Did the strategy work across more than one market condition?
- Did the risk rules protect the account during bad periods?
- Did the safety filters block trades when they should?
- Were the results stable enough to justify paper validation?

A good backtest does not prove a strategy is ready for real money. It only shows whether the strategy deserves more testing.

## 2. Required Baseline

Before trusting any backtest result:

- [ ] Full pytest must pass.
- [ ] End-to-end demo validation should pass.
- [ ] No live trading code should be used.
- [ ] Backtest must use historical data only.
- [ ] No broker connection should be used.
- [ ] No external API should be required.
- [ ] No real order execution should occur.

Recommended test command:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

For deeper research-only backtest validation, the CLI can limit or expand rolling backtest iterations with:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --backtest-max-iterations 25
```

More iterations can help reduce `INSUFFICIENT_DATA` when enough historical candles exist. This is still historical backtesting only, not paper trading or live trading.

## 3. Data Quality Checklist

Historical data must be clean enough to trust the result.

- [ ] Enough historical candles/sessions are included.
- [ ] Timestamps are correct.
- [ ] Price columns are correct.
- [ ] Open, high, low, and close values are valid.
- [ ] No missing data.
- [ ] No duplicated candles.
- [ ] No obvious price spikes caused by bad data.
- [ ] Spread assumptions are reviewed.
- [ ] Session times are reviewed.
- [ ] News events are considered if possible.
- [ ] Sierra Chart / Order Flow CSV quality is checked separately.

If data quality is weak, the backtest result should not be trusted.

## 4. Performance Metrics Checklist

Record the main performance metrics before making any decision.

- [ ] Total trades.
- [ ] Win rate.
- [ ] Profit factor.
- [ ] Average win.
- [ ] Average loss.
- [ ] Average R.
- [ ] Max drawdown.
- [ ] Consecutive losses.
- [ ] Daily loss behavior.
- [ ] Daily profit target behavior.
- [ ] Expectancy.

Do not focus only on profit. Drawdown, losing streaks, and risk behavior matter more than a good-looking return.

## 5. Risk Checklist

Risk rules must work during the backtest.

- [ ] Daily loss limit is respected.
- [ ] Daily profit target is respected.
- [ ] Loss streak protection is tested.
- [ ] Max open trades is respected.
- [ ] Position sizing is reviewed.
- [ ] Safety gate blocks unsafe trades.
- [ ] No trade is taken if filters block.
- [ ] Risk behavior is reviewed during winning periods.
- [ ] Risk behavior is reviewed during losing periods.

If risk rules fail, the strategy should not move forward.

## 6. Market Condition Checklist

The strategy should be tested across different market conditions.

- [ ] Trending days.
- [ ] Range days.
- [ ] High volatility days.
- [ ] Low volatility days.
- [ ] News days.
- [ ] London session behavior.
- [ ] New York session behavior.
- [ ] Bad spread conditions.
- [ ] Weekend blocked behavior.

A strategy that only works in one condition may fail when the market changes.

## 7. Overfitting / Curve Fitting Warning

A good backtest result alone is not enough.

Avoid these mistakes:

- Do not tune rules only to fit one sample of data.
- Do not keep changing settings until the old data looks perfect.
- Do not ignore losing periods because the final result is positive.
- Do not assume a strong historical result will repeat in the future.

Safer validation requires:

- [ ] Out-of-sample testing.
- [ ] Different market periods.
- [ ] Different session conditions.
- [ ] Forward paper trading after backtest.
- [ ] Human review before moving forward.

## 8. Pass / Fail Guideline

A strategy should not move forward unless:

- [ ] Backtest data quality is acceptable.
- [ ] Drawdown is controlled.
- [ ] Risk rules are respected.
- [ ] Results are stable across different sessions.
- [ ] Safety filters work correctly.
- [ ] Losing streak behavior is acceptable.
- [ ] Daily loss behavior is acceptable.
- [ ] Human review approves moving to paper validation.

If any major safety item fails, the strategy should stay in research mode.

## 9. Not Allowed Yet

The following are not allowed during backtest validation:

- No live trading.
- No broker execution.
- No real-money trading.
- No automatic strategy changes.
- No bypassing safety gates.
- No broker credentials.
- No external live market-data connections.
- No real order placement.

Backtest validation is a research step only.

## 10. Beginner Summary

Backtesting is like testing the strategy on old market data before risking anything real.

The goal is not to prove the strategy is perfect. The goal is to find problems early, check whether risk rules work, and decide whether the strategy deserves paper trading validation.

If the backtest is weak, unsafe, or based on bad data, stop there. Protecting capital matters more than moving fast.
