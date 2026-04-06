"""号码模式分析：奇偶、大小、连号、区间"""

from collections import Counter
from typing import List, Dict, Tuple

from lottery.data.models import DrawResult


def odd_even_distribution(draws: List[DrawResult]) -> Dict[str, float]:
    """奇偶比分布统计"""
    counter = Counter()
    for d in draws:
        odd = sum(1 for n in d.main_numbers if n % 2 == 1)
        even = len(d.main_numbers) - odd
        counter[f"{odd}:{even}"] += 1

    total = len(draws)
    return {k: round(v / total * 100, 1) for k, v in sorted(counter.items(), key=lambda x: -x[1])}


def high_low_distribution(draws: List[DrawResult], midpoint: int) -> Dict[str, float]:
    """大小比分布统计（以 midpoint 为界）"""
    counter = Counter()
    for d in draws:
        high = sum(1 for n in d.main_numbers if n > midpoint)
        low = len(d.main_numbers) - high
        counter[f"{high}:{low}"] += 1

    total = len(draws)
    return {k: round(v / total * 100, 1) for k, v in sorted(counter.items(), key=lambda x: -x[1])}


def consecutive_analysis(draws: List[DrawResult]) -> Dict[str, any]:
    """连号分析"""
    has_consecutive = 0
    pair_count = 0
    triple_count = 0

    for d in draws:
        nums = sorted(d.main_numbers)
        has_pair = False
        consecutive_run = 1
        max_run = 1
        for i in range(1, len(nums)):
            if nums[i] == nums[i - 1] + 1:
                consecutive_run += 1
                max_run = max(max_run, consecutive_run)
                has_pair = True
            else:
                consecutive_run = 1

        if has_pair:
            has_consecutive += 1
        if max_run >= 2:
            pair_count += 1
        if max_run >= 3:
            triple_count += 1

    total = len(draws)
    return {
        "consecutive_rate": round(has_consecutive / total * 100, 1),
        "pair_rate": round(pair_count / total * 100, 1),
        "triple_rate": round(triple_count / total * 100, 1),
    }


def zone_distribution(draws: List[DrawResult], pool_min: int, pool_max: int,
                      zones: int = 3) -> Dict[str, float]:
    """区间分布（将号码池分成 N 个区间）"""
    pool_size = pool_max - pool_min + 1
    zone_size = pool_size / zones

    counter = Counter()
    for d in draws:
        zone_counts = [0] * zones
        for n in d.main_numbers:
            z = min(int((n - pool_min) / zone_size), zones - 1)
            zone_counts[z] += 1
        key = ":".join(str(c) for c in zone_counts)
        counter[key] += 1

    total = len(draws)
    # 返回前10个最常见分布
    return {k: round(v / total * 100, 1)
            for k, v in sorted(counter.items(), key=lambda x: -x[1])[:10]}


def most_common_patterns(draws: List[DrawResult], pool_max: int) -> dict:
    """综合模式分析"""
    midpoint = pool_max // 2
    return {
        "odd_even": odd_even_distribution(draws),
        "high_low": high_low_distribution(draws, midpoint),
        "consecutive": consecutive_analysis(draws),
        "zones": zone_distribution(draws, 1, pool_max),
    }
