import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ai.trade_reviewer import TradeReviewer
from analysis.news_filter import NewsEvent, NewsFilterConfig
from analysis.session_filter import SessionFilterConfig
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
    to_volatility_filter_config,
)
from core.backtest_runner import BacktestConfig, BacktestRunner
from core.capital_protection import CapitalProtectionConfig, CapitalProtectionState
from core.market_analyzer import MarketAnalyzerConfig
from core.multi_timeframe import MultiTimeframeConfig
from core.paper_trading_flow import PaperTradingFlow, PaperTradingFlowConfig
from risk.risk_engine import RiskEngineConfig
from storage.backtest_quality import BacktestQualityChecker, BacktestQualityConfig
from storage.performance_report import PerformanceReporter
from storage.trade_journal import TradeJournal


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
    return parser


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


def _run_demo_scenario(
    name: str,
    profile: TradingProfile,
    capital_config: CapitalProtectionConfig,
    broker_config: PaperBrokerConfig,
    risk_config: RiskEngineConfig,
    session_config: SessionFilterConfig,
    news_config: NewsFilterConfig,
    volatility_config: VolatilityFilterConfig,
    session_time: datetime,
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
    flow_config = PaperTradingFlowConfig(symbol=profile.symbol)
    broker_state = _create_broker_state(broker_config)

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
    session_time: datetime,
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
    )

    print("\nAI Trader Backtest")
    print(f"- Scenario: {name}")
    print(f"- Total iterations: {result.total_iterations}")
    print(f"- Trades executed: {result.trades_executed}")
    print(f"- Trades blocked: {result.trades_blocked}")
    print(f"- Final balance: {result.final_balance:.2f}")
    print(f"- Total PnL: {result.total_pnl:.2f}")
    print("- Note: research-only simulation, not live trading")

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

    print("\nBacktest explanation")
    print(f"- {runner.explain(result)}")

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

    _print_profile_summary(selected_profile)
    if session_time_warning:
        print(f"- Warning: {session_time_warning}")
    for warning in news_warnings:
        print(f"- Warning: {warning}")
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
                    parsed_session_time,
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
                    parsed_session_time,
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
            parsed_session_time,
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
            parsed_session_time,
        )


if __name__ == "__main__":
    main()
