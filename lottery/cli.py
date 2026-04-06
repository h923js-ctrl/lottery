"""CLI 命令行接口"""

import argparse
import sys
from datetime import date, datetime

from lottery.config import LOTTERY_TYPES, Color as C
from lottery.display import formatter as fmt


def cmd_update(args):
    """更新历史数据"""
    from lottery.data.updater import update_all, update_lottery

    fmt.header("📡 更新历史开奖数据")

    def progress(msg):
        print(msg)

    if args.type and args.type != "all":
        count = update_lottery(args.type, callback=progress)
        name = LOTTERY_TYPES[args.type]["name"]
        if count >= 0:
            fmt.success(f"{name}: 更新了 {count} 期数据")
        else:
            fmt.error(f"{name}: 更新失败")
    else:
        results = update_all(callback=progress)
        print()
        for code, count in results.items():
            name = LOTTERY_TYPES[code]["name"]
            if count >= 0:
                fmt.success(f"{name}: 更新了 {count} 期数据")
            else:
                fmt.error(f"{name}: 更新失败")

    print()
    fmt.info("数据缓存在 ~/.lottery_cache/")


def cmd_history(args):
    """显示最近开奖记录"""
    from lottery.data.storage import load_draws

    lottery_code = args.type or "ssq"
    config = LOTTERY_TYPES[lottery_code]
    draws = load_draws(lottery_code)

    if not draws:
        fmt.error(f"暂无 {config['name']} 数据，请先运行: python lottery.py update")
        return

    n = min(args.num or 20, len(draws))
    fmt.header(f"📋 {config['name']} 最近 {n} 期开奖记录")

    for d in draws[-n:]:
        date_str = f"{C.DIM}{d.date}{C.RESET}" if d.date else ""
        nums = fmt.format_numbers(lottery_code, d.main_numbers, d.bonus_numbers)
        print(f"  {C.BOLD}{d.period}{C.RESET}  {date_str}  {nums}")

    print()
    fmt.info(f"共有 {len(draws)} 期历史数据")


def cmd_stats(args):
    """统计分析"""
    from lottery.data.storage import load_draws
    from lottery.stats.frequency import hot_numbers, cold_numbers, number_frequency, recent_vs_overall
    from lottery.stats.gap import overdue_numbers, current_gap
    from lottery.stats.pattern import most_common_patterns
    from lottery.stats.sum_analysis import sum_statistics

    lottery_code = args.type or "ssq"
    config = LOTTERY_TYPES[lottery_code]
    draws = load_draws(lottery_code)

    if not draws:
        fmt.error(f"暂无 {config['name']} 数据，请先运行: python lottery.py update")
        return

    period = min(args.period or 100, len(draws))
    recent_draws = draws[-period:]
    pool_min, pool_max = config["main_range"]

    fmt.header(f"📊 {config['name']} 统计分析 (最近{period}期)")

    # 冷热号
    fmt.sub_header("冷热号分析")
    hot = hot_numbers(recent_draws, pool_min, pool_max, top_n=8)
    cold = cold_numbers(recent_draws, pool_min, pool_max, top_n=8)
    fmt.hot_cold_display(hot, cold)

    # 频率柱状图（显示前15个号码）
    fmt.sub_header("号码频率 (Top 15)")
    freq = number_frequency(recent_draws, pool_min, pool_max)
    max_freq = max(freq.values()) if freq else 1
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])[:15]
    for n, count in sorted_freq:
        color = C.RED if count > max_freq * 0.7 else (C.BLUE if count < max_freq * 0.3 else C.GREEN)
        fmt.bar_chart(f"{n:02d}", count, max_freq, color=color)
    print()

    # 遗漏分析
    fmt.sub_header("遗漏值分析 (超期号码)")
    overdue = overdue_numbers(recent_draws, pool_min, pool_max)
    if overdue:
        for item in overdue[:8]:
            n = item["number"]
            gap = item["current_gap"]
            avg = item["avg_gap"]
            ratio = item["overdue_ratio"]
            color = C.RED if ratio > 2 else C.YELLOW
            print(f"  {color}{n:02d}{C.RESET}: 当前遗漏 {gap} 期 (平均 {avg:.0f} 期, 超出 {ratio}x)")
    else:
        fmt.info("暂无明显超期号码")
    print()

    # 奇偶/大小分布
    if lottery_code != "qxc":
        fmt.sub_header("模式分析")
        patterns = most_common_patterns(recent_draws, pool_max)

        print(f"  奇偶比分布:")
        for k, v in list(patterns["odd_even"].items())[:5]:
            print(f"    {k}: {C.CYAN}{v}%{C.RESET}")

        print(f"  大小比分布:")
        for k, v in list(patterns["high_low"].items())[:5]:
            print(f"    {k}: {C.CYAN}{v}%{C.RESET}")

        cons = patterns["consecutive"]
        print(f"  连号出现率: {C.YELLOW}{cons['consecutive_rate']}%{C.RESET}")
        print()

    # 和值分析
    fmt.sub_header("和值分析")
    sum_stats = sum_statistics(recent_draws)
    if sum_stats:
        print(f"  平均和值: {C.BOLD}{sum_stats['mean']}{C.RESET}")
        print(f"  和值范围: {sum_stats['min']} ~ {sum_stats['max']}")
        print(f"  推荐范围: {C.GREEN}{sum_stats['q1']} ~ {sum_stats['q3']}{C.RESET} (IQR)")
        print(f"  最近10期均值: {sum_stats['recent_10_avg']}")
    print()


