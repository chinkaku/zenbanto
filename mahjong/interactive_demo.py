#!/usr/bin/env python3
"""
真实交互演示：展示一个完整的出牌流程
"""

from 框架 import *

def interactive_demo():
    """交互式演示一个回合"""
    game = Game()
    game.initialize_game()
    game.start_round()
    
    player = game.players[0]  # 东家（人类）
    
    print("\n" + "="*60)
    print("真实交互演示：出牌流程")
    print("="*60)
    
    # 演示当前手牌
    sorted_hand = sorted(player.hand, key=lambda t: (t.tile_type.value, t.rank))
    hand_shorthands = [tile.to_shorthand() for tile in sorted_hand]
    
    print(f"\n【您的手牌】({len(player.hand)}张):")
    print(f"  {' '.join(hand_shorthands)}\n")
    
    # 让用户选择一张牌打出
    print("现在请选择要打出的牌。\n示例输入：")
    for i in range(min(5, len(hand_shorthands))):
        print(f"  - 输入 '{hand_shorthands[i]}' 打出第{i+1}张牌")
    
    print("\n" + "-"*60)
    choice = input("请输入要打出的牌的简称: ").strip().upper()
    
    if choice in hand_shorthands:
        idx = hand_shorthands.index(choice)
        tile = sorted_hand[idx]
        print(f"\n✓ 您成功打出：{tile}（{choice}）")
        player.discard_tile(tile)
        game.discard_pool.append(tile)
        
        print(f"\n【打牌后手牌】({len(player.hand)}张):")
        sorted_hand = sorted(player.hand, key=lambda t: (t.tile_type.value, t.rank))
        hand_shorthands = [tile.to_shorthand() for tile in sorted_hand]
        print(f"  {' '.join(hand_shorthands)}")
        
        print(f"\n【牌河】")
        print(f"  已打出：{tile}（{choice}）")
    else:
        print(f"\n✗ 错误：'{choice}' 不在你的手牌中")
        print(f"有效的简称为：{' '.join(hand_shorthands)}")
    
    print("\n" + "="*60)
    print("演示完成！现在你可以运行 'python 框架.py' 进行完整游戏。")
    print("="*60 + "\n")

if __name__ == "__main__":
    interactive_demo()
