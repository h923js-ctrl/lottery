"""和值分析"""

import statistics
from typing import List, Dict, Tuple

from lottery.data.models import DrawResult


def sum_values(draws: List[DrawResult]) -> List[int]:
    """计算每期主号码和值"""
    return [sum(d.main_numbers) for d in draws]


def sum_statistics(draws: List[DrawResult]) -> dict:
    """和值的统计指标"""
    sums = sum_values(draws)
    if not sums:
        return {}

    sorted_sums = sorted(sums)
    n = len(sorted_sums)
    q1 = sorted_sums[n // 4]
    q3 = sorted_sums[3 * n // 4]

    return {
        "mean": round(statistics.mean(sums), 1),
        "median": statistics.median(sums),
        "stdev": round(statistics.stdev(sums), 1) if len(sums) > 1 else 0,
        "min": min(sums),
        "max": max(sums),
        "q1": q1,
        "q3": q3,
        "iqr_range": (q1, q3),
        "recent_10_avg": round(statistics.mean(sums[-10:]), 1) if len(sums) >= 10 else round(statistics.mean(sums), 1),
    }


def sum_distribution(draws: List[DrawResult], bins: int = 10) -> Dict[str, int]:
    """和值区间分布"""
    sums = sum_values(draws)
    if not sums:
        return {}

    min_s, max_s = min(sums), max(sums)
    bin_size = max((max_s - min_s) // bins, 1)

    dist = {}
    for s in sums:
        bin_start = min_s + ((s - min_s) // bin_size) * bin_size
        bin_end = bin_start + bin_size - 1
        key = f"{bin_start}-{bin_end}"
        dist[key] = dist.get(key, 0) + 1

    return dist


def sum_trend(draws: List[DrawResult], window: int = 20) -> List[float]:
    """和值移动平均趋势"""
    sums = sum_values(draws)
    if len(sums) < window:
        return [statistics.mean(sums)] if sums else []

    result = []
    for i in range(window - 1, len(sums)):
        avg = statistics.mean(sums[i - window + 1:i + 1])
        result.append(round(avg, 1))
    return result