def cmd_xuanxue(args):
    """今日玄学分析"""
    from lottery.xuanxue.wuxing import get_wuxing_analysis, get_day_ganzhi
    from lottery.xuanxue.shengxiao import get_shengxiao_analysis
    from lottery.xuanxue.bagua import get_bagua_analysis
    from lottery.xuanxue.lunar import get_lunar_analysis
    from lottery.xuanxue.fengshui import get_fengshui_analysis

    today = date.today()
    fmt.header(f"🔮 今日玄学分析 ({today.strftime('%Y-%m-%d')})")

    # 五行
    fmt.sub_header(fmt.xuanxue_icon("wuxing"))
    wx = get_wuxing_analysis(today)
    tg, dz = get_day_ganzhi(today)
    print(f"  今日干支: {C.BOLD}{tg}{dz}{C.RESET}")
    print(f"  今日五行: {C.YELLOW}{C.BOLD}{wx['today_element']}{C.RESET}")
    print(f"  {wx['element_desc']}")
    lucky_t = ", ".join(str(n) for n in wx["lucky_tails"])
    avoid_t = ", ".join(str(n) for n in wx["avoid_tails"])
    print(f"  吉利尾数: {C.GREEN}{lucky_t}{C.RESET}")
    print(f"  不利尾数: {C.RED}{avoid_t}{C.RESET}")
    print()

    # 生肖
    fmt.sub_header(fmt.xuanxue_icon("shengxiao"))
    sx = get_shengxiao_analysis(today)
    print(f"  {sx['desc']}")
    lucky_n = ", ".join(str(n) for n in sx["lucky_numbers"])
    print(f"  吉利数字: {C.GREEN}{lucky_n}{C.RESET}")
    warn_n = ", ".join(str(n) for n in sx["chong_warn"])
    print(f"  注意避免: {C.RED}{warn_n}{C.RESET}")
    print()

    # 八卦
    fmt.sub_header(fmt.xuanxue_icon("bagua"))
    bg = get_bagua_analysis(today)
    print(f"  {bg['desc']}")
    print(f"  {bg['upper_desc']}")
    print(f"  {bg['lower_desc']}")
    gua_nums = ", ".join(str(n) for n in bg["lucky_numbers"][:10])
    print(f"  卦象吉数: {C.GREEN}{gua_nums}{C.RESET}")
    print()

    # 农历
    fmt.sub_header(fmt.xuanxue_icon("lunar"))
    ln = get_lunar_analysis(today)
    print(f"  {ln['display']}")
    print(f"  {ln['lucky_desc']}")
    print()

    # 风水
    fmt.sub_header(fmt.xuanxue_icon("fengshui"))
    fs = get_fengshui_analysis()
    print(f"  {fs['desc']}")
    great = ", ".join(f"{n:02d}" for n in fs["great_lucky"][:10])
    print(f"  大吉号码: {C.GREEN}{great}{C.RESET}")
    avoid = ", ".join(f"{n:02d}" for n in fs["avoid"][:10])
    print(f"  建议避免: {C.RED}{avoid}{C.RESET}")
    print()


