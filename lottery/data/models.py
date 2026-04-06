"""数据模型定义"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class DrawResult:
    """一期开奖结果"""
    period: str              # 期号 "2024001"
    date: str                # 日期 "2024-01-02"
    main_numbers: List[int]  # 主号码
    bonus_numbers: List[int] = field(default_factory=list)  # 附加号码

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(
            period=d["period"],
            date=d["date"],
            main_numbers=d["main_numbers"],
            bonus_numbers=d.get("bonus_numbers", []),
        )
