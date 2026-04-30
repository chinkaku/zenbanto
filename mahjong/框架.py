"""
全番斗麻将框架
单人游戏 + 3个AI
AI：不鸣牌，每次打摸上来的牌
"""

from enum import Enum
from typing import List, Optional, Set, Tuple
import random
from dataclasses import dataclass, field
from collections import Counter


# ==================== 基础定义 ====================

class TileType(Enum):
    """牌的类型"""
    MAN = 'm'      # 万
    PIN = 'p'      # 筒
    SOU = 's'      # 条
    HONOUR = 'z'   # 字牌


@dataclass(frozen=True)
class Tile:
    """麻将牌"""
    tile_type: TileType
    rank: int  # 1-9（数牌）或 0-6（字牌：东南西北中发白）
    
    def __str__(self):
        if self.tile_type == TileType.HONOUR:
            honour_names = ['东', '南', '西', '北', '中', '发', '白']
            return honour_names[self.rank] if 0 <= self.rank < 7 else '?'
        else:
            type_names = {'m': '万', 'p': '筒', 's': '条'}
            return f"{self.rank}{type_names[self.tile_type.value]}"
    
    def to_shorthand(self) -> str:
        """返回牌的简称"""
        if self.tile_type == TileType.MAN:
            return f"{self.rank}m"
        elif self.tile_type == TileType.PIN:
            return f"{self.rank}p"
        elif self.tile_type == TileType.SOU:
            return f"{self.rank}s"
        elif self.tile_type == TileType.HONOUR:
            honour_shorthand = ['E', 'S', 'W', 'N', 'C', 'F', 'P']
            return honour_shorthand[self.rank] if 0 <= self.rank < 7 else '?'
        return '?'
    
    def is_terminal_or_honour(self) -> bool:
        """是否为幺九牌或字牌（用于十三幺判定）"""
        if self.tile_type == TileType.HONOUR:
            return True
        return self.rank in [1, 9]


class PlayerRole(Enum):
    """玩家位置"""
    EAST = "东"
    SOUTH = "南"
    WEST = "西"
    NORTH = "北"


class PlayerType(Enum):
    """玩家类型"""
    HUMAN = "人类"
    AI = "AI"


@dataclass
class MeldSet:
    """一组副露牌"""
    tiles: List[Tile]
    meld_type: str  # 'CHOW'(吃), 'PUNG'(碰), 'KONG'(杠), 'DARK_KONG'(暗杠)
    hidden_count: int = 0  # 暗置的牌数（暗杠用）


# ==================== 牌山管理 ====================

class TileWall:
    """牌山"""
    
    def __init__(self):
        self.tiles: List[Tile] = []
        self.head_idx = 0
        self.tail_idx = -1
    
    def initialize(self):
        """初始化牌山"""
        self.tiles = []
        
        # 创建一副标准麻将牌（34种 × 4张）
        for tile_type in [TileType.MAN, TileType.PIN, TileType.SOU]:
            for rank in range(1, 10):
                for _ in range(4):
                    self.tiles.append(Tile(tile_type, rank))
        
        # 字牌：东南西北中发白
        for rank in range(7):
            for _ in range(4):
                self.tiles.append(Tile(TileType.HONOUR, rank))
        
        random.shuffle(self.tiles)
        self.head_idx = 0
        self.tail_idx = len(self.tiles) - 1
    
    def draw_from_head(self) -> Optional[Tile]:
        """从牌山头摸牌"""
        if self.head_idx <= self.tail_idx:
            tile = self.tiles[self.head_idx]
            self.head_idx += 1
            return tile
        return None
    
    def draw_from_tail(self) -> Optional[Tile]:
        """从牌山尾摸牌（杠后摸）"""
        if self.head_idx <= self.tail_idx:
            tile = self.tiles[self.tail_idx]
            self.tail_idx -= 1
            return tile
        return None
    
    def is_empty(self) -> bool:
        """检查牌山是否为空"""
        return self.head_idx > self.tail_idx
    
    def remaining_count(self) -> int:
        """剩余牌数"""
        return max(0, self.tail_idx - self.head_idx + 1)


# ==================== 玩家类 ====================

