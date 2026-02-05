from mahjonglibq import *
from fanq import *
from itertools import groupby
import copy

# 预处理：按category分组，每组内按番值降序排列
fanTable_by_category = {
    11: [  # 全体系色形门一色类
        {'name': '字一色', 'category': 11, 'func': allHonors, 'value': 24, 'unique': False},
        {'name': '清一色', 'category': 11, 'func': fullFlush, 'value': 6, 'unique': False},
        {'name': '混一色', 'category': 11, 'func': halfFlush, 'value': 3, 'unique': False},
    ],
    12: [#两色类
        {'name':'镜同四面','category':12,'func':mirrorHand,'value':6,'unique':False},
        {'name':'镜同六对','category':12,'func':mirrorHand6Pairs,'value':6,'unique':False},
        {'name':'形同四面','category':12,'func':parallelHand,'value':3,'unique':False},
        {'name':'镜同四对','category':12,'func':mirrorHand4Pairs,'value':3,'unique':False},
        {'name':'形同六对','category':12,'func':parallelHand6Pairs,'value':2,'unique':False},
        {'name':'形同四对','category':12,'func':paralleHand4Pairs,'value':1,'unique':False},
        {'name':'清缺门','category':12,'func':fullCut,'value':1,'unique':False},
    ], 
    13:[#杂色类
        {'name': '九数齐', 'category': 13, 'func': nineNumbersCombined, 'value': 8, 'unique': False},
        {'name': '七连齐', 'category': 13, 'func': sevenNumbersCombined, 'value': 6, 'unique': False},
        {'name': '五连齐', 'category': 13, 'func': fiveNumbersCombined, 'value': 6, 'unique': False},
        {'name': '五门齐', 'category': 13, 'func': fiveTypesCombined, 'value': 3, 'unique': False},
        {'name': '九数全', 'category': 13, 'func': nineNumbersHave, 'value': 2, 'unique': False},
    ],
    21:[#数形门聚数类
        {'name': '二序数', 'category': 21, 'func': twoNumbers, 'value': 16, 'unique': False},
        {'name': '聚三数', 'category': 21, 'func': tripleConsecutive, 'value': 8, 'unique': False},
        {'name': '满庭芳', 'category': 21, 'func': AllHaving, 'value': 6, 'unique': False},
        {'name': '聚四数', 'category': 21, 'func': quadConsecutive, 'value': 4, 'unique': False},
        {'name': '三面芳', 'category': 21, 'func': ThreeHaving, 'value': 3, 'unique': False},
        {'name': '聚五数', 'category': 21, 'func': fifConsecutive, 'value': 2, 'unique': False},
        {'name': '两面芳', 'category': 21, 'func': TwoHaving, 'value': 1, 'unique': False},
    ],
    22: [#序数类
        {'name': '混一数', 'category': 22, 'func': mixedOnenumber, 'value': 6, 'unique': False},   
        {'name': '混二数', 'category': 22, 'func': mixedtwoNumbers, 'value': 3, 'unique': False},
    ],  
    23: [#散数类
        {'name': '一条筋', 'category': 23, 'func': allKeys, 'value': 8, 'unique': False},
        {'name': '全双数', 'category': 23, 'func': allEvens, 'value': 6, 'unique': False},
        {'name': '全单数', 'category': 23, 'func': allOdds, 'value': 4, 'unique': False},
        {'name': '清无将', 'category': 23, 'func': allNojoker, 'value': 3, 'unique': False},    
    ],
    24:[#断数类
        {'name': '断中数', 'category': 24, 'func': No456, 'value': 1, 'unique': False},
        {'name': '断幺九', 'category': 24, 'func': No19, 'value': 1, 'unique': False},
    ],
    25:[#映数类
        {'name': '映同七对', 'category': 25, 'func': reflectedHand7, 'value': 8, 'unique': False},
        {'name': '映数七对', 'category': 25, 'func': reflectNum7, 'value': 6, 'unique': False},
        {'name': '映同五面', 'category': 25, 'func': reflectedHand5, 'value': 6, 'unique': False},
        {'name': '映数五面', 'category': 25, 'func': reflectNum5, 'value': 4, 'unique': False},
        {'name': '映同四面', 'category': 25, 'func': reflectedHand4, 'value': 3, 'unique': False},
    ],
    30: [#对刻门
        {'name': '碰碰和', 'category': 30, 'func': allPungs, 'value': 3, 'unique': False},
        {'name': '七对子', 'category': 30, 'func': sevenPairs, 'value': 3, 'unique': False},
    ],
    40: [#幺九门
        {'name': '清幺九', 'category': 40, 'func': allTerminals, 'value': 12, 'unique': False},
        {'name': '清带幺', 'category': 40, 'func': pureOutsideHand, 'value': 6, 'unique': False},
        {'name': '混幺九', 'category': 40, 'func': allTerminalsAndHonors, 'value': 6, 'unique': False},
        {'name': '混带幺', 'category': 40, 'func': mixedOutsideHand, 'value': 3, 'unique': False},
    ],
    51: [#牌画门牌色类
        {'name': '绿一色', 'category': 51, 'func': allgreen, 'value': 16, 'unique': False},
        {'name': '大车轮', 'category': 51, 'func': bigwheels, 'value': 12, 'unique': False},
        {'name': '中车轮', 'category': 51, 'func': middlewheels, 'value': 12, 'unique': False},
        {'name': '小车轮', 'category': 51, 'func': smallwheels, 'value': 12, 'unique': False},
        {'name': '黑一色', 'category': 51, 'func': allblack, 'value': 12, 'unique': False},
        {'name': '断红和', 'category': 51, 'func': nored, 'value': 3, 'unique': False},
        {'name': '全带红', 'category': 51, 'func': allred, 'value': 2, 'unique': False},
    ],
    52:[#牌形类
        {'name': '推不倒', 'category': 52, 'func': cannotpush, 'value': 3, 'unique': False},
    ],
    111: [#一色类
        {'name': '四步高', 'category': 111, 'func': pureFourShiftedChows, 'value': 16, 'unique': False},
        {'name': '四连环', 'category': 111, 'func': pureFourChainedChows, 'value': 12, 'unique': False},
        {'name': '三步高', 'category': 111, 'func': pureThreeShiftedChows, 'value': 6, 'unique': False},
        {'name': '三连环', 'category': 111, 'func': pureThreeChainedChows, 'value': 4, 'unique': False},
        {'name': '一条龙', 'category': 111, 'func': pureStraight, 'value': 4, 'unique': False},
        {'name': '清两连六', 'category': 111, 'func': pureTwoSextuplets, 'value': 3, 'unique': False},
        {'name': '连六', 'category': 111, 'func': sextuplet, 'value': 1, 'unique': False},
    ],
    112:[#两色类
        {'name': '二同刻', 'category': 112, 'func': twoMixedDoublePungs, 'value': 6, 'unique': False},
        {'name': '两色同刻', 'category': 112, 'func': mixedDoublePungs, 'value': 3, 'unique': False},
        {'name': '双连六', 'category': 112, 'func': twoSextuplets, 'value': 2, 'unique': False},
        {'name': '二相逢', 'category': 112, 'func': doubletwomeets, 'value': 1, 'unique': False},
    ],
    113:[#杂色类
        {'name': '三色连刻', 'category': 113, 'func': mixedTriShiftedPungs, 'value': 4, 'unique': False},
        {'name': '三色同刻', 'category': 113, 'func': mixedTriplePungs, 'value': 3, 'unique': False},
        {'name': '三色同顺', 'category': 113, 'func': mixedTripleChows, 'value': 3, 'unique': False},
        {'name': '三色龙', 'category': 113, 'func': mixedStraight, 'value': 3, 'unique': False},
    ],
    114: [#同和类
        {'name': '四同顺', 'category': 114, 'func': pureQuadrupleChows, 'value': 40, 'unique': False},
        {'name': '三同顺', 'category': 114, 'func': pureTripleChows, 'value': 12, 'unique': False},
        {'name': '清两般高', 'category': 114, 'func': pureTwoDoubleChows, 'value': 12, 'unique': False},
        {'name': '两般高', 'category': 114, 'func': twoDoubleChows, 'value': 6, 'unique': False},
        {'name': '三色四同顺', 'category': 114, 'func': mixedQuadrupleChows, 'value': 6, 'unique': False},
        {'name': '一般高', 'category': 114, 'func': pureDoubleChows, 'value': 2, 'unique': False},
        {'name': '喜相逢', 'category': 114, 'func': twomeet, 'value': 1, 'unique': False},
    ],
    121: [#数形门聚数类
        {'name': '四顺同数', 'category': 121, 'func':fourchowsSamenum, 'value': 4, 'unique': False},
        {'name': '三顺同数', 'category': 121, 'func':threechowsSamenum, 'value': 2, 'unique': False},
    ],
    122: [#序数类
        {'name': '四牌齐', 'category': 122, 'func': fourallin, 'value': 16, 'unique': False},
        {'name': '三四归', 'category': 122, 'func': threeTileHogs, 'value': 12, 'unique': False},
        {'name': '三牌齐', 'category': 122, 'func': threeallin,'value': 8, 'unique': False},
        {'name': '两四归', 'category': 122, 'func': twoTileHogs, 'value': 6, 'unique': False},
        {'name': '四归四', 'category': 122, 'func': tileHog4, 'value': 6, 'unique': False},
        {'name': '四归三', 'category': 122, 'func': tileHog3, 'value': 3, 'unique': False},
        {'name': '四归二', 'category': 122, 'func': tileHog2, 'value': 2, 'unique': False},
        {'name': '两牌齐', 'category': 122, 'func': twoallin, 'value': 1, 'unique': False},
    ],
    123: [#散数类
        {'name': '三跳刻', 'category': 123, 'func': threeJumpedPungs, 'value': 4, 'unique': False},
        {'name': '杂三跳刻', 'category': 123, 'func': mixedTriJumpedPungs, 'value': 2, 'unique': False},
        {'name': '三跳牌', 'category': 123, 'func': threeJumpedPai, 'value': 2, 'unique': False},
    ],
    125: [#映数类
        {'name': '对中二副', 'category': 125, 'func': mirrorTwoPai, 'value': 4, 'unique': False},
        {'name': '对中刻', 'category': 125, 'func': mirrorOnePung, 'value': 2, 'unique': False},
        {'name': '对中副', 'category': 125, 'func': mirrorOnePai, 'value': 1, 'unique': False},
    ],
    126: [#特殊类
        {'name': '九莲宝灯', 'category': 126, 'func': nineGates, 'value': 40, 'unique': False},
    ],
    131: [  # 刻子门连刻类
        {'name': '五连牌', 'category': 131, 'func': fiveShiftedPai, 'value': 12, 'unique': False},
        {'name': '四连刻', 'category': 131, 'func': fourShiftedPungs, 'value': 12, 'unique': False},
        {'name': '二重连刻', 'category': 131, 'func': NichuuShiftedPungs, 'value': 8, 'unique': False},
        {'name': '三连刻', 'category': 131, 'func': threeShiftedPungs, 'value': 6, 'unique': False},
        {'name': '双二连刻', 'category': 131, 'func': doubleTwoShiftedPungs, 'value': 4, 'unique': False},
        {'name': '二连刻', 'category': 131, 'func': twoShiftedPungs, 'value': 2, 'unique': False},
    ],
   
 
    
    132: [  # 自刻类
        {'name': '四自刻', 'category': 132, 'func': fourSelfPungs, 'value': 12, 'unique': False},
        {'name': '三自刻', 'category': 132, 'func': threeSelfPungs, 'value': 6, 'unique': False},
        {'name': '两自刻', 'category': 132, 'func': twoSelfPungs, 'value': 2, 'unique': False},
    ],
    133: [  # 杠类
        {'name': '四杠', 'category': 133, 'func': fourKongs, 'value': 16, 'unique': False},
        {'name': '三杠', 'category': 133, 'func': threeKongs, 'value': 8, 'unique': False},
        {'name': '两杠', 'category': 133, 'func': twoKongs, 'value': 3, 'unique': False},
        {'name': '一杠', 'category': 133, 'func': oneKong, 'value': 1, 'unique': False},
    ],
    134: [  # 暗杠类
        {'name': '四暗杠', 'category': 134, 'func': fourAnKongs, 'value': 40, 'unique': False},
        {'name': '三暗杠', 'category': 134, 'func': threeAnKongs, 'value': 12, 'unique': False},
        {'name': '两暗杠', 'category': 134, 'func': twoAnKongs, 'value': 3, 'unique': False},
        {'name': '一暗杠', 'category': 134, 'func': oneAnKong, 'value': 1, 'unique': False},
    ],
    140:[#十三幺
        {'name': '十三幺', 'category': 140, 'func': thirteenOrphans, 'value': 16, 'unique': False},
    ],
    141: [ #风牌类
        {'name': '十六风', 'category': 141, 'func': sixteenWinds, 'value': 64, 'unique': False},
        {'name': '大四喜', 'category': 141, 'func': bigFourWinds, 'value': 40, 'unique': False},
        {'name': '七风对', 'category': 141, 'func': biggerFourWinds, 'value': 32, 'unique': False},
        {'name': '六风对', 'category': 141, 'func': middleFourWinds, 'value': 24, 'unique': False},
        {'name': '小四喜', 'category': 141, 'func': littleFourWinds, 'value': 16, 'unique': False},
        {'name': '三风刻', 'category': 141, 'func': threeWindPungs, 'value': 8, 'unique': False},
        {'name': '三风牌', 'category': 141, 'func': threeWindPai, 'value': 4, 'unique': False},
        {'name': '两风刻', 'category': 141, 'func': twoWindPungs, 'value': 3, 'unique': False},
        {'name': '两风牌', 'category': 141, 'func': twoWindPai, 'value': 1, 'unique': False},
    ],
    142: [  # 箭牌类
        {'name': '十二元', 'category': 142, 'func': twelveDragons, 'value': 24, 'unique': False},
        {'name': '五元对', 'category': 142, 'func': biggerThreeDragons, 'value': 16, 'unique': False},
        {'name': '大三元', 'category': 142, 'func': bigThreeDragons, 'value': 16, 'unique': False},
        {'name': '四元对', 'category': 142, 'func': middleThreeDragons, 'value': 12, 'unique': False},
        {'name': '小三元', 'category': 142, 'func': littleThreeDragons, 'value': 6, 'unique': False},
        {'name': '两箭刻', 'category': 142, 'func': twoDragonPungs, 'value': 4, 'unique': False},
        {'name': '两箭牌', 'category': 142, 'func': twoDragons, 'value': 2, 'unique': False},
        {'name': '一箭牌', 'category': 142, 'func': oneDragon, 'value': 1, 'unique': False},
    ],
    143: [  # 门风类
        {'name': '门风牌', 'category': 143, 'func': seatWind, 'value': 1, 'unique': False},
    ],
    210: [  # 特殊系鸣牌门
        {'name': '门清自摸', 'category': 210, 'func': ccHtsumo, 'value': 3, 'unique': False},
        {'name': '门前清', 'category': 210, 'func': concealedHand, 'value': 2, 'unique': False},
        {'name': '一路顺', 'category': 210, 'func': allWayGreat, 'value': 2, 'unique': False},
        {'name': '金钩钓', 'category': 210, 'func': GoldenHook, 'value': 2, 'unique': False},
        {'name': '全求人', 'category': 210, 'func': AllBegging, 'value': 2, 'unique': False},
    ],
    
    220: [  # 巡数门
        {'name': '一巡和', 'category': 220, 'func': firstTurn, 'value': 16, 'unique': False},
        {'name': '柳暗花明', 'category': 220, 'func': lastTile, 'value': 3, 'unique': False},
    ],
    230: [  # 杠子门
        {'name': '杠上开花', 'category': 230, 'func': outWithReplacementTile, 'value': 3, 'unique': False},
        {'name': '抢杠和', 'category': 230, 'func': robbingTheKong, 'value': 3, 'unique': False},
    ],
    250: [  #特型门
        {'name': '平和', 'category': 250, 'func': Heiwa, 'value': 2, 'unique': False},
        
    ],
    260: [  #雀头门
        {'name': '字雀头', 'category': 260, 'func': CharacterPai, 'value': 1, 'unique': False},
        
    ],
    310:[#立直门
        {'name': '振听反和', 'category': 310, 'func': FuritenReverseWin, 'value': 4, 'unique': False},
        {'name': '立直', 'category': 310, 'func': Richi, 'value': 3, 'unique': False},
    ]
}

