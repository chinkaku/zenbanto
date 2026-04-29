"""
番种计算模块 - 接口预留

本文件用于补充"全番斗"的具体番种计算规则。
框架会调用 calculate_fan_and_score() 函数来获取分数。

示例番种（待补充）：
- 小和：1番
- 中和：2番
- 大和：3番
- 等等...

"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Fan:
    """番种"""
    name: str
    value: int  # 番数


def calculate_fan_and_score(
    hand: List,  # Tile列表
    melds: List,  # MeldSet列表
    win_type: str,  # "标准和" / "七对" / "十三幺"
    winner_role,  # PlayerRole
    dealer_role,  # PlayerRole
    is_self_draw: bool
) -> Tuple[int, int]:
    """
    计算和牌的番数和分数
    
    参数：
    - hand: 玩家的手牌（List[Tile]）
    - melds: 玩家的副露（List[MeldSet]）
    - win_type: 和牌类型
    - winner_role: 赢家位置
    - dealer_role: 庄家位置
    - is_self_draw: 是否自摸
    
    返回：
    - (番数, 分数)
    
    示例实现：
    """
    # TODO: 补充具体的番种判定逻辑
    
    # 暂时返回默认值
    if is_self_draw and winner_role == dealer_role:
        return (1, 8)  # 庄家自摸：1番，8分
    elif is_self_draw:
        return (1, 4)  # 闲家自摸：1番，4分
    else:
        return (1, 4)  # 其他：1番，4分


# 以下是可能需要用到的辅助函数框架

def check_dragon_pung(hand: List, melds: List) -> bool:
    """检查是否有龙刻（中发白之一的三张刻子）"""
    # TODO: 实现
    pass


def check_wind_pung(hand: List, melds: List) -> bool:
    """检查是否有风刻"""
    # TODO: 实现
    pass


def check_all_sequences(hand: List, melds: List) -> bool:
    """检查是否全是顺子"""
    # TODO: 实现
    pass


def check_all_pungs(hand: List, melds: List) -> bool:
    """检查是否全是刻子"""
    # TODO: 实现
    pass


def check_terminal_or_honour_only(hand: List, melds: List) -> bool:
    """检查是否全是幺九牌和字牌"""
    # TODO: 实现
    pass


def count_melds_of_type(melds: List, meld_type: str) -> int:
    """统计特定类型的副露数量"""
    # TODO: 实现
    pass


# 其他番种检查函数可在此添加...
