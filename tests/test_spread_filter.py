from analysis.spread_filter import SpreadFilter, SpreadFilterConfig


def test_normal_spread_allows_trading() -> None:
    result = SpreadFilter().evaluate(1.2, SpreadFilterConfig(max_spread=3.0))

    assert result.allowed is True
    assert result.status == "SPREAD_ALLOWED"


def test_high_spread_blocks_trading() -> None:
    result = SpreadFilter().evaluate(4.5, SpreadFilterConfig(max_spread=3.0))

    assert result.allowed is False
    assert result.status == "SPREAD_TOO_HIGH"


def test_unknown_spread_blocks_by_default() -> None:
    result = SpreadFilter().evaluate(None, SpreadFilterConfig())

    assert result.allowed is False
    assert result.status == "SPREAD_UNKNOWN"


def test_unknown_spread_can_be_allowed_if_configured() -> None:
    result = SpreadFilter().evaluate(
        None,
        SpreadFilterConfig(block_if_spread_unknown=False),
    )

    assert result.allowed is True
    assert result.status == "SPREAD_UNKNOWN"
    assert "allowed by configuration" in "; ".join(result.reasons)


def test_negative_spread_blocks_trading() -> None:
    result = SpreadFilter().evaluate(-0.1, SpreadFilterConfig())

    assert result.allowed is False
    assert result.status == "INVALID_SPREAD"


def test_disabled_filter_allows_trading() -> None:
    result = SpreadFilter().evaluate(99.0, SpreadFilterConfig(enabled=False))

    assert result.allowed is True
    assert result.status == "FILTER_DISABLED"
    assert "Spread filter disabled" in result.reasons


def test_explain_returns_readable_text() -> None:
    result = SpreadFilter().evaluate(1.0, SpreadFilterConfig(max_spread=3.0))
    text = SpreadFilter().explain(result)

    assert "Spread filter status" in text
    assert "allowed" in text
    assert "spread" in text
