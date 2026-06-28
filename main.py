import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from analysis.news_filter import NewsEvent, NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
from analysis.spread_filter import SpreadFilterConfig
from analysis.volatility_filter import VolatilityFilterConfig
from broker.paper_broker import PaperBroker, PaperBrokerConfig, PaperBrokerState
from config.trading_profiles import (
    TradingProfile,
    TradingProfileFactory,
    to_capital_protection_config,
    to_news_filter_config,
    to_paper_broker_config,
    to_risk_engine_config,
    to_session_filter_config,
    to_spread_filter_config,
    to_volatility_filter_config,
)
from core.backtest_runner import BacktestConfig, BacktestRunner
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from ai.orderflow_replay_coach import (
    OrderFlowReplayCoach,
    OrderFlowReplayCoachConfig,
    OrderFlowReplayCoachReview,
)
from orderflow.absorption import AbsorptionAnalyzer, AbsorptionConfig
from orderflow.data_quality import (
    OrderFlowDataQualityChecker,
    OrderFlowDataQualityConfig,
    OrderFlowDataQualityResult,
)
from orderflow.delta_cvd import DeltaCVDAnalyzer, DeltaCVDConfig
from orderflow.imbalance import ImbalanceAnalyzer, ImbalanceConfig
from orderflow.orderflow_context import OrderFlowContextCombiner, OrderFlowContextConfig, OrderFlowContextResult
from orderflow.replay import OrderFlowReplayConfig, OrderFlowReplayEngine, OrderFlowReplayResult
from orderflow.replay_report import OrderFlowReplayReport, OrderFlowReplayReportGenerator
from orderflow.sierra_chart_importer import SierraChartImporter, SierraChartImportConfig
from risk.risk_engine import RiskEngineConfig
from storage.decision_trace import DecisionTracer
from storage.backtest_quality import BacktestQualityChecker, BacktestQualityConfig
from storage.orderflow_replay_exporter import (
    OrderFlowReplayExportConfig,
    OrderFlowReplayExporter,
    OrderFlowReplayExportResult,
)
from storage.performance_report import PerformanceReporter
from storage.trade_journal import TradeJournal


@dataclass
class OrderFlowCsvDemoResult:
    """Order Flow context plus CSV data-quality status for CLI output."""

    context: OrderFlowContextResult | None = None
    data_quality: OrderFlowDataQualityResult | None = None


def _load_candles(path: Path) -> pd.DataFrame:
    """Load sample candles and fall back to a safe empty frame if needed."""
    try:
        candles = pd.read_csv(path)
    except Exception:
        candles = pd.DataFrame(columns=["time", "open", "high", "low", "close"])

    required_columns = {"time", "open", "high", "low", "close"}
    if not required_columns.issubset(candles.columns):
        for column in required_columns:
            if column not in candles.columns:
                candles[column] = 0.0

    return candles


def _build_parser() -> argparse.ArgumentParser:
    """Create a small CLI parser for demo and backtest modes."""
    parser = argparse.ArgumentParser(description="Run the AI Trader paper-trading and backtest modes")
    parser.add_argument(
        "--mode",
        default="demo",
        help="Choose execution mode: demo or backtest",
    )
    parser.add_argument(
        "--scenario",
        default="weak",
        help="Choose which sample scenario to run (bullish, bearish, weak, or all)",
    )
    parser.add_argument(
        "--profile",
        default="safe",
        help="Choose profile: apex, spot, or safe",
    )
    parser.add_argument(
        "--session-time",
        default="",
        help="Optional UTC time override, example: 2026-06-28T14:00:00Z",
    )
    parser.add_argument(
        "--news-event",
        action="append",
        default=[],
        help="Optional manual news event in NAME:TIME:IMPACT format. Repeatable.",
    )
    parser.add_argument(
        "--spread",
        default="",
        help="Optional current spread value for spread safety checks, example: 2.0",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Show decision trace details in output",
    )
    parser.add_argument(
        "--show-orderflow",
        action="store_true",
        help="Show detailed Order Flow context output when available",
    )
    parser.add_argument(
        "--orderflow-csv",
        default="",
        help="Optional sample footprint CSV path for research-only Order Flow context",
    )
    parser.add_argument(
        "--orderflow-replay-csv",
        default="",
        help="Optional footprint CSV path for standalone Order Flow replay output",
    )
    parser.add_argument(
        "--show-orderflow-replay-steps",
        action="store_true",
        help="Show each Order Flow replay step when --orderflow-replay-csv is provided",
    )
    parser.add_argument(
        "--export-orderflow-report",
        action="store_true",
        help="Export Order Flow replay report txt/json files when --orderflow-replay-csv is provided",
    )
    parser.add_argument(
        "--orderflow-report-dir",
        default="reports",
        help="Output folder for exported Order Flow replay reports",
    )
    parser.add_argument(
        "--no-orderflow-report-steps",
        action="store_true",
        help="Export Order Flow replay report without detailed replay steps",
    )
    return parser


def _unknown_orderflow_context(reason: str) -> OrderFlowContextResult:
    """Build a safe UNKNOWN context when CSV order flow cannot be used."""
    return OrderFlowContextResult(
        bias="UNKNOWN",
        confidence=0.0,
        delta_direction=None,
        imbalance_bias=None,
        absorption_bias=None,
        final_cvd=None,
        reasons=[reason],
        blocking_reasons=[],
    )


