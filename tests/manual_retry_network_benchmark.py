"""真实外网下的网络抖动重试基准脚本。

该脚本用于对比：
1. 裸调用：单次原子网络请求，不额外包裹本项目的统一 retry；
2. retry 调用：同一原子网络请求，使用 `efinance_cli.retry_utils.with_network_retry`
   进行最多 32 次、带 delay 的真实重试。

设计目标：
- 使用真实外网与真实上游 `efinance` 调用；
- 给出成功率、失败率、恢复次数、尝试次数与耗时分布；
- 结果可复跑，且不依赖 mock。
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import efinance
from efinance.utils import MarketType

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from efinance_cli.retry_utils import with_network_retry


DEFAULT_ROUNDS = 30


@dataclass(slots=True)
class BenchmarkCase:
    """描述一条真实网络基准用例。"""

    name: str
    func: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass(slots=True)
class AttemptResult:
    """描述单次调用结果。"""

    mode: str
    success: bool
    attempts: int
    duration_seconds: float
    error_type: str | None
    error_message: str | None


def build_cases() -> list[BenchmarkCase]:
    """构造真实外网基准用例。"""

    return [
        BenchmarkCase(
            name="common.get_latest_quote(105.AAPL)",
            func=efinance.common.get_latest_quote,
            args=("105.AAPL",),
            kwargs={},
        ),
        BenchmarkCase(
            name="utils.search_quote(AAPL, US_stock)",
            func=efinance.utils.search_quote,
            args=("AAPL",),
            kwargs={
                "market_type": MarketType.US_stock,
                "count": 2,
                "use_local": False,
            },
        ),
        BenchmarkCase(
            name="stock.get_quote_history(AAPL, US_stock)",
            func=efinance.stock.get_quote_history,
            args=("AAPL",),
            kwargs={
                "market_type": MarketType.US_stock,
                "beg": "20250501",
                "end": "20250528",
            },
        ),
    ]


def run_once(case: BenchmarkCase, mode: str) -> AttemptResult:
    """执行一次真实网络调用。"""

    attempts = 0

    def counted_call() -> Any:
        nonlocal attempts
        attempts += 1
        return case.func(*case.args, **case.kwargs)

    caller = counted_call if mode == "raw" else with_network_retry(counted_call)

    started = time.perf_counter()
    try:
        caller()
        duration_seconds = time.perf_counter() - started
        return AttemptResult(
            mode=mode,
            success=True,
            attempts=attempts,
            duration_seconds=duration_seconds,
            error_type=None,
            error_message=None,
        )
    except Exception as exc:  # noqa: BLE001
        duration_seconds = time.perf_counter() - started
        return AttemptResult(
            mode=mode,
            success=False,
            attempts=attempts,
            duration_seconds=duration_seconds,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )


def summarize(case: BenchmarkCase, results: list[AttemptResult]) -> dict[str, Any]:
    """汇总某个用例的一组 raw/retry 结果。"""

    grouped = {
        "raw": [item for item in results if item.mode == "raw"],
        "retry": [item for item in results if item.mode == "retry"],
    }
    summary: dict[str, Any] = {"case": case.name}
    for mode, items in grouped.items():
        durations = [item.duration_seconds for item in items]
        successes = [item for item in items if item.success]
        failures = [item for item in items if not item.success]
        recovered_successes = [item for item in successes if item.attempts > 1]
        attempt_histogram = Counter(item.attempts for item in items)
        error_histogram = Counter(item.error_type for item in failures if item.error_type)
        summary[mode] = {
            "rounds": len(items),
            "successes": len(successes),
            "failures": len(failures),
            "success_rate": len(successes) / len(items) if items else 0.0,
            "failure_rate": len(failures) / len(items) if items else 0.0,
            "recovered_successes": len(recovered_successes),
            "recovered_success_rate": len(recovered_successes) / len(items) if items else 0.0,
            "avg_attempts": statistics.mean(item.attempts for item in items) if items else 0.0,
            "max_attempts": max(item.attempts for item in items) if items else 0,
            "attempt_histogram": dict(sorted(attempt_histogram.items())),
            "error_histogram": dict(error_histogram),
            "avg_duration_seconds": statistics.mean(durations) if durations else 0.0,
            "median_duration_seconds": statistics.median(durations) if durations else 0.0,
            "p95_duration_seconds": percentile(durations, 0.95) if durations else 0.0,
        }

    raw_failures = summary["raw"]["failures"]
    retry_failures = summary["retry"]["failures"]
    raw_success_rate = summary["raw"]["success_rate"]
    retry_success_rate = summary["retry"]["success_rate"]
    summary["comparison"] = {
        "success_rate_delta": retry_success_rate - raw_success_rate,
        "failure_count_delta": retry_failures - raw_failures,
        "failure_reduction_ratio": (
            (raw_failures - retry_failures) / raw_failures if raw_failures else None
        ),
    }
    return summary


def percentile(values: list[float], ratio: float) -> float:
    """计算简单分位数。"""

    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * ratio))))
    return ordered[index]


def benchmark_case(case: BenchmarkCase, rounds: int) -> tuple[list[AttemptResult], dict[str, Any]]:
    """对单个用例执行成对 raw/retry 基准。"""

    results: list[AttemptResult] = []
    for round_index in range(rounds):
        modes = ("raw", "retry") if round_index % 2 == 0 else ("retry", "raw")
        for mode in modes:
            result = run_once(case, mode)
            results.append(result)
            print(
                json.dumps(
                    {
                        "case": case.name,
                        "round": round_index + 1,
                        "mode": mode,
                        **asdict(result),
                    },
                    ensure_ascii=False,
                )
            )
    return results, summarize(case, results)


def main() -> None:
    """运行真实外网重试基准。"""

    rounds = DEFAULT_ROUNDS
    started_at = datetime.now().astimezone()
    summaries: list[dict[str, Any]] = []
    all_results: dict[str, list[dict[str, Any]]] = {}

    for case in build_cases():
        print(f"\n### START {case.name} ###")
        results, summary = benchmark_case(case, rounds)
        summaries.append(summary)
        all_results[case.name] = [asdict(item) for item in results]
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    ended_at = datetime.now().astimezone()
    report = {
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "rounds_per_mode": rounds,
        "summaries": summaries,
        "results": all_results,
    }

    output_path = Path("docs") / f"retry-benchmark-{started_at.strftime('%Y%m%d-%H%M%S')}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nREPORT_SAVED={output_path}")


if __name__ == "__main__":
    main()
