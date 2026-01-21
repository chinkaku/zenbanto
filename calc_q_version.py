'''
自然麻将算番器 - 修复版

牌张: 123456789m, 123456789s, 123456789p, 1234567z
门风: ! - 东, @ - 南, # - 西, $ - 北
和牌: % - 自摸, ^ - 杠上开花/抢杠和, & - 柳暗花明, * - 一巡和
副露: [] - 暗杠, () - 其余

如果手牌数模3余2, 则输入的最后一张牌视为和张.

输入示例: (789m)(123p)4455666s5s!%
'''

from mahjonglib import *
import re
import fan_calc
import copy
import io
import sys
from functools import lru_cache

# 缓存解析结果
@lru_cache(maxsize=1000)
def cached_parse_input(s):
    """缓存的输入解析"""
    melds = []
    s_meld = s
    
    # 解析副露
    for m in re.findall(r'\([^\)]*\)|\[[^\]]*\]', s):
        tilestr = m[1:-1]
        meld = stringToIndices(tilestr, tile_list)
        if m.startswith('['):
            melds.append((tuple(meld), 6))  # 暗杠 - 使用元组
        else:
            melds.append((tuple(meld), 0))  # 其他副露 - 使用元组
        s_meld = s_meld.replace(m, '')
    
    # 解析门风
    seatWindTile = 27   # 默认东风
    for c, idx in {'!':27, '@':28, '#':29, '$':30}.items():
        if c in s_meld:
            seatWindTile = idx
            s_meld = s_meld.replace(c, '')
            break
    
    # 解析和牌方式
    way = 0
    for c, v in {'%':1, '^':2, '&':4, '*':8}.items():
        if c in s_meld:
            way += v
            s_meld = s_meld.replace(c, '')
    
    # 解析手牌
    hand = stringToIndices(s_meld, tile_list)
    
    return tuple(hand), tuple(melds), seatWindTile, way

def parse_input(s):
    """解析输入字符串"""
    hand_tuple, melds_tuple, seatWindTile, way = cached_parse_input(s)
    
    # 转换回列表格式
    hand = list(hand_tuple)
    melds = []
    for meld_tuple in melds_tuple:
        tiles, meld_type = meld_tuple
        melds.append([list(tiles), meld_type])
    
    return hand, melds, seatWindTile, way

@lru_cache(maxsize=500)
def cached_validate_hand(hand_tuple, melds_tuple):
    """缓存的手牌验证 - 修复版"""
    hand = list(hand_tuple)
    melds = []
    for meld_tuple in melds_tuple:
        tiles, meld_type = meld_tuple
        melds.append([list(tiles), meld_type])
    
    # 检查手牌数量
    total_tiles = len(hand) + 3 * len(melds)
    if total_tiles not in [13, 14]:
        return False, f'手牌数量应为13或14张，当前{total_tiles}张'
    
    # 检查牌数量限制
    from collections import Counter
    tile_count = Counter(hand)
    for meld in melds:
        for tile in meld[0]:
            tile_count[tile] += 1
    
    for tile, count in tile_count.items():
        if count > 4:
            return False, f'{tile_list[tile]}数量超过4张（{count}张）'
    
    # 验证副露合法性
    for meld in melds:
        tiles = meld[0]
        if len(tiles) == 3:  # 顺子或刻子
            if tiles[0] == tiles[1] == tiles[2]:
                continue  # 刻子
            else:  # 顺子
                sorted_tiles = sorted(tiles)
                if (sorted_tiles[0] < 27 and  # 数字牌
                    sorted_tiles[0] // 9 == sorted_tiles[1] // 9 == sorted_tiles[2] // 9 and
                    sorted_tiles == [sorted_tiles[0], sorted_tiles[0]+1, sorted_tiles[0]+2]):
                    continue
                else:
                    return False, f"副露牌组不合法: {strlist(tiles)}"
        elif len(tiles) == 4:  # 杠子
            if tiles[0] == tiles[1] == tiles[2] == tiles[3]:
                continue
            else:
                return False, f"杠子牌组不合法: {strlist(tiles)}"
        else:
            return False, f"副露牌组数量不正确: {strlist(tiles)}"
    
    return True, ''

def check_hand_valid(hand, melds):
    """检查手牌有效性"""
    hand_tuple = tuple(hand)
    # 将melds转换为可哈希的元组格式
    melds_tuple = tuple((tuple(meld[0]), meld[1]) for meld in melds)
    return cached_validate_hand(hand_tuple, melds_tuple)

