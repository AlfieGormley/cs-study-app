---
id: rep-ascii-and-codepoints
title: ASCII, Unicode and scalar values
level: intermediate
minutes: 4
summary: A character set and its byte encoding answer different questions.
sourceLesson: rep-text-encoding
---

Text is just numbers with an agreed mapping. The letter `A` is stored as 65 because, long ago, people agreed that 65 means `A`. The hard part is that for decades different groups agreed on different mappings, and a byte written under one was read under another.

This lesson separates two ideas that are easy to blur:

- A coded **character set** assigns numbers to its encoded elements; a user-perceived character can require several of those elements. In Unicode that number is a **code point**.
- A **character encoding** turns those numbers into bytes. UTF-8, UTF-16 and UTF-32 are three encoding forms for Unicode scalar values (code points excluding U+D800 through U+DFFF, the surrogate range). UTF-16 and UTF-32 also need a byte-order convention for byte serialisation.

## ASCII and the code-page era

**ASCII** uses 7 bits for 128 code positions. Its early revisions differed; the established table preserved by Unicode contains control codes 0–31 and 127, then space, digits, punctuation, and upper- and lower-case English letters.

```
'0' = 0x30   'A' = 0x41   'a' = 0x61
```

Two tidy design choices are worth knowing. First, the ten digit characters are numbered in order, starting at 0x30. After checking that a character is an ASCII digit, subtract the code of `'0'` to obtain its numeric value. The character `'7'` is a text code, not the integer seven.

That is why `c - '0'` in C converts a digit character to its value. Second, upper- and lower-case ASCII letters differ only in bit 5. Setting that bit changes uppercase to the corresponding lowercase letter. This depends on the ASCII layout; it is not a Unicode case-conversion algorithm.

So `c | 0x20` can lower-case an ASCII letter, but must not be applied indiscriminately to punctuation or UTF-8 bytes.

In an eight-bit byte, seven-bit ASCII leaves the top 128 values unused. Everyone filled them differently: ISO 8859-1 (Latin-1) for Western Europe, Windows-1252 (mostly shares Latin-1 assignments but replaces many C1-control positions with other characters), KOI8-R for Russian, Shift JIS for Japanese, and many others. Plain text bytes often lack encoding metadata, though a file format can include such metadata. Shift JIS is variable-width, not merely a different assignment of single high bytes. Open a Russian file with the Western code page and you got gibberish, which the Japanese call **mojibake**.

## Unicode: code points and scalar values

**Unicode** provides a shared repertoire of encoded characters across many writing systems, written `U+` followed by hex:

```
U+0041  A    LATIN CAPITAL LETTER A
U+00E9  é    LATIN SMALL LETTER E WITH ACUTE
U+20AC  €    EURO SIGN
U+4F60  你   CJK UNIFIED IDEOGRAPH
U+1F600 😀   GRINNING FACE
```

The code space runs from U+0000 to **U+10FFFF**, which is 1,114,112 positions in 17 **Unicode planes** of 65,536.

Plane 0, the **Basic Multilingual Plane** (BMP, U+0000 to U+FFFF), includes many common scripts. Supplementary planes contain further scripts, CJK characters and many emoji; some emoji are in the BMP. Not every code point is an assigned character: the code space also includes surrogates, private-use areas, noncharacters and unassigned positions.

The first 128 code points are identical to ASCII, and the first 256 to Latin-1.

## UTF-32: simple and wasteful

UTF-32 stores each Unicode scalar value as one 32-bit code unit. That is four octets per scalar value, so finding the code point at any position takes O(1) time: the same small amount of work whatever the position, because each successive scalar value starts four octets after the previous one, counting from the first encoded scalar value. But English text becomes four times larger, and the bytes depend on endianness (UTF-32LE vs UTF-32BE). It is used internally sometimes, rarely for storage or exchange.

> [!analogy] Real-world analogy: Catalogue numbers and shipping labels
> A catalogue assigns each item a number; a shipping system decides how that number appears on a label.
>
> **How it maps:** Unicode code points identify encoded elements, while Unicode encodings specify the code units or bytes used to carry scalar values.
>
> **Where it stops:** One user-perceived character can involve several code points; a code point does not imply a fixed number of bytes.

## Key takeaways
- A character set and its byte encoding answer different questions.
- Unicode scalar values exclude surrogate code points.
- UTF-32 uses one four-octet unit per scalar value.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
