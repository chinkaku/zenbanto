import copy
from mahjonglibq import *
import pdb

tile_list = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', 
             '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 
             '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
             '1z', '2z', '3z', '4z', '5z', '6z', '7z']

# 以下为一些判断手牌是否满足番种的函数
'''
以 11_1m 2^22m _435m 手里 6789m 铳和 9m 为例
group是和牌拆解，这里为[[0,0,0], [1,1,1], [2,3,4], [5,6,7], [8,8]]，杠牌是三元的而不是四元
seatWindTile是门风牌，27=东、28=南、29=西、30=北
melds是鸣牌，这里为[[[0,0,0], 2], [[1,1,1,1], 4], [2,3,4], 1]
    吃牌：
    0 = _123
    1 = _213
    2 = _312
    碰牌：
    0 = _111
    1 = 1_11
    2 = 11_1
    杠牌：
    0 = _1111
    1 = 11_11
    2 = 111_1
    3 = ^111
    4 = 1^11
    5 = 11^1
    6 = +11+
wait是手里听牌，这里为[5,6,7,8]
oriGroup是手牌拆解，这里为[[5,6,7], [8,8]]
winTile是和张，这里为8
way是和牌方式，自摸+1，杠开/抢杠+2，柳暗花明+4，一巡和+8
'''
# 全体系
#色形门
# 字一色
def allHonors(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x >= 27 for part in group for x in part)

# 清一色
def fullFlush(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x // 9 == group[0][0] // 9 and x < 27 for part in group for x in part)

# 混一色
def halfFlush(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    return all(x // 9 == mixedGroup[0] // 9 or x >= 27 for x in mixedGroup)

# 镜同和（全部）
def mirrorHandSetup(group):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    if len(mixedGroup) != 12 or any(x >= 27 for x in mixedGroup):
        return False
    return mixedGroup[6] - mixedGroup[0] == mixedGroup[7] - mixedGroup[1] \
        and mixedGroup[7] - mixedGroup[1] == mixedGroup[8] - mixedGroup[2] \
        and mixedGroup[8] - mixedGroup[2] == mixedGroup[9] - mixedGroup[3] \
        and mixedGroup[9] - mixedGroup[3] == mixedGroup[10] - mixedGroup[4] \
        and mixedGroup[10] - mixedGroup[4] == mixedGroup[11] - mixedGroup[5]\
        and mixedGroup[6] // 9 != mixedGroup[5] // 9 and mixedGroup[5] // 9 == mixedGroup[0] // 9 and mixedGroup[6] % 9 == mixedGroup[0] % 9

#镜同四面
def mirrorHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) == 5:
        group2 = [i for i in group if len(i) != 2]
        return mirrorHandSetup(group2)
    else:
        return False
#镜同六对
def mirrorHand6Pairs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) == 7:
        flag = False
        for i in range(7):
            group2 = group[:]
            group2.pop(i)
            if mirrorHandSetup(group2):
                flag = True
                break
        return flag
    else:
        return False
#镜同四对
def mirrorHand4Setup(group):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    if len(mixedGroup) != 8 or any(x >= 27 for x in mixedGroup):
        return False
    return mixedGroup[4] - mixedGroup[0] == mixedGroup[5] - mixedGroup[1] \
        and mixedGroup[5] - mixedGroup[1] == mixedGroup[6] - mixedGroup[2] \
        and mixedGroup[6] - mixedGroup[2] == mixedGroup[7] - mixedGroup[3] \
        and mixedGroup[4] // 9 != mixedGroup[3] // 9 and mixedGroup[3] // 9 == mixedGroup[0] // 9 and mixedGroup[4] % 9 == mixedGroup[0] % 9

def mirrorHand4Pairs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        flag = False
        for i in range(7):
            group2 = group[:]
            group2.pop(i)
            for i1 in range(i,6):
                group3=group2[:]
                group3.pop(i1)
                for i2 in range(i1,5):
                    group4=group3[:]
                    group4.pop(i2)
                    if mirrorHand4Setup(group4):
                        flag = True
                        break
        return flag
    else:
        return False

'''    
def mirrorHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return mirrorHand1Pair(group) or mirrorHand7Pairs(group)
'''
# 形同和(全部)
def parallelHandSetup(group):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    if len(mixedGroup) == 12 and all(x < 27 for x in mixedGroup):
        if mixedGroup[6] - mixedGroup[0] == mixedGroup[7] - mixedGroup[1] \
            and mixedGroup[7] - mixedGroup[1] == mixedGroup[8] - mixedGroup[2] \
            and mixedGroup[8] - mixedGroup[2] == mixedGroup[9] - mixedGroup[3] \
            and mixedGroup[9] - mixedGroup[3] == mixedGroup[10] - mixedGroup[4] \
            and mixedGroup[10] - mixedGroup[4] == mixedGroup[11] - mixedGroup[5]\
            and mixedGroup[6] // 9 != mixedGroup[5] // 9 and mixedGroup[5] // 9 == mixedGroup[0] // 9 and mixedGroup[11] // 9 == mixedGroup[6] // 9:
            return True
        else:
            pass
    return False
#形同四面
def parallelHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) == 5:
        group2 = [i for i in group if len(i) != 2]
        return parallelHandSetup(group2)
    else:
        return False
#形同六对
def parallelHand6Pairs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) == 7:
        flag = False
        for i in range(7):
            group2 = group[:]
            group2.pop(i)
            if parallelHandSetup(group2):
                flag = True
                break
        return flag
    else:
        return False
