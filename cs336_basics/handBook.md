# tokenizer
这段代码中的 "[b]" 代表用一个整数列表创建一个bytes 对象
```python
def decode_utf8_bytes_to_str_wrong:
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])
```

```python
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
```
这一段正则表达式这样理解：
(?:[sdmt]|ll|ve|re)专门匹配英文缩写的后半部分