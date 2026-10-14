---
id: lin-string-operation-pitfalls
title: String operations, slices and text pitfalls
level: basic
minutes: 3
sourceLesson: lin-strings
summary: Repeated slices can make an otherwise linear recursion quadratic.
---

For these bounds, n is the string length in the units the runtime indexes, and basic element comparisons have constant cost. The earlier encoding unit explains why these units are not necessarily bytes or visible characters. Runtime shortcuts can avoid copying a whole unchanged string; bounds here describe general proper slices and changed results.

## Common operations and their complexity

For a string `s` of length n (Python and Java, which store their length and support O(1) indexing). In the table, `a` and `b` in `s[a:b]` are the start and end positions of the slice, and m is the length of the string `t` being searched for:

| Operation | Cost | Note |
|---|---|---|
| `len(s)` | O(1) | Length is stored |
| `s[i]` | O(1) | Fixed-width units |
| `s[a:b]` | O(b − a + 1) | Proper nonempty slices copy; unchanged whole slices may reuse |
| `a == b` | O(n) | Stops at first difference |
| `t in s` | O(n·m) worst | Usually much faster |
| `upper` | O(n + 1) | Unicode case conversion; output may expand |
| literal `split`, `replace` | Depends on search and output size | Replacement can expand the output |
| `"".join(parts)` | O(pieces + output length) | Must inspect empty pieces too |

A few details matter here:

- **C's `strlen` is O(n).** C strings are byte arrays ending in a zero byte, and the length is found by scanning for it. Writing `for (i = 0; i < strlen(s); i++)` makes the loop O(n²) unless the compiler hoists the call.
- **Slices copy.** An ordinary nonempty proper CPython slice such as `s[1:]` generally copies its selected characters; empty and full unchanged slices can reuse objects. Recursive functions that pass `s[1:]` down at each level copy O(n) per call: O(n²) total. Pass indices instead. Java's `substring` has also copied since Java 7u6; earlier versions shared the parent's array, which caused memory leaks when a tiny substring kept a huge string alive.
- **Substring search.** A naive search tries every start position, O(n·m) in the worst case. Library implementations use cleverer algorithms and are fast on typical text; CPython adopted the linear-time two-way algorithm for longer needles in Python 3.10. Linear-time algorithms such as KMP appear in a later module.
- **Hashing** is O(n) the first time, but Python and Java cache the result on the string object.

## Pitfalls in practice

- **Byte limits vs character limits.** A database column, HTTP header or SMS segment limited in bytes can overflow on text that looks short. Truncating UTF-8 at a byte boundary can slice a character in half and produce invalid data. Truncate on code points (or graphemes), then check the byte length.
- **Identity vs equality.** In Python, `a is b` asks "same object?", not "same text?". Interning makes it accidentally true for some literals and false for strings built at runtime. In Java, `==` on `String` compares references; use `.equals()`.
- **Repeated `replace` or `+` in hot paths.** Each creates a new string. Build once with a builder or `join`.
- **Reversing user-visible text.** `s[::-1]` reverses code points, which mangles combining accents and multi-code-point emoji.

## Key takeaways
- Repeated slices can make an otherwise linear recursion quadratic.
- Use text equality and preserve encoding or grapheme boundaries.

## Further reading
- [Python built-in types: text sequences](https://docs.python.org/3/library/stdtypes.html)
