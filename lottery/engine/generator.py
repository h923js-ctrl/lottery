"""约束随机生成器"""

import random
from datetime import date
from typing import List, Dict, Optional

from lottery.config import LOTTERY_TYPES
from lottery.data.models import DrawResult
from lottery.engine.recommender import compute_final_scores


def _weighted_sample(scores: Dict[int, float], count: int) -> List[int]:
    """加权随机采样"""
    numbers = list(scores.keys())
    weights = [max(scores[n], 0.001) for n in numbers]  # 确保非零
    selected = []

    for _ in range(count):
        if not numbers:
            break
        chosen = random.choices(numbers, weights=weights, k=1)[0]
        idx = numbers.index(chosen)
        selected.append(chosen)
        numbers.pop(idx)
        weights.pop(idx)

    return sorted(selected)


def _check_constraints(numbers: List[int], pool_max: int) -> bool:
    """检查号码是否满足约束"""
    if not numbers:
        return False

    n = len(numbers)

    # 1. 奇偶比不能太极端（全奇或全偶）
    odd_count = sum(1 for x in numbers if x % 2 == 1)
    if odd_count == 0 or odd_count == n:
        return False

    # 2. 不能超过3个连号
    sorted_nums = sorted(numbers)
    consecutive = 1
    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i - 1] + 1:
            consecutive += 1
            if consecutive > 3:
                return False
        else:
            consecutive = 1

    # 3. 和值不能太极端
    total = sum(numbers)
    expected_avg = (1 + pool_max) / 2 * n
    if total < expected_avg * 0.4 or total > expected_avg * 1.6:
        return False

    return True


def generate_numbers(draws: List[DrawResult], lottery_code: str,
                     mode: str = "balanced", d: date = None) -> dict:
    """
    生成一注推荐号码

    Returns:
        {"main": [...], "bonus": [...], "scores": {...}}
    """
    config = LOTTERY_TYPES[lottery_code]
    pool_min, pool_max = config["main_range"]
    main_count = config["main_count"]

    # 计算主号码评分
    main_scores = compute_final_scores(
        draws, pool_min, pool_max, mode, d, use_main=True
    )

    # 生成主号码（带约束重试）
    main_numbers = None
    for _ in range(50):
        candidate = _weighted_sample(main_scores, main_count)
        if lottery_code == "qxc":
            # 七星彩特殊处理：7个位置独立选
            candidate = []
            for pos in range(7):
                pos_range = config.get("position_ranges", [(0, 9)] * 7)[pos]
                pos_scores = {n: main_scores.get(n, 0.5) for n in range(pos_range[0], pos_range[1] + 1)}
                chosen = random.choices(
                    list(pos_scores.keys()),
                    weights=list(pos_scores.values()),
                    k=1
                )[0]
                candidate.append(chosen)
            main_numbers = candidate
            break
        if _check_constraints(candidate, pool_max):
            main_numbers = candidate
            break
    else:
        # 放弃约束，直接用加权采样
        main_numbers = _weighted_sample(main_scores, main_count)

    # 生成附加号码
    bonus_numbers = []
    if config.get("bonus_range") and config.get("bonus_count", 0) > 0:
        b_min, b_max = config["bonus_range"]
        b_count = config["bonus_count"]
        bonus_scores = compute_final_scores(
            draws, b_min, b_max, mode, d, use_main=False
        )
        bonus_numbers = _weighted_sample(bonus_scores, b_count)

    return {
        "main": main_numbers,
        "bonus": bonus_numbers,
        "main_scores": {n: main_scores.get(n, 0) for n in main_numbers},
    }


def generate_multiple(draws: List[DrawResult], lottery_code: str,
                      count: int = 5, mode: str = "balanced",
                      d: date = None) -> List[dict]:
    """生成多注推荐号码"""
    results = []
    seen = set()

    for _ in range(count * 3):  # 多尝试几次避免重复
        if len(results) >= count:
            break
        result = generate_numbers(draws, lottery_code, mode, d)
        key = tuple(result["main"]) + tuple(result["bonus"])
        if key not in seen:
            seen.add(key)
            results.append(result)

    return results
