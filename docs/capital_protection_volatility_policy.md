# Capital Protection Volatility Policy

## Scope

Documentation-only policy for how volatility protection should behave before any future production enforcement, broker integration, live data integration, or simulation expansion.

## Purpose

Define the official volatility measurement basis, ATR timeframe and threshold guardrails, abnormal last-candle behavior, invalid-data handling, and profile-specific restrictions for capital protection decisions.

## Current implementation checkpoint

Current volatility filtering is research-only. It uses ATR over a configurable period, blocks missing or invalid candle data, blocks insufficient candle history, blocks ATR below the configured minimum, blocks ATR above the configured maximum, and blocks an abnormally large last candle relative to ATR.

## Profile behavior

FUTURES_PROP profiles currently use ATR period 14, minimum ATR 0.5, maximum ATR 80.0, and last-candle range multiplier 3.0. SPOT_GOLD profiles currently use ATR period 14, minimum ATR 0.3, maximum ATR 120.0, and last-candle range multiplier 3.5. Fallback profiles use an intentionally impossible ATR range to block new entries conservatively.

## Resolved policy

ATR should remain the primary volatility measurement for the evaluated candle timeframe, with the abnormal last-candle range check retained as an additional spike safeguard.

The authoritative timeframe should be the timeframe of the candle dataset explicitly passed to the filter. The filter must not infer, substitute, or combine other timeframes implicitly.

Instrument-specific and timeframe-specific ATR thresholds are not approved implicitly. Each threshold set must be explicitly configured, documented, and covered by tests before use.

Missing, malformed, non-numeric, or insufficient candle data must block new entries conservatively. Volatility protection must not fail open when required data is unavailable.

A volatility block applies to new entry decisions only. It must not automatically close, reduce, reverse, or otherwise modify an already-open position.

A new entry may proceed only when ATR is within the configured minimum and maximum bounds and the last candle range does not exceed ATR multiplied by the configured spike multiplier.

The filter may allow entries while disabled only when disabled status is explicitly configured and recorded in the decision reason.

Standard deviation, realized volatility, volume-based volatility, machine-learned thresholds, or other alternative measures must not be added implicitly. Any additional measure requires separate documentation, configuration, and tests.

## Not approved

This policy does not approve live trading, broker connectivity, MT5 integration, Sierra live integration, CME live data, external APIs, real orders, automatic threshold calibration, implicit timeframe inference, or automatic modification of existing positions.

## Test implications

Tests must verify normal-volatility allowance, low-ATR blocking, high-ATR blocking, abnormal last-candle blocking, invalid-data blocking, insufficient-data blocking, explicit disabled-filter allowance, profile-specific configuration behavior, and the absence of broker or external API dependencies.

## Recommended next step

Validate this policy through offline simulation and backtest evidence before considering any broader enforcement or integration change.
