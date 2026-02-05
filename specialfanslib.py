import random
import copy
from math import comb
from mahjonglib import *
from fan import *
from fan_calc import *
import colorama
from colorama import Fore
colorama.init(autoreset=True)

from calc_q_version import all_calc

import re

# ===== 预计算常量，避免重复计算 =====
# 预计算牌张到字符串的映射
TILE_TO_STR_CACHE = {}
TILE_TO_HTML_CACHE = {}
for t in range(34):
    if 0 <= t <= 8:
        TILE_TO_STR_CACHE[t] = f"{t%9+1}m"
        TILE_TO_HTML_CACHE[t] = f'<span class="tile-red">{t%9+1}m</span>'
    elif 9 <= t <= 17:
        TILE_TO_STR_CACHE[t] = f"{t%9+1}s"
        TILE_TO_HTML_CACHE[t] = f'<span class="tile-green">{t%9+1}s</span>'
    elif 18 <= t <= 26:
        TILE_TO_STR_CACHE[t] = f"{t%9+1}p"
        TILE_TO_HTML_CACHE[t] = f'<span class="tile-blue">{t%9+1}p</span>'
    elif 27 <= t <= 33:
        TILE_TO_STR_CACHE[t] = f"{t-26}z"
        TILE_TO_HTML_CACHE[t] = f'<span class="tile-purple">{t-26}z</span>'

# 预计算门风映射
SEATWIND_CACHE = {27: "!", 28: "@", 29: "#", 30: "$"}
WIND_NAMES = {27: "东", 28: "南", 29: "西", 30: "北"}

# 预计算和牌方式标记
WAY_MARKS = {
    1: "%",   # 自摸
    2: "^",   # 杠上开花/抢杠和
    4: "&",   # 柳暗花明
    8: "*"    # 一巡和
}

# 预计算组合数缓存
COMB_CACHE = {}
for i in range(5):
    for j in range(4):
        if j <= i:
            COMB_CACHE[(i, j)] = comb(i, j)

# 预计算顺子基数
SHUN_BASES = [0, 9, 18]

# 预计算幺九牌
YAOCHU_TILES = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]