@lru_cache(maxsize=500)
def cached_calc_14_tiles(hand_tuple, melds_tuple, seatWindTile, way):
    """缓存的14张牌计算 - 修复版"""
    hand = list(hand_tuple)
    melds = []
    for meld_tuple in melds_tuple:
        tiles, meld_type = meld_tuple
        melds.append([list(tiles), meld_type])
    
    result = fan_calc.calc_fan_common(hand, melds, seatWindTile, way)
    if result:
        return result[1], tuple(tuple(group) if isinstance(group, list) else group for group in result[0])  # fan, groups (转为可哈希)
    return None, None

@lru_cache(maxsize=500)
def cached_calc_13_tiles(hand_tuple, melds_tuple, seatWindTile):
    """缓存的13张牌状态计算 - 修复版"""
    hand = list(hand_tuple)
    melds = []
    for meld_tuple in melds_tuple:
        tiles, meld_type = meld_tuple
        melds.append([list(tiles), meld_type])
    
    # 计算各种状态
    draw_result = fan_calc.calcTFforDraw(hand, melds, seatWindTile, 0)
    semidraw_result = fan_calc.calcTFforSemidraw(hand, melds, seatWindTile, 0)
    weak_semidraw_result = fan_calc.calcTFforWeakSemidraw(hand, melds, seatWindTile, 0)
    
    # 计算分数
    drawScore = 3 * draw_result[1] - 6 if draw_result else 0
    semidrawScore = 2 * semidraw_result[4] - 4 if semidraw_result else 0
    weakSemidrawScore = weak_semidraw_result[4] - 2 if weak_semidraw_result else 0
    
    # 将结果转换为可哈希格式再返回
    draw_result_hashable = tuple(draw_result) if draw_result else None
    semidraw_result_hashable = tuple(semidraw_result) if semidraw_result else None
    weak_semidraw_result_hashable = tuple(weak_semidraw_result) if weak_semidraw_result else None
    
    return drawScore, semidrawScore, weakSemidrawScore, draw_result_hashable, semidraw_result_hashable, weak_semidraw_result_hashable

def get_calc_detail(hand, melds, seatWindTile, way, result_type, groups=None):
    """获取计算详情: 返回结构化的番种数据"""
    try:
        buf = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf

        if result_type == "和牌" and groups:
            # 14张牌和牌详情
            finalGroup = copy.deepcopy(list(list(group) if isinstance(group, tuple) else group for group in groups))
            for meld in melds:
                if len(meld[0]) == 4:
                    finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                else:
                    finalGroup.append(meld[0])
            fan_calc.calcTF(finalGroup, seatWindTile, melds, hand[:-1], list(groups), hand[-1], way, print_fan_details=True)
        elif result_type == "听牌":
            fan_calc.calcTFforDraw(hand, melds, seatWindTile, 1)
        elif result_type == "一向听":
            fan_calc.calcTFforSemidraw(hand, melds, seatWindTile, 1)
        elif result_type == "弱一向听":
            fan_calc.calcTFforWeakSemidraw(hand, melds, seatWindTile, 1)

        sys.stdout = sys_stdout
        detail = buf.getvalue()
        buf.close()

        # 解析输出
        return parse_calc_output(detail)
    except Exception as e:
        sys.stdout = sys_stdout
        return {"error": f"获取详情时出错: {str(e)}"}

def parse_calc_output(output):
    """
    解析calcTF系列输出，提取番种名称、番值、总分等信息
    """
    lines = output.splitlines()
    result = {
        "status": None,
        "high_tile": None,
        "fan_details": [],
        "total_fan": 0,
        "total_score": 0,
    }

    # 解析状态和高目
    for line in lines:
        if line.startswith("状态:"):
            result["status"] = line.split("状态:")[1].strip()
        elif line.startswith("高目:"):
            result["high_tile"] = line.split("高目:")[1].strip()

    # 解析番种和番值
    in_fan_section = False
    for line in lines:
        if line.startswith("===================="):
            in_fan_section = not in_fan_section
            continue
        if in_fan_section and "(" in line and "番)" in line:
            try:
                name, value = line.rsplit("(", 1)
                result["fan_details"].append({
                    "name": name.strip(),
                    "value": int(value.replace("番)", "").strip())
                })
            except ValueError:
                continue

    # 解析总番值和总分数
    for line in lines:
        if line.startswith("总番值:"):
            result["total_fan"] = int(line.split("总番值:")[1].strip().replace("番", ""))
        elif line.startswith("总分数:"):
            result["total_score"] = int(line.split("总分数:")[1].strip().replace("分", ""))

    return result

