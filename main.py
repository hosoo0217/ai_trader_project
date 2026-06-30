import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from ai.session_trend_coach import SessionTrendCoach, SessionTrendCoachConfig, SessionTrendCoachReview
from ai.strategy_improvement import (
    StrategyImprovementConfig,
    StrategyImprovementEngine,
    StrategyImprovementResult,
)
from ai.strategy_approval_pipeline import (
    StrategyApprovalPipeline,
    StrategyApprovalPipelineConfig,
    StrategyApprovalPipelineResult,
)
from ai.human_approval import HumanApprovalConfig, HumanApprovalResult, HumanApprovalWorkflow
from ai.change_proposal import ChangeProposal, ChangeProposalConfig, ChangeProposalResult, ChangeProposalEngine
from ai.change_proposal_review import (
    ChangeProposalReviewConfig,
    ChangeProposalReviewResult,
    ChangeProposalReviewWorkflow,
)
from ai.implementation_plan import (
    ImplementationPlanConfig,
    ImplementationPlanResult,
    ImplementationPlanWorkflow,
)
from ai.implementation_final_review import (
    ImplementationFinalReviewConfig,
    ImplementationFinalReviewResult,
    ImplementationFinalReviewWorkflow,
)
from ai.implementation_readiness import (
    ImplementationReadinessChecker,
    ImplementationReadinessChecklist,
    ImplementationReadinessConfig,
)
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
from storage.session_report import TradingSessionReport, TradingSessionReportGenerator
from storage.session_report_exporter import (
    SessionReportExportConfig,
    SessionReportExporter,
    SessionReportExportResult,
)
from storage.session_history import SessionHistoryConfig, SessionHistoryStore, SessionHistorySummary
from storage.session_trend import SessionTrendAnalyzer, SessionTrendConfig, SessionTrendResult
from storage.human_approval_log import HumanApprovalLogConfig, HumanApprovalLogResult, HumanApprovalLogStore
from storage.change_proposal_store import ChangeProposalStoreConfig, ChangeProposalStoreResult, ChangeProposalStore
from storage.change_proposal_review_log import (
    ChangeProposalReviewLogConfig,
    ChangeProposalReviewLogResult,
    ChangeProposalReviewLogStore,
)
from storage.implementation_plan_store import (
    ImplementationPlanStore,
    ImplementationPlanStoreConfig,
    ImplementationPlanStoreResult,
)
from storage.implementation_final_review_log import (
    ImplementationFinalReviewLogConfig,
    ImplementationFinalReviewLogResult,
    ImplementationFinalReviewLogStore,
)
from storage.trade_journal import TradeJournal


@dataclass
class OrderFlowCsvDemoResult:
    """Order Flow context plus CSV data-quality status for CLI output."""

    context: OrderFlowContextResult | None = None
    data_quality: OrderFlowDataQualityResult | None = None


@dataclass
class BacktestMarketCsvResult:
    """Optional market candles loaded from a research-only CSV file."""

    candles: pd.DataFrame | None = None
    source: str | None = None
    reason: str | None = None


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


def _first_matching_column(dataframe: pd.DataFrame, aliases: list[str]) -> str | None:
    """Find the first column matching aliases while tolerating duplicate headers."""
    normalized_aliases = {_normalize_market_column(alias) for alias in aliases}
    for column in dataframe.columns:
        if _normalize_market_column(column) in normalized_aliases:
            return str(column)
    return None


def _normalize_market_column(name: object) -> str:
    """Normalize CSV headers for market candle loading."""
    base_name = str(name).strip()
    if "." in base_name:
        prefix, suffix = base_name.rsplit(".", 1)
        if suffix.isdigit():
            base_name = prefix
    return base_name.lower().replace(" ", "").replace("_", "")


def _series_from_market_column(dataframe: pd.DataFrame, column: str) -> pd.Series:
    """Read a DataFrame column safely when duplicate headers are present."""
    values = dataframe[column]
    if isinstance(values, pd.DataFrame):
        return values.iloc[:, 0]
    return values


def _candles_from_footprint_candles(candles: list[object]) -> pd.DataFrame:
    """Convert imported Sierra candles into the market OHLC DataFrame shape."""
    rows: list[dict[str, object]] = []
    for candle in candles:
        rows.append(
            {
                "time": getattr(candle, "time", None),
                "open": getattr(candle, "open", None),
                "high": getattr(candle, "high", None),
                "low": getattr(candle, "low", None),
                "close": getattr(candle, "close", None),
                "volume": getattr(candle, "reported_volume", None),
            }
        )
    return pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])


def _is_sierra_bar_summary_market_dataframe(dataframe: pd.DataFrame) -> bool:
    """Detect Sierra BAR_SUMMARY market rows by the first price columns."""
    if dataframe is None or not isinstance(dataframe, pd.DataFrame) or len(dataframe.columns) < 6:
        return False
    first_columns = [_normalize_market_column(column) for column in list(dataframe.columns[:6])]
    return (
        first_columns[0] == "date"
        and first_columns[1] == "time"
        and first_columns[2] == "open"
        and first_columns[3] == "high"
        and first_columns[4] == "low"
        and first_columns[5] in {"last", "close"}
    )


