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

from specialfanslib import *

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

def calc_fan_by_fanqi_input(fanqi_str):
    """优化的算番器调用"""
    try:
        score = all_calc(fanqi_str, show_detail=False)
        return {"score": score, "input": fanqi_str}
    except Exception as e:
        return {"score": 0, "fan": 0, "detail": f"算番器调用失败:{e}", "input": fanqi_str}

# ===== 优化的可视化输出工具 =====
def tile_str(t):
    # 条：0~8, 筒：9~17, 万：18~26, 字：27~33（1z~7z）
    if 0 <= t <= 8:
        return red(f"{t%9+1}m")
    elif 9 <= t <= 17:
        return green(f"{t%9+1}s")
    elif 18 <= t <= 26:
        return cyan(f"{t%9+1}p")
    elif 27 <= t <= 33:
        return white(f"{t-26}z")
    else:
        return str(t)

def tile_list_str(lst):
    """优化的牌列表显示"""
    if not lst:
        return ""
    sorted_lst = sorted(lst) if lst != sorted(lst) else lst
    return " ".join(tile_str(x) for x in sorted_lst)

def tile_str_html(t):
    """HTML格式牌张显示"""
    return TILE_TO_HTML_CACHE.get(t, str(t))

def tile_list_str_html(lst):
    """HTML格式牌列表显示"""
    if not lst:
        return ""
    sorted_lst = sorted(lst) if lst != sorted(lst) else lst
    return " ".join(TILE_TO_HTML_CACHE.get(x, str(x)) for x in sorted_lst)

# ========== 修复后的生成手牌相关函数 ==========

def parse_fan_func(fan_func):
    """
    支持括号、&（且）、|（或），None表示无条件。
    返回一个函数，输入fan_names（番型名列表），输出True/False。
    用法示例：
      parse_fan_func("三步高")                # 只要有三步高
      parse_fan_func("三步高&门前清")         # 必须同时有三步高和门前清
      parse_fan_func("三步高|碰碰和")         # 有三步高或有碰碰和
      parse_fan_func("三步高&门前清|碰碰和")   # (三步高且门前清) 或 碰碰和
      parse_fan_func("三步高&(门前清|碰碰和)") # 三步高且(门前清或碰碰和)
    """

    if fan_func is None:
        return lambda fan_names: True

    expr = fan_func.replace(" ", "")  # 去空格

    # 番型名可能包含汉字、字母、数字（不包含&|()），所以拆词用正则
    token_pat = re.compile(r'[\u4e00-\u9fa5\w]+|[&|()]')
    tokens = token_pat.findall(expr)

    # 转为逆波兰表达式（RPN），标准运算符优先级：括号 > & > |
    def to_rpn(tokens):
        output = []
        stack = []
        precedence = {'|':1, '&':2}
        for token in tokens:
            if token not in "&|()":
                output.append(token)
            elif token in '&|':
                while stack and stack[-1] in '&|' and precedence[stack[-1]] >= precedence[token]:
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:  # 弹出左括号
                    stack.pop()
        while stack:
            output.append(stack.pop())
        return output

    rpn = to_rpn(tokens)

    # RPN求值，输入fan_names，输出True/False
    def checker(fan_names):
        stack = []
        for token in rpn:
            if token not in "&|":
                stack.append(token in fan_names)
            elif token == '&':
                if len(stack) >= 2:
                    b = stack.pop()
                    a = stack.pop()
                    stack.append(a and b)
                else:
                    return False
            elif token == '|':
                if len(stack) >= 2:
                    b = stack.pop()
                    a = stack.pop()
                    stack.append(a or b)
                else:
                    return False
        return stack[0] if stack else True
    
    return checker

