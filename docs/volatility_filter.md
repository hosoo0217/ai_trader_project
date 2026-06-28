# Volatility Filter

## Why Volatility Filter Exists
The volatility filter is a safety layer for paper trading and backtesting.

It helps block entries when market conditions are abnormal and likely to reduce decision quality.

This module is research-only:
- no live trading
- no broker connection
- no external API

## Why High Volatility Can Be Dangerous
Very high volatility can cause sudden and erratic movement.

That can lead to:
- unstable entries
- wider slippage assumptions in simulation
- higher probability of stop-outs from noise spikes

The filter blocks when ATR is above the configured maximum or when the last candle is abnormally large versus ATR.

## Why Low Volatility Can Reduce Trade Quality
Very low volatility can mean weak participation and limited price expansion.

That can reduce trade quality by:
- lowering follow-through after entry
- increasing the chance of chop and fake movement

The filter blocks when ATR is below the configured minimum.

## Apex Futures Scalping Use Case
Apex-style futures scalping needs controlled and readable volatility.

If volatility is too high, execution quality can degrade quickly.
If volatility is too low, setups may not move enough to justify risk.

The volatility filter helps avoid both extremes.

## Spot Gold Use Case
Spot Gold can shift between calm ranges and sharp expansions.

A volatility filter helps keep research behavior consistent by allowing only candles within a defined ATR regime and blocking abnormal spikes.

## v1 Behavior Summary
- Missing or invalid candle data blocks trading.
- Not enough candles for ATR blocks trading.
- Disabled filter allows trading with reason: Volatility filter disabled.
- ATR below minimum blocks trading.
- ATR above maximum blocks trading.
- Last candle range above ATR multiplier threshold blocks trading.
- Otherwise trading is allowed.

## Future Plan
Future versions can support profile-specific volatility presets.

Example direction:
- Apex profile: tighter ATR and spike thresholds
- Spot profile: wider ATR range for swing conditions
- Safe profile: very conservative thresholds
