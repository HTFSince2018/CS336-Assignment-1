import string
from collections import defaultdict
import regex as re

# 通过遍历初始化词汇表
dic = {}
def __init__():
    for i in range(257):
        if i == 256:
            dic[bytes("<|endoftext|>".encode("utf-8"))] = 0
            continue
        dic[bytes(chr(i).encode("utf-8"))] = i

# 设置预分词匹配正则表达式
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
# 频率表，每次更新
count = defaultdict(int)
# 预分词
def pre_tokenization(text: string):
    # 1. 通过正则表达式预分词
    for m in re.finditer(PAT, text):
        # 2. 根据找出来的每一个预分词转化为tuple元组(占内存更少，结构更加轻量)，并将这些元组插入到频率表中
        temp = tuple()
        for t in m.group().strip():
            temp = tuple((*temp, bytes(t.encode("utf-8"))))
        count[tuple(temp)] += 1

    # 3. 返回频率表
    return count

def merge():
    # 1. 遍历字典，取得字典中的key元素，两两组合在一起统计出现次数(后续可以转为大根堆实现)]
    key_count = defaultdict(int)
    for key in count:
        for j in range(len(key)):
            if j == 0:
                begin = key[j]
                continue
            end = key[j]
            key_count[(begin, end)] += count[key]
            begin = end
    # 2. 选取频次最高的组合(频次相同的选择字典序最高的一组)合并到词汇表中
    sorted_key_count = sorted(key_count.items(), key=lambda item: (item[1], item[0][0], item[0][1]), reverse=True)
    ad2dic = b''.join(sorted_key_count[0][0])
    dic[ad2dic] = len(dic)
    # 3. 更新频次表


    pass
def main():
    pre_tokenization("""low low low low low lower lower widest widest widest newest newest newest newest newest newest""")
    print(count)
    merge()
if __name__ == '__main__':
    __init__()
    main()