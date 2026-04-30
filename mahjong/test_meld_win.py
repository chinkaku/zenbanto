"""
测试修复：鸣牌后能否和牌
"""

from 框架 import *

def test_melded_win():
    """测试鸣牌后能否和牌"""
    
    print("="*60)
    print("测试：鸣牌后能否和牌")
    print("="*60)
    
    # 构造一个和牌局面
    # 副露：一个碰（3张2万）+ 一个吃（1-2-3万）= 2个面子
    # 手牌：还需2个面子 + 1个对子 = 8张牌
    
    hand = [
        Tile(TileType.MAN, 4), Tile(TileType.MAN, 5), Tile(TileType.MAN, 6),  # 顺子
        Tile(TileType.PIN, 4), Tile(TileType.PIN, 4), Tile(TileType.PIN, 4),  # 刻子
        Tile(TileType.SOU, 1), Tile(TileType.SOU, 1),  # 对子
    ]
    
    melds = [
        MeldSet([Tile(TileType.MAN, 2), Tile(TileType.MAN, 2), Tile(TileType.MAN, 2)], 'PUNG'),  # 碰
        MeldSet([Tile(TileType.MAN, 1), Tile(TileType.MAN, 2), Tile(TileType.MAN, 3)], 'CHOW'),  # 吃
    ]
    
    print(f"\n手牌({len(hand)}张)：{' '.join(str(t) for t in hand)}")
    print(f"副露({len(melds)}个面子)：")
    for i, meld in enumerate(melds, 1):
        print(f"  {i}. {' '.join(str(t) for t in meld.tiles)} ({meld.meld_type})")
    
    total = len(hand) + sum(len(m.tiles) for m in melds)
    print(f"\n总牌数：{total}张")
    
    is_win, win_type = is_winning_hand(hand, melds)
    
    if is_win:
        print(f"✓ 和牌成功！类型：{win_type}")
    else:
        print(f"✗ 和牌失败")
    
    print("\n" + "="*60)
    print("\n测试2：只有手牌的标准和牌（无副露）")
    print("="*60)
    
    hand2 = [
        Tile(TileType.MAN, 1), Tile(TileType.MAN, 2), Tile(TileType.MAN, 3),
        Tile(TileType.MAN, 1), Tile(TileType.MAN, 2), Tile(TileType.MAN, 3),
        Tile(TileType.PIN, 1), Tile(TileType.PIN, 1), Tile(TileType.PIN, 1),
        Tile(TileType.SOU, 1), Tile(TileType.SOU, 1), Tile(TileType.SOU, 1),
        Tile(TileType.SOU, 5), Tile(TileType.SOU, 5),
    ]
    
    print(f"\n手牌({len(hand2)}张)：{' '.join(str(t) for t in hand2)}")
    is_win2, win_type2 = is_winning_hand(hand2, [])
    
    if is_win2:
        print(f"✓ 和牌成功！类型：{win_type2}")
    else:
        print(f"✗ 和牌失败")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_melded_win()
