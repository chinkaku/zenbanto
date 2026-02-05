import streamlit as st
from mahjonglibq import *
from fan_calcq import calc_fan_common, calcTFforDraw, calcTFforSemidraw, calcTFforWeakSemidraw, calcTF
import re

# 配置缓存
st.set_page_config(page_title="自然麻将算番器", layout="wide")

# 缓存解析函数
@st.cache_data
def cached_parse_input(s):
    return parse_input(s)

# 缓存算番函数 - 修复melds数据结构
@st.cache_data
def cached_calc_fan_common(hand_tuple, melds_tuple, seatWindTile, way, minFan=3, special=False):
    hand = list(hand_tuple)
    # 修复：正确重建melds数据结构
    melds = []
    for meld_data in melds_tuple:
        tiles, meld_type = meld_data
        melds.append([list(tiles), meld_type])
    return calc_fan_common(hand, melds, seatWindTile, way, minFan, special)

@st.cache_data
def cached_calcTFforDraw(hand_tuple, melds_tuple, seatWindTile, print_details=0, special=False):
    hand = list(hand_tuple)
    melds = []
    for meld_data in melds_tuple:
        tiles, meld_type = meld_data
        melds.append([list(tiles), meld_type])
    return calcTFforDraw(hand, melds, seatWindTile, print_details, special)

@st.cache_data
def cached_calcTFforSemidraw(hand_tuple, melds_tuple, seatWindTile, print_details=0):
    hand = list(hand_tuple)
    melds = []
    for meld_data in melds_tuple:
        tiles, meld_type = meld_data
        melds.append([list(tiles), meld_type])
    return calcTFforSemidraw(hand, melds, seatWindTile, print_details)

@st.cache_data
def cached_calcTFforWeakSemidraw(hand_tuple, melds_tuple, seatWindTile, print_details=0):
    hand = list(hand_tuple)
    melds = []
    for meld_data in melds_tuple:
        tiles, meld_type = meld_data
        melds.append([list(tiles), meld_type])
    return calcTFforWeakSemidraw(hand, melds, seatWindTile, print_details)

@st.cache_data
def cached_analyze_13_tiles(hand_tuple, melds_tuple, seatWindTile):
    """缓存的13张牌分析函数"""
    hand = list(hand_tuple)
    melds = []
    for meld_data in melds_tuple:
        tiles, meld_type = meld_data
        melds.append([list(tiles), meld_type])
    
    # 一次性调用所有检测函数
    draw_result = calcTFforDraw(hand, melds, seatWindTile, 0)
    semidraw_result = calcTFforSemidraw(hand, melds, seatWindTile, 0)
    weak_semidraw_result = calcTFforWeakSemidraw(hand, melds, seatWindTile, 0)
    
    # 计算分数
    drawScore = 3 * draw_result[1] - 6 if draw_result else 0
    semidrawScore = 2 * semidraw_result[4] - 4 if semidraw_result else 0
    weakSemidrawScore = weak_semidraw_result[4] - 2 if weak_semidraw_result else 0
    
    # 返回状态和结果数据
    if drawScore >= semidrawScore and drawScore >= weakSemidrawScore and drawScore > 0:
        return "听牌", drawScore, draw_result
    elif semidrawScore >= weakSemidrawScore and semidrawScore > 0:
        return "一向听", semidrawScore, semidraw_result
    elif weakSemidrawScore > 0:
        return "弱一向听", weakSemidrawScore, weak_semidraw_result
    else:
        return "未成牌", 0, None

def to_halfwidth(s):
    """全角转半角"""
    res = []
    for c in s:
        code = ord(c)
        if code == 0x3000:
            res.append(' ')
        elif 0xFF01 <= code <= 0xFF5E:
            res.append(chr(code - 0xFEE0))
        elif c in '（）［］【】｛｝《》""''':
            res.append({
                '（':'(', '）':')', '［':'[', '］':']', '【':'[', '】':']',
                '｛':'{', '｝':'}', '《':'<', '》':'>',
                '"':'"', '"':'"', ''':"'", ''':"'"}.get(c, c))
        else:
            res.append(c)
    return ''.join(res)