def _quality_result(
    status: str,
    passed: bool,
    reason: str,
    blocking_reason: str | None = None,
) -> OrderFlowDataQualityResult:
    """Build a small data-quality result for CSV load failures."""
    return OrderFlowDataQualityResult(
        passed=passed,
        status=status,
        candle_count=0,
        total_levels=0,
        invalid_levels=0,
        invalid_level_ratio=0.0,
        reasons=[reason],
        blocking_reasons=[blocking_reason] if blocking_reason else [],
    )


def _orderflow_context_blocked_by_quality(
    reason: str,
    quality_result: OrderFlowDataQualityResult,
) -> OrderFlowContextResult:
    """Build an inactive Order Flow context when data quality blocks the CSV."""
    blocking_reasons = list(quality_result.blocking_reasons)
    if not blocking_reasons:
        blocking_reasons = [reason]

    return OrderFlowContextResult(
        bias="UNKNOWN",
        confidence=0.0,
        delta_direction=None,
        imbalance_bias=None,
        absorption_bias=None,
        final_cvd=None,
        reasons=[
            reason,
            *_orderflow_quality_trace_reasons(quality_result),
            *list(quality_result.reasons),
        ],
        blocking_reasons=blocking_reasons,
    )


def _orderflow_quality_trace_reasons(quality_result: OrderFlowDataQualityResult) -> list[str]:
    """Create simple key=value lines that also show up in decision trace."""
    blocking_text = "; ".join(quality_result.blocking_reasons) if quality_result.blocking_reasons else "None"
    return [
        f"orderflow_data_quality_status={quality_result.status}",
        f"orderflow_data_quality_passed={quality_result.passed}",
        f"orderflow_data_quality_blocking_reasons={blocking_text}",
    ]


def _resolve_orderflow_csv_path(raw_path: str) -> Path:
    """Resolve user-provided CSV paths relative to the project folder."""
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parent / path


def _build_orderflow_context_from_csv(raw_path: str) -> OrderFlowCsvDemoResult:
    """Load a footprint CSV and convert it into one Order Flow context.

    This is intentionally offline-only: it reads a CSV from disk and never
    connects to Sierra Chart, CME, a broker, or any external data service.
    """
    cleaned = (raw_path or "").strip()
    if not cleaned:
        return OrderFlowCsvDemoResult()

    csv_path = _resolve_orderflow_csv_path(cleaned)
    if not csv_path.exists() or not csv_path.is_file():
        quality_result = _quality_result(
            status="INVALID",
            passed=False,
            reason=f"Order Flow CSV not found: {cleaned}",
            blocking_reason="Order Flow CSV path does not exist",
        )
        return OrderFlowCsvDemoResult(
            context=_orderflow_context_blocked_by_quality(f"Order Flow CSV not found: {cleaned}", quality_result),
            data_quality=quality_result,
        )

    importer = SierraChartImporter()
    candles = importer.load_csv(str(csv_path), SierraChartImportConfig())
    quality_result = OrderFlowDataQualityChecker().check(candles, OrderFlowDataQualityConfig())
    if quality_result.status in {"FAILED", "EMPTY", "INVALID"} or not quality_result.passed:
        reason = f"Order Flow CSV blocked by data quality: {csv_path.name}"
        if not candles:
            reason = f"Order Flow CSV could not be imported: {csv_path.name}"
        return OrderFlowCsvDemoResult(
            context=_orderflow_context_blocked_by_quality(reason, quality_result),
            data_quality=quality_result,
        )

    latest_candle = candles[-1]
    delta_result = DeltaCVDAnalyzer().analyze(candles, DeltaCVDConfig())
    imbalance_result = ImbalanceAnalyzer().analyze(latest_candle, ImbalanceConfig())
    absorption_result = AbsorptionAnalyzer().analyze(latest_candle, AbsorptionConfig())
    context = OrderFlowContextCombiner().combine(
        delta_result,
        imbalance_result,
        absorption_result,
        OrderFlowContextConfig(),
    )
    context.reasons.insert(0, f"Loaded Order Flow CSV: {csv_path.name}")
    context.reasons.extend(_orderflow_quality_trace_reasons(quality_result))
    context.reasons.extend(quality_result.reasons)
    context.reasons.append(importer.explain_import(candles))
    return OrderFlowCsvDemoResult(context=context, data_quality=quality_result)


def _build_orderflow_replay_from_csv(raw_path: str) -> OrderFlowReplayResult | None:
    """Run standalone Order Flow replay from a CSV when requested."""
    cleaned = (raw_path or "").strip()
    if not cleaned:
        return None

    csv_path = _resolve_orderflow_csv_path(cleaned)
    if not csv_path.exists() or not csv_path.is_file():
        return OrderFlowReplayResult(
            steps=[],
            final_bias="UNKNOWN",
            final_confidence=0.0,
            final_cvd=0.0,
            data_quality_status="INVALID",
            passed=False,
            reasons=[f"Order Flow replay CSV not found: {cleaned}"],
            blocking_reasons=["Order Flow replay CSV path does not exist"],
        )

    return OrderFlowReplayEngine().replay_csv(str(csv_path), OrderFlowReplayConfig())


def _parse_session_time(raw_value: str) -> tuple[datetime, str | None]:
    """Parse optional session time string and return safe UTC fallback on errors."""
    if not raw_value:
        return datetime.now(timezone.utc), None

    cleaned = raw_value.strip()
    if not cleaned:
        return datetime.now(timezone.utc), None

    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return datetime.now(timezone.utc), "Invalid --session-time format. Using current UTC fallback."

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc), "Naive --session-time provided. Treating it as UTC."

    return parsed.astimezone(timezone.utc), None


