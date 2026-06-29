# Real Sierra Market CSV Validation Result

This document records the real Sierra Chart market CSV validation result for `ai_trader_project`.

It is documentation only. It does not add features, change strategy logic, change risk logic, connect Sierra Chart live, connect CME live data, connect MT5, connect a broker, call external APIs, create real trade execution, or implement live trading.

## 1. Purpose

This document records the first validation result using a private Sierra Chart `BAR_SUMMARY` CSV as both:

- market candles for rolling backtest mode through `--backtest-market-csv`,
- Order Flow context through `--orderflow-csv`.

The goal was to confirm that real Sierra OHLC data can be used safely for research-only backtest validation.

## 2. Private Local Test File

The private local test file was:

```text
private_data/sierra_chart/gc_weekday_test.csv
```

This file was created locally from a Sierra Chart export.

This file is private data and must not be committed to GitHub.

## 3. Commands Tested

The validation used the real Sierra CSV as historical market candles and also as Order Flow context.

Example command shape:

```powershell
.\venv\Scripts\python.exe main.py --mode backtest --scenario bullish --profile apex --backtest-market-csv private_data/sierra_chart/gc_weekday_test.csv --orderflow-csv private_data/sierra_chart/gc_weekday_test.csv --backtest-max-iterations 10 --show-trace
```

This command reads local CSV files only. It does not connect to live Sierra Chart, CME, MT5, a broker, or any external API.

## 4. Market CSV Result

Observed market CSV result:

- Backtest market candles: `gc_weekday_test.csv (BAR_SUMMARY positional OHLC)`
- Market candles used real Sierra OHLC data.
- Total iterations: `10`
- Backtest stopped at `max_iterations`.

The market CSV loader uses positional OHLC for Sierra `BAR_SUMMARY` files:

- `Date`: column index `0`
- `Time`: column index `1`
- `Open`: column index `2`
- `High`: column index `3`
- `Low`: column index `4`
- `Last` / `Close`: column index `5`
- `Volume`: column index `6`, when available

This positional mapping is important because Sierra `BAR_SUMMARY` exports can contain duplicate `Open`, `High`, `Low`, `Last`, or `Close` study columns later in the file.

The positional OHLC fix corrected a false `VOLATILITY_TOO_HIGH` issue caused by reading the wrong duplicate study columns as market prices.

## 5. Order Flow Result

Observed Order Flow result:

- Import source: `BAR_SUMMARY`
- Order Flow CSV loaded successfully.
- Order Flow Data Quality: `PASSED`
- Candle count: `864`
- Total levels: `864`
- Order Flow bias: `NEUTRAL`

`BAR_SUMMARY` Order Flow uses one synthetic close-price level per candle. It is useful for early validation, but it is not full price-level footprint data.

## 6. Safety Gate Result

Observed safety results:

- Session filter: `SESSION_ALLOWED`
- Volatility filter: `VOLATILITY_ALLOWED`
- Safety gate: `SAFETY_PASSED`

The earlier false volatility block was resolved by using the first positional price OHLC group for market candles.

## 7. Decision Result

Observed decision result:

- Final result: `NO_TRADE`
- Blocking reason: `Strong SMC conflict with final direction`

Context alignment:

- Market Analyzer was bullish.
- Multi-Timeframe was bullish.
- CRT was bullish.
- SMC context was bearish.
- Order Flow was neutral.

Because the context was conflicting, the Decision Engine chose `NO_TRADE`.

## 8. Why NO_TRADE Is Correct

`NO_TRADE` is safe and expected in this validation.

This is not a bug.

The system correctly refused to trade because the bullish market/CRT context conflicted with bearish SMC context, while Order Flow did not provide strong confirmation.

Do not weaken strategy filters just to force trades. A safe blocked trade is a useful validation result.

## 9. What This Proves

This validation proves:

- Real Sierra `BAR_SUMMARY` market candles can be used in rolling backtest mode.
- `--backtest-market-csv` can use real Sierra OHLC data.
- `--orderflow-csv` can still load the same file separately for Order Flow context.
- Duplicate Sierra OHLC headers can be handled safely for market candles.
- The first price OHLC group is used instead of later study columns.
- Order Flow data quality can pass on a real weekday Sierra export.
- The safety gate can pass while the Decision Engine still blocks due to context conflict.
- `NO_TRADE` can be the correct safe result.

## 10. What This Does Not Prove

This validation does not prove:

- The strategy is profitable.
- The strategy is ready for paper trading.
- The strategy is ready for live trading.
- `BAR_SUMMARY` data is as strong as full price-level footprint data.
- Strategy filters should be weakened.
- Broker integration should begin.

This is still early real-data backtest validation.

## 11. Safety Confirmation

- No Sierra Chart live connection.
- No CME live data connection.
- No MT5 login.
- No broker connection.
- No real order execution.
- No live trading.
- No external API connection.
- No `private_data` files committed.

The validation stayed local, offline, and research-only.

## 12. Next Validation Steps

1. Test more weekday sessions.
2. Test larger `--backtest-max-iterations` values.
3. Export a cleaner one-session Sierra CSV.
4. Later test full price-level footprint data.
5. Do not weaken strategy filters just to force trades.
6. Continue documenting blocked trades and conflict reasons.
7. Consider paper trading only after enough backtest evidence exists.

## 13. Beginner Summary

The project successfully used a real Sierra Chart weekday CSV as backtest market data.

The system loaded the market candles correctly, passed Order Flow data quality, passed the session and volatility filters, and then chose `NO_TRADE` because the trading context was conflicting.

That is safe behavior. The goal is not to force trades. The goal is to prove that the system reads real data correctly and protects the account when the setup is not clean.
