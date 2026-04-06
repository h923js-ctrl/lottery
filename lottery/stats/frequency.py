"""号码频率分析"""

from collections import Counter
from typing import List, Dict, Tuple

from lottery.data.models import DrawResult


def number_frequency(draws: List[DrawResult], pool_min: int, pool_max: int,
                     use_main: bool = True) -> Dict[int, int]:
    """统计每个号码出现次数"""
    counter = Counter()
    for d in draws:
        nums = d.main_numbers if use_main else d.bonus_numbers
        for n in nums:
            counter[n] += 1
    # 确保所有号码都有记录
    for n in range(pool_min, pool_max + 1):
        if n not in counter:
            counter[n] = 0
    return dict(sorted(counter.items()))


def hot_numbers(draws: List[DrawResult], pool_min: int, pool_max: int,
                top_n: int = 10, use_main: bool = True) -> List[Tuple[int, int]]:
    """热号：出现频率最高的号码"""
    freq = number_frequency(draws, pool_min, pool_max, use_main)
    return sorted(freq.items(), key=lambda x: -x[1])[:top_n]


def cold_numbers(draws: List[DrawResult], pool_min: int, pool_max: int,
                 top_n: int = 10, use_main: bool = True) -> List[Tuple[int, int]]:
    """冷号：出现频率最低的号码"""
    freq = number_frequency(draws, pool_min, pool_max, use_main)
    return sorted(freq.items(), key=lambda x: x[1])[:top_n]


def recent_vs_overall(draws: List[DrawResult], pool_min: int, pool_max: int,
                      recent_n: int = 30, use_main: bool = True) -> Dict[int, dict]:
    """
    对比近期频率和总体频率

    Returns:
        {号码: {"overall": 总频率, "recent": 近期频率, "ratio": 近期/总体比值, "status": 热/冷/平}}
    """
    overall = number_frequency(draws, pool_min, pool_max, use_main)
    recent = number_frequency(draws[-recent_n:], pool_min, pool_max, use_main) if len(draws) > recent_n else overall

    total = len(draws)
    recent_total = min(recent_n, len(draws))

    result = {}
    for n in range(pool_min, pool_max + 1):
        overall_rate = overall.get(n, 0) / max(total, 1)
        recent_rate = recent.get(n, 0) / max(recent_total, 1)

        if overall_rate > 0:
            ratio = recent_rate / overall_rate
        else:
            ratio = 1.0

        if ratio > 1.3:
            status = "hot"
        elif ratio < 0.7:
            status = "cold"
        else:
            status = "normal"

        result[n] = {
            "overall_count": overall.get(n, 0),
            "recent_count": recent.get(n, 0),
            "overall_rate": round(overall_rate, 4),
            "recent_rate": round(recent_rate, 4),
            "ratio": round(ratio, 2),
            "status": status,
        }
    return result