def cmd_pick(args):
    """智能选号"""
    from lottery.data.storage import load_draws
    from lottery.engine.generator import generate_multiple
    from lottery.engine.recommender import MODES

    lottery_code = args.type or "ssq"
    config = LOTTERY_TYPES[lottery_code]
    mode = args.mode or "balanced"
    count = args.num or 5
    today = date.today()

    draws = load_draws(lottery_code)

    if not draws and mode != "random":
        fmt.warning(f"暂无历史数据，将使用随机模式。运行 'python lottery.py update' 获取数据")
        mode = "random"

    mode_info = MODES.get(mode, MODES["balanced"])
    fmt.header(f"🎯 {config['name']} 智能选号")

    print(f"  📅 日期: {today.strftime('%Y-%m-%d')}")
    print(f"  🎲 模式: {C.CYAN}{mode_info['name']}{C.RESET} ({mode_info['desc']})")
    if draws:
        print(f"  📊 数据: {len(draws)} 期历史记录")
    print()

    # 生成号码
    results = generate_multiple(draws, lottery_code, count, mode, today)

    fmt.sub_header("推荐号码")
    for i, r in enumerate(results, 1):
        nums_str = fmt.format_numbers(lottery_code, r["main"], r["bonus"])
        # 评分
        avg_score = sum(r["main_scores"].values()) / len(r["main_scores"]) if r["main_scores"] else 0
        stars = "★" * min(int(avg_score * 10), 5)
        print(f"  第{i}注: {nums_str}  {C.YELLOW}{stars}{C.RESET}")

    print()

    # 简要玄学提示
    if mode in ("xuanxue", "balanced"):
        from lottery.xuanxue.wuxing import get_wuxing_analysis
        from lottery.xuanxue.shengxiao import get_shengxiao_analysis

        wx = get_wuxing_analysis(today)
        sx = get_shengxiao_analysis(today)

        fmt.sub_header("玄学提示")
        print(f"  ☯️  今日五行{C.BOLD}{wx['today_element']}{C.RESET}，{wx['element_desc']}")
        print(f"  🐉 {sx['desc']}")
        print()

    fmt.warning("本工具仅供娱乐，号码基于统计和随机生成，不构成投注建议。")
    fmt.info("理性购彩，量力而行。")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="🎰 彩票智能选号工具 - 统计分析 + 玄学辅助",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令示例:
  python lottery.py update              下载/更新历史数据
  python lottery.py pick -t ssq -n 5    双色球智能选号5注
  python lottery.py pick -t dlt -m xuanxue  大乐透玄学模式
  python lottery.py stats -t ssq        双色球统计分析
  python lottery.py xuanxue             今日玄学分析
  python lottery.py history -t dlt      大乐透最近开奖
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # update
    p_update = subparsers.add_parser("update", help="下载/更新历史数据")
    p_update.add_argument("-t", "--type", choices=list(LOTTERY_TYPES.keys()) + ["all"],
                          default="all", help="彩票类型")

    # pick
    p_pick = subparsers.add_parser("pick", help="智能选号")
    p_pick.add_argument("-t", "--type", choices=list(LOTTERY_TYPES.keys()),
                        default="ssq", help="彩票类型 (默认: ssq)")
    p_pick.add_argument("-n", "--num", type=int, default=5, help="生成注数 (默认: 5)")
    p_pick.add_argument("-m", "--mode", choices=["stats", "xuanxue", "balanced", "random"],
                        default="balanced", help="推荐模式 (默认: balanced)")

    # stats
    p_stats = subparsers.add_parser("stats", help="统计分析")
    p_stats.add_argument("-t", "--type", choices=list(LOTTERY_TYPES.keys()),
                         default="ssq", help="彩票类型")
    p_stats.add_argument("-p", "--period", type=int, default=100, help="分析最近N期")

    # xuanxue
    p_xuan = subparsers.add_parser("xuanxue", help="今日玄学分析")

    # history
    p_hist = subparsers.add_parser("history", help="最近开奖记录")
    p_hist.add_argument("-t", "--type", choices=list(LOTTERY_TYPES.keys()),
                        default="ssq", help="彩票类型")
    p_hist.add_argument("-n", "--num", type=int, default=20, help="显示条数")

    args = parser.parse_args()

    if not args.command:
        # 无命令时进入交互模式
        interactive_mode()
        return

    commands = {
        "update": cmd_update,
        "pick": cmd_pick,
        "stats": cmd_stats,
        "xuanxue": cmd_xuanxue,
        "history": cmd_history,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        parser.print_help()


def interactive_mode():
    """交互式菜单"""
    fmt.header("🎰 彩票智能选号工具 v2.0")

    print(f"  {C.BOLD}请选择操作:{C.RESET}")
    print(f"  1. 🎯 智能选号")
    print(f"  2. 📊 统计分析")
    print(f"  3. 🔮 今日玄学")
    print(f"  4. 📋 开奖记录")
    print(f"  5. 📡 更新数据")
    print(f"  0. 退出")
    print()

    try:
        choice = input(f"  请输入选项: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice == "0":
        return

    if choice == "1":
        _interactive_pick()
    elif choice == "2":
        _interactive_stats()
    elif choice == "3":
        args = argparse.Namespace()
        cmd_xuanxue(args)
    elif choice == "4":
        _interactive_history()
    elif choice == "5":
        args = argparse.Namespace(type="all")
        cmd_update(args)
    else:
        print(f"  {C.RED}无效选项{C.RESET}")


def _choose_lottery() -> str:
    """选择彩票类型"""
    print()
    print(f"  {C.BOLD}选择彩票:{C.RESET}")
    codes = list(LOTTERY_TYPES.keys())
    for i, code in enumerate(codes, 1):
        name = LOTTERY_TYPES[code]["name"]
        print(f"  {i}. {name}")
    print()
    try:
        idx = int(input("  请输入 (1-4): ").strip()) - 1
        return codes[idx] if 0 <= idx < len(codes) else "ssq"
    except (ValueError, EOFError, KeyboardInterrupt):
        return "ssq"


def _interactive_pick():
    code = _choose_lottery()
    print()
    print(f"  {C.BOLD}选择模式:{C.RESET}")
    print(f"  1. 平衡模式 (统计60% + 玄学40%)")
    print(f"  2. 统计模式 (纯数据分析)")
    print(f"  3. 玄学模式 (以玄学为主)")
    print(f"  4. 随机模式")
    print()
    try:
        m = input("  请输入 (默认1): ").strip() or "1"
        modes = {"1": "balanced", "2": "stats", "3": "xuanxue", "4": "random"}
        mode = modes.get(m, "balanced")
    except (EOFError, KeyboardInterrupt):
        mode = "balanced"

    try:
        n = input("  生成几注? (默认5): ").strip() or "5"
        num = int(n)
    except (ValueError, EOFError, KeyboardInterrupt):
        num = 5

    args = argparse.Namespace(type=code, mode=mode, num=num)
    cmd_pick(args)


def _interactive_stats():
    code = _choose_lottery()
    try:
        p = input("  分析最近几期? (默认100): ").strip() or "100"
        period = int(p)
    except (ValueError, EOFError, KeyboardInterrupt):
        period = 100

    args = argparse.Namespace(type=code, period=period)
    cmd_stats(args)


def _interactive_history():
    code = _choose_lottery()
    try:
        n = input("  显示几条? (默认20): ").strip() or "20"
        num = int(n)
    except (ValueError, EOFError, KeyboardInterrupt):
        num = 20

    args = argparse.Namespace(type=code, num=num)
    cmd_history(args)
