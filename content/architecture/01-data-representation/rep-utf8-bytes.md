---
id: rep-utf8-bytes
title: Encoding and recognising UTF-8
level: intermediate
minutes: 3
summary: UTF-8 uses one to four bytes per scalar value.
sourceLesson: rep-text-encoding
---

This unit continues the preceding material on Unicode scalar values and their encodings.

## UTF-8: the encoding that won

**UTF-8** was designed by Ken Thompson and Rob Pike in 1992. It uses 1 to 4 bytes per Unicode scalar value:

| Code points | Bytes | Bit pattern |
|---|---|---|
| U+0000–007F | 1 | `0xxxxxxx` |
| U+0080–07FF | 2 | `110xxxxx 10xxxxxx` |
| U+0800–FFFF, excluding D800–DFFF | 3 | `1110xxxx` + 2 × `10xxxxxx` |
| U+10000–10FFFF | 4 | `11110xxx` + 3 × `10xxxxxx` |

The `x` positions carry the code point's bits, most significant first. For a valid multibyte sequence, the number of leading 1s gives the **total** byte count, not the number of following bytes, and every continuation byte starts with `10`.

### Worked example: € (U+20AC)

U+20AC is between 0x0800 and 0xFFFF, so it needs 3 bytes with 4 + 6 + 6 = 16 payload bits.

```
0x20AC = 0010 0000 1010 1100

split 4 | 6 | 6:
0010 | 000010 | 101100

fill the template:
1110 0010  10 000010  10 101100
= E2       82         AC
```

So `€` is the three bytes `E2 82 AC`.

### Worked example: 😀 (U+1F600)

Above U+FFFF, so 4 bytes with 3 + 6 + 6 + 6 = 21 payload bits.

```
0x1F600 as 21 bits:
000 011111 011000 000000

11110 000 = F0
10 011111 = 9F
10 011000 = 98
10 000000 = 80
```

`😀` is `F0 9F 98 80`.

```python
# Encode code points into UTF-8 bytes.
'€'.encode('utf-8')   # b'\xe2\x82\xac'
'😀'.encode('utf-8')  # b'\xf0\x9f\x98\x80'
```

### Why UTF-8 is so good

- **ASCII compatible.** ASCII text is valid UTF-8 byte for byte. Tools that recognise only ASCII delimiters can often process UTF-8 unchanged, provided they otherwise preserve arbitrary bytes.
- **No zero bytes** except for U+0000 itself, so C strings and `strlen` still function (counting bytes, not characters).
- **Self-synchronising.** In a valid UTF-8 stream, continuation bytes start with 10 and other bytes start a sequence. At most three continuation bytes remain after an arbitrary position inside a character. Invalid bytes such as C0, C1 and F5–FF require rejection or specified error handling; corruption is not guaranteed to damage exactly one character.
- **No byte order.** It is a sequence of bytes, so endianness never arises.
- **Sorting.** Lexicographic comparison of unsigned bytes in valid UTF-8 agrees with scalar-value order. This is not linguistic collation, and normalisation differences still matter.

UTF-8 is widely used for interchange. RFC 8259 requires it for JSON exchanged outside a closed ecosystem; Rust and Go source text use UTF-8, and it is Python 3 source's default. Operating-system files and C strings are not universally UTF-8, and decoding defaults depend on the interface and configuration.

> [!note] Evidence gap
> The previous website-adoption percentage is omitted: it lacked a dated survey and sampling definition, so it was not reliable evidence for a current universal figure.

## Key takeaways
- UTF-8 uses one to four bytes per scalar value.
- Continuation bytes begin with the bits 10.
- Only shortest valid forms are permitted.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