class Player:
    """玩家"""
    
    def __init__(self, role: PlayerRole, player_type: PlayerType):
        self.role = role
        self.player_type = player_type
        self.hand: List[Tile] = []  # 手牌（不包括副露）
        self.melds: List[MeldSet] = []  # 副露
        self.status_flag: Optional[str] = None  # 状态标：None, 'MELD', 'KONG'
        self.discards: List[Tile] = []  # 打出的牌
        self.score = 0
        self.rank = 0
    
    def add_tile(self, tile: Tile):
        """添加一张牌到手牌"""
        self.hand.append(tile)
    
    def remove_tile(self, tile: Tile) -> bool:
        """从手牌移除一张牌"""
        if tile in self.hand:
            self.hand.remove(tile)
            return True
        return False
    
    def discard_tile(self, tile: Tile):
        """打出一张牌"""
        if self.remove_tile(tile):
            self.discards.append(tile)
    
    def add_meld(self, meld: MeldSet):
        """添加一组副露"""
        self.melds.append(meld)
    
    def get_all_tiles(self) -> List[Tile]:
        """获取所有牌（手牌+副露）"""
        all_tiles = self.hand.copy()
        for meld in self.melds:
            all_tiles.extend(meld.tiles)
        return all_tiles
    
    def __str__(self):
        return f"{self.role.value}({self.player_type.value})"


# ==================== 和牌判定 ====================

def is_winning_hand(hand: List[Tile], melds: List[MeldSet]) -> Tuple[bool, str]:
    """
    检查是否为和牌（标准和牌、七对、十三幺）
    返回 (是否和牌, 和牌类型)
    
    通过将手牌和副露组合成一个完整的牌列表，判断是否达到14张和牌。
    副露中的面子已经是确定的面子，因此直接计入总牌数。
    """
    total_tiles = hand + sum([meld.tiles for meld in melds], [])
    
    # 14张牌（含暗杠）
    if len(total_tiles) != 14:
        return False, ""
    
    # 特殊和牌检查：十三幺只能在无副露时成立
    if check_thirteen_orphans(total_tiles, melds):
        return True, "十三幺"
    
    # 七对只能在无副露时成立
    if check_seven_pairs(hand, melds):
        return True, "七对"
    
    # 标准和牌检查，考虑副露的面子数量
    if check_standard_win(hand, melds):
        return True, "标准和"
    
    return False, ""


def check_standard_win(hand: List[Tile], melds: List[MeldSet]) -> bool:
    """
    检查标准和牌（4个面子+1个雀头）

    副露（melds）中的牌已经组成了面子，计入总的14张和牌。
    规则：4个面子 + 1个对子 = 14张。
    """
    total_tiles = hand + sum([meld.tiles for meld in melds], [])
    if len(total_tiles) != 14:
        return False
    
    # 副露中的面子数量，已经固定不需要重新判断
    meld_count = len(melds)
    needed_melds = 4 - meld_count
    needed_tiles = 3 * needed_melds + 2  # 剩余手牌需要组成的牌数
    
    # 手牌数量必须恰好匹配剩余待组成面子与雀头的要求
    if len(hand) != needed_tiles:
        return False
    
    tile_count = Counter(hand)
    
    # 遍历所有可能的对子作为雀头
    for pair_tile in tile_count:
        if tile_count[pair_tile] >= 2:
            remaining = hand.copy()
            remaining.remove(pair_tile)
            remaining.remove(pair_tile)
            
            # 剩余牌是否能组成所需数量的面子
            if can_form_melds(remaining, needed_melds):
                return True
    
    return False


def check_seven_pairs(hand: List[Tile], melds: List[MeldSet]) -> bool:
    """检查七对"""
    # 七对不能有副露（副露会破坏对子的结构）
    if len(melds) > 0:
        return False
    
    if len(hand) != 14:
        return False
    
    tile_count = Counter(hand)
    
    # 应该有7个对子，每个对子2张，共14张
    pair_count = sum(1 for count in tile_count.values() if count == 2)
    
    return pair_count == 7 and len(tile_count) == 7


