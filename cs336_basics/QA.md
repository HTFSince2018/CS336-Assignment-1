# Problem 1: Understanding Unicode
## (a) What Unicoade character does chr(0) return?

- 会输出一个空的字符串“”

## (b) How does this character’s string representation (__repr__()) differ from its printed representation?

- repr()中会直接输出所有在括号中的东西，即括号中参数为 "zcsad " ，终端会输出 'zcsad '

## (c) What happens when this character occurs in text? It may be helpful to play around with the following in your Python interpreter and see if it matches your expectations:

\>>> chr(0)

\>>> print(chr(0))

\>>> "this is a test" + chr(0) + "string"

\>>> print("this is a test" + chr(0) + "string")

- 会输出 "this is a teststring"，即chr(0)为空字符串

# Problem 2: Unicode Encodings

## (a) What are some reasons to prefer training our tokenizer on UTF-8 encoded bytes, rather than UTF-16 or UTF-32? It may be helpful to compare the output of these encodings for various input strings.

- 因为utf-8的编码的互联网语料资料丰富，便于模型的训练，且utf-8的编码更加紧凑，也会根据字符的大小来动态选择1~4个bytes表示，不会像utf16或者utf32一样产生很多的"00"，比如

| 字符串 | UTF-8 | UTF-16LE | UTF-32LE |
|---|---|---|---|
| `hello` | `68 65 6C 6C 6F` | `68 00 65 00 6C 00 6C 00 6F 00` | `68 00 00 00 ...` |
| 字节数 | **5** | 10 | 20 |
| `中文` | `E4 B8 AD E6 96 87` | `2D 4E 87 65` | `2D 4E 00 00 87 65 00 00` |
| 字节数 | 6 | **4** | 8 |
| `🙂` | `F0 9F 99 82` | `3D D8 42 DE` | `42 F6 01 00` |
| 字节数 | 4 | 4 | 4 |

## (b) Consider the following (incorrect) function, which is intended to decode a UTF-8 byte string into a Unicode string. Why is this function incorrect? Provide an example of an input byte string that yields incorrect results.
```python
def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])

>>> decode_utf8_bytes_to_str_wrong("hello".encode("utf-8"))
``` 

- 当调用这个函数是传入的参数是中文或者表情包的时候就会报错，即当字符无法被1个byte所解释时就会有问题

## (c) Give a two-byte sequence that does not decode to any Unicode character(s).

