"""推荐引擎 - 融合统计与玄学"""

from datetime import date
from typing import List, Dict, Optional

from lottery.data.models import DrawResult
from lottery.engine.scorer import statistical_scores, xuanxue_modifier


# 推荐模式
MODES = {
    "stats": {"stat_weight": 1.0, "xuan_weight": 0.0, "name": "统计模式", "desc": "纯数据分析"},
    "xuanxue": {"stat_weight": 0.3, "xuan_weight": 0.7, "name": "玄学模式", "desc": "以玄学为主"},
    "balanced": {"stat_weight": 0.6, "xuan_weight": 0.4, "name": "平衡模式", "desc": "统计+玄学"},
    "random": {"stat_weight": 0.0, "xuan_weight": 0.0, "name": "随机模式", "desc": "纯随机"},
}


def compute_final_scores(draws: List[DrawResult], pool_min: int, pool_max: int,
                         mode: str = "balanced", d: date = None,
                         use_main: bool = True) -> Dict[int, float]:
    """
    计算最终综合评分

    Args:
        draws: 历史数据
        pool_min: 号码池最小值
        pool_max: 号码池最大值
        mode: 推荐模式
        d: 日期
        use_main: 是否用主号码

    Returns:
        {号码: 最终评分}
    """
    mode_config = MODES.get(mode, MODES["balanced"])
    sw = mode_config["stat_weight"]
    xw = mode_config["xuan_weight"]

    if mode == "random":
        import random
        return {n: random.random() for n in range(pool_min, pool_max + 1)}

    # 统计评分
    stat_scores = statistical_scores(draws, pool_min, pool_max, use_main) if sw > 0 else {}

    # 玄学修正
    xuan_mods = xuanxue_modifier(d, pool_max) if xw > 0 else {}

    final = {}
    for n in range(pool_min, pool_max + 1):
        stat_s = stat_scores.get(n, 0.5)
        xuan_m = xuan_mods.get(n, 1.0)

        if sw > 0 and xw > 0:
            # 统计分 * 统计权重 + 玄学修正 * 玄学权重
            score = stat_s * sw + (xuan_m - 0.5) * xw  # 把修正因子转为0-1范围
        elif sw > 0:
            score = stat_s
        elif xw > 0:
            score = xuan_m
        else:
            import random
            score = random.random()

        final[n] = round(max(0, score), 4)

    return final


def get_top_numbers(scores: Dict[int, float], top_n: int = 10) -> List[dict]:
    """获取评分最高的 N 个号码"""
    sorted_nums = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
    return [{"number": n, "score": s} for n, s in sorted_nums]
