"""号码遗漏值分析"""

from typing import List, Dict

from lottery.data.models import DrawResult


def current_gap(draws: List[DrawResult], pool_min: int, pool_max: int,
                use_main: bool = True) -> Dict[int, int]:
    """
    每个号码距离上次出现的期数（当前遗漏值）
    """
    gaps = {}
    for n in range(pool_min, pool_max + 1):
        gap = 0
        for d in reversed(draws):
            nums = d.main_numbers if use_main else d.bonus_numbers
            if n in nums:
                break
            gap += 1
        else:
            gap = len(draws)  # 从未出现
        gaps[n] = gap
    return gaps


def average_gap(draws: List[DrawResult], pool_min: int, pool_max: int,
                use_main: bool = True) -> Dict[int, float]:
    """每个号码的平均出现间隔"""
    result = {}
    for n in range(pool_min, pool_max + 1):
        positions = []
        for i, d in enumerate(draws):
            nums = d.main_numbers if use_main else d.bonus_numbers
            if n in nums:
                positions.append(i)
        if len(positions) >= 2:
            intervals = [positions[j] - positions[j - 1] for j in range(1, len(positions))]
            result[n] = round(sum(intervals) / len(intervals), 1)
        elif len(positions) == 1:
            result[n] = float(len(draws))
        else:
            result[n] = float(len(draws))
    return result


def max_gap(draws: List[DrawResult], pool_min: int, pool_max: int,
            use_main: bool = True) -> Dict[int, int]:
    """每个号码的历史最大遗漏"""
    result = {}
    for n in range(pool_min, pool_max + 1):
        positions = [-1]  # 虚拟起始
        for i, d in enumerate(draws):
            nums = d.main_numbers if use_main else d.bonus_numbers
            if n in nums:
                positions.append(i)
        positions.append(len(draws))  # 到当前
        max_g = 0
        for j in range(1, len(positions)):
            max_g = max(max_g, positions[j] - positions[j - 1] - 1)
        result[n] = max_g
    return result


def overdue_numbers(draws: List[DrawResult], pool_min: int, pool_max: int,
                    threshold: float = 1.5, use_main: bool = True) -> List[dict]:
    """
    找出遗漏值超过平均遗漏 threshold 倍的号码（"该出了"）
    """
    cur = current_gap(draws, pool_min, pool_max, use_main)
    avg = average_gap(draws, pool_min, pool_max, use_main)

    overdue = []
    for n in range(pool_min, pool_max + 1):
        if avg[n] > 0 and cur[n] > avg[n] * threshold:
            overdue.append({
                "number": n,
                "current_gap": cur[n],
                "avg_gap": avg[n],
                "overdue_ratio": round(cur[n] / avg[n], 1),
            })
    return sorted(overdue, key=lambda x: -x["overdue_ratio"])
