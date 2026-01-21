import streamlit as st
import random
import os
from mahjonglibq import *
import fan_calcq
import base64
from collections import Counter

import shutil

# 手动清除缓存（在代码开头添加）
cache_path = os.path.join(os.getcwd(), "__pycache__")
if os.path.exists(cache_path):
    shutil.rmtree(cache_path)

# 清除streamlit缓存
st.cache_data.clear()
st.cache_resource.clear()
st.set_page_config(page_title="自然麻将 全斗番")

if 'bg_music_enabled' not in st.session_state:
    st.session_state.bg_music_enabled = False
if 'music_initialized' not in st.session_state:
    st.session_state.music_initialized = False
# 添加背景音乐控制功能
def add_background_music():
    """添加背景音乐功能 - 改进版"""
    # 初始化
    if 'music_status' not in st.session_state:
        st.session_state.music_status = "stopped"  # stopped, playing
    
    audio_file = "永劫之春V3.mp3"
    
    # 检查文件是否存在
    if not os.path.exists(audio_file):
        st.sidebar.warning("❌ 音乐文件未找到")
        return
    
    # 音乐控制
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎵 背景音乐")
        
        if st.session_state.music_status == "stopped":
            if st.button("▶️ 播放背景音乐", use_container_width=True):
                st.session_state.music_status = "playing"
                st.rerun()
        else:
            if st.button("⏸️ 停止背景音乐", use_container_width=True):
                st.session_state.music_status = "stopped"
                st.rerun()
        
        # 显示音乐播放器
        if st.session_state.music_status == "playing":
            st.audio(audio_file, format="audio/mp3", loop=True)
            st.success("音乐播放中")

# 在页面中调用