def check_thirteen_orphans(tiles: List[Tile], melds: List[MeldSet]) -> bool:
    """检查十三幺"""
    # 十三幺不能有副露
    if len(melds) > 0:
        return False
    
    if len(tiles) != 14:
        return False
    
    # 十三幺：13种幺九牌各1张 + 其中一种2张
    orphan_tiles = [
        Tile(TileType.MAN, 1), Tile(TileType.MAN, 9),
        Tile(TileType.PIN, 1), Tile(TileType.PIN, 9),
        Tile(TileType.SOU, 1), Tile(TileType.SOU, 9),
        Tile(TileType.HONOUR, 0), Tile(TileType.HONOUR, 1),
        Tile(TileType.HONOUR, 2), Tile(TileType.HONOUR, 3),
        Tile(TileType.HONOUR, 4), Tile(TileType.HONOUR, 5),
        Tile(TileType.HONOUR, 6),
    ]
    
    tile_count = Counter(tiles)
    
    # 检查是否包含所有13种幺九牌
    for orphan in orphan_tiles:
        if tile_count[orphan] == 0:
            return False
    
    # 检查是否恰好14张（13种各1张，其中1种2张）
    pair_count = sum(1 for count in tile_count.values() if count == 2)
    return pair_count == 1 and len(tile_count) == 13


def can_form_melds(tiles: List[Tile], meld_count: int) -> bool:
    """检查是否能组成指定数量的面子"""
    # 如果不再需要构成面子，则检查是否已经把所有牌用完
    if meld_count == 0:
        return len(tiles) == 0
    
    # 面子至少需要3张牌
    if len(tiles) < 3:
        return False
    
    tile_count = Counter(tiles)
    # 从最小的一张牌开始尝试构造面子，避免排列重复
    first_tile = min(tile_count.keys(), key=lambda t: (t.tile_type.value, t.rank))
    
    # 尝试用第一张牌组成刻子
    if tile_count[first_tile] >= 3:
        new_count = tile_count.copy()
        new_count[first_tile] -= 3
        remaining_tiles = []
        for tile, count in new_count.items():
            remaining_tiles.extend([tile] * count)
        
        if can_form_melds(remaining_tiles, meld_count - 1):
            return True
    
    # 尝试用第一张牌组成顺子（仅数牌有效）
    if first_tile.tile_type != TileType.HONOUR and first_tile.rank <= 7:
        next_tile_1 = Tile(first_tile.tile_type, first_tile.rank + 1)
        next_tile_2 = Tile(first_tile.tile_type, first_tile.rank + 2)
        
        if tile_count[next_tile_1] > 0 and tile_count[next_tile_2] > 0:
            new_count = tile_count.copy()
            new_count[first_tile] -= 1
            new_count[next_tile_1] -= 1
            new_count[next_tile_2] -= 1
            remaining_tiles = []
            for tile, count in new_count.items():
                remaining_tiles.extend([tile] * count)
            
            if can_form_melds(remaining_tiles, meld_count - 1):
                return True
    
    return False


# ==================== 番种计算（接口预留） ====================

def calculate_score(hand: List[Tile], melds: List[MeldSet], win_type: str, 
                    winner_role: PlayerRole, dealer_role: PlayerRole, 
                    is_self_draw: bool) -> int:
    """
    计算番数和分数
    接口预留：可在 score_calculator.py 中补充具体的番种计算规则
    
    参数：
    - hand: 玩家的手牌
    - melds: 玩家的副露
    - win_type: 和牌类型（标准和/七对/十三幺）
    - winner_role: 赢家位置
    - dealer_role: 庄家位置
    - is_self_draw: 是否自摸
    
    返回：
    - 总分数
    """
    # TODO: 调用 score_calculator.calculate_fan_and_score()
    # 暂时返回简单的分数
    if is_self_draw and winner_role == dealer_role:
        return 8  # 庄家自摸
    elif is_self_draw:
        return 4  # 闲家自摸
    else:
        return 4  # 其他情况
    

# ==================== 游戏主类 ====================