def parse_input(s):
    """解析输入字符串为手牌、副露、门风、和牌方式"""
    s = to_halfwidth(s)
    melds = []
    s_meld = s
    
    # 解析副露
    for m in re.findall(r'\([^\)]*\)|\[[^\]]*\]', s):
        tilestr = m[1:-1]
        meld = stringToIndices(tilestr, tile_list)
        if m.startswith('['):
            melds.append([meld, 6])  # 暗杠
        else:
            melds.append([meld, 0])  # 其他鸣牌
        s_meld = s_meld.replace(m, '')
    
    # 解析门风
    seatWindTile = 27  # 默认东风
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
    return hand, melds, seatWindTile, way

def check_hand_valid(hand, melds):
    """验证手牌合法性"""
    total_tiles = len(hand) + 3 * len(melds)
    if total_tiles not in [13, 14]:
        return False, '手牌数量应为13或14张'
    
    # 检查每种牌是否超过4张
    all_tiles = hand[:]
    for meld in melds:
        all_tiles.extend(meld[0])
    
    if any(all_tiles.count(i) > 4 for i in set(all_tiles)):
        return False, '有牌数量超过4张'
    
    return True, ''

def print_fan_result(finalGroup, seatWindTile, melds, hand, oriGroup, winTile, way, situation=2):
    """格式化番型结果"""
    from fan_calcq import calcTF_with_names
    names, values, final_score = calcTF_with_names(
        finalGroup, seatWindTile, melds, hand, oriGroup, winTile, way, situation=situation
    )
    
    output = ""
    if names:
        for n, v in zip(names, values):
            output += f"{n} ({v}番)\n"
    
    output += f"\n总番值: {final_score}番\n"
    
    # 根据不同情况计算分数
    if situation == 2:
        output += f"总分数: {4*final_score-8}分\n"
    elif situation == 1:
        output += f"总分数: {3*final_score-6}分\n"
    elif situation == 0:
        output += f"总分数: {2*final_score-4}分\n"
    elif situation == -1:
        output += f"总分数: {final_score-2}分\n"
    
    return output

def get_semidraw_detail(hand, melds, seatWindTile, result_data, status):
    """获取一向听的详细番型信息"""
    try:
        if status == "一向听":
            # 模拟一向听的完整流程
            finalHand = hand[:]
            finalMelds = melds[:]
            
            # 根据result_data[1]的值执行对应操作
            if result_data[1] == 0:  # 碰
                finalHand.remove(result_data[0])
                finalHand.remove(result_data[0])
                finalMelds.append([[result_data[0], result_data[0], result_data[0]], 0])
            elif result_data[1] == 1:  # 左吃
                finalHand.remove(result_data[0]-1)
                finalHand.remove(result_data[0]-2)
                finalMelds.append([[result_data[0]-2, result_data[0]-1, result_data[0]], 2])
            elif result_data[1] == 2:  # 中吃
                finalHand.remove(result_data[0]-1)
                finalHand.remove(result_data[0]+1)
                finalMelds.append([[result_data[0]-1, result_data[0], result_data[0]+1], 1])
            else:  # 右吃
                finalHand.remove(result_data[0]+1)
                finalHand.remove(result_data[0]+2)
                finalMelds.append([[result_data[0], result_data[0]+1, result_data[0]+2], 0])
            
            finalHand.remove(result_data[2])
            drawWait = finalHand[:]
            finalHand.append(result_data[3])
            
            # 计算最终番型
            res = calc_fan_common(finalHand, finalMelds, seatWindTile, 0, 3)
            if res:
                oriGroup = res[0][:]
                finalGroup = res[0][:]
                for meld in finalMelds:
                    if len(meld[0]) == 4:
                        finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                    else:
                        finalGroup.append(meld[0])
                
                return print_fan_result(finalGroup, seatWindTile, finalMelds, drawWait, oriGroup, result_data[3], 0, situation=0)
        
        elif status == "弱一向听":
            # 模拟弱一向听的完整流程
            finalHand = hand[:]
            finalMelds = melds[:]
            finalHand.append(result_data[0])
            finalHand.remove(result_data[2])
            drawWait = finalHand[:]
            finalHand.append(result_data[3])
            
            res = calc_fan_common(finalHand, finalMelds, seatWindTile, 0, 3, True)
            if res:
                oriGroup = res[0][:]
                finalGroup = res[0][:]
                
                return print_fan_result(finalGroup, seatWindTile, finalMelds, drawWait, oriGroup, result_data[3], 0, situation=-1)
        
        return f"状态: {status}\n分数: {result_data[4] if len(result_data) > 4 else 0}分"
    except:
        return f"状态: {status}\n分数: {result_data[4] if len(result_data) > 4 else 0}分"

