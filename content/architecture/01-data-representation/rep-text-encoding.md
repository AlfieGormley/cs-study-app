---
id: rep-text-encoding
title: Unicode, UTF-8 and UTF-16
level: intermediate
minutes: 14
summary: From ASCII to Unicode code points, how UTF-8 and UTF-16 turn them into bytes bit by bit, and why string length, mojibake and normalisation catch so many programs out.
---

Text is just numbers with an agreed mapping. The letter `A` is stored as 65 because, long ago, people agreed that 65 means `A`. The hard part is that for decades different groups agreed on different mappings, and a byte written under one was read under another.

This lesson separates two ideas that are easy to blur:

- A coded **character set** assigns numbers to its encoded elements; a user-perceived character can require several of those elements. In Unicode that number is a **code point**.
- An **encoding** turns those numbers into bytes. UTF-8, UTF-16 and UTF-32 are three encoding forms for Unicode scalar values (code points excluding the surrogate range). UTF-16 and UTF-32 also need a byte-order convention for byte serialisation.

## ASCII and the code-page era

**ASCII** (1963) uses 7 bits for 128 characters: control codes 0–31 and 127, then space, digits, punctuation, and upper- and lower-case English letters.

```
'0' = 0x30   'A' = 0x41   'a' = 0x61
```

Two tidy design choices are worth knowing. The digit `d` is `0x30 + d`, so `c - '0'` converts a digit character to its value. Upper and lower case differ only in bit 5 (`0x20`), so `c | 0x20` lower-cases an ASCII letter.

Bytes have 8 bits, so the top 128 values were free. Everyone filled them differently: ISO 8859-1 (Latin-1) for Western Europe, Windows-1252 (mostly shares Latin-1 assignments but replaces many C1-control positions with other characters), KOI8-R for Russian, Shift JIS for Japanese, and many others. Plain text bytes often lack encoding metadata, though a file format can include such metadata. Shift JIS is variable-width, not merely a different assignment of single high bytes. Open a Russian file with the Western code page and you got gibberish, which the Japanese call **mojibake**.

## Unicode: one number per character

**Unicode** provides a shared repertoire of encoded characters across many writing systems, written `U+` followed by hex:

```
U+0041  A    LATIN CAPITAL LETTER A
U+00E9  é    LATIN SMALL LETTER E WITH ACUTE
U+20AC  €    EURO SIGN
U+4F60  你   CJK UNIFIED IDEOGRAPH
U+1F600 😀   GRINNING FACE
```

The code space runs from U+0000 to **U+10FFFF**, which is 1,114,112 positions in 17 **planes** of 65,536. Plane 0, the **Basic Multilingual Plane** (BMP, U+0000 to U+FFFF), includes many common scripts. Supplementary planes contain further scripts, CJK characters and many emoji; some emoji are in the BMP. Not every code point is an assigned character: the code space also includes surrogates, private-use areas, noncharacters and unassigned positions.

The first 128 code points are identical to ASCII, and the first 256 to Latin-1.

## UTF-32: simple and wasteful

UTF-32 stores each Unicode scalar value as one 32-bit code unit. That is four octets per scalar value, so finding the *n*th code point is O(1). But English text becomes four times larger, and the bytes depend on endianness (UTF-32LE vs UTF-32BE). It is used internally sometimes, rarely for storage or exchange.

## UTF-8: the encoding that won

**UTF-8** was designed by Ken Thompson and Rob Pike in 1992. It uses 1 to 4 bytes per code point:

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

## UTF-16 and surrogate pairs

**UTF-16** uses 16-bit **code units**. BMP scalar values (excluding D800–DFFF) take one unit. Code points above U+FFFF take two, called a **surrogate pair**, built from a range of the BMP (U+D800 to U+DFFF) reserved so that no character uses it.

To encode a code point *c* above U+FFFF:

1. Subtract 0x10000, leaving a 20-bit number.
2. The top 10 bits plus 0xD800 give the **high surrogate**.
3. The low 10 bits plus 0xDC00 give the **low surrogate**.

For 😀 (U+1F600):

```
0x1F600 - 0x10000 = 0x0F600
= 0000 1111 01 | 10 0000 0000
top 10:  0x03D  -> D800 + 03D = D83D
low 10:  0x200  -> DC00 + 200 = DE00
```

So 😀 in UTF-16 is `D83D DE00`. Because of the reserved surrogate block, those 2,048 values can never be characters, leaving 1,112,064 valid **scalar values**.

UTF-16 extends an earlier 16-bit design with surrogate pairs. Java, JavaScript, Windows W APIs, .NET and Qt use 16-bit code units in their string interfaces; their adoption histories differ, so they should not all be described as pre-1996 adopters. UTF-16 also has byte-order variants (UTF-16LE and UTF-16BE), often signalled by a **byte order mark** (BOM), U+FEFF, at the start of the file.

## What is the length of a string?

There are at least four answers, and languages disagree on which one `len` returns.

```
string: "é😀"
code points        2
UTF-16 code units  3   (1 + 2)
UTF-8 bytes        6   (2 + 4)
```

| Language | `len` / `length` counts |
|---|---|
| Python 3 `str` | code points |
| JavaScript, Java | UTF-16 code units |
| Go string len; Rust str.len() | bytes (Rust str is valid UTF-8; Go strings may hold arbitrary bytes) |
| C strlen | bytes before the first NUL, regardless of encoding |

In JavaScript `'😀'.length` is 2, and slicing it in the middle can produce a lone surrogate: allowed in a JavaScript string but not well-formed UTF-16 for interchange. In C, strlen("é") is 2 if the execution string literal encoding is UTF-8; source-file encoding alone does not guarantee that.