# 添加背景音乐播放器（隐藏的）
def render_background_music():
    """渲染背景音乐播放器"""
    if st.session_state.bg_music_enabled:
        # 使用HTML audio元素播放背景音乐
        audio_html = f"""
        <audio autoplay loop style="display:none;">
            <source src="永劫之春V3.mp3" type="audio/mp3">
            您的浏览器不支持音频元素。
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# 在页面加载时调用背景音乐功能
add_background_music()

st.markdown("""
<style>
.mj-titlebar {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1em;
    margin-bottom: 0.3em;
}
.mj-titles {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.mj-title {
    font-size: 2.1em;
    font-weight: bold;
    margin-bottom: 0.12em;
    line-height: 1.2;
}
.mj-subtitle {
    color: #888;
    font-size: 1.12em;
    margin-bottom: 0.2em;
    margin-top: 0.12em;
    font-weight: 500;
    letter-spacing: 0.02em;
}

/* 按钮风格 */
.mj-btnbox {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
}
.mj-btnbox button {
    font-size:1.08em;
    padding:0.48em 1.3em;
    border:1.4px solid #ddd;
    border-radius:6px;
    background-color:#fafbfc;
    color:#555;
    cursor:pointer;
    box-shadow:0 1px 2px rgba(0,0,0,0.02);
    transition:background 0.18s, border 0.18s;
}
.mj-btnbox button:hover {
    background:#f3f4f6;
    border-color:#bbb;
}
@media (prefers-color-scheme: dark) {
  .mj-btnbox button {
    background-color: #292929 !important;
    color: #f6f6f6 !important;
    border: 1.4px solid #444 !important;
  }
  .mj-btnbox button:hover {
    background-color: #333 !important;
    border-color: #888 !important;
  }
}
/* 移动端样式 */
@media (max-width: 600px) {
    .mj-titlebar {
        padding: 0 0.2em;
    }
    .mj-title { font-size: 1.25em; }
    .mj-subtitle { font-size: 1em; }
    .mj-btnbox button { font-size: 1em; padding: 0.40em 1em; }
}
@media (prefers-color-scheme: dark) {
  /* 顶部按钮样式已存在，这里仅针对所有 st.button 进行全局覆盖 */
  .stButton>button, .stButton button, div[class*="st-"] button, button[data-testid="baseButton-secondaryForm"] {
    background-color: #222 !important;
    color: #eee !important;
    border: 1.5px solid #444 !important;
    box-shadow: none !important;
    opacity: 1 !important;
    transition: background 0.15s, color 0.15s, border 0.15s;
  }
  .stButton>button:hover, .stButton button:hover, div[class*="st-"] button:hover, button[data-testid="baseButton-secondaryForm"]:hover {
    background-color: #333 !important;
    color: #fff !important;
    border-color: #aaa !important;
  }
  .stButton>button:active, .stButton button:active, div[class*="st-"] button:active, button[data-testid="baseButton-secondaryForm"]:active {
    background-color: #222 !important;
    color: #fff !important;
    border-color: #888 !important;
  }
  .stButton>button[disabled], .stButton button[disabled], div[class*="st-"] button[disabled], button[data-testid="baseButton-secondaryForm"][disabled] {
    background-color: #222 !important;
    color: #888 !important;
    border: 1.5px solid #444 !important;
    opacity: 1 !important;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mj-titlebar">
  <div class="mj-titles">
    <div class="mj-title">自然麻将</div>
    <div class="mj-subtitle">全斗番</div>
  </div>
  <div class="mj-btnbox">
    <a href="http://47.94.14.84:8531" target="_blank" style="text-decoration: none;">
      <button>算番器</button>
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

# 渲染背景音乐播放器
render_background_music()

BTN_HEIGHT = 48
BTN_WIDTH = 48

def img_to_base64(img_path):
    try:
        # 添加路径检查
        if not os.path.exists(img_path):
            st.error(f"❌ 图片文件不存在: {img_path}")
            st.info(f"当前工作目录: {os.getcwd()}")
            # 列出当前目录内容
            if os.path.exists("static"):
                st.info("static目录内容: " + str(os.listdir("static")))
                if os.path.exists("static/tiles"):
                    st.info("tiles目录内容: " + str(os.listdir("static/tiles")))
            return ""
        
        with open(img_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"❌ 图片加载失败: {str(e)}")
        return ""
def tile_img(idx):
    tile_name = tile_list[idx]
    return f"static/tiles/{tile_name}.png"

def tile_img_discard(idx, is_selfdrawgiri):
    tile_name = tile_list[idx]
    if is_selfdrawgiri:
        tile_name += "1"
    return f"static/tiles/{tile_name}.png"

def markDiscardedTileAsCalled(tile):
    lastPlayer = st.session_state['lastPlayer']
    if lastPlayer:
        for i in range(len(lastPlayer.discardPile)-1, -1, -1):
            if lastPlayer.discardPile[i][0] == tile:
                discard_tile, _ = lastPlayer.discardPile[i]
                lastPlayer.discardPile[i] = (discard_tile, [True, lastPlayer.discardPile[i][1][1]])
                break

st.markdown("""
    <style>
    form button[name="discard_btn"] {
        transition:background 0.1s;
    }
    form button[name="discard_btn"]:hover {
        background:#e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.stButton>button {
    min-width: 96px !important;
    min-height: 36px !important;
    font-size: 1.18em !important;
    border-radius: 6px !important;
    border: 1.5px solid #666 !important;
    background: #fff !important;
    padding: 0 12px !important;
}
</style>
""", unsafe_allow_html=True)

def show_hand_row_md_with_button(img_paths, enabled, riichi, player=None, player_idx=0):
    BTN_WIDTH = 48
    BTN_HEIGHT = 64
    cols = st.columns(len(img_paths), gap="small")

    # 判断哪个是摸上来的牌（尽量使用 already_drawn + need_sort_hand 约定）
    drawn_idx = None
    if player is not None and getattr(player, 'already_drawn', False) and not getattr(player, 'need_sort_hand', True):
        drawn_idx = len(player.hand) - 1

    for i, (col, img_path) in enumerate(zip(cols, img_paths)):
        with col:
            st.markdown('<div class="mj-discard-btn">', unsafe_allow_html=True)
            img_b64 = img_to_base64(img_path)
            st.markdown(
                f'<img src="data:image/png;base64,{img_b64}" width="{BTN_WIDTH}" height="{BTN_HEIGHT}" style="margin:0;display:block;"/>',
                unsafe_allow_html=True
            )
            # 正常可出牌且未立直：所有牌可出
            if enabled and not riichi:
                key = f"discard_p{player_idx}_{i}"
                if st.button("出", key=key):
                    st.session_state['pending_discard_idx'] = i
                    st.session_state['pending_discard_btn'] = True
                    st.rerun()
            # 立直状态：只允许出摸上的牌（若存在），其他牌显示为禁用按钮
            elif enabled and riichi:
                if drawn_idx is not None and i == drawn_idx:
                    key = f"discard_p{player_idx}_drawn"
                    if st.button("出", key=key):
                        st.session_state['pending_discard_idx'] = i
                        st.session_state['pending_discard_btn'] = True
                        st.rerun()
                else:
                    # 显示禁用按钮，防止误点并且保证 widget key 唯一
                    st.button("出", key=f"discard_disabled_p{player_idx}_{i}", disabled=True)
            # 不可出牌：什么都不做（只显示牌）
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
<style>
div[class*="st-key-discard_"] button {
    min-width: 36px !important;
    width: 36px !important;
    max-width: 36px !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    font-size: 1.08em !important;
}
</style>
""", unsafe_allow_html=True)
    
st.markdown("""
<style>
.stImage img,
.stImage > img,
.stImage img[class],
img[src*="static/tiles/"] {
    border-radius: 0 !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
    background: none !important;
}
</style>
""", unsafe_allow_html=True)

class Player:
    def __init__(self, name, ptype):
        self.hand = []
        self.melds = []
        self.discardPile = []
        self.firstTurn = True
        self.score = 0
        self.previousScore = 0
        self.type = ptype
        self.name = name
        self.seatWind = 0
        self.seatWindTile = 27
        self.win = False
        self.need_sort_hand = True
        self.win_score_added = False


def reset_game():
    if 'players' not in st.session_state or not st.session_state['players']:
        st.session_state['players'] = [
            Player('玩家', 'controlled'),
            Player('电脑1', 'comp'),
            Player('电脑2', 'comp'),
            Player('电脑3', 'comp')
        ]
    if 'main_seat_wind' in st.session_state:
        st.session_state['main_seat_wind'] = (st.session_state['main_seat_wind'] - 1) % 4
    else:
        st.session_state['main_seat_wind'] = random.randint(0, 3)
    if 'round_number' not in st.session_state:
        st.session_state['round_number'] = 1
    else:
        st.session_state['round_number'] += 1

    for idx, player in enumerate(st.session_state['players']):
        player.hand = []
        player.melds = []
        player.discardPile = []
        player.firstTurn = True
        player.win = False
        player.need_sort_hand = True
        player.seatWind = (st.session_state['main_seat_wind'] + idx) % 4
        player.seatWindTile = player.seatWind + 27
        player.win_score_added = False
        player.riichi=False
        player.furiten=False

    st.session_state['deck'] = [i for i in range(34)] * 4
    random.shuffle(st.session_state['deck'])
    st.session_state['currentTurn'] = 0
    st.session_state['lastTile'] = -1
    st.session_state['lastPlayer'] = None
    st.session_state['game_phase'] = 'draw'
    st.session_state['pending_action'] = None
    st.session_state['pending_action_player'] = None
    st.session_state['pending_action_options'] = None
    st.session_state['tingpai_info'] = ""
    st.session_state['liuju_flag'] = False
    st.session_state['pending_discard_idx'] = None
    st.session_state['pending_discard_btn'] = False
    st.session_state['win_way'] = None

    for i in range(12):
        st.session_state['players'][(-i)%4].hand += st.session_state['deck'][4*i:4*i+4]
    for i in range(4):
        st.session_state['players'][(-i)%4].hand.append(st.session_state['deck'][i+48])
    st.session_state['currentTurn'] = sum(len(p.hand) for p in st.session_state['players'])
    for p in st.session_state['players']:
        p.hand.sort()
        p.need_sort_hand = True

    dongjia_idx = None
    for idx, player in enumerate(st.session_state['players']):
        if player.seatWind == 0:
            dongjia_idx = idx
            break
    if dongjia_idx is not None:
        st.session_state['currentPlayerIndex'] = dongjia_idx
    else:
        st.session_state['currentPlayerIndex'] = 0

    for p in st.session_state['players']:
        p.already_drawn = False
        p.already_discard = False

def game_init():
    if 'players' not in st.session_state or not st.session_state['players']:
        st.session_state['players'] = [
            Player('玩家', 'controlled'),
            Player('电脑1', 'comp'),
            Player('电脑2', 'comp'),
            Player('电脑3', 'comp')
        ]
    reset_game()

if 'players' not in st.session_state:
    game_init()
players = st.session_state['players']

def can_draw():
    return st.session_state['currentTurn'] < len(st.session_state['deck'])

def draw(player):
    if not can_draw():
        st.session_state['game_phase'] = 'end'
        st.session_state['liuju_flag'] = True
        st.rerun()
        return False
    if getattr(player, 'already_drawn', False):
        return False
    player.hand.append(st.session_state['deck'][st.session_state['currentTurn']])
    st.session_state['currentTurn'] += 1
    player.need_sort_hand = False
    player.already_drawn = True
    if st.session_state['currentTurn'] == len(st.session_state['deck']):
        st.session_state['just_lastTile'] = True
    return True

# 优化算番缓存系统
@st.cache_data
def cached_analyze_13_tiles(hand_tuple, melds_tuple, seatWindTile, riichi=False):
    """缓存的13张牌状态分析 - 一次性计算所有状态"""
    hand = list(hand_tuple)
    melds = []
    for meld_data in melds_tuple:
        if len(meld_data) == 2:
            tiles, meld_type = meld_data
            melds.append([list(tiles), meld_type])
        else:
            melds.append(list(meld_data))
    
    # 一次性调用所有检测函数
    draw_result = fan_calcq.calcTFforDraw(hand, melds, seatWindTile, 0, riichi=16*int(riichi))
    semidraw_result = fan_calcq.calcTFforSemidraw(hand, melds, seatWindTile, 0)
    weak_semidraw_result = fan_calcq.calcTFforWeakSemidraw(hand, melds, seatWindTile, 0)
    
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

def update_tingpai_info(player):
    """优化的听牌信息更新 - 减少重复计算"""
    try:
        hand = player.hand[:]
        melds = player.melds[:]
        seatWindTile = player.seatWindTile

        # 一次性计算所有状态
        tingpais = fan_calcq.get_all_tingpais(hand, melds, seatWindTile, riichi=player.riichi)
        sf = fan_calcq.calcTFforSemidraw(hand, melds, seatWindTile, 0)
        wf = fan_calcq.calcTFforWeakSemidraw(hand, melds, seatWindTile, 0)

        # 计算分数
        tingpai_score = None
        semidraw_score = None
        weaksemidraw_score = None
        
        tingpai_str = ""
        semidraw_str = ""
        weaksemidraw_str = ""

        # 听牌处理
        if tingpais:
            max_ting = max(tingpais, key=lambda x: x[1])
            tingpai_score = 3 * max_ting[1] - 6
            
            # 获取番型名称
            res = fan_calcq.calc_fan_common_with_names(hand + [max_ting[0]], melds, seatWindTile, 16 * int(player.riichi))
            tingpai_names = res[1] if res else []
            name_str = "、".join(tingpai_names) if tingpai_names else ""
            
            tingpai_str = f"听牌 {name_str} {max_ting[1]}番 {tingpai_score}分".replace("  ", " ").strip()

        # 一向听处理
        if sf:
            semidraw_score = 2 * sf[4] - 4
            
            # 快速模拟听牌后的状态
            tmp_hand = hand.copy()
            tmp_melds = melds.copy()
            penult, typ, out_tile, tingpai = sf[0], sf[1], sf[2], sf[3]
            
            # 根据类型添加面子
            if typ == 0:  # 碰
                tmp_hand.remove(penult)
                tmp_hand.remove(penult)
                tmp_melds.append([[penult]*3, 0])
            elif typ == 1:  # 左吃
                tmp_hand.remove(penult-1)
                tmp_hand.remove(penult-2)
                tmp_melds.append([[penult-2, penult-1, penult], 2])
            elif typ == 2:  # 中吃
                tmp_hand.remove(penult-1)
                tmp_hand.remove(penult+1)
                tmp_melds.append([[penult-1, penult, penult+1], 1])
            elif typ == 3:  # 右吃
                tmp_hand.remove(penult+1)
                tmp_hand.remove(penult+2)
                tmp_melds.append([[penult, penult+1, penult+2], 0])
            
            tmp_hand.remove(out_tile)
            tmp_hand.append(tingpai)
            
            res = fan_calcq.calc_fan_common_with_names(tmp_hand, tmp_melds, seatWindTile, 0)
            semidraw_names = res[1] if res else []
            name_str = "、".join(semidraw_names) if semidraw_names else ""
            semidraw_str = f"一向听 {name_str} {sf[4]}番 {semidraw_score}分".replace("  ", " ").strip()

        # 弱一向听处理
        if wf:
            weaksemidraw_score = wf[4] - 2
            
            # 快速模拟弱一向听状态
            tmp_hand = hand.copy()
            tmp_melds = melds.copy()
            penult, typ, out_tile, tingpai = wf[0], wf[1], wf[2], wf[3]
            tmp_hand.append(penult)
            tmp_hand.remove(out_tile)
            tmp_hand.append(tingpai)
            
            res = fan_calcq.calc_fan_common_with_names(tmp_hand, tmp_melds, seatWindTile, 0)
            weaksemidraw_names = res[1] if res else []
            name_str = "、".join(weaksemidraw_names) if weaksemidraw_names else ""
            weaksemidraw_str = f"弱一向听 {name_str} {wf[4]}番 {weaksemidraw_score}分".replace("  ", " ").strip()

        # 选择最佳状态
        score_items = []
        if tingpai_score is not None and tingpai_score > 0:
            score_items.append((tingpai_score, tingpai_str))
        if semidraw_score is not None and semidraw_score > 0:
            score_items.append((semidraw_score, semidraw_str))
        if weaksemidraw_score is not None and weaksemidraw_score > 0:
            score_items.append((weaksemidraw_score, weaksemidraw_str))

        if score_items:
            best_score, best_str = max(score_items, key=lambda x: x[0])
            
            # 只为听牌添加详细列表
            if tingpais:
                tingpai_list_str = "听牌列表: " + "<br>".join(
                    f"{tile_list[w]}({v}番 和牌{4*v-8}分)" for w, v in tingpais
                )
                st.session_state['tingpai_info'] = best_str + "<br>" + tingpai_list_str
            else:
                st.session_state['tingpai_info'] = best_str
        else:
            st.session_state['tingpai_info'] = ""
            
    except Exception as e:
        st.session_state['tingpai_info'] = f"状态计算出错: {str(e)}"

def discard(player, idx):
    if getattr(player, 'already_discard', False):
        return
    if idx < 0 or idx >= len(player.hand):
        return
    tile = player.hand[idx]
    player.hand.pop(idx)
    is_selfdrawgiri = (idx == len(player.hand) and not player.need_sort_hand)
    st.session_state['lastTile'] = tile
    st.session_state['lastPlayer'] = player
    player.discardPile.append((tile, [False, is_selfdrawgiri]))
    player.need_sort_hand = True
    player.already_discard = True
    player.firstTurn = False
    if st.session_state['currentTurn'] == len(st.session_state['deck']):
        st.session_state['just_lastTile'] = True
    if player.need_sort_hand:
        player.hand.sort()
    if player.type == 'controlled':
        update_tingpai_info(player)
    if st.session_state.get('just_gang', False):
        st.session_state['just_gang'] = False
    return tile

def after_discard(last_tile, last_player_idx, offset=1):
    for p in players:
        p.already_drawn = False
        p.already_discard = False
    n = len(players)
    if offset > 3:
        st.session_state['currentPlayerIndex'] = (last_player_idx + 1) % n
        st.session_state['game_phase'] = 'draw'
        return
    i = (last_player_idx + offset) % n
    player = players[i]
    if player.type == "controlled":
        actions = []
        if check_win(player, last_tile):
            actions.append('win')
        if check_gang(player, last_tile):
            actions.append('gang')
        if check_peng(player, last_tile):
            actions.append('peng')
        if offset == 1:
            chiopts = get_chi_options(player, last_tile)
            if chiopts:
                actions.append(('chi', chiopts))
        if actions:
            st.session_state['pending_action'] = actions
            st.session_state['pending_action_player'] = i
            st.session_state['pending_action_tile'] = last_tile
            st.session_state['pending_action_offset'] = offset
            st.session_state['game_phase'] = 'wait'
            return
    st.session_state["pending_skip"] = {
        "tile": last_tile,
        "last_player_idx": last_player_idx,
        "offset": offset + 1
    }

def wait_for_action():
    actions = st.session_state.get('pending_action', None)
    pid = st.session_state.get('pending_action_player', None)
    offset = st.session_state.get('pending_action_offset', 1)
    if pid is None:
        return
    player = players[pid]
    tile = st.session_state.get('pending_action_tile', st.session_state.get('lastTile', -1))

    if not actions:
        st.session_state["pending_skip"] = {
            "tile": tile,
            "last_player_idx": (pid - offset + 4) % 4,
            "offset": offset + 1
        }
        return

    op_buttons = []
    op_fns = []
    op_keys = []
    for act in actions:
        if act == 'win' and not player.furiten:
            # 计算分数
            hand = player.hand[:] + [tile]
            melds = player.melds[:]
            seatWindTile = player.seatWindTile
            way = get_current_way(player, is_selfdraw=False)
            maxcomb = fan_calcq.calc_fan_common_with_names(hand, melds, seatWindTile, way)
            score_str = ""
            if maxcomb:
                score = 4 * maxcomb[3] - 8
                score_str = f" ({score}分)"
            op_buttons.append(f"和 {tile_list[tile]}{score_str}")
            def _win(player=player, tile=tile):
                if player.firstTurn:
                    st.session_state['just_first_turn'] = True
                else:
                    st.session_state['just_first_turn'] = False
                way = get_current_way(player, is_selfdraw=(player == players[0] and st.session_state["currentPlayerIndex"] == 0 and st.session_state['game_phase'] == 'action'))
                if st.session_state.get('just_gang', False):
                    st.session_state['just_gang'] = False
                if st.session_state.get('just_lastTile', False):
                    st.session_state['just_lastTile'] = False
                if st.session_state.get('just_first_turn', False):
                    st.session_state['just_first_turn'] = False
                perform_win(player, tile, way)
                for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
                    st.session_state[k] = None
                st.session_state['game_phase'] = 'end'
                st.rerun()
            op_fns.append(_win)
            op_keys.append("win")
        elif act == 'gang' and not player.riichi:
            op_buttons.append(f"杠 {tile_list[tile]}")
            def _gang(player=player, tile=tile):
                perform_gang(player, tile)
                for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
                    st.session_state[k] = None
                st.session_state['game_phase'] = 'action'
                st.session_state['currentPlayerIndex'] = pid
                st.rerun()
            op_fns.append(_gang)
            op_keys.append("gang")
        elif act == 'peng' and not player.riichi:
            op_buttons.append(f"碰 {tile_list[tile]}")
            def _peng(player=player, tile=tile):
                perform_peng(player, tile)
                for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
                    st.session_state[k] = None
                st.session_state['game_phase'] = 'action'
                st.session_state['currentPlayerIndex'] = pid
                st.rerun()
            op_fns.append(_peng)
            op_keys.append("peng")
        elif isinstance(act, tuple) and act[0] == 'chi' and not player.riichi:
            chiopts = act[1]
            for idx, meld in enumerate(chiopts):
                op_buttons.append(f"吃 {' '.join(tile_list[x] for x in meld)}")
                def _chi(player=player, meld=meld):
                    perform_chi(player, meld)
                    for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
                        st.session_state[k] = None
                    st.session_state['game_phase'] = 'action'
                    st.session_state['currentPlayerIndex'] = pid
                    st.rerun()
                op_fns.append(_chi)
                op_keys.append(f"chi_{idx}")

    if op_buttons:
        op_buttons.append("跳过")
        def _skip():
            # 仅当玩家此时有“和”选项且已立直时，把该玩家标记为振听（furiten）
            # 这样保证立直前的放弃不会引入振听
            if 'win' in actions and player.riichi:
                players[pid].furiten = True
            for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
                st.session_state[k] = None
            st.session_state["pending_skip"] = {
                "tile": tile,
                "last_player_idx": (pid - offset + 4) % 4,
                "offset": offset + 1
            }
            st.rerun()
        op_fns.append(_skip)
        op_keys.append("skip")
        cols = st.columns(len(op_buttons))
        for i, (btxt, bfn, bkey) in enumerate(zip(op_buttons, op_fns, op_keys)):
            # 生成一个在当前上下文中稳定且唯一的 key
            current_player_idx = st.session_state.get('currentPlayerIndex', 0)
            unique_key = f"{bkey}_p{current_player_idx}_i{i}"
            if cols[i].button(btxt, key=unique_key):
                bfn()
        st.markdown("#### 手牌")
        if player.hand:
            img_paths = [tile_img_discard(t, True) for t in player.hand]
            # 给出当前等待操作玩家的手牌（禁用/只读），传入 player 与其索引以便立直时正确限制出牌
            show_hand_row_md_with_button(img_paths, False, player.riichi, player, pid)
    else:
        for k in ["pending_action","pending_action_player","pending_action_tile","pending_action_offset"]:
            st.session_state[k] = None
        st.session_state["pending_skip"] = {
            "tile": tile,
            "last_player_idx": (pid - offset + 4) % 4,
            "offset": offset + 1
        }
        st.rerun()

def show_melds(player):
    if player.melds:
        melds_html = '<div style="display:flex;align-items:center;">'
        for meld in player.melds:
            meld_imgs = ''
            tiles, meld_type = meld[0], meld[1]
            if len(tiles) == 4 and meld_type == 6:
                back_img = "static/tiles/back.png"
                img_b64_back = img_to_base64(back_img)
                img_b64_mid = img_to_base64(tile_img(tiles[0]))
                meld_imgs += f'<img src="data:image/png;base64,{img_b64_back}" width="32" style="margin-right:0px;"/>'
                meld_imgs += f'<img src="data:image/png;base64,{img_b64_mid}" width="32" style="margin-right:0px;"/>'
                meld_imgs += f'<img src="data:image/png;base64,{img_b64_mid}" width="32" style="margin-right:0px;"/>'
                meld_imgs += f'<img src="data:image/png;base64,{img_b64_back}" width="32" style="margin-right:0px;"/>'
            else:
                for tidx in tiles:
                    img_path = tile_img(tidx)
                    try:
                        img_b64 = img_to_base64(img_path)
                        meld_imgs += f'<img src="data:image/png;base64,{img_b64}" width="32" style="margin-right:0px;"/>'
                    except Exception:
                        meld_imgs += '<span style="color:red;">[无图片]</span>'
            melds_html += f'<div class="mj-meld">{meld_imgs}</div>'
        melds_html += '</div>'
        st.markdown(melds_html, unsafe_allow_html=True)

def show_discards(player):
    tiles = player.discardPile
    if not tiles:
        st.write("无")
        return
    img_paths = []
    for tile, (was_called, is_selfdrawgiri) in tiles:
        if was_called:
            continue
        img_paths.append(tile_img_discard(tile, is_selfdrawgiri))
    if img_paths:
        st.image(img_paths, width=24)

def show_player_waits():
    tingpai_info = st.session_state.get('tingpai_info', '')
    
    if tingpai_info:
        info = tingpai_info.replace('\n', '<br>')
        st.markdown(f"""<div style="background-color:#eaf2fb;padding:0.4em 0.8em;border-radius:6px;color:#2673b8">{info}</div>""", unsafe_allow_html=True)
    # 如果没有信息，什么都不渲染，Streamlit会自动清空这个区域

    # 显示振听状态（针对本地玩家 players[0]），在听牌信息下方以红色强调
    try:
        player = players[0]
        if getattr(player, 'furiten', False):
            st.markdown(
                '<div style="color:#c0392b;font-weight:700;margin-top:0.4em;">振听 — 已放弃荣和（本局只能通过自摸和牌）</div>',
                unsafe_allow_html=True
            )
    except Exception:
        # 若 players 未就绪则静默跳过
        pass

def get_chi_options(player, lastTile):
    options = []
    if lastTile >= 2 and lastTile < 27 and lastTile - 1 in player.hand and lastTile - 2 in player.hand and lastTile // 9 == (lastTile - 1) // 9 == (lastTile - 2) // 9:
        options.append([lastTile - 2, lastTile - 1, lastTile])
    if lastTile >= 1 and lastTile < 26 and lastTile - 1 in player.hand and lastTile + 1 in player.hand and lastTile // 9 == (lastTile - 1) // 9 == (lastTile + 1) // 9:
        options.append([lastTile - 1, lastTile, lastTile + 1])
    if lastTile < 25 and lastTile < 27 and lastTile + 1 in player.hand and lastTile + 2 in player.hand and lastTile // 9 == (lastTile + 1) // 9 == (lastTile + 2) // 9:
        options.append([lastTile, lastTile + 1, lastTile + 2])
    return options

def check_peng(player, lastTile):
    return player.hand.count(lastTile) >= 2

def check_gang(player, lastTile):
    return player.hand.count(lastTile) >= 3

def check_concealed_gang(player):
    c = Counter(player.hand)
    return [t for t in c if c[t] == 4]

def check_add_gang(player):
    add_gang = []
    for meld in player.melds:
        if len(meld[0]) == 3 and meld[0][0] == meld[0][1] and meld[0][1] == meld[0][2]:
            if player.hand.count(meld[0][0]) > 0:
                add_gang.append(meld[0][0])
    return add_gang

def get_current_way(player, is_selfdraw=False):
    way = 0
    if is_selfdraw:
        way += 1
    if st.session_state.get('just_gang', False):
        way += 2
    if st.session_state.get('just_lastTile', False):
        way += 4
    if player.firstTurn:
        way += 8
    if player.riichi:
        way+=16
    if player.furiten:
        way+=32
    return way

def check_win(player, lastTile):
    # 区分“被别人打出和牌（ron）”和“自摸（tsumo）”。
    # 如果 player.furiten，则不能在别人打出的牌上荣和（只能自摸）。
    way_win_on_discard = get_current_way(player, is_selfdraw=False)
    hand_win_on_discard = player.hand[:] + [lastTile]
    melds = player.melds[:]
    seatWindTile = player.seatWindTile
    maxcomb_win_on_discard = fan_calcq.calc_fan_common_with_names(hand_win_on_discard, melds, seatWindTile, way_win_on_discard)

    # 自摸情况（始终允许）
    way_selfdraw = get_current_way(player, is_selfdraw=True)
    hand_selfdraw = player.hand[:]
    maxcomb_selfdraw = fan_calcq.calc_fan_common_with_names(hand_selfdraw, melds, seatWindTile, way_selfdraw)

    # 只有当玩家不是振听时才允许别人打出的牌上荣和
    if not getattr(player, 'furiten', False):
        if maxcomb_win_on_discard and maxcomb_win_on_discard[3] >= 3:
            return True
    # 自摸仍然允许（振听反和由番表判定）
    if maxcomb_selfdraw and maxcomb_selfdraw[3] >= 3:
        return True
    return False

def can_selfdraw(player):
    way = get_current_way(player, is_selfdraw=True)
    hand = player.hand[:]
    melds = player.melds[:]
    seatWindTile = player.seatWindTile
    maxcomb = fan_calcq.calc_fan_common_with_names(hand, melds, seatWindTile, way)
    return maxcomb and maxcomb[3] >= 3

def can_win_on_discard(player, tile):
    way = get_current_way(player, is_selfdraw=False)
    hand = player.hand[:] + [tile]
    melds = player.melds[:]
    seatWindTile = player.seatWindTile
    maxcomb = fan_calcq.calc_fan_common_with_names(hand, melds, seatWindTile, way)
    return maxcomb and maxcomb[3] >= 3

def perform_win(player, lastTile, way=0):
    if way & 1 == 0:
        player.hand.append(lastTile)
    st.success(f"{player.name} 和牌！")
    player.win = True
    st.session_state['win_way'] = way
    if not player.win_score_added:
        maxcomb = fan_calcq.calc_fan_common_with_names(player.hand, player.melds, player.seatWindTile, way)
        if maxcomb:
            fan_names, fan_values, fan_score = maxcomb[1], maxcomb[2], maxcomb[3]
            remain = len(st.session_state['deck']) - st.session_state['currentTurn']
            if remain >= 10:
                extra = remain // 10
                fan_names.append(f"余牌{remain}")
                fan_values.append(extra)
                fan_score += extra
            hupai_str = f"和牌：{tile_list[lastTile]}"
            fan_names_str = "<br>".join(f"- {n}({v}番)" for n, v in zip(fan_names, fan_values)) if fan_names else "无"
            st.markdown(
                f"{player.name}的状态: 和牌<br>"
                f"{hupai_str}<br>"
                f"番数：{fan_score}番<br>"
                f"番种：<br>{fan_names_str}<br>"
                f"得分：{4*fan_score-8}分",
                unsafe_allow_html=True
            )
            player.score += (4*fan_score-8)
        else:
            st.warning("未能识别番型")
        player.win_score_added = True
    if way & 1 == 0:
        player.hand.remove(lastTile)
        player.hand.sort()

def perform_peng(player, lastTile):
    for _ in range(2):
        player.hand.remove(lastTile)
    player.melds.append([[lastTile, lastTile, lastTile], 0])
    markDiscardedTileAsCalled(lastTile)
    player.hand.sort()
    # 更新听牌信息（碰后需要刷新听牌显示）
    if player.type == 'controlled':
        update_tingpai_info(player)

def perform_gang(player, lastTile):
    for _ in range(3):
        player.hand.remove(lastTile)
    player.melds.append([[lastTile, lastTile, lastTile, lastTile], 0])
    markDiscardedTileAsCalled(lastTile)
    player.hand.sort()
    st.session_state['just_gang'] = True
    if player.type == 'controlled':
        update_tingpai_info(player)
    draw(player)
    st.session_state['game_phase'] = 'action'
    player.already_drawn = True
    player.already_discard = False


def perform_chi(player, meld):
    for tile in meld:
        if tile != st.session_state['lastTile'] and tile in player.hand:
            player.hand.remove(tile)
    player.melds.append([meld, meld.index(st.session_state['lastTile'])])
    markDiscardedTileAsCalled(st.session_state['lastTile'])
    player.hand.sort()
    # 吃牌后也更新听牌信息
    if player.type == 'controlled':
        update_tingpai_info(player)

def check_concealed_gang_and_add_gang(player):
    concealed = check_concealed_gang(player)
    add = check_add_gang(player)
    return concealed, add
def check_riichi(player):
    lis=[]
    for i in range (len(player.hand)):
        # 使用索引移除以构造去掉一张牌后的手牌进行检测
        ply = player.hand[:]
        try:
            del ply[i]
        except Exception:
            continue
        # 用删除后的手牌检测是否满足立直条件
        if fan_calcq.checkDraw(ply):
            lis.append(player.hand[i])
    return lis

def hand_no_overflow(hand, melds):
    c = Counter(hand)
    for meld in melds:
        for t in meld[0]:
            c[t] += 1
    return all(v <= 4 for v in c.values())

def display_table_and_player():
    if 'round_number' not in st.session_state:
        st.session_state['round_number'] = 1
    my_idx = 0
    n = len(players)
    seat_wind_map = ["东", "南", "西", "北"]
    p = players[my_idx]
    left_tiles = len(st.session_state['deck']) - st.session_state['currentTurn']
    st.write(f"当前第 {st.session_state['round_number']} 局 ｜ 你的门风：{seat_wind_map[p.seatWind]} ｜ 剩余牌数：{left_tiles} ｜ 你的分数: {p.score}")
    cols = st.columns(3)
    seat_names = ["上家", "对家", "下家"]
    pid_map = [ (my_idx - 1) % n, (my_idx + 2) % n, (my_idx + 1) % n ]
    for i, cname in enumerate(seat_names):
        pid = pid_map[i]
        player = players[pid]
        with cols[i]:
            st.write(f"{cname}（{player.name}）")
            show_discards(player)
    show_discards(p)
    show_melds(p)
    show_player_waits()

if st.session_state.get("pending_discard_btn", False):
    idx = st.session_state.get("pending_discard_idx", None)
    cur_idx = st.session_state["currentPlayerIndex"]
    player = players[cur_idx]
    if player.type == "controlled" and st.session_state["game_phase"] == "action" and idx is not None:
        discard(player, idx)
        after_discard(st.session_state['lastTile'], cur_idx)
        st.session_state['pending_discard_idx'] = None
        st.session_state['pending_discard_btn'] = False
        st.rerun()

def controlled_turn_imgs():
    player = players[0]
    op_buttons = []
    op_keys = []
    op_fns = []

    concealed_gangs, add_gangs = check_concealed_gang_and_add_gang(player)
    canriichi=check_riichi(player)
    for t in concealed_gangs:
        op_buttons.append(f"暗杠 {tile_list[t]}")
        op_keys.append(f"concealed_gang_{t}")
        def _concealed_gang(t=t):
            [player.hand.remove(t) for _ in range(4)]
            player.melds.append([[t]*4, 6])
            player.already_drawn = False
            st.session_state['just_gang'] = True
            if player.type == 'controlled':
                update_tingpai_info(player)
            draw(player)
            st.session_state['game_phase'] = 'action'
            player.already_drawn = True
            player.already_discard = False
            st.rerun()
        op_fns.append(_concealed_gang)
    for t in add_gangs:
        op_buttons.append(f"加杠 {tile_list[t]}")
        op_keys.append(f"add_gang_{t}")
        def _addgang(t=t):
            player.hand.remove(t)
            for meld in player.melds:
                if len(meld[0]) == 3 and meld[0][0] == t:
                    meld[0].append(t)
                    meld[1] += 3
                    break
            player.already_drawn = False
            st.session_state['just_gang'] = True
            if player.type == 'controlled':
                update_tingpai_info(player)
            draw(player)
            st.session_state['game_phase'] = 'action'
            player.already_drawn = True
            player.already_discard = False
            st.rerun()
        op_fns.append(_addgang)
    if not player.riichi:
        for t in canriichi:
            op_buttons.append(f"立直{tile_list[t]}")
            op_keys.append(f"riichi_{t}")
            def _riichi(t=t):
                # 把选择的牌正常弃出（使用 discard 保持一致的状态更新）
                try:
                    idx = player.hand.index(t)
                except ValueError:
                    return
                # 使用已有的 discard() 来处理弃牌、lastTile/lastPlayer/flag 等
                discarded_tile = discard(player, idx)
                if discarded_tile is None:
                    return
                # 标记为立直（在弃牌后设置）
                player.riichi = True
                # 更新听牌信息
                update_tingpai_info(player)
                # 触发其他玩家对该弃牌的判定（碰/吃/杠/和）
                # currentPlayerIndex 是出牌者索引（通常为0）
                last_player_idx = st.session_state.get('currentPlayerIndex', 0)
                after_discard(st.session_state.get('lastTile', -1), last_player_idx)
                # 清理任何 pending_discard 的临时标记
                st.session_state['pending_discard_idx'] = None
                st.session_state['pending_discard_btn'] = False
                # 切到等待响应的阶段，等待其他玩家操作
                st.session_state['game_phase'] = 'wait'
                st.rerun()
            op_fns.append(_riichi)

    if st.session_state['game_phase'] == 'action' and can_selfdraw(player):
        hand = player.hand[:]
        melds = player.melds[:]
        seatWindTile = player.seatWindTile
        way = get_current_way(player, is_selfdraw=True)
        maxcomb = fan_calcq.calc_fan_common_with_names(hand, melds, seatWindTile, way)
        score_str = ""
        if maxcomb:
            score = 4 * maxcomb[3] - 8
            score_str = f" ({score}分)"
        op_buttons.append(f"自摸和牌{score_str}")
        op_keys.append("selfdraw")
        def _selfdraw():
            if player.firstTurn:
                st.session_state['just_first_turn'] = True
            else:
                st.session_state['just_first_turn'] = False
            way = get_current_way(player, is_selfdraw=True)
            if st.session_state.get('just_gang', False):
                st.session_state['just_gang'] = False
            if st.session_state.get('just_lastTile', False):
                st.session_state['just_lastTile'] = False
            if st.session_state.get('just_first_turn', False):
                st.session_state['just_first_turn'] = False
            perform_win(player, player.hand[-1], way)
            st.session_state['game_phase'] = 'end'
            st.rerun()
        op_fns.append(_selfdraw)

    if op_buttons:
        cols = st.columns(len(op_buttons))
        for i, (btxt, bkey, bfn) in enumerate(zip(op_buttons, op_keys, op_fns)):
            # 生成一个在当前上下文中稳定且唯一的 key
            current_player_idx = st.session_state.get('currentPlayerIndex', 0)
            unique_key = f"{bkey}_p{current_player_idx}_i{i}"
            if cols[i].button(btxt, key=unique_key):
                bfn()

    if st.session_state['game_phase'] == 'draw':
        if not getattr(player, 'already_drawn', False):
            if draw(player):
                if 'gang_flag' in st.session_state and st.session_state['gang_flag']:
                    st.session_state['just_gang'] = True
                    st.session_state['gang_flag'] = False
                if st.session_state['currentTurn'] == len(st.session_state['deck']):
                    st.session_state['just_lastTile'] = True
                st.session_state['game_phase'] = 'action'
                st.rerun()
        return

    st.markdown("#### 手牌")
    if st.session_state['game_phase'] == 'action':
        img_paths = [tile_img(t) for t in player.hand]
        # 受控玩家 (index 0) 可操作手牌；立直时只可摸打最后一张牌
        show_hand_row_md_with_button(img_paths, True, player.riichi, player, 0)
    else:
        img_paths = [tile_img_discard(t, True) for t in player.hand]
        show_hand_row_md_with_button(img_paths, False, player.riichi, player, 0)

def comp_discard(player):
    return len(player.hand) - 1

def comp_turn_imgs():
    idx = st.session_state['currentPlayerIndex']
    if idx == 0:
        return
    player = players[idx]
    if st.session_state['game_phase'] == 'draw':
        if not can_draw():
            st.session_state['game_phase'] = 'end'
            st.session_state['liuju_flag'] = True
            st.rerun()
            return
        if not getattr(player, 'already_drawn', False):
            if draw(player):
                if st.session_state['currentTurn'] == len(st.session_state['deck']):
                    st.session_state['just_lastTile'] = True
                st.session_state['game_phase'] = 'action'
                st.rerun()
    elif st.session_state['game_phase'] == 'action':
        if not getattr(player, 'already_discard', False):
            tile_idx = comp_discard(player)
            discard(player, tile_idx)
            after_discard(st.session_state['lastTile'], idx)
            st.rerun()

# 优化的游戏结束计算 - 参考算番器的get_semidraw_detail函数
def get_detailed_fan_result(hand, melds, seatWindTile, result_data, status):
    """获取详细的番型信息"""
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
            res = fan_calcq.calc_fan_common_with_names(finalHand, finalMelds, seatWindTile, 0)
            if res:
                return res[1], res[2], res[3]  # fan_names, fan_values, fan_score
        
        elif status == "弱一向听":
            # 模拟弱一向听的完整流程
            finalHand = hand[:]
            finalMelds = melds[:]
            finalHand.append(result_data[0])
            finalHand.remove(result_data[2])
            drawWait = finalHand[:]
            finalHand.append(result_data[3])
            
            res = fan_calcq.calc_fan_common_with_names(finalHand, finalMelds, seatWindTile, 0)
            if res:
                return res[1], res[2], res[3]  # fan_names, fan_values, fan_score
        
        return [], [], 0
    except:
        return [], [], 0

def endGameCalculations(player):
    """优化的游戏结束计算"""
    if player.type == 'comp':
        return

    if player.win:
        # 无论是否已加分，都要显示详细和牌信息
        way = st.session_state.get('win_way', 0)
        if way & 1 == 0:  # 荣和
            hupai_tile = st.session_state.get('lastTile', -1)
            hand = player.hand[:] + [hupai_tile]
        else:  # 自摸
            hand = player.hand[:]
            hupai_tile = hand[-1] if hand else -1
        
        if hand_no_overflow(hand, player.melds):
            maxcomb = fan_calcq.calc_fan_common_with_names(hand, player.melds, player.seatWindTile, way)
            if maxcomb:
                fan_names, fan_values, fan_score = maxcomb[1], maxcomb[2], maxcomb[3]
                
                # 添加余牌奖励
                remain = len(st.session_state['deck']) - st.session_state['currentTurn']
                if remain >= 10:
                    extra = remain // 10
                    fan_names.append(f"余牌{remain}")
                    fan_values.append(extra)
                    fan_score += extra
                
                # 构建显示信息
                hupai_str = f"和牌：{tile_list[hupai_tile]}" if hupai_tile >= 0 else "和牌"
                fan_names_str = "<br>".join(f"• {n} ({v}番)" for n, v in zip(fan_names, fan_values))
                final_score = 4 * fan_score - 8
                
                st.markdown(
                    f"**{player.name} 状态:** 和牌<br>"
                    f"**{hupai_str}**<br>"
                    f"**番数：** {fan_score}番<br>"
                    f"**番种：**<br>{fan_names_str}<br>"
                    f"**当局得分：** {final_score}分",
                    unsafe_allow_html=True
                )
                
                # 只在未加分时才加分
                if not player.win_score_added:
                    player.score += final_score
                    player.win_score_added = True
            else:
                st.info(f"{player.name}的状态: 和牌，未能识别番型")
        else:
            st.info(f"{player.name}的状态: 和牌 牌张数超限，未能识别番型")
        
        st.write(f"📈 **{player.name} 总分: {player.score}**")
        return

    # 未和牌玩家的处理
    try:
        hand_tuple = tuple(player.hand)
        melds_tuple = tuple(tuple(meld) if isinstance(meld, list) else meld for meld in player.melds)
        
        # 使用缓存的统一分析函数
        status, score, result_data = cached_analyze_13_tiles(hand_tuple, melds_tuple, player.seatWindTile, riichi=player.riichi)
        
        if status == "听牌" and result_data and score > 0:
            tingpai = result_data[0]
            hand = player.hand + [tingpai]
            
            if hand_no_overflow(hand, player.melds):
                # 直接使用fan_calc的函数获取番型信息
                comb = fan_calcq.calc_fan_common_with_names(hand, player.melds, player.seatWindTile, 16 * player.riichi)
                if comb:
                    fan_names, fan_values, fan_score = comb[1], comb[2], comb[3]
                    fan_names_str = "<br>".join(f"• {n} ({v}番)" for n, v in zip(fan_names, fan_values))
                    
                    st.markdown(
                        f"**{player.name} 状态:** 听牌<br>"
                        f"**高目：** {tile_list[tingpai]}<br>"
                        f"**番数：** {fan_score}番<br>"
                        f"**番种：**<br>{fan_names_str}<br>"
                        f"**当局得分：** {score}分",
                        unsafe_allow_html=True
                    )
                else:
                    st.info(f"{player.name}的状态: 听牌，高目：{tile_list[tingpai]}，未能识别番型，当局得分：{score}分")
                
                # 只在未加分时才加分
                if not player.win_score_added:
                    player.score += score
            else:
                st.info(f"{player.name}的状态: 听牌 牌张数超限，不计分")
                
        elif status == "一向听" and result_data and score > 0:
            penult, typ, out_tile, tingpai = result_data[0], result_data[1], result_data[2], result_data[3]
            
            # 使用优化的详细计算函数
            fan_names, fan_values, fan_score = get_detailed_fan_result(player.hand, player.melds, player.seatWindTile, result_data, status)
            
            if fan_names:
                fan_names_str = "<br>".join(f"• {n} ({v}番)" for n, v in zip(fan_names, fan_values))
                st.markdown(
                    f"**{player.name} 状态:** 一向听<br>"
                    f"**高目：** +{tile_list[penult]} -{tile_list[out_tile]} +{tile_list[tingpai]}<br>"
                    f"**番数：** {fan_score}番<br>"
                    f"**番种：**<br>{fan_names_str}<br>"
                    f"**当局得分：** {score}分",
                    unsafe_allow_html=True
                )
            else:
                st.info(f"{player.name}的状态: 一向听，高目：+{tile_list[penult]} -{tile_list[out_tile]} +{tile_list[tingpai]}，未能识别番型，当局得分：{score}分")
            
            # 只在未加分时才加分
            if not player.win_score_added:
                player.score += score
                
        elif status == "弱一向听" and result_data and score > 0:
            penult, typ, out_tile, tingpai = result_data[0], result_data[1], result_data[2], result_data[3]
            
            # 使用优化的详细计算函数
            fan_names, fan_values, fan_score = get_detailed_fan_result(player.hand, player.melds, player.seatWindTile, result_data, status)
            
            if fan_names:
                fan_names_str = "<br>".join(f"• {n} ({v}番)" for n, v in zip(fan_names, fan_values))
                st.markdown(
                    f"**{player.name} 状态:** 弱一向听<br>"
                    f"**高目：** d{tile_list[penult]} -{tile_list[out_tile]} +{tile_list[tingpai]}<br>"
                    f"**番数：** {fan_score}番<br>"
                    f"**番种：**<br>{fan_names_str}<br>"
                    f"**当局得分：** {score}分",
                    unsafe_allow_html=True
                )
            else:
                st.info(f"{player.name}的状态: 弱一向听，高目：d{tile_list[penult]} -{tile_list[out_tile]} +{tile_list[tingpai]}，未能识别番型，当局得分：{score}分")
            
            # 只在未加分时才加分
            if not player.win_score_added:
                player.score += score
        else:
            st.info(f"{player.name}的状态: 未成牌")
        
        # 标记已处理
        if not player.win_score_added:
            player.win_score_added = True
            
    except Exception as e:
        st.error(f"计算 {player.name} 状态时出错: {str(e)}")
        st.info(f"{player.name}的状态: 计算错误")
        
    st.write(f"📈 **{player.name} 总分: {player.score}**")

# 游戏主流程和界面
display_table_and_player()

if st.session_state.get("pending_skip"):
    skip = st.session_state["pending_skip"]
    st.session_state["pending_skip"] = None
    after_discard(skip["tile"], skip["last_player_idx"], skip["offset"])
    st.rerun()

if (
    st.session_state.get('game_phase') == 'end'
    or st.session_state.get('liuju_flag', False)
):
    st.write("游戏结束！")
    p = players[0]
    img_urls = [tile_img(t) for t in p.hand]
    show_hand_row_md_with_button(img_urls, False, p.riichi, p, 0)
    for p in players:
        endGameCalculations(p)
    st.session_state['tingpai_info'] = ""
    if st.button("重新开始"):
        for key in ['liuju_flag', 'pending_action', 'pending_action_player', 'pending_action_tile', 'pending_action_offset',
                    'win_way', 'win_flag', 'game_phase', 'pending_discard_idx', 'pending_discard_btn', 'just_lastTile', 'just_gang', 'just_first_turn']:
            if key in st.session_state:
                del st.session_state[key]
        reset_game()
        st.rerun()
    st.stop()

if st.session_state['game_phase'] == 'wait' and st.session_state.get('pending_action'):
    wait_for_action()
elif st.session_state['game_phase'] == 'wait':
    if st.session_state['currentPlayerIndex'] == 0:
        controlled_turn_imgs()
    else:
        comp_turn_imgs()
elif st.session_state['currentPlayerIndex'] == 0:
    controlled_turn_imgs()
else:
    comp_turn_imgs()