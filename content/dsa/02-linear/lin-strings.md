---
id: lin-strings
title: Strings
level: basic
minutes: 11
summary: Strings as arrays of characters, why most languages make them immutable, what encodings do to length and indexing, why concatenating in a loop is quadratic, and the real cost of common string operations.
---

A string represents a sequence of text units. Many implementations use arrays, but indexing cost depends on which units are requested and how the string is represented. But strings come with two complications that trip up beginners and experienced engineers alike:

1. In most modern languages they are **immutable**: you can never change one, only make a new one.
2. A "character" is not as simple as it sounds. How many bytes it takes depends on the **encoding**.

Both have real performance and correctness consequences.

## Immutability

In Python, Java, JavaScript, C# and Go, a string object can never be modified after it is created.

```python
s = "hello"
s[0] = "H"      # TypeError: 'str' object
                # does not support item
                # assignment
s = "H" + s[1:] # builds a new string
```

Operations that look like modification (`upper()`, `replace()`, `+`) return an immutable string value and leave the original contents alone; an implementation may reuse an existing object when the result is unchanged. A variable can be re-pointed at a new string, but any other variable still pointing at the old one sees no change.

```python
s = "hello"
t = s
s += " world"
print(t)        # hello
```

C++ std::string and Rust String are mutable growable buffers with separate borrowed-view types, std::string_view and &str. C char arrays can be mutable but C does not provide those ownership/view types.

### Why make strings immutable?

- **Safe as hash keys.** A dict or HashMap stores a key in a bucket chosen by its hash. If the key could change, it would sit in the wrong bucket forever. Immutable strings can also **cache** their hash: Python and Java compute it once and store it.
- **Free sharing.** Many variables, threads or data structures can point at the same string with no copying and no locks, because nobody can change it.
- **Interning.** Identical literals can share one object. Java interns string literals; CPython interns many identifiers and short strings.
- **Security.** A checked string value cannot change through an alias. This does not prevent the file, permissions or other external resource named by it from changing between check and use.

Changing the text generally requires producing another value; allocation and copying may be optimized when observable immutability is preserved.

## Encoding basics

Computers store bytes, not letters. An **encoding** maps characters to bytes.

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

Even code points aren't what a reader thinks of as a character. `é` can be one code point (`U+00E9`) or two (`e` plus a combining accent `U+0301`). The two forms look identical but compare unequal unless you **normalise** them (Python's `unicodedata.normalize`). A flag emoji like 🇬🇧 is two code points. What users perceive as one character is a **grapheme cluster**.

### How runtimes store strings

- **CPython** (PEP 393) picks 1, 2 or 4 bytes per code point for each string, based on the widest character it contains. Every code point then has a fixed width, so `s[i]` stays O(1). One emoji in a long ASCII string makes the whole string 4 bytes per character.
- **Java 9+** uses "compact strings": Latin-1 (1 byte per char) when possible, otherwise UTF-16.
- **Rust String** stores valid UTF-8. **Go strings** are arbitrary byte sequences, conventionally UTF-8 for text. Getting the *i*-th code point means scanning from the start, O(n), which is why Rust doesn't let you write `s[i]` on a `String` and Go's `s[i]` gives you a byte.

## Concatenation cost

Because strings are immutable, `a + b` allocates a new string of length `len(a) + len(b)` and copies both in. That is O(len(a) + len(b)).

Now put it in a loop:

```python
result = ""
for word in words:   # n words
    result += word   # copies all of result
```

If each word has length k, iteration i copies about i·k characters. Total: k + 2k + ... + nk ≈ **k·n²/2**. That's quadratic. For 100,000 one-character pieces, about 5 billion character copies.

> [!note] CPython sometimes cheats
> CPython can extend `result` in place when nothing else references it, which often makes this loop fast in practice. It's an implementation detail: it disappears if another reference exists, and PEP 8 says not to rely on it. It is not a portable guarantee across Python implementations.

### The fix: collect, then join