def calcTF(group, seatWindTile, melds, wait, oriGroup, winTile, way, print_fan_details=False, situation=2):
    """
    优化版本的番值计算 - 按category分组，每组只计算最高番值的番种
    """
    valid_fans = []
    
    # 按category处理，每个category只取第一个满足条件的（即番值最高的）
    for category, fans in fanTable_by_category.items():
        for fan in fans:  # fans已经按番值降序排列
            if fan['func'](group, seatWindTile, melds, wait, oriGroup, winTile, way):
                valid_fans.append(fan)
                break  # 找到该category中的最高番值，跳出内循环
    
    # 如果没有满足条件的番种，返回0
    if not valid_fans:
        if print_fan_details:
            print("没有满足条件的番种")
        return 0
    
    # 分离unique和non-unique番种
    unique_fans = [fan for fan in valid_fans if fan['unique']]
    non_unique_fans = [fan for fan in valid_fans if not fan['unique']]
    
    # 计算non-unique番种的总分
    non_unique_score = sum(fan['value'] for fan in non_unique_fans)
    
    # 计算unique番种的最大分数
    unique_score = max((fan['value'] for fan in unique_fans), default=0)
    best_unique_fan = max(unique_fans, key=lambda x: x['value']) if unique_fans else None
    
    # 选择得分更高的方案
    final_score = max(non_unique_score, unique_score)
    
    # 打印详细信息
    if print_fan_details:
        print("\n"+"="*20)
        if final_score == non_unique_score and non_unique_score >= unique_score:
            if non_unique_fans:
                for fan in non_unique_fans:
                    print(f"{fan['name']} ({fan['value']}番)")
        elif best_unique_fan and final_score == unique_score:
            print(f"{best_unique_fan['name']} ({unique_score}番)")
        print("\n"+"="*20)
        print(f"总番值: {final_score}番")
        if situation == 2:
            print(f"总分数: {4*final_score-8}分\n")
        elif situation == 1:
            print(f"总分数: {3*final_score-6}分\n")
        elif situation == 0:
            print(f"总分数: {2*final_score-4}分\n")
        elif situation == -1:
            print(f"总分数: {final_score-2}分\n")
        print("="*20)
    
    return final_score