# ===== 优化的权重选择算法 =====
class WeightedSelector:
    """预计算权重的选择器"""
    def __init__(self):
        self.cache = {}
        self.cache_size_limit = 1000
    
    def choice(self, options, weights):
        if not options or not weights:
            return None
            
        # 为小规模选择使用缓存
        if len(options) <= 20:
            key = tuple(weights)
            if key not in self.cache:
                # 清理缓存
                if len(self.cache) >= self.cache_size_limit:
                    # 删除一半的缓存项
                    items_to_remove = list(self.cache.keys())[:len(self.cache)//2]
                    for k in items_to_remove:
                        del self.cache[k]
                
                total = sum(weights)
                if total == 0:
                    return random.choice(options)
                    
                cumulative = []
                acc = 0
                for w in weights:
                    acc += w
                    cumulative.append(acc / total)
                self.cache[key] = cumulative
            cumulative = self.cache[key]
        else:
            # 大规模选择直接计算
            total = sum(weights)
            if total == 0:
                return random.choice(options)
                
            cumulative = []
            acc = 0
            for w in weights:
                acc += w
                cumulative.append(acc / total)
        
        r = random.random()
        for i, cum_prob in enumerate(cumulative):
            if r <= cum_prob:
                return options[i]
        return options[-1]

# 全局选择器实例
weighted_selector = WeightedSelector()

def weighted_choice(options, weights):
    """优化的权重选择"""
    return weighted_selector.choice(options, weights)

# ===== 优化的算番器字符串拼接工具 =====
def melds_to_str(melds):
    """优化的副露转字符串"""
    if not melds:
        return ""
    
    out_parts = []
    for tiles, typ in melds:
        tile_parts = []
        for t in tiles:
            tile_parts.append(TILE_TO_STR_CACHE.get(t, str(t)))
        s = "".join(tile_parts)
        if typ == 6:
            out_parts.append(f"[{s}]")
        else:
            out_parts.append(f"({s})")
    return "".join(out_parts)

def hand_to_str(hand):
    """优化的手牌转字符串"""
    if not hand:
        return ""
    # 优化排序：检查是否已经排序
    sorted_hand = sorted(hand) if hand != sorted(hand) else hand
    return "".join(TILE_TO_STR_CACHE.get(t, str(t)) for t in sorted_hand)

def tile_to_str(tile):
    """快速牌张转字符串"""
    return TILE_TO_STR_CACHE.get(tile, str(tile))

def seatwind_to_char(seatWindTile):
    """快速门风转字符"""
    return SEATWIND_CACHE.get(seatWindTile, "!")

def to_fanqi_input(hand, melds, seatWindTile, way=0, win_tile=None):
    """
    优化的算番器输入字符串生成
    如果指定了win_tile，会将其从hand中移除并放在最后
    """
    # 预构建字符串部分
    melds_str = melds_to_str(melds)
    
    # 处理手牌：如果有和张，将其从手牌中移除
    actual_hand = hand.copy() if win_tile is not None and win_tile in hand else hand
    if win_tile is not None and win_tile in actual_hand:
        actual_hand.remove(win_tile)
    
    hand_str = hand_to_str(actual_hand)
    
    # 构建完整字符串
    parts = [melds_str, hand_str]
    
    # 如果有和张，添加到最后
    if win_tile is not None:
        parts.append(TILE_TO_STR_CACHE.get(win_tile, str(win_tile)))
    
    # 添加门风
    parts.append(SEATWIND_CACHE.get(seatWindTile, "!"))
    
    # 添加和牌方式标记
    for flag, mark in WAY_MARKS.items():
        if way & flag:
            parts.append(mark)
    
    return "".join(parts)

def determine_way_for_hand():
    """确定和牌方式：75%铳和，25%自摸"""
    return 1 if random.random() < 0.25 else 0  # 1=自摸, 0=铳和

def generate_wumenqi_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成五门齐的手牌 - 直接分配策略
    1. 随机选一门做雀头
    2. 其他四门各分配一个面子
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        outside = random.random() < 0.1 and min_fan >= 9  # 要求较高时, 10%概率强制混带幺
        outside = random.random() < 0.2 and min_fan >= 16  # 要求极高时, 20%概率强制混带幺
        pung = random.random() < 0.1 and min_fan >= 12  # 要求很高时, 10%概率强制碰碰和
        pung = random.random() < 0.2 and min_fan >= 16  # 要求极高时, 20%概率强制碰碰和
        # 定义五门
        suits = {
            "wan": list(range(0, 9)),     # 万 0-8
            "tiao": list(range(9, 18)),      # 条 9-17
            "tong": list(range(18, 27)),     # 筒 18-26
            "feng": list(range(27, 31)),    # 风 27-30
            "jian": list(range(31, 34))     # 箭 31-33
        }

        if outside:
            suits = {
                "wan": [0,8],     # 万 0,8
                "tiao": [9,17],      # 条 9,17
                "tong": [18,26],     # 筒 18,26
                "feng": list(range(27, 31)),    # 风 27-30
                "jian": list(range(31, 34))     # 箭 31-33
            }
        
        suit_names = list(suits.keys())
        remain = [4] * 34
        
        # 1. 随机选择一门做雀头
        head_suit = random.choice(suit_names)
        head_tiles = suits[head_suit]
        head_tile = random.choice(head_tiles)
        
        if remain[head_tile] < 2:
            continue
        
        head = [head_tile, head_tile]
        remain[head_tile] -= 2
        
        # 2. 其他四门各分配一个面子
        remaining_suits = [s for s in suit_names if s != head_suit]
        sets = []
        set_types = []
        
        success = True
        for suit in remaining_suits:
            suit_tiles = suits[suit]
            
            # 为这门生成一个面子
            candidates = []
            weights = []
            set_type_marks = []
            
            # 尝试生成顺子（只有万、条、筒可以）
            if suit in ["wan", "tiao", "tong"] and not pung:
                base = suit_tiles[0]  # 获取这门的起始牌
                chow_range = range(7) if not outside else [0, 6]
                for i in chow_range:  # 顺子
                    a, b, c = base+i, base+i+1, base+i+2
                    if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                        candidates.append([a, b, c])
                        weights.append(remain[a] * remain[b] * remain[c])
                        set_type_marks.append("shun")
            
            # 尝试生成刻子
            for tile in suit_tiles:
                if remain[tile] >= 3:
                    candidates.append([tile, tile, tile])
                    weights.append(COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3)))
                    set_type_marks.append("ke")
            
            if not candidates:
                success = False
                break
            
            # 选择面子
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                success = False
                break
                
            selected_set = candidates[idx]
            sets.append(selected_set)
            set_types.append(set_type_marks[idx])
            
            # 更新剩余牌数
            for tile in selected_set:
                remain[tile] -= 1
        
        if not success or len(sets) != 4:
            continue
        
        # 3. 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            t = set_types[i]
            is_open = random.random() < 0.5
            
            if t == "shun":
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
            elif t == "ke":
                is_kan = random.random() < 0.1
                
                if is_kan and remain[m[0]] >= 1:
                    m_kan = m + [m[0]]
                    remain[m[0]] -= 1
                    if is_open:
                        melds.append([m_kan, 0])
                        melds_count += 1
                    else:
                        melds.append([m_kan, 6])
                        melds_count += 1
                else:
                    if is_open:
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
        
        # 添加雀头到手牌
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        # 4. 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 必须检查是否真的有五门齐
            if "五门齐" not in fan_names:
                continue
                
            if score < (min_fan * 4) and melds == []:
                continue
            if score < (min_fan * 4 - 8):
                continue
            
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_jiushuqi_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成九数齐的手牌
    九数齐必然结构：两顺两刻一雀头 (3*2 + 1*2 + 1 = 9个序数)
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sequences = list(range(1, 10))  # 1,2,3,4,5,6,7,8,9
        random.shuffle(sequences)
        
        # 第一步：生成两个序数不重复的顺子
        shun_sets = []
        shun_seqs = []
        suits = [0, 9, 18]  # 条、筒、万的基数
        
        # 生成第一个顺子
        for start_seq in range(1, 8):  # 1-7可以作为顺子起点
            if start_seq + 2 <= 9:  # 确保顺子不超出1-9范围
                suit_base = random.choice(suits)
                a = suit_base + start_seq - 1
                b = suit_base + start_seq
                c = suit_base + start_seq + 1
                
                if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                    shun_sets.append([a, b, c])
                    shun_seqs.extend([start_seq, start_seq+1, start_seq+2])
                    for tile in [a, b, c]:
                        remain[tile] -= 1
                    break
        
        if len(shun_sets) != 1:
            continue
        
        # 生成第二个顺子（序数不能与第一个重复）
        used_seqs = set(shun_seqs)
        remaining_seqs = [s for s in range(1, 10) if s not in used_seqs]
        
        second_shun_found = False
        for start_seq in remaining_seqs:
            if (start_seq + 1 in remaining_seqs and 
                start_seq + 2 in remaining_seqs and
                start_seq <= 7):
                
                suit_base = random.choice(suits)
                a = suit_base + start_seq - 1
                b = suit_base + start_seq
                c = suit_base + start_seq + 1
                
                if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                    shun_sets.append([a, b, c])
                    shun_seqs.extend([start_seq, start_seq+1, start_seq+2])
                    for tile in [a, b, c]:
                        remain[tile] -= 1
                    second_shun_found = True
                    break
        
        if not second_shun_found or len(shun_sets) != 2:
            continue
        
        # 第二步：在剩余的3个序数中选择2个做刻子，1个做雀头
        used_seqs = set(shun_seqs)
        remaining_seqs = [s for s in range(1, 10) if s not in used_seqs]
        
        if len(remaining_seqs) != 3:
            continue
        
        # 随机分配：2个刻子 + 1个雀头
        random.shuffle(remaining_seqs)
        ke_seqs = remaining_seqs[:2]  # 前两个做刻子
        head_seq = remaining_seqs[2]  # 最后一个做雀头
        
        # 生成两个刻子
        ke_sets = []
        for seq in ke_seqs:
            suit_base = random.choice(suits)
            tile = suit_base + seq - 1
            
            if remain[tile] >= 3:
                ke_sets.append([tile, tile, tile])
                remain[tile] -= 3
            else:
                break
        
        if len(ke_sets) != 2:
            continue
        
        # 生成雀头
        suit_base = random.choice(suits)
        head_tile = suit_base + head_seq - 1
        
        if remain[head_tile] < 2:
            continue
        
        head = [head_tile, head_tile]
        remain[head_tile] -= 2
        
        # 验证是否覆盖了全部9个序数
        all_seqs = set(shun_seqs + ke_seqs + [head_seq])
        if len(all_seqs) != 9 or all_seqs != set(range(1, 10)):
            continue
        
        # 合并所有面子
        all_sets = shun_sets + ke_sets
        all_set_types = ["shun", "shun", "ke", "ke"]
        
        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(all_sets):
            t = all_set_types[i]
            is_open = random.random() < 0.5
            
            if t == "shun":
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
            elif t == "ke":
                is_kan = random.random() < 0.1
                
                if is_kan and remain[m[0]] >= 1:
                    m_kan = m + [m[0]]
                    remain[m[0]] -= 1
                    if is_open:
                        melds.append([m_kan, 0])
                        melds_count += 1
                    else:
                        melds.append([m_kan, 6])
                        melds_count += 1
                else:
                    if is_open:
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
        
        # 添加雀头到手牌
        hand.extend(head)
        hand_idx_map.extend([100, 100])  # 使用+100标记雀头

        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 必须检查是否真的有九数齐
            if "九数齐" not in fan_names:
                continue
                
            if score < (min_fan * 4) and melds == []:
                continue
            if score < (min_fan * 4 - 8):
                continue
            
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_hundaiyao_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成混带幺的手牌
    混带幺要求：每个部分组合都含有1、9或字牌
    - 刻子/对子：必须是1、9或字牌 (0,8,9,17,18,26,27-33)
    - 顺子：必须是123(0,1,2 或 9,10,11 或 18,19,20) 或 789(6,7,8 或 15,16,17 或 24,25,26)
    """
    max_attempts = 1000
    
    # 定义混带幺的有效牌
    # 幺九牌：可以组成刻子/对子
    yao_jiu_tiles = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]
    
    # 有效顺子：123和789
    valid_shuns = [
        [0, 1, 2],    # 123条
        [6, 7, 8],    # 789条
        [9, 10, 11],  # 123筒
        [15, 16, 17], # 789筒
        [18, 19, 20], # 123万
        [24, 25, 26]  # 789万
    ]
    
    for attempt in range(max_attempts):
        pure = random.random() < 0.1 and min_fan >= 9  # 要求较高时, 10%概率强制清带幺
        pure = random.random() < 0.2 and min_fan >= 16  # 要求极高时, 20%概率强制清带幺
        pung = random.random() < 0.1 and min_fan >= 12  # 要求很高时, 10%概率强制碰碰和
        pung = random.random() < 0.2 and min_fan >= 16  # 要求极高时, 20%概率强制碰碰和

        remain = [4] * 34
        sets = []
        set_types = []
        
        # 生成四副面子
        for _ in range(4):
            candidates = []
            weights = []
            set_type_marks = []
            
            # 生成有效的顺子（123或789）
            if not pung:
                for shun in valid_shuns:
                    a, b, c = shun
                    if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                        comb_weight = remain[a] * remain[b] * remain[c]
                        final_weight = 1 * comb_weight
                        candidates.append([a, b, c])
                        weights.append(final_weight)
                        set_type_marks.append("shun")
            
            # 生成幺九牌的刻子
            for tile in yao_jiu_tiles:
                if remain[tile] >= 3 and (not pure or tile < 27):
                    comb_weight = COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3))
                    final_weight = 2 * comb_weight  # 刻子权重稍高
                    candidates.append([tile, tile, tile])
                    weights.append(final_weight)
                    set_type_marks.append("ke")
            
            if not candidates:
                break
                
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                break
                
            s = candidates[idx]
            sets.append(s)
            set_types.append(set_type_marks[idx])
            
            for t in s:
                remain[t] -= 1
        
        if len(sets) != 4:
            continue
            
        # 生成雀头（必须是幺九牌）
        head_cands = []
        head_weights = []
        for tile in yao_jiu_tiles:
            if remain[tile] >= 2 and (not pure or tile < 27):
                w = COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2))
                if w > 0:
                    head_cands.append([tile, tile])
                    head_weights.append(w)
        
        if not head_cands:
            continue
            
        head = weighted_choice(head_cands, head_weights)
        if head is None:
            continue

        # 副露与杠逻辑
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        random_values = [random.random() for _ in range(len(sets) * 2)]
        rand_idx = 0
        
        for i, m in enumerate(sets):
            t = set_types[i]
            if t == "shun":
                is_open = random_values[rand_idx] < 0.4
                rand_idx += 1
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
            elif t == "ke":
                is_open = random_values[rand_idx] < 0.6
                is_kan = random_values[rand_idx + 1] < 0.2
                rand_idx += 2
                
                if is_kan and remain[m[0]] >= 1:
                    m_kan = m + [m[0]]
                    remain[m[0]] -= 1
                    if is_open:
                        melds.append([m_kan, 0])
                        melds_count += 1
                    else:
                        melds.append([m_kan, 6])
                        melds_count += 1
                else:
                    if is_open:
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
        
        # 添加雀头到手牌
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 必须检查是否真的有混带幺
            if set(fan_names) & {"混带幺", "清带幺", "混幺九", "清幺九"} == {}:
                continue
                
            if score < (min_fan * 4) and melds == []:
                continue
            if score < (min_fan * 4 - 8):
                continue
            
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_jushu_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成聚数牌型的手牌
    聚四数：序数牌只使用连续的4个数字（4番）
    聚三数：序数牌只使用连续的3个数字（6番）
    
    策略：
    - 一般情况生成聚四数
    - fan>=12时，10%概率强制生成聚三数
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        # 决定生成聚三数还是聚四数
        force_jusanshu = random.random() < 0.1 and min_fan >= 12
        force_jusanshu = random.random() < 0.2 and min_fan >= 16
        remain = [4] * 34
        
        # 选择使用的数字范围
        if force_jusanshu:
            # 聚三数：选择连续的3个数字 (1-3, 2-4, 3-5, 4-6, 5-7, 6-8, 7-9)
            start_num = random.randint(1, 7)  # 1到7可以作为起始
            used_numbers = [start_num, start_num + 1, start_num + 2]
        else:
            # 聚四数：选择连续的4个数字 (1-4, 2-5, 3-6, 4-7, 5-8, 6-9)
            start_num = random.randint(1, 6)  # 1到6可以作为起始
            used_numbers = [start_num, start_num + 1, start_num + 2, start_num + 3]
        
        # 转换为牌张索引（减1因为牌张索引从0开始）
        suits = [0, 9, 18]  # 万、条、筒的基数
        valid_tiles = []
        for suit_base in suits:
            for num in used_numbers:
                valid_tiles.append(suit_base + num - 1)

        all_valid_tiles = valid_tiles
        
        # 生成四副面子
        sets = []
        set_types = []
        
        success = True
        for _ in range(4):
            candidates = []
            weights = []
            set_type_marks = []
            
            # 生成顺子（只能使用指定的数字）
            for suit_base in suits:
                for i in range(len(used_numbers) - 2):  # 可以组成顺子的起始位置
                    start_idx = used_numbers[i] - 1  # 转换为牌张索引
                    if start_idx + 2 < 9:  # 确保不超出范围
                        a = suit_base + start_idx
                        b = suit_base + start_idx + 1
                        c = suit_base + start_idx + 2
                        
                        # 检查这三张牌是否都在允许的数字范围内
                        if (a in valid_tiles and b in valid_tiles and c in valid_tiles and
                            remain[a] > 0 and remain[b] > 0 and remain[c] > 0):
                            candidates.append([a, b, c])
                            weights.append(remain[a] * remain[b] * remain[c])
                            set_type_marks.append("shun")
            
            # 生成刻子（序数牌限制在指定数字）
            for tile in all_valid_tiles:
                if remain[tile] >= 3:
                    candidates.append([tile, tile, tile])
                    weights.append(COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3)))
                    set_type_marks.append("ke")
            
            if not candidates:
                success = False
                break
            
            # 选择面子
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                success = False
                break
                
            selected_set = candidates[idx]
            sets.append(selected_set)
            set_types.append(set_type_marks[idx])
            
            # 更新剩余牌数
            for tile in selected_set:
                remain[tile] -= 1
        
        if not success or len(sets) != 4:
            continue
        
        # 生成雀头（序数牌限制在指定数字）
        head_candidates = []
        head_weights = []
        for tile in all_valid_tiles:
            if remain[tile] >= 2:
                head_candidates.append([tile, tile])
                head_weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue
        
        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            t = set_types[i]
            is_open = random.random() < 0.5
            
            if t == "shun":
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
            elif t == "ke":
                is_kan = random.random() < 0.15
                
                if is_kan and remain[m[0]] >= 1:
                    m_kan = m + [m[0]]
                    remain[m[0]] -= 1
                    if is_open:
                        melds.append([m_kan, 0])
                        melds_count += 1
                    else:
                        melds.append([m_kan, 6])
                        melds_count += 1
                else:
                    if is_open:
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
        
        # 添加雀头到手牌
        hand.extend(head)
        hand_idx_map.extend([100, 100])
        
        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否生成了目标番型
            has_target_fan = '聚三数' in fan_names or '聚四数' in fan_names
            
            if not has_target_fan:
                continue
            
            # 检查番数要求
            if score < (min_fan * 4) and melds == []:
                continue
            if score < (min_fan * 4 - 8):
                continue
            
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_jushu_seven_pairs(min_fan=3, forced_wayEq0=False):
    """
    专门生成聚数牌型的七对子
    聚四数：序数牌只使用连续的4个数字（4番）
    聚三数：序数牌只使用连续的3个数字（6番）
    
    七对子的聚数要求：7个对子的序数牌只能使用连续的数字
    """
    max_attempts = 3000
    
    for attempt in range(max_attempts):
        # 决定生成聚三数还是聚四数
        force_jusanshu = random.random() < 0.1 and min_fan >= 12
        force_jusanshu = random.random() < 0.2 and min_fan >= 16
        
        # 选择使用的数字范围
        if force_jusanshu:
            # 聚三数：选择连续的3个数字
            start_num = random.randint(1, 7)
            used_numbers = [start_num, start_num + 1, start_num + 2]
        else:
            # 聚四数：选择连续的4个数字
            start_num = random.randint(1, 6)
            used_numbers = [start_num, start_num + 1, start_num + 2, start_num + 3]
        
        # 转换为牌张索引
        suits = [0, 9, 18]  # 万、条、筒的基数
        valid_tiles = []
        for suit_base in suits:
            for num in used_numbers:
                valid_tiles.append(suit_base + num - 1)
        
        # 为七对子生成对子
        remain = [4] * 34
        pairs = []
        
        success = True
        for pair_idx in range(7):
            candidates = []
            weights = []
            
            # 只从有效牌中选择对子
            for tile in valid_tiles:
                if remain[tile] >= 2:
                    candidates.append(tile)
                    weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
            
            if not candidates:
                success = False
                break
            
            # 选择对子
            selected_tile = weighted_choice(candidates, weights)
            if selected_tile is None:
                success = False
                break
            
            pairs.append([selected_tile, selected_tile])
            remain[selected_tile] -= 2
        
        if not success or len(pairs) != 7:
            continue
        
        # 构建手牌
        hand = []
        for pair in pairs:
            hand.extend(pair)
        hand.sort()
        
        melds = []  # 七对子没有副露
        
        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否生成了目标番型
            has_qidui = "七对子" in fan_names
            has_jushu = '聚三数' in fan_names or '聚四数' in fan_names
            
            if not (has_qidui and has_jushu):
                continue
            
            # 检查番数要求
            if score >= (min_fan * 4 - 8):
                return hand, melds, pairs, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_jushu_combined(hand_type="standard", min_fan=3, forced_wayEq0=False):
    """
    聚数生成器的统一入口
    根据手牌类型选择相应的生成方法
    """
    if hand_type == "seven_pairs":
        return generate_jushu_seven_pairs(min_fan, forced_wayEq0)
    else:
        return generate_jushu_hand(min_fan, forced_wayEq0)
    
# 在 specialfanslib.py 中添加以下函数

def generate_yise_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成一色牌型的手牌
    混一色: 一种序数牌+字牌 (6番)
    清一色: 一种序数牌(24番)
    
    策略：
    - 一般情况生成混一色
    - fan>=12时, 10%概率强制生成清一色
    """
    max_attempts = 2000
    
    # 决定生成清一色还是混一色
    force_qingyise = random.random() < 0.2 and min_fan >= 12
    force_qingyise = random.random() < 0.4 and min_fan >= 16
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        
        # 随机选择一种序数牌花色
        suit_base = random.choice([0, 9, 18])  # 万、条、筒的基数
        suit_tiles = list(range(suit_base, suit_base + 9))  # 该花色的9张牌
        
        # 定义有效牌张
        if force_qingyise:
            # 清一色：只能用选中的序数牌
            valid_tiles = suit_tiles
        else:
            # 混一色：选中的序数牌 + 所有字牌
            zi_tiles = list(range(27, 34))
            valid_tiles = suit_tiles + zi_tiles
        
        # 生成四副面子
        sets = []
        set_types = []
        
        success = True
        for face_num in range(4):
            candidates = []
            weights = []
            set_type_marks = []
            
            # 生成顺子（只能使用选中的序数牌）
            for i in range(7):  # 1-7可以作为顺子起始
                a = suit_base + i
                b = suit_base + i + 1
                c = suit_base + i + 2
                
                if (a in valid_tiles and b in valid_tiles and c in valid_tiles and
                    remain[a] > 0 and remain[b] > 0 and remain[c] > 0):
                    candidates.append([a, b, c])
                    weights.append(remain[a] * remain[b] * remain[c] * 3)  # 提高顺子权重
                    set_type_marks.append("shun")
            
            # 生成刻子（序数牌 + 字牌）
            for tile in valid_tiles:
                if remain[tile] >= 3:
                    base_weight = COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3))
                    
                    if not force_qingyise:
                        # 混一色：字牌刻子权重稍高
                        if tile in suit_tiles:  # 序数牌
                            weight = base_weight * 2
                        else:  # 字牌
                            weight = base_weight * 3
                    else:
                        # 清一色：只有序数牌
                        weight = base_weight * 2
                    
                    candidates.append([tile, tile, tile])
                    weights.append(weight)
                    set_type_marks.append("ke")
            
            if not candidates:
                success = False
                break
            
            # 选择面子
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                success = False
                break
                
            selected_set = candidates[idx]
            sets.append(selected_set)
            set_types.append(set_type_marks[idx])
            
            # 更新剩余牌数
            for tile in selected_set:
                remain[tile] -= 1
        
        if not success or len(sets) != 4:
            continue
        
        # 生成雀头
        head_candidates = []
        head_weights = []
        for tile in valid_tiles:
            if remain[tile] >= 2:
                base_weight = COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2))
                
                if not force_qingyise:
                    # 混一色：字牌雀头权重稍高
                    if tile in suit_tiles:
                        weight = base_weight
                    else:
                        weight = base_weight * 2
                else:
                    # 清一色：只有序数牌
                    weight = base_weight
                
                head_candidates.append([tile, tile])
                head_weights.append(weight)
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue
        
        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            t = set_types[i]
            # 适当降低副露率以保持番数
            is_open = random.random() < 0.4
            
            if t == "shun":
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
            elif t == "ke":
                is_kan = random.random() < 0.1  # 降低杠牌率
                
                if is_kan and remain[m[0]] >= 1:
                    m_kan = m + [m[0]]
                    remain[m[0]] -= 1
                    if is_open:
                        melds.append([m_kan, 0])
                        melds_count += 1
                    else:
                        melds.append([m_kan, 6])
                        melds_count += 1
                else:
                    if is_open:
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
        
        # 添加雀头到手牌
        hand.extend(head)
        hand_idx_map.extend([100, 100])
        
        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否生成了目标番型
            has_target_fan = "清一色" in fan_names or "混一色" in fan_names
            
            if not has_target_fan:
                continue
            
            # 检查番数要求（放宽一些）
            required_score = min_fan * 4
            if melds:
                required_score -= 8  # 有副露时降低要求
            
            if score >= required_score:
                return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_yise_seven_pairs(min_fan=3, forced_wayEq0=False):
    """
    专门生成一色牌型的七对子
    混一色: 一种序数牌+字牌 (3番)
    清一色: 一种序数牌 (6番)
    
    七对子的一色要求: 7个对子都在指定花色范围内
    """
    max_attempts = 3000
    
    for attempt in range(max_attempts):
        # 决定生成清一色还是混一色
        force_qingyise = random.random() < 0.1 and min_fan >= 12
        force_qingyise = random.random() < 0.3 and min_fan >= 16
        
        # 随机选择一种序数牌花色
        suit_base = random.choice([0, 9, 18])
        suit_tiles = list(range(suit_base, suit_base + 9))
        
        # 定义有效牌张
        if force_qingyise:
            # 清一色：只能用选中的序数牌
            valid_tiles = suit_tiles
        else:
            # 混一色：选中的序数牌 + 所有字牌
            zi_tiles = list(range(27, 34))
            valid_tiles = suit_tiles + zi_tiles
        
        # 为七对子生成对子
        remain = [4] * 34
        pairs = []
        
        success = True
        for pair_idx in range(7):
            candidates = []
            weights = []
            
            # 如果是混一色，控制字牌对子的数量
            if not force_qingyise:
                # 前5个对子优先用序数牌，后2个可以用字牌
                prefer_seq = pair_idx < 5
                
                for tile in valid_tiles:
                    if remain[tile] >= 2:
                        base_weight = COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2))
                        
                        if tile in suit_tiles:  # 序数牌
                            weight = base_weight * (3 if prefer_seq else 2)
                        else:  # 字牌
                            weight = base_weight * (1 if prefer_seq else 2)
                        
                        candidates.append(tile)
                        weights.append(weight)
            else:
                # 清一色：只从序数牌中选择对子
                for tile in valid_tiles:
                    if remain[tile] >= 2:
                        candidates.append(tile)
                        weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
            
            if not candidates:
                success = False
                break
            
            # 选择对子
            selected_tile = weighted_choice(candidates, weights)
            if selected_tile is None:
                success = False
                break
            
            pairs.append([selected_tile, selected_tile])
            remain[selected_tile] -= 2
        
        if not success or len(pairs) != 7:
            continue
        
        # 构建手牌
        hand = []
        for pair in pairs:
            hand.extend(pair)
        hand.sort()
        
        melds = []  # 七对子没有副露
        
        # 验证和计算番数
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否生成了目标番型
            has_qidui = "七对子" in fan_names
            target_fan_type = "清一色" if force_qingyise else "混一色"
            has_yise = target_fan_type in fan_names
            
            if not (has_qidui and has_yise):
                continue
            
            # 检查番数要求
            if score >= (min_fan * 4 - 8):
                return hand, melds, pairs, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_yise_combined(hand_type="standard", min_fan=3, forced_wayEq0=False):
    """
    一色生成器的统一入口
    根据手牌类型选择相应的生成方法
    """
    if hand_type == "seven_pairs":
        return generate_yise_seven_pairs(min_fan, forced_wayEq0)
    else:
        return generate_yise_hand(min_fan, forced_wayEq0)