class Game:
    """麻将游戏"""
    
    def __init__(self):
        self.players: List[Player] = []
        self.tile_wall = TileWall()
        self.round_num = 0
        self.dealer_idx = 0  # 庄家索引
        self.current_player_idx = 0
        self.discard_pool: List[Tile] = []  # 牌河
        self.is_playing = True
        self.accumulated_score = {}  # 累积分数
    
    def initialize_game(self):
        """初始化游戏"""
        roles = [PlayerRole.EAST, PlayerRole.SOUTH, PlayerRole.WEST, PlayerRole.NORTH]
        player_types = [PlayerType.HUMAN, PlayerType.AI, PlayerType.AI, PlayerType.AI]
        
        self.players = [
            Player(roles[i], player_types[i]) for i in range(4)
        ]
        
        for player in self.players:
            self.accumulated_score[player.role] = 0
        
        print("=" * 50)
        print("游戏初始化完成")
        print("玩家配置：")
        for player in self.players:
            print(f"  {player}")
        print("=" * 50)
    
    def start_round(self):
        """开始一盘"""
        self.round_num += 1
        print(f"\n{'=' * 50}")
        print(f"第 {self.round_num} 盘 | 庄家：{self.players[self.dealer_idx].role.value}")
        print(f"{'=' * 50}")
        
        # 重置玩家状态
        for player in self.players:
            player.hand.clear()
            player.melds.clear()
            player.status_flag = None
            player.discards.clear()
            player.score = 0
        
        self.discard_pool.clear()
        self.tile_wall.initialize()
        
        # 发牌
        self.deal_tiles()
        self.current_player_idx = self.dealer_idx
    
    def deal_tiles(self):
        """发牌"""
        # 按规则发牌：3轮×16张 + 1轮×4张 = 52张
        # 前3轮：东摸4，南摸4，西摸4，北摸4
        for _ in range(3):
            for i in range(4):
                player_idx = (self.dealer_idx + i) % 4
                player = self.players[player_idx]
                for _ in range(4):
                    tile = self.tile_wall.draw_from_head()
                    if tile:
                        player.add_tile(tile)
        
        # 第4轮：东摸1，南摸1，西摸1，北摸1（完成13张）
        for i in range(4):
            player_idx = (self.dealer_idx + i) % 4
            player = self.players[player_idx]
            tile = self.tile_wall.draw_from_head()
            if tile:
                player.add_tile(tile)
        
        print(f"发牌完成，每家初始13张")
        for player in self.players:
            print(f"  {player}: {len(player.hand)}张牌")
    
    def play_round(self):
        """进行一盘游戏的主循环"""
        self.start_round()
        
        turn_count = 0
        max_turns = 200  # 安全机制
        
        while self.is_playing and turn_count < max_turns:
            turn_count += 1
            
            player = self.players[self.current_player_idx]
            
            # 摸牌阶段
            self.draw_phase(player)
            if not self.is_playing:
                break
            
            # 鸣牌阶段
            self.win_phase(player)
            if not self.is_playing:
                break
            
            # 出牌阶段
            self.discard_phase(player)
            if not self.is_playing:
                break
            
            # 待鸣阶段
            claim_success = self.claim_phase(player)
            if not self.is_playing:
                break
            
            # 如果有人鸣牌，当前玩家转换到响应的玩家
            # 否则进入下一个玩家
            if not claim_success:
                self.current_player_idx = self.get_next_player_idx(self.current_player_idx)
        
        if turn_count >= max_turns:
            print("超过最大回合数，游戏异常结束")
            self.is_playing = False
        
        # 结算
        self.settle_round()
    
    def get_next_player_idx(self, idx: int) -> int:
        """获取下一个玩家索引"""
        return (idx + 1) % 4
    
    def draw_phase(self, player: Player):
        """摸牌阶段"""
        # 根据状态标决定摸牌来源：默认从牌山头摸牌；杠后从牌山尾摸牌；鸣牌状态不摸牌
        if player.status_flag is None:
            tile = self.tile_wall.draw_from_head()
        elif player.status_flag == 'KONG':
            tile = self.tile_wall.draw_from_tail()
        elif player.status_flag == 'MELD':
            # 鸣牌后当前回合不用再摸牌，直接清除状态标
            player.status_flag = None
            return
        else:
            tile = self.tile_wall.draw_from_head()
        
        if tile is None:
            print(f"牌山为空！游戏结束（无人和牌）")
            self.is_playing = False
            return
        
        player.add_tile(tile)
        player.status_flag = None
    
    def win_phase(self, player: Player):
        """鸣牌阶段：自摸、暗杠、加杠"""
        # AI不鸣牌，只有人类玩家需要选择
        if player.player_type == PlayerType.AI:
            return
        print(f"\n[{player} 的回合 - 鸣牌阶段]")
        sorted_hand = sorted(player.hand, key=lambda t: (t.tile_type.value, t.rank))
        hand_shorthands = ' '.join(tile.to_shorthand() for tile in sorted_hand)
        print(f"当前手牌({len(player.hand)}张)：{hand_shorthands}")
        
        options = []
        
        # 自摸检查
        is_win, win_type = is_winning_hand(player.hand, player.melds)
        if is_win:
            options.append(f"1. 自摸（{win_type}）")
        
        # 暗杠检查：手中有4张相同牌
        tile_count = Counter(player.hand)
        dark_kongs = [tile for tile, count in tile_count.items() if count == 4]
        if dark_kongs:
            for tile in dark_kongs:
                options.append(f"2. 暗杠（{tile.to_shorthand()}）")
        
        # 加杠检查：手中有牌可补已碰的刻子
        add_kongs = []
        for meld in player.melds:
            if meld.meld_type == 'PUNG':
                for tile in player.hand:
                    if tile in meld.tiles:
                        add_kongs.append((meld, tile))
                        break
        
        if add_kongs:
            for meld, tile in add_kongs:
                options.append(f"3. 加杠（{tile.to_shorthand()}）")
        
        options.append("0. 不鸣牌，继续出牌")
        
        if len(options) == 1:
            return
        
        print("可选操作：")
        for opt in options:
            print(f"  {opt}")
        
        choice = input("请选择（输入序号）：").strip()
        
        if choice == "1" and is_win:
            print(f">>> {player}自摸！和牌类型：{win_type}")
            score = calculate_score(player.hand, player.melds, win_type, 
                                   player.role, self.players[self.dealer_idx].role, True)
            player.score = score
            self.is_playing = False
            return
        elif choice == "2" and dark_kongs:
            tile = dark_kongs[0]
            print(f">>> {player}暗杠{tile.to_shorthand()}！")
            for _ in range(4):
                player.remove_tile(tile)
            meld = MeldSet([tile, tile, tile, tile], 'DARK_KONG', hidden_count=2)
            player.add_meld(meld)
            player.status_flag = 'KONG'
            self.is_playing = False
            return
        elif choice == "3" and add_kongs:
            meld, tile = add_kongs[0]
            print(f">>> {player}加杠{tile.to_shorthand()}！")
            player.remove_tile(tile)
            meld.tiles.append(tile)
            player.status_flag = 'KONG'
            self.is_playing = False
            return
        
        return
    
    def discard_phase(self, player: Player):
        """出牌阶段"""
        print(f"\n[{player} 的回合 - 出牌阶段]")
        
        # AI策略：打最后摸到的牌
        if player.player_type == PlayerType.AI:
            tile = player.hand[-1]
            player.discard_tile(tile)
            self.discard_pool.append(tile)
            print(f"  {player} 打出：{tile}")
            return
        
        # 人类玩家：显示所有手牌简称，输入简称选择出牌
        sorted_hand = sorted(player.hand, key=lambda t: (t.tile_type.value, t.rank))
        hand_shorthands = [tile.to_shorthand() for tile in sorted_hand]
        normalized_hand = [h.lower() for h in hand_shorthands]
        
        print(f"手牌({len(player.hand)}张)：{' '.join(hand_shorthands)}")
        
        while True:
            choice = input("请输入要打出的牌的简称：").strip().lower()
            
            # 检查输入的简称是否在手牌中（不区分大小写）
            if choice in normalized_hand:
                idx = normalized_hand.index(choice)
                tile = sorted_hand[idx]
                player.discard_tile(tile)
                self.discard_pool.append(tile)
                print(f"  {player} 打出：{tile} ({hand_shorthands[idx]})")
                return
            else:
                print(f"输入错误：'{choice}' 不在你的手牌中，请重新输入")
    
    def claim_phase(self, current_player: Player):
        """待鸣阶段：其他玩家可以碰、杠、吃、荣"""
        discarded_tile = self.discard_pool[-1]
        print(f"\n[待鸣阶段] 牌河中的牌：{discarded_tile.to_shorthand()}")
        
        # 按优先级询问其他玩家是否要鸣牌
        for relative_pos in range(1, 4):  # 1=下家，2=对家，3=上家
            other_player_idx = (self.current_player_idx + relative_pos) % 4
            other_player = self.players[other_player_idx]
            
            if other_player.player_type == PlayerType.AI:
                continue
            
            options = []
            tile_count = Counter(other_player.hand)
            
            # 碰：手里有2张相同牌
            if tile_count[discarded_tile] >= 2:
                options.append("1. 碰")
            
            # 杠：手里有3张相同牌
            if tile_count[discarded_tile] >= 3:
                options.append("2. 杠")
            
            # 吃：仅下家可吃，且能与打出的牌组成顺子
            if relative_pos == 1:
                can_chow = self.can_form_chow(other_player.hand, discarded_tile)
                if can_chow:
                    options.append("3. 吃")
            
            # 荣：手牌加上打出的牌后是否组成和牌
            test_hand = other_player.hand + [discarded_tile]
            is_win, win_type = is_winning_hand(test_hand, other_player.melds)
            if is_win:
                options.append("4. 荣")
            
            options.append("0. 不鸣牌")
            
            if len(options) == 1:
                continue
            
            print(f"\n{other_player} 的可选操作：")
            for opt in options:
                print(f"  {opt}")
            
            choice = input("请选择（输入序号）：").strip()
            
            if choice == "1" and "1. 碰" in options:
                print(f">>> {other_player} 碰 {discarded_tile.to_shorthand()}！")
                self.execute_pung(other_player, discarded_tile)
                self.current_player_idx = other_player_idx
                return True
            
            elif choice == "2" and "2. 杠" in options:
                print(f">>> {other_player} 杠 {discarded_tile.to_shorthand()}！")
                self.execute_kong(other_player, discarded_tile)
                self.current_player_idx = other_player_idx
                return True
            
            elif choice == "3" and "3. 吃" in options:
                print(f">>> {other_player} 吃 {discarded_tile.to_shorthand()}！")
                self.execute_chow(other_player, discarded_tile)
                self.current_player_idx = other_player_idx
                return True
            
            elif choice == "4" and "4. 荣" in options:
                print(f">>> {other_player} 荣 {discarded_tile.to_shorthand()}！")
                other_player.hand.append(discarded_tile)
                score = calculate_score(other_player.hand, other_player.melds, win_type,
                                       other_player.role, self.players[self.dealer_idx].role, False)
                other_player.score = score
                self.is_playing = False
                return True
        
        return False
    
    def can_form_chow(self, hand: List[Tile], tile: Tile) -> bool:
        """检查是否能与打出的牌组成顺子"""
        if tile.tile_type == TileType.HONOUR:
            return False
        
        # 检查三种可能的顺子位置
        possible_sequences = []
        if tile.rank >= 3:
            possible_sequences.append((tile.rank - 2, tile.rank - 1, tile.rank))
        if 1 < tile.rank < 9:
            possible_sequences.append((tile.rank - 1, tile.rank, tile.rank + 1))
        if tile.rank <= 7:
            possible_sequences.append((tile.rank, tile.rank + 1, tile.rank + 2))
        
        tile_count = Counter(hand)
        for seq in possible_sequences:
            tile1 = Tile(tile.tile_type, seq[0])
            tile2 = Tile(tile.tile_type, seq[1])
            tile3 = Tile(tile.tile_type, seq[2])
            if seq.index(tile.rank) == 0:
                if tile_count[tile2] > 0 and tile_count[tile3] > 0:
                    return True
            elif seq.index(tile.rank) == 1:
                if tile_count[tile1] > 0 and tile_count[tile3] > 0:
                    return True
            else:
                if tile_count[tile1] > 0 and tile_count[tile2] > 0:
                    return True
        
        return False
    
    def execute_pung(self, player: Player, tile: Tile):
        """执行碰"""
        player.hand.remove(tile)
        player.hand.remove(tile)
        self.discard_pool.pop()  # 移除牌河中的牌
        meld = MeldSet([tile, tile, tile], 'PUNG')
        player.add_meld(meld)
        player.status_flag = 'MELD'
    
    def execute_kong(self, player: Player, tile: Tile):
        """执行杠"""
        player.hand.remove(tile)
        player.hand.remove(tile)
        player.hand.remove(tile)
        self.discard_pool.pop()  # 移除牌河中的牌
        meld = MeldSet([tile, tile, tile, tile], 'KONG')
        player.add_meld(meld)
        player.status_flag = 'KONG'
    
    def execute_chow(self, player: Player, tile: Tile):
        """执行吃"""
        # 字牌不能吃
        if tile.tile_type == TileType.HONOUR:
            return
        
        tile_count = Counter(player.hand)
        
        # 三种可能的顺子：tile为末张、中间张、开头张
        if tile.rank >= 3:
            tile1 = Tile(tile.tile_type, tile.rank - 2)
            tile2 = Tile(tile.tile_type, tile.rank - 1)
            if tile_count[tile1] > 0 and tile_count[tile2] > 0:
                player.remove_tile(tile1)
                player.remove_tile(tile2)
                self.discard_pool.pop()
                meld = MeldSet([tile1, tile2, tile], 'CHOW')
                player.add_meld(meld)
                player.status_flag = 'MELD'
                return
        
        if 1 < tile.rank < 9:
            tile1 = Tile(tile.tile_type, tile.rank - 1)
            tile2 = Tile(tile.tile_type, tile.rank + 1)
            if tile_count[tile1] > 0 and tile_count[tile2] > 0:
                player.remove_tile(tile1)
                player.remove_tile(tile2)
                self.discard_pool.pop()
                meld = MeldSet([tile1, tile, tile2], 'CHOW')
                player.add_meld(meld)
                player.status_flag = 'MELD'
                return
        
        if tile.rank <= 7:
            tile1 = Tile(tile.tile_type, tile.rank + 1)
            tile2 = Tile(tile.tile_type, tile.rank + 2)
            if tile_count[tile1] > 0 and tile_count[tile2] > 0:
                player.remove_tile(tile1)
                player.remove_tile(tile2)
                self.discard_pool.pop()
                meld = MeldSet([tile, tile1, tile2], 'CHOW')
                player.add_meld(meld)
                player.status_flag = 'MELD'
                return
    
    def settle_round(self):
        """结算一盘"""
        print(f"\n盘结算：")
        
        # 找到赢家
        winner = None
        for player in self.players:
            if player.score > 0:
                winner = player
                break
        
        if winner:
            print(f"赢家：{winner}，得分：{winner.score}")
            self.accumulated_score[winner.role] += winner.score
        else:
            print("流局：无人和牌")
        
        print(f"\n当前累积分数：")
        for role, score in self.accumulated_score.items():
            print(f"  {role.value}：{score}")
        
        self.is_playing = False
    
    def play_game(self, num_rounds: int = 4):
        """进行完整的游戏"""
        self.initialize_game()
        
        for _ in range(num_rounds):
            self.is_playing = True
            self.play_round()
            self.dealer_idx = (self.dealer_idx + 1) % 4  # 庄家交换
        
        self.end_game()
    
    def end_game(self):
        """游戏结束"""
        print(f"\n{'=' * 50}")
        print("游戏结束！最终排名：")
        print(f"{'=' * 50}")
        
        sorted_players = sorted(self.accumulated_score.items(), 
                               key=lambda x: x[1], reverse=True)
        
        current_rank = 1
        prev_score = None
        
        for idx, (role, score) in enumerate(sorted_players):
            if score != prev_score:
                current_rank = idx + 1
            print(f"{current_rank}. {role.value}：{score}分")
            prev_score = score


# ==================== 主程序 ====================

if __name__ == "__main__":
    game = Game()
    game.play_game(num_rounds=4)
