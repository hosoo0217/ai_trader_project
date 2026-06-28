from datetime import datetime, timedelta

import pandas as pd

from analysis.volatility_filter import VolatilityFilter, VolatilityFilterConfig


def _make_candles(rows: int = 40, base_range: float = 2.0) -> pd.DataFrame:
    start = datetime(2026, 1, 1, 0, 0, 0)
    data: list[dict[str, float | datetime]] = []

    price = 100.0
    for index in range(rows):
        open_price = price
        high = open_price + (base_range / 2.0)
        low = open_price - (base_range / 2.0)
        close = open_price + 0.1

        data.append(
            {
                "time": start + timedelta(minutes=index),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
            }
        )
        price = close

    return pd.DataFrame(data)


def test_normal_volatility_allows_trading() -> None:
    candles = _make_candles(base_range=2.0)
    config = VolatilityFilterConfig(atr_period=14, min_atr=0.5, max_atr=5.0)

    result = VolatilityFilter().evaluate(candles, config)

    assert result.allowed is True
    assert result.status == "VOLATILITY_ALLOWED"


def test_too_low_volatility_blocks_trading() -> None:
    candles = _make_candles(base_range=0.02)
    config = VolatilityFilterConfig(atr_period=14, min_atr=0.1, max_atr=5.0)

    result = VolatilityFilter().evaluate(candles, config)

    assert result.allowed is False
    assert result.status == "VOLATILITY_TOO_LOW"


def test_too_high_volatility_blocks_trading() -> None:
    candles = _make_candles(base_range=12.0)
    config = VolatilityFilterConfig(atr_period=14, min_atr=0.1, max_atr=5.0)

    result = VolatilityFilter().evaluate(candles, config)

    assert result.allowed is False
    assert result.status == "VOLATILITY_TOO_HIGH"


def test_abnormal_last_candle_blocks_trading() -> None:
    candles = _make_candles(base_range=2.0)
    candles.loc[candles.index[-1], "high"] = candles.loc[candles.index[-1], "close"] + 20.0
    candles.loc[candles.index[-1], "low"] = candles.loc[candles.index[-1], "close"] - 20.0

    config = VolatilityFilterConfig(
        atr_period=14,
        min_atr=0.1,
        max_atr=100.0,
        max_last_candle_range_multiplier=3.0,
    )
    result = VolatilityFilter().evaluate(candles, config)

    assert result.allowed is False
    assert result.status == "ABNORMAL_LAST_CANDLE"


def test_missing_columns_returns_invalid_data() -> None:
    candles = _make_candles().drop(columns=["close"])

    result = VolatilityFilter().evaluate(candles, VolatilityFilterConfig())

    assert result.allowed is False
    assert result.status == "INVALID_DATA"


def test_not_enough_candles_returns_not_enough_data() -> None:
    candles = _make_candles(rows=10)

    result = VolatilityFilter().evaluate(candles, VolatilityFilterConfig(atr_period=14))

    assert result.allowed is False
    assert result.status == "NOT_ENOUGH_DATA"


def test_disabled_filter_allows_trading() -> None:
    candles = _make_candles()

    result = VolatilityFilter().evaluate(candles, VolatilityFilterConfig(enabled=False))

    assert result.allowed is True
    assert result.status == "FILTER_DISABLED"
    assert "Volatility filter disabled" in result.reasons


def test_explain_returns_readable_text() -> None:
    candles = _make_candles(base_range=2.0)
    result = VolatilityFilter().evaluate(candles, VolatilityFilterConfig())
    text = VolatilityFilter().explain(result)

    assert "Volatility filter status" in text
    assert "allowed" in text
    assert "atr" in text
