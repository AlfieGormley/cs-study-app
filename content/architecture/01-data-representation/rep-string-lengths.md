---
id: rep-string-lengths
title: Bytes, code points and grapheme clusters
level: intermediate
minutes: 3
summary: String length depends on the unit a language counts.
sourceLesson: rep-text-encoding
---

Before enforcing a text limit, decide what it counts: storage bytes, code units, code points or user-perceived characters.

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

## Key takeaways
- String length depends on the unit a language counts.
- User-perceived characters can contain several code points.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
