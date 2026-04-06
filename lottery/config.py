"""彩票类型定义和全局配置"""

import os
from pathlib import Path

# 缓存目录
CACHE_DIR = Path(os.path.expanduser("~/.lottery_cache"))

# ANSI 颜色
class Color:
    RED = "\033[91m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    BG_RED = "\033[41m"
    BG_BLUE = "\033[44m"


# 彩票类型配置
LOTTERY_TYPES = {
    "ssq": {
        "code": "ssq",
        "name": "双色球",
        "main_range": (1, 33),
        "main_count": 6,
        "bonus_range": (1, 16),
        "bonus_count": 1,
        "draw_days": [1, 3, 6],  # 周二、四、日 (0=周一)
        "url": "https://datachart.500.com/ssq/history/newinc/history.php",
    },
    "dlt": {
        "code": "dlt",
        "name": "大乐透",
        "main_range": (1, 35),
        "main_count": 5,
        "bonus_range": (1, 12),
        "bonus_count": 2,
        "draw_days": [0, 2, 5],  # 周一、三、六
        "url": "https://datachart.500.com/dlt/history/newinc/history.php",
    },
    "qxc": {
        "code": "qxc",
        "name": "七星彩",
        "positions": 7,  # 7个位置，每位0-9(前6位)，第7位0-14
        "position_ranges": [(0, 9)] * 6 + [(0, 14)],
        "main_range": (0, 9),
        "main_count": 7,
        "bonus_range": None,
        "bonus_count": 0,
        "draw_days": [1, 4],  # 周二、五
        "url": "https://datachart.500.com/qxc/history/newinc/history.php",
    },
    "kl8": {
        "code": "kl8",
        "name": "快乐8",
        "main_range": (1, 80),
        "main_count": 10,  # 用户选10个
        "draw_count": 20,  # 官方开20个
        "bonus_range": None,
        "bonus_count": 0,
        "draw_days": list(range(7)),  # 每天
        "url": "https://datachart.500.com/kl8/history/newinc/history.php",
    },
}

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
