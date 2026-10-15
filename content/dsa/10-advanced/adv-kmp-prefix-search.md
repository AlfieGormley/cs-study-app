---
id: adv-kmp-prefix-search
title: KMP borders, prefix tables and overlapping matches
level: advanced
minutes: 3
summary: The prefix function stores the longest proper border of each prefix.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## KMP: the prefix function

For a pattern p, `pi[i]` is the length of the longest **proper prefix** of `p[0..i]` that is also a **suffix** of it. ("Proper" means not the whole string.) A string that is both a proper prefix and a suffix is called a **border**, so `pi` is often called the failure function or border array. As a formula:

```formula
pi[i] = max L   such that   0 ≤ L ≤ i
  and p[0..L−1] = p[i−L+1..i]
pi[4] = 3   as p[0..2] = "aba" = p[2..4]
where
p: the pattern, with characters numbered from 0
i: a position in the pattern, from 0 to m − 1
m: the length of the pattern
pi[i]: the prefix-function value at position i, a whole number from 0 to i
L: a candidate border length, in characters
max: the largest value that satisfies the conditions (0 if only L = 0 does)
p[a..b]: the characters of p from position a to position b, both included
≤: is at most
In words: pi[i] is the length of the longest piece that both starts the pattern and ends at position i, without being the whole of p[0..i].
```

```
p:    a b a b a c a
i:    0 1 2 3 4 5 6
pi:   0 0 1 2 3 0 1
```

For example, `ababa` (positions 0 to 4) ends with `aba`, which is also how it starts, so the value at position 4 is 3: the last line of the block. The border must be *proper*, so `ababa` itself does not count.

```python
def prefix_function(p):
    pi = [0] * len(p)
    k = 0  # length of current border
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:
            # Try the next shorter known
            # border.
            k = pi[k - 1]   # fall back
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi
```

When `p[i]` does not extend the current border of length k, the next candidate border is the border of that border, `pi[k - 1]`. The loop keeps falling back until something extends or k reaches 0.

### Searching with it

The search uses the same loop, with the text in place of the pattern:

```python
def kmp_search(text, p):
    if not p:
        return list(range(len(text) + 1))
    pi = prefix_function(p)
    hits, k = [], 0
    for i, c in enumerate(text):
        while k > 0 and c != p[k]:
            k = pi[k - 1]
        if c == p[k]:
            k += 1
        if k == len(p):
            hits.append(i - k + 1)
            # Keep a border for overlapping
            # matches.
            k = pi[k - 1]  # allow overlaps
    return hits
```

`kmp_search("abababab", "abab")` returns `[0, 2, 4]`, including overlapping matches.

## Key takeaways

- The prefix function stores the longest proper border of each prefix.
- After a full match, falling back to its border retains overlapping matches.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
- [Knuth, Morris and Pratt’s original paper](https://www.cs.jhu.edu/~misha/Spring23/Knuth77.pdf)