def _market_candles_from_sierra_bar_summary_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Read Sierra BAR_SUMMARY price OHLC from fixed first-column positions."""
    market_candles = pd.DataFrame()
    market_candles["time"] = [
        f"{str(date).strip()} {str(time).strip()}".strip()
        for date, time in zip(dataframe.iloc[:, 0], dataframe.iloc[:, 1])
    ]
    market_candles["open"] = pd.to_numeric(dataframe.iloc[:, 2], errors="coerce")
    market_candles["high"] = pd.to_numeric(dataframe.iloc[:, 3], errors="coerce")
    market_candles["low"] = pd.to_numeric(dataframe.iloc[:, 4], errors="coerce")
    market_candles["close"] = pd.to_numeric(dataframe.iloc[:, 5], errors="coerce")
    if len(dataframe.columns) > 6:
        market_candles["volume"] = pd.to_numeric(dataframe.iloc[:, 6], errors="coerce")
    return market_candles.dropna(subset=["time", "open", "high", "low", "close"]).reset_index(drop=True)


def _load_backtest_market_candles_from_csv(raw_path: str) -> BacktestMarketCsvResult:
    """Load optional research-only market candles from OHLC or Sierra CSV files."""
    cleaned = (raw_path or "").strip()
    if not cleaned:
        return BacktestMarketCsvResult()

    csv_path = _resolve_orderflow_csv_path(cleaned)
    if not csv_path.exists() or not csv_path.is_file():
        return BacktestMarketCsvResult(reason=f"Backtest market CSV not found: {cleaned}")

    try:
        dataframe = pd.read_csv(csv_path)
    except Exception:
        return BacktestMarketCsvResult(reason=f"Backtest market CSV could not be read: {cleaned}")

    if dataframe.empty:
        return BacktestMarketCsvResult(reason=f"Backtest market CSV is empty: {cleaned}")

    if _is_sierra_bar_summary_market_dataframe(dataframe):
        market_candles = _market_candles_from_sierra_bar_summary_dataframe(dataframe)
        if market_candles.empty:
            return BacktestMarketCsvResult(reason=f"Backtest market CSV had no usable candles: {cleaned}")
        return BacktestMarketCsvResult(
            candles=market_candles,
            source=f"{csv_path.name} (BAR_SUMMARY positional OHLC)",
            reason=f"Loaded backtest market CSV from Sierra BAR_SUMMARY price columns: {csv_path.name}",
        )

    importer = SierraChartImporter()
    footprint_candles = importer.load_csv(str(csv_path), SierraChartImportConfig())
    if footprint_candles:
        market_candles = _candles_from_footprint_candles(footprint_candles)
        return BacktestMarketCsvResult(
            candles=market_candles,
            source=f"{csv_path.name} ({getattr(footprint_candles[0], 'source_format', 'PRICE_LEVEL_FOOTPRINT')})",
            reason=f"Loaded backtest market CSV from Sierra import: {csv_path.name}",
        )

    column_map = {
        "time": _first_matching_column(dataframe, ["time", "datetime", "timestamp", "Date Time", "DateTime"]),
        "date": _first_matching_column(dataframe, ["date", "Date"]),
        "open": _first_matching_column(dataframe, ["open", "Open"]),
        "high": _first_matching_column(dataframe, ["high", "High"]),
        "low": _first_matching_column(dataframe, ["low", "Low"]),
        "close": _first_matching_column(dataframe, ["close", "Close", "last", "Last"]),
        "volume": _first_matching_column(dataframe, ["volume", "Volume"]),
    }
    has_time = column_map["time"] is not None or (column_map["date"] is not None and column_map["time"] is not None)
    required = ["open", "high", "low", "close"]
    if not has_time or any(column_map[field] is None for field in required):
        return BacktestMarketCsvResult(reason=f"Backtest market CSV missing required OHLC columns: {cleaned}")

    market_candles = pd.DataFrame()
    if column_map["date"] and column_map["time"] and column_map["date"] != column_map["time"]:
        dates = _series_from_market_column(dataframe, column_map["date"])
        times = _series_from_market_column(dataframe, column_map["time"])
        market_candles["time"] = [
            f"{str(date).strip()} {str(time).strip()}".strip()
            for date, time in zip(dates, times)
        ]
    else:
        market_candles["time"] = _series_from_market_column(dataframe, str(column_map["time"]))

    for field in required:
        market_candles[field] = pd.to_numeric(
            _series_from_market_column(dataframe, str(column_map[field])),
            errors="coerce",
        )
    if column_map["volume"] is not None:
        market_candles["volume"] = pd.to_numeric(
            _series_from_market_column(dataframe, column_map["volume"]),
            errors="coerce",
        )

    market_candles = market_candles.dropna(subset=["time", "open", "high", "low", "close"])
    if market_candles.empty:
        return BacktestMarketCsvResult(reason=f"Backtest market CSV had no usable candles: {cleaned}")

    return BacktestMarketCsvResult(
        candles=market_candles.reset_index(drop=True),
        source=csv_path.name,
        reason=f"Loaded backtest market CSV: {csv_path.name}",
    )


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
        "--backtest-max-iterations",
        type=_positive_int,
        default=None,
        help="Optional maximum number of rolling backtest iterations to run",
    )
    parser.add_argument(
        "--backtest-market-csv",
        default="",
        help="Optional OHLC CSV path to use as market candles for research-only backtests",
    )
    parser.add_argument(
        "--export-backtest-trade-traces",
        action="store_true",
        help="Export research-only executed backtest trade trace reports",
    )
    parser.add_argument(
        "--backtest-trace-dir",
        default="reports",
        help="Output folder for exported backtest trade trace reports",
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
    parser.add_argument(
        "--show-session-report",
        action="store_true",
        help="Show the full trading session report for demo/backtest output",
    )
    parser.add_argument(
        "--export-session-report",
        action="store_true",
        help="Export the full trading session report txt/json files",
    )
    parser.add_argument(
        "--session-report-dir",
        default="reports",
        help="Output folder for exported full trading session reports",
    )
    parser.add_argument(
        "--save-session-history",
        action="store_true",
        help="Save the full trading session report into session history",
    )
    parser.add_argument(
        "--show-session-history-summary",
        action="store_true",
        help="Show a summary of saved full trading session reports",
    )
    parser.add_argument(
        "--session-history-dir",
        default="reports",
        help="Output folder for session_history.json",
    )
    parser.add_argument(
        "--show-session-trend",
        action="store_true",
        help="Show performance trend analysis from saved session history",
    )
    parser.add_argument(
        "--approval-decision",
        default="",
        help="Record a human approval decision for a generated request: APPROVE, REJECT, or NEEDS_REVIEW",
    )
    parser.add_argument(
        "--approval-request-index",
        type=int,
        default=0,
        help="Zero-based Human Approval Request index to decide",
    )
    parser.add_argument(
        "--approval-decided-by",
        default="",
        help="Optional reviewer name for the approval decision log",
    )
    parser.add_argument(
        "--approval-notes",
        default="",
        help="Optional notes for the approval decision log",
    )
    parser.add_argument(
        "--approval-log-dir",
        default="reports",
        help="Output folder for human_approval_log.json",
    )
    parser.add_argument(
        "--proposal-dir",
        default="reports",
        help="Output folder for change_proposals.json",
    )
    parser.add_argument(
        "--register-change-proposal-doc",
        default="",
        help="Register a documentation-based proposal into change_proposals.json",
    )
    parser.add_argument(
        "--proposal-category",
        default="STRATEGY",
        help="Category for --register-change-proposal-doc records",
    )
    parser.add_argument(
        "--proposal-priority",
        default="MEDIUM",
        help="Priority for --register-change-proposal-doc records",
    )
    parser.add_argument(
        "--proposal-title",
        default="",
        help="Title for --register-change-proposal-doc records",
    )
    parser.add_argument(
        "--review-change-proposal",
        default="",
        help="Review a saved change proposal: ACCEPT, REJECT, NEEDS_MORE_DATA, or NEEDS_BACKTEST",
    )
    parser.add_argument(
        "--change-proposal-index",
        type=int,
        default=0,
        help="Zero-based saved Change Proposal index to review",
    )
    parser.add_argument(
        "--proposal-reviewed-by",
        default="",
        help="Optional reviewer name for the change proposal review log",
    )
    parser.add_argument(
        "--proposal-review-notes",
        default="",
        help="Optional notes for the change proposal review log",
    )
    parser.add_argument(
        "--proposal-review-log-dir",
        default="reports",
        help="Output folder for change_proposal_reviews.json",
    )
    parser.add_argument(
        "--implementation-plan-dir",
        default="reports",
        help="Output folder for implementation_plans.json",
    )
    parser.add_argument(
        "--final-review-implementation-plan",
        default="",
        help="Final-review a saved implementation plan: APPROVE_FOR_WORK, REJECT, NEEDS_BACKTEST, or NEEDS_MORE_REVIEW",
    )
    parser.add_argument(
        "--implementation-plan-index",
        type=int,
        default=0,
        help="Zero-based saved Implementation Plan index to final-review",
    )
    parser.add_argument(
        "--implementation-reviewed-by",
        default="",
        help="Optional reviewer name for the implementation final review log",
    )
    parser.add_argument(
        "--implementation-review-notes",
        default="",
        help="Optional notes for the implementation final review log",
    )
    parser.add_argument(
        "--implementation-final-review-log-dir",
        default="reports",
        help="Output folder for implementation_final_reviews.json",
    )
    parser.add_argument(
        "--check-implementation-readiness",
        action="store_true",
        help="Check whether a saved Implementation Plan is ready for future human-reviewed work",
    )
    return parser


def _positive_int(raw_value: str) -> int:
    """Parse a CLI integer that must be at least one."""
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("must be an integer greater than or equal to 1") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("must be greater than or equal to 1")
    return value


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


def _export_backtest_trade_traces(
    output_dir: str,
    scenario: str,
    profile: TradingProfile,
    result,
    performance,
    quality,
) -> tuple[Path, Path]:
    """Export research-only backtest trade diagnostics as JSON and TXT."""
    destination = Path(output_dir or "reports")
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "backtest_trade_traces.json"
    txt_path = destination / "backtest_trade_traces.txt"

    all_iterations = list(getattr(result, "iteration_traces", []))
    executed_iterations = [item for item in all_iterations if item.trade_executed]
    blocked_iterations = [item for item in all_iterations if not item.trade_executed]

    blocking_counter: Counter[str] = Counter()
    for item in blocked_iterations:
        for reason in item.blocking_reasons:
            blocking_counter[str(reason)] += 1

    summary = {
        "scenario": scenario,
        "profile": profile.profile_name,
        "research_only": True,
        "safety": {
            "live_trading": False,
            "broker_connection": False,
            "mt5_login": False,
            "sierra_chart_live_connection": False,
            "cme_live_data_connection": False,
            "external_apis": False,
        },
        "total_iterations": result.total_iterations,
        "executed_trades": result.trades_executed,
        "blocked_trades": result.trades_blocked,
        "final_balance": result.final_balance,
        "total_pnl": result.total_pnl,
        "win_rate": performance.win_rate,
        "max_drawdown": performance.max_drawdown,
        "profit_factor": "INF" if performance.profit_factor == float("inf") else performance.profit_factor,
        "backtest_quality_grade": quality.grade,
        "backtest_quality_passed": quality.passed,
        "backtest_quality_failures": list(quality.failures),
        "backtest_quality_warnings": list(quality.warnings),
        "common_blocking_reasons": [
            {"reason": reason, "count": count} for reason, count in blocking_counter.most_common()
        ],
    }

    payload = {
        "summary": summary,
        "executed_trade_iterations": [asdict(item) for item in executed_iterations],
        "blocked_trade_summary": {
            "count": len(blocked_iterations),
            "common_blocking_reasons": summary["common_blocking_reasons"],
        },
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "Backtest Trade Trace Diagnostic Report",
        "",
        "Safety",
        "- Research-only diagnostic export",
        "- No live trading",
        "- No broker connection",
        "- No MT5 login",
        "- No Sierra Chart live connection",
        "- No CME live data connection",
        "- No external APIs",
        "",
        "Summary",
        f"- Scenario: {scenario}",
        f"- Profile: {profile.profile_name}",
        f"- Total iterations: {result.total_iterations}",
        f"- Executed trades: {result.trades_executed}",
        f"- Blocked trades: {result.trades_blocked}",
        f"- Final balance: {result.final_balance:.2f}",
        f"- Total PnL: {result.total_pnl:.2f}",
        f"- Win rate: {performance.win_rate:.2f}%",
        f"- Max drawdown: {performance.max_drawdown:.2f}",
        f"- Backtest quality grade: {quality.grade}",
        "",
        "Common Blocking Reasons",
    ]
    if blocking_counter:
        for reason, count in blocking_counter.most_common():
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("- None")

    lines.extend(["", "Executed Trade Iterations"])
    if not executed_iterations:
        lines.append("- None")
    else:
        for item in executed_iterations:
            lines.extend(
                [
                    "",
                    f"Iteration {item.iteration_index}",
                    f"- Final action: {item.final_action}",
                    f"- Final allowed: {item.final_allowed}",
                    f"- Status: {item.status}",
                    f"- Simulated PnL: {item.simulated_pnl if item.simulated_pnl is not None else 'N/A'}",
                    f"- Outcome: {item.outcome or 'N/A'}",
                    f"- Decision reasons: {'; '.join(item.reasons) if item.reasons else 'None'}",
                    f"- Blocking reasons: {'; '.join(item.blocking_reasons) if item.blocking_reasons else 'None'}",
                    (
                        f"- Decision engine: {item.decision_engine_status or 'N/A'} | "
                        f"{'; '.join(item.decision_engine_reasons) if item.decision_engine_reasons else 'None'}"
                    ),
                    f"- SMC: {item.smc_status or 'N/A'} | {'; '.join(item.smc_reasons) if item.smc_reasons else 'None'}",
                    f"- CRT: {item.crt_status or 'N/A'} | {'; '.join(item.crt_reasons) if item.crt_reasons else 'None'}",
                    (
                        f"- Multi-timeframe: {item.multi_timeframe_status or 'N/A'} | "
                        f"{'; '.join(item.multi_timeframe_reasons) if item.multi_timeframe_reasons else 'None'}"
                    ),
                    (
                        f"- Order Flow: {item.orderflow_status or 'N/A'} | "
                        f"{'; '.join(item.orderflow_reasons) if item.orderflow_reasons else 'None'}"
                    ),
                    f"- Safety gate: {item.safety_status or 'N/A'} | {'; '.join(item.safety_reasons) if item.safety_reasons else 'None'}",
                    f"- Risk engine: {item.risk_status or 'N/A'} | {'; '.join(item.risk_reasons) if item.risk_reasons else 'None'}",
                    (
                        f"- Trade manager: {item.trade_manager_status or 'N/A'} | "
                        f"{'; '.join(item.trade_manager_reasons) if item.trade_manager_reasons else 'None'}"
                    ),
                    (
                        f"- Exit simulator: {item.exit_simulator_status or 'N/A'} | "
                        f"{'; '.join(item.exit_simulator_reasons) if item.exit_simulator_reasons else 'None'}"
                    ),
                ]
            )

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def _print_full_trading_session_report(report: TradingSessionReport) -> None:
    """Print one beginner-readable full session report."""
    blocked_text = "; ".join(report.blocked_reasons) if report.blocked_reasons else "None"
    reasons_text = "; ".join(report.reasons) if report.reasons else "None"
    warnings_text = "; ".join(report.warnings) if report.warnings else "None"
    journal_text = report.journal_summary if report.journal_summary else "None"
    performance_text = report.performance_summary if report.performance_summary else "None"

    print("\nFull Trading Session Report")
    print(f"- Session ID: {report.session_id}")
    print(f"- Mode: {report.mode}")
    print(f"- Scenario: {report.scenario or 'N/A'}")
    print(f"- Profile: {report.profile or 'N/A'}")
    print(f"- Final action: {report.final_action}")
    print(f"- Trade executed: {report.trade_executed}")
    print(f"- Market bias: {report.market_bias or 'UNKNOWN'}")
    print(f"- SMC bias: {report.smc_bias or 'N/A'}")
    print(f"- CRT bias: {report.crt_bias or 'N/A'}")
    print(f"- Order Flow bias: {report.orderflow_bias or 'N/A'}")
    print(f"- Safety status: {report.safety_status or 'N/A'}")
    print(f"- Safety passed: {report.safety_passed}")
    print(f"- Blocked reasons: {blocked_text}")
    print(f"- Journal summary: {journal_text}")
    print(f"- Performance summary: {performance_text}")
    print(f"- AI Coach summary: {report.ai_coach_summary or 'N/A'}")
    print(f"- Decision trace ID: {report.decision_trace_id or 'N/A'}")
    print(f"- Reasons: {reasons_text}")
    print(f"- Warnings: {warnings_text}")


def _print_session_report_export(result: SessionReportExportResult) -> None:
    """Print full session report export status without crashing the run."""
    reasons_text = "; ".join(result.reasons) if result.reasons else "None"
    blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

    print("\nFull Trading Session Report Export")
    print(f"- Exported: {result.exported}")
    print(f"- Text path: {result.text_path or 'N/A'}")
    print(f"- JSON path: {result.json_path or 'N/A'}")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocks_text}")


def _print_session_history_status(
    saved: bool,
    history_config: SessionHistoryConfig,
    summary: SessionHistorySummary | None,
    reasons: list[str] | None = None,
    warnings: list[str] | None = None,
) -> None:
    """Print session history save/summary details."""
    history_path = Path(history_config.output_dir) / history_config.history_filename
    reasons_text = "; ".join(reasons or []) if reasons else "None"
    warnings_text = "; ".join(warnings or []) if warnings else "None"
    common_blocks = (
        "; ".join(f"{reason}={count}" for reason, count in summary.common_blocking_reasons.items())
        if summary is not None and summary.common_blocking_reasons
        else "None"
    )

    print("\nBacktest Session History")
    print(f"- Saved: {saved}")
    print(f"- History path: {history_path}")
    if summary is not None:
        print(f"- Total sessions: {summary.total_sessions}")
        print(f"- Executed sessions: {summary.executed_sessions}")
        print(f"- Blocked sessions: {summary.blocked_sessions}")
        print(f"- Common blocking reasons: {common_blocks}")
        if summary.reasons:
            reasons_text = "; ".join(summary.reasons)
        if summary.warnings:
            warnings_text = "; ".join(summary.warnings)
    print(f"- Reasons: {reasons_text}")
    print(f"- Warnings: {warnings_text}")


def _print_session_history_trend(result: SessionTrendResult) -> None:
    """Print session-history trend analysis in beginner-readable form."""
    blocking_counts = (
        "; ".join(f"{reason}={count}" for reason, count in result.blocking_reason_counts.items())
        if result.blocking_reason_counts
        else "None"
    )
    reasons_text = "; ".join(result.reasons) if result.reasons else "None"
    warnings_text = "; ".join(result.warnings) if result.warnings else "None"

    print("\nSession History Trend")
    print(f"- Total sessions: {result.total_sessions}")
    print(f"- Executed sessions: {result.executed_sessions}")
    print(f"- Blocked sessions: {result.blocked_sessions}")
    print(f"- Execution rate: {result.execution_rate:.1f}%")
    print(f"- Block rate: {result.block_rate:.1f}%")
    print(f"- Bullish sessions: {result.bullish_sessions}")
    print(f"- Bearish sessions: {result.bearish_sessions}")
    print(f"- Neutral sessions: {result.neutral_sessions}")
    print(f"- Unknown sessions: {result.unknown_sessions}")
    print(f"- Most common blocking reason: {result.most_common_blocking_reason or 'None'}")
    print(f"- Blocking reason counts: {blocking_counts}")
    print(f"- Trend status: {result.trend_status}")
    print(f"- Reasons: {reasons_text}")
    print(f"- Warnings: {warnings_text}")


def _print_session_trend_coach_review(review: SessionTrendCoachReview) -> None:
    """Print beginner-friendly coach feedback for session history trend."""
    strengths_text = "; ".join(review.strengths) if review.strengths else "None"
    risks_text = "; ".join(review.risks) if review.risks else "None"
    lessons_text = "; ".join(review.lessons) if review.lessons else "None"
    next_steps_text = "; ".join(review.next_steps) if review.next_steps else "None"
    warnings_text = "; ".join(review.warnings) if review.warnings else "None"
    reasons_text = "; ".join(review.reasons) if review.reasons else "None"

    print("\nAI Coach Session Trend Review")
    print(f"- Status: {review.status}")
    print(f"- Grade: {review.grade}")
    print(f"- Summary: {review.summary}")
    print(f"- Trend read: {review.trend_read}")
    print(f"- Strengths: {strengths_text}")
    print(f"- Risks: {risks_text}")
    print(f"- Lessons: {lessons_text}")
    print(f"- Next steps: {next_steps_text}")
    print(f"- Warnings: {warnings_text}")
    print(f"- Reasons: {reasons_text}")


def _print_strategy_improvement_suggestions(result: StrategyImprovementResult) -> None:
    """Print safe strategy improvement suggestions in beginner-readable form."""
    warnings_text = "; ".join(result.warnings) if result.warnings else "None"
    reasons_text = "; ".join(result.reasons) if result.reasons else "None"

    print("\nStrategy Improvement Suggestions")
    print(f"- Status: {result.status}")
    print(f"- Summary: {result.summary}")
    print("- Suggestions:")
    if result.suggestions:
        for suggestion in result.suggestions:
            approval = "Yes" if suggestion.human_approval_required else "No"
            print(f"  - Category: {suggestion.category}")
            print(f"    Priority: {suggestion.priority}")
            print(f"    Suggestion: {suggestion.suggestion}")
            print(f"    Reason: {suggestion.reason}")
            print(f"    Risk: {suggestion.risk}")
            print(f"    Human approval required: {approval}")
    else:
        print("  - None")
    print(f"- Warnings: {warnings_text}")
    print(f"- Reasons: {reasons_text}")


def _print_human_approval_requests(result: StrategyApprovalPipelineResult) -> None:
    """Print pending human approval requests without applying any change."""
    reasons_text = "; ".join(result.reasons) if result.reasons else "None"
    blocking_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"

    print("\nHuman Approval Requests")
    print(f"- Status: {result.status}")
    print(f"- Total suggestions: {result.total_suggestions}")
    print(f"- Pending requests: {result.pending_requests}")
    print("- Created requests:")
    if result.created_requests:
        for request in result.created_requests:
            approval = "Yes" if request.human_approval_required else "No"
            print(f"  - Request ID: {request.request_id}")
            print(f"    Suggestion category: {request.suggestion_category}")
            print(f"    Suggestion priority: {request.suggestion_priority}")
            print(f"    Suggestion text: {request.suggestion_text}")
            print(f"    Reason: {request.reason}")
            print(f"    Risk: {request.risk}")
            print(f"    Status: {request.status}")
            print(f"    Human approval required: {approval}")
            print("    Note: No strategy rule was changed. Review before applying any future change.")
    else:
        print("  - None")

    print("- Skipped suggestions:")
    if result.skipped_suggestions:
        for suggestion in result.skipped_suggestions:
            print(f"  - Category: {getattr(suggestion, 'category', 'UNKNOWN')}")
            print(f"    Priority: {getattr(suggestion, 'priority', 'UNKNOWN')}")
            print(f"    Suggestion: {getattr(suggestion, 'suggestion', 'UNKNOWN')}")
    else:
        print("  - None")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _print_human_approval_decision(
    request: object | None,
    decision_result: HumanApprovalResult | None,
    log_result: HumanApprovalLogResult | None,
    message: str | None = None,
) -> None:
    """Print one human approval decision log result safely."""
    print("\nHuman Approval Decision")
    if message:
        print(f"- Message: {message}")

    decision = decision_result.decision if decision_result is not None else None
    request_id = getattr(request, "request_id", None) or getattr(decision, "request_id", None) or "N/A"
    decision_text = getattr(decision, "decision", None) or "UNKNOWN"
    decided_by = getattr(decision, "decided_by", None) or "N/A"
    notes = getattr(decision, "notes", None) or "None"
    reasons = decision_result.reasons if decision_result is not None else []
    blocking_reasons = decision_result.blocking_reasons if decision_result is not None else []
    if log_result is not None and log_result.blocking_reasons:
        blocking_reasons = list(blocking_reasons) + list(log_result.blocking_reasons)

    reasons_text = "; ".join(reasons) if reasons else "None"
    blocking_text = "; ".join(blocking_reasons) if blocking_reasons else "None"
    print(f"- Request ID: {request_id}")
    print(f"- Decision: {decision_text}")
    print(f"- Approved: {decision_result.approved if decision_result is not None else False}")
    print(f"- Allowed to apply: {decision_result.allowed_to_apply if decision_result is not None else False}")
    print(f"- Decided by: {decided_by}")
    print(f"- Notes: {notes}")
    print(f"- Log saved: {log_result.saved if log_result is not None else False}")
    print(f"- Log path: {log_result.log_path if log_result is not None else 'None'}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- Approval is only recorded for future human-reviewed work.")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _print_approved_change_proposal(
    proposal_result: ChangeProposalResult | None,
    store_result: ChangeProposalStoreResult | None,
    message: str | None = None,
) -> None:
    """Print approved change proposal output without applying changes."""
    print("\nApproved Change Proposal")
    if message:
        print(f"- Message: {message}")

    proposal = proposal_result.proposal if proposal_result is not None else None
    reasons = proposal_result.reasons if proposal_result is not None else []
    blocking_reasons = proposal_result.blocking_reasons if proposal_result is not None else []
    if store_result is not None and store_result.blocking_reasons:
        blocking_reasons = list(blocking_reasons) + list(store_result.blocking_reasons)

    reasons_text = "; ".join(reasons) if reasons else "None"
    blocking_text = "; ".join(blocking_reasons) if blocking_reasons else "None"
    print(f"- Created: {proposal_result.created if proposal_result is not None else False}")
    print(f"- Proposal ID: {proposal.proposal_id if proposal is not None else 'N/A'}")
    print(f"- Source request ID: {proposal.source_request_id if proposal is not None else 'N/A'}")
    print(f"- Category: {proposal.category if proposal is not None else 'N/A'}")
    print(f"- Priority: {proposal.priority if proposal is not None else 'N/A'}")
    print(f"- Title: {proposal.title if proposal is not None else 'N/A'}")
    print(f"- Description: {proposal.description if proposal is not None else 'N/A'}")
    print(f"- Reason: {proposal.reason if proposal is not None else 'N/A'}")
    print(f"- Risk: {proposal.risk if proposal is not None else 'N/A'}")
    print(f"- Proposed change: {proposal.proposed_change if proposal is not None else 'N/A'}")
    print(f"- Status: {proposal.status if proposal is not None else (proposal_result.status if proposal_result else 'UNKNOWN')}")
    print(f"- Human review required: {proposal.human_review_required if proposal is not None else True}")
    print(f"- Auto implementation allowed: {proposal.auto_implementation_allowed if proposal is not None else False}")
    print(f"- Saved: {store_result.saved if store_result is not None else False}")
    print(f"- Proposals path: {store_result.proposals_path if store_result is not None else 'None'}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- Proposal is saved for future human review only.")
    print("- Final human review is still required.")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _approval_record_from_decision(
    request: object | None,
    decision_result: HumanApprovalResult,
    log_result: HumanApprovalLogResult | None,
    log_config: HumanApprovalLogConfig,
) -> dict | None:
    """Use the saved approval log record when available."""
    if log_result is not None and log_result.saved:
        records = HumanApprovalLogStore().load_log(log_config)
        if records:
            return records[-1]

    decision = decision_result.decision
    return {
        "request_id": getattr(request, "request_id", None),
        "suggestion_category": getattr(request, "suggestion_category", "UNKNOWN"),
        "suggestion_priority": getattr(request, "suggestion_priority", "UNKNOWN"),
        "suggestion_text": getattr(request, "suggestion_text", "UNKNOWN"),
        "request_status": getattr(request, "status", decision_result.status),
        "decision": getattr(decision, "decision", "UNKNOWN") if decision is not None else "UNKNOWN",
        "approved": decision_result.approved,
        "allowed_to_apply": decision_result.allowed_to_apply,
        "reasons": list(decision_result.reasons),
        "blocking_reasons": list(decision_result.blocking_reasons),
    }


def _create_and_store_change_proposal(
    request: object | None,
    decision_result: HumanApprovalResult,
    log_result: HumanApprovalLogResult | None,
    log_config: HumanApprovalLogConfig,
    proposal_config: ChangeProposalStoreConfig,
) -> None:
    """Create a future proposal only for approved decisions."""
    if not decision_result.approved:
        proposal_result = ChangeProposalResult(
            proposal=None,
            created=False,
            status="NO_APPROVED_DECISION",
            reasons=["No change proposal created because decision was not approved"],
            blocking_reasons=[],
        )
        _print_approved_change_proposal(
            proposal_result,
            None,
            message="No change proposal created because decision was not approved",
        )
        return

    approval_record = _approval_record_from_decision(request, decision_result, log_result, log_config)
    try:
        proposal_result = ChangeProposalEngine().create_from_approval_record(
            approval_record,
            ChangeProposalConfig(),
        )
    except Exception as exc:
        proposal_result = ChangeProposalResult(
            proposal=None,
            created=False,
            status="UNKNOWN",
            reasons=["Approved change proposal could not be created"],
            blocking_reasons=[f"Change proposal engine failed: {exc}"],
        )

    store_result = None
    if proposal_result.proposal is not None:
        try:
            store_result = ChangeProposalStore().append_proposal(proposal_result.proposal, proposal_config)
        except Exception as exc:
            store_result = ChangeProposalStoreResult(
                saved=False,
                proposals_path=None,
                total_proposals=0,
                reasons=["Change proposal store was requested"],
                blocking_reasons=[f"Change proposal could not be saved: {exc}"],
            )

    _print_approved_change_proposal(proposal_result, store_result)


def _register_change_proposal_doc(
    doc_path_text: str,
    category: str,
    priority: str,
    title: str,
    proposal_config: ChangeProposalStoreConfig,
) -> None:
    """Register a markdown proposal document without approving or implementing it."""
    print("\nDocumentation Change Proposal Registration")

    doc_path = Path(doc_path_text)
    normalized_doc_path = doc_path.as_posix()
    safe_category = (category or "STRATEGY").strip() or "STRATEGY"
    safe_priority = (priority or "MEDIUM").strip() or "MEDIUM"
    safe_title = (title or doc_path.stem.replace("_", " ").replace("-", " ").title()).strip()
    store = ChangeProposalStore()

    try:
        document_text = doc_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"- Registered: False")
        print(f"- Status: BLOCKED")
        print(f"- Document path: {normalized_doc_path}")
        print(f"- Blocking reasons: Could not read proposal document: {exc}")
        print("- No strategy rule was changed.")
        print("- No implementation plan was created.")
        return

    existing = store.load_proposals(proposal_config)
    normalized_title = safe_title.casefold()
    normalized_path = normalized_doc_path.casefold()
    for record in existing:
        existing_title = str(record.get("title", "")).casefold()
        existing_path = str(record.get("doc_path", "")).casefold()
        if existing_title == normalized_title or (existing_path and existing_path == normalized_path):
            print("- Registered: False")
            print("- Status: DUPLICATE")
            print(f"- Existing proposal ID: {record.get('proposal_id', 'UNKNOWN')}")
            print(f"- Document path: {normalized_doc_path}")
            print(f"- Proposals path: {Path(proposal_config.output_dir) / proposal_config.proposals_filename}")
            print("- Duplicate title or document path already registered.")
            print("- Registration is not approval.")
            print("- No strategy rule was changed.")
            print("- No implementation plan was created.")
            return

    description = _proposal_doc_description(document_text, normalized_doc_path)
    proposal = ChangeProposal(
        proposal_id=f"proposal-doc-{uuid4().hex[:8]}",
        source_request_id=None,
        category=safe_category,
        priority=safe_priority,
        title=safe_title,
        description=description,
        reason="Documentation-based proposal registration only",
        risk="Backtesting and human review are required before implementation.",
        proposed_change=(
            "Research whether this documentation proposal should become a strategy change. "
            "Do not implement code, execution rules, or risk changes until review and backtest evidence are complete."
        ),
        status="PROPOSED",
        human_review_required=True,
        auto_implementation_allowed=False,
        implementation_allowed=False,
        doc_path=normalized_doc_path,
        reasons=[
            "Documentation-based proposal registration only",
            "No strategy rules changed",
            "Backtesting required before implementation",
            "Human review required",
        ],
        blocking_reasons=[
            "Backtesting is required before implementation",
        ],
    )
    store_result = store.append_proposal(proposal, proposal_config)

    print(f"- Registered: {store_result.saved}")
    print(f"- Proposal ID: {proposal.proposal_id}")
    print(f"- Title: {proposal.title}")
    print(f"- Category: {proposal.category}")
    print(f"- Priority: {proposal.priority}")
    print(f"- Status: {proposal.status}")
    print(f"- Human review required: {proposal.human_review_required}")
    print(f"- Auto implementation allowed: {proposal.auto_implementation_allowed}")
    print(f"- Implementation allowed: {proposal.implementation_allowed}")
    print(f"- Document path: {proposal.doc_path}")
    print(f"- Proposals path: {store_result.proposals_path if store_result.proposals_path else 'None'}")
    print("- Registration is not approval.")
    print("- Registration is not implementation.")
    print("- NEEDS_BACKTEST review is required before any strategy code change.")
    print("- No strategy rule was changed.")
    print("- No implementation plan was created.")


def _proposal_doc_description(document_text: str, doc_path: str) -> str:
    """Create a compact description from the markdown proposal text."""
    for raw_line in document_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        return line[:500]
    return f"Documentation-based change proposal from {doc_path}"


def _print_change_proposal_review(
    proposal: object | None,
    review_result: ChangeProposalReviewResult | None,
    log_result: ChangeProposalReviewLogResult | None,
    message: str | None = None,
) -> None:
    """Print one proposal review decision without implementing changes."""
    print("\nChange Proposal Review")
    if message:
        print(f"- Message: {message}")

    decision = review_result.decision if review_result is not None else None
    proposal_id = (
        getattr(proposal, "proposal_id", None)
        if proposal is not None and not isinstance(proposal, dict)
        else (proposal or {}).get("proposal_id") if isinstance(proposal, dict) else None
    )
    proposal_id = proposal_id or (review_result.proposal_id if review_result is not None else None) or "N/A"
    decision_text = getattr(decision, "decision", None) or "UNKNOWN"
    reviewed_by = getattr(decision, "reviewed_by", None) or "N/A"
    notes = getattr(decision, "notes", None) or "None"
    reasons = review_result.reasons if review_result is not None else []
    blocking_reasons = review_result.blocking_reasons if review_result is not None else []
    if log_result is not None and log_result.blocking_reasons:
        blocking_reasons = list(blocking_reasons) + list(log_result.blocking_reasons)

    reasons_text = "; ".join(reasons) if reasons else "None"
    blocking_text = "; ".join(blocking_reasons) if blocking_reasons else "None"
    print(f"- Proposal ID: {proposal_id}")
    print(f"- Decision: {decision_text}")
    print(f"- Status: {review_result.status if review_result is not None else 'UNKNOWN'}")
    print(f"- Accepted: {review_result.accepted if review_result is not None else False}")
    print(f"- Implementation allowed: {review_result.implementation_allowed if review_result is not None else False}")
    print(f"- Reviewed by: {reviewed_by}")
    print(f"- Notes: {notes}")
    print(f"- Log saved: {log_result.saved if log_result is not None else False}")
    print(f"- Log path: {log_result.log_path if log_result is not None else 'None'}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- Review decision is recorded for future human-reviewed work only.")
    print("- ACCEPT does not mean automatic implementation.")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _print_implementation_plan(
    plan_result: ImplementationPlanResult | None,
    store_result: ImplementationPlanStoreResult | None,
    message: str | None = None,
) -> None:
    """Print implementation plan output without applying implementation."""
    print("\nImplementation Plan")
    if message:
        print(f"- Message: {message}")

    plan = plan_result.plan if plan_result is not None else None
    reasons = plan_result.reasons if plan_result is not None else []
    blocking_reasons = plan_result.blocking_reasons if plan_result is not None else []
    if store_result is not None and store_result.blocking_reasons:
        blocking_reasons = list(blocking_reasons) + list(store_result.blocking_reasons)

    reasons_text = "; ".join(reasons) if reasons else "None"
    blocking_text = "; ".join(blocking_reasons) if blocking_reasons else "None"
    proposed_steps = "; ".join(plan.proposed_steps) if plan is not None and plan.proposed_steps else "None"
    required_tests = "; ".join(plan.required_tests) if plan is not None and plan.required_tests else "None"
    risk_checks = "; ".join(plan.risk_checks) if plan is not None and plan.risk_checks else "None"

    print(f"- Created: {plan_result.created if plan_result is not None else False}")
    print(f"- Plan ID: {plan.plan_id if plan is not None else 'N/A'}")
    print(f"- Source proposal ID: {plan.source_proposal_id if plan is not None else 'N/A'}")
    print(f"- Title: {plan.title if plan is not None else 'N/A'}")
    print(f"- Category: {plan.category if plan is not None else 'N/A'}")
    print(f"- Priority: {plan.priority if plan is not None else 'N/A'}")
    print(f"- Objective: {plan.objective if plan is not None else 'N/A'}")
    print(f"- Proposed steps: {proposed_steps}")
    print(f"- Required tests: {required_tests}")
    print(f"- Risk checks: {risk_checks}")
    print(f"- Rollback plan: {plan.rollback_plan if plan is not None else 'N/A'}")
    print(f"- Status: {plan.status if plan is not None else (plan_result.status if plan_result else 'UNKNOWN')}")
    print(f"- Human final approval required: {plan.human_final_approval_required if plan is not None else True}")
    print(f"- Auto implementation allowed: {plan.auto_implementation_allowed if plan is not None else False}")
    print(f"- Saved: {store_result.saved if store_result is not None else False}")
    print(f"- Plans path: {store_result.plans_path if store_result is not None else 'None'}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- No implementation was applied automatically.")
    print("- Plan is saved for future human-reviewed work only.")
    print("- Final human approval is still required.")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _create_and_store_implementation_plan(
    proposal: object | None,
    review_result: ChangeProposalReviewResult,
    plan_config: ImplementationPlanStoreConfig,
) -> None:
    """Create a future implementation plan only for accepted reviews."""
    if not review_result.accepted:
        plan_result = ImplementationPlanResult(
            plan=None,
            created=False,
            status="NO_ACCEPTED_REVIEW",
            reasons=["No implementation plan created because proposal was not accepted"],
            blocking_reasons=[],
        )
        _print_implementation_plan(
            plan_result,
            None,
            message="No implementation plan created because proposal was not accepted",
        )
        return

    try:
        plan_result = ImplementationPlanWorkflow().create_from_review(
            proposal,
            review_result,
            ImplementationPlanConfig(),
        )
    except Exception as exc:
        plan_result = ImplementationPlanResult(
            plan=None,
            created=False,
            status="UNKNOWN",
            reasons=["Implementation plan could not be created"],
            blocking_reasons=[f"Implementation plan workflow failed: {exc}"],
        )

    store_result = None
    if plan_result.plan is not None:
        try:
            store_result = ImplementationPlanStore().append_plan(plan_result.plan, plan_config)
        except Exception as exc:
            store_result = ImplementationPlanStoreResult(
                saved=False,
                plans_path=None,
                total_plans=0,
                reasons=["Implementation plan store was requested"],
                blocking_reasons=[f"Implementation plan could not be saved: {exc}"],
            )

    _print_implementation_plan(plan_result, store_result)


def _review_saved_change_proposal(
    review_decision: str,
    proposal_index: int,
    reviewed_by: str | None,
    notes: str | None,
    proposal_config: ChangeProposalStoreConfig,
    review_log_config: ChangeProposalReviewLogConfig,
    implementation_plan_config: ImplementationPlanStoreConfig,
) -> None:
    """Review one saved proposal without implementing it."""
    try:
        proposals = ChangeProposalStore().load_proposals(proposal_config)
    except Exception as exc:
        _print_change_proposal_review(
            None,
            None,
            None,
            message=f"Could not load saved change proposals: {exc}",
        )
        return

    if not proposals:
        _print_change_proposal_review(
            None,
            None,
            None,
            message="No saved change proposals available",
        )
        return

    if proposal_index < 0 or proposal_index >= len(proposals):
        _print_change_proposal_review(
            None,
            None,
            None,
            message="Change proposal index is out of range",
        )
        return

    proposal = proposals[proposal_index]
    try:
        review_result = ChangeProposalReviewWorkflow().review(
            proposal,
            review_decision,
            ChangeProposalReviewConfig(),
            reviewed_by=reviewed_by or None,
            notes=notes or None,
        )
    except Exception as exc:
        review_result = ChangeProposalReviewResult(
            proposal_id=proposal.get("proposal_id") if isinstance(proposal, dict) else None,
            decision=None,
            status="UNKNOWN",
            accepted=False,
            implementation_allowed=False,
            reasons=["Change proposal review could not be recorded"],
            blocking_reasons=[f"Review workflow failed: {exc}"],
        )

    try:
        log_result = ChangeProposalReviewLogStore().append_review(proposal, review_result, review_log_config)
    except Exception as exc:
        log_result = ChangeProposalReviewLogResult(
            saved=False,
            log_path=None,
            total_records=0,
            reasons=["Change proposal review log was requested"],
            blocking_reasons=[f"Change proposal review log could not be saved: {exc}"],
        )

    _print_change_proposal_review(proposal, review_result, log_result)
    _create_and_store_implementation_plan(proposal, review_result, implementation_plan_config)


def _print_implementation_final_review(
    plan: object | None,
    final_review_result: ImplementationFinalReviewResult | None,
    log_result: ImplementationFinalReviewLogResult | None,
    message: str | None = None,
) -> None:
    """Print final implementation review output without implementing changes."""
    print("\nImplementation Final Review")
    if message:
        print(f"- Message: {message}")

    decision = final_review_result.decision if final_review_result is not None else None
    plan_id = (
        getattr(plan, "plan_id", None)
        if plan is not None and not isinstance(plan, dict)
        else (plan or {}).get("plan_id") if isinstance(plan, dict) else None
    )
    plan_id = plan_id or (final_review_result.plan_id if final_review_result is not None else None) or "N/A"
    decision_text = getattr(decision, "decision", None) or "UNKNOWN"
    reviewed_by = getattr(decision, "reviewed_by", None) or "N/A"
    notes = getattr(decision, "notes", None) or "None"
    reasons = final_review_result.reasons if final_review_result is not None else []
    blocking_reasons = final_review_result.blocking_reasons if final_review_result is not None else []
    if log_result is not None and log_result.blocking_reasons:
        blocking_reasons = list(blocking_reasons) + list(log_result.blocking_reasons)

    reasons_text = "; ".join(reasons) if reasons else "None"
    blocking_text = "; ".join(blocking_reasons) if blocking_reasons else "None"
    print(f"- Plan ID: {plan_id}")
    print(f"- Decision: {decision_text}")
    print(f"- Status: {final_review_result.status if final_review_result is not None else 'UNKNOWN'}")
    print(f"- Approved for work: {final_review_result.approved_for_work if final_review_result is not None else False}")
    print(
        "- Implementation allowed now: "
        f"{final_review_result.implementation_allowed_now if final_review_result is not None else False}"
    )
    print(f"- Reviewed by: {reviewed_by}")
    print(f"- Notes: {notes}")
    print(f"- Log saved: {log_result.saved if log_result is not None else False}")
    print(f"- Log path: {log_result.log_path if log_result is not None else 'None'}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- No implementation was applied automatically.")
    print("- Final review is recorded for future human-reviewed work only.")
    print("- APPROVE_FOR_WORK does not mean automatic implementation.")
    print(f"- Reasons: {reasons_text}")
    print(f"- Blocking reasons: {blocking_text}")


def _final_review_saved_implementation_plan(
    final_review_decision: str,
    plan_index: int,
    reviewed_by: str | None,
    notes: str | None,
    plan_config: ImplementationPlanStoreConfig,
    final_review_log_config: ImplementationFinalReviewLogConfig,
) -> None:
    """Final-review one saved implementation plan without implementing it."""
    try:
        plans = ImplementationPlanStore().load_plans(plan_config)
    except Exception as exc:
        _print_implementation_final_review(
            None,
            None,
            None,
            message=f"Could not load saved implementation plans: {exc}",
        )
        return

    if not plans:
        _print_implementation_final_review(
            None,
            None,
            None,
            message="No saved implementation plans available",
        )
        return

    if plan_index < 0 or plan_index >= len(plans):
        _print_implementation_final_review(
            None,
            None,
            None,
            message="Implementation plan index is out of range",
        )
        return

    plan = plans[plan_index]
    try:
        final_review_result = ImplementationFinalReviewWorkflow().review(
            plan,
            final_review_decision,
            ImplementationFinalReviewConfig(),
            reviewed_by=reviewed_by or None,
            notes=notes or None,
        )
    except Exception as exc:
        final_review_result = ImplementationFinalReviewResult(
            plan_id=plan.get("plan_id") if isinstance(plan, dict) else None,
            decision=None,
            status="UNKNOWN",
            approved_for_work=False,
            implementation_allowed_now=False,
            reasons=["Implementation final review could not be recorded"],
            blocking_reasons=[f"Final review workflow failed: {exc}"],
        )

    try:
        log_result = ImplementationFinalReviewLogStore().append_review(
            plan,
            final_review_result,
            final_review_log_config,
        )
    except Exception as exc:
        log_result = ImplementationFinalReviewLogResult(
            saved=False,
            log_path=None,
            total_records=0,
            reasons=["Implementation final review log was requested"],
            blocking_reasons=[f"Implementation final review log could not be saved: {exc}"],
        )

    _print_implementation_final_review(plan, final_review_result, log_result)


def _print_implementation_readiness(
    checklist: ImplementationReadinessChecklist | None,
    message: str | None = None,
) -> None:
    """Print implementation readiness output without applying changes."""
    print("\nImplementation Readiness")
    if message:
        print(f"- Message: {message}")

    checklist_items = checklist.checklist_items if checklist is not None else {}
    item_lines = (
        "; ".join(f"{name}={value}" for name, value in checklist_items.items())
        if checklist_items
        else "None"
    )
    missing = "; ".join(checklist.missing_items) if checklist is not None and checklist.missing_items else "None"
    warnings = "; ".join(checklist.warnings) if checklist is not None and checklist.warnings else "None"
    reasons = "; ".join(checklist.reasons) if checklist is not None and checklist.reasons else "None"
    blocking = (
        "; ".join(checklist.blocking_reasons)
        if checklist is not None and checklist.blocking_reasons
        else "None"
    )

    print(f"- Plan ID: {checklist.plan_id if checklist is not None and checklist.plan_id else 'N/A'}")
    print(f"- Ready: {checklist.ready if checklist is not None else False}")
    print(f"- Status: {checklist.status if checklist is not None else 'UNKNOWN'}")
    print(f"- Checklist items: {item_lines}")
    print(f"- Missing items: {missing}")
    print(f"- Warnings: {warnings}")
    print("- No strategy rule was changed.")
    print("- No trade signal was created.")
    print("- No implementation was applied automatically.")
    print("- Readiness means future human-reviewed work only.")
    print("- Live trading changes are not allowed.")
    print(f"- Reasons: {reasons}")
    print(f"- Blocking reasons: {blocking}")


def _latest_final_review_for_plan(records: list[dict], plan_id: str | None) -> dict | None:
    """Return the latest saved final review record for the selected plan."""
    if not plan_id:
        return None
    for record in reversed(records):
        if str(record.get("plan_id") or "") == str(plan_id):
            return record
    return None


def _check_saved_implementation_readiness(
    plan_index: int,
    plan_config: ImplementationPlanStoreConfig,
    final_review_log_config: ImplementationFinalReviewLogConfig,
) -> None:
    """Check readiness for one saved implementation plan."""
    try:
        plans = ImplementationPlanStore().load_plans(plan_config)
    except Exception as exc:
        _print_implementation_readiness(
            None,
            message=f"Could not load saved implementation plans: {exc}",
        )
        return

    if not plans:
        _print_implementation_readiness(
            None,
            message="No saved implementation plans available",
        )
        return

    if plan_index < 0 or plan_index >= len(plans):
        _print_implementation_readiness(
            None,
            message="Implementation plan index is out of range",
        )
        return

    plan = plans[plan_index]
    plan_id = str(plan.get("plan_id") or "") if isinstance(plan, dict) else str(getattr(plan, "plan_id", "") or "")
    try:
        final_review_records = ImplementationFinalReviewLogStore().load_log(final_review_log_config)
    except Exception:
        final_review_records = []

    final_review_record = _latest_final_review_for_plan(final_review_records, plan_id)
    checklist = ImplementationReadinessChecker().check(
        plan,
        final_review_record,
        ImplementationReadinessConfig(),
    )
    if final_review_record is None and "Final review approval was not found" not in checklist.blocking_reasons:
        checklist.blocking_reasons.append("Final review approval was not found")
    _print_implementation_readiness(checklist)


def _record_human_approval_decision(
    approval_result: StrategyApprovalPipelineResult,
    approval_decision: str,
    request_index: int,
    decided_by: str | None,
    notes: str | None,
    log_config: HumanApprovalLogConfig,
    proposal_config: ChangeProposalStoreConfig,
) -> None:
    """Record one approval decision without changing strategy behavior."""
    if not approval_result.created_requests:
        _print_human_approval_decision(
            None,
            None,
            None,
            message="No approval requests available",
        )
        return

    if request_index < 0 or request_index >= len(approval_result.created_requests):
        _print_human_approval_decision(
            None,
            None,
            None,
            message="No approval requests available at that index",
        )
        return

    request = approval_result.created_requests[request_index]
    try:
        decision_result = HumanApprovalWorkflow().decide(
            request,
            approval_decision,
            HumanApprovalConfig(),
            decided_by=decided_by or None,
            notes=notes or None,
        )
    except Exception as exc:
        decision_result = HumanApprovalResult(
            request=request,
            decision=None,
            approved=False,
            allowed_to_apply=False,
            status="UNKNOWN",
            reasons=["Human approval decision could not be recorded"],
            blocking_reasons=[f"Decision workflow failed: {exc}"],
        )

    try:
        log_result = HumanApprovalLogStore().append_decision(request, decision_result, log_config)
    except Exception as exc:
        log_result = HumanApprovalLogResult(
            saved=False,
            log_path=None,
            total_records=0,
            reasons=["Human approval decision log was requested"],
            blocking_reasons=[f"Approval decision log could not be saved: {exc}"],
        )

    _print_human_approval_decision(request, decision_result, log_result)
    _create_and_store_change_proposal(request, decision_result, log_result, log_config, proposal_config)


def _show_session_trend(
    session_history_config: SessionHistoryConfig,
    approval_decision: str = "",
    approval_request_index: int = 0,
    approval_decided_by: str | None = None,
    approval_notes: str | None = None,
    approval_log_config: HumanApprovalLogConfig | None = None,
    proposal_store_config: ChangeProposalStoreConfig | None = None,
) -> None:
    """Load saved session history and print trend analysis safely."""
    history = SessionHistoryStore().load_history(session_history_config)
    trend = SessionTrendAnalyzer().analyze(history, SessionTrendConfig())
    _print_session_history_trend(trend)
    review = SessionTrendCoach().review(trend, SessionTrendCoachConfig())
    _print_session_trend_coach_review(review)
    improvements = StrategyImprovementEngine().suggest(trend, review, StrategyImprovementConfig())
    _print_strategy_improvement_suggestions(improvements)
    try:
        approval_result = StrategyApprovalPipeline().create_requests(
            improvements,
            StrategyApprovalPipelineConfig(),
        )
    except Exception as exc:
        approval_result = StrategyApprovalPipelineResult(
            status="UNKNOWN",
            reasons=["Human approval request output was requested"],
            blocking_reasons=[f"Approval pipeline could not create requests: {exc}"],
        )
    _print_human_approval_requests(approval_result)
    if approval_decision:
        _record_human_approval_decision(
            approval_result,
            approval_decision,
            approval_request_index,
            approval_decided_by,
            approval_notes,
            approval_log_config or HumanApprovalLogConfig(),
            proposal_store_config or ChangeProposalStoreConfig(),
        )



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
    show_session_report: bool,
    export_session_report: bool,
    session_report_export_config: SessionReportExportConfig,
    save_session_history: bool,
    show_session_history_summary: bool,
    session_history_config: SessionHistoryConfig,
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
    reviews = reviewer.review_journal(journal) if journal.get_all_entries() else []
    if journal.get_all_entries():
        for review in reviews:
            print(f"- {review.trade_id}: {review.grade}")
            print(f"  Summary: {review.summary}")
            print(f"  Lesson: {review.lesson}")
    else:
        print("- No journal entries were recorded.")

    performance = _print_performance_report(journal)
    ai_coach_summary = reviews[0].summary if reviews else None

    print("\nFlow explanation")
    print(f"- {flow.explain(result)}")

    if show_trace:
        _print_decision_trace(result.trace_id, result.trace_explanation)

    if show_session_report or export_session_report or save_session_history or show_session_history_summary:
        result.journal_summary = summary
        result.performance_report = performance
        result.ai_coach_summary = ai_coach_summary
        session_report = TradingSessionReportGenerator().generate_from_flow_result(
            result,
            mode="demo",
            scenario=name,
            profile=profile.profile_name,
        )
    else:
        session_report = None

    if show_session_report and session_report is not None:
        _print_full_trading_session_report(session_report)

    if export_session_report:
        export_result = SessionReportExporter().export_all(session_report, session_report_export_config)
        _print_session_report_export(export_result)

    if save_session_history or show_session_history_summary:
        store = SessionHistoryStore()
        saved = False
        reasons = ["Session history summary requested"] if show_session_history_summary else []
        warnings: list[str] = []
        if save_session_history:
            saved = store.append_report(session_report, session_history_config)
            if saved:
                reasons.append("Session report saved to history")
            else:
                warnings.append("Session report could not be saved to history")
        history = store.load_history(session_history_config)
        history_summary = store.summarize(history) if (show_session_history_summary or save_session_history) else None
        _print_session_history_status(saved, session_history_config, history_summary, reasons, warnings)

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
    backtest_market_csv_result: BacktestMarketCsvResult,
    orderflow_replay_result: OrderFlowReplayResult | None,
    show_orderflow_replay_steps: bool,
    export_orderflow_report: bool,
    orderflow_export_config: OrderFlowReplayExportConfig,
    show_session_report: bool,
    export_session_report: bool,
    session_report_export_config: SessionReportExportConfig,
    save_session_history: bool,
    show_session_history_summary: bool,
    session_history_config: SessionHistoryConfig,
    backtest_max_iterations: int | None,
    export_backtest_trade_traces: bool,
    backtest_trace_dir: str,
) -> None:
    """Run one backtest scenario and print aggregate results."""
    print(f"Scenario: {name}")
    print("-" * 24)

    if backtest_market_csv_result.reason and backtest_market_csv_result.candles is None:
        print(f"- {backtest_market_csv_result.reason}")
        print("- Safe fallback: no backtest run")
        return

    if backtest_market_csv_result.candles is not None:
        candles = backtest_market_csv_result.candles.copy()
        print(f"- Backtest market candles: {backtest_market_csv_result.source}")
    else:
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
        BacktestConfig(
            symbol=profile.symbol,
            timeframe="M5",
            window_size=60,
            step_size=5,
            max_iterations=backtest_max_iterations,
        ),
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
        collect_iteration_traces=export_backtest_trade_traces,
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

    if export_backtest_trade_traces:
        json_path, txt_path = _export_backtest_trade_traces(
            backtest_trace_dir,
            name,
            profile,
            result,
            performance,
            quality,
        )
        print("\nBacktest Trade Trace Export")
        print(f"- JSON: {json_path}")
        print(f"- TXT: {txt_path}")
        print("- Research-only diagnostic export; no live systems were connected")

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

    if show_session_report or export_session_report or save_session_history or show_session_history_summary:
        backtest_report_source = SimpleNamespace(
            decision_action="BACKTEST",
            trade_executed=result.trades_executed > 0,
            market_bias="UNKNOWN",
            smc_bias=None,
            crt_bias=None,
            orderflow_bias=getattr(orderflow_context_result, "bias", None) if orderflow_context_result else None,
            safety_status=result.status,
            safety_allowed=result.completed,
            reasons=list(result.reasons),
            session_blocking_reasons=list(result.session_blocking_reasons),
            news_blocking_reasons=list(result.news_blocking_reasons),
            volatility_blocking_reasons=list(result.volatility_blocking_reasons),
            spread_blocking_reasons=list(result.spread_blocking_reasons),
            journal_summary=journal.summarize(),
            performance_report=performance,
            ai_coach_summary="Backtest summary generated from paper-trading journal and performance report.",
        )
        session_report = TradingSessionReportGenerator().generate_from_flow_result(
            backtest_report_source,
            mode="backtest",
            scenario=name,
            profile=profile.profile_name,
        )
    else:
        session_report = None

    if show_session_report and session_report is not None:
        _print_full_trading_session_report(session_report)

    if export_session_report:
        export_result = SessionReportExporter().export_all(session_report, session_report_export_config)
        _print_session_report_export(export_result)

    if save_session_history or show_session_history_summary:
        store = SessionHistoryStore()
        saved = False
        reasons = ["Session history summary requested"] if show_session_history_summary else []
        warnings: list[str] = []
        if save_session_history:
            saved = store.append_report(session_report, session_history_config)
            if saved:
                reasons.append("Session report saved to history")
            else:
                warnings.append("Session report could not be saved to history")
        history = store.load_history(session_history_config)
        history_summary = store.summarize(history) if (show_session_history_summary or save_session_history) else None
        _print_session_history_status(saved, session_history_config, history_summary, reasons, warnings)

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
    backtest_market_csv_result = _load_backtest_market_candles_from_csv(
        getattr(parsed_args, "backtest_market_csv", "")
    )
    orderflow_replay_result = _build_orderflow_replay_from_csv(getattr(parsed_args, "orderflow_replay_csv", ""))
    show_orderflow_replay_steps = bool(getattr(parsed_args, "show_orderflow_replay_steps", False))
    export_orderflow_report = bool(getattr(parsed_args, "export_orderflow_report", False))
    orderflow_export_config = OrderFlowReplayExportConfig(
        output_dir=getattr(parsed_args, "orderflow_report_dir", "reports") or "reports",
        include_steps=not bool(getattr(parsed_args, "no_orderflow_report_steps", False)),
    )
    show_session_report = bool(getattr(parsed_args, "show_session_report", False))
    export_session_report = bool(getattr(parsed_args, "export_session_report", False))
    session_report_export_config = SessionReportExportConfig(
        output_dir=getattr(parsed_args, "session_report_dir", "reports") or "reports",
    )
    save_session_history = bool(getattr(parsed_args, "save_session_history", False))
    show_session_history_summary = bool(getattr(parsed_args, "show_session_history_summary", False))
    session_history_config = SessionHistoryConfig(
        output_dir=getattr(parsed_args, "session_history_dir", "reports") or "reports",
    )
    show_session_trend = bool(getattr(parsed_args, "show_session_trend", False))
    approval_decision = str(getattr(parsed_args, "approval_decision", "") or "").strip()
    approval_request_index = int(getattr(parsed_args, "approval_request_index", 0) or 0)
    approval_decided_by = str(getattr(parsed_args, "approval_decided_by", "") or "").strip()
    approval_notes = str(getattr(parsed_args, "approval_notes", "") or "").strip()
    approval_log_config = HumanApprovalLogConfig(
        output_dir=getattr(parsed_args, "approval_log_dir", "reports") or "reports",
    )
    proposal_store_config = ChangeProposalStoreConfig(
        output_dir=getattr(parsed_args, "proposal_dir", "reports") or "reports",
    )
    register_change_proposal_doc = str(
        getattr(parsed_args, "register_change_proposal_doc", "") or ""
    ).strip()
    proposal_category = str(getattr(parsed_args, "proposal_category", "STRATEGY") or "STRATEGY").strip()
    proposal_priority = str(getattr(parsed_args, "proposal_priority", "MEDIUM") or "MEDIUM").strip()
    proposal_title = str(getattr(parsed_args, "proposal_title", "") or "").strip()
    review_change_proposal = str(getattr(parsed_args, "review_change_proposal", "") or "").strip()
    change_proposal_index = int(getattr(parsed_args, "change_proposal_index", 0) or 0)
    proposal_reviewed_by = str(getattr(parsed_args, "proposal_reviewed_by", "") or "").strip()
    proposal_review_notes = str(getattr(parsed_args, "proposal_review_notes", "") or "").strip()
    proposal_review_log_config = ChangeProposalReviewLogConfig(
        output_dir=getattr(parsed_args, "proposal_review_log_dir", "reports") or "reports",
    )
    implementation_plan_config = ImplementationPlanStoreConfig(
        output_dir=getattr(parsed_args, "implementation_plan_dir", "reports") or "reports",
    )
    final_review_implementation_plan = str(
        getattr(parsed_args, "final_review_implementation_plan", "") or ""
    ).strip()
    implementation_plan_index = int(getattr(parsed_args, "implementation_plan_index", 0) or 0)
    implementation_reviewed_by = str(getattr(parsed_args, "implementation_reviewed_by", "") or "").strip()
    implementation_review_notes = str(getattr(parsed_args, "implementation_review_notes", "") or "").strip()
    implementation_final_review_log_config = ImplementationFinalReviewLogConfig(
        output_dir=getattr(parsed_args, "implementation_final_review_log_dir", "reports") or "reports",
    )
    check_implementation_readiness = bool(getattr(parsed_args, "check_implementation_readiness", False))
    backtest_max_iterations = getattr(parsed_args, "backtest_max_iterations", None)
    export_backtest_trade_traces = bool(getattr(parsed_args, "export_backtest_trade_traces", False))
    backtest_trace_dir = getattr(parsed_args, "backtest_trace_dir", "reports") or "reports"

    if check_implementation_readiness:
        _check_saved_implementation_readiness(
            implementation_plan_index,
            implementation_plan_config,
            implementation_final_review_log_config,
        )
        return

    if final_review_implementation_plan:
        _final_review_saved_implementation_plan(
            final_review_implementation_plan,
            implementation_plan_index,
            implementation_reviewed_by,
            implementation_review_notes,
            implementation_plan_config,
            implementation_final_review_log_config,
        )
        return

    if review_change_proposal:
        _review_saved_change_proposal(
            review_change_proposal,
            change_proposal_index,
            proposal_reviewed_by,
            proposal_review_notes,
            proposal_store_config,
            proposal_review_log_config,
            implementation_plan_config,
        )
        return

    if register_change_proposal_doc:
        _register_change_proposal_doc(
            register_change_proposal_doc,
            proposal_category,
            proposal_priority,
            proposal_title,
            proposal_store_config,
        )
        return

    if approval_decision and not show_session_trend:
        print("Session trend is required to create approval requests")
        print("- No strategy rule was changed.")
        print("- No trade signal was created.")
        print("- Approval is only recorded for future human-reviewed work.")
        return

    only_showing_session_trend = (
        show_session_trend
        and args is not None
        and "--mode" not in args
        and "--scenario" not in args
        and not save_session_history
        and not show_session_history_summary
        and not show_session_report
        and not export_session_report
        and not export_orderflow_report
        and not getattr(parsed_args, "orderflow_replay_csv", "")
        and not getattr(parsed_args, "orderflow_csv", "")
    )
    if only_showing_session_trend:
        _show_session_trend(
            session_history_config,
            approval_decision=approval_decision,
            approval_request_index=approval_request_index,
            approval_decided_by=approval_decided_by,
            approval_notes=approval_notes,
            approval_log_config=approval_log_config,
            proposal_store_config=proposal_store_config,
        )
        return

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

    if show_session_trend:
        _show_session_trend(
            session_history_config,
            approval_decision=approval_decision,
            approval_request_index=approval_request_index,
            approval_decided_by=approval_decided_by,
            approval_notes=approval_notes,
            approval_log_config=approval_log_config,
            proposal_store_config=proposal_store_config,
        )

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
                    show_session_report,
                    export_session_report,
                    session_report_export_config,
                    save_session_history,
                    show_session_history_summary,
                    session_history_config,
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
                    backtest_market_csv_result,
                    orderflow_replay_result,
                    show_orderflow_replay_steps,
                    export_orderflow_report,
                    orderflow_export_config,
                    show_session_report,
                    export_session_report,
                    session_report_export_config,
                    save_session_history,
                    show_session_history_summary,
                    session_history_config,
                    backtest_max_iterations,
                    export_backtest_trade_traces,
                    backtest_trace_dir,
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
            show_session_report,
            export_session_report,
            session_report_export_config,
            save_session_history,
            show_session_history_summary,
            session_history_config,
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
            backtest_market_csv_result,
            orderflow_replay_result,
            show_orderflow_replay_steps,
            export_orderflow_report,
            orderflow_export_config,
            show_session_report,
            export_session_report,
            session_report_export_config,
            save_session_history,
            show_session_history_summary,
            session_history_config,
            backtest_max_iterations,
            export_backtest_trade_traces,
            backtest_trace_dir,
        )


if __name__ == "__main__":
    main()