def calc_fan_from_str(s, show_detail=False):
    """从字符串计算番数，返回分数、详情、番种名称等结构化信息"""
    try:
        hand, melds, seatWindTile, way = parse_input(s)
    except Exception as e:
        return {"error": f"输入解析失败: {str(e)}", "input": s}
    
    # 验证手牌
    valid, msg = check_hand_valid(hand, melds)
    if not valid:
        return {"error": msg, "input": s}
    
    detail_lines = []
    total_tiles = len(hand) + 3 * len(melds)
    
    # ===== 和牌判定 =====
    if total_tiles == 14:
        hand_tuple = tuple(hand)
        melds_tuple = tuple((tuple(meld[0]), meld[1]) for meld in melds)
        fan, groups = cached_calc_14_tiles(hand_tuple, melds_tuple, seatWindTile, way)
        
        # 获取番种名和值
        if fan and fan >= 3:  # 自然麻将至少3番
            score = fan * 4 - 8
            # 提取番型名和值
            names, values = [], []
            try:
                # 使用fan_calc.calc_fan_common_with_names获取详细番种信息
                res = fan_calc.calc_fan_common_with_names(hand, melds, seatWindTile, way)
                if res:
                    names = res[1]
                    values = res[2]
            except Exception as e:
                # 如果上面失败，尝试手动计算番种
                try:
                    winTile = hand[-1]
                    wait = sorted([t for t in hand if t != winTile] + [t for t in hand if t == winTile][1:])
                    
                    for combination in fan_calc.findCombinations(hand):
                        oriGroup = combination[:]
                        finalGroup = combination[:]
                        for meld in melds:
                            if len(meld[0]) == 4:
                                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                            else:
                                finalGroup.append(meld[0])
                        if len(finalGroup) not in [2, 5, 7]:
                            continue
                        
                        fan_names, fan_values, fan_score = fan_calc.calcTF_with_names(
                            finalGroup, seatWindTile, melds, wait, oriGroup, winTile, way
                        )
                        
                        if fan_score >= 3:
                            names = fan_names
                            values = fan_values
                            break
                except Exception:
                    pass
                    
            if show_detail:
                detail = get_calc_detail(hand, melds, seatWindTile, way, "和牌", groups)
                detail_lines.append(f"状态: 和牌\n{detail}")
            return {
                "score": score,
                "fan": fan,
                "names": names,
                "values": values,
                "detail": "\n".join(detail_lines),
                "input": s
            }
        else:
            return {
                "score": 0,
                "fan": 0,
                "names": [],
                "values": [],
                "detail": "没有和牌或番数不够（需要至少3番）。",
                "input": s
            }
    
    # ===== 听牌/一向听判定 =====
    elif total_tiles == 13:
        hand_tuple = tuple(hand)
        melds_tuple = tuple((tuple(meld[0]), meld[1]) for meld in melds)
        drawScore, semidrawScore, weakSemidrawScore, draw_result, semidraw_result, weak_semidraw_result = cached_calc_13_tiles(hand_tuple, melds_tuple, seatWindTile)
        
        status, score, names, values = "未成牌", 0, [], []
        if drawScore >= semidrawScore and drawScore >= weakSemidrawScore and drawScore > 0:
            status = "听牌"
            score = drawScore
            # 提取番型名和值（仅高目）
            try:
                if draw_result:
                    tingpai = draw_result[0]
                    res = fan_calc.calc_fan_common_with_names(hand + [tingpai], melds, seatWindTile, 0)
                    if res:
                        names = res[1]
                        values = res[2]
            except Exception as e:
                pass
            if show_detail:
                detail = get_calc_detail(hand, melds, seatWindTile, 0, "听牌")
                detail_lines.append(f"状态: 听牌\n{detail}")
        elif semidrawScore >= weakSemidrawScore and semidrawScore > 0:
            status = "一向听"
            score = semidrawScore
            # 一向听获取番种名（基于高目组合）
            try:
                if semidraw_result:
                    # 构建一向听高目的完整手牌
                    hand14 = copy.deepcopy(hand)
                    melds_new = copy.deepcopy(melds)
                    if semidraw_result[1] == 0:
                        hand14.remove(semidraw_result[0])
                        hand14.remove(semidraw_result[0])
                        melds_new.append([[semidraw_result[0], semidraw_result[0], semidraw_result[0]], 0])
                    elif semidraw_result[1] == 1:
                        hand14.remove(semidraw_result[0]-1)
                        hand14.remove(semidraw_result[0]-2)
                        melds_new.append([[semidraw_result[0]-2, semidraw_result[0]-1, semidraw_result[0]], 2])
                    elif semidraw_result[1] == 2:
                        hand14.remove(semidraw_result[0]-1)
                        hand14.remove(semidraw_result[0]+1)
                        melds_new.append([[semidraw_result[0]-1, semidraw_result[0], semidraw_result[0]+1], 1])
                    else:
                        hand14.remove(semidraw_result[0]+1)
                        hand14.remove(semidraw_result[0]+2)
                        melds_new.append([[semidraw_result[0], semidraw_result[0]+1, semidraw_result[0]+2], 0])
                    hand14.remove(semidraw_result[2])
                    hand14.append(semidraw_result[3])
                    
                    res = fan_calc.calc_fan_common_with_names(hand14, melds_new, seatWindTile, 0)
                    if res:
                        names = res[1]
                        values = res[2]
            except Exception as e:
                pass
            if show_detail:
                detail = get_calc_detail(hand, melds, seatWindTile, 0, "一向听")
                detail_lines.append(f"状态: 一向听\n{detail}")
        elif weakSemidrawScore > 0:
            status = "弱一向听"
            score = weakSemidrawScore
            # 弱一向听获取番种名（基于高目七对子）
            try:
                if weak_semidraw_result:
                    hand14 = copy.deepcopy(hand)
                    hand14.append(weak_semidraw_result[0])
                    hand14.remove(weak_semidraw_result[2])
                    hand14.append(weak_semidraw_result[3])
                    
                    res = fan_calc.calc_fan_common_with_names(hand14, [], seatWindTile, 0, 3, True)
                    if res:
                        names = res[1]
                        values = res[2]
            except Exception as e:
                pass
            if show_detail:
                detail = get_calc_detail(hand, melds, seatWindTile, 0, "弱一向听")
                detail_lines.append(f"状态: 弱一向听\n{detail}")
        else:
            status = "未成牌"
            score = 0
            detail_lines.append(f"状态: {status}")
        
        return {
            "score": score,
            "fan": 0,
            "names": names,
            "values": values,
            "detail": "\n".join(detail_lines),
            "input": s
        }
    
    # ===== 非法手牌数 =====
    else:
        return {
            "error": f"手牌数量不正确: {total_tiles}张",
            "input": s,
            "names": [],
            "values": [],
        }