def calc_fan_common(hand, melds, seatWindTile, way, minFan=3, special=False):
    """
    提取算番通用函数 - 添加早期退出优化
    """
    maxcombination = []
    winTile = hand[-1]
    wait = sorted([t for t in hand if t != winTile] + [t for t in hand if t == winTile][1:])

    for combination in findCombinations(hand, special):
        oriGroup = combination[:]
        finalGroup = combination[:]
        for meld in melds:
            if len(meld[0]) == 4:
                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
            else:
                finalGroup.append(meld[0])
        if len(finalGroup) not in [2, 5, 7]:
            continue
        
        fanValue = calcTF(finalGroup, seatWindTile, melds, wait, oriGroup, winTile, way, situation=2)

        if fanValue >= minFan:
            if not maxcombination:
                maxcombination = [combination, fanValue]
            elif fanValue > maxcombination[1]:
                maxcombination = [combination, fanValue]
                
    return maxcombination

def checkDraw(group, special=False):
    """
    优化的听牌检查 - 减少不必要的复制
    """
    if len(group) % 3 != 1:
        return []
    waitingList = []
    for i in range(34):
        group2 = group + [i]  # 使用加法而不是append+复制
        if findCombinations(group2, special):
            waitingList.append(i)
    return waitingList

def calcTFforDraw(wait, melds, seatWindTile, print_fan_details=0, special=False, riichi=0):
    """
    优化的听牌算番
    """
    waitingList = checkDraw(wait, special)
    tileinHand = wait[:]
    for meld in melds:
        tileinHand.extend(meld[0])
    
    tileinHand.sort()
    # 修正：如果一张牌已经有5张，则听牌本身不合法
    if any(tileinHand.count(x) >= 5 for x in set(tileinHand)):  # 优化：先去重再检查
        return []
    # 修正：如果一张牌已经有4张，则不能再和这张牌了
    waitingList = [i for i in waitingList if tileinHand.count(i) < 4]

    maxforDraw = []
    allDraws = []
    if not waitingList:
        return []
    
    for i in waitingList:
        wholeHand = wait + [i]
        maxCombination = calc_fan_common(wholeHand, melds, seatWindTile, 16 * riichi, 3, special)
        if not maxCombination:
            continue
        allDraws.append([i, maxCombination[1]])
        if not maxforDraw or maxCombination[1] > maxforDraw[1]:
            maxforDraw = [i, maxCombination[1]]
    
    if print_fan_details == 1:
        print(f"高目: {tile_list[maxforDraw[0]]}")
        maxcombination = calc_fan_common(wait + [maxforDraw[0]], melds, seatWindTile, 16 * riichi, 3, special)
        oriGroup = maxcombination[0][:]
        finalGroup = maxcombination[0][:]
        for meld in melds:
            if len(meld[0]) == 4:
                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
            else:
                finalGroup.append(meld[0])
        calcTF(finalGroup, seatWindTile, melds, wait, oriGroup, maxforDraw[0], 16 * riichi, True, situation=1)
    elif print_fan_details == 2:
        drawInfo1 = yellow(f"已听牌 {maxforDraw[1]}番{3*maxforDraw[1]-6}分")
        drawInfo2 = yellow("听牌列表: ")
        for i in allDraws:
            drawInfo2 += f"{tile_list[i[0]]}({i[1]}番 和牌{4*i[1]-8}分) "
        print(drawInfo1)
        print(drawInfo2)
    
    return maxforDraw