def _parse_news_event(raw_value: str) -> tuple[NewsEvent | None, str | None]:
    """Parse one --news-event value in NAME:TIME:IMPACT format."""
    cleaned = (raw_value or "").strip()
    if not cleaned:
        return None, "Empty --news-event ignored."

    first_colon = cleaned.find(":")
    last_colon = cleaned.rfind(":")
    if first_colon <= 0 or last_colon <= first_colon:
        return None, f"Invalid --news-event format '{raw_value}'. Expected NAME:TIME:IMPACT."

    name = cleaned[:first_colon].strip()
    time_text = cleaned[first_colon + 1 : last_colon].strip()
    impact = cleaned[last_colon + 1 :].strip().upper()

    if not name:
        return None, f"Invalid --news-event '{raw_value}': name is required."

    if impact not in {"HIGH", "MEDIUM", "LOW"}:
        return None, f"Invalid --news-event impact '{impact}' in '{raw_value}'. Use HIGH, MEDIUM, or LOW."

    parsed_time, warning = _parse_session_time(time_text)
    if warning and "Invalid" in warning:
        return None, f"Invalid --news-event time in '{raw_value}'."

    event = NewsEvent(name=name, event_time_utc=parsed_time, impact=impact)
    if warning:
        return event, f"{warning} (event '{name}')"
    return event, None


def _parse_news_events(raw_values: list[str]) -> tuple[list[NewsEvent], list[str]]:
    """Parse all --news-event values and return valid events plus warnings."""
    events: list[NewsEvent] = []
    warnings: list[str] = []

    for raw in raw_values:
        event, warning = _parse_news_event(raw)
        if warning:
            warnings.append(warning)
        if event is not None:
            events.append(event)

    return events, warnings


def _parse_spread(raw_value: str) -> tuple[float | None, str | None]:
    """Parse optional spread value and keep safe fallback behavior on errors."""
    if raw_value is None:
        return None, None

    cleaned = str(raw_value).strip()
    if not cleaned:
        return None, None

    try:
        parsed = float(cleaned)
    except ValueError:
        return None, "Invalid --spread value. Using unknown spread safe behavior."

    return parsed, None


def _select_profile(profile_key: str) -> TradingProfile | None:
    """Map a profile key to a TradingProfile object."""
    normalized = profile_key.lower().strip()
    profile_map = {
        "apex": TradingProfileFactory.create_apex_futures_profile,
        "spot": TradingProfileFactory.create_spot_gold_profile,
        "safe": TradingProfileFactory.create_safe_default_profile,
    }
    creator = profile_map.get(normalized)
    if creator is None:
        return None
    return creator()


def _print_profile_summary(profile: TradingProfile) -> None:
    """Print selected profile details for transparency."""
    print("\nSelected Trading Profile")
    print(f"- Profile name: {profile.profile_name}")
    print(f"- Account type: {profile.account_type}")
    print(f"- Symbol: {profile.symbol}")
    print(f"- Starting balance: {profile.starting_balance:.2f}")
    print(f"- Daily profit target: {profile.daily_profit_target:.2f}")
    print(f"- Max daily loss: {profile.max_daily_loss:.2f}")
    print(f"- Risk per trade percent: {profile.risk_per_trade_percent:.2f}%")


def _print_session_summary(
    session_status: str | None,
    active_session: str | None,
    session_allowed: bool,
    session_blocking_reasons: list[str],
) -> None:
    """Print session filter status in a simple user-facing format."""
    print("\nSession Filter")
    print(f"- Session filter status: {session_status if session_status else 'N/A'}")
    print(f"- Active session: {active_session if active_session else 'None'}")
    print(f"- Session allowed: {session_allowed}")
    if session_blocking_reasons:
        print(f"- Session blocking reasons: {'; '.join(session_blocking_reasons)}")
    else:
        print("- Session blocking reasons: None")


def _print_news_summary(
    news_status: str | None,
    active_news_event: str | None,
    news_allowed: bool,
    news_blocking_reasons: list[str],
) -> None:
    """Print news filter status in a simple user-facing format."""
    print("\nNews Filter")
    print(f"- News filter status: {news_status if news_status else 'N/A'}")
    print(f"- Active news event: {active_news_event if active_news_event else 'None'}")
    print(f"- News allowed: {news_allowed}")
    if news_blocking_reasons:
        print(f"- News blocking reasons: {'; '.join(news_blocking_reasons)}")
    else:
        print("- News blocking reasons: None")


def _print_volatility_summary(
    volatility_status: str | None,
    atr: float | None,
    last_candle_range: float | None,
    volatility_allowed: bool,
    volatility_blocking_reasons: list[str],
) -> None:
    """Print volatility filter status in a simple user-facing format."""
    atr_text = f"{atr:.4f}" if atr is not None else "N/A"
    range_text = f"{last_candle_range:.4f}" if last_candle_range is not None else "N/A"

    print("\nVolatility Filter")
    print(f"- Volatility filter status: {volatility_status if volatility_status else 'N/A'}")
    print(f"- ATR: {atr_text}")
    print(f"- Last candle range: {range_text}")
    print(f"- Volatility allowed: {volatility_allowed}")
    if volatility_blocking_reasons:
        print(f"- Volatility blocking reasons: {'; '.join(volatility_blocking_reasons)}")
    else:
        print("- Volatility blocking reasons: None")


