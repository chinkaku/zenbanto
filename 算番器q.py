'''
自然麻将算番器 - 完全优化版
'''

from mahjonglibq import *
import re
import fan_calcq

def parse_input(s):
    # 解析副露
    melds = []
    s_meld = s
    for m in re.findall(r'\([^\)]*\)|\[[^\]]*\]', s):
        tilestr = m[1:-1]
        meld = stringToIndices(tilestr, tile_list)
        if m.startswith('['):
            melds.append([meld, 6])
        else:
            melds.append([meld, 0])
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
            way += v    # 和牌方式可以叠加
            s_meld = s_meld.replace(c, '')
    # 解析手牌
    hand = stringToIndices(s_meld, tile_list)
    return hand, melds, seatWindTile, way

def check_hand_valid(hand, melds):
    if len(hand) + 3 * len(melds) not in [13, 14]:
        return False, '手牌数量应为13或14张'
    if any(hand.count(i) > 4 for i in set(hand)):
        return False, '有牌数量超过4张'
    return True, ''

def analyze_13_tiles_optimized(hand, melds, seatWindTile):
    """
    优化的13张牌分析函数 - 一次性分析所有状态
    返回: (状态类型, 结果数据)
    """
    print("正在分析牌型...")
    
    # 一次性调用所有检测函数
    draw_result = fan_calcq.calcTFforDraw(hand, melds, seatWindTile, 0)
    semidraw_result = fan_calcq.calcTFforSemidraw(hand, melds, seatWindTile, 0)
    weak_semidraw_result = fan_calcq.calcTFforWeakSemidraw(hand, melds, seatWindTile, 0)
    
    # 计算分数
    drawScore = 3 * draw_result[1] - 6 if draw_result else 0
    semidrawScore = 2 * semidraw_result[4] - 4 if semidraw_result else 0
    weakSemidrawScore = weak_semidraw_result[4] - 2 if weak_semidraw_result else 0
    
    # 返回状态和对应的详细信息显示函数
    if drawScore >= semidrawScore and drawScore >= weakSemidrawScore and drawScore > 0:
        return "听牌", lambda: fan_calcq.calcTFforDraw(hand, melds, seatWindTile, 1)
    elif semidrawScore >= weakSemidrawScore and semidrawScore > 0:
        return "一向听", lambda: fan_calcq.calcTFforSemidraw(hand, melds, seatWindTile, 1)
    elif weakSemidrawScore > 0:
        return "弱一向听", lambda: fan_calcq.calcTFforWeakSemidraw(hand, melds, seatWindTile, 1)
    else:
        return "未成牌", None

def main():
    print('**自然麻将算番器'+'*'*20)
    print('牌张: 123456789m, 123456789s, 123456789p, 1234567z')
    print('门风: ! - 东, @ - 南, # - 西, $ - 北')
    print('和牌: % - 自摸, ^ - 杠上开花/抢杠和, & - 柳暗花明, * - 一巡和')
    print('副露: [] - 暗杠, () - 其余')
    print('手牌数模3余2算和牌, 模3余1算听牌或一向听.\n')
    print('如果手牌数模3余2, 则输入的最后一张牌视为和张.\n')
    print('输入示例: (789m)(123p)4455666s5s!%')
    print('*'*36)
    
    while True:
        s = input('请输入手牌: ')
        try:
            hand, melds, seatWindTile, way = parse_input(s)
        except Exception as e:
            print('输入解析失败:', e)
            continue
            
        # 验证副露
        fail = False
        for i in melds:
            if i[0] not in [[i[0][0], i[0][0], i[0][0], i[0][0]], [i[0][0], i[0][0], i[0][0]]]:
                validStarter = [0,1,2,3,4,5,6,9,10,11,12,13,14,15,18,19,20,21,22,23,24]
                iSort = sorted(i[0])
                if iSort[0] not in validStarter or iSort != [iSort[0], iSort[0]+1, iSort[0]+2]:
                    print('副露牌组不合法:', strlist(i[0]))
                    fail = True
                    break
        if fail:
            continue
            
        valid, msg = check_hand_valid(hand, melds)
        if not valid:
            print(msg)
            continue
            
        if seatWindTile is None:
            print('未包含门风标记，默认为东风')
            
        if len(hand) + 3 * len(melds) == 14:
            # 和牌情况
            result = fan_calcq.calc_fan_common(hand, melds, seatWindTile, way)
            if result:
                oriGroup = result[0][:]
                finalGroup = result[0][:]
                for meld in melds:
                    if len(meld[0]) == 4:
                        finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                    else:
                        finalGroup.append(meld[0])
                fan_calcq.calcTF(finalGroup, seatWindTile, melds, hand[:-1], oriGroup, hand[-1], way, print_fan_details=True)
            else:
                print('没有和牌或番数不够。')
                
        elif len(hand) + 3 * len(melds) == 13:
            # 13张牌情况 - 使用优化函数
            status, detail_func = analyze_13_tiles_optimized(hand, melds, seatWindTile)
            print(f"状态: {status}")
            
            if detail_func:
                detail_func()  # 显示详细信息
                
        else:
            print('手牌数量不正确。')

if __name__ == '__main__':
    main()