def calcTFforDraw14(hand, melds, seatWindTile, print_fan_details=0, special=False):
    """
    优化的14张牌听牌检查 - 避免重复检查相同的牌
    """
    if len(hand) % 3 != 2:
        return []
    correctList = []
    checked_tiles = set()  # 避免重复检查相同的牌
    
    for i in range(len(hand)):
        tile = hand[i]
        if tile in checked_tiles:
            continue
        checked_tiles.add(tile)
        
        wait = hand[:]
        wait.pop(i)
        if not checkDraw(wait, special):
            continue
        maxforDraw = calcTFforDraw(wait, melds, seatWindTile, 0, special)
        if maxforDraw:
            correctList.append([tile, maxforDraw[0], maxforDraw[1]])
    
    if print_fan_details == 1:
        for i in correctList:
            print(f"打出{tile_list[i[0]]}后，高目为{tile_list[i[1]]}，番值{i[2]}番，听牌得分{3*i[2]-6}分")
    
    return correctList

def checkHandPeng(hand, lastTile):
    return hand.count(lastTile) >= 2

def checkHandLeftChi(hand, lastTile):
    valid = [2,3,4,5,6,7,8,11,12,13,14,15,16,17,20,21,22,23,24,25,26]
    return lastTile in valid and lastTile-1 in hand and lastTile-2 in hand

