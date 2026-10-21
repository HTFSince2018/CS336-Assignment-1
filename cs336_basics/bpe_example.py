import string
from collections import defaultdict
import regex as re

# 通过遍历初始化词汇表
dic = {}
def __init__():
    for i in range(257):
        if i == 256:
            dic[b"<|endoftext|>"] = 256
            # dic[bytes("<|endoftext|>".encode("utf-8"))] = 256
            continue
        # 按值编码来初始化词汇表
        dic[bytes([i])] = i
        # dic[bytes(chr(i).encode("utf-8"))] = i

# 频率表，每次更新
count = defaultdict(int)

# 预分词
def pre_tokenization(text: string):   
    # bpe_example示例按文档来，只按照空格进行分词
    sub_word = text.split(" ")
    sum_word = defaultdict(int)
    for word in sub_word:
        sum_word[word] += 1
    # 通过items来获得键与值
    for (word, coun) in sum_word.items():
        tup = ()
        for byte in word.encode("utf-8"):
            # 通过 * 解开元组并与之后的字符包含在一起
            tup = (*tup, bytes([byte]))
        count[tup] = coun
    return count

def merge():
    global count
    # 1. 遍历分词表来获得每一个互相邻字节的出现次数(不跨元组)
    sum_neighbor = defaultdict(int)
    # 通过两个窗口的滑动窗口来统计
    for word, coun in count.items():
        for i in range(len(word) - 1):
            pair = (word[i], word[i + 1])
            sum_neighbor[pair] += coun
    if len(sum_neighbor) <= 0:
        return
    # 2. 排序选出出现次数最多的互相邻字节
    sum_neighbor_sorted = sorted(sum_neighbor.items(), key=lambda x:(x[1], x[0]), reverse=True)

    # 3. 合并出现次数最多的互相邻字节
    # 先更新词汇表
    best_pair = sum_neighbor_sorted[0][0]
    best_pair = b"".join(best_pair)
    dic[best_pair] = len(dic)
    best_pair = (sum_neighbor_sorted[0][0][0], sum_neighbor_sorted[0][0][1])
    target = b"".join(best_pair)
    new_count = defaultdict(int)
    # 开始在count中合并
    for word, freq in count.items():
        if keyINWords(best_pair, word):
            new_word = ()
            i = 0
            while i < len(word):
                if i + 1 < len(word) and word[i] == best_pair[0] and word[i + 1] == best_pair[1]:
                    new_word += (target, )
                    i += 2
                else:
                    new_word += (word[i], )
                    i += 1
            new_count[new_word] += freq
        else:
            new_count[word] += freq
    count = new_count

def keyINWords(key, words):
    for ch in key:
        if ch in words:
            continue
        return False
    return True
def main():
    str = "low low low low low lower lower widest widest widest newest newest newest newest newest newest"
    pre_tokenization(str)
    for i in range(6):
        merge()
    print(dic)
    print(count)

if __name__ == '__main__':
    __init__()
    main()