#形同四对
def paralleHand4Setup(group):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    if len(mixedGroup) != 8 or any(x >= 27 for x in mixedGroup):
        return False
    return mixedGroup[4] - mixedGroup[0] == mixedGroup[5] - mixedGroup[1] \
        and mixedGroup[5] - mixedGroup[1] == mixedGroup[6] - mixedGroup[2] \
        and mixedGroup[6] - mixedGroup[2] == mixedGroup[7] - mixedGroup[3] \
        and mixedGroup[4] // 9 != mixedGroup[3] // 9 and mixedGroup[3] // 9 == mixedGroup[0] // 9 and mixedGroup[7] // 9 == mixedGroup[4] // 9

def paralleHand4Pairs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        flag = False
        for i in range(7):
            group2 = group[:]
            group2.pop(i)
            for i1 in range(i,6):
                group3=group2[:]
                group3.pop(i1)
                for i2 in range(i1,5):
                    group4=group3[:]
                    group4.pop(i2)
                    if paralleHand4Setup(group4):
                        flag = True
                        break
        return flag
    else:
        return False
'''    
def parallelHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return parallelHand1Pair(group) or parallelHand7Pairs(group)
'''
#清缺门
def fullCut(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    return all((x // 9 == mixedGroup[0] // 9 or x//9 ==mixedGroup[13] //9 ) and x < 27 for part in group for x in part)

# 九数齐
from itertools import combinations  # 导入组合工具

def nineNumbersCombined(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) != 5:
        return False
    if any(i[0] >= 27 for i in group):  # 确保子列表非空
        return False
    
    groupmod9 = [[x % 9 for x in i] for i in group]  # 模9运算
    mixedGroupMod9 = sorted(x for sublist in groupmod9 for x in sublist)  # 合并并排序
    
    # 条件1: 检查0-8是否全部存在
    condition1 = all(x in mixedGroupMod9 for x in range(9))
    
    # 条件2: 检查任意两个子列表是否无交集
    condition2 = all(
        set(A).isdisjoint(B)  # 用集合判断无交集
        for A, B in combinations(groupmod9, 2)  # 生成所有两两组合
    )
    
    return condition1 and condition2

# 七连齐
def sevenNumbersCombinedSetup(group, setnum):
    if any(i[0] >= 27 for i in group):  # 确保子列表非空
        return False
    
    groupmod9 = [[x % 9 for x in i] for i in group]  # 模9运算
    mixedGroupMod9 = sorted(x for sublist in groupmod9 for x in sublist)  # 合并并排序
    
    # 条件1: 检查0-8是否全部存在
    condition1 = all(x in mixedGroupMod9 for x in range(setnum,setnum+7))
    
    # 条件2: 检查任意两个子列表是否无交集
    condition2 = all(
        set(A).isdisjoint(B)  # 用集合判断无交集
        for A, B in combinations(groupmod9, 2)  # 生成所有两两组合
    )
    
    return condition1 and condition2
def sevenNumbersCombined(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Flag=False
    for i in range(3):
        if sevenNumbersCombinedSetup(group,i):
            Flag=True
            break
    return Flag
# 五连齐
def fiveNumbersCombinedSetup(group, setnum):
    if len(group) != 5:
        return False
    if any(i[0] >= 27 for i in group):  # 确保子列表非空
        return False
    
    groupmod9 = [[x % 9 for x in i] for i in group]  # 模9运算
    mixedGroupMod9 = sorted(x for sublist in groupmod9 for x in sublist)  # 合并并排序
    
    # 条件1: 检查0-8是否全部存在
    condition1 = all(x in mixedGroupMod9 for x in range(setnum,setnum+5))
    
    # 条件2: 检查任意两个子列表是否无交集
    condition2 = all(
        set(A).isdisjoint(B)  # 用集合判断无交集
        for A, B in combinations(groupmod9, 2)  # 生成所有两两组合
    )
    
    return condition1 and condition2
def fiveNumbersCombined(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Flag=False
    for i in range(5):
        if fiveNumbersCombinedSetup(group,i):
            Flag=True
            break
    return Flag
# 五门齐
def fiveTypesCombined(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    types = [range(0, 9), range(9, 18), range(18, 27), range(27, 31), range(31, 34)]
    return all(any(x[0] in r for x in group) for r in types) and len(group) == 5
    
#九数全
def nineNumbersHave(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) != 5:
        return False
    if any(i[0] >= 27 for i in group):  # 确保子列表非空
        return False
    
    groupmod9 = [[x % 9 for x in i] for i in group]  # 模9运算
    mixedGroupMod9 = sorted(x for sublist in groupmod9 for x in sublist)  # 合并并排序
    
    # 条件1: 检查0-8是否全部存在
    condition1 = all(x in mixedGroupMod9 for x in range(9))
    
    # 条件2: 检查任意两个子列表是否无交集
    
    
    return condition1 

#数形门
# 二序数
def twoNumbers(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x < 27 for x in mixedGroup) and all(x == mixedGroupMod9[0] or x == mixedGroupMod9[-1] for x in mixedGroupMod9)
    
# 聚三数
def tripleConsecutive(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x < 27 for x in mixedGroup) and mixedGroupMod9[-1] - mixedGroupMod9[0] <= 2
#满庭芳
def AllHaving(group, seatWindTile, melds, wait, oriGroup, winTile, way) :
    if len(group)!=5:
        return False
    pairs= [(g[0]%9) for g in group if len(g) == 2 and g[0] < 27]
    return all((x[0]%9 in pairs or x[1]%9 in pairs or x[-1]%9 in pairs) and x[0]<=26 for x in group)
# 聚四数
def quadConsecutive(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x < 27 for x in mixedGroup) and mixedGroupMod9[-1] - mixedGroupMod9[0] <= 3
#三面芳
def ThreeHaving(group, seatWindTile, melds, wait, oriGroup, winTile, way) :
    if len(group)!=5:
        return False
    pairs= [(g[0]%9) for g in group if len(g) == 2 and g[0] < 27]
    time=0
    for x in group:
        if x[0]%9 in pairs or x[1]%9 in pairs or x[-1]%9 in pairs and x[0]<=26:
            time+=1
    return time>=4
# 聚五数
def fifConsecutive(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x < 27 for x in mixedGroup) and mixedGroupMod9[-1] - mixedGroupMod9[0] <= 4
# 两面芳
def TwoHaving(group, seatWindTile, melds, wait, oriGroup, winTile, way) :
    if len(group)!=5:
        return False
    pairs= [(g[0]%9) for g in group if len(g) == 2 and g[0] < 27]
    time=0
    for x in group:
        if x[0]%9 in pairs or x[1]%9 in pairs or x[-1]%9 in pairs and x[0]<=26:
            time+=1
    return time>=3
# 混一数
def mixedOnenumber(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part if x <= 26]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x%9==mixedGroupMod9[0] or x>=27 for x in mixedGroup) and any(x<=26 for x in mixedGroup)
# 混二数
def mixedtwoNumbers(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part if x <= 26]
    mixedGroupMod9 = [x % 9 for x in mixedGroup]
    mixedGroupMod9.sort()
    return all(x%9 == mixedGroupMod9[0] or x%9 == mixedGroupMod9[-1] or x>=27 for x in mixedGroup) and any(x<=26 for x in mixedGroup)

# 一条筋
def allKeys(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroupMod3 = [x % 3 for x in mixedGroup]
    mixedGroupMod3.sort()
    return all(x < 27 for x in mixedGroup) and mixedGroupMod3[-1] == mixedGroupMod3[0]
    
# 全双数
def allEvens(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25] for part in group for x in part)
    
# 全单数
def allOdds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [0, 2, 4, 6, 8, 9, 11, 13, 15, 17, 18, 20, 22, 24, 26] for part in group for x in part)

# 清无将
def allNojoker(group, seatWindTile, melds, wait, oriGroup, winTile, way) :
    return all(x in [0,2,3,5,6,8,9,11,12,14,15,17,18,20,21,23,24,26]for part in group for x in part)

# 断中数
def No456(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x not in [3,4,5,12,13,14,21,22,23]for part in group for x in part)

# 断幺九
def No19(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x not in [0,8,9,17,18,26,27,28,29,30,31,32,33]for part in group for x in part)

# 映同五面
def reflectedHand5(group, seatWindTile, melds, wait, oriGroup, winTile, way): 
    if len(group) == 5:
        # 标准和
        pairs = [g for g in group if len(g) == 2 and g[0] < 27]
        if len(pairs) != 1:
            return False
        pair = pairs[0]
        pair_num = pair[0] % 9
        pair_suit = pair[0] // 9
        parts = [g for g in group if len(g) == 3 and g[0] < 27]
        if len(parts) != 4:
            return False
        used = [False] * 4
        for i in range(4):
            if used[i]:
                continue
            m1 = parts[i]
            # 自己一组对称
            if m1[1] % 9 == pair_num:
                used[i] = True
                continue
            # 尝试和其它面子对称
            for j in range(i+1, 4):
                if used[j]:
                    continue
                m2 = parts[j]
                if m2[0] // 9 != m1[0] // 9:
                    continue
                # 对称条件
                if m1[0] % 9 + m2[2] % 9 == 2 * pair_num and m1[1] % 9 + m2[1] % 9 == 2 * pair_num and m1[2] % 9 + m2[0] % 9 == 2 * pair_num:
                    used[i] = used[j] = True
                    break
            # 失败了
            if not used[i]:
                return False
        partsMod9 = [[x % 9 for x in g] for g in parts]
        return any(g[1] != pair_num for g in partsMod9)
    else:
        return False
    
#映同七对
def reflectedHand7(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group) == 7:
        # 七对子
        pairs = [g for g in group if len(g) == 2 and g[0] < 27]
        if len(pairs) != 7:
            return False
        suit0 = [p[0] % 9 for p in pairs if p[0] // 9 == 0]
        suit1 = [p[0] % 9 for p in pairs if p[0] // 9 == 1]
        suit2 = [p[0] % 9 for p in pairs if p[0] // 9 == 2]
        suits = suit0 + suit1 + suit2
        suits.sort()
        return all(suit[x] + suit[-x-1] == 2 * suits[3] for suit in [suit0, suit1, suit2] for x in range(len(suit)))
    else:
        return False
    
#映数七对
def reflectNum7(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if not all(x<=26 for parts in group for x in parts):
        return False
    elif len(group)==7:
        mixedGroup = [x%9 for part in group for x in part]
        mixedGroup.sort()
        middle=mixedGroup[6]
        for i in range(6):
            if not mixedGroup[i]+mixedGroup[13-i]==middle*2:
                return False
        return True
    else:
        return False
    
# 映数五面
def reflectNum5(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==5:
        group2 = [i for i in group if len(i) != 2]
        pairs=[i for i in group if len(i)==2]
        mixedGroup = [x%9 for part in group2 for x in part]
        mixedGroup.sort()
        for i in range(7):
            if not mixedGroup[i]+mixedGroup[11-i]==(pairs[0][0]%9)*2:
                return False
        return True
    else:
        return False
    
#映同四面
def reflectedHand4(group, seatWindTile, melds, wait, oriGroup, winTile, way): 
    if len(group) == 5:
        # 标准和
        for pair in range(0,8):
            pair_num = pair % 9
            parts = [g for g in group if len(g) == 3 and g[0] < 27]
            if len(parts) != 4:
                return False
            used = [False] * 4
            for i in range(4):
                if used[i]:
                    continue
                m1 = parts[i]
                # 自己一组对称
                if m1[1] % 9 == pair_num:
                    used[i] = True
                    continue
                # 尝试和其它面子对称
                for j in range(i+1, 4):
                    if used[j]:
                        continue
                    m2 = parts[j]
                    if m2[0] // 9 != m1[0] // 9:
                        continue
                    # 对称条件
                    if m1[0] % 9 + m2[2] % 9 == 2 * pair_num and m1[1] % 9 + m2[1] % 9 == 2 * pair_num and m1[2] % 9 + m2[0] % 9 == 2 * pair_num:
                        used[i] = used[j] = True
                        break
            if all(i for i in used):
                return True
        return False
    else:
        return False

# 对刻门
# 碰碰和
def allPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 5 and all(x[0] == x[1] for x in group)
    
# 七对子
def sevenPairs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 7

# 幺九门
# 清幺九
def allTerminals(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [0, 8, 9, 17, 18, 26] for part in group for x in part)
    
# 混幺九
def allTerminalsAndHonors(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    return all(x in [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33] for x in mixedGroup) and\
           any(x in [0, 8, 9, 17, 18, 26] for x in mixedGroup)
    
# 清全带幺
def pureOutsideHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x[0] in [0, 9, 18] or x[-1] in [8, 17, 26] for x in group)
    
# 混全带幺
def mixedOutsideHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    return all(x[0] in [0, 9, 18, 27, 28, 29, 30, 31, 32, 33] or x[-1] in [8, 17, 26] for x in group) and\
           any(x in [0, 8, 9, 17, 18, 26] for x in mixedGroup)
# 牌画门
# 绿一色
def allgreen(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [10,11,12,14,16,32] for part in group for x in part)

# 大车轮
def bigwheels(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 7 and [x for part in group for x in part].sort() == [19,19,20,20,21,21,22,22,23,23,24,24,25,25]

# 中车轮
def middlewheels(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 7 and [x for part in group for x in part].sort() == [18,18,19,19,20,20,22,22,24,24,25,25,26,26]

# 小车轮
def smallwheels(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 7 and ([x for part in group for x in part].sort() == [18,18,19,19,20,20,21,21,22,22,23,23,24,24]\
                                or [x for part in group for x in part].sort() == [20,20,21,21,22,22,23,23,24,24,25,25,26,26])
# 黑一色
def allblack(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [19,21,25,27,28,29,30,33] for part in group for x in part)

# 全带红
def allred(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [0,1,2,3,4,5,6,7,8,13,15,17,18,20,22,23,24] for part in group for x in part)
# 断红和
def nored(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x not in [0,1,2,3,4,5,6,7,8,13,15,17,18,20,22,23,24] for part in group for x in part)

# 推不倒
def cannotpush(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(x in [10,12,13,14,16,17,18,19,20,21,22,25,26,33] for part in group for x in part)

# 组合系
# 九莲宝灯
def nineGates(group, seatWindTile, melds, wait, oriGroup, winTile, way): 
    wait.sort()
    return wait in [[0,0,0,1,2,3,4,5,6,7,8,8,8], [9,9,9,10,11,12,13,14,15,16,17,17,17], [18,18,18,19,20,21,22,23,24,25,26,26,26]]

# 三色四同顺（在下面）
# 四步高
def pureFourShiftedChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,9,10,11,12,18,19,20,21]
    return any(([i,i+1,i+2] in group and [i+1,i+2,i+3] in group and [i+2,i+3,i+4] in group and [i+3,i+4,i+5] in group) for i in start)

# 四连环
def pureFourChainedChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,9,18]
    return any(([i,i+1,i+2] in group and [i+2,i+3,i+4] in group and [i+4,i+5,i+6] in group and [i+6,i+7,i+8] in group) for i in start)


# 三步高
def pureThreeShiftedChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,9,10,11,12,13,18,19,20,21,22]
    return any(([i,i+1,i+2] in group and [i+1,i+2,i+3] in group and [i+2,i+3,i+4] in group) for i in start)

# 三连环
def pureThreeChainedChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,9,10,11,18,19,20]
    return any(([i,i+1,i+2] in group and [i+2,i+3,i+4] in group and [i+4,i+5,i+6] in group) for i in start)

# 一条龙
def pureStraight(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,9,18]
    return any(([i,i+1,i+2] in group and [i+3,i+4,i+5] in group and [i+6,i+7,i+8] in group) for i in start)
    
# 清两连六
def pureTwoSextuplets(group, seatWindTile, melds, wait, oriGroup, winTile, way):
	combs = [i[0] for i in group if  len(i) == 3 and i[0] != i[1]]
	if len(combs) != 4:
		return False
	combs.sort()
	return combs[2] - combs[0] == 3 and combs[3] - combs[1] == 3 and combs[3] // 9 == combs[0] // 9

# 连六顺
def sextuplet(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    combs = [i[0] for i in group if  len(i) == 3 and i[0] != i[1]]
    if len(combs) <2 :
        return False
    combs.sort()
    for i in range(len(combs)):
        for j in range(i+1,len(combs)):
            if combs[j]-combs[i]==3:
                return True
    return False
# 二同刻
def twoMixedDoublePungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) != 2]
    group2.sort()
    if len(group2) == 4:
        checker = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in group2:
            if i[0] == i[1] and i[0] < 27:
                checker[i[0] % 9] += 1
        if checker.count(2) >= 2:
            return True
    return False

# 两色同刻
def mixedDoublePungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any((([i,i,i] in group and [i+9,i+9,i+9] in group) or\
                ([i,i,i] in group and [i+18,i+18,i+18] in group) or\
                ([i+9,i+9,i+9] in group and [i+18,i+18,i+18] in group)) for i in range(9))
# 两连六
def twoSextuplets(group, seatWindTile, melds, wait, oriGroup, winTile, way):
	if pureTwoSextuplets(group, seatWindTile, melds, wait, oriGroup, winTile, way):
		return True
	combs = [i[0] for i in group if  len(i) == 3 and i[0] != i[1]]
	if len(combs) != 4:
		return False
	combs.sort()
	return combs[1] - combs[0] == 3 and combs[3] - combs[2] == 3 and combs[1] // 9 == combs[0] // 9 and combs[3] // 9 == combs[2] // 9
# 二相逢
def doubletwomeets(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if twoDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
        return False
    if pureDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way) and not(mixedQuadrupleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way)):
        return False
    combs = [i[0] for i in group if  len(i) == 3 and i[0] != i[1]]
    if len(combs) != 4:
        return False
    combs.sort()
    return (combs[3]-combs[1])%9==0 and (combs[2]-combs[0])%9==0 or (combs[3]-combs[2])%9==0 \
        and (combs[1]-combs[0])%9==0 or (combs[3]-combs[0])%9==0 and (combs[2]-combs[1])%9==0
# 三色连刻
def mixedTriShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(([i,i,i]in group and [i+10,i+10,i+10]in group and [i+20,i+20,i+20] in group)for i in range(7)) or\
          any(([i,i,i]in group and [i+10,i+10,i+10]in group and [i+17,i+17,i+17]in group)for i in range(1,8)) or\
          any(([i,i,i]in group and [i+8,i+8,i+8]in group and [i+19,i+19,i+19]in group)for i in range(1,8))or\
          any(([i,i,i]in group and [i+8,i+8,i+8]in group and [i+16,i+16,i+16]in group)for i in range(2,9))or\
          any(([i,i,i]in group and [i+11,i+11,i+11]in group and [i+19,i+19,i+19]in group)for i in range(7))or\
          any(([i,i,i]in group and [i+7,i+7,i+7]in group and [i+17,i+17,i+17]in group)for i in range(2,9))
# 三色同刻
def mixedTriplePungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(([i,i,i] in group and [i+9,i+9,i+9] in group and [i+18,i+18,i+18] in group) for i in range(9))

# 三色同顺
def mixedTripleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(([i,i+1,i+2] in group and [i+9,i+10,i+11] in group and [i+18,i+19,i+20] in group) for i in range(7))

# 三色龙
def mixedStraight(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return ([0,1,2] in group and (([12,13,14] in group and [24,25,26] in group) or ([15,16,17] in group and [21,22,23] in group)))\
        or ([3,4,5] in group and (([9,10,11] in group and [24,25,26] in group) or ([15,16,17] in group and [18,19,20] in group)))\
        or ([6,7,8] in group and (([9,10,11] in group and [21,22,23] in group) or ([12,13,14] in group and [18,19,20] in group)))

# 四同顺
def pureQuadrupleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) == 3]
    group2.sort()
    if group2 == []:
        return False
    return group2[0] == group2[3] and group2[0][0] != group2[0][1]

# 三同顺   
def pureTripleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) == 3]
    group2.sort()
    if group2 == []:
        return False
    return(group2[0] == group2[2] or group2[1] == group2[3]) and group2[0][0] != group2[0][1]

# 清两般高
def pureTwoDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) == 3]
    group2.sort()
    if group2 == []:
        return False
    return (group2[0] == group2[1] and group2[2] == group2[3])\
        and group2[0][0] != group2[0][1] and group2[2][0] != group2[2][1]\
        and group2[0][0]//9 == group2[2][0]//9

# 两般高
def twoDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) == 3]
    group2.sort()
    if group2 == []:
        return False
    return (group2[0] == group2[1] and group2[2] == group2[3])\
        and group2[0][0] != group2[0][1] and group2[2][0] != group2[2][1]
        

