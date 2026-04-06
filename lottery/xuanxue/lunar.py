"""农历日期与吉数分析"""

from datetime import date

# 农历新年日期查表（公历日期）2016-2027
LUNAR_NEW_YEAR = {
    2016: (2, 8),
    2017: (1, 28),
    2018: (2, 16),
    2019: (2, 5),
    2020: (1, 25),
    2021: (2, 12),
    2022: (2, 1),
    2023: (1, 22),
    2024: (2, 10),
    2025: (1, 29),
    2026: (2, 17),
    2027: (2, 6),
}

# 每月天数模式（用位编码存储，1=大月30天，0=小月29天）+ 闰月信息
# 格式: (月天数位编码, 闰月月份, 闰月天数 0=无闰月)
LUNAR_YEAR_INFO = {
    2016: (0b010110101010, 0, 0),
    2017: (0b100101101010, 6, 29),
    2018: (0b100101011010, 0, 0),
    2019: (0b101010101010, 0, 0),
    2020: (0b011010101010, 4, 29),
    2021: (0b010101101010, 0, 0),
    2022: (0b101001011010, 0, 0),
    2023: (0b110100101010, 2, 29),
    2024: (0b011010101010, 0, 0),
    2025: (0b010101011010, 6, 29),
    2026: (0b100101010110, 0, 0),
    2027: (0b010010101010, 0, 0),
}

# 吉日（农历）
LUCKY_DAYS = [1, 2, 3, 6, 8, 9, 15, 16, 18, 28]

# 特别吉利的数字组合（谐音吉利）
LUCKY_COMBOS = {
    168: "一路发",
    518: "我要发",
    618: "六一八顺发",
    888: "发发发",
    666: "六六大顺",
    99: "长长久久",
    88: "发发",
    66: "顺顺",
    18: "要发",
    68: "顺发",
}


def estimate_lunar_date(d: date = None) -> dict:
    """
    估算农历日期（简化算法）

    返回大致的农历月日，精度约±1天
    """
    if d is None:
        d = date.today()

    year = d.year
    if year not in LUNAR_NEW_YEAR:
        # 回退到简单估算
        return {"lunar_month": ((d.month + 10) % 12) + 1, "lunar_day": d.day, "is_estimate": True}

    ny_month, ny_day = LUNAR_NEW_YEAR[year]
    new_year_date = date(year, ny_month, ny_day)

    if d < new_year_date:
        # 还在上一年的农历
        year -= 1
        if year not in LUNAR_NEW_YEAR:
            return {"lunar_month": 12, "lunar_day": d.day, "is_estimate": True}
        ny_month, ny_day = LUNAR_NEW_YEAR[year]
        new_year_date = date(year, ny_month, ny_day)

    days_since = (d - new_year_date).days

    # 用月天数信息推算月份
    lunar_month = 1
    lunar_day = days_since + 1

    if year in LUNAR_YEAR_INFO:
        month_bits, leap_month, leap_days = LUNAR_YEAR_INFO[year]
        month = 1
        for i in range(12):
            month_len = 30 if (month_bits >> (11 - i)) & 1 else 29
            if lunar_day <= month_len:
                break
            lunar_day -= month_len
            month += 1
            # 闰月
            if leap_month > 0 and month == leap_month + 1 and i < 11:
                if lunar_day <= (30 if leap_days == 30 else 29):
                    break
                lunar_day -= (30 if leap_days == 30 else 29)
        lunar_month = min(month, 12)
    else:
        # 简单估算：每月约29.5天
        lunar_month = min(int(days_since / 29.5) + 1, 12)
        lunar_day = days_since - int((lunar_month - 1) * 29.5) + 1

    return {
        "lunar_year": year,
        "lunar_month": lunar_month,
        "lunar_day": max(1, min(lunar_day, 30)),
        "is_lucky_day": lunar_day in LUCKY_DAYS,
        "is_estimate": False,
    }


def lunar_lucky_numbers(d: date = None, pool_max: int = 35) -> dict:
    """
    基于农历生成吉利数字权重

    Returns:
        {number: weight}
    """
    if d is None:
        d = date.today()

    lunar = estimate_lunar_date(d)
    lm = lunar["lunar_month"]
    ld = lunar["lunar_day"]

    weights = {}
    for n in range(1, pool_max + 1):
        weight = 1.0

        # 月份相关数字
        if n == lm or n % 10 == lm % 10:
            weight = 1.2

        # 日期相关数字
        if n == ld or n % 10 == ld % 10:
            weight = max(weight, 1.15)

        # 吉日加成
        if lunar["is_lucky_day"]:
            if n in [6, 8, 9, 16, 18, 28]:
                weight = max(weight, 1.25)

        # 数字谐音吉利
        if n in [6, 8, 9, 16, 18, 28, 66 % pool_max if pool_max > 66 else 6]:
            weight = max(weight, 1.1)

        weights[n] = round(weight, 2)

    return weights


def get_lunar_analysis(d: date = None) -> dict:
    """完整农历分析"""
    if d is None:
        d = date.today()

    lunar = estimate_lunar_date(d)
    month_names = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "腊"]
    day_names = {1: "初一", 2: "初二", 3: "初三", 15: "十五", 16: "十六", 30: "三十"}

    lm = lunar["lunar_month"]
    ld = lunar["lunar_day"]

    month_str = month_names[min(lm - 1, 11)]
    day_str = day_names.get(ld, f"第{ld}日")

    return {
        "lunar": lunar,
        "display": f"农历{month_str}月{day_str}",
        "is_lucky_day": lunar["is_lucky_day"],
        "lucky_desc": "今日为吉日，适宜选号" if lunar["is_lucky_day"] else "今日平常，宜稳健选号",
        "month_number": lm,
        "day_number": ld,
    }
