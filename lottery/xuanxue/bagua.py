"""八卦数理分析"""

from datetime import date

# 先天八卦数
XIANTIAN_GUA = {
    "乾": {"number": 1, "element": "金", "direction": "南", "meaning": "天", "numbers": [1, 9, 11, 19]},
    "兑": {"number": 2, "element": "金", "direction": "东南", "meaning": "泽", "numbers": [2, 12, 22, 32]},
    "离": {"number": 3, "element": "火", "direction": "东", "meaning": "火", "numbers": [3, 13, 23, 33]},
    "震": {"number": 4, "element": "木", "direction": "东北", "meaning": "雷", "numbers": [4, 14, 24, 34]},
    "巽": {"number": 5, "element": "木", "direction": "西南", "meaning": "风", "numbers": [5, 15, 25, 35]},
    "坎": {"number": 6, "element": "水", "direction": "西", "meaning": "水", "numbers": [6, 16, 26]},
    "艮": {"number": 7, "element": "土", "direction": "西北", "meaning": "山", "numbers": [7, 17, 27]},
    "坤": {"number": 8, "element": "土", "direction": "北", "meaning": "地", "numbers": [8, 18, 28]},
}

# 后天八卦数（洛书数）
HOUTIAN_GUA = {
    "坎": 1, "坤": 2, "震": 3, "巽": 4,
    "中": 5, "乾": 6, "兑": 7, "艮": 8, "离": 9,
}


def _date_to_gua_index(d: date) -> int:
    """日期转卦象索引"""
    # 用日期数字之和取卦
    total = d.year + d.month + d.day
    return total % 8


def get_day_gua(d: date = None) -> dict:
    """获取当日主卦"""
    if d is None:
        d = date.today()

    gua_names = list(XIANTIAN_GUA.keys())

    # 上卦：(年+月)%8
    upper_idx = (d.year + d.month) % 8
    upper = gua_names[upper_idx]

    # 下卦：(年+月+日)%8
    lower_idx = (d.year + d.month + d.day) % 8
    lower = gua_names[lower_idx]

    # 动爻：总数%6 + 1
    yao = (d.year + d.month + d.day) % 6 + 1

    return {
        "upper": upper,
        "lower": lower,
        "upper_info": XIANTIAN_GUA[upper],
        "lower_info": XIANTIAN_GUA[lower],
        "yao": yao,
        "combined_name": f"{upper}{lower}卦",
    }


def bagua_lucky_numbers(d: date = None, pool_max: int = 35) -> dict:
    """
    基于八卦生成吉利数字权重

    Returns:
        {number: weight}
    """
    if d is None:
        d = date.today()

    gua = get_day_gua(d)
    upper = gua["upper"]
    lower = gua["lower"]

    # 主卦相关数字为大吉
    upper_nums = set(XIANTIAN_GUA[upper]["numbers"])
    lower_nums = set(XIANTIAN_GUA[lower]["numbers"])

    # 洛书数
    upper_luoshu = HOUTIAN_GUA.get(upper, 5)
    lower_luoshu = HOUTIAN_GUA.get(lower, 5)

    weights = {}
    for n in range(1, pool_max + 1):
        weight = 1.0

        if n in upper_nums:
            weight = 1.35
        elif n in lower_nums:
            weight = 1.25

        # 洛书数对应的尾数
        if n % 10 == upper_luoshu or n % 10 == lower_luoshu:
            weight = max(weight, 1.15)

        # 动爻数
        if n % 10 == gua["yao"]:
            weight = max(weight, 1.1)

        weights[n] = round(weight, 2)

    return weights


def get_bagua_analysis(d: date = None) -> dict:
    """完整八卦分析"""
    if d is None:
        d = date.today()

    gua = get_day_gua(d)
    upper = gua["upper"]
    lower = gua["lower"]

    return {
        "gua": gua,
        "upper_desc": f"上卦{upper}({XIANTIAN_GUA[upper]['meaning']})，五行属{XIANTIAN_GUA[upper]['element']}",
        "lower_desc": f"下卦{lower}({XIANTIAN_GUA[lower]['meaning']})，五行属{XIANTIAN_GUA[lower]['element']}",
        "lucky_numbers": sorted(set(XIANTIAN_GUA[upper]["numbers"] + XIANTIAN_GUA[lower]["numbers"])),
        "yao_number": gua["yao"],
        "desc": f"今日{gua['combined_name']}，上{upper}下{lower}，动爻第{gua['yao']}爻",
    }
