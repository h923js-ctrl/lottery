#!/usr/bin/env python3
"""
构建脚本：抓取最新数据 + 预计算统计/玄学 → 输出 JSON 到 docs/data/
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

# 确保能找到 lottery 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lottery.config import LOTTERY_TYPES
from lottery.data.scraper import fetch_history
from lottery.data.models import DrawResult
from lottery.stats.frequency import hot_numbers, cold_numbers, number_frequency
from lottery.stats.gap import overdue_numbers
from lottery.stats.pattern import most_common_patterns
from lottery.stats.sum_analysis import sum_statistics
from lottery.xuanxue.wuxing import get_wuxing_analysis, get_day_ganzhi
from lottery.xuanxue.shengxiao import get_shengxiao_analysis
from lottery.xuanxue.bagua import get_bagua_analysis
from lottery.xuanxue.lunar import get_lunar_analysis
from lottery.xuanxue.fengshui import get_fengshui_analysis

DOCS_DIR = Path(__file__).parent / "docs" / "data"


def build_lottery_data(code: str) -> dict:
    """为一种彩票构建完整数据"""
    config = LOTTERY_TYPES[code]
    print(f"  📥 抓取 {config['name']} 数据...")

    # 抓取数据
    draws = fetch_history(code, callback=lambda m: print(m))
    if not draws:
        print(f"  ❌ {config['name']} 无数据")
        return None

    pool_min, pool_max = config["main_range"]
    period = min(100, len(draws))
    recent = draws[-period:]

    # 统计分析
    hot = hot_numbers(recent, pool_min, pool_max, top_n=10)
    cold = cold_numbers(recent, pool_min, pool_max, top_n=10)
    overdue = overdue_numbers(recent, pool_min, pool_max)
    freq = number_frequency(recent, pool_min, pool_max)
    sum_stats = sum_statistics(recent)

    patterns = {}
    if code != "qxc":
        patterns = most_common_patterns(recent, pool_max)

    # 最近50期历史
    history = []
    for d in draws[-50:]:
        history.append({
            "period": d.period,
            "date": d.date,
            "main": d.main_numbers,
            "bonus": d.bonus_numbers,
        })
    history.reverse()

    # 全部频率数据（前端选号用）
    all_freq = [{"number": n, "count": c} for n, c in sorted(freq.items())]

    return {
        "name": config["name"],
        "code": code,
        "main_range": list(config["main_range"]),
        "main_count": config["main_count"],
        "bonus_range": list(config["bonus_range"]) if config.get("bonus_range") else None,
        "bonus_count": config.get("bonus_count", 0),
        "total": len(draws),
        "period": period,
        "history": history,
        "stats": {
            "hot": [{"number": n, "count": c} for n, c in hot],
            "cold": [{"number": n, "count": c} for n, c in cold],
            "overdue": overdue[:8],
            "frequency": all_freq,
            "sum_stats": sum_stats,
            "patterns": patterns,
        },
    }


def build_xuanxue() -> dict:
    """构建今日玄学数据"""
    today = date.today()
    tg, dz = get_day_ganzhi(today)
    wx = get_wuxing_analysis(today)
    sx = get_shengxiao_analysis(today)
    bg = get_bagua_analysis(today)
    ln = get_lunar_analysis(today)
    fs = get_fengshui_analysis()

    return {
        "date": today.isoformat(),
        "wuxing": {
            "ganzhi": tg + dz,
            "element": wx["today_element"],
            "desc": wx["element_desc"],
            "lucky_tails": wx["lucky_tails"],
            "sheng_tails": wx["sheng_tails"],
            "avoid_tails": wx["avoid_tails"],
        },
        "shengxiao": {
            "year": sx["year"],
            "animal": sx["animal"],
            "lucky_numbers": sx["lucky_numbers"],
            "liuhe": sx["liuhe"],
            "sanhe": sx["sanhe"],
            "chong": sx["chong"],
            "desc": sx["desc"],
        },
        "bagua": {
            "name": bg["gua"]["combined_name"],
            "upper_desc": bg["upper_desc"],
            "lower_desc": bg["lower_desc"],
            "lucky_numbers": bg["lucky_numbers"][:10],
            "yao": bg["yao_number"],
            "desc": bg["desc"],
        },
        "lunar": {
            "display": ln["display"],
            "is_lucky_day": ln["is_lucky_day"],
            "desc": ln["lucky_desc"],
        },
        "fengshui": {
            "great_lucky": fs["great_lucky"][:10],
            "lucky": fs["lucky"][:10],
            "avoid": fs["avoid"][:10],
            "desc": fs["desc"],
        },
    }


def main():
    print("🔨 开始构建静态数据...\n")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 构建每种彩票数据
    for code in ["ssq", "dlt", "qxc", "kl8"]:
        data = build_lottery_data(code)
        if data:
            out = DOCS_DIR / f"{code}.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
            size = out.stat().st_size / 1024
            print(f"  ✅ {data['name']}: {data['total']}期 → {out.name} ({size:.0f}KB)\n")

    # 构建玄学数据
    print("  🔮 计算今日玄学...")
    xuan = build_xuanxue()
    out = DOCS_DIR / "xuanxue.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(xuan, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  ✅ 玄学数据 → xuanxue.json\n")

    print("✅ 构建完成！文件在 docs/data/")


if __name__ == "__main__":
    main()