Gather the pieces in a list (amortised O(1) appends), then join once. `join` measures the total length, allocates once, and copies each piece once: **O(number of pieces + total length)**.

```python
parts = []
for word in words:
    parts.append(word)
result = "".join(parts)
```

In Java, use `StringBuilder`, a mutable, growable character buffer (a dynamic array, so appending k units costs amortised O(k + 1)):

```java
StringBuilder sb = new StringBuilder();
for (String w : words) {
    sb.append(w);
}
String result = sb.toString();
```

> [!warning] The compiler won't save you in a loop
> `javac` turns a single expression like `a + b + c` into one efficient concatenation. But `s = s + w` inside a loop still builds a brand-new string on every iteration. The loop remains O(n²).

## Common operations and their complexity

For a string of length n (Python and Java, which store their length and support O(1) indexing):

| Operation | Cost | Note |
|---|---|---|
| `len(s)` | O(1) | Length is stored |
| `s[i]` | O(1) | Fixed-width units |
| `s[a:b]` | O(b − a) | Copies a new string |
| `a == b` | O(n) | Stops at first difference |
| `t in s` | O(n·m) worst | Usually much faster |
| `upper` | O(n) | Unicode case conversion |
| literal `split`, `replace` | Depends on search and output size | Replacement can expand the output |
| `"".join(parts)` | O(pieces + output length) | Must inspect empty pieces too |

A few details matter here:

- **C's `strlen` is O(n).** C strings are byte arrays ending in a zero byte, and the length is found by scanning for it. Writing `for (i = 0; i < strlen(s); i++)` makes the loop O(n²) unless the compiler hoists the call.
- **Slices copy.** In Python, `s[1:]` is a new string. Recursive functions that pass `s[1:]` down at each level copy O(n) per call: O(n²) total. Pass indices instead. Java's `substring` has also copied since Java 7u6; earlier versions shared the parent's array, which caused memory leaks when a tiny substring kept a huge string alive.
- **Substring search.** A naive search tries every start position, O(n·m) in the worst case. Library implementations use cleverer algorithms and are fast on typical text; CPython adopted the linear-time two-way algorithm for longer needles in Python 3.10. Linear-time algorithms such as KMP appear in a later module.
- **Hashing** is O(n) the first time, but Python and Java cache the result on the string object.

## Pitfalls in practice

- **Byte limits vs character limits.** A database column, HTTP header or SMS segment limited in bytes can overflow on text that looks short. Truncating UTF-8 at a byte boundary can slice a character in half and produce invalid data. Truncate on code points (or graphemes), then check the byte length.
- **Identity vs equality.** In Python, `a is b` asks "same object?", not "same text?". Interning makes it accidentally true for some literals and false for strings built at runtime. In Java, `==` on `String` compares references; use `.equals()`.
- **Repeated `replace` or `+` in hot paths.** Each creates a new string. Build once with a builder or `join`.
- **Reversing user-visible text.** `s[::-1]` reverses code points, which mangles combining accents and multi-code-point emoji.

## Key takeaways
- A string is an array of code units: O(1) indexing and length in Python and Java; O(n) `strlen` in C.
- Immutability makes strings safe to share and to use as hash keys, at the cost of copying on every change.
- UTF-8 uses 1–4 bytes per Unicode scalar value; Java and JavaScript lengths count UTF-16 units, so an emoji has length 2.
- `s += piece` in a loop is O(n²) in general. Use `"".join(list)` or `StringBuilder` for O(n).
- Slicing copies, so passing `s[1:]` down a recursion is quadratic; pass indices.

## Further reading
- [PEP 393 — Flexible String Representation](https://peps.python.org/pep-0393/)
- [UTF-8 — Wikipedia](https://en.wikipedia.org/wiki/UTF-8)
- [The Absolute Minimum Every Software Developer Must Know About Unicode — Joel Spolsky](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
- [StringBuilder — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html)
- [Python built-in types: text sequences](https://docs.python.org/3/library/stdtypes.html)
- [String interning — Wikipedia](https://en.wikipedia.org/wiki/String_interning)
