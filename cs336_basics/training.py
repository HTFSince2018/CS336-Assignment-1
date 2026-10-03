import regex as re

test_string = "Hello, 刘江龙!"
utf8_encoded = test_string.encode("utf-8")
print(type(utf8_encoded))

list_of_encoded = list(utf8_encoded)
print(list_of_encoded)

test_string = "ab"
utf8_encoded = test_string.encode("utf-8")

list_of_encoded = list(utf8_encoded)
print(list_of_encoded)

def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])

print(decode_utf8_bytes_to_str_wrong("hello".encode("utf-8")))

re.finditer()