def _print_spread_summary(
    spread_status: str | None,
    spread: float | None,
    spread_allowed: bool,
    spread_blocking_reasons: list[str],
) -> None:
    """Print spread filter status in a simple user-facing format."""
    spread_text = f"{spread:.4f}" if spread is not None else "N/A"

    print("\nSpread Filter")
    print(f"- Spread filter status: {spread_status if spread_status else 'N/A'}")
    print(f"- Current spread: {spread_text}")
    print(f"- Spread allowed: {spread_allowed}")
    if spread_blocking_reasons:
        print(f"- Spread blocking reasons: {'; '.join(spread_blocking_reasons)}")
    else:
        print("- Spread blocking reasons: None")


def _print_orderflow_summary(
    orderflow_checked: bool,
    orderflow_bias: str | None,
    orderflow_confidence: float | None,
    orderflow_reasons: list[str],
    orderflow_blocking_reasons: list[str],
    show_detail: bool = False,
    delta_direction: str | None = None,
    imbalance_bias: str | None = None,
    absorption_bias: str | None = None,
    final_cvd: float | None = None,
    data_quality: OrderFlowDataQualityResult | None = None,
) -> None:
    """Print order flow context status without requiring footprint data."""
    bias = orderflow_bias if orderflow_bias else "UNKNOWN"
    confidence = float(orderflow_confidence or 0.0)
    has_context = bool(orderflow_checked and bias not in {"UNKNOWN", None} and confidence > 0.0)
    status = "Provided" if has_context else "Not provided"
    if bias == "NEUTRAL":
        status = "Neutral"
    elif orderflow_blocking_reasons:
        status = "Conflicting or blocked"

    print("\nOrder Flow Context")
    print(f"- Active: {has_context}")
    print(f"- Bias: {bias}")
    print(f"- Confidence: {confidence:.1f}")
    print(f"- Status: {status}")
    reason_text = "; ".join(orderflow_reasons) if orderflow_reasons else "Order Flow context not provided"
    print(f"- Reason: {reason_text}")

    if has_context or show_detail:
        final_cvd_text = f"{final_cvd:.2f}" if final_cvd is not None else "N/A"
        print(f"- Delta direction: {delta_direction or 'N/A'}")
        print(f"- Imbalance bias: {imbalance_bias or 'N/A'}")
        print(f"- Absorption bias: {absorption_bias or 'N/A'}")
        print(f"- Final CVD: {final_cvd_text}")

    if show_detail:
        print(f"- Order Flow checked: {orderflow_checked}")
        if orderflow_blocking_reasons:
            print(f"- Order Flow blocking reasons: {'; '.join(orderflow_blocking_reasons)}")
        else:
            print("- Order Flow blocking reasons: None")

    if data_quality is not None:
        print("\nOrder Flow Data Quality")
        print(f"- Status: {data_quality.status}")
        print(f"- Passed: {data_quality.passed}")
        print(f"- Candle count: {data_quality.candle_count}")
        print(f"- Total levels: {data_quality.total_levels}")
        print(f"- Invalid levels: {data_quality.invalid_levels}")
        print(f"- Invalid level ratio: {data_quality.invalid_level_ratio:.2f}")
        reasons_text = "; ".join(data_quality.reasons) if data_quality.reasons else "None"
        blocks_text = "; ".join(data_quality.blocking_reasons) if data_quality.blocking_reasons else "None"
        print(f"- Reasons: {reasons_text}")
        print(f"- Blocking reasons: {blocks_text}")


def _print_orderflow_replay_summary(
    replay_result: OrderFlowReplayResult | None,
    show_steps: bool,
    export_report: bool = False,
    export_config: OrderFlowReplayExportConfig | None = None,
) -> None:
    """Print standalone Order Flow replay output without affecting trading flow."""
    if replay_result is None:
        if export_report:
            _print_orderflow_replay_export(
                OrderFlowReplayExportResult(
                    exported=False,
                    text_path=None,
                    json_path=None,
                    reasons=["Order Flow replay CSV is required to export report"],
                    blocking_reasons=["Order Flow replay CSV is required to export report"],
                )
            )
        return

    active = bool(replay_result.passed and len(replay_result.steps) > 0)
    reasons_text = "; ".join(replay_result.reasons) if replay_result.reasons else "None"
    blocks_text = "; ".join(replay_result.blocking_reasons) if replay_result.blocking_reasons else "None"

    print("\nOrder Flow Replay")
    print(f"- Active: {active}")
    print(f"- Passed: {replay_result.passed}")
    print(f"- Data quality status: {replay_result.data_quality_status or 'N/A'}")
    print(f"- Steps: {len(replay_result.steps)}")
    print(f"- Final bias: {replay_result.final_bias}")
    print(f"- Final confidence: {replay_result.final_confidence:.1f}")
    print(f"- Final CVD: {replay_result.final_cvd:.2f}")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocks_text}")

    replay_report = OrderFlowReplayReportGenerator().generate(replay_result)
    _print_orderflow_replay_report(replay_report)
    coach_review = OrderFlowReplayCoach().review(replay_report, OrderFlowReplayCoachConfig())
    _print_orderflow_replay_coach_review(coach_review)

    if export_report:
        resolved_export_config = export_config or OrderFlowReplayExportConfig()
        export_result = OrderFlowReplayExporter().export_all(
            replay_result,
            replay_report,
            coach_review,
            resolved_export_config,
        )
        _print_orderflow_replay_export(export_result)

    if not show_steps:
        return

    print("- Replay steps:")
    if not replay_result.steps:
        print("  - None")
        return

    for step in replay_result.steps:
        print(f"  - Index: {step.index}")
        print(f"    Time: {step.time if step.time is not None else 'N/A'}")
        print(f"    Candle delta: {step.candle_delta:.2f}")
        print(f"    Cumulative delta: {step.cumulative_delta:.2f}")
        print(f"    Delta direction: {step.delta_direction}")
        print(f"    Imbalance bias: {step.imbalance_bias}")
        print(f"    Absorption bias: {step.absorption_bias}")
        print(f"    Order Flow bias: {step.orderflow_bias}")
        print(f"    Confidence: {step.orderflow_confidence:.1f}")