# 一般高
def pureDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    group2 = [i for i in group if len(i) == 3]
    group2.sort()
    if group2 == []:
        return False
    return (group2[0] == group2[1] or group2[1] == group2[2] or group2[2] == group2[3])
# 三色四同顺
def mixedQuadrupleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return pureDoubleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way) \
        and mixedTripleChows(group, seatWindTile, melds, wait, oriGroup, winTile, way)
# 喜相逢
def twomeet(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    combs = [i[0] for i in group if  len(i) == 3 and i[0] != i[1]]
    if len(combs) <2:
        return False
    combs.sort()
    for i in range(len(combs)):
        for j in range(i+1,len(combs)):
            if combs[i]%9==combs[j]%9 and combs[i]!=combs[j]:
                return True
    return False

# 四顺同数
def fourchowsSamenum(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    combs = [i[0]%9 for i in group if  len(i) == 3 and i[0] != i[1]]
    if len(combs) !=4:
        return False
    combs.sort()
    return combs[3]-combs[0]<=2

# 三顺同数
def threechowsSamenum(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    combs = [i[0]%9 for i in group if  len(i) == 3 and i[0] != i[1]]
    if len(combs) ==3:
        combs.sort()
        return combs[2]-combs[0]<=2
    elif len(combs)<3:
        return False
    else:
        for i in range(4):
            groupnew=group[:]
            groupnew.pop(i)
            if threechowsSamenum(groupnew, seatWindTile, melds, wait, oriGroup, winTile, way):
                return True
        return False
    
# 四牌齐
def fourallin(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    for pairs in melds:
        if len(pairs[0])==4:
             mixedGroup.append(pairs[0][0])
    mixedGroup.sort()
    count = 0
    for i in range(len(mixedGroup)-3):
        if mixedGroup[i] == mixedGroup[i+3]:
            count += 1
    return count >= 4

# 三四归
def threeTileHogs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    count = 0
    for i in range(11):
        if mixedGroup[i] == mixedGroup[i+3]:
            count += 1
    return count >= 3

# 三牌齐
def threeallin(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    for pairs in melds:
        if len(pairs[0])==4:
             mixedGroup.append(pairs[0][0])
    mixedGroup.sort()
    count = 0
    for i in range(len(mixedGroup)-3):
        if mixedGroup[i] == mixedGroup[i+3]:
            count += 1
    return count >= 3

# 两四归
def twoTileHogs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    mixedGroup.sort()
    count = 0
    for i in range(11):
        if mixedGroup[i] == mixedGroup[i+3]:
            count += 1
    return count >= 2

# 四归四
def tileHog4(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(len([x for x in group if n in x]) == 4 for n in range(27))

# 四归三
def tileHog3(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixGroup=[x for part in group for x in part]
    return any(len([x for x in group if n in x]) == 3 and mixGroup.count(n)>=4 for n in range(27))

# 四归二
def tileHog2(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixGroup=[x for part in group for x in part]
    return any(len([x for x in group if n in x]) == 2 and mixGroup.count(n)>=4 for n in range(27))

# 二牌齐
def twoallin(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    for pairs in melds:
        if len(pairs[0])==4:
             mixedGroup.append(pairs[0][0])
    mixedGroup.sort()
    count = 0
    for i in range(len(mixedGroup)-3):
        if mixedGroup[i] == mixedGroup[i+3]:
            count += 1
    return count >= 2

# 三跳刻
def threeJumpedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,9,10,11,12,13,18,19,20,21,22]
    return any(([i,i,i] in group and [i+2,i+2,i+2] in group and [i+4,i+4,i+4] in group) for i in start)

# 杂三跳刻
def mixedTriJumpedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(([i,i,i]in group and [i+11,i+11,i+11]in group and [i+22,i+22,i+22] in group)for i in range(5)) or\
          any(([i,i,i]in group and [i+11,i+11,i+11]in group and [i+16,i+16,i+16]in group)for i in range(2,7)) or\
          any(([i,i,i]in group and [i+7,i+7,i+7]in group and [i+20,i+20,i+20]in group)for i in range(2,7))or\
          any(([i,i,i]in group and [i+7,i+7,i+7]in group and [i+14,i+14,i+14]in group)for i in range(4,9))or\
          any(([i,i,i]in group and [i+13,i+13,i+13]in group and [i+20,i+20,i+20]in group)for i in range(5))or\
          any(([i,i,i]in group and [i+5,i+5,i+5]in group and [i+16,i+16,i+16]in group)for i in range(4,9))

# 三跳牌
def threeJumpedPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,9,10,11,12,13,18,19,20,21,22]
    return any(([i,i,i] in group and [i+2,i+2] in group and [i+4,i+4,i+4] in group) for i in start) or\
          any(([i,i] in group and [i+2,i+2,i+2] in group and [i+4,i+4,i+4] in group) for i in start) or\
          any(([i,i,i] in group and [i+2,i+2] in group and [i+4,i+4,i+4] in group) for i in start) or\
          any(([i,i,i] in group and [i+2,i+2] in group and [i+4,i+4] in group) for i in start)

# 对中二副
def mirrorTwoPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    pair_num = 4
    parts = [g for g in group if len(g) == 3 and g[0] < 27]
    if len(parts) != 4:
        return False
    used = [False] * 4
    for i in range(4):
        if used[i]:
            continue
        m1 = parts[i]
        # 尝试和其它面子对称
        for j in range(i+1, 4):
            if used[j]:
                continue
            m2 = parts[j]
            if m2[0] // 9 != m1[0] // 9:
                continue
            # 对称条件
            if m1[0] % 9 + m2[2] % 9 == 2 * pair_num and m1[1] % 9 + m2[1] % 9 == 2 * pair_num and m1[2] % 9 + m2[0] % 9 == 2 * pair_num:
                used[i] = used[j] = True
                break
            # 失败了
        if not used[i]:
            return False
    return True

# 对中刻
def mirrorOnePung(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group)==5 and any([9*i,9*i,9*i] in group and [9*i+8,9*i+8,9*i+8] in group for i in range(3) ) or\
        any([9*i+1,9*i+1,9*i+1] in group and [9*i+7,9*i+7,9*i+7] in group for i in range(3) ) or\
        any([9*i+2,9*i+2,9*i+2] in group and [9*i+6,9*i+6,9*i+6] in group for i in range(3) ) or\
        any([9*i+3,9*i+3,9*i+3] in group and [9*i+5,9*i+5,9*i+5] in group for i in range(3) )

# 对中副
def mirrorOnePai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if(mirrorOnePung(group, seatWindTile, melds, wait, oriGroup, winTile, way)):
        return True
    return any([9*i,9*i+1,9*i+2] in group and [9*i+6,9*i+7,9*i+8] in group for i in range(3) ) or\
        any([9*i+1,9*i+2,9*i+3] in group and [9*i+5,9*i+6,9*i+7] in group for i in range(3) ) or\
        any([9*i+2,9*i+3,9*i+4] in group and [9*i+4,9*i+5,9*i+6] in group for i in range(3) ) or\
        any([9*i+3,9*i+4,9*i+5] in group and [9*i+3,9*i+4,9*i+5] in group for i in range(3) )
# 五连牌
def fiveShiftedPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if not allPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
        return False
    m = [x for part in group for x in part]
    if any(x>=27 for x in m):
        return False
    return m[3]-m[0]==1 and m[6]-m[3]==1 and m[9]-m[6]==1 and m[12]-m[9]==1 and m[12]//9 == m[0]//9

# 四连刻
def fourShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,5,9,10,11,12,13,14,18,19,20,21,22,23]
    return any(([i,i,i] in group and [i+1,i+1,i+1] in group and [i+2,i+2,i+2] in group and [i+3,i+3,i+3] in group) for i in start)

# 二重连刻
def NichuuShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if not allPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
        return False
    groupnum = [i[0] for i in group if len(i) != 2]
    if any(i >= 27 for i in groupnum):
        return False
    groupnum.sort()
    return groupnum[0]//9 ==groupnum[3]//9 and groupnum[1]-groupnum[0]==1 and groupnum[3]-groupnum[2]==1

# 三连刻
def threeShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,5,6,9,10,11,12,13,14,15,18,19,20,21,22,23,24]
    return any(([i,i,i] in group and [i+1,i+1,i+1] in group and [i+2,i+2,i+2] in group) for i in start)

# 双二连刻
def doubleTwoShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if not allPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
        return False
    groupnum = [i[0] for i in group if len(i) != 2]
    if any(i >= 27 for i in groupnum):
        return False
    groupnum.sort()
    return groupnum[0]//9 == groupnum[1]//9 and groupnum[3]//9 == groupnum[2]//9 and groupnum[1]-groupnum[0] == 1 and groupnum[3]-groupnum[2] == 1

# 二连刻
def twoShiftedPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    start = [0,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,18,19,20,21,22,23,24,25]
    return any(([i,i,i] in group and [i+1,i+1,i+1] in group) for i in start)

# 四自刻
def fourSelfPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    selfPungs = 0
    for i in group:
        if len(i) == 3 and i[0] == i[1]:
            # 这是个刻子
            selfPungs += 1
    for i in melds:
        if len(i[0]) == 3 and i[0][0] == i[0][1]:
            # 这是个明刻，不是自刻
            selfPungs -= 1
    if way % 2 == 0 and [winTile, winTile, winTile] in oriGroup and wait.count(winTile) == 2:
        # 铳和，和张刻子在手牌中，且原本只有2张，算不上自刻
        selfPungs -= 1
    return selfPungs >= 4

# 三自刻
def threeSelfPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    selfPungs = 0
    for i in group:
        if len(i) == 3 and i[0] == i[1]:
            # 这是个刻子
            selfPungs += 1
    for i in melds:
        if len(i[0]) == 3  and i[0][0] == i[0][1]:
            # 这是个明刻，不是自刻
            selfPungs -= 1
    if way % 2 == 0 and [winTile, winTile, winTile] in oriGroup and wait.count(winTile) == 2:
        # 铳和，和张刻子在手牌中，且原本只有2张，算不上自刻
        selfPungs -= 1
    return selfPungs >= 3

# 两自刻
def twoSelfPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    selfPungs = 0
    for i in group:
        if len(i) == 3 and i[0] == i[1]:
            # 这是个刻子
            selfPungs += 1
    for i in melds:
        if len(i[0]) == 3  and i[0][0] == i[0][1]:
            # 这是个明刻，不是自刻
            selfPungs -= 1
    if way % 2 == 0 and [winTile, winTile, winTile] in oriGroup and wait.count(winTile) == 2:
        # 铳和，和张刻子在手牌中，且原本只有2张，算不上自刻
        selfPungs -= 1
    return selfPungs >= 2

# 四杠
def fourKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Kongs = 0
    for i in melds:
        if len(i[0]) == 4:
            Kongs += 1
    return Kongs >= 4

# 三杠
def threeKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Kongs = 0
    for i in melds:
        if len(i[0]) == 4:
            Kongs += 1
    return Kongs >= 3

# 两杠
def twoKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Kongs = 0
    for i in melds:
        if len(i[0]) == 4:
            Kongs += 1
    return Kongs >= 2

# 一杠
def oneKong(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    Kongs = 0
    for i in melds:
        if len(i[0]) == 4:
            Kongs += 1
    return Kongs >= 1

# 四暗杠
def fourAnKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    ankongs=0
    for i in melds:
        if i[1]==6:
            ankongs += 1
    return ankongs >=4

# 三暗杠
def threeAnKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    ankongs=0
    for i in melds:
        if i[1]==6:
            ankongs += 1
    return ankongs >=3

# 两暗杠
def twoAnKongs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    ankongs=0
    for i in melds:
        if i[1]==6:
            ankongs += 1
    return ankongs >=2

# 一暗杠
def oneAnKong(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    ankongs=0
    for i in melds:
        if i[1]==6:
            ankongs += 1
    return ankongs >=1
# 十三幺
def thirteenOrphans(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(group) == 2
# 十六风
def sixteenWinds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    for pairs in melds:
        if len(pairs[0])==4:
             mixedGroup.append(pairs[0][0])
    mixedGroup.sort()
    feng=0
    for i in mixedGroup:
        if 27<=i and i<=30 :
            feng += 1
    return feng==16

# 大四喜
def bigFourWinds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return [27, 27, 27] in group and [28, 28, 28] in group and [29, 29, 29] in group and [30, 30, 30] in group
# 四风七对
def biggerFourWinds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        return all(27<=x and x<=30 for pairs in group for x in pairs)
    return False
# 四风六对
def middleFourWinds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        notfeng=0
        for pairs in group:
            for x in pairs:
                if not (27<=x and x<=30):
                    notfeng += 1
        return notfeng<=2
    return False
# 小四喜
def littleFourWinds(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    windPungs = 0
    for x in range(27,31):
        if [x,x,x] in group or [x,x] in group:
            windPungs += 1
    return windPungs >= 4
    
# 三风刻
def threeWindPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    windPungs = 0
    for x in range(27,31):
        if [x,x,x] in group:
            windPungs += 1
    return windPungs >= 3

# 三风牌
def threeWindPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    windPungs = 0
    for x in range(27,31):
        if [x,x,x] in group or [x,x] in group:
            windPungs += 1
    return windPungs >= 3

# 两风刻
def twoWindPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    windPungs = 0
    for x in range(27,31):
        if [x,x,x] in group:
            windPungs += 1
    return windPungs >= 2

# 两风牌
def twoWindPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    windPungs = 0
    for x in range(27,31):
        if [x,x,x] in group or [x,x] in group:
            windPungs += 1
    return windPungs >= 2

# 十二元
def twelveDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    for pairs in melds:
        if len(pairs[0])==4:
             mixedGroup.append(pairs[0][0])
    mixedGroup.sort()
    yuan=0
    for i in mixedGroup:
        if 31<=i and i<=33 :
            yuan += 1
    return yuan == 12

# 五元对
def biggerThreeDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        notyuan=0
        for pairs in group:
            for x in pairs:
                if not (31<=x and x<=33):
                    notyuan += 1
        return notyuan<=4
    return False
# 大三元
def bigThreeDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return [31, 31, 31] in group and [32, 32, 32] in group and [33, 33, 33] in group
# 四元对
def middleThreeDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    if len(group)==7:
        notyuan=0
        for pairs in group:
            for x in pairs:
                if not (31<=x and x<=33):
                    notyuan += 1
        return notyuan<=6
    return False
# 小三元
def littleThreeDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    return 31 in mixedGroup and 32 in mixedGroup and 33 in mixedGroup and len(group) >= 5
    
# 两元刻
def twoDragonPungs(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    dragonPungs = 0
    for x in range(31,34):
        if [x,x,x] in group:
            dragonPungs += 1
    return dragonPungs >= 2

# 两元牌
def twoDragons(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    dragons = [31, 32, 33]
    mixedGroup = [x for part in group for x in part]
    return len(list(set(mixedGroup) & set(dragons))) >= 2 and len(group) >= 5

# 一元牌
def oneDragon(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    return mixedGroup.count(31) >= 2 or mixedGroup.count(32) >= 2 or mixedGroup.count(33) >= 2

# 门风牌
def seatWind(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    mixedGroup = [x for part in group for x in part]
    return mixedGroup.count(seatWindTile) >= 2

# 特殊系
'''
以 11_1m 2^22m _435m 手里 6789m 铳和 9m 为例
group是和牌拆解，这里为[[0,0,0], [1,1,1], [2,3,4], [5,6,7], [8,8]]，杠牌是三元的而不是四元
seatWindTile是门风牌，27=东、28=南、29=西、30=北
melds是鸣牌，这里为[[[0,0,0], 2], [[1,1,1,1],  4], [2,3,4], 1]
    吃牌：
    0 = _123
    1 = _213
    2 = _312
    碰牌：
    0 = _111
    1 = 1_11
    2 = 11_1
    杠牌：
    0 = _1111
    1 = 11_11
    2 = 111_1
    3 = ^111
    4 = 1^11
    5 = 11^1
    6 = +11+
wait是手里听牌，这里为[5,6,7,8]
oriGroup是手牌拆解，这里为[[5,6,7], [8,8]]
winTile是和张，这里为8
way是和牌方式，自摸+1，杠开/抢杠+2，柳暗花明+4，一巡和+8，立直+16，振听+32
'''

# 门前清
def concealedHand(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return all(len(x[0]) == 4 and x[1] == 6 for x in melds)

# 门清自摸
def ccHtsumo(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return concealedHand(group, seatWindTile, melds, wait, oriGroup, winTile, way) and way % 2 ==1

# 一路顺
def allWayGreat(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(melds)==4 and all(pair[0][0] != pair[0][1] for pair in melds)

# 金钩钓
def GoldenHook(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(melds)==4 and all(pair[0][0] == pair[0][1] for pair in melds)

# 全求人
def AllBegging(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(melds)==4 and way %2 ==0

# 一巡和
def firstTurn(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return way & 8 != 0

# 柳暗花明
def lastTile(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return way & 4 != 0

# 杠上开花
def outWithReplacementTile(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return way & 3 == 3

# 抢杠和
def robbingTheKong(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return way & 3 == 2

# 平和
def Heiwa(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return len(melds)==0 and all(pair[0] != pair[1] for pair in group if len(pair)==3) and len(wait)>=2 and len(group)==5

# 字对子
def CharacterPai(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return any(27<=pair[0] and pair[0]<=33  and len(pair)==2 for pair in group)

# 立直
def Richi(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    return way>=16

# 新增：振听反和（自摸并且处于振听状态）
def FuritenReverseWin(group, seatWindTile, melds, wait, oriGroup, winTile, way):
    # 自摸（最低位1）且带有振听标记（32）
    return (way & 1) == 1 and (way & 32) != 0