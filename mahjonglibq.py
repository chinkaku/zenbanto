import random
import copy

tile_list = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', 
             '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 
             '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
             '1z', '2z', '3z', '4z', '5z', '6z', '7z']

from colorama import init, Fore, Back, Style

init(autoreset=True)

def red(s):
    return Fore.RED + s + Fore.RESET

def green(s):
    return Fore.GREEN + s + Fore.RESET

def cyan(s):
    return Fore.CYAN + s + Fore.RESET

def white(s):
    return Fore.WHITE + s + Fore.RESET

def yellow(s):
    return Fore.YELLOW + s + Fore.RESET

def strlist(group):
    sgroup = []
    for i in range(len(group)):
        if group[i] < 9:
            geek = red(tile_list[group[i]])
        elif group[i] < 18:
            geek = green(tile_list[group[i]])
        elif group[i] < 27:
            geek = cyan(tile_list[group[i]])
        else:
            geek = white(tile_list[group[i]])
        if i < len(group) - 1:
            if group[i] // 9 == group[i + 1] // 9:
                geek = geek[:-1]
        sgroup.append(geek)
    want = ""
    for i in sgroup:
        want = want + i
    return want

def strlist2(group):
    sgroup = []
    for i in range(len(group)):
        if group[i] < 9:
            geek = red(tile_list[group[i]])
        elif group[i] < 18:
            geek = green(tile_list[group[i]])
        elif group[i] < 27:
            geek = cyan(tile_list[group[i]])
        else:
            geek = white(tile_list[group[i]])
        sgroup.append(geek)
    want = ""
    for i in sgroup:
        want = want + i + " "
    want = want[:-1]
    return want

def charConvert(s):
    result = []
    num_buffer = ""
    
    for char in s:
        if char.isalpha():  # 检查字符是否为字母
            if num_buffer:  # 如果数字缓冲区中有内容
                for num in num_buffer:
                    result.append(num + char)  # 将每个数字与字母组合
                num_buffer = ""  # 清空数字缓冲区
        elif char.isdigit():  # 如果字符为数字
            num_buffer += char  # 将数字添加到数字缓冲区
    
    return result

def indicesFromTileList(converted_list, tile_list):
    result_indices = []
    
    for tile in converted_list:
        if tile in tile_list:
            index = tile_list.index(tile)
            result_indices.append(index)
        else:
            # 这里忽略
            pass
    
    return result_indices

def stringToIndices(s, tile_list):
    converted_list = charConvert(s)
    indices_list = indicesFromTileList(converted_list, tile_list)
    return indices_list


def checkValid(group):
    if len(group) in [3, 4]:
        # 检查刻子
        if len(set(group)) == 1:
            return True
        # 检查顺子
        elif len(group) == 3:
            sorted_group = sorted(group)
            if (sorted_group[2] - sorted_group[1] == 1 and
                sorted_group[1] - sorted_group[0] == 1 and
                all(i // 9 == sorted_group[0] // 9 for i in sorted_group) and
                sorted_group[0] < 27):
                return True
    return False

def isValidSet(set_):
    if len(set_) == 3 and checkValid(set_):
        return True
    return False

def noPairCombinationsFind(group101):
    group=group101[:]
    group.sort()
    if len(group) == 3:
        if isValidSet(group):
            return [[group]]
        else:
            return []

    allPossibleVersions = []
    
    # 处理刻子
    if group[0] == group[2]:
        subCombinations = noPairCombinationsFind(group[3:])
        for combination in subCombinations:
            allPossibleVersions.append(combination + [group[:3]])

    # 处理顺子
    if group[0] % 9 <= 6 and group[0] < 27 and group[0]+1 in group and group[0]+2 in group:
        temporaryList1 = group[:]
        temporaryList1.remove(group[0])
        temporaryList1.remove(group[0]+1)
        temporaryList1.remove(group[0]+2)
        subCombinations = noPairCombinationsFind(temporaryList1)
        for combination in subCombinations:
            allPossibleVersions.append(combination + [[group[0], group[0]+1, group[0]+2]])

    return allPossibleVersions

def onePairCombinationsFind(group101):
    group=group101[:]
    group.sort()
    if len(group) % 3 != 2:
        return []
    if len(group) == 2:
        if group[0] == group[1]:
            return [[group]]
        else:
            return []

    allPossibleVersions = []

    # 处理刻子
    if group[0] == group[2]:
        subCombinations = onePairCombinationsFind(group[3:])
        for combination in subCombinations:
            allPossibleVersions.append(combination + [group[:3]])

    # 处理顺子
    if group[0] % 9 <= 6 and group[0] < 27 and group[0]+1 in group and group[0]+2 in group:
        temporaryList1 = group[:]
        temporaryList1.remove(group[0])
        temporaryList1.remove(group[0]+1)
        temporaryList1.remove(group[0]+2)
        subCombinations = onePairCombinationsFind(temporaryList1)
        for combination in subCombinations:
            allPossibleVersions.append(combination + [[group[0], group[0]+1, group[0]+2]])

    # 处理雀头
    if group[0] == group[1]:
        subCombinations = noPairCombinationsFind(group[2:])
        for combination in subCombinations:
            allPossibleVersions.append(combination + [group[:2]])

    return allPossibleVersions

def sevenPairsCombinationsFind(group101):
    group=group101[:]
    group.sort()
    if len(group) == 14:
        if all(group[2*i] == group[2*i+1] for i in range(7)):
            result =[[group[:2], group[2:4], group[4:6], group[6:8], group[8:10], group[10:12], group[12:14]]]
            result.sort()
            return result
        else:
            return []
    else:
        return []

def thirteenOrphansCombinationsFind(group101):
    group=group101[:]
    group.sort()
    if len(group) == 14 and set(group) == {0,8,9,17,18,26,27,28,29,30,31,32,33}:
        pair = [i for i in group if group.count(i) == 2][0]
        return [[[pair], [0,8,9,17,18,26,27,28,29,30,31,32,33]]]
    return []

def findCombinations(group, special=False):
    test = []
    if not special:
        test.extend(onePairCombinationsFind(group))
    test.extend(sevenPairsCombinationsFind(group))
    test.extend(thirteenOrphansCombinationsFind(group))
    
    # 首先确保所有子列表都已排序
    for sublist in test:
        if isinstance(sublist, list):  # 确保是列表
            sublist.sort()
    
    # 使用元组去重（确保所有元素都是可哈希的）
    unique_set = set()
    result = []
    
    for sublist in test:
        # 如果子列表包含嵌套列表，需要递归转换为元组
        if any(isinstance(item, list) for item in sublist):
            # 递归转换嵌套列表为元组
            tuple_repr = tuple(
                tuple(item) if isinstance(item, list) else item 
                for item in sublist
            )
        else:
            tuple_repr = tuple(sublist)
        
        if tuple_repr not in unique_set:
            unique_set.add(tuple_repr)
            result.append(sublist)  # 保留原始列表
    
    return result

