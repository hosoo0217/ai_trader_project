from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path

import pytest

import main
from core.backtest_runner import BacktestIterationTrace, BacktestResult


def _run_main(*args: str) -> str:
    buffer = StringIO()
    with redirect_stdout(buffer):
        main.main(list(args))
    return buffer.getvalue()


def _write_sierra_bar_summary_csv(path: Path, rows: int = 75) -> None:
    lines = [
        "Date, Time, Open, High, Low, Last, Volume, # of Trades, OHLC Avg, HLC Avg, HL Avg, Bid Volume, Ask Volume, Open, High, Low, Last, Finish, CPL, Open, High, Low, Close, Delta, Volume, Volume / Sec"
    ]
    for index in range(rows):
        open_price = 4160.0 + index
        high_price = open_price + 4.0
        low_price = open_price - 3.0
        close_price = open_price + 1.5
        bid_volume = 100 + index
        ask_volume = 120 + index
        delta = ask_volume - bid_volume
        lines.append(
            "2026-6-21, "
            f"18:{index % 60:02d}:00.000000, "
            f"{open_price:.1f}, {high_price:.1f}, {low_price:.1f}, {close_price:.1f}, "
            f"{bid_volume + ask_volume}, 50, 0, 0, 0, {bid_volume}, {ask_volume}, "
            f"{open_price:.1f}, {high_price:.1f}, {low_price:.1f}, {close_price:.1f}, "
            f"0, 0, 9000.0, 99999.0, 1.0, 88888.0, {delta}, {bid_volume + ask_volume}, 1"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def test_demo_bullish_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish")
    assert "AI Trader Paper Trading Demo" in output
    assert "Scenario: bullish" in output


def test_demo_all_runs_without_crashing() -> None:
    output = _run_main("--mode", "demo", "--scenario", "all")
    assert "Scenario: bullish" in output
    assert "Scenario: bearish" in output
    assert "Scenario: weak" in output


def test_backtest_bullish_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "AI Trader Backtest" in output
    assert "Scenario: bullish" in output


def test_backtest_bearish_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bearish")
    assert "AI Trader Backtest" in output
    assert "Scenario: bearish" in output


def test_backtest_weak_runs_without_crashing() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "weak")
    assert "AI Trader Backtest" in output
    assert "Scenario: weak" in output


def test_backtest_mode_prints_backtest_title() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish")
    assert "AI Trader Backtest" in output


def test_demo_mode_prints_demo_title() -> None:
    output = _run_main("--mode", "demo", "--scenario", "bullish")
    assert "AI Trader Paper Trading Demo" in output


def test_invalid_mode_is_rejected_safely() -> None:
    output = _run_main("--mode", "invalid", "--scenario", "bullish")
    assert "Invalid mode" in output


def test_invalid_scenario_is_rejected_safely() -> None:
    output = _run_main("--mode", "demo", "--scenario", "invalid")
    assert "Invalid scenario" in output


def test_help_includes_backtest_max_iterations() -> None:
    help_text = main._build_parser().format_help()

    assert "--backtest-max-iterations" in help_text
    assert "rolling backtest iterations" in help_text


def test_help_includes_backtest_market_csv() -> None:
    help_text = main._build_parser().format_help()

    assert "--backtest-market-csv" in help_text
    assert "market candles" in help_text
    assert "research-only backtests" in help_text


def test_help_includes_export_backtest_trade_traces() -> None:
    help_text = main._build_parser().format_help()
    normalized_help = " ".join(help_text.split())

    assert "--export-backtest-trade-traces" in help_text
    assert "--backtest-trace-dir" in help_text
    assert "executed backtest trade trace reports" in normalized_help


def test_help_includes_simulate_orderflow_confirmation_ab() -> None:
    help_text = main._build_parser().format_help()

    assert "--simulate-orderflow-confirmation-ab" in help_text
    assert "Order Flow confirmation" in help_text


def test_help_includes_register_change_proposal_doc() -> None:
    help_text = main._build_parser().format_help()

    assert "--register-change-proposal-doc" in help_text
    assert "--proposal-category" in help_text
    assert "--proposal-priority" in help_text
    assert "--proposal-title" in help_text


