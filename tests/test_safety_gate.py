from analysis.news_filter import NewsFilterResult
from analysis.session_filter import SessionFilterResult
from analysis.spread_filter import SpreadFilterResult
from analysis.volatility_filter import VolatilityFilterResult
from core.capital_protection import CapitalProtectionDecision
from core.safety_gate import SafetyGate


def _allowed_session() -> SessionFilterResult:
    return SessionFilterResult(
        allowed=True,
        active_session="London",
        status="SESSION_ALLOWED",
        reasons=["Inside enabled session"],
        blocking_reasons=[],
    )


def _blocked_session() -> SessionFilterResult:
    return SessionFilterResult(
        allowed=False,
        active_session=None,
        status="SESSION_BLOCKED",
        reasons=[],
        blocking_reasons=["Outside allowed sessions"],
    )


def _allowed_news() -> NewsFilterResult:
    return NewsFilterResult(
        allowed=True,
        status="NEWS_ALLOWED",
        active_event=None,
        reasons=["No blocking event"],
        blocking_reasons=[],
    )


def _blocked_news() -> NewsFilterResult:
    return NewsFilterResult(
        allowed=False,
        status="NEWS_BLOCKED",
        active_event="NFP",
        reasons=[],
        blocking_reasons=["High impact event active"],
    )


def _allowed_volatility() -> VolatilityFilterResult:
    return VolatilityFilterResult(
        allowed=True,
        status="VOLATILITY_ALLOWED",
        atr=2.0,
        last_candle_range=1.0,
        reasons=["Volatility in range"],
        blocking_reasons=[],
    )


def _blocked_volatility() -> VolatilityFilterResult:
    return VolatilityFilterResult(
        allowed=False,
        status="VOLATILITY_TOO_HIGH",
        atr=20.0,
        last_candle_range=5.0,
        reasons=[],
        blocking_reasons=["ATR too high"],
    )


def _allowed_spread() -> SpreadFilterResult:
    return SpreadFilterResult(
        allowed=True,
        status="SPREAD_ALLOWED",
        spread=1.2,
        reasons=["Spread within range"],
        blocking_reasons=[],
    )


def _blocked_spread() -> SpreadFilterResult:
    return SpreadFilterResult(
        allowed=False,
        status="SPREAD_TOO_HIGH",
        spread=9.0,
        reasons=[],
        blocking_reasons=["Spread above threshold"],
    )


def _allowed_capital() -> CapitalProtectionDecision:
    return CapitalProtectionDecision(allowed=True, status="allowed", reasons=[])


def _blocked_capital() -> CapitalProtectionDecision:
    return CapitalProtectionDecision(
        allowed=False,
        status="blocked",
        reasons=["Daily loss limit reached"],
    )


def test_no_checks_blocks_trading() -> None:
    decision = SafetyGate().evaluate()

    assert decision.allowed is False
    assert decision.status == "NO_CHECKS_PROVIDED"


def test_all_checks_allowed_passes() -> None:
    decision = SafetyGate().evaluate(
        session_result=_allowed_session(),
        news_result=_allowed_news(),
        volatility_result=_allowed_volatility(),
        spread_result=_allowed_spread(),
        capital_decision=_allowed_capital(),
    )

    assert decision.allowed is True
    assert decision.status == "SAFETY_PASSED"
    assert set(decision.passed_checks) == {"SESSION", "NEWS", "VOLATILITY", "SPREAD", "CAPITAL_PROTECTION"}


def test_session_blocked_blocks_safety_gate() -> None:
    decision = SafetyGate().evaluate(session_result=_blocked_session())

    assert decision.allowed is False
    assert decision.status == "SAFETY_BLOCKED"
    assert "SESSION" in decision.failed_checks


def test_news_blocked_blocks_safety_gate() -> None:
    decision = SafetyGate().evaluate(news_result=_blocked_news())

    assert decision.allowed is False
    assert "NEWS" in decision.failed_checks


def test_volatility_blocked_blocks_safety_gate() -> None:
    decision = SafetyGate().evaluate(volatility_result=_blocked_volatility())

    assert decision.allowed is False
    assert "VOLATILITY" in decision.failed_checks


def test_spread_blocked_blocks_safety_gate() -> None:
    decision = SafetyGate().evaluate(spread_result=_blocked_spread())

    assert decision.allowed is False
    assert "SPREAD" in decision.failed_checks


def test_capital_protection_blocked_overrides_everything() -> None:
    decision = SafetyGate().evaluate(
        session_result=_allowed_session(),
        news_result=_allowed_news(),
        volatility_result=_allowed_volatility(),
        spread_result=_allowed_spread(),
        capital_decision=_blocked_capital(),
    )

    assert decision.allowed is False
    assert decision.status == "SAFETY_BLOCKED"
    assert "CAPITAL_PROTECTION" in decision.failed_checks


def test_reasons_are_collected() -> None:
    decision = SafetyGate().evaluate(
        session_result=_allowed_session(),
        news_result=_allowed_news(),
    )

    combined = "; ".join(decision.reasons)
    assert "SESSION" in combined
    assert "NEWS" in combined


def test_blocking_reasons_are_collected() -> None:
    decision = SafetyGate().evaluate(
        session_result=_blocked_session(),
        spread_result=_blocked_spread(),
    )

    combined = "; ".join(decision.blocking_reasons)
    assert "SESSION" in combined
    assert "SPREAD" in combined


def test_explain_returns_readable_text() -> None:
    decision = SafetyGate().evaluate(
        session_result=_blocked_session(),
        capital_decision=_blocked_capital(),
    )
    text = SafetyGate().explain(decision)

    assert "Safety status" in text
    assert "allowed" in text
    assert "passed checks" in text
    assert "failed checks" in text
    assert "blocking reasons" in text
    assert "Safety blocked. Do not trade." in text
