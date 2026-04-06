"""本地 JSON 缓存管理"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from lottery.config import CACHE_DIR
from lottery.data.models import DrawResult


def ensure_cache_dir():
    """确保缓存目录存在"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path(lottery_code: str) -> Path:
    return CACHE_DIR / f"{lottery_code}.json"


def load_draws(lottery_code: str) -> List[DrawResult]:
    """从缓存加载开奖数据"""
    path = cache_path(lottery_code)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [DrawResult.from_dict(d) for d in data.get("draws", [])]
    except (json.JSONDecodeError, KeyError):
        return []


def save_draws(lottery_code: str, draws: List[DrawResult]):
    """保存开奖数据到缓存"""
    ensure_cache_dir()
    data = {
        "lottery_type": lottery_code,
        "last_updated": datetime.now().isoformat(),
        "count": len(draws),
        "draws": [d.to_dict() for d in draws],
    }
    path = cache_path(lottery_code)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_draws(existing: List[DrawResult], new_draws: List[DrawResult]) -> List[DrawResult]:
    """合并去重，按期号排序"""
    by_period = {d.period: d for d in existing}
    for d in new_draws:
        by_period[d.period] = d
    return sorted(by_period.values(), key=lambda d: d.period)


def get_last_period(lottery_code: str) -> Optional[str]:
    """获取缓存中最新期号"""
    draws = load_draws(lottery_code)
    return draws[-1].period if draws else None