def test_register_change_proposal_doc_creates_record(tmp_path: Path) -> None:
    proposal_doc = tmp_path / "orderflow_confirmation_change_proposal.md"
    proposal_doc.write_text(
        "# Order Flow Confirmation Change Proposal\n\n"
        "Require directional Order Flow confirmation before execution.\n",
        encoding="utf-8",
    )
    proposal_dir = tmp_path / "proposals"

    output = _run_main(
        "--register-change-proposal-doc",
        str(proposal_doc),
        "--proposal-category",
        "STRATEGY",
        "--proposal-priority",
        "HIGH",
        "--proposal-title",
        "Require Order Flow confirmation before Apex execution",
        "--proposal-dir",
        str(proposal_dir),
    )

    proposals = json.loads((proposal_dir / "change_proposals.json").read_text(encoding="utf-8"))
    record = proposals[0]

    assert "Documentation Change Proposal Registration" in output
    assert len(proposals) == 1
    assert record["title"] == "Require Order Flow confirmation before Apex execution"
    assert record["category"] == "STRATEGY"
    assert record["priority"] == "HIGH"
    assert record["status"] == "PROPOSED"
    assert record["human_review_required"] is True
    assert record["auto_implementation_allowed"] is False
    assert record["implementation_allowed"] is False
    assert record["doc_path"] == proposal_doc.as_posix()
    assert "Documentation-based proposal registration only" in record["reasons"]
    assert "Backtesting is required before implementation" in record["blocking_reasons"]


def test_register_change_proposal_doc_does_not_duplicate_same_doc_or_title(tmp_path: Path) -> None:
    proposal_doc = tmp_path / "orderflow_confirmation_change_proposal.md"
    proposal_doc.write_text(
        "# Order Flow Confirmation Change Proposal\n\n"
        "Require directional Order Flow confirmation before execution.\n",
        encoding="utf-8",
    )
    proposal_dir = tmp_path / "proposals"
    args = (
        "--register-change-proposal-doc",
        str(proposal_doc),
        "--proposal-title",
        "Require Order Flow confirmation before Apex execution",
        "--proposal-dir",
        str(proposal_dir),
    )

    first_output = _run_main(*args)
    second_output = _run_main(*args)

    proposals = json.loads((proposal_dir / "change_proposals.json").read_text(encoding="utf-8"))

    assert "- Registered: True" in first_output
    assert "- Status: DUPLICATE" in second_output
    assert len(proposals) == 1


def test_default_behavior_does_not_register_change_proposal_doc(tmp_path: Path) -> None:
    proposal_dir = tmp_path / "proposals"

    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--proposal-dir", str(proposal_dir))

    assert "AI Trader Backtest" in output
    assert not (proposal_dir / "change_proposals.json").exists()


def test_backtest_max_iterations_is_passed_to_config(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, int | None] = {}

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        seen["max_iterations"] = backtest_config.max_iterations
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=3,
            trades_executed=0,
            trades_blocked=3,
            final_balance=10000.0,
            total_pnl=0.0,
            reasons=["Backtest completed"],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--backtest-max-iterations", "3")

    assert "AI Trader Backtest" in output
    assert seen["max_iterations"] == 3


def test_export_backtest_trade_trace_files_are_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_dir = tmp_path / "trace_reports"

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=1,
            trades_executed=1,
            trades_blocked=0,
            final_balance=9990.0,
            total_pnl=-10.0,
            reasons=["Backtest completed"],
            iteration_traces=[
                BacktestIterationTrace(
                    iteration_index=1,
                    window_start=0,
                    window_end=59,
                    final_action="BUY",
                    final_allowed=True,
                    trade_executed=True,
                    status="CLOSED",
                    reasons=["BUY", "diagnostic test trade"],
                    trace_steps=[
                        {
                            "step_name": "TRADE_MANAGER",
                            "status": "EXECUTED",
                            "allowed": True,
                            "reasons": ["Paper order accepted"],
                            "blocking_reasons": [],
                        }
                    ],
                    trade_manager_status="EXECUTED",
                    trade_manager_reasons=["Paper order accepted"],
                    exit_simulator_status="EXITED",
                    exit_simulator_reasons=["Stop loss reached"],
                    simulated_pnl=-10.0,
                    outcome="LOSS",
                )
            ],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--export-backtest-trade-traces",
        "--backtest-trace-dir",
        str(trace_dir),
    )

    json_path = trace_dir / "backtest_trade_traces.json"
    txt_path = trace_dir / "backtest_trade_traces.txt"
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert "Backtest Trade Trace Export" in output
    assert json_path.exists()
    assert txt_path.exists()
    assert payload["summary"]["executed_trades"] == 1
    assert payload["executed_trade_iterations"][0]["iteration_index"] == 1
    assert payload["executed_trade_iterations"][0]["outcome"] == "LOSS"
    assert "decision_engine_status" in payload["executed_trade_iterations"][0]
    assert "Iteration 1" in txt_path.read_text(encoding="utf-8")


