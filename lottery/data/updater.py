"""数据增量更新"""

from typing import Callable, Optional

from lottery.config import LOTTERY_TYPES
from lottery.data.scraper import fetch_history
from lottery.data.storage import load_draws, save_draws, merge_draws


def update_lottery(lottery_code: str, callback: Optional[Callable] = None) -> int:
    """
    更新指定彩票数据

    Returns:
        新增的期数
    """
    existing = load_draws(lottery_code)
    last_period = existing[-1].period if existing else None

    new_draws = fetch_history(
        lottery_code,
        start=last_period if last_period else None,
        callback=callback,
    )

    if not new_draws and not existing:
        return 0

    if new_draws:
        merged = merge_draws(existing, new_draws)
        save_draws(lottery_code, merged)
        new_count = len(merged) - len(existing)
        return new_count
    return 0


def update_all(callback: Optional[Callable] = None) -> dict:
    """更新所有彩票数据"""
    results = {}
    for code in LOTTERY_TYPES:
        try:
            count = update_lottery(code, callback)
            results[code] = count
        except Exception as e:
            if callback:
                callback(f"  ❌ {LOTTERY_TYPES[code]['name']} 更新失败: {e}")
            results[code] = -1
    return results
