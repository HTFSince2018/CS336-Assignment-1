from collections import defaultdict
import pretokenization_example
from typing import Tuple
import regex as re
import multiprocess


PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

# 定义一个线程来处理分词任务
def worker(arg):
    text = arg
    subtext = re.split('|'.join([r'<\|endoftext\|>']), text)
    res = [re.findall(PAT, t) for t in subtext]
    return res

class BPE:
    # 初始化分词器
    def __init__(
            self,
            vocab_size: int = 1000,
            special_tokens: list[str] = None
        ):
        self.dic = {}
        self.count = defaultdict(int)
        self.MAX_DIC = vocab_size
        self.special_tokens = special_tokens
        self.merges = []
        self.neighbor_sum = defaultdict(int)
        self.init_dic(special_tokens)

    def init_dic(self, special_tokens: list[str]):
        for i in range(256):
            # 初始字节词汇表(0~255)
            self.dic[bytes([i])] = i
        # 特殊字符串，在这里将这些字符串视为硬性边界
        if special_tokens:
            for token in special_tokens:
                if len(self.dic) > self.MAX_DIC:
                    raise IndexError("超出了类的字典最大值！！")
                self.dic[bytes(token.encode("utf-8"))] = len(self.dic)


    # 预分词
    def _pre_tokenization(self, input_path: str, workers: int = 4):
        chunks = []
        # 使用官方作业中给的切块的方式来进行切块
        with open(input_path, "rb") as f:
            boundaries = pretokenization_example.find_chunk_boundaries(f, workers, b"<|endoftext|>")
            for start, end in zip(boundaries[:-1], boundaries[1:]):
                f.seek(start)
                chunk = f.read(end - start).decode("utf-8", errors="ignore")
                # 切的每一块都保存下来
                chunks.append(chunk)
        
        with multiprocess.Pool(processes=workers) as pool:
            # pool.map会自动对应每一个chunks
            results = pool.map(worker, chunks)
        all_tokens = []
        for result in results:
            all_tokens.extend(result)
        # 把各个线程中的结果加和起来返回
        return all_tokens

    # 合并操作
    def _merge(self):
        # 更新词典，将合并后的词元加入到字典中
        self.dic[self.merges[-1]] = len(self.dic)

        # 并将相邻字符对结合起来并更新count
        new_count = defaultdict(int)
        for token in self.count:
            i = 0
            while i < len(token) - 1:
                pair = (token[i], token[i + 1])
                if pair[0] == self.merges[-1][0] and pair[1] == self.merges[-1][1]:
                    new_token = token[:i] + (self.merges[-1],) + token[i + 2:]
                    new_count[new_token] += self.count[token]
                    i += 2
                else:
                    new_count[token] = self.count[token]
                    i += 1
        self.count = new_count

    # 统计相邻字节词元的数量
    def acount_adjacent_tokens(self, all_tokens: list[list[str]]):
        for token in all_tokens:
            for sub_token in token:
                token_bytes = sub_token.encode("utf-8")
                token_bytes = tuple(bytes([b]) for b in token_bytes) # 将单个词元按字节转换为元组，以便同一个词内的字符对进行比较
                self.count[token_bytes] += 1
        for token_bytes, freq in self.count.items():
            for i in range(len(token_bytes) - 1):
                pair = (token_bytes[i], token_bytes[i + 1])
                self.neighbor_sum[pair] += freq

                    
                

    # 训练函数
    def train(self, input_path:str, workers: int = 4) -> Tuple[dict[int, bytes],list[tuple[bytes, bytes]]]:
        # 预先将每一段语句的单词分开
        all_tokens = self._pre_tokenization(input_path, workers)

        # 统计出每段语句中的相邻词元的数量
        self.acount_adjacent_tokens(all_tokens)

        # 每次选择最大相邻词元进行合并
        # TODO: // 将acount改为堆
        while len(self.dic) < self.MAX_DIC and self.neighbor_sum:            
            sorted_neighbor_sum = sorted(self.neighbor_sum.items(), key=lambda x:(x[1], x[0]), reverse=True)
            if sorted_neighbor_sum:
                best_pair = sorted_neighbor_sum[0][0]
                self.merges.append(list(best_pair))
            self._merge()
        vocab = {v: k for k, v in self.dic.items()}
        return vocab, self.merges






def __main__():
    bpe = BPE(vocab_size=1000, special_tokens=["<|endoftext|>"])
    vocab, merges = bpe.train("../data/TinyStoriesV2-GPT4-valid.txt", workers=8)
    print("Vocabulary:", vocab)
    print("Merges:", merges)
if __name__ == "__main__":
    __main__()