def checkHandMiddleChi(hand, lastTile):
    valid = [1,2,3,4,5,6,7,10,11,12,13,14,15,16,19,20,21,22,23,24,25]
    return lastTile in valid and lastTile+1 in hand and lastTile-1 in hand

def checkHandRightChi(hand, lastTile):
    valid = [0,1,2,3,4,5,6,9,10,11,12,13,14,15,18,19,20,21,22,23,24]
    return lastTile in valid and lastTile+1 in hand and lastTile+2 in hand

def checkHandPair(hand, lastTile):
    return hand.count(lastTile) >= 1

def checkHandThirteenOrphans(hand, lastTile):
    o13 = [0,8,9,17,18,26,27,28,29,30,31,32,33]
    if lastTile not in o13:
        return False
    return all(x in (hand + [lastTile]) for x in o13)

def calcTFforSemidraw(wait, melds, seatWindTile, print_fan_details=0):
    """
    优化的一向听计算
    """
    # 这种情况下手牌为3n+1，摸完牌，再打完牌才能听牌，当前为一向听
    # 1. 找出所有可以组成听牌的牌并算番
    waitingList = []
    maxSemidraw = []
    for penult in range(34):
        if not (checkHandPeng(wait, penult) or checkHandLeftChi(wait, penult) or 
                checkHandMiddleChi(wait, penult) or checkHandRightChi(wait, penult)):
            continue    # 这张牌无法用来吃碰，不符合规则
            
        if checkHandPeng(wait, penult):  #Situation 1: 碰
            hand = wait[:]
            hand.remove(penult)
            hand.remove(penult)
            meldsNew = melds[:]
            meldsNew.append([[penult, penult, penult], 0])  # 明刻
            correctList = calcTFforDraw14(hand, meldsNew, seatWindTile, 0)
            if not correctList:
                continue    # 这张牌无法使玩家听牌，不符合规则
            maxDrawforSemidraw = max(correctList, key=lambda x: x[2])
            waitingList.append([penult, 0] + maxDrawforSemidraw)
            
        if checkHandLeftChi(wait, penult):  #Situation 2: 左吃
            hand = wait[:]
            hand.remove(penult-1)
            hand.remove(penult-2)
            meldsNew = melds[:]
            meldsNew.append([[penult-2, penult-1, penult], 2])  # 明顺
            correctList = calcTFforDraw14(hand, meldsNew, seatWindTile, 0)
            if not correctList:
                continue    # 这张牌无法使玩家听牌，不符合规则
            maxDrawforSemidraw = max(correctList, key=lambda x: x[2])
            waitingList.append([penult, 1] + maxDrawforSemidraw)
            
        if checkHandMiddleChi(wait, penult):  #Situation 3: 中吃
            hand = wait[:]
            hand.remove(penult-1)
            hand.remove(penult+1)
            meldsNew = melds[:]
            meldsNew.append([[penult-1, penult, penult+1], 1])  # 明顺
            correctList = calcTFforDraw14(hand, meldsNew, seatWindTile, 0)
            if not correctList:
                continue    # 这张牌无法使玩家听牌，不符合规则
            maxDrawforSemidraw = max(correctList, key=lambda x: x[2])
            waitingList.append([penult, 2] + maxDrawforSemidraw)
            
        if checkHandRightChi(wait, penult):  #Situation 4: 右吃
            hand = wait[:]
            hand.remove(penult+1)
            hand.remove(penult+2)
            meldsNew = melds[:]
            meldsNew.append([[penult, penult+1, penult+2], 0])  # 明顺
            correctList = calcTFforDraw14(hand, meldsNew, seatWindTile, 0)
            if not correctList:
                continue    # 这张牌无法使玩家听牌，不符合规则
            maxDrawforSemidraw = max(correctList, key=lambda x: x[2])
            waitingList.append([penult, 3] + maxDrawforSemidraw)
    
    if not waitingList:
        return []   # 不是一向听
    
    # 2. 找出最大番值
    maxSemidraw = max(waitingList, key=lambda x: x[4])

    # 3. 如果需要打印详细情况
    if print_fan_details == 1 and maxSemidraw:
        print(f"高目: +{tile_list[maxSemidraw[0]]} -{tile_list[maxSemidraw[2]]} +{tile_list[maxSemidraw[3]]}")
        finalHand = wait[:]
        finalMelds = melds[:]
        if maxSemidraw[1] == 0:
            finalHand.remove(maxSemidraw[0])
            finalHand.remove(maxSemidraw[0])
            finalMelds.append([[maxSemidraw[0], maxSemidraw[0], maxSemidraw[0]], 0])  # 明刻
        elif maxSemidraw[1] == 1:
            finalHand.remove(maxSemidraw[0]-1)
            finalHand.remove(maxSemidraw[0]-2)
            finalMelds.append([[maxSemidraw[0]-2, maxSemidraw[0]-1, maxSemidraw[0]], 2])  # 明顺
        elif maxSemidraw[1] == 2:
            finalHand.remove(maxSemidraw[0]-1)
            finalHand.remove(maxSemidraw[0]+1)
            finalMelds.append([[maxSemidraw[0]-1, maxSemidraw[0], maxSemidraw[0]+1], 1])  # 明顺
        else:
            finalHand.remove(maxSemidraw[0]+1)
            finalHand.remove(maxSemidraw[0]+2)
            finalMelds.append([[maxSemidraw[0], maxSemidraw[0]+1, maxSemidraw[0]+2], 0])  # 明顺
        finalHand.remove(maxSemidraw[2])
        drawWait = finalHand[:]
        finalHand.append(maxSemidraw[3])
        maxcombination = calc_fan_common(finalHand, finalMelds, seatWindTile, 0, 3)
        oriGroup = maxcombination[0][:]
        finalGroup = maxcombination[0][:]
        for meld in finalMelds:
            if len(meld[0]) == 4:
                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
            else:
                finalGroup.append(meld[0])
        calcTF(finalGroup, seatWindTile, finalMelds, drawWait, oriGroup, maxSemidraw[3], 0, True, situation=0)

    return maxSemidraw

