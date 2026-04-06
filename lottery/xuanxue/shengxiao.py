"""生肖分析"""

from datetime import date

# 地支对应生肖
DIZHI_SHENGXIAO = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
    "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪",
}

# 生肖吉利数字
SHENGXIAO_LUCKY = {
    "鼠": [2, 3, 8],
    "牛": [1, 4, 9],
    "虎": [1, 3, 4],
    "兔": [3, 4, 6],
    "龙": [1, 6, 7],
    "蛇": [2, 8, 9],
    "马": [2, 3, 7],
    "羊": [2, 7, 8],
    "猴": [4, 9, 8],
    "鸡": [5, 7, 8],
    "狗": [3, 4, 9],
    "猪": [2, 5, 8],
}

# 六合关系（最佳搭档）
LIUHE = {
    "鼠": "牛", "牛": "鼠", "虎": "猪", "兔": "狗",
    "龙": "鸡", "蛇": "猴", "马": "羊", "羊": "马",
    "猴": "蛇", "鸡": "龙", "狗": "兔", "猪": "虎",
}

# 三合局
SANHE = {
    "鼠": ["龙", "猴"], "牛": ["蛇", "鸡"], "虎": ["马", "狗"], "兔": ["羊", "猪"],
    "龙": ["鼠", "猴"], "蛇": ["牛", "鸡"], "马": ["虎", "狗"], "羊": ["兔", "猪"],
    "猴": ["鼠", "龙"], "鸡": ["牛", "蛇"], "狗": ["虎", "马"], "猪": ["兔", "虎"],
}

# 相冲关系（不利）
XIANGCHONG = {
    "鼠": "马", "牛": "羊", "虎": "猴", "兔": "鸡",
    "龙": "狗", "蛇": "猪", "马": "鼠", "羊": "牛",
    "猴": "虎", "鸡": "兔", "狗": "龙", "猪": "蛇",
}


def get_year_shengxiao(year: int) -> str:
    """获取年份的生肖"""
    animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    return animals[(year - 4) % 12]


def shengxiao_lucky_numbers(d: date = None, pool_max: int = 35) -> dict:
    """
    基于生肖生成吉利数字权重

    Returns:
        {number: weight}
    """
    if d is None:
        d = date.today()

    animal = get_year_shengxiao(d.year)
    lucky_digits = SHENGXIAO_LUCKY[animal]

    # 六合生肖的吉数
    liuhe_animal = LIUHE[animal]
    liuhe_digits = SHENGXIAO_LUCKY[liuhe_animal]

    # 三合生肖的吉数
    sanhe_animals = SANHE[animal]
    sanhe_digits = set()
    for a in sanhe_animals:
        sanhe_digits.update(SHENGXIAO_LUCKY[a])

    # 相冲生肖的数字（不利）
    chong_animal = XIANGCHONG[animal]
    chong_digits = SHENGXIAO_LUCKY[chong_animal]

    weights = {}
    for n in range(1, pool_max + 1):
        tail = n % 10
        weight = 1.0

        if tail in lucky_digits:
            weight = 1.3
        if tail in liuhe_digits:
            weight = max(weight, 1.2)
        if tail in sanhe_digits:
            weight = max(weight, 1.1)
        if tail in chong_digits:
            weight = min(weight, 0.85)

        weights[n] = round(weight, 2)

    return weights


def get_shengxiao_analysis(d: date = None) -> dict:
    """完整生肖分析"""
    if d is None:
        d = date.today()

    animal = get_year_shengxiao(d.year)

    return {
        "year": d.year,
        "animal": animal,
        "lucky_numbers": SHENGXIAO_LUCKY[animal],
        "liuhe": LIUHE[animal],
        "liuhe_lucky": SHENGXIAO_LUCKY[LIUHE[animal]],
        "sanhe": SANHE[animal],
        "chong": XIANGCHONG[animal],
        "chong_warn": SHENGXIAO_LUCKY[XIANGCHONG[animal]],
        "desc": f"{d.year}年为{animal}年，与{LIUHE[animal]}六合，与{'/'.join(SANHE[animal])}三合，冲{XIANGCHONG[animal]}",
    }