def _print_orderflow_replay_export(result: OrderFlowReplayExportResult) -> None:
    """Print export status without interrupting the demo/backtest flow."""
    reasons_text = "; ".join(result.reasons) if result.reasons else "None"
    blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

    print("\nOrder Flow Replay Export")
    print(f"- Exported: {result.exported}")
    print(f"- Text path: {result.text_path or 'N/A'}")
    print(f"- JSON path: {result.json_path or 'N/A'}")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocks_text}")


def _print_orderflow_replay_report(report: OrderFlowReplayReport) -> None:
    """Print a compact replay report below the replay summary."""
    warnings_text = "; ".join(report.warnings) if report.warnings else "None"
    reasons_text = "; ".join(report.reasons) if report.reasons else "None"

    print("\nOrder Flow Replay Report")
    print(f"- Total steps: {report.total_steps}")
    print(f"- Bullish steps: {report.bullish_steps}")
    print(f"- Bearish steps: {report.bearish_steps}")
    print(f"- Neutral steps: {report.neutral_steps}")
    print(f"- Unknown steps: {report.unknown_steps}")
    print(f"- Dominant bias: {report.dominant_bias}")
    print(f"- Average confidence: {report.average_confidence:.1f}")
    print(f"- Max confidence: {report.max_confidence:.1f}")
    print(f"- Min confidence: {report.min_confidence:.1f}")
    print(f"- Final bias: {report.final_bias}")
    print(f"- Final confidence: {report.final_confidence:.1f}")
    print(f"- Final CVD: {report.final_cvd:.2f}")
    print(f"- Warnings: {warnings_text}")
    print(f"- Reasons: {reasons_text}")


def _print_orderflow_replay_coach_review(review: OrderFlowReplayCoachReview) -> None:
    """Print beginner-friendly coach feedback for the replay report."""
    strengths_text = "; ".join(review.strengths) if review.strengths else "None"
    risks_text = "; ".join(review.risks) if review.risks else "None"
    lessons_text = "; ".join(review.lessons) if review.lessons else "None"
    next_steps_text = "; ".join(review.next_steps) if review.next_steps else "None"
    warnings_text = "; ".join(review.warnings) if review.warnings else "None"
    reasons_text = "; ".join(review.reasons) if review.reasons else "None"

    print("\nAI Coach Order Flow Replay Review")
    print(f"- Status: {review.status}")
    print(f"- Grade: {review.grade}")
    print(f"- Summary: {review.summary}")
    print(f"- Market read: {review.market_read}")
    print(f"- Strengths: {strengths_text}")
    print(f"- Risks: {risks_text}")
    print(f"- Lessons: {lessons_text}")
    print(f"- Next steps: {next_steps_text}")
    print(f"- Warnings: {warnings_text}")
    print(f"- Reasons: {reasons_text}")


def _create_broker_state(config: PaperBrokerConfig) -> PaperBrokerState:
    """Create broker state using the configured starting balance."""
    return PaperBroker().create_default_state(config)


def _get_scenario_data_path(name: str) -> Path:
    """Resolve scenario name to a sample data file path."""
    scenario_files = {
        "bullish": "bullish_sample_xauusd.csv",
        "bearish": "bearish_sample_xauusd.csv",
        "weak": "weak_sample_xauusd.csv",
    }
    return Path(__file__).resolve().parent / "data" / scenario_files.get(name, "weak_sample_xauusd.csv")


def _print_performance_report(journal: TradeJournal):
    """Print a readable performance report from journal entries."""
    performance = PerformanceReporter().generate_report(journal)

    print("\nPerformance Report")
    print(f"- Total trades: {performance.total_trades}")
    print(f"- Executed trades: {performance.executed_trades}")
    print(f"- Blocked trades: {performance.blocked_trades}")
    print(f"- Wins: {performance.wins}")
    print(f"- Losses: {performance.losses}")
    print(f"- Win rate: {performance.win_rate:.2f}%")
    print(f"- Total PnL: {performance.total_pnl:.2f}")
    if performance.profit_factor == float("inf"):
        print("- Profit factor: INF")
    else:
        print(f"- Profit factor: {performance.profit_factor:.2f}")
    print(f"- Max drawdown: {performance.max_drawdown:.2f}")

    return performance


def _print_decision_trace(trace_id: str | None, trace_explanation: str | None) -> None:
    """Print a readable decision trace section without crashing on missing data."""
    print("\nDecision Trace")
    if not trace_id and not trace_explanation:
        print("- Trace not available")
        return

    segments = [segment.strip() for segment in (trace_explanation or "").split(" | ") if segment.strip()]
    parsed: dict[str, str] = {}
    for segment in segments:
        if ":" not in segment:
            continue
        key, value = segment.split(":", 1)
        parsed[key.strip()] = value.strip()

    trace_id_text = trace_id or parsed.get("Decision trace ID") or "N/A"
    final_action = parsed.get("Final action", "NO_TRADE")
    final_allowed = parsed.get("Final allowed", "False")
    steps_text = parsed.get("Steps", "None")
    blocking_text = parsed.get("Blocking reasons", "None")

    print(f"- Trace ID: {trace_id_text}")
    print(f"- Final action: {final_action}")
    print(f"- Final allowed: {final_allowed}")

    print("- Steps:")
    if steps_text == "None":
        print("  - None")
    else:
        for raw_step in [item.strip() for item in steps_text.split(" || ") if item.strip()]:
            print(f"  - {raw_step}")

    print(f"- Blocking reasons: {blocking_text}")