def generate_symmetry_hand(min_fan=3, forced_wayEq0=False):
    """
    对称牌型生成器
    1. 选定两种花色，4副面子只能在这两种花色中选择。
    2. 4副面子的分布：2/3为2:2（一般对称），1/3为3:1（包含映同和必成法）。
    3. 雀头权重：2:2时两花色雀头与箭牌/门风优先；3:1时三种数牌花色的3~7权重×10。
    4. 最后牌型必须满足两对称|镜同和|形同和|映同和之一。
    """
    max_attempts = 2000
    suits = [0, 9, 18]  # 万、条、筒
    dragons = [31, 32, 33]

    for attempt in range(max_attempts):
        remain = [4] * 34

        # 1. 随机选定两种花色
        suit_choices = random.sample(suits, 2)
        suit_a, suit_b = suit_choices

        # 2. 0.5%概率采用31映同和必成法，否则走普通22分布
        if random.random() < 0.005:
            # 31结构，主色3面子，副色1面子。主色a，副色b
            center = random.choice([2,6] + [3,5] * 6 + [4] * 8)  # 中心序数，范围3-7, 中间概率更大
            # x2(主色)和y(副色)都用顺子或刻子，中心序数=中心
            # x1 x3类型和x2一样，中心序数关于center对称
            valid = False
            ttype = random.choice(["shun"] * 9 + ["ke"]) # 顺子概率更高
            # 顺子情况
            if ttype == "shun":
                # 顺子的中心序数 = 起始+1
                offset_list_ori = list(range(1, min(center-1, 7-center)+1))
                offset_list = []
                for offset in offset_list_ori:
                    offset_list += [offset] * [0,1,6,8][offset]
                random.shuffle(offset_list)
                if not offset_list:
                    continue
                for offset in offset_list:
                    c1 = center - offset
                    c3 = center + offset
                    if not (1 <= c1 <= 7 and 1 <= c3 <= 7):
                        continue
                    # x1, x2, x3
                    x1 = [suit_a + c1 - 1, suit_a + c1, suit_a + c1 + 1]
                    x2 = [suit_a + center - 1, suit_a + center, suit_a + center + 1]
                    x3 = [suit_a + c3 - 1, suit_a + c3, suit_a + c3 + 1]
                    y  = [suit_b + center - 1, suit_b + center, suit_b + center + 1]
                    all_sets = [x1, x2, x3, y]
                    if all(0 <= t < 27 for s in all_sets for t in s) and \
                        all(remain[t] > 0 for s in all_sets for t in s):
                        # 分配面子
                        for s in all_sets:
                            for t in s:
                                remain[t] -= 1
                        sets = [x1, x2, x3, y]
                        set_types = ["shun"]*4
                        valid = True
                        break
            elif ttype == "ke":
                # 刻子的中心序数 = 牌值
                offset_list = list(range(1, min(center, 8-center)+1))
                random.shuffle(offset_list)
                if not offset_list:
                    continue
                for offset in offset_list:
                    c1 = center - offset
                    c3 = center + offset
                    if not (0 <= c1 <= 8 and 0 <= c3 <= 8):
                        continue
                    x1 = [suit_a + c1]*3
                    x2 = [suit_a + center]*3
                    x3 = [suit_a + c3]*3
                    y  = [suit_b + center]*3
                    all_sets = [x1, x2, x3, y]
                    if all(0 <= t < 27 for s in all_sets for t in s) and \
                        all(remain[t] >= 1 for s in all_sets for t in s):
                        for s in all_sets:
                            for t in s:
                                remain[t] -= 1
                        sets = [x1, x2, x3, y]
                        set_types = ["ke"]*4
                        valid = True
                        break
            if not valid:
                continue
            # 雀头中心序数，主/副色任选
            seatWindTile = random.choice(range(27, 31))
            head_candidates = []
            head_weights = []
            for color in [0, 9, 18]:
                tile = color + center
                if remain[tile] >= 2:
                    head_candidates.append([tile, tile])
                    head_weights.append(10)
            if not head_candidates:
                continue
            head = weighted_choice(head_candidates, head_weights)
            if head is None:
                continue
            hand = []
            melds = []
            hand_idx_map = []
            for i, m in enumerate(sets):
                t = set_types[i]
                # 你可以调整副露概率
                if t == "shun":
                    is_open = random.random() < 0.4
                    if is_open:
                        melds.append([m, 0])
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
                elif t == "ke":
                    is_open = random.random() < 0.6
                    is_kan = random.random() < 0.08
                    if is_kan and remain[m[0]] >= 1:
                        m_kan = m + [m[0]]
                        remain[m[0]] -= 1
                        if is_open:
                            melds.append([m_kan, 0])
                        else:
                            melds.append([m_kan, 6])
                    else:
                        if is_open:
                            melds.append([m, 0])
                        else:
                            hand.extend(m)
                            hand_idx_map.extend([i]*3)
            # 雀头直接加入手牌
            hand.extend(head)
            hand_idx_map.extend([100, 100])
        else:
            # 普通2:2分布
            face_pattern = [suit_a, suit_a, suit_b, suit_b]
            sets = []
            set_types = []
            success = True
            for idx, suit_base in enumerate(face_pattern):
                candidates = []
                weights = []
                set_type_marks = []
                # 顺子
                for i in range(7):
                    a = suit_base + i
                    b = suit_base + i + 1
                    c = suit_base + i + 2
                    if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                        candidates.append([a, b, c])
                        weights.append(remain[a] * remain[b] * remain[c] * 3)
                        set_type_marks.append("shun")
                # 刻子
                for i in range(suit_base, suit_base + 9):
                    if remain[i] >= 3:
                        candidates.append([i, i, i])
                        weights.append(COMB_CACHE.get((remain[i], 3), comb(remain[i], 3)))
                        set_type_marks.append("ke")
                if not candidates:
                    success = False
                    break
                idx_choice = weighted_choice(range(len(candidates)), weights)
                if idx_choice is None:
                    success = False
                    break
                selected_set = candidates[idx_choice]
                sets.append(selected_set)
                set_types.append(set_type_marks[idx_choice])
                for t in selected_set:
                    remain[t] -= 1
            if not success or len(sets) != 4:
                continue
            seatWindTile = random.choice(range(27, 31))
            head_candidates = []
            head_weights = []
            for i in range(34):
                if remain[i] >= 2:
                    if i in range(suit_a, suit_a+9) or i in range(suit_b, suit_b+9):
                        weight = 5
                    elif i in dragons or i == seatWindTile:
                        weight = 5
                    else:
                        weight = 1
                    head_candidates.append([i, i])
                    head_weights.append(weight)
            if not head_candidates:
                continue
            head = weighted_choice(head_candidates, head_weights)
            if head is None:
                continue
            hand = []
            melds = []
            hand_idx_map = []
            for i, m in enumerate(sets):
                t = set_types[i]
                # 你可以调整副露概率
                if t == "shun":
                    is_open = random.random() < 0.4
                    if is_open:
                        melds.append([m, 0])
                    else:
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)
                elif t == "ke":
                    is_open = random.random() < 0.6
                    is_kan = random.random() < 0.08
                    if is_kan and remain[m[0]] >= 1:
                        m_kan = m + [m[0]]
                        remain[m[0]] -= 1
                        if is_open:
                            melds.append([m_kan, 0])
                        else:
                            melds.append([m_kan, 6])
                    else:
                        if is_open:
                            melds.append([m, 0])
                        else:
                            hand.extend(m)
                            hand_idx_map.extend([i]*3)
            # 雀头直接加入手牌
            hand.extend(head)
            hand_idx_map.extend([100, 100])

        # 4. 验证番型
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        win_tile = random.choice(hand) if hand else 0
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            # 必须有两对称、镜同和、形同和、映同和之一
            if not set(fan_names) & {"两对称", "镜同和", "形同和", "映同和"}:
                continue
            if score < (min_fan * 4) and melds == []:
                continue
            if score < (min_fan * 4 - 8):
                continue
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
        except Exception:
            continue
    return None