def test_backtest_trade_trace_export_works_with_no_executed_trades(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_dir = tmp_path / "empty_trace_reports"

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=1,
            trades_executed=0,
            trades_blocked=1,
            final_balance=10000.0,
            total_pnl=0.0,
            reasons=["Backtest completed"],
            iteration_traces=[
                BacktestIterationTrace(
                    iteration_index=1,
                    window_start=0,
                    window_end=59,
                    final_action="NO_TRADE",
                    final_allowed=False,
                    trade_executed=False,
                    status="NO_TRADE",
                    blocking_reasons=["Safety gate blocked trade"],
                )
            ],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--export-backtest-trade-traces",
        "--backtest-trace-dir",
        str(trace_dir),
    )

    payload = json.loads((trace_dir / "backtest_trade_traces.json").read_text(encoding="utf-8"))
    txt_report = (trace_dir / "backtest_trade_traces.txt").read_text(encoding="utf-8")

    assert payload["executed_trade_iterations"] == []
    assert payload["blocked_trade_summary"]["count"] == 1
    assert "Executed Trade Iterations\n- None" in txt_report


def test_orderflow_confirmation_ab_report_counts_neutral_executed_trade_as_b_blocked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_dir = tmp_path / "ab_reports"
    seen: dict[str, bool] = {}

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        seen["collect_iteration_traces"] = bool(kwargs.get("collect_iteration_traces", False))
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=2,
            trades_executed=2,
            trades_blocked=0,
            final_balance=9990.0,
            total_pnl=-10.0,
            reasons=["Backtest completed"],
            iteration_traces=[
                BacktestIterationTrace(
                    iteration_index=1,
                    window_start=0,
                    window_end=59,
                    final_action="SELL",
                    final_allowed=True,
                    trade_executed=True,
                    status="CLOSED",
                    orderflow_status="NEUTRAL",
                    simulated_pnl=-10.0,
                    outcome="LOSS",
                ),
                BacktestIterationTrace(
                    iteration_index=2,
                    window_start=5,
                    window_end=64,
                    final_action="SELL",
                    final_allowed=True,
                    trade_executed=True,
                    status="CLOSED",
                    orderflow_status="BEARISH",
                    simulated_pnl=10.0,
                    outcome="WIN",
                ),
            ],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--simulate-orderflow-confirmation-ab",
        "--backtest-trace-dir",
        str(trace_dir),
    )

    report_path = trace_dir / "orderflow_confirmation_ab_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert "Order Flow Confirmation A/B Diagnostic" in output
    assert seen["collect_iteration_traces"] is True
    assert payload["a_current_behavior"]["executed_trades"] == 2
    assert payload["b_simulated_behavior"]["executed_trades"] == 1
    assert payload["b_simulated_behavior"]["blocked_by_orderflow_confirmation"] == 1
    assert payload["b_simulated_behavior"]["blocked_because_orderflow_neutral"] == 1
    assert payload["b_simulated_blocked_trades"][0]["iteration_index"] == 1


def test_orderflow_confirmation_ab_report_warns_when_b_blocks_everything(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_dir = tmp_path / "ab_reports"

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=1,
            trades_executed=1,
            trades_blocked=0,
            final_balance=9990.0,
            total_pnl=-10.0,
            reasons=["Backtest completed"],
            iteration_traces=[
                BacktestIterationTrace(
                    iteration_index=1,
                    window_start=0,
                    window_end=59,
                    final_action="SELL",
                    final_allowed=True,
                    trade_executed=True,
                    status="CLOSED",
                    orderflow_status="NEUTRAL",
                    simulated_pnl=-10.0,
                    outcome="LOSS",
                )
            ],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--simulate-orderflow-confirmation-ab",
        "--backtest-trace-dir",
        str(trace_dir),
    )

    payload = json.loads((trace_dir / "orderflow_confirmation_ab_report.json").read_text(encoding="utf-8"))

    assert payload["b_simulated_behavior"]["executed_trades"] == 0
    assert payload["summary"]["warning"] == "B simulated behavior blocks every A executed trade"


