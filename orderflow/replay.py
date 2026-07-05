"""Replay footprint candles into Order Flow Context over time.

This module is CSV/research/backtesting only. It does not connect to live data,
brokers, Sierra Chart live feeds, CME, or any external API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from orderflow.absorption import AbsorptionAnalyzer, AbsorptionConfig
from orderflow.data_quality import OrderFlowDataQualityChecker, OrderFlowDataQualityConfig
from orderflow.delta_cvd import DeltaCVDAnalyzer, DeltaCVDConfig, DeltaCVDPoint, DeltaCVDResult
from orderflow.footprint import FootprintCandle
from orderflow.imbalance import ImbalanceAnalyzer, ImbalanceConfig
from orderflow.orderflow_context import OrderFlowContextCombiner, OrderFlowContextConfig
from orderflow.sierra_chart_importer import SierraChartImportConfig, SierraChartImporter


@dataclass
class OrderFlowReplayConfig:
    """Configuration for replaying footprint candles."""

    require_data_quality: bool = True
    minimum_confidence: float = 50.0
    max_steps: int | None = None


@dataclass
class OrderFlowReplayStep:
    """One replay snapshot after processing a footprint candle."""

    index: int
    time: object | None
    candle_delta: float
    cumulative_delta: float
    delta_direction: str
    imbalance_bias: str
    absorption_bias: str
    orderflow_bias: str
    orderflow_confidence: float
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass
class OrderFlowReplayResult:
    """Full replay output for a footprint candle sequence."""

    steps: list[OrderFlowReplayStep] = field(default_factory=list)
    final_bias: str = "UNKNOWN"
    final_confidence: float = 0.0
    final_cvd: float = 0.0
    data_quality_status: str | None = None
    passed: bool = False
    reasons: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)


class OrderFlowReplayEngine:
    """Replay imported footprint candles one by one into context snapshots."""

    def replay(
        self,
        candles: Iterable[FootprintCandle] | None,
        config: OrderFlowReplayConfig,
    ) -> OrderFlowReplayResult:
        """Replay candles safely without generating trade signals."""
        candle_list = self._safe_candle_list(candles)
        if candle_list is None:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status="INVALID",
                passed=False,
                reasons=["Invalid footprint candle input"],
                blocking_reasons=["Footprint candle input is not iterable"],
            )

        data_quality_status: str | None = None
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if config.require_data_quality:
            quality = OrderFlowDataQualityChecker().check(candle_list, OrderFlowDataQualityConfig())
            data_quality_status = quality.status
            reasons.extend(quality.reasons)
            if quality.status in {"FAILED", "EMPTY", "INVALID"} or not quality.passed:
                return OrderFlowReplayResult(
                    steps=[],
                    final_bias="UNKNOWN",
                    final_confidence=0.0,
                    final_cvd=0.0,
                    data_quality_status=data_quality_status,
                    passed=False,
                    reasons=reasons or ["Order Flow data quality blocked replay"],
                    blocking_reasons=list(quality.blocking_reasons),
                )

        if not candle_list:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status=data_quality_status or "EMPTY",
                passed=False,
                reasons=reasons or ["No footprint candles available"],
                blocking_reasons=blocking_reasons or ["No footprint candles available"],
            )

        max_steps = self._safe_max_steps(config.max_steps, len(candle_list))
        replay_candles = candle_list[:max_steps]
        if not replay_candles:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status=data_quality_status,
                passed=False,
                reasons=[*reasons, "Replay produced no steps"],
                blocking_reasons=["Replay max_steps allowed zero candles"],
            )

        steps: list[OrderFlowReplayStep] = []
        combiner_config = OrderFlowContextConfig(minimum_confidence=config.minimum_confidence)

        for index, candle in enumerate(replay_candles):
            candles_so_far = replay_candles[: index + 1]
            delta_result = DeltaCVDAnalyzer().analyze(candles_so_far, DeltaCVDConfig())
            imbalance_result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())
            absorption_result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig())
            context = OrderFlowContextCombiner().combine(
                delta_result,
                imbalance_result,
                absorption_result,
                combiner_config,
            )

            latest_delta = float(delta_result.latest_delta or 0.0)
            confidence = self._clamp_confidence(context.confidence)
            steps.append(
                OrderFlowReplayStep(
                    index=index,
                    time=getattr(candle, "time", None),
                    candle_delta=latest_delta,
                    cumulative_delta=float(delta_result.final_cvd),
                    delta_direction=str(delta_result.latest_direction or "NEUTRAL"),
                    imbalance_bias=str(imbalance_result.bias or "UNKNOWN"),
                    absorption_bias=str(absorption_result.bias or "UNKNOWN"),
                    orderflow_bias=str(context.bias or "UNKNOWN"),
                    orderflow_confidence=confidence,
                    reasons=list(context.reasons),
                    blocking_reasons=list(context.blocking_reasons),
                )
            )

        final_step = steps[-1]
        result_reasons = [*reasons, f"Replayed {len(steps)} footprint candle(s)"]
        if config.max_steps is not None and len(steps) < len(candle_list):
            result_reasons.append(f"Replay limited to max_steps={len(steps)}")

        return OrderFlowReplayResult(
            steps=steps,
            final_bias=final_step.orderflow_bias,
            final_confidence=final_step.orderflow_confidence,
            final_cvd=final_step.cumulative_delta,
            data_quality_status=data_quality_status,
            passed=True,
            reasons=result_reasons,
            blocking_reasons=[],
        )


    def replay_incremental(
        self,
        candles: Iterable[FootprintCandle] | None,
        config: OrderFlowReplayConfig,
    ) -> OrderFlowReplayResult:
        """Replay candles with incremental Delta/CVD state for diagnostics."""
        candle_list = self._safe_candle_list(candles)
        if candle_list is None:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status="INVALID",
                passed=False,
                reasons=["Invalid footprint candle input"],
                blocking_reasons=["Footprint candle input is not iterable"],
            )

        data_quality_status: str | None = None
        reasons: list[str] = []
        blocking_reasons: list[str] = []

        if config.require_data_quality:
            quality = OrderFlowDataQualityChecker().check(candle_list, OrderFlowDataQualityConfig())
            data_quality_status = quality.status
            reasons.extend(quality.reasons)
            if quality.status in {"FAILED", "EMPTY", "INVALID"} or not quality.passed:
                return OrderFlowReplayResult(
                    steps=[],
                    final_bias="UNKNOWN",
                    final_confidence=0.0,
                    final_cvd=0.0,
                    data_quality_status=data_quality_status,
                    passed=False,
                    reasons=reasons or ["Order Flow data quality blocked replay"],
                    blocking_reasons=list(quality.blocking_reasons),
                )

        if not candle_list:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status=data_quality_status or "EMPTY",
                passed=False,
                reasons=reasons or ["No footprint candles available"],
                blocking_reasons=blocking_reasons or ["No footprint candles available"],
            )

        max_steps = self._safe_max_steps(config.max_steps, len(candle_list))
        replay_candles = candle_list[:max_steps]
        if not replay_candles:
            return OrderFlowReplayResult(
                steps=[],
                final_bias="UNKNOWN",
                final_confidence=0.0,
                final_cvd=0.0,
                data_quality_status=data_quality_status,
                passed=False,
                reasons=[*reasons, "Replay produced no steps"],
                blocking_reasons=["Replay max_steps allowed zero candles"],
            )

        steps: list[OrderFlowReplayStep] = []
        combiner_config = OrderFlowContextConfig(minimum_confidence=config.minimum_confidence)
        delta_threshold = max(0.0, float(DeltaCVDConfig().strong_delta_threshold))
        cumulative_delta = 0.0

        for index, candle in enumerate(replay_candles):
            if candle is None:
                latest_delta = 0.0
                total_volume = 0.0
                time_value = None
                point_reasons = ["Missing candle treated as neutral"]
            else:
                try:
                    latest_delta = float(candle.delta())
                except Exception:
                    latest_delta = 0.0
                try:
                    total_volume = float(candle.total_volume())
                except Exception:
                    total_volume = 0.0
                time_value = getattr(candle, "time", None)
                point_reasons = []

            cumulative_delta += latest_delta
            delta_direction = self._direction_from_delta(latest_delta, delta_threshold)

            if delta_direction == "BUYING_PRESSURE":
                point_reasons.append("Delta is above strong threshold")
            elif delta_direction == "SELLING_PRESSURE":
                point_reasons.append("Delta is below negative strong threshold")
            else:
                point_reasons.append("Delta is inside neutral threshold range")

            delta_point = DeltaCVDPoint(
                index=index,
                time=time_value,
                delta=latest_delta,
                cumulative_delta=cumulative_delta,
                total_volume=total_volume,
                direction=delta_direction,
                reasons=point_reasons,
            )
            delta_result = DeltaCVDResult(
                points=[delta_point],
                final_cvd=cumulative_delta,
                latest_delta=latest_delta,
                latest_direction=delta_direction,
                reasons=[
                    f"Processed {index + 1} footprint candle(s)",
                    self._latest_delta_reason(delta_direction),
                ],
                blocking_reasons=[],
            )
            imbalance_result = ImbalanceAnalyzer().analyze(candle, ImbalanceConfig())
            absorption_result = AbsorptionAnalyzer().analyze(candle, AbsorptionConfig())
            context = OrderFlowContextCombiner().combine(
                delta_result,
                imbalance_result,
                absorption_result,
                combiner_config,
            )

            confidence = self._clamp_confidence(context.confidence)
            steps.append(
                OrderFlowReplayStep(
                    index=index,
                    time=getattr(candle, "time", None),
                    candle_delta=latest_delta,
                    cumulative_delta=float(delta_result.final_cvd),
                    delta_direction=str(delta_result.latest_direction or "NEUTRAL"),
                    imbalance_bias=str(imbalance_result.bias or "UNKNOWN"),
                    absorption_bias=str(absorption_result.bias or "UNKNOWN"),
                    orderflow_bias=str(context.bias or "UNKNOWN"),
                    orderflow_confidence=confidence,
                    reasons=list(context.reasons),
                    blocking_reasons=list(context.blocking_reasons),
                )
            )

        final_step = steps[-1]
        result_reasons = [*reasons, f"Replayed {len(steps)} footprint candle(s)"]
        if config.max_steps is not None and len(steps) < len(candle_list):
            result_reasons.append(f"Replay limited to max_steps={len(steps)}")

        return OrderFlowReplayResult(
            steps=steps,
            final_bias=final_step.orderflow_bias,
            final_confidence=final_step.orderflow_confidence,
            final_cvd=final_step.cumulative_delta,
            data_quality_status=data_quality_status,
            passed=True,
            reasons=result_reasons,
            blocking_reasons=[],
        )

    def replay_csv(self, path: str, config: OrderFlowReplayConfig) -> OrderFlowReplayResult:
        """Load a footprint CSV from disk and replay it safely."""
        candles = SierraChartImporter().load_csv(path, SierraChartImportConfig())
        result = self.replay(candles, config)
        if not candles and not result.blocking_reasons:
            result.blocking_reasons.append("CSV could not be imported or contained no candles")
        if not candles and not result.reasons:
            result.reasons.append("No footprint candles imported from CSV")
        return result

    def explain(self, result: OrderFlowReplayResult) -> str:
        """Return a readable replay summary."""
        reasons_text = "; ".join(result.reasons) if result.reasons else "None"
        blocks_text = "; ".join(result.blocking_reasons) if result.blocking_reasons else "None"
        return (
            "Order Flow replay: "
            f"steps={len(result.steps)}, "
            f"final_bias={result.final_bias}, "
            f"final_confidence={result.final_confidence:.1f}, "
            f"final_cvd={result.final_cvd:.2f}, "
            f"data_quality_status={result.data_quality_status}, "
            f"passed={result.passed}, "
            f"reasons={reasons_text}, "
            f"blocking_reasons={blocks_text}."
        )


    def _direction_from_delta(self, delta: float, threshold: float) -> str:
        """Classify directional pressure from delta and threshold."""
        if delta > threshold:
            return "BUYING_PRESSURE"
        if delta < -threshold:
            return "SELLING_PRESSURE"
        return "NEUTRAL"

    def _latest_delta_reason(self, direction: str) -> str:
        """Return the standard latest delta reason text."""
        if direction == "BUYING_PRESSURE":
            return "Latest delta indicates buying pressure"
        if direction == "SELLING_PRESSURE":
            return "Latest delta indicates selling pressure"
        return "Latest delta is neutral"

    def _safe_candle_list(self, candles: Iterable[FootprintCandle] | None) -> list[FootprintCandle] | None:
        """Convert optional iterables to a list without crashing."""
        if candles is None:
            return []
        try:
            return list(candles)
        except TypeError:
            return None

    def _safe_max_steps(self, max_steps: int | None, candle_count: int) -> int:
        """Resolve max_steps while keeping at least zero replay steps."""
        if max_steps is None:
            return candle_count
        try:
            return max(0, min(int(max_steps), candle_count))
        except (TypeError, ValueError):
            return candle_count

    def _clamp_confidence(self, confidence: float) -> float:
        """Keep confidence inside the normal 0-100 range."""
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(100.0, value))