def generate_symmetry_seven_pairs(min_fan=3, forced_wayEq0=False):
    """
    对称七对子生成器
    - 先选一个对子作为雀头，剩余六个对子作为面子
    - 面子分布：3:3（概率4/5），2:2:2（概率1/5）
    - 雀头权重分配：三个花色的3~7权重×5，如果3:3，门风与箭牌权重也×5
    - 结果必须有两对称|镜同和|形同和|映同和之一
    """
    max_attempts = 3000
    suits = [0, 9, 18]
    arrows = [31, 32, 33]

    for attempt in range(max_attempts):
        remain = [4] * 34

        # 面子分布
        is_33 = random.random() < 0.8
        if is_33:
            suit_choices = random.sample(suits, 2)
            face_pattern = [suit_choices[0]]*3 + [suit_choices[1]]*3
        else:
            suit_choices = random.sample(suits, 3)
            face_pattern = [suit_choices[0]]*2 + [suit_choices[1]]*2 + [suit_choices[2]]*2

        # 先生成所有对子（不重复）
        # 允许选门风和箭牌
        valid_tiles = []
        for s in set(suit_choices):
            valid_tiles.extend(list(range(s, s+9)))
        valid_tiles += [27,28,29,30,31,32,33]

        pairs = []
        for face_suit in face_pattern + ["head"]:  # 7个对子（最后一个是雀头）
            candidates = []
            weights = []
            if face_suit == "head":
                for i in valid_tiles:
                    if remain[i] >= 2:
                        # 雀头权重
                        weight = 1
                        if i in range(suits[0]+2,suits[0]+7) or i in range(suits[1]+2,suits[1]+7) or i in range(suits[2]+2,suits[2]+7):
                            weight *= 5
                        if is_33 and (i in arrows or i in [27,28,29,30]):
                            weight *= 5
                        candidates.append(i)
                        weights.append(weight)
            else:
                for i in range(face_suit, face_suit+9):
                    if remain[i] >= 2:
                        candidates.append(i)
                        weights.append(remain[i])
                # 允许偶尔选门风箭牌
                for i in [27,28,29,30,31,32,33]:
                    if remain[i] >= 2:
                        candidates.append(i)
                        weights.append(1)
            if not candidates:
                break
            chosen = weighted_choice(candidates, weights)
            if chosen is None:
                break
            pairs.append([chosen, chosen])
            remain[chosen] -= 2

        if len(pairs) != 7:
            continue

        head = pairs[-1]
        hand_pairs = pairs[:-1]

        # 构建手牌
        hand = []
        for pair in hand_pairs:
            hand.extend(pair)
        hand.extend(head)
        hand.sort()
        melds = []

        # 门风
        seatWindTile = random.choice(range(27, 31))
        way = determine_way_for_hand() if not forced_wayEq0 else 0
        win_tile = random.choice(hand) if hand else 0

        # 验证番型
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            # 必须有两对称、镜同和、形同和、映同和之一
            if not set(fan_names) & {"两对称", "镜同和", "形同和", "映同和"}:
                continue
            if score < (min_fan * 4 - 8):
                continue
            return hand, melds, pairs, seatWindTile, way, win_tile
        except Exception:
            continue
    return None