def display_cached_result(status, result_text, result_data=None):
    """正确显示缓存的结果，无缓存提示"""
    if status == "和牌":
        st.success("✅ 状态: 和牌")
        st.code(result_text)
        
    elif status == "听牌":
        st.success("✅ 状态: 听牌")
        # 从缓存的result_text中提取高目信息
        lines = result_text.split('\n')
        if lines and lines[0].startswith("高目:"):
            st.info(f"🎯 {lines[0]}")
            # 显示剩余的番型信息
            remaining_text = '\n'.join(lines[2:]) if len(lines) > 2 else ""
            if remaining_text.strip():
                st.code(remaining_text)
        else:
            st.code(result_text)
            
    elif status in ["一向听", "弱一向听"]:
        st.success(f"✅ 状态: {status}")
        # 如果有详细的高目信息，先显示
        if result_data:
            if status == "一向听":
                plus = tile_list[result_data[0]]
                minus = tile_list[result_data[2]]
                plus2 = tile_list[result_data[3]]
                st.info(f"🎯 高目: +{plus} -{minus} +{plus2}")
            else:  # 弱一向听
                st.info(f"🎯 高目: d{tile_list[result_data[0]]} -{tile_list[result_data[2]]} +{tile_list[result_data[3]]}")
        st.code(result_text)
        
    elif status == "无效":
        st.warning("⚠️ 没有和牌或番数不够")
        
    elif status == "未成牌":
        st.warning("⚠️ 状态: 未成牌")

# CSS样式
st.markdown("""
<style>
.main > div { 
    padding-top: 1rem; 
}

/* 精确调整按钮位置，与输入框对齐 */
.stButton > button {
    width: 100%;
    height: 2.4rem;
    margin-top: 1.75rem !important;
    margin-bottom: 0 !important;
}

/* 确保输入框标准高度 */
.stTextInput > div > div > input {
    height: 2.4rem;
}

/* 移除按钮容器的默认边距 */
.stButton {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* 确保文本输入框label的标准间距 */
.stTextInput > label {
    margin-bottom: 0.5rem;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .stColumns {
        flex-direction: column;
    }
    
    .stButton > button {
        margin-top: 0.5rem !important;
        height: auto;
    }
}
</style>
""", unsafe_allow_html=True)

# 页面标题
st.title("自然麻将算番器")
st.markdown("---")

# 使用说明
with st.expander("📖 使用说明", expanded=False):
    st.markdown("""
    - **牌张**: 123456789m/s/p, 1234567z
    - **门风**: ! 东 @ 南 # 西 $ 北  
    - **和牌**: % 自摸 ^ 杠开/抢杠 & 柳暗花明 * 一巡和
    - **副露**: [] 暗杠 () 其他鸣牌
    - **示例**: `(789m)(123p)4455666s5s!%`
    
    **常用测试手牌:**
    - 和牌: `[1111z][2222z][3333z][4444z]!%^&`
    - 听牌: `1112345678999m`
    - 清一色: `1111222333444m`
    - 七对子: `1122334455667z#`
    """)