def all_calc(s, show_detail=False, return_name=False):
    """
    主要计算接口
    
    Args:
        s: 算番器字符串输入
        show_detail: 若为True，返回(score, detail_string)，否则只返回score（或0）
        return_name: 若为True，返回符合条件的番种名称的列表
    
    Returns:
        show_detail=True and return_name=False: (score, detail_string)
        show_detail=False and return_name=False: score
        show_detail=True and return_name=True: (score, detail_string, fan_names)
        show_detail=False and return_name=True: (score, fan_names)
    """
    try:
        result = calc_fan_from_str(s, show_detail=show_detail)
        
        if "error" in result:
            if show_detail and return_name:
                return 0, result.get("error", "计算出错"), []
            elif show_detail:
                return 0, result.get("error", "计算出错")
            elif return_name:
                return 0, []
            else:
                return 0
        
        score = result["score"]
        detail = result.get("detail", "")
        fan_names = result.get("names", []) if return_name else []

        if show_detail and return_name:
            return score, detail, fan_names
        elif show_detail:
            return score, detail
        elif return_name:
            return score, fan_names
        else:
            return score
            
    except Exception as e:
        if show_detail and return_name:
            return 0, f"计算异常: {str(e)}", []
        elif show_detail:
            return 0, f"计算异常: {str(e)}"
        elif return_name:
            return 0, []
        else:
            return 0

# 提供兼容接口
def quick_calc(s):
    """快速计算接口，只返回分数"""
    return all_calc(s, show_detail=False)

def detail_calc(s):
    """详细计算接口，返回分数和详情"""
    return all_calc(s, show_detail=True)

# 清除缓存的辅助函数
def clear_cache():
    """清除所有缓存"""
    cached_parse_input.cache_clear()
    cached_validate_hand.cache_clear()
    cached_calc_14_tiles.cache_clear()
    cached_calc_13_tiles.cache_clear()

def get_cache_info():
    """获取缓存信息"""
    return {
        "parse_input": cached_parse_input.cache_info(),
        "validate_hand": cached_validate_hand.cache_info(),
        "calc_14_tiles": cached_calc_14_tiles.cache_info(),
        "calc_13_tiles": cached_calc_13_tiles.cache_info()
    }

if __name__ == "__main__":
    # 测试例子
    test_cases = [
        "(789m)(123p)(6666s)4455s5s!%",  # 和牌
        "123456789m1122p",           # 听牌
        "111222333m11p22s",          # 一向听
        "147m258p369s1234z"          # 未成牌
    ]
    
    print("=== 自然麻将算番器测试 ===")
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case}")
        score, detail = detail_calc(case)
        print(f"分数: {score}")
        if detail:
            print(f"详情:\n{detail}")
        print("-" * 50)
    
    print(f"\n缓存状态: {get_cache_info()}")