def calcTFforWeakSemidraw(wait, melds, seatWindTile, print_fan_details=0):
    """
    优化的弱一向听计算
    """
    if len(wait) != 13 or melds != []:
        return []   # 弱一向听的前提是手牌门清
    waitingList = []
    maxWeakSemidraw = []
    for penult in range(34):
        if not(checkHandPair(wait, penult) or checkHandThirteenOrphans(wait, penult)):
            continue    # 这张牌无法用来组成面子，不符合规则
        hand = wait[:]
        hand.append(penult)
        correctList = calcTFforDraw14(hand, melds, seatWindTile, 0, True)
        if not correctList:
            continue    # 这张牌无法使玩家听牌特殊和牌型，不符合规则
        maxDrawforWeakSemidraw = max(correctList, key=lambda x: x[2])
        waitingList.append([penult, 4] + maxDrawforWeakSemidraw)
    if not waitingList:
        return []   # 不是弱一向听
    
    # 2. 找出最大番值
    maxWeakSemidraw = max(waitingList, key=lambda x: x[4])

    # 3. 如果需要打印详细情况
    if print_fan_details == 1 and maxWeakSemidraw:
        print(f"高目: d{tile_list[maxWeakSemidraw[0]]} -{tile_list[maxWeakSemidraw[2]]} +{tile_list[maxWeakSemidraw[3]]}")
        finalHand = wait[:]
        finalMelds = melds[:]
        finalHand.append(maxWeakSemidraw[0])
        finalHand.remove(maxWeakSemidraw[2])
        drawWait = finalHand[:]
        finalHand.append(maxWeakSemidraw[3])
        maxcombination = calc_fan_common(finalHand, finalMelds, seatWindTile, 0, 3, True)
        oriGroup = maxcombination[0][:]
        finalGroup = maxcombination[0][:]
        calcTF(finalGroup, seatWindTile, finalMelds, drawWait, oriGroup, maxWeakSemidraw[3], 0, True, situation=-1)

    return maxWeakSemidraw

