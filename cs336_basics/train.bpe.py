from collections import defaultdict
import pretokenization_example
from typing import Tuple
import regex as re
import multiprocess

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
                self.dic[bytes([token.encode("utf-8")])] = len(self.dic)


    # 预分词
    def _pre_tokenization(self, input_path: str, workers: int = 4):
        PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

        # 定义一个线程
        def woker(text: str):
            subwords = re.split(PAT.join(self.special_tokens), text)
            
            pass
        with open(input_path, "rb") as f:
            boundaries = pretokenization_example.find_chunk_boundaries(f, workers, self.special_tokens)
            for start, end in zip(boundaries[:-1], boundaries[1:]):
                f.seek(start)
                chunk = f.read(end - start).decode("utf-8", errors="ignore")
                


    # 分线程完成分词操作
    def _process_pre_tokenization():
        pass

    # 合并操作
    def _merge():
        pass

    # 训练函数
    def train() -> Tuple[dict[int, bytes],list[tuple[bytes, bytes]]]:
        pass