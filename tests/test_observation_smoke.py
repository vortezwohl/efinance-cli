"""结构化 observation 输出的组装与端到端烟雾测试。

该文件覆盖：

- `trace_window` 默认值与用户覆盖；
- 多指标 recent event detection 的基础契约；
- 支持命令在 observation 视图下的最小 CLI 输出链路。
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd
from click.testing import CliRunner

from efinance_cli.commands import create_root_command
from efinance_cli.models import (
    CommandSpec,
    InvocationRequest,
    InvocationResult,
    ObservationPayload,
    OutputOptions,
)
from efinance_cli.observation import build_observation_output, detect_recent_events
from tests.cli_regression_support import print_observation


def build_history_frame() -> pd.DataFrame:
    """构造带多指标交叉与阈值事件的历史行情样本。"""

    return pd.DataFrame(
        {
            "股票代码": ["AAPL"] * 6,
            "股票名称": ["Apple Inc."] * 6,
            "日期": [
                "2026-05-21",
                "2026-05-22",
                "2026-05-23",
                "2026-05-26",
                "2026-05-27",
                "2026-05-28",
            ],
            "收盘": [99.0, 101.0, 100.0, 102.0, 104.0, 106.0],
            "开盘": [98.0, 100.0, 99.0, 101.0, 103.0, 105.0],
            "最高": [100.0, 102.0, 101.0, 103.0, 105.0, 107.0],
            "最低": [97.0, 99.0, 98.0, 100.0, 102.0, 104.0],
            "成交量": [1000, 1200, 1100, 1300, 1500, 1700],
            "ma5": [100.0, 100.0, 99.8, 100.5, 102.0, 103.0],
            "ma10": [100.2, 100.2, 100.1, 100.4, 101.0, 102.5],
            "ma20": [100.5, 100.5, 100.4, 100.3, 100.8, 101.4],
            "ema12": [99.7, 100.1, 100.0, 100.9, 101.8, 102.9],
            "ema26": [100.1, 100.2, 100.1, 100.5, 101.0, 101.7],
            "macd_dif": [-0.30, -0.10, 0.05, 0.20, 0.28, 0.36],
            "macd_dea": [-0.20, -0.12, -0.02, 0.08, 0.18, 0.26],
            "macd_histogram": [-0.10, 0.02, 0.07, 0.12, 0.10, 0.10],
            "rsi14": [45.0, 48.0, 51.0, 54.0, 56.0, 59.0],
            "kdj_k": [40.0, 45.0, 50.0, 55.0, 60.0, 62.0],
            "kdj_d": [42.0, 44.0, 47.0, 52.0, 57.0, 60.0],
            "kdj_j": [36.0, 47.0, 56.0, 61.0, 66.0, 66.0],
            "ppo": [-0.10, -0.05, 0.02, 0.06, 0.09, 0.12],
            "ppo_signal": [-0.08, -0.06, -0.01, 0.03, 0.06, 0.09],
            "atr14": [2.1, 2.0, 1.9, 2.0, 2.1, 2.2],
            "boll_upper": [103.0, 103.0, 103.0, 103.5, 104.0, 105.0],
            "boll_lower": [96.0, 96.0, 96.0, 96.5, 97.0, 97.5],
            "obv": [100.0, 220.0, 180.0, 320.0, 470.0, 640.0],
            "volume_ratio_5": [0.8, 0.9, 1.1, 1.2, 1.0, 1.3],
            "mfi14": [48.0, 50.0, 53.0, 55.0, 58.0, 60.0],
            "cmf20": [-0.05, -0.02, 0.01, 0.03, 0.06, 0.08],
            "supertrend": [101.5, 101.4, 101.2, 101.0, 102.0, 103.0],
            "supertrend_direction": [-1.0, -1.0, 1.0, 1.0, 1.0, 1.0],
            "plus_di": [18.0, 19.0, 21.0, 24.0, 26.0, 28.0],
            "minus_di": [22.0, 21.0, 20.0, 18.0, 17.0, 16.0],
        }
    )


def build_request(trace_window: int = 32) -> InvocationRequest:
    """构造 observation 组装请求。"""

    return InvocationRequest(
        spec=CommandSpec(
            module_name="common",
            function_name="get_quote_history",
            callback=lambda **_: None,
            help_text="test",
        ),
        kwargs={},
        output=OutputOptions(
            format_name="table",
            indicator_level="full",
            view_mode="observation",
            trace_window=trace_window,
        ),
    )


class ObservationSmokeTest(unittest.TestCase):
    """覆盖 observation 结构化输出的关键烟雾场景。"""

    def test_trace_window_defaults_to_32_and_accepts_user_override(self) -> None:
        """默认 trace window 为 32，用户传值时应按请求裁剪。"""

        frame = build_history_frame()
        default_payload = build_observation_output(build_request(), frame)
        override_payload = build_observation_output(build_request(trace_window=4), frame)
        self.assertIsInstance(default_payload, ObservationPayload)
        self.assertIsInstance(override_payload, ObservationPayload)
        print_observation("默认 trace payload.meta", default_payload.meta)
        print_observation("覆盖 trace payload.meta", override_payload.meta)

        self.assertEqual(default_payload.meta["trace_window"], 32)
        self.assertEqual(len(default_payload.trace_points[0].points), len(frame))
        self.assertEqual(override_payload.meta["trace_window"], 4)
        self.assertEqual(len(override_payload.trace_points[0].points), 4)
        self.assertEqual(override_payload.trace_points[0].points[0]["bar_offset"], -3)

    def test_recent_events_cover_multiple_indicator_families(self) -> None:
        """事件检测应覆盖线交叉、阈值穿越、band touch 与方向变化。"""

        frame = build_history_frame()
        series_map = {column: pd.to_numeric(frame[column], errors="coerce") for column in frame.columns if column not in {"股票代码", "股票名称", "日期"}}
        series_map["close"] = pd.to_numeric(frame["收盘"], errors="coerce")
        events = detect_recent_events(frame, series_map)
        keys = {event.event_key for event in events}
        print_observation("recent event keys", sorted(keys))

        self.assertIn("ma5_crossed_above_ma10", keys)
        self.assertIn("macd_dif_crossed_above_macd_dea", keys)
        self.assertIn("rsi14_crossed_above_50", keys)
        self.assertIn("close_touched_upper_band_boll_upper", keys)
        self.assertIn("supertrend_direction_changed_positive", keys)
        self.assertIn("obv_rose_3_bars", keys)

    def test_supported_history_command_can_render_observation_table(self) -> None:
        """支持命令在 observation 模式下应输出 boxed table。"""

        frame = build_history_frame()
        payload = build_observation_output(build_request(trace_window=4), frame)

        def fake_invoke(executor_self, request):
            self.assertEqual(request.spec.module_name, "common")
            self.assertEqual(request.spec.function_name, "get_quote_history")
            self.assertEqual(request.output.view_mode, "observation")
            self.assertEqual(request.output.trace_window, 4)
            return InvocationResult(value=payload)

        with patch("efinance_cli.executor.CommandExecutor.invoke", new=fake_invoke):
            runner = CliRunner()
            cli = create_root_command()
            result = runner.invoke(
                cli,
                [
                    "common",
                    "get-quote-history",
                    "105.AAPL",
                    "--beg",
                    "20260501",
                    "--end",
                    "20260528",
                    "--view",
                    "observation",
                    "--trace-window",
                    "4",
                ],
            )

        print_observation("history observation CLI 输出", result.output)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("| meta", result.output)
        self.assertIn("| trace_points.price_ma", result.output)
        self.assertIn("| recent_events", result.output)

    def test_supported_latest_command_can_render_observation_json(self) -> None:
        """最新行情 observation 模式应产出完整 JSON section。"""

        history_frame = build_history_frame()
        payload = build_observation_output(build_request(trace_window=4), history_frame)

        def fake_invoke(executor_self, request):
            self.assertEqual(request.spec.module_name, "common")
            self.assertEqual(request.spec.function_name, "get_latest_quote")
            self.assertEqual(request.output.view_mode, "observation")
            self.assertEqual(request.output.trace_window, 4)
            return InvocationResult(value=payload)

        with patch("efinance_cli.executor.CommandExecutor.invoke", new=fake_invoke):
            runner = CliRunner()
            cli = create_root_command()
            result = runner.invoke(
                cli,
                [
                    "common",
                    "get-latest-quote",
                    "105.AAPL",
                    "--view",
                    "observation",
                    "--format",
                    "json",
                    "--trace-window",
                    "4",
                ],
            )

        print_observation("latest observation JSON 输出", result.output)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn('"meta"', result.output)
        self.assertIn('"latest_quote"', result.output)
        self.assertIn('"trace_points"', result.output)
        self.assertIn('"recent_events"', result.output)


if __name__ == "__main__":
    unittest.main()
