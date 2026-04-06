"""从 500.com XML 数据源抓取历史开奖数据"""

import re
import time
import xml.etree.ElementTree as ET
from typing import List, Optional

import requests

from lottery.config import HEADERS, LOTTERY_TYPES
from lottery.data.models import DrawResult


# XML 数据源（包含完整历史记录）
XML_URLS = {
    "ssq": "https://kaijiang.500.com/static/info/kaijiang/xml/ssq/list.xml",
    "dlt": "https://kaijiang.500.com/static/info/kaijiang/xml/dlt/list.xml",
    "qxc": "https://kaijiang.500.com/static/info/kaijiang/xml/qxc/list.xml",
    "kl8": "https://kaijiang.500.com/static/info/kaijiang/xml/kl8/list.xml",
}


def _fetch_xml(url: str, retries: int = 3) -> str:
    """带重试的 HTTP 请求"""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.encoding = "utf-8"
            if resp.status_code == 200:
                return resp.text
        except requests.RequestException:
            pass
        if attempt < retries - 1:
            time.sleep(2 * (attempt + 1))
    return ""


def _parse_ssq_row(row) -> Optional[DrawResult]:
    """解析双色球 XML 行: opencode="11,22,27,29,31,33|12" """
    try:
        period = row.get("expect", "")
        opencode = row.get("opencode", "")
        opentime = row.get("opentime", "")

        if "|" in opencode:
            main_str, bonus_str = opencode.split("|")
            main = [int(x) for x in main_str.split(",")]
            bonus = [int(x) for x in bonus_str.split(",")]
        else:
            return None

        date_str = opentime[:10] if opentime else ""

        return DrawResult(
            period=period,
            date=date_str,
            main_numbers=main,
            bonus_numbers=bonus,
        )
    except (ValueError, IndexError):
        return None


def _parse_dlt_row(row) -> Optional[DrawResult]:
    """解析大乐透 XML 行: opencode="02,22,30,33,34|08,12" """
    return _parse_ssq_row(row)  # 格式相同


def _parse_qxc_row(row) -> Optional[DrawResult]:
    """解析七星彩 XML 行: opencode="9,9,6,9,4,0,1" """
    try:
        period = row.get("expect", "")
        opencode = row.get("opencode", "")
        opentime = row.get("opentime", "")

        nums = [int(x) for x in opencode.split(",")]
        date_str = opentime[:10] if opentime else ""

        return DrawResult(
            period=period,
            date=date_str,
            main_numbers=nums,
            bonus_numbers=[],
        )
    except (ValueError, IndexError):
        return None


def _parse_kl8_row(row) -> Optional[DrawResult]:
    """解析快乐8 XML 行: opencode="01,03,04,11,..." (20个号码)"""
    try:
        period = row.get("expect", "")
        opencode = row.get("opencode", "")
        opentime = row.get("opentime", "")

        nums = [int(x) for x in opencode.split(",")]
        date_str = opentime[:10] if opentime else ""

        return DrawResult(
            period=period,
            date=date_str,
            main_numbers=nums,
            bonus_numbers=[],
        )
    except (ValueError, IndexError):
        return None


PARSERS = {
    "ssq": _parse_ssq_row,
    "dlt": _parse_dlt_row,
    "qxc": _parse_qxc_row,
    "kl8": _parse_kl8_row,
}


def fetch_history(lottery_code: str, start: str = None, end: str = None,
                  callback=None) -> List[DrawResult]:
    """
    从 XML 数据源抓取历史开奖数据

    Args:
        lottery_code: 彩票代码 ssq/dlt/qxc/kl8
        start: 起始期号（可选，用于过滤）
        callback: 进度回调 callback(message)
    """
    config = LOTTERY_TYPES[lottery_code]
    url = XML_URLS.get(lottery_code)
    parser = PARSERS[lottery_code]

    if not url:
        if callback:
            callback(f"  ❌ 不支持的彩票类型: {lottery_code}")
        return []

    if callback:
        callback(f"  正在下载 {config['name']} 数据...")

    xml_text = _fetch_xml(url)
    if not xml_text:
        if callback:
            callback(f"  ❌ 获取 {config['name']} 数据失败")
        return []

    # 解析 XML
    results = []
    try:
        root = ET.fromstring(xml_text)
        for row in root.findall("row"):
            result = parser(row)
            if result:
                # 过滤期号
                if start and result.period < start:
                    continue
                results.append(result)
    except ET.ParseError as e:
        if callback:
            callback(f"  ⚠️  XML 解析错误: {e}")
        return []

    # 按期号排序（XML 默认是倒序的）
    results.sort(key=lambda x: x.period)

    # 只保留最近10年的数据（大约从期号 16xxx 开始）
    if not start:
        # 过滤掉10年前的数据
        cutoff_year = "16"
        filtered = [r for r in results if r.period[:2] >= cutoff_year or len(r.period) > 5]
        if filtered:
            results = filtered

    if callback:
        callback(f"  ✅ {config['name']}: 获取到 {len(results)} 期数据")

    return results