def main():
    # 使用session_state避免重复计算
    if 'last_input' not in st.session_state:
        st.session_state.last_input = ""
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

    # 输入区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        s = st.text_input("请输入手牌：", placeholder="例: (789m)(123p)4455666s5s!%")
    
    with col2:
        calculate = st.button("🎯 计算", type="primary")
    
    # 主要计算逻辑
    if calculate and s.strip():
        # 检查缓存但正常显示结果，无缓存提示
        if s == st.session_state.last_input and st.session_state.last_result:
            # 正确显示缓存的结果，无特殊提示
            if len(st.session_state.last_result) == 3:
                status, result_text, result_data = st.session_state.last_result
                display_cached_result(status, result_text, result_data)
            else:
                status, result_text = st.session_state.last_result
                display_cached_result(status, result_text)
            return
            
        try:
            # 解析输入
            hand, melds, seatWindTile, way = parse_input(s)
            
            # 修复：正确转换melds为可哈希的格式用于缓存
            hand_tuple = tuple(hand)
            melds_tuple = tuple((tuple(meld[0]), meld[1]) for meld in melds)
            
        except Exception as e:
            st.error(f"❌ 输入解析失败: {e}")
            return
        
        # 验证手牌合法性
        valid, msg = check_hand_valid(hand, melds)
        if not valid:
            st.error(f"❌ {msg}")
            return
            
        # 验证副露格式
        fail = False
        for i in melds:
            # 检查是否为刻子或杠子
            if len(set(i[0])) == 1:
                continue  # 刻子/杠子，跳过
            
            # 检查顺子
            validStarter = [0,1,2,3,4,5,6,9,10,11,12,13,14,15,18,19,20,21,22,23,24]
            iSort = sorted(i[0])
            if len(iSort) == 3 and iSort[0] in validStarter and iSort == [iSort[0], iSort[0]+1, iSort[0]+2]:
                continue  # 顺子，跳过
            
            # 不符合规则
            st.error(f"❌ 副露牌组不合法: {strlist(i[0])}")
            fail = True
            break
            
        if fail:
            return
            
        # 使用缓存进行计算
        with st.spinner("⚡ 正在计算..."):
            total_tiles = len(hand) + 3 * len(melds)
            
            if total_tiles == 14:
                # 14张和牌情况
                result = cached_calc_fan_common(hand_tuple, melds_tuple, seatWindTile, way)
                if result:
                    oriGroup = result[0][:]
                    finalGroup = result[0][:]
                    
                    # 添加副露到最终组合
                    for meld in melds:
                        if len(meld[0]) == 4:  # 杠子只算3张
                            finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                        else:
                            finalGroup.append(meld[0])
                    
                    st.success("✅ 状态: 和牌")
                    result_text = print_fan_result(finalGroup, seatWindTile, melds, hand[:-1], oriGroup, hand[-1], way, situation=2)
                    st.code(result_text)
                    
                    # 保存缓存数据
                    st.session_state.last_result = ("和牌", result_text)
                else:
                    st.warning("⚠️ 没有和牌或番数不够")
                    st.session_state.last_result = ("无效", "没有和牌或番数不够")
                    
            elif total_tiles == 13:
                # 13张听牌/一向听/弱一向听情况
                status, score, result_data = cached_analyze_13_tiles(hand_tuple, melds_tuple, seatWindTile)
                
                if status == "听牌" and result_data:
                    st.success("✅ 状态: 听牌")
                    high_tile = result_data[0]
                    st.info(f"🎯 高目: {tile_list[high_tile]}")
                    
                    # 计算听牌和牌后的番型
                    hand14 = hand + [high_tile]
                    hand14_tuple = tuple(hand14)
                    res = cached_calc_fan_common(hand14_tuple, melds_tuple, seatWindTile, 0)
                    
                    if res:
                        oriGroup = res[0][:]
                        finalGroup = res[0][:]
                        
                        for meld in melds:
                            if len(meld[0]) == 4:
                                finalGroup.append([meld[0][0], meld[0][1], meld[0][2]])
                            else:
                                finalGroup.append(meld[0])
                        
                        result_text = print_fan_result(finalGroup, seatWindTile, melds, hand, oriGroup, high_tile, 0, situation=1)
                        st.code(result_text)
                        
                        # 保存完整的显示文本，包含高目信息
                        full_result_text = f"高目: {tile_list[high_tile]}\n\n" + result_text
                        st.session_state.last_result = ("听牌", full_result_text, result_data)
                        
                elif status in ["一向听", "弱一向听"] and result_data:
                    st.success(f"✅ 状态: {status}")
                    
                    if status == "一向听":
                        plus = tile_list[result_data[0]]
                        minus = tile_list[result_data[2]]
                        plus2 = tile_list[result_data[3]]
                        st.info(f"🎯 高目: +{plus} -{minus} +{plus2}")
                    else:  # 弱一向听
                        st.info(f"🎯 高目: d{tile_list[result_data[0]]} -{tile_list[result_data[2]]} +{tile_list[result_data[3]]}")
                    
                    # 修复：计算并显示详细的番型信息
                    result_text = get_semidraw_detail(hand, melds, seatWindTile, result_data, status)
                    st.code(result_text)
                    st.session_state.last_result = (status, result_text, result_data)
                    
                else:
                    st.warning("⚠️ 状态: 未成牌")
                    st.session_state.last_result = ("未成牌", "", None)
                    
            else:
                st.error("❌ 手牌数量不正确")
                return
                
        # 缓存输入
        st.session_state.last_input = s
        
    elif calculate and not s.strip():
        st.error("❌ 请输入手牌")

if __name__ == '__main__':
    main()