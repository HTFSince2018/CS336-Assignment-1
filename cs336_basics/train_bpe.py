from collections import Counter, defaultdict
import pretokenization_example
import regex as re
import multiprocess
import json
from pathlib import Path

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""


# 多进程执行预分词，并统计词频
def worker(args):
    text, special_tokens = args

    # 特殊词元作为硬性边界
    if special_tokens:
        pattern = "|".join(re.escape(s) for s in special_tokens)
        subtexts = re.split(pattern, text)
    else:
        subtexts = [text]

    count = Counter()

    for subtext in subtexts:
        tokens = re.findall(PAT, subtext)

        for token in tokens:
            # 将字符串转成单字节组成的元组
            token_bytes = tuple(
                bytes([b]) for b in token.encode("utf-8")
            )
            count[token_bytes] += 1

    return count


class BPE:
    def __init__(
        self,
        vocab_size: int = 1000,
        special_tokens: list[str] = None
    ):
        self.dic = {}
        self.count = Counter()
        self.MAX_DIC = vocab_size
        self.special_tokens = special_tokens or []
        self.merges = []
        self.neighbor_sum = Counter()
        self.pair_to_words = defaultdict(set)

        if vocab_size < 256 + len(self.special_tokens):
            raise ValueError("词表大小不能小于初始词元数量")

        self.init_dic(self.special_tokens)

    # 初始化词表
    def init_dic(self, special_tokens):
        for i in range(256):
            self.dic[bytes([i])] = i

        for token in special_tokens:
            token_bytes = token.encode("utf-8")
            if token_bytes in self.dic:
                raise ValueError("特殊词元重复")
            self.dic[token_bytes] = len(self.dic)

    # 预分词
    def _pre_tokenization(
        self,
        input_path: str,
        workers: int = 4
    ):
        chunks = []

        with open(input_path, "rb") as f:
            boundaries = (
                pretokenization_example.find_chunk_boundaries(
                    f, workers, b"<|endoftext|>"
                )
            )

            for start, end in zip(
                boundaries[:-1], boundaries[1:]
            ):
                f.seek(start)
                chunk = f.read(end - start).decode(
                    "utf-8", errors="ignore"
                )
                chunks.append(chunk)

        # 并行计算词频，避免保存全部分词结果
        with multiprocess.Pool(processes=workers) as pool:
            args = [
                (chunk, self.special_tokens)
                for chunk in chunks
            ]

            for result in pool.imap(worker, args):
                self.count.update(result)

    def _update_pair_counts(self, token, freq, sign):
        # 一个词内同一相邻对可能出现多次；索引里则只需记录这个词一次。
        pair_counts = Counter(zip(token, token[1:]))
        for pair, occurrences in pair_counts.items():
            updated = self.neighbor_sum[pair] + sign * freq * occurrences
            if updated:
                self.neighbor_sum[pair] = updated
            else:
                self.neighbor_sum.pop(pair, None)

            if sign > 0:
                self.pair_to_words[pair].add(token)
            else:
                words = self.pair_to_words[pair]
                words.remove(token)
                if not words:
                    del self.pair_to_words[pair]

    # 建立相邻对频率及其所在词的索引
    def acount_adjacent_tokens(self):
        self.neighbor_sum.clear()
        self.pair_to_words.clear()

        for token, freq in self.count.items():
            self._update_pair_counts(token, freq, 1)

    # 合并指定词元对
    def _merge(self, best_pair):
        # 生成合并后的新词元
        merged_token = best_pair[0] + best_pair[1]

        # 将新词元添加到词表
        self.dic[merged_token] = len(self.dic)

        new_count = Counter()

        # 只有包含目标相邻对的词会变化；先移除旧词的频率贡献。
        affected_words = tuple(self.pair_to_words[best_pair])
        for token in affected_words:
            freq = self.count.pop(token)
            self._update_pair_counts(token, freq, -1)
            new_token = []
            i = 0

            while i < len(token):
                if (
                    i < len(token) - 1
                    and (token[i], token[i + 1]) == best_pair
                ):
                    new_token.append(merged_token)
                    i += 2
                else:
                    new_token.append(token[i])
                    i += 1

            # 不同旧词可能合并成同一个新词，先汇总再更新索引。
            new_count[tuple(new_token)] += freq

        for token, freq in new_count.items():
            self.count[token] += freq
            self._update_pair_counts(token, freq, 1)

    # 训练 BPE
    def train(
        self,
        input_path: str,
        workers: int = 4
    ) -> tuple[dict[int, bytes], list[tuple[bytes, bytes]]]:

        # 重置训练状态
        self.count.clear()
        self.neighbor_sum.clear()
        self.pair_to_words.clear()
        self.merges.clear()
        self.dic.clear()
        self.init_dic(self.special_tokens)

        # 预分词并统计词频
        self._pre_tokenization(input_path, workers)

        # 初始化相邻词元对频率
        self.acount_adjacent_tokens()

        # 持续合并最高频的相邻词元对
        while (
            len(self.dic) < self.MAX_DIC
            and self.neighbor_sum
        ):
            # 频率优先，频率相同按字节序选择最大的
            best_pair = max(
                self.neighbor_sum,
                key=lambda pair: (
                    self.neighbor_sum[pair],
                    pair
                )
            )

            self.merges.append(best_pair)

            # 合并并更新统计
            self._merge(best_pair)

        vocab = {v: k for k, v in self.dic.items()}
        return vocab, self.merges

def save_bpe(vocab, merges, output_dir="output"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 将 bytes 转换为十六进制字符串
    vocab_data = {
        str(token_id): token.decode("utf-8", errors="ignore")
        for token_id, token in vocab.items()
    }

    merges_data = [
        [left.decode('latin-1'), right.decode('latin-1')]
        for left, right in merges
    ]

    # 保存词表
    with open(output_dir / "vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, ensure_ascii=False, indent=2)

    # 保存合并规则
    with open(output_dir / "merges.json", "w", encoding="utf-8") as f:
        json.dump(merges_data, f, ensure_ascii=False, indent=2)

def __main__():
    bpe = BPE(
        vocab_size=1000,
        special_tokens=["<|endoftext|>"]
    )

    vocab, merges = bpe.train(
        "../data/TinyStoriesV2-GPT4-valid.txt",
        workers=8
    )
    save_bpe(vocab, merges, output_dir="output")


if __name__ == "__main__":
    __main__()