def calcTF_with_names(group, seatWindTile, melds, wait, oriGroup, winTile, way, situation=2):
    """
    返回 (番型名list, 番值list, 最大番数) 供网页显示用
    """
    valid_fans = []
    # 使用优化的算法
    for category, fans in fanTable_by_category.items():
        for fan in fans:
            if fan['func'](group, seatWindTile, melds, wait, oriGroup, winTile, way):
                valid_fans.append(fan)
                break  # 每个category只取最高番值
    
    if not valid_fans:
        return [], [], 0  # 没有番型

    unique_fans = [fan for fan in valid_fans if fan['unique']]
    non_unique_fans = [fan for fan in valid_fans if not fan['unique']]

    non_unique_score = sum(fan['value'] for fan in non_unique_fans)
    non_unique_names = [fan['name'] for fan in non_unique_fans]
    non_unique_values = [fan['value'] for fan in non_unique_fans]

    unique_score = max([fan['value'] for fan in unique_fans], default=0)
    unique_name = max(unique_fans, key=lambda x: x['value'])['name'] if unique_fans else None
    unique_value = max(unique_fans, key=lambda x: x['value'])['value'] if unique_fans else None

    if non_unique_score >= unique_score:
        final_score = non_unique_score
        names = non_unique_names
        values = non_unique_values
    else:
        final_score = unique_score
        names = [unique_name] if unique_name else []
        values = [unique_value] if unique_name else []

    return names, values, final_score

