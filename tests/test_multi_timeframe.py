"""Unit tests for the multi-timeframe bias combiner."""

from core.market_analyzer import MarketAnalysisResult
from core.multi_timeframe import MultiTimeframeBiasCombiner, MultiTimeframeConfig, MultiTimeframeDecision


def make_result(timeframe: str, bias: str, confidence: float) -> MarketAnalysisResult:
    """Create a simple analysis result for testing."""
    return MarketAnalysisResult(timeframe=timeframe, bias=bias, confidence=confidence)


def test_buy_bias_when_higher_timeframes_are_bullish():
    """Bullish higher timeframes should produce a BUY_BIAS decision."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "W1": make_result("W1", "BULLISH", 90.0),
        "D1": make_result("D1", "BULLISH", 90.0),
        "H4": make_result("H4", "BULLISH", 88.0),
        "H1": make_result("H1", "BULLISH", 82.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig())

    assert decision.bias == "BUY_BIAS"
    assert decision.allowed
    assert decision.confidence >= 70.0


def test_sell_bias_when_higher_timeframes_are_bearish():
    """Bearish higher timeframes should produce a SELL_BIAS decision."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "W1": make_result("W1", "BEARISH", 90.0),
        "D1": make_result("D1", "BEARISH", 90.0),
        "H4": make_result("H4", "BEARISH", 88.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig())

    assert decision.bias == "SELL_BIAS"
    assert decision.allowed


def test_wait_when_higher_timeframes_conflict():
    """Conflicting higher timeframes should return WAIT."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "W1": make_result("W1", "BULLISH", 90.0),
        "D1": make_result("D1", "BEARISH", 90.0),
        "H4": make_result("H4", "BULLISH", 88.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig())

    assert decision.bias == "WAIT"
    assert not decision.allowed


def test_no_trade_when_required_timeframe_is_missing():
    """Missing required higher timeframe should block the decision."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "D1": make_result("D1", "BULLISH", 90.0),
        "H4": make_result("H4", "BULLISH", 88.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig())

    assert decision.bias == "NO_TRADE"
    assert not decision.allowed


def test_no_trade_when_required_timeframe_is_unknown():
    """A required timeframe marked UNKNOWN should block the decision."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "W1": make_result("W1", "UNKNOWN", 0.0),
        "D1": make_result("D1", "BULLISH", 90.0),
        "H4": make_result("H4", "BULLISH", 88.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig())

    assert decision.bias == "NO_TRADE"
    assert not decision.allowed


def test_wait_when_confidence_is_below_threshold():
    """Low average confidence should produce WAIT rather than a trade decision."""
    combiner = MultiTimeframeBiasCombiner()
    results = {
        "W1": make_result("W1", "BULLISH", 60.0),
        "D1": make_result("D1", "BULLISH", 65.0),
        "H4": make_result("H4", "BULLISH", 70.0),
    }

    decision = combiner.combine(results, MultiTimeframeConfig(minimum_confidence=70.0))

    assert decision.bias == "WAIT"
    assert not decision.allowed


def test_explain_returns_readable_text():
    """Explanation text should summarize the combined bias and reasons."""
    combiner = MultiTimeframeBiasCombiner()
    decision = MultiTimeframeDecision(
        bias="BUY_BIAS",
        allowed=True,
        confidence=80.0,
        reasons=["Higher timeframes are aligned"],
        blocking_reasons=[],
        timeframe_summary={"W1": "BULLISH"},
    )

    explanation = combiner.explain(decision)

    assert "BUY_BIAS" in explanation
    assert "Higher timeframes are aligned" in explanation
