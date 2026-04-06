"""五行分析 - 天干地支 → 金木水火土 → 数字映射"""

from datetime import datetime, date

# 天干
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干对应五行
TIAN_GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 地支对应五行
DI_ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 河图数字：五行对应数字
# 一六为水，二七为火，三八为木，四九为金，五十为土
WUXING_NUMBERS = {
    "水": [1, 6],
    "火": [2, 7],
    "木": [3, 8],
    "金": [4, 9],
    "土": [5, 0],  # 0代表10的尾数
}

# 五行生克关系
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 生
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}    # 克


def _days_from_base(d: date) -> int:
    """计算从基准日(甲子日)的天数差"""
    # 2000年1月7日是甲子日
    base = date(2000, 1, 7)
    return (d - base).days


def get_day_ganzhi(d: date = None) -> tuple:
    """获取某天的天干地支"""
    if d is None:
        d = date.today()
    days = _days_from_base(d)
    tg = TIAN_GAN[days % 10]
    dz = DI_ZHI[days % 12]
    return tg, dz


def get_year_ganzhi(year: int) -> tuple:
    """获取年份的天干地支"""
    # 2000年是庚辰年
    tg = TIAN_GAN[(year - 4) % 10]
    dz = DI_ZHI[(year - 4) % 12]
    return tg, dz


def get_day_wuxing(d: date = None) -> dict:
    """
    获取当日五行信息

    Returns:
        {
            "ganzhi": "甲子",
            "tian_gan": "甲",
            "di_zhi": "子",
            "tg_wuxing": "木",
            "dz_wuxing": "水",
            "dominant": "木",  # 以天干为主
        }
    """
    tg, dz = get_day_ganzhi(d)
    return {
        "ganzhi": tg + dz,
        "tian_gan": tg,
        "di_zhi": dz,
        "tg_wuxing": TIAN_GAN_WUXING[tg],
        "dz_wuxing": DI_ZHI_WUXING[dz],
        "dominant": TIAN_GAN_WUXING[tg],
    }


def wuxing_lucky_numbers(d: date = None, pool_max: int = 35) -> dict:
    """
    基于五行生成吉利数字权重

    Returns:
        {number: weight} 权重范围 0.7 ~ 1.5
    """
    info = get_day_wuxing(d)
    dominant = info["dominant"]
    sheng_element = WUXING_SHENG[dominant]  # 今日五行所生的元素
    ke_element = WUXING_KE[dominant]        # 今日五行所克的元素

    weights = {}
    for n in range(pool_max + 1):
        tail = n % 10
        weight = 1.0

        # 本行数字：大吉
        if tail in WUXING_NUMBERS[dominant]:
            weight = 1.4

        # 所生元素的数字：吉
        elif tail in WUXING_NUMBERS[sheng_element]:
            weight = 1.2

        # 生我元素的数字：次吉
        for wx, target in WUXING_SHENG.items():
            if target == dominant and tail in WUXING_NUMBERS[wx]:
                weight = max(weight, 1.15)

        # 所克元素的数字：不利
        if tail in WUXING_NUMBERS[ke_element]:
            weight = 0.8

        # 克我元素的数字：最不利
        for wx, target in WUXING_KE.items():
            if target == dominant and tail in WUXING_NUMBERS[wx]:
                weight = min(weight, 0.75)

        if n > 0:  # 跳过0
            weights[n] = round(weight, 2)

    return weights


def get_wuxing_analysis(d: date = None) -> dict:
    """完整的五行分析"""
    info = get_day_wuxing(d)
    dominant = info["dominant"]

    return {
        "info": info,
        "today_element": dominant,
        "element_desc": {
            "木": "木主仁，生发之气。宜选尾数3、8",
            "火": "火主礼，光明之气。宜选尾数2、7",
            "土": "土主信，厚重之气。宜选尾数5、0",
            "金": "金主义，肃杀之气。宜选尾数4、9",
            "水": "水主智，灵动之气。宜选尾数1、6",
        }[dominant],
        "lucky_tails": WUXING_NUMBERS[dominant],
        "sheng_tails": WUXING_NUMBERS[WUXING_SHENG[dominant]],
        "avoid_tails": WUXING_NUMBERS[WUXING_KE[dominant]],
    }
