---
id: lin-string-unicode-units
title: Bytes, code points and grapheme clusters
level: basic
minutes: 3
sourceLesson: lin-strings
summary: Byte length, code-unit length and visible-character length can differ.
---

A string represents text, but byte storage and visible characters are different layers. This unit follows the encoding from a byte representation through runtime indexing to grapheme clusters, so you can choose the length limit your application actually needs.

## Encoding basics

Computers store bytes, not letters. A **character encoding** maps characters to bytes.

- **ASCII** covers 128 characters (English letters, digits, punctuation) in 7 bits.
- **Unicode** assigns a number, a **code point**, to over 150,000 characters: `U+0041` is `A`, `U+00E9` is `é`, `U+1F600` is 😀.
- **UTF-8** stores each Unicode scalar value in 1 to 4 bytes; surrogate code points are excluded. ASCII characters take 1 byte, so plain ASCII text is valid UTF-8. It is the dominant encoding on the web and in files.
- **UTF-16** uses 2 bytes for most common characters and 4 bytes (a **surrogate pair**) for the rest, including most emoji.

```
char   code point  UTF-8 bytes  UTF-16 units
A      U+0041      1            1
é      U+00E9      2            1
€      U+20AC      3            1
😀     U+1F600     4            2
```

### What does "length" mean?

Different languages count different things:

```python
s = "café"
len(s)                  # 4 code points
len(s.encode("utf-8"))  # 5 bytes
len("😀")               # 1
```

In Java and JavaScript, `"😀".length()` / `"😀".length` is **2**, because they count UTF-16 code units. Slicing such a string in the wrong place splits a surrogate pair and produces garbage.

Even code points aren't what a reader thinks of as a character. `é` can be one code point (`U+00E9`) or two (`e` plus a combining accent `U+0301`). The two forms look identical but compare unequal unless you apply **Unicode normalisation** to both (Python's `unicodedata.normalize`). A flag emoji like 🇬🇧 is two code points. What users perceive as one character is a **grapheme cluster**.

### How runtimes store strings

- **CPython** (PEP 393) picks 1, 2 or 4 bytes per code point for each string, based on the widest character it contains. Every code point then has a fixed width, so `s[i]` stays O(1). One emoji in a long ASCII string makes the whole string 4 bytes per character.
- **Java** 9+ uses "compact strings": Latin-1 (1 byte per char) when possible, otherwise UTF-16.
- **Rust** `String` stores valid UTF-8. **Go strings** are arbitrary byte sequences, conventionally UTF-8 for text. Getting the *i*-th code point of an n-byte string means scanning from the start, O(n), which is why Rust doesn't let you write `s[i]` on a `String` and Go's `s[i]` gives you a byte.

## Key takeaways
- Byte length, code-unit length and visible-character length can differ.
- Runtime representation determines what an index means and costs.

## Further reading
- [PEP 393 — Flexible String Representation](https://peps.python.org/pep-0393/)
- [UTF-8 — Wikipedia](https://en.wikipedia.org/wiki/UTF-8)
- [The Absolute Minimum Every Software Developer Must Know About Unicode — Joel Spolsky](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
- [Python built-in types: text sequences](https://docs.python.org/3/library/stdtypes.html)
