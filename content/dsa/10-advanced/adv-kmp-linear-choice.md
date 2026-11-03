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

The text index only moves forward. The matched length rises by at most one per text character. Each fallback lowers it by at least one, and it never becomes negative. Fallbacks therefore spend progress made earlier: one character can trigger several fallbacks, but the whole scan cannot have more fallbacks than earlier increases.

Searching takes O(n), and the same argument gives O(m) preprocessing for a pattern of length m. Total time is O(n + m), including repetitive inputs. The prefix table uses O(m) memory, excluding the returned match positions. The empty pattern matches at every text boundary.

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
> CPython's forward string search combines Boyer–Moore/Horspool-style skipping with a two-way algorithm, selecting between them based on input sizes and observed work. The two-way path has a linear worst-case bound.
> Benchmark the actual workload and implementation before deciding which algorithm is fastest.

## Key takeaways

- Every fallback spends an earlier increase in matched-border length.
- Choose deterministic matching when collision verification or stream access matters.

## Further reading
- [CPython’s forward string-search implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/stringlib/fastsearch.h)
- [Prefix function and KMP — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