### Graphemes: what the user sees

Even code points are not "characters" as a reader sees them. An extended **grapheme cluster** approximates a user-perceived character under Unicode segmentation rules, and it can be many code points:

- `é` can be one code point (U+00E9) or two: `e` + U+0301 COMBINING ACUTE ACCENT.
- 👍🏽 is U+1F44D plus a skin-tone modifier, U+1F3FD: 2 code points, 8 UTF-8 bytes.
- 🇬🇧 is two "regional indicator" code points, G and B.
- Family emoji join several people with U+200D ZERO WIDTH JOINER and can exceed 20 bytes.

User-facing cursor movement and character limits often need grapheme segmentation. Storage/protocol limits still need byte counts; neither replaces the other. Python's standard library has no grapheme function; the third-party `regex` module's `\X` pattern finds them.

## Normalisation

Because `é` has two spellings, two strings can look identical but compare unequal:

```python
import unicodedata as ud

a = 'café'      # precomposed
b = 'café'     # e + combining
a == b               # False
len(a), len(b)       # (4, 5)
ud.normalize('NFC', b) == a   # True
```

Unicode defines normal forms. **NFC** composes where possible (the usual choice for storage and comparison). **NFD** decomposes. HFS+ historically uses a modified decomposed form; other macOS file systems have different storage and comparison rules. Do not assume that all macOS filenames are byte-for-byte standard NFD. **NFKC** also folds "compatibility" variants such as `ﬁ` (one ligature code point) into `fi`, which is useful for search and usernames.

## Mojibake and other failures

### Wrong decoder

Decoding UTF-8 bytes as Windows-1252 often produces mojibake, but some bytes are undefined in strict Windows-1252 decoders and can raise errors:

```python
'é'.encode('utf-8').decode('cp1252')
# 'Ã©'
'€'.encode('utf-8').decode('cp1252')
# 'â‚¬'
```

Sequences such as `Ã©` or `â€™` often indicate UTF-8 decoded as Windows-1252 (though the displayed text alone is not conclusive). The fix is to know the encoding at every boundary: HTTP `Content-Type: text/html; charset=utf-8`, `open(path, encoding='utf-8')` in Python, the connection charset in a database driver.

> [!warning] MySQL's utf8 is not UTF-8
> In MySQL, the character set historically named `utf8` is really `utf8mb3`: at most 3 bytes per character, so it cannot store supplementary characters such as 😀. Some emoji are BMP characters and do fit. Inserting 😀 fails or truncates. Use `utf8mb4`, which is the default since MySQL 8.0.

### Overlong encodings

Nothing in the bit layout stops you writing `/` (U+002F) in two bytes as `C0 AF`. The standard forbids such **overlong** forms, but early decoders accepted them. Microsoft IIS was hit by a famous directory-traversal attack in 2000: `..%c0%af..` slipped past a check for `../` and was decoded to it afterwards. Correct decoders reject overlongs, lone surrogates and values above U+10FFFF. Decode strictly, apply the protocol's canonicalisation rules, then validate the decoded path and enforce containment in the intended directory. Unicode normalisation alone is not a path-traversal defence.

### Bytes versus text

Python 3 makes the distinction a type: `bytes` is raw data, `str` is a sequence of code points. You convert explicitly with `.encode()` and `.decode()`. Many Python 2 bugs came from mixing them silently. In C, `char` is a byte; functions such as toupper operate on unsigned-char values (or EOF) according to the C locale, not arbitrary Unicode characters. Passing a negative signed char value other than EOF is undefined behaviour. Processing UTF-8 byte by byte this way is not Unicode case conversion and may leave bytes unchanged or corrupt them, depending on the locale.

Case conversion is itself language-dependent: `'Straße'.upper()` is `'STRASSE'`, which is one character longer, and Turkish has a dotted and a dotless i.

## Key takeaways
- Unicode has code points from U+0000 to U+10FFFF; UTF-8, UTF-16 and UTF-32 encode scalar values, excluding surrogate code points, with byte-order conventions needed for UTF-16/32 serialisation.
- UTF-8 uses 1–4 bytes: leading byte `0`, `110`, `1110` or `11110`, continuation bytes `10`. € is `E2 82 AC`, 😀 is `F0 9F 98 80`.
- UTF-8 is ASCII-compatible, self-synchronising and byte-order free, which is why it won.
- UTF-16 uses surrogate pairs above U+FFFF: subtract 0x10000, split into two 10-bit halves, add 0xD800 and 0xDC00.
- "Length" can mean bytes, UTF-16 units, code points or graphemes; know which your language counts.
- Choose normalisation and comparison rules for the application. NFC handles canonical equivalence; do not silently change text when exact original bytes or a protocol-specific form are required.
- `Ã©`-style mojibake often indicates UTF-8 decoded with the wrong code page. Declare the encoding at every boundary, and use `utf8mb4` in MySQL.

## Further reading
- [UTF-8 — Wikipedia](https://en.wikipedia.org/wiki/UTF-8)
- [UTF-16 — Wikipedia](https://en.wikipedia.org/wiki/UTF-16)
- [The Absolute Minimum Every Software Developer Must Know About Unicode — Joel Spolsky](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
- [Unicode HOWTO — Python docs](https://docs.python.org/3/howto/unicode.html)
- [RFC 3629: UTF-8, a transformation format of ISO 10646](https://www.rfc-editor.org/rfc/rfc3629)
- [Unicode Normalization Forms (UAX #15)](https://www.unicode.org/reports/tr15/)
