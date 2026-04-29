"""
手动演示框架的新功能：简称和横向显示
"""

from 框架 import *

def demo():
    game = Game()
    game.initialize_game()
    
    # 快速手动演示
    game.start_round()
    
    player = game.players[0]  # 东家
    
    print("\n=== 演示：新的手牌显示格式 ===\n")
    print("原来的格式（竖向+序号）：")
    sorted_hand = sorted(player.hand, key=lambda t: (t.tile_type.value, t.rank))
    for idx, tile in enumerate(sorted_hand, 1):
        print(f"  {idx}. {tile}")
    
    print("\n新的格式（横向+简称）：")
    hand_shorthands = ' '.join(tile.to_shorthand() for tile in sorted_hand)
    print(f"  {hand_shorthands}")
    
    print("\n简称说明：")
    print("  数牌：1m-9m(万), 1p-9p(筒), 1s-9s(条)")
    print("  字牌：E(东), S(南), W(西), N(北), C(中), F(发), P(白)")
    
    print("\n=== 现在可以直接输入简称来出牌 ===")
    print(f"示例：输入 '{sorted_hand[0].to_shorthand()}' 就能打出该牌")

if __name__ == "__main__":
    demo()
