"""
自动测试脚本：让人类玩家自动选择，出牌时输入有效的简称
"""

import subprocess
import sys
import re

def auto_play():
    """自动运行一盘游戏"""
    process = subprocess.Popen(
        [sys.executable, '框架.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd='q:\\mahjong',
        bufsize=1
    )
    
    output_lines = []
    current_hand = []
    input_count = 0
    
    try:
        for line in process.stdout:
            output_lines.append(line)
            print(line, end='')
            
            # 如果检测到"请输入要打出的牌的简称"，发送第一张牌的简称
            if "请输入要打出的牌的简称" in line and current_hand:
                tile = current_hand[0]
                process.stdin.write(f"{tile}\n")
                process.stdin.flush()
                print(f">>> 自动输入: {tile}")
                input_count += 1
            
            # 如果检测到"手牌"行，提取简称
            elif "手牌(" in line:
                match = re.search(r'手牌\(\d+张\)：(.+)', line)
                if match:
                    hand_str = match.group(1).strip()
                    current_hand = hand_str.split()
            
            # 如果检测到"可选操作"，发送0（不鸣牌）
            elif "请选择（输入序号）" in line:
                if "可选操作" in ''.join(output_lines[-10:]):
                    process.stdin.write("0\n")
                    process.stdin.flush()
                    print(">>> 自动输入: 0 (不鸣牌)")
            
            if input_count > 50:  # 安全机制：超过50次输入就停止
                break
        
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        print("\n游戏超时")

if __name__ == "__main__":
    auto_play()

