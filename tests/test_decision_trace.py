from storage.decision_trace import DecisionTracer


def test_create_trace() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD")

    assert trace.trace_id
    assert trace.symbol == "XAUUSD"
    assert trace.final_action == "NO_TRADE"
    assert trace.final_allowed is False
    assert trace.steps == []


def test_add_allowed_step() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD")

    tracer.add_step(
        trace,
        step_name="SESSION_FILTER",
        status="SESSION_ALLOWED",
        allowed=True,
        reasons=["Inside enabled session"],
    )

    assert len(trace.steps) == 1
    assert trace.steps[0].step_name == "SESSION_FILTER"
    assert trace.steps[0].allowed is True


def test_add_blocked_step() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD")

    tracer.add_step(
        trace,
        step_name="SPREAD_FILTER",
        status="SPREAD_TOO_HIGH",
        allowed=False,
        blocking_reasons=["Spread is above maximum threshold"],
    )

    assert len(trace.steps) == 1
    assert trace.steps[0].allowed is False
    assert trace.steps[0].blocking_reasons == ["Spread is above maximum threshold"]


def test_get_blocking_steps() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD")

    tracer.add_step(trace, "SESSION_FILTER", "SESSION_ALLOWED", True)
    tracer.add_step(trace, "SPREAD_FILTER", "SPREAD_TOO_HIGH", False, blocking_reasons=["Spread too high"])

    blocking_steps = tracer.get_blocking_steps(trace)

    assert len(blocking_steps) == 1
    assert blocking_steps[0].step_name == "SPREAD_FILTER"


def test_explain_trace_returns_readable_text() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD", final_action="NO_TRADE", final_allowed=False)
    tracer.add_step(trace, "MARKET_ANALYZER", "BULLISH", True, reasons=["Bias detected"])
    tracer.add_step(trace, "SPREAD_FILTER", "SPREAD_TOO_HIGH", False, blocking_reasons=["Spread too high"])

    text = tracer.explain_trace(trace)

    assert "Symbol: XAUUSD" in text
    assert "Final action: NO_TRADE" in text
    assert "Final allowed: False" in text
    assert "MARKET_ANALYZER" in text
    assert "SPREAD_FILTER" in text
    assert "Blocking reasons" in text


def test_empty_trace_does_not_crash() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="GC")

    text = tracer.explain_trace(trace)

    assert "Symbol: GC" in text
    assert "Steps: None" in text


def test_multiple_steps_are_preserved_in_order() -> None:
    tracer = DecisionTracer()
    trace = tracer.create_trace(symbol="XAUUSD")

    tracer.add_step(trace, "MARKET_ANALYZER", "BULLISH", True)
    tracer.add_step(trace, "MULTI_TIMEFRAME", "BUY_BIAS", True)
    tracer.add_step(trace, "RISK_ENGINE", "RISK_ALLOWED", True)

    names = [step.step_name for step in trace.steps]
    assert names == ["MARKET_ANALYZER", "MULTI_TIMEFRAME", "RISK_ENGINE"]
