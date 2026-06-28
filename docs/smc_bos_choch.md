# SMC BOS / CHOCH v1

This document explains the first Break of Structure (BOS) and Change of Character (CHOCH) analyzer in this project.

## Scope

This is research logic for analysis and backtesting.

It does not:
- execute live trades
- connect to live brokers
- use MT5 or Sierra Chart live connections
- act as final trade execution logic

## What BOS Means

BOS (Break of Structure) means price breaks a key swing level in the same direction as the current structure bias.

- If structure is bullish and price breaks above swing high, it is bullish BOS.
- If structure is bearish and price breaks below swing low, it is bearish BOS.

## What CHOCH Means

CHOCH (Change of Character) means price breaks a key swing level against the prior structure direction (or from neutral/unclear structure).

- If structure was bearish or neutral and price breaks above swing high, it is bullish CHOCH.
- If structure was bullish or neutral and price breaks below swing low, it is bearish CHOCH.

## Bullish BOS Example

- Previous structure bias: BULLISH
- Last swing high: 2000.0
- Candle close: 2001.5
- Result: BOS, direction BULLISH

## Bearish BOS Example

- Previous structure bias: BEARISH
- Last swing low: 1980.0
- Candle close: 1978.5
- Result: BOS, direction BEARISH

## Bullish CHOCH Example

- Previous structure bias: BEARISH
- Last swing high: 2000.0
- Candle close: 2002.0
- Result: CHOCH, direction BULLISH

## Bearish CHOCH Example

- Previous structure bias: BULLISH
- Last swing low: 1980.0
- Candle close: 1979.0
- Result: CHOCH, direction BEARISH

## Detection Controls

- require_close_break=True:
  - bullish uses close > swing_high + buffer
  - bearish uses close < swing_low - buffer
- require_close_break=False:
  - bullish uses high > swing_high + buffer
  - bearish uses low < swing_low - buffer
- buffer adds a minimum break distance to avoid weak breaks.

## Why This Is Still Research Logic

BOS/CHOCH alone is not enough for robust trade decisions.

This module only reports structure breaks. It does not handle complete confirmation, risk gating, execution, or portfolio constraints.

## Future Plan

Planned v2 improvements include:
- liquidity sweep confirmation before counting a break
- stronger multi-timeframe confirmation
- better filtering for noisy intrabar breaks
- richer integration into SMC context scoring