def test_orderflow_confirmation_ab_report_works_with_no_executed_trades(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_dir = tmp_path / "ab_empty_reports"

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=1,
            trades_executed=0,
            trades_blocked=1,
            final_balance=10000.0,
            total_pnl=0.0,
            reasons=["Backtest completed"],
            iteration_traces=[
                BacktestIterationTrace(
                    iteration_index=1,
                    window_start=0,
                    window_end=59,
                    final_action="NO_TRADE",
                    final_allowed=False,
                    trade_executed=False,
                    status="NO_TRADE",
                    orderflow_status="NEUTRAL",
                )
            ],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--simulate-orderflow-confirmation-ab",
        "--backtest-trace-dir",
        str(trace_dir),
    )

    payload = json.loads((trace_dir / "orderflow_confirmation_ab_report.json").read_text(encoding="utf-8"))

    assert payload["a_current_behavior"]["executed_trades"] == 0
    assert payload["b_simulated_behavior"]["executed_trades"] == 0
    assert payload["b_simulated_behavior"]["blocked_by_orderflow_confirmation"] == 0
    assert payload["summary"]["warning"] is None


def test_backtest_trace_collection_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, bool] = {}

    def fake_run(self, candles, backtest_config, *args, **kwargs):
        seen["collect_iteration_traces"] = bool(kwargs.get("collect_iteration_traces", False))
        return BacktestResult(
            completed=True,
            status="COMPLETED",
            total_iterations=1,
            trades_executed=0,
            trades_blocked=1,
            final_balance=10000.0,
            total_pnl=0.0,
            reasons=["Backtest completed"],
        )

    monkeypatch.setattr(main.BacktestRunner, "run", fake_run)

    _run_main("--mode", "backtest", "--scenario", "bullish")

    assert seen["collect_iteration_traces"] is False


def test_backtest_max_iterations_rejects_zero() -> None:
    with pytest.raises(SystemExit):
        main.main(["--mode", "backtest", "--backtest-max-iterations", "0"])


def test_backtest_max_iterations_rejects_negative() -> None:
    with pytest.raises(SystemExit):
        main.main(["--mode", "backtest", "--backtest-max-iterations", "-1"])


def test_sierra_bar_summary_loads_as_backtest_market_candles(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=3)

    result = main._load_backtest_market_candles_from_csv(str(csv_path))

    assert result.candles is not None
    assert len(result.candles) == 3
    assert result.candles.iloc[0]["time"] == "2026-6-21 18:00:00.000000"
    assert result.candles.iloc[0]["open"] == 4160.0
    assert result.candles.iloc[0]["close"] == 4161.5
    assert "BAR_SUMMARY" in str(result.source)


def test_sierra_bar_summary_market_candles_use_first_price_ohlc_group(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=3)

    result = main._load_backtest_market_candles_from_csv(str(csv_path))

    assert result.candles is not None
    first_range = result.candles.iloc[0]["high"] - result.candles.iloc[0]["low"]
    assert first_range == 7.0
    assert result.candles.iloc[0]["high"] == 4164.0
    assert result.candles.iloc[0]["low"] == 4157.0
    assert result.candles.iloc[0]["close"] == 4161.5


def test_backtest_market_csv_can_produce_multiple_iterations(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=75)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--backtest-market-csv",
        str(csv_path),
        "--backtest-max-iterations",
        "3",
    )

    assert "- Backtest market candles:" in output
    assert "- Total iterations: 3" in output


def test_missing_backtest_market_csv_fails_safely(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"

    output = _run_main("--mode", "backtest", "--backtest-market-csv", str(missing_path))

    assert "Backtest market CSV not found" in output
    assert "Safe fallback: no backtest run" in output
    assert "- Total iterations:" not in output


def test_default_backtest_scenario_behavior_does_not_use_market_csv() -> None:
    output = _run_main("--mode", "backtest", "--scenario", "bullish", "--profile", "apex")

    assert "- Total iterations: 1" in output
    assert "- Backtest market candles:" not in output


def test_orderflow_csv_does_not_replace_backtest_market_candles(tmp_path: Path) -> None:
    csv_path = tmp_path / "sierra_bar_summary.csv"
    _write_sierra_bar_summary_csv(csv_path, rows=75)

    output = _run_main(
        "--mode",
        "backtest",
        "--scenario",
        "bullish",
        "--profile",
        "apex",
        "--orderflow-csv",
        str(csv_path),
        "--backtest-max-iterations",
        "3",
    )

    assert "Order Flow Data Quality" in output
    assert "- Total iterations: 1" in output
    assert "- Backtest market candles:" not in output
