from contextlib import redirect_stdout
from io import StringIO

import main


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_main_runs_without_crashing() -> None:
    output = _run_main()
    assert "AI Trader Paper Trading Demo" in output


def test_output_contains_performance_report() -> None:
    output = _run_main("--scenario", "bullish")
    assert "Performance Report" in output
    assert "Total trades" in output


def test_weak_scenario_still_prints_performance_report() -> None:
    output = _run_main("--scenario", "weak")
    assert "Scenario: weak" in output
    assert "Performance Report" in output


def test_all_scenario_runs_without_crashing() -> None:
    output = _run_main("--scenario", "all")
    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output
    assert "Performance Report" in output