def _run_demo_scenario(
    name: str,
    profile: TradingProfile,
    capital_config: CapitalProtectionConfig,
    broker_config: PaperBrokerConfig,
    risk_config: RiskEngineConfig,
    session_config: SessionFilterConfig,
    news_config: NewsFilterConfig,
    volatility_config: VolatilityFilterConfig,
    spread_config: SpreadFilterConfig,
    current_spread: float | None,
    session_time: datetime,
    show_trace: bool,
    show_orderflow: bool,
    orderflow_csv_result: OrderFlowCsvDemoResult,
    orderflow_replay_result: OrderFlowReplayResult | None,
    show_orderflow_replay_steps: bool,
    export_orderflow_report: bool,
    orderflow_export_config: OrderFlowReplayExportConfig,
) -> None:
    """Run one demo scenario and print the results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    data_path = _get_scenario_data_path(name)
    if not data_path.exists():
        print(f"- File not found: {data_path.name}")
        print("- Safe fallback: no trade")
        return

    candles = _load_candles(data_path)

    journal = TradeJournal()
    reviewer = TradeReviewer()
    flow = PaperTradingFlow()
    tracer = DecisionTracer() if show_trace else None
    flow_config = PaperTradingFlowConfig(symbol=profile.symbol)
    broker_state = _create_broker_state(broker_config)
    orderflow_context_result = orderflow_csv_result.context

    result = flow.run_single_timeframe(
        candles,
        flow_config,
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        capital_config,
        CapitalProtectionState(),
        broker_config,
        broker_state,
        journal,
        risk_config,
        session_config,
        session_time,
        news_config,
        volatility_config,
        spread_config,
        current_spread,
        tracer,
        orderflow_context_result=orderflow_context_result,
    )

    print("\nMarket result")
    print(f"- Market bias: {result.market_bias}")
    print(f"- Final decision: {result.decision_action}")
    print(f"- Trade executed or blocked: {'Executed' if result.trade_executed else 'Blocked / No trade'}")
    print(f"- Paper balance: {result.balance if result.balance is not None else 'N/A'}")

    if result.reasons:
        print(f"- Reasons: {'; '.join(result.reasons)}")

    _print_session_summary(
        result.session_status,
        result.active_session,
        result.session_allowed,
        result.session_blocking_reasons,
    )

    _print_news_summary(
        result.news_status,
        result.active_news_event,
        result.news_allowed,
        result.news_blocking_reasons,
    )

    _print_volatility_summary(
        result.volatility_status,
        result.atr,
        result.last_candle_range,
        result.volatility_allowed,
        result.volatility_blocking_reasons,
    )

    _print_spread_summary(
        result.spread_status,
        result.spread,
        result.spread_allowed,
        result.spread_blocking_reasons,
    )

    _print_orderflow_summary(
        result.orderflow_checked,
        result.orderflow_bias,
        result.orderflow_confidence,
        result.orderflow_reasons,
        result.orderflow_blocking_reasons,
        show_orderflow,
        delta_direction=getattr(orderflow_context_result, "delta_direction", None),
        imbalance_bias=getattr(orderflow_context_result, "imbalance_bias", None),
        absorption_bias=getattr(orderflow_context_result, "absorption_bias", None),
        final_cvd=getattr(orderflow_context_result, "final_cvd", None),
        data_quality=orderflow_csv_result.data_quality,
    )

    print("\nJournal summary")
    summary = journal.summarize()
    print(f"- Entries: {summary['total_entries']}")
    print(f"- Executed trades: {summary['executed_trades']}")
    print(f"- Blocked trades: {summary['blocked_trades']}")
    print(f"- Total PnL: {summary['total_pnl']:.2f}")

    print("\nAI Coach review")
    if journal.get_all_entries():
        for review in reviewer.review_journal(journal):
            print(f"- {review.trade_id}: {review.grade}")
            print(f"  Summary: {review.summary}")
            print(f"  Lesson: {review.lesson}")
    else:
        print("- No journal entries were recorded.")

    _print_performance_report(journal)

    print("\nFlow explanation")
    print(f"- {flow.explain(result)}")

    if show_trace:
        _print_decision_trace(result.trace_id, result.trace_explanation)

    _print_orderflow_replay_summary(
        orderflow_replay_result,
        show_orderflow_replay_steps,
        export_orderflow_report,
        orderflow_export_config,
    )

    if not profile.enabled:
        print("- Safe profile is a conservative fallback. Trading is intentionally blocked.")


def _run_backtest_scenario(
    name: str,
    profile: TradingProfile,
    capital_config: CapitalProtectionConfig,
    broker_config: PaperBrokerConfig,
    risk_config: RiskEngineConfig,
    session_config: SessionFilterConfig,
    news_config: NewsFilterConfig,
    volatility_config: VolatilityFilterConfig,
    spread_config: SpreadFilterConfig,
    current_spread: float | None,
    session_time: datetime,
    show_trace: bool,
    show_orderflow: bool,
    orderflow_csv_result: OrderFlowCsvDemoResult,
    orderflow_replay_result: OrderFlowReplayResult | None,
    show_orderflow_replay_steps: bool,
    export_orderflow_report: bool,
    orderflow_export_config: OrderFlowReplayExportConfig,
) -> None:
    """Run one backtest scenario and print aggregate results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    data_path = _get_scenario_data_path(name)
    if not data_path.exists():
        print(f"- File not found: {data_path.name}")
        print("- Safe fallback: no backtest run")
        return

    candles = _load_candles(data_path)
    journal = TradeJournal()
    broker_state = _create_broker_state(broker_config)
    runner = BacktestRunner()
    orderflow_context_result = orderflow_csv_result.context
    result = runner.run(
        candles,
        BacktestConfig(symbol=profile.symbol, timeframe="M5", window_size=60, step_size=5),
        PaperTradingFlowConfig(symbol=profile.symbol, simulate_exit=True),
        MarketAnalyzerConfig(),
        MultiTimeframeConfig(),
        capital_config,
        CapitalProtectionState(),
        broker_config,
        broker_state,
        risk_config,
        journal,
        session_config,
        session_time,
        news_config,
        volatility_config,
        spread_config,
        current_spread,
        orderflow_context_result,
    )

    print("\nAI Trader Backtest")
    print(f"- Scenario: {name}")
    print(f"- Total iterations: {result.total_iterations}")
    print(f"- Trades executed: {result.trades_executed}")
    print(f"- Trades blocked: {result.trades_blocked}")
    print(f"- Final balance: {result.final_balance:.2f}")
    print(f"- Total PnL: {result.total_pnl:.2f}")
    print("- Note: research-only simulation, not live trading")
    print("- Note: decision tracing is available with --show-trace")

    performance = _print_performance_report(journal)

    quality = BacktestQualityChecker().evaluate(
        result,
        performance,
        BacktestQualityConfig(),
    )

    failures_text = "; ".join(quality.failures) if quality.failures else "None"
    warnings_text = "; ".join(quality.warnings) if quality.warnings else "None"
    if quality.grade == "INSUFFICIENT_DATA":
        recommendation = "Needs more data"
    elif not quality.passed:
        recommendation = "Not ready for live trading"
    elif quality.grade == "GOOD":
        recommendation = "Promising but needs paper testing"
    else:
        recommendation = "Good research result, still not live-ready"

    print("\nBacktest Quality Check")
    print(f"- Grade: {quality.grade}")
    print(f"- Score: {quality.score:.1f}")
    print(f"- Passed: {quality.passed}")
    print(f"- Failures: {failures_text}")
    print(f"- Warnings: {warnings_text}")
    print(f"- Recommendation: {recommendation}")

    _print_session_summary(
        result.session_status,
        result.active_session,
        result.session_allowed,
        result.session_blocking_reasons,
    )

    _print_news_summary(
        result.news_status,
        result.active_news_event,
        result.news_allowed,
        result.news_blocking_reasons,
    )

    _print_volatility_summary(
        result.volatility_status,
        result.atr,
        result.last_candle_range,
        result.volatility_allowed,
        result.volatility_blocking_reasons,
    )

    _print_spread_summary(
        result.spread_status,
        result.spread,
        result.spread_allowed,
        result.spread_blocking_reasons,
    )

    if orderflow_context_result is None:
        _print_orderflow_summary(
            orderflow_checked=False,
            orderflow_bias="UNKNOWN",
            orderflow_confidence=0.0,
            orderflow_reasons=["Order Flow context not provided for this backtest run"],
            orderflow_blocking_reasons=[],
            show_detail=show_orderflow,
            data_quality=orderflow_csv_result.data_quality,
        )
    else:
        _print_orderflow_summary(
            orderflow_checked=True,
            orderflow_bias=orderflow_context_result.bias,
            orderflow_confidence=orderflow_context_result.confidence,
            orderflow_reasons=list(orderflow_context_result.reasons),
            orderflow_blocking_reasons=list(orderflow_context_result.blocking_reasons),
            show_detail=show_orderflow,
            delta_direction=orderflow_context_result.delta_direction,
            imbalance_bias=orderflow_context_result.imbalance_bias,
            absorption_bias=orderflow_context_result.absorption_bias,
            final_cvd=orderflow_context_result.final_cvd,
            data_quality=orderflow_csv_result.data_quality,
        )

    print("\nBacktest explanation")
    print(f"- {runner.explain(result)}")

    if show_trace:
        last_window_size = 60
        if len(candles) >= last_window_size:
            last_window = candles.iloc[-last_window_size:].copy()
            tracer = DecisionTracer()
            preview_flow = PaperTradingFlow()
            preview_result = preview_flow.run_single_timeframe(
                last_window,
                PaperTradingFlowConfig(symbol=profile.symbol, simulate_exit=True),
                MarketAnalyzerConfig(),
                MultiTimeframeConfig(),
                capital_config,
                CapitalProtectionState(),
                broker_config,
                _create_broker_state(broker_config),
                None,
                risk_config,
                session_config,
                session_time,
                news_config,
                volatility_config,
                spread_config,
                current_spread,
                tracer,
                orderflow_context_result=orderflow_context_result,
            )
            print("\nDecision Trace (Last Iteration)")
            _print_decision_trace(preview_result.trace_id, preview_result.trace_explanation)
        else:
            print("\nDecision Trace")
            print("- Trace unavailable: not enough candles for a preview window")

    _print_orderflow_replay_summary(
        orderflow_replay_result,
        show_orderflow_replay_steps,
        export_orderflow_report,
        orderflow_export_config,
    )

    if not profile.enabled:
        print("- Safe profile is a conservative fallback. Trading is intentionally blocked.")


