"""综合评分系统"""

import random
from typing import List, Dict

from lottery.data.models import DrawResult
from lottery.stats.frequency import recent_vs_overall
from lottery.stats.gap import current_gap, average_gap
from lottery.stats.trend import number_momentum


def statistical_scores(draws: List[DrawResult], pool_min: int, pool_max: int,
                       use_main: bool = True) -> Dict[int, float]:
    """
    统计学综合评分 (0 ~ 1)

    评分因子:
    - 频率得分 (25%): 近期频率相对总体的比值
    - 遗漏得分 (25%): 当前遗漏值 vs 平均遗漏
    - 趋势得分 (25%): 号码动量
    - 随机因子 (25%): 增加多样性
    """
    if not draws:
        return {n: 0.5 for n in range(pool_min, pool_max + 1)}

    # 1. 频率得分
    freq_data = recent_vs_overall(draws, pool_min, pool_max, use_main=use_main)
    freq_scores = {}
    for n in range(pool_min, pool_max + 1):
        ratio = freq_data[n]["ratio"]
        # 热号得分高，但不要太极端
        freq_scores[n] = min(ratio / 2.0, 1.0)

    # 2. 遗漏得分
    cur_gaps = current_gap(draws, pool_min, pool_max, use_main)
    avg_gaps = average_gap(draws, pool_min, pool_max, use_main)
    gap_scores = {}
    for n in range(pool_min, pool_max + 1):
        if avg_gaps[n] > 0:
            overdue = cur_gaps[n] / avg_gaps[n]
            # 越超过平均遗漏，得分越高（"该出了"）
            gap_scores[n] = min(overdue / 3.0, 1.0)
        else:
            gap_scores[n] = 0.5

    # 3. 趋势得分
    momentum = number_momentum(draws, pool_min, pool_max, use_main=use_main)

    # 4. 随机因子
    random_scores = {n: random.random() for n in range(pool_min, pool_max + 1)}

    # 综合评分
    scores = {}
    for n in range(pool_min, pool_max + 1):
        score = (
            freq_scores.get(n, 0.5) * 0.25 +
            gap_scores.get(n, 0.5) * 0.25 +
            momentum.get(n, 0.5) * 0.25 +
            random_scores[n] * 0.25
        )
        scores[n] = round(score, 4)

    return scores


def xuanxue_modifier(d=None, pool_max: int = 35) -> Dict[int, float]:
    """
    玄学综合修正因子

    融合五行、生肖、八卦、农历、风水的权重
    """
    from datetime import date as date_type
    from lottery.xuanxue.wuxing import wuxing_lucky_numbers
    from lottery.xuanxue.shengxiao import shengxiao_lucky_numbers
    from lottery.xuanxue.bagua import bagua_lucky_numbers
    from lottery.xuanxue.lunar import lunar_lucky_numbers
    from lottery.xuanxue.fengshui import fengshui_lucky_numbers

    if d is None:
        d = date_type.today()

    wuxing = wuxing_lucky_numbers(d, pool_max)
    shengxiao = shengxiao_lucky_numbers(d, pool_max)
    bagua = bagua_lucky_numbers(d, pool_max)
    lunar = lunar_lucky_numbers(d, pool_max)
    fengshui = fengshui_lucky_numbers(d, pool_max)

    modifiers = {}
    for n in range(1, pool_max + 1):
        # 加权平均：五行30% + 八卦25% + 风水20% + 生肖15% + 农历10%
        mod = (
            wuxing.get(n, 1.0) * 0.30 +
            bagua.get(n, 1.0) * 0.25 +
            fengshui.get(n, 1.0) * 0.20 +
            shengxiao.get(n, 1.0) * 0.15 +
            lunar.get(n, 1.0) * 0.10
        )
        modifiers[n] = round(mod, 3)

    return modifiers