def generate_complete_hand(
    hand_type="standard",  # 可选值: "standard", "seven_pairs", "thirteen_orphans"
    fan_func=None, 
    min_fan=3, 
    max_attempts=10000, 
    special=False, 
    return_melds=True, 
    forced_wayEq0=False
):
    """
    统一的和牌生成函数：支持标准和牌、七对子、十三幺
    
    Args:
        hand_type: 生成手牌类型 ("standard", "seven_pairs", "thirteen_orphans")
        fan_func: 番型筛选表达式
        min_fan: 最低番数
        max_attempts: 最大尝试次数
        special: 是否为特殊和牌型
        return_melds: 是否返回副露信息
        forced_wayEq0: 是否强制和牌方式为0

    Returns:
        统一返回格式 (6项): (hand, melds, melds_idx_map, seatWindTile, way, win_tile)
        - 标准和牌: hand=手牌列表, melds=副露列表, melds_idx_map=面子映射
        - 七对子: hand=手牌列表, melds=[], melds_idx_map=pairs列表
        - 十三幺: hand=手牌列表, melds=[], melds_idx_map=[yaochu, pair]
    """
    
    # 解析番型筛选条件
    fan_checker = parse_fan_func(fan_func)

    # **添加满贯专门逻辑**
    if min_fan >= 27:
        # 先尝试专门的满贯生成
        for _ in range(max_attempts // 3 * 2):  # 用三分之二的尝试次数
            if fan_func == "字一色":
                res = generate_ziyise_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "清幺九":
                res = generate_qingyaojiu_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "四同顺":
                res = generate_sitongshun_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "清一色 & 四连刻":
                res = generate_qingyise_silianke_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "两对称 & 二同刻":
                res = generate_liangduichen_ertongke_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "四自刻 & 三杠 | 四杠":
                res = generate_sizike_sangang_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "混幺九 & 小四喜":
                res = generate_hunyaojiu_xiaosixi_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "大四喜":
                res = generate_dasixi_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "混一色 & 混幺九 & 大三元":
                res = generate_hunyise_hunyaojiu_dasanyuan_hand(forced_wayEq0=forced_wayEq0)
            elif fan_func == "九莲宝灯":
                res = generate_jiulianbaodeng_hand(forced_wayEq0=forced_wayEq0)

            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue 
    
    # **添加五门齐专门逻辑**
    if hand_type == "standard" and fan_func and "五门齐" in fan_func:
        # 先尝试专门的五门齐生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_wumenqi_hand(min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue

    # **添加九数齐专门逻辑**
    if hand_type == "standard" and fan_func and "九数齐" in fan_func:
        # 先尝试专门的九数齐生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_jiushuqi_hand(min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue

    # **添加混带幺专门逻辑**
    if hand_type == "standard" and fan_func and "混带幺" in fan_func:
        # 先尝试专门的九数齐生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_hundaiyao_hand(min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue

    # **添加聚数专门逻辑**
    if ("聚三数" in fan_func or "聚四数" in fan_func) and hand_type != "thirteen_orphans":
        # 先尝试专门的聚数生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_jushu_combined(hand_type=hand_type, min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue

    # **添加一色专门逻辑**
    if ("清一色" in fan_func or "混一色" in fan_func) and hand_type != "thirteen_orphans":
        # 先尝试专门的一色生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_yise_combined(hand_type=hand_type, min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue

    # **添加对称专门逻辑**
    if ("两对称" in fan_func or "镜同和" in fan_func or "形同和" in fan_func or "映同和" in fan_func) and\
        hand_type != "thirteen_orphans":
        # 先尝试专门的对称生成
        for _ in range(max_attempts // 3):  # 用三分之一的尝试次数
            res = generate_symmetry_combined(hand_type=hand_type, min_fan=min_fan, forced_wayEq0=forced_wayEq0)
            if res:
                hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if fan_checker(fan_names):
                        return hand, melds, melds_idx_map, seatWindTile, way, win_tile
                except Exception:
                    continue
    
    # 通用生成逻辑
    if hand_type == "seven_pairs":
        # 七对子生成逻辑
        for _ in range(max_attempts):
            remain = [4] * 34
            pairs = []
            
            for pair_num in range(7):
                candidates = []
                weights = []
                for i in range(34):
                    if remain[i] >= 2:
                        w = COMB_CACHE.get((remain[i], 2), comb(remain[i], 2))
                        candidates.append(i)
                        weights.append(w)
                
                if not candidates:
                    break
                    
                idx = weighted_choice(candidates, weights)
                if idx is None:
                    break
                pairs.append([idx, idx])
                remain[idx] -= 2
            else:
                hand = []
                for pair in pairs:
                    hand.extend(pair)
                hand.sort()
                melds = []
                
                # 确定和牌方式并验证番数
                way = determine_way_for_hand() if not forced_wayEq0 else 0
                seatWindTile = random.choice(range(27, 31))
                win_tile = random.choice(hand) if hand else 0
                
                fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
                try:
                    score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                    if score < (min_fan * 4 - 8):
                        continue
                    
                    # 番型表达式判定
                    if not fan_checker(fan_names):
                        continue
                    
                    return hand, melds, pairs, seatWindTile, way, win_tile
                except Exception as e:
                    continue
        return None
    
    else:  # hand_type == "standard"
        for attempt in range(max_attempts):
            remain = [4] * 34
            sets = []
            set_types = []
            
            # 生成四副面子
            for _ in range(4):
                candidates = []
                weights = []
                set_type_marks = []
                
                if fan_func is None or ("碰碰和" not in fan_func):
                    # 生成所有可能的顺子
                    for base in SHUN_BASES:
                        for i in range(7):
                            a, b, c = base+i, base+i+1, base+i+2
                            if remain[a] > 0 and remain[b] > 0 and remain[c] > 0:
                                comb_weight = remain[a] * remain[b] * remain[c]
                                final_weight = 1 * comb_weight
                                candidates.append([a, b, c])
                                weights.append(final_weight)
                                set_type_marks.append("shun")
                
                # 生成所有可能的刻子
                for i in range(34):
                    if remain[i] >= 3:
                        comb_weight = COMB_CACHE.get((remain[i], 3), comb(remain[i], 3))
                        final_weight = 2 * comb_weight
                        candidates.append([i, i, i])
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
                
            # 生成雀头
            head_cands = []
            head_weights = []
            for i in range(34):
                if remain[i] >= 2:
                    w = COMB_CACHE.get((remain[i], 2), comb(remain[i], 2))
                    if w > 0:
                        head_cands.append([i, i])
                        head_weights.append(w)
            
            if not head_cands:
                continue
                
            head = weighted_choice(head_cands, head_weights)
            if head is None:
                continue

            # 副露与杠逻辑 - 修复版本
            hand = []
            melds = []
            hand_idx_map = []  # 只记录手牌的索引映射
            melds_count = 0
            
            random_values = [random.random() for _ in range(len(sets) * 2)]
            rand_idx = 0
            
            for i, m in enumerate(sets):
                t = set_types[i]
                if t == "shun":
                    is_open = random_values[rand_idx] < 0.45
                    rand_idx += 1
                    if is_open and (fan_func is None or "门前清" not in fan_func):
                        # 副露：不加入手牌，加入melds
                        melds.append([m, 0])
                        melds_count += 1
                    else:
                        # 手牌：加入手牌，记录索引
                        hand.extend(m)
                        hand_idx_map.extend([i]*3)  # 面子ID
                elif t == "ke":
                    is_open = random_values[rand_idx] < 0.65
                    is_kan = random_values[rand_idx + 1] < 0.2
                    rand_idx += 2
                    
                    if is_kan and remain[m[0]] >= 1:
                        m_kan = m + [m[0]]
                        remain[m[0]] -= 1
                        if is_open:
                            # 明杠：不加入手牌
                            melds.append([m_kan, 0])
                            melds_count += 1
                        else:
                            # 暗杠：不加入手牌
                            melds.append([m_kan, 6])
                            melds_count += 1
                    else:
                        if is_open:
                            # 明刻：不加入手牌
                            melds.append([m, 0])
                            melds_count += 1
                        else:
                            # 手牌刻子：加入手牌
                            hand.extend(m)
                            hand_idx_map.extend([i]*3)  # 面子ID
            
            # 添加雀头到手牌
            hand.extend(head)
            hand_idx_map.extend([100, 100])  # 雀头标记

            # 验证：hand_idx_map 长度应该等于 hand 长度
            if len(hand_idx_map) != len(hand):
                continue
            
            # 验证：hand_idx_map 不应该有负数
            if any(idx < 0 for idx in hand_idx_map):
                continue

            # 确定和牌方式并验证番数
            way = determine_way_for_hand() if not forced_wayEq0 else 0
            seatWindTile = random.choice(range(27, 31))
            win_tile = random.choice(hand) if hand else 0
            
            fanqi_str = to_fanqi_input(hand, melds, seatWindTile, way, win_tile)
            try:
                score, fan_names = all_calc(fanqi_str, show_detail=False, return_name=True)
                
                if not fan_checker(fan_names):
                    continue
                    
                if score < (min_fan * 4) and melds == []:
                    continue
                if score < (min_fan * 4 - 8):
                    continue
                
                # 返回修正后的格式：hand_idx_map 就是 melds_idx_map
                result = (hand, melds, hand_idx_map, seatWindTile, way, win_tile)
                return result
                
            except Exception as e:
                continue
                
        return None

# 同样更新听牌生成函数
def generate_tenpai_by_complete(
    hand_type="standard",  # 可选值: "standard", "seven_pairs", "thirteen_orphans"
    fan_func=None, 
    min_fan=3, 
    max_attempts=10000, 
    special=False
):
    """
    统一的听牌生成函数：支持标准听牌、七对子听牌、十三幺听牌
    
    Returns:
        统一返回格式 (6项): (wait_hand, win_tile, complete_hand, melds, extra_data, seatWindTile)
        - 标准听牌: extra_data=None
        - 七对子听牌: extra_data=pairs
        - 十三幺听牌: extra_data=yaochu_data
    """
    
    if hand_type == "seven_pairs":
        for _ in range(max_attempts):
            res = generate_complete_hand(hand_type="seven_pairs", fan_func=fan_func, min_fan=min_fan)
            if not res:
                continue
            hand, melds, pairs, seatWindTile, way, win_tile = res

            if len(pairs) != 7:
                continue

            # 从手牌中随机去掉一张牌，形成13张的听牌状态
            remove_idx = random.randint(0, len(hand) - 1)
            wait_hand = hand[:remove_idx] + hand[remove_idx+1:]
            win_tile = hand[remove_idx]

            fanqi_str = to_fanqi_input(wait_hand, [], seatWindTile, 0)
            score = all_calc(fanqi_str, show_detail=False)
            if score < (min_fan * 3 - 6):
                continue
            return wait_hand, win_tile, hand, [], pairs, seatWindTile
        return None, None, None, None, None, None
    
    elif hand_type == "thirteen_orphans":
        for _ in range(max_attempts):
            tenpai_type = random.choice(["single_wait", "thirteen_wait"])
            
            if tenpai_type == "single_wait":
                available_yaochu = YAOCHU_TILES.copy()
                pair_tile = random.choice(available_yaochu)
                available_yaochu.remove(pair_tile)
                wait_tile = random.choice(available_yaochu)
                available_yaochu.remove(wait_tile)
                hand = [pair_tile, pair_tile] + available_yaochu
                win_tile = wait_tile
            else:  # thirteen_wait
                hand = YAOCHU_TILES.copy()
                win_tile = random.choice(YAOCHU_TILES)
            
            if len(hand) != 13:
                continue
            
            way = 0
            seatWindTile = random.choice(range(27, 31))
            
            fanqi_str = to_fanqi_input(hand, [], seatWindTile, way)
            try:
                score = all_calc(fanqi_str, show_detail=False)
                if score < (min_fan * 3 - 6):
                    continue
                
                complete_hand = hand + [win_tile]
                yaochu_data = [YAOCHU_TILES, [win_tile, win_tile] if tenpai_type == "single_wait" else [win_tile]]
                
                return hand, win_tile, complete_hand, [], yaochu_data, seatWindTile
            except Exception as e:
                continue
        return None, None, None, None, None, None
    
    else:  # hand_type == "standard"
        for _ in range(max_attempts):
            res = generate_complete_hand(hand_type="standard", fan_func=fan_func, min_fan=min_fan, 
                                        max_attempts=max_attempts, special=special, forced_wayEq0=True)
            if not res:
                continue
            hand, melds, melds_idx_map, seatWindTile, way, win_tile = res
            
            hand_tiles_count = len(hand)
            melds_tiles_count = len(melds) * 3
            total_tiles = hand_tiles_count + melds_tiles_count
            
            if total_tiles != 14:
                continue
                
            if not hand:
                continue
            
            remove_idx = random.randint(0, len(hand) - 1)
            wait_hand = hand[:remove_idx] + hand[remove_idx+1:]
            win_tile = hand[remove_idx]
            
            final_hand_count = len(wait_hand)
            final_melds_count = len(melds) * 3
            final_total = final_hand_count + final_melds_count
            
            if final_total != 13:
                continue
            
            fanqi_str = to_fanqi_input(wait_hand, melds, seatWindTile, 0)
            score = all_calc(fanqi_str, show_detail=False)
            if score < (min_fan * 3 - 6):
                continue
            return wait_hand, win_tile, hand, melds, None, seatWindTile
        return None, None, None, None, None, None

# 同样更新一向听和弱一向听
def generate_issyanten_by_complete(fan_func=None, min_fan=3, max_attempts=10000, special=False):
    """修正版：只在hand内，且删除的两张分属不同面子"""
    
    for attempt in range(max_attempts):
        res = generate_complete_hand(hand_type="standard", fan_func=fan_func, min_fan=min_fan, 
                                    max_attempts=max_attempts, special=special, forced_wayEq0=True)
        if not res:
            continue
            
        hand, melds, hand_idx_map, seatWindTile, way, win_tile = res

        # 计算总牌数和检查逻辑
        total_tiles = len(hand) + 3 * len(melds)
        if total_tiles != 14:
            continue
            
        # 检查手牌中是否有足够的不同面子的牌
        if len(hand) < 3:
            continue

        # 验证：不应该有负数
        if any(idx < 0 for idx in hand_idx_map):
            continue

        # 随机选两个不同面子的牌删掉
        tries = 0
        while tries < 100:
            idx1, idx2 = random.sample(range(len(hand)), 2)
            # 修复：现在所有值都应该>=0，要求不同即可
            if hand_idx_map[idx1] != hand_idx_map[idx2]:
                break
            tries += 1
        
        if tries >= 100:
            continue

        base12 = [hand[i] for i in range(len(hand)) if i not in (idx1, idx2)]

        # 找一张新牌补进来
        candidate_adds = [i for i in range(34) if base12.count(i) < 4]
        if not candidate_adds:
            continue
        add = random.choice(candidate_adds)
        h13 = sorted(base12 + [add])

        total_count = len(h13) + len(melds) * 3
        if total_count != 13:
            continue

        fanqi_str = to_fanqi_input(h13, melds, seatWindTile, 0)
        score = all_calc(fanqi_str, show_detail=False)
        if score < (min_fan * 2 - 4):
            continue
            
        return h13, hand, melds, seatWindTile
        
    return None, None, None, None

def generate_weak_issyanten_by_complete(fan_func=None, min_fan=3, max_attempts=10000):
    """优化的弱一向听生成"""
    for _ in range(max_attempts):
        res = generate_complete_hand(hand_type="seven_pairs", fan_func=fan_func, min_fan=min_fan)
        if not res:
            continue
        hand, melds, pairs, seatWindTile, way, win_tile = res
        
        # 从7对子中选择2对，每对取1张，形成12张基础
        idx1, idx2 = random.sample(range(7), 2)
        base12 = []
        for i, pair in enumerate(pairs):
            if i == idx1 or i == idx2:
                base12.append(pair[0])  # 只取一张
            else:
                base12.extend(pair)  # 取两张
                
        # 添加一张新牌形成13张
        add_candidates = [i for i in range(34) if base12.count(i) < 4]
        if not add_candidates:
            continue
        add = random.choice(add_candidates)
        h13 = base12 + [add]
        h13.sort()
        
        if len(h13) != 13:
            continue
            
        fanqi_str = to_fanqi_input(h13, [], seatWindTile, 0)
        score = all_calc(fanqi_str, show_detail=False)
        if score < (min_fan - 2):
            continue
        return h13, pairs, seatWindTile
    return None, None, None