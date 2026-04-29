"""
生成测试输入文件
"""

# 生成足够的输入来完成一盘游戏
inputs = []

# 第一盘的输入：大约需要20-30次选择
for i in range(50):
    if i % 3 == 0:  # 出牌时
        inputs.append("1m")  # 输入一个简称，但实际需要检查手牌
    else:  # 鸣牌或待鸣时
        inputs.append("0")  # 不选择鸣牌

with open('test_input.txt', 'w') as f:
    f.write('\n'.join(inputs))

print("生成测试输入文件完成")
