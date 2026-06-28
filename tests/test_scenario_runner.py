from io import StringIO
from contextlib import redirect_stdout

import main


def run_main_with_args(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def test_bullish_scenario_runs_without_crashing() -> None:
    output = run_main_with_args("--scenario", "bullish")
    assert "Scenario: bullish" in output


def test_bearish_scenario_runs_without_crashing() -> None:
    output = run_main_with_args("--scenario", "bearish")
    assert "Scenario: bearish" in output


def test_weak_scenario_runs_without_crashing() -> None:
    output = run_main_with_args("--scenario", "weak")
    assert "Scenario: weak" in output


def test_all_scenario_runs_without_crashing() -> None:
    output = run_main_with_args("--scenario", "all")
    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output


def test_output_includes_scenario_name() -> None:
    output = run_main_with_args("--scenario", "bearish")
    assert "Scenario: bearish" in output


def test_invalid_scenario_is_rejected_safely() -> None:
    output = run_main_with_args("--scenario", "invalid")
    assert "Invalid scenario" in output