def generate_symmetry_combined(hand_type="standard", min_fan=3, forced_wayEq0=False):
    """
    对称生成器的统一入口
    根据手牌类型选择相应的生成方法
    """
    if hand_type == "seven_pairs":
        return generate_symmetry_seven_pairs(min_fan, forced_wayEq0)
    else:
        return generate_symmetry_hand(min_fan, forced_wayEq0)
    
#  满贯牌型生成函数

def generate_ziyise_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成字一色的手牌
    字一色：手牌全部由字牌组成
    """
    max_attempts = 1000
    
    # 字牌范围：27-33
    zi_tiles = list(range(27, 34))
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 生成四副刻子（字牌只能组刻子，不能组顺子）
        for _ in range(4):
            candidates = []
            weights = []
            
            for tile in zi_tiles:
                if remain[tile] >= 3:
                    candidates.append([tile, tile, tile])
                    weights.append(COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3)))
            
            if not candidates:
                break
                
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                break
                
            s = candidates[idx]
            sets.append(s)
            
            for t in s:
                remain[t] -= 1
        
        if len(sets) != 4:
            continue
            
        # 生成雀头（必须是字牌）
        head_candidates = []
        head_weights = []
        for tile in zi_tiles:
            if remain[tile] >= 2:
                head_candidates.append([tile, tile])
                head_weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "字一色" not in fan_names:
                continue
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_qingyaojiu_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成清幺九的手牌
    清幺九：全部由1、9的序数牌组成，无字牌
    """
    max_attempts = 1000
    
    # 清幺九有效牌：1m,9m,1s,9s,1p,9p
    qing_yao_tiles = [0, 8, 9, 17, 18, 26]
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 生成四副刻子（清幺九只能组刻子）
        for _ in range(4):
            candidates = []
            weights = []
            
            for tile in qing_yao_tiles:
                if remain[tile] >= 3:
                    candidates.append([tile, tile, tile])
                    weights.append(COMB_CACHE.get((remain[tile], 3), comb(remain[tile], 3)))
            
            if not candidates:
                break
                
            idx = weighted_choice(range(len(candidates)), weights)
            if idx is None:
                break
                
            s = candidates[idx]
            sets.append(s)
            
            for t in s:
                remain[t] -= 1
        
        if len(sets) != 4:
            continue
            
        # 生成雀头
        head_candidates = []
        head_weights = []
        for tile in qing_yao_tiles:
            if remain[tile] >= 2:
                head_candidates.append([tile, tile])
                head_weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "清幺九" not in fan_names:
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_sitongshun_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成四同顺的手牌
    四同顺：四副相同的顺子
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        
        # 随机选择一个顺子类型
        base_suits = [0, 9, 18]  # 条、筒、万
        shun_start = random.randint(0, 6)  # 1-7的顺子
        
        # 生成四副相同顺子
        sets = []
        for _ in range(4):
            suit_base = random.choice(base_suits)
            a, b, c = suit_base + shun_start, suit_base + shun_start + 1, suit_base + shun_start + 2
            
            if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                sets.append([a, b, c])
                remain[a] -= 1
                remain[b] -= 1
                remain[c] -= 1
            else:
                break
        
        if len(sets) != 4:
            continue
            
        # 生成雀头
        head_candidates = []
        head_weights = []
        for i in range(34):
            if remain[i] >= 2:
                head_candidates.append([i, i])
                head_weights.append(COMB_CACHE.get((remain[i], 2), comb(remain[i], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 顺子副露率0.4
            is_open = random.random() < 0.4
            
            if is_open:
                melds.append([m, 0])
                melds_count += 1
            else:
                hand.extend(m)
                hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "四同顺" not in fan_names:
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_qingyise_silianke_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成清一色&四连刻的手牌
    清一色：同一花色；四连刻：四个连续数字的刻子
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        
        # 随机选择花色
        suit_base = random.choice([0, 9, 18])  # 条、筒、万
        
        # 随机选择四连刻起始位置（1-6可以组成四连刻）
        ke_start = random.randint(0, 5)
        
        # 生成四个连续刻子
        sets = []
        for i in range(4):
            tile = suit_base + ke_start + i
            if remain[tile] >= 3:
                sets.append([tile, tile, tile])
                remain[tile] -= 3
            else:
                break
        
        if len(sets) != 4:
            continue
            
        # 生成雀头（必须是同花色）
        head_candidates = []
        head_weights = []
        for i in range(suit_base, suit_base + 9):
            if remain[i] >= 2:
                head_candidates.append([i, i])
                head_weights.append(COMB_CACHE.get((remain[i], 2), comb(remain[i], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "清一色" not in fan_names or "四连刻" not in fan_names:
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_liangduichen_ertongke_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成两对称&二同刻的手牌
    两对称&二同刻的结构：
    1. 选择两个奇偶性相同的序数作为刻子序数
    2. 二者的平均数作为雀头序数
    3. 每个刻子序数用两种花色（形成二同刻）
    4. 雀头花色任意
    
    例如：222m 222s 666m 666s 44p (刻子序数2,6，雀头序数4)
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 选择两个奇偶性相同的序数
        # 奇数组：1,3,5,7,9 (索引0,2,4,6,8)
        # 偶数组：2,4,6,8 (索引1,3,5,7)
        
        if random.random() < 0.5:
            # 选择奇数序数
            odd_numbers = [1, 3, 5, 7, 9]  # 序数
            selected_nums = random.sample(odd_numbers, 2)
        else:
            # 选择偶数序数
            even_numbers = [2, 4, 6, 8]  # 序数
            selected_nums = random.sample(even_numbers, 2)
        
        # 计算雀头序数（平均数）
        head_num = (selected_nums[0] + selected_nums[1]) // 2
        
        # 验证平均数是否为整数且在有效范围内
        if head_num < 1 or head_num > 9:
            continue
        
        # 为每个刻子序数选择两种不同花色
        suits = [0, 9, 18]  # 条、筒、万
        
        for num in selected_nums:
            # 为这个序数选择两种花色
            selected_suits = random.sample(suits, 2)
            
            for suit_base in selected_suits:
                tile = suit_base + (num - 1)  # 序数转换为牌号
                if remain[tile] >= 3:
                    sets.append([tile, tile, tile])
                    remain[tile] -= 3
                else:
                    break
            else:
                continue
            break
        
        if len(sets) != 4:
            continue
        
        # 生成雀头（指定序数，任意花色）
        head_candidates = []
        head_weights = []
        
        for suit_base in suits:
            head_tile = suit_base + (head_num - 1)  # 序数转换为牌号
            if remain[head_tile] >= 2:
                head_candidates.append([head_tile, head_tile])
                head_weights.append(COMB_CACHE.get((remain[head_tile], 2), comb(remain[head_tile], 2)))
        
        # 如果指定序数的牌不够，也可以选择其他牌做雀头
        if not head_candidates:
            for i in range(34):
                if remain[i] >= 2:
                    head_candidates.append([i, i])
                    head_weights.append(COMB_CACHE.get((remain[i], 2), comb(remain[i], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否同时有两对称和二同刻
            has_liangduicheng = "两对称" in fan_names
            has_ertongke = "二同刻" in fan_names
            
            if not (has_liangduicheng and has_ertongke):
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_sizike_sangang_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成四自刻&三杠的手牌
    四自刻：四个刻子（暗刻/明杠/暗杠）；三杠：三个杠
    """
    max_attempts = 5
    
    for attempt in range(max_attempts):       
        # 1. 直接从34张牌中选择5种不同的牌
        selected_tiles = random.sample(range(34), 5)
        
        # 前4种做刻子，最后1种做雀头
        ke_tiles = selected_tiles[:4]
        head_tile = selected_tiles[4]
    
        
        # 2. 构建面子
        sets = []
        
        # 前三种牌：强制杠（明杠/暗杠，概率7:3）
        for i in range(3):
            tile = ke_tiles[i]
            sets.append([tile, tile, tile, tile])
        
        # 第四种牌：暗刻/明杠/暗杠（暗刻概率50%，杠概率50%）
        tile = ke_tiles[3]
        if random.random() < 0.5:
            # 暗刻：只用3张，归还1张
            sets.append([tile, tile, tile])
        else:
            # 杠：用4张
            sets.append([tile, tile, tile, tile])
        
        # 3. 生成雀头
        head = [head_tile, head_tile]

        # 4. 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        
        for i, m in enumerate(sets):
            if len(m) == 4:  # 杠
                if i < 3:
                    # 前三个杠：明杠概率70%，暗杠概率30%
                    is_open = random.random() < 0.7
                else:
                    # 第四个杠：明杠概率60%，暗杠概率40%
                    is_open = random.random() < 0.6
                
                if is_open:
                    melds.append([m, 0])  # 明杠
                else:
                    melds.append([m, 6])  # 暗杠
            else:  # 普通刻子（必须暗刻才能算自刻）
                hand.extend(m)
                hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            # 检查是否有四自刻和三杠（或四杠）
            has_sizike = "四自刻" in fan_names
            has_sangang = "三杠" in fan_names or "四杠" in fan_names
            
            if not (has_sizike and has_sangang):
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_hunyaojiu_xiaosixi_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成混幺九&小四喜的手牌
    混幺九：全部由1、9、字牌组成；小四喜：三副风刻+一对风
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 小四喜：选择3个风做刻子，1个风做雀头
        feng_tiles = [27, 28, 29, 30]  # 东南西北
        random.shuffle(feng_tiles)
        
        # 前3个风做刻子
        for i in range(3):
            tile = feng_tiles[i]
            sets.append([tile, tile, tile])
            remain[tile] -= 3
        
        # 第4个风做雀头
        head = [feng_tiles[3], feng_tiles[3]]
        remain[feng_tiles[3]] -= 2
        
        # 剩余一个面子，必须是幺九牌
        yao_jiu_remaining = [0, 8, 9, 17, 18, 26, 31, 32, 33]  # 排除已用的风牌
        ke_candidates = []
        for tile in yao_jiu_remaining:
            if remain[tile] >= 3:
                ke_candidates.append(tile)
        
        if not ke_candidates:
            continue
            
        last_tile = random.choice(ke_candidates)
        sets.append([last_tile, last_tile, last_tile])
        remain[last_tile] -= 3

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "混幺九" not in fan_names or "小四喜" not in fan_names:
                continue
                
            if score >= 88:
                return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_dasixi_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成大四喜的手牌
    大四喜：四副风刻
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 大四喜：四个风都做刻子
        feng_tiles = [27, 28, 29, 30]  # 东南西北
        
        for tile in feng_tiles:
            sets.append([tile, tile, tile])
            remain[tile] -= 3
        
        # 生成雀头（不能是风牌）
        head_candidates = []
        head_weights = []
        for i in range(34):
            if i not in feng_tiles and remain[i] >= 2:
                head_candidates.append([i, i])
                head_weights.append(COMB_CACHE.get((remain[i], 2), comb(remain[i], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "大四喜" not in fan_names:
                continue
                
            return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_hunyise_hunyaojiu_dasanyuan_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成混幺九&混一色&大三元的手牌
    混幺九：全部由1、9、字牌组成；混一色：一种花色+字牌；大三元：三副箭刻
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        remain = [4] * 34
        sets = []
        
        # 大三元：三个箭牌做刻子
        jian_tiles = [31, 32, 33]  # 红中、发财、白板
        
        for tile in jian_tiles:
            sets.append([tile, tile, tile])
            remain[tile] -= 3
        
        # 随机选择一种花色
        suit_base = random.choice([0, 9, 18])
        suit_yao_tiles = [suit_base, suit_base + 8]  # 该花色的1和9
        
        # 剩余一个面子，必须是该花色的1或9
        ke_candidates = []
        for tile in suit_yao_tiles:
            if remain[tile] >= 3:
                ke_candidates.append(tile)
        
        if not ke_candidates:
            continue
            
        last_tile = random.choice(ke_candidates)
        sets.append([last_tile, last_tile, last_tile])
        remain[last_tile] -= 3
        
        # 生成雀头（必须是该花色的1或9，或剩余字牌）
        head_candidates = []
        head_weights = []
        valid_head_tiles = suit_yao_tiles + [27, 28, 29, 30]  # 花色1,9+风牌
        
        for tile in valid_head_tiles:
            if remain[tile] >= 2:
                head_candidates.append([tile, tile])
                head_weights.append(COMB_CACHE.get((remain[tile], 2), comb(remain[tile], 2)))
        
        if not head_candidates:
            continue
            
        head = weighted_choice(head_candidates, head_weights)
        if head is None:
            continue

        # 构建手牌和副露
        hand = []
        melds = []
        hand_idx_map = []
        melds_count = 0
        
        for i, m in enumerate(sets):
            # 刻子副露率0.6，杠牌率0.2
            is_open = random.random() < 0.6
            is_kan = random.random() < 0.2
            
            if is_kan and remain[m[0]] >= 1:
                m_kan = m + [m[0]]
                remain[m[0]] -= 1
                if is_open:
                    melds.append([m_kan, 0])
                    melds_count += 1
                else:
                    melds.append([m_kan, 6])
                    melds_count += 1
            else:
                if is_open:
                    melds.append([m, 0])
                    melds_count += 1
                else:
                    hand.extend(m)
                    hand_idx_map.extend([i]*3)
        
        hand.extend(head)
        hand_idx_map.extend([100, 100])

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand) if hand else 0
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            required_fans = ["混幺九", "混一色", "大三元"]
            if not all(fan in fan_names for fan in required_fans):
                continue
                
            if score >= 88:
                return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None

def generate_jiulianbaodeng_hand(min_fan=3, forced_wayEq0=False):
    """
    专门生成九莲宝灯的手牌
    九莲宝灯：清一色，1112345678999 + 任意一张同花色牌
    """
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        # 随机选择花色
        suit_base = random.choice([0, 9, 18])
        
        # 九莲宝灯固定结构：1112345678999
        base_tiles = []
        # 三张1
        base_tiles.extend([suit_base] * 3)
        # 一张2-8
        for i in range(1, 8):
            base_tiles.append(suit_base + i)
        # 三张9
        base_tiles.extend([suit_base + 8] * 3)
        
        # 随机添加一张同花色牌作为第14张
        extra_tile = random.choice(range(suit_base, suit_base + 9))
        hand = base_tiles + [extra_tile]
        
        # 九莲宝灯必须门前清
        melds = []
        hand_idx_map = [0] * 14  # 简化索引

        way = determine_way_for_hand() if not forced_wayEq0 else 0
        seatWindTile = random.choice(range(27, 31))
        win_tile = random.choice(hand)
        
        fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
        try:
            score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
            
            if "九莲宝灯" not in fan_names:
                continue
                
            if score >= 88:
                return hand, melds, hand_idx_map, seatWindTile, way, win_tile
            
        except Exception as e:
            continue
                
    return None
