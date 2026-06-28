"""Unit tests for footprint order flow data models."""

from orderflow.footprint import FootprintAnalyzer, FootprintCandle, FootprintLevel


def make_candle() -> FootprintCandle:
    """Create a small footprint candle for tests."""
    return FootprintCandle(
        time="2024-01-01 09:30",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        levels=[
            FootprintLevel(price=99.0, bid_volume=20.0, ask_volume=10.0),
            FootprintLevel(price=100.0, bid_volume=30.0, ask_volume=40.0),
            FootprintLevel(price=101.0, bid_volume=5.0, ask_volume=70.0),
        ],
    )


def test_footprint_level_delta() -> None:
    level = FootprintLevel(price=100.0, bid_volume=25.0, ask_volume=40.0)

    assert level.delta() == 15.0


def test_footprint_level_total_volume() -> None:
    level = FootprintLevel(price=100.0, bid_volume=25.0, ask_volume=40.0)

    assert level.total_volume() == 65.0


def test_footprint_level_imbalance_ratio() -> None:
    level = FootprintLevel(price=100.0, bid_volume=20.0, ask_volume=50.0)

    assert level.imbalance_ratio() == 2.5


def test_footprint_candle_total_bid_volume() -> None:
    candle = make_candle()

    assert candle.total_bid_volume() == 55.0


def test_footprint_candle_total_ask_volume() -> None:
    candle = make_candle()

    assert candle.total_ask_volume() == 120.0


def test_footprint_candle_delta() -> None:
    candle = make_candle()

    assert candle.delta() == 65.0


def test_buy_delta_detection() -> None:
    candle = make_candle()

    assert candle.is_buy_delta() is True
    assert candle.is_sell_delta() is False


def test_sell_delta_detection() -> None:
    candle = FootprintCandle(
        time=None,
        open=100.0,
        high=101.0,
        low=99.0,
        close=99.5,
        levels=[
            FootprintLevel(price=100.0, bid_volume=80.0, ask_volume=20.0),
            FootprintLevel(price=99.5, bid_volume=50.0, ask_volume=10.0),
        ],
    )

    assert candle.is_sell_delta() is True
    assert candle.is_buy_delta() is False


def test_point_of_control_calculation() -> None:
    summary = FootprintAnalyzer().summarize(make_candle())

    assert summary.point_of_control == 101.0
    assert summary.max_bid_level == 100.0
    assert summary.max_ask_level == 101.0
    assert summary.total_volume == 175.0
    assert summary.delta == 65.0


def test_empty_levels_do_not_crash() -> None:
    candle = FootprintCandle(
        time=None,
        open=100.0,
        high=100.0,
        low=100.0,
        close=100.0,
        levels=[],
    )

    summary = FootprintAnalyzer().summarize(candle)

    assert summary.total_volume == 0.0
    assert summary.point_of_control is None
    assert "No footprint levels available" in summary.reasons


def test_negative_volume_is_handled_safely() -> None:
    candle = FootprintCandle(
        time=None,
        open=100.0,
        high=100.0,
        low=100.0,
        close=100.0,
        levels=[FootprintLevel(price=100.0, bid_volume=-10.0, ask_volume=20.0)],
    )

    summary = FootprintAnalyzer().summarize(candle)

    assert summary.total_bid_volume == 0.0
    assert summary.total_ask_volume == 20.0
    assert summary.delta == 20.0
    assert "Negative volume was treated as zero" in summary.reasons


def test_explain_returns_readable_text() -> None:
    summary = FootprintAnalyzer().summarize(make_candle())

    text = FootprintAnalyzer().explain(summary)

    assert "Footprint summary" in text
    assert "POC=101.00" in text
    assert "delta=65.00" in text
