# Order Flow Data Quality

Order Flow analysis depends on clean footprint data. If a CSV has missing price
levels, bad prices, negative volume, or too few candles, the analyzers can
produce misleading context.

This v1 data-quality gate checks imported footprint candles before they are used
for research or backtesting decisions. It does not connect to Sierra Chart live
data, CME, brokers, or any external API.

## Why Quality Matters

Bad CSV data can create bad AI decisions. For example:

- Missing levels can hide real bid or ask pressure.
- Negative volume can distort delta.
- Empty candles can make Order Flow look neutral when there is no usable data.
- Too many invalid levels can make imbalance and absorption readings unreliable.

The quality gate gives a clear status before Order Flow Context is trusted.

## What Is Checked

The checker validates:

- Minimum candle count.
- Minimum levels per candle.
- Negative bid or ask volume.
- Missing, NaN, or infinite prices.
- Optional zero-volume level handling.
- Ratio of invalid levels to total levels.

## Status Values

- `PASSED`: Data is clean enough to use.
- `WARNING`: Data passed, but minor invalid levels were found below the configured threshold.
- `FAILED`: Data exists, but quality rules were violated.
- `EMPTY`: No footprint candles were provided.
- `INVALID`: The input itself was not usable.

## Future Plan

The next step is to run this gate before Order Flow Context enters
`PaperTradingFlow`. If data quality fails, Order Flow can stay inactive or
UNKNOWN instead of influencing the SMC + CRT alignment gate.
