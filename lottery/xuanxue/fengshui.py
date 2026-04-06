"""风水数字能量分析"""

from datetime import date
from typing import Dict, List

# 数字吉凶
NUMBER_ENERGY = {
    0: {"energy": "中", "meaning": "圆满、归零", "level": 0},
    1: {"energy": "吉", "meaning": "独立、开始", "level": 1},
    2: {"energy": "吉", "meaning": "好事成双", "level": 1},
    3: {"energy": "吉", "meaning": "生生不息", "level": 2},
    4: {"energy": "凶", "meaning": "谐音不吉", "level": -1},
    5: {"energy": "吉", "meaning": "五福临门", "level": 1},
    6: {"energy": "大吉", "meaning": "六六大顺", "level": 3},
    7: {"energy": "吉", "meaning": "七星高照", "level": 1},
    8: {"energy": "大吉", "meaning": "发财发达", "level": 3},
    9: {"energy": "大吉", "meaning": "长长久久", "level": 2},
}

# 数字组合能量（两两搭配）
PAIR_ENERGY = {
    (1, 6): 2,   # 一路顺
    (1, 8): 3,   # 要发
    (2, 8): 2,   # 易发
    (3, 8): 2,   # 生发
    (5, 8): 2,   # 我发
    (6, 6): 3,   # 六六大顺
    (6, 8): 3,   # 顺发
    (8, 8): 3,   # 发发
    (9, 9): 2,   # 久久
    (1, 4): -1,  # 要死（避免）
    (4, 4): -2,  # 死死（大忌）
    (5, 4): -1,  # 我死（避免）
}


def number_fengshui_score(n: int) -> float:
    """单个数字的风水评分"""
    tail = n % 10
    info = NUMBER_ENERGY.get(tail, {"level": 0})
    return info["level"]


def pair_harmony(a: int, b: int) -> float:
    """两个数字的搭配和谐度"""
    t1, t2 = a % 10, b % 10
    key = (min(t1, t2), max(t1, t2))
    return PAIR_ENERGY.get(key, 0)


def combination_fengshui_score(numbers: List[int]) -> float:
    """一组数字的综合风水评分"""
    # 单数评分
    total = sum(number_fengshui_score(n) for n in numbers)

    # 两两搭配评分
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            total += pair_harmony(numbers[i], numbers[j]) * 0.5

    return round(total, 1)


def fengshui_lucky_numbers(d: date = None, pool_max: int = 35) -> dict:
    """
    基于风水生成数字权重

    Returns:
        {number: weight}
    """
    weights = {}
    for n in range(1, pool_max + 1):
        tail = n % 10
        info = NUMBER_ENERGY.get(tail, {"level": 0})
        level = info["level"]

        # 将 level (-2 ~ 3) 映射到权重 (0.7 ~ 1.4)
        weight = 1.0 + level * 0.1
        weight = max(0.7, min(1.4, weight))
        weights[n] = round(weight, 2)

    return weights


def get_fengshui_analysis(pool_max: int = 35) -> dict:
    """完整风水分析"""
    # 大吉数字
    great_lucky = [n for n in range(1, pool_max + 1) if NUMBER_ENERGY.get(n % 10, {}).get("level", 0) >= 2]
    # 吉数字
    lucky = [n for n in range(1, pool_max + 1) if NUMBER_ENERGY.get(n % 10, {}).get("level", 0) == 1]
    # 需避免
    avoid = [n for n in range(1, pool_max + 1) if NUMBER_ENERGY.get(n % 10, {}).get("level", 0) < 0]

    return {
        "great_lucky": great_lucky,
        "lucky": lucky,
        "avoid": avoid,
        "best_pairs": [(1, 8), (6, 8), (3, 8), (6, 6), (8, 8), (9, 9)],
        "worst_pairs": [(4, 4), (1, 4), (5, 4)],
        "desc": "风水数理以8(发)、6(顺)、9(久)为大吉，4为凶数宜避",
    }
