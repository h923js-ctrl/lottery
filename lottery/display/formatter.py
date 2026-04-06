"""终端彩色输出格式化"""

from lottery.config import Color as C


def header(text: str, width: int = 56):
    """打印标题框"""
    print()
    print(f"  {C.BOLD}╔{'═' * width}╗{C.RESET}")
    padded = text.center(width)
    print(f"  {C.BOLD}║{C.YELLOW}{padded}{C.RESET}{C.BOLD}║{C.RESET}")
    print(f"  {C.BOLD}╚{'═' * width}╝{C.RESET}")
    print()


def sub_header(text: str):
    """子标题"""
    print(f"  {C.BOLD}{C.CYAN}▸ {text}{C.RESET}")
    print(f"  {C.DIM}{'─' * 50}{C.RESET}")


def bar_chart(label: str, value: int, max_value: int, width: int = 30,
              color: str = C.GREEN):
    """水平柱状图"""
    if max_value <= 0:
        max_value = 1
    filled = int(value / max_value * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:>4s}: {color}{bar}{C.RESET} {value}")


def format_ssq(main: list, bonus: list) -> str:
    """格式化双色球号码"""
    red = " ".join(f"{C.RED}{C.BOLD}{n:02d}{C.RESET}" for n in main)
    blue = " ".join(f"{C.BLUE}{C.BOLD}{n:02d}{C.RESET}" for n in bonus)
    return f"  {red}  {blue}"


def format_dlt(main: list, bonus: list) -> str:
    """格式化大乐透号码"""
    front = " ".join(f"{C.RED}{C.BOLD}{n:02d}{C.RESET}" for n in main)
    back = " ".join(f"{C.BLUE}{C.BOLD}{n:02d}{C.RESET}" for n in bonus)
    return f"  {front}  {back}"


def format_qxc(main: list) -> str:
    """格式化七星彩号码"""
    nums = " ".join(f"{C.YELLOW}{C.BOLD}{n}{C.RESET}" for n in main)
    return f"  {nums}"


def format_kl8(main: list) -> str:
    """格式化快乐8号码"""
    nums = " ".join(f"{C.MAGENTA}{C.BOLD}{n:02d}{C.RESET}" for n in main)
    return f"  {nums}"


def format_numbers(lottery_code: str, main: list, bonus: list = None) -> str:
    """根据彩票类型格式化号码"""
    if bonus is None:
        bonus = []
    formatters = {
        "ssq": lambda: format_ssq(main, bonus),
        "dlt": lambda: format_dlt(main, bonus),
        "qxc": lambda: format_qxc(main),
        "kl8": lambda: format_kl8(main),
    }
    return formatters.get(lottery_code, lambda: str(main))()


def hot_cold_display(hot: list, cold: list):
    """显示冷热号"""
    hot_str = " ".join(f"{C.RED}{C.BOLD}{n:02d}{C.RESET}" for n, _ in hot)
    cold_str = " ".join(f"{C.BLUE}{n:02d}{C.RESET}" for n, _ in cold)
    print(f"  🔥 热号: {hot_str}")
    print(f"  ❄️  冷号: {cold_str}")
    print()


def score_display(number: int, score: float, max_score: float = 1.0):
    """显示号码评分"""
    pct = int(score / max_score * 10)
    stars = "★" * pct + "☆" * (10 - pct)
    print(f"  {C.BOLD}{number:02d}{C.RESET} {C.YELLOW}{stars}{C.RESET} {score:.3f}")


def divider():
    print(f"  {C.DIM}{'─' * 50}{C.RESET}")


def info(text: str):
    print(f"  {C.DIM}{text}{C.RESET}")


def success(text: str):
    print(f"  {C.GREEN}✅ {text}{C.RESET}")


def warning(text: str):
    print(f"  {C.YELLOW}⚠️  {text}{C.RESET}")


def error(text: str):
    print(f"  {C.RED}❌ {text}{C.RESET}")


def xuanxue_icon(module: str) -> str:
    """玄学模块图标"""
    icons = {
        "wuxing": "☯️  五行",
        "shengxiao": "🐉 生肖",
        "bagua": "☰  八卦",
        "lunar": "🌙 农历",
        "fengshui": "🧭 风水",
    }
    return icons.get(module, module)