def calc_fan_common_with_names(hand, melds, seatWindTile, way, minFan=3, special=False):
    """
    返回 [最大组合, [番型名list], [番值list], 最大番数]
    """
    maxcombination = []
    maxfan_names = []
    maxfan_values = []
    maxfan_value = 0
    winTile = hand[-1]
    wait = sorted([t for t in hand if t != winTile] + [t for t in hand if t == winTile][1:])

    for combination in findCombinations(hand, special):
        oriGroup = combination[:]
        finalGroup = combination[:]
        for meld in melds:
            if len(meld[0]) == 4:
                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
            else:
                finalGroup.append(meld[0])
        if len(finalGroup) not in [2, 5, 7]:
            continue

        names, values, score = calcTF_with_names(
            finalGroup, seatWindTile, melds, wait, oriGroup, winTile, way
        )

        if score >= minFan and score > maxfan_value:
            maxcombination = combination
            maxfan_names = names
            maxfan_values = values
            maxfan_value = score

    if maxfan_value > 0:
        return [maxcombination, maxfan_names, maxfan_values, maxfan_value]
    else:
        return []

def get_all_tingpais(wait, melds, seatWindTile, special=False, riichi=0):
    """
    返回所有听牌及其番数list: [(听牌索引, 番数)]
    """
    waitingList = checkDraw(wait, special)
    tileinHand = wait[:]
    for meld in melds:
        tileinHand.extend(meld[0])
    waitingList = [i for i in waitingList if tileinHand.count(i) < 4]
    allDraws = []
    if not waitingList:
        return []
    for i in waitingList:
        wholeHand = wait + [i]
        maxCombination = calc_fan_common(wholeHand, melds, seatWindTile, 16 * riichi, 3, special)
        if not maxCombination:
            continue
        allDraws.append((i, maxCombination[1]))
    return allDraws