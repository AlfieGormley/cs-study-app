---
id: adv-kmp-linear-choice
title: Why KMP is linear and when to use it
level: advanced
minutes: 3
summary: Every fallback spends an earlier increase in matched-border length.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

### Why it is linear

The text index i only moves forward. Each step raises k by at most 1, and each fallback lowers it by at least 1. k can never go below 0, so it cannot fall more often than it rose:

```formula
F ≤ R ≤ n
T_search = O(n + F) = O(n)
T_build = O(m)
T = O(n + m)
where
F: the total number of fallbacks (k = pi[k − 1] steps) during the search
R: the total number of times k rises by 1, at most once per text character
n: the length of the text, in characters
m: the length of the pattern, in characters
k: the length of the current partial match
T_search: the time for the search loop
T_build: the time to build the prefix function
T: the total time
O(f): grows at most in proportion to f
≤: is at most
In words: every fallback undoes an earlier rise, and there is at most one rise per text character, so the whole search is linear in the text plus the pattern.
```

For a 1,000,000-character text and a 100-character pattern that is at most about 2,000,000 loop steps plus 200 for the table, however repetitive the input. Memory is O(m) for `pi`, excluding the returned list of match positions. The empty pattern matches at every text boundary.

> [!tip] A concatenation trick
> Compute the prefix function of `p + "#" + t`, where `#` appears in neither string. Every position where `pi` equals m is the end of a match. The separator stops a border from running past the pattern.

## KMP vs Rabin–Karp vs Z

Here n is the text length, m the pattern length and C the number of Rabin–Karp hash candidates.

| | Time | Best for |
|---|---|---|
| KMP | O(n + m) worst | Streams, one pattern |
| Rabin–Karp | O(n + m + mC), C candidates | Many patterns, substring hashing |
| Z | O(n + m) worst | Prefix-matching questions |

KMP processes the text one character at a time and never looks back, so it works on a stream. The Z trick needs the whole text concatenated in memory.

> [!note] What real libraries do
> CPython's forward string search combines Boyer–Moore/Horspool-style skipping with a two-way algorithm and adaptive selection based on input sizes and observed work. The two-way path has a linear worst-case bound.
>
> Content gap: no universal fastest-algorithm ranking is given; that requires reproducible benchmarks for the workload and implementation.

## Key takeaways

- Every fallback spends an earlier increase in matched-border length.
- Choose deterministic matching when collision verification or stream access matters.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
