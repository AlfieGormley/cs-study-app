---
id: rep-text-boundaries
title: Wrong decoders and text boundary failures
level: intermediate
minutes: 3
summary: Declare and enforce the encoding at each boundary.
sourceLesson: rep-text-encoding
---

This unit continues the preceding material on Unicode scalar values and their encodings.

## Mojibake and other failures

### Wrong decoder

Decoding UTF-8 bytes as Windows-1252 often produces mojibake, but some bytes are undefined in strict Windows-1252 decoders and can raise errors:

```python
# A wrong decoder garbles valid bytes.
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
- Declare and enforce the encoding at each boundary.
- Strict decoding and path containment are separate requirements.
- Byte-oriented case conversion is not Unicode case conversion.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
- [UTF-8 — Wikipedia](https://en.wikipedia.org/wiki/UTF-8)
- [UTF-16 — Wikipedia](https://en.wikipedia.org/wiki/UTF-16)
- [The Absolute Minimum Every Software Developer Must Know About Unicode — Joel Spolsky](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
- [Unicode HOWTO — Python docs](https://docs.python.org/3/howto/unicode.html)
- [RFC 3629: UTF-8, a transformation format of ISO 10646](https://www.rfc-editor.org/rfc/rfc3629)
- [Unicode Normalization Forms (UAX #15)](https://www.unicode.org/reports/tr15/)