def main(args: list[str] | None = None) -> None:
    """Run demo or backtest mode using research-only modules."""
    parser = _build_parser()
    if args is None:
        parsed_args, _ = parser.parse_known_args()
    else:
        parsed_args, _ = parser.parse_known_args(args)

    mode = parsed_args.mode.lower().strip() if parsed_args.mode else "demo"
    scenario = parsed_args.scenario.lower().strip() if parsed_args.scenario else "weak"
    profile_key = parsed_args.profile.lower().strip() if parsed_args.profile else "safe"
    parsed_session_time, session_time_warning = _parse_session_time(parsed_args.session_time or "")
    news_events, news_warnings = _parse_news_events(parsed_args.news_event or [])
    parsed_spread, spread_warning = _parse_spread(parsed_args.spread)
    show_trace = bool(getattr(parsed_args, "show_trace", False))
    show_orderflow = bool(getattr(parsed_args, "show_orderflow", False))
    orderflow_csv_result = _build_orderflow_context_from_csv(getattr(parsed_args, "orderflow_csv", ""))
    orderflow_replay_result = _build_orderflow_replay_from_csv(getattr(parsed_args, "orderflow_replay_csv", ""))
    show_orderflow_replay_steps = bool(getattr(parsed_args, "show_orderflow_replay_steps", False))
    export_orderflow_report = bool(getattr(parsed_args, "export_orderflow_report", False))
    orderflow_export_config = OrderFlowReplayExportConfig(
        output_dir=getattr(parsed_args, "orderflow_report_dir", "reports") or "reports",
        include_steps=not bool(getattr(parsed_args, "no_orderflow_report_steps", False)),
    )

    if mode not in {"demo", "backtest"}:
        print(f"Invalid mode: {mode}")
        print("Safe fallback: choose --mode demo or --mode backtest")
        return

    if mode == "demo":
        print("AI Trader Paper Trading Demo")
        print("=" * 32)
    else:
        print("AI Trader Backtest")
        print("=" * 18)

    if scenario not in {"bullish", "bearish", "weak", "all"}:
        print(f"Invalid scenario: {scenario}")
        print("Safe fallback: choose bullish, bearish, weak, or all")
        return

    selected_profile = _select_profile(profile_key)
    if selected_profile is None:
        print(f"Invalid profile: {profile_key}")
        print("Safe fallback: choose --profile apex, --profile spot, or --profile safe")
        return

    capital_config = to_capital_protection_config(selected_profile)
    risk_config = to_risk_engine_config(selected_profile)
    broker_config = to_paper_broker_config(selected_profile)
    session_config = to_session_filter_config(selected_profile)
    news_config = to_news_filter_config(selected_profile, news_events)
    volatility_config = to_volatility_filter_config(selected_profile)
    spread_config = to_spread_filter_config(selected_profile)

    _print_profile_summary(selected_profile)
    if session_time_warning:
        print(f"- Warning: {session_time_warning}")
    for warning in news_warnings:
        print(f"- Warning: {warning}")
    if spread_warning:
        print(f"- Warning: {spread_warning}")
    if not selected_profile.enabled:
        print("- Note: Safe profile selected. This conservative fallback keeps trading disabled.")

    if scenario == "all":
        for scenario_name in ["bullish", "bearish", "weak"]:
            if mode == "demo":
                _run_demo_scenario(
                    scenario_name,
                    selected_profile,
                    capital_config,
                    broker_config,
                    risk_config,
                    session_config,
                    news_config,
                    volatility_config,
                    spread_config,
                    parsed_spread,
                    parsed_session_time,
                    show_trace,
                    show_orderflow,
                    orderflow_csv_result,
                    orderflow_replay_result,
                    show_orderflow_replay_steps,
                    export_orderflow_report,
                    orderflow_export_config,
                )
            else:
                _run_backtest_scenario(
                    scenario_name,
                    selected_profile,
                    capital_config,
                    broker_config,
                    risk_config,
                    session_config,
                    news_config,
                    volatility_config,
                    spread_config,
                    parsed_spread,
                    parsed_session_time,
                    show_trace,
                    show_orderflow,
                    orderflow_csv_result,
                    orderflow_replay_result,
                    show_orderflow_replay_steps,
                    export_orderflow_report,
                    orderflow_export_config,
                )
            print("\n" + "=" * 40)
            print()
        return

    if mode == "demo":
        _run_demo_scenario(
            scenario,
            selected_profile,
            capital_config,
            broker_config,
            risk_config,
            session_config,
            news_config,
            volatility_config,
            spread_config,
            parsed_spread,
            parsed_session_time,
            show_trace,
            show_orderflow,
            orderflow_csv_result,
            orderflow_replay_result,
            show_orderflow_replay_steps,
            export_orderflow_report,
            orderflow_export_config,
        )
    else:
        _run_backtest_scenario(
            scenario,
            selected_profile,
            capital_config,
            broker_config,
            risk_config,
            session_config,
            news_config,
            volatility_config,
            spread_config,
            parsed_spread,
            parsed_session_time,
            show_trace,
            show_orderflow,
            orderflow_csv_result,
            orderflow_replay_result,
            show_orderflow_replay_steps,
            export_orderflow_report,
            orderflow_export_config,
        )


if __name__ == "__main__":
    main()
