"""号码趋势分析"""

from typing import List, Dict

from lottery.data.models import DrawResult
from lottery.stats.frequency import number_frequency


def trend_direction(draws: List[DrawResult], pool_min: int, pool_max: int,
                    window: int = 30, use_main: bool = True) -> Dict[int, dict]:
    """
    分析每个号码的近期趋势

    比较最近 window 期和前一个 window 期的频率变化
    """
    if len(draws) < window * 2:
        # 数据不足，全部标记为平稳
        return {n: {"direction": "stable", "change": 0.0}
                for n in range(pool_min, pool_max + 1)}

    recent = draws[-window:]
    previous = draws[-window * 2:-window]

    freq_recent = number_frequency(recent, pool_min, pool_max, use_main)
    freq_prev = number_frequency(previous, pool_min, pool_max, use_main)

    result = {}
    for n in range(pool_min, pool_max + 1):
        r = freq_recent.get(n, 0) / window
        p = freq_prev.get(n, 0) / window

        change = r - p
        if change > 0.05:
            direction = "rising"
        elif change < -0.05:
            direction = "falling"
        else:
            direction = "stable"

        result[n] = {
            "direction": direction,
            "change": round(change, 3),
            "recent_freq": freq_recent.get(n, 0),
            "prev_freq": freq_prev.get(n, 0),
        }
    return result


def number_momentum(draws: List[DrawResult], pool_min: int, pool_max: int,
                    windows: List[int] = None, use_main: bool = True) -> Dict[int, float]:
    """
    号码动量指标：综合多个时间窗口的趋势

    短期上升 + 中期上升 = 强动量
    """
    if windows is None:
        windows = [10, 20, 50]

    momentum = {n: 0.0 for n in range(pool_min, pool_max + 1)}
    weights = [0.5, 0.3, 0.2]  # 短期权重更高

    for w, weight in zip(windows, weights):
        if len(draws) < w:
            continue
        trend = trend_direction(draws, pool_min, pool_max, w // 2, use_main)
        for n in range(pool_min, pool_max + 1):
            momentum[n] += trend[n]["change"] * weight

    # 归一化到 0-1
    values = list(momentum.values())
    min_v = min(values) if values else 0
    max_v = max(values) if values else 1
    range_v = max_v - min_v if max_v > min_v else 1

    return {n: round((v - min_v) / range_v, 3) for n, v in momentum.items()}
