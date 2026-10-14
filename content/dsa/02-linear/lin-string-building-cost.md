---
id: lin-string-building-cost
title: Building strings without repeated copying
level: basic
minutes: 4
sourceLesson: lin-strings
summary: Repeated full-copy concatenation sums growing prefixes.
---

An immutable string cannot be observably changed through an alias. A full-copy concatenation creates the combined value; repeat that operation and you repeatedly copy earlier prefixes. The cost model below explicitly excludes optimisations that extend an unshared buffer in place.

## Concatenation cost

In the full-copy model, joining two immutable strings creates a value with space for both inputs and copies their code units. Observable immutability itself does not forbid optimising an unshared internal buffer; the CPython caveat below matters:

```formula
W ∝ L_a + L_b
where
W: copying work to construct the joined string, in copied code units
L_a: the left input’s code-unit length
L_b: the right input’s code-unit length
∝: proportional to: doubling the right-hand side roughly doubles the cost
In words: joining two strings costs time in proportion to their combined length, because both are copied in full.
```

So `"abc" + "de"` copies 5 characters, and appending one character to a 1,000-character string copies 1,001. That is linear in the combined input lengths.

Now put it in a loop:

```python
result = ""
for word in words:   # n words
    result += word   # full-copy model
```

Each pass copies everything built so far plus the new word, so the cost of each pass grows. Adding up all the passes gives an arithmetic series:

```formula
total = k + 2k + ... + nk
total = kn(n + 1) / 2
total ≈ kn^2 / 2
where
total: the number of characters copied over the whole loop
n: the number of words joined
k: the length of each word, in characters (assumed all equal)
≈: approximately equal to; for large n, n + 1 is about the same as n
In words: pass i copies about i words' worth of characters, so the total grows with the square of the number of words.
```

That's quadratic: **O(n²)** for a fixed word length. For 100,000 one-character pieces, the formula predicts about five billion character copies.

> [!note] CPython sometimes cheats
> CPython can extend `result` in place when nothing else references it, which often makes this loop fast in practice. It's an implementation detail: it disappears if another reference exists, and PEP 8 says not to rely on it. It is not a portable guarantee across Python implementations.

### The fix: collect, then join

Gather the pieces in a list (amortised O(1) appends), then join once. `join` measures the total length, allocates once, and copies each piece once: **O(number of pieces + total length)**.

```python
parts = []
for word in words:
    # Collect pieces without copying
    # prefixes.
    parts.append(word)
# Build the complete text in one pass.
result = "".join(parts)
```

In Java, use `StringBuilder`, a mutable, growable character buffer (a dynamic array, so appending k units costs amortised O(k + 1)):

```java
StringBuilder sb = new StringBuilder();
for (String w : words) {
    // Append into the growable builder.
    sb.append(w);
}
// Produce the final immutable text value.
String result = sb.toString();
```

> [!warning] The compiler won't save you in a loop
> `javac` turns a single expression like `a + b + c` into one efficient concatenation. But `s = s + w` inside a loop still creates growing immutable results. For n equal-sized pieces and no cross-iteration optimisation, the loop remains O(n²).

## Key takeaways
- Repeated full-copy concatenation sums growing prefixes.
- Collect pieces and join once, or use a mutable builder.

## Further reading
- [StringBuilder — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html)
- [Python built-in types: text sequences](https://docs.python.org/3/library/stdtypes.html)
- [PEP 8 — string-concatenation portability](https://peps.python.org/pep-0008/)
