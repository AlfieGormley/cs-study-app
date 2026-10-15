---
id: adv-lcp-substring-indexes
title: LCP arrays and indexed substring questions
level: advanced
minutes: 3
summary: Adjacent longest-common-prefix values expose repeated substrings.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

### The LCP array

The **LCP array** stores, for each adjacent pair in the suffix array, the length of their longest common prefix. For banana, with `lcp[0] = 0` by convention:

```
sa:  5    3     1      0       4   2
     a    ana   anana  banana  na  nana
lcp: 0    1     3      0       0   2
```

Kasai's algorithm builds it in O(n), where n is the string length. The LCP array turns many problems into array scans:

- **Longest repeated substring**: the maximum LCP value. For banana that is 3 (`ana`).
- **Number of distinct substrings**: every substring is a prefix of some suffix, and each suffix's first lcp characters were already counted by its sorted neighbour:

```formula
D = n(n + 1) / 2 − Σ lcp[k]
D = 6 × 7 / 2 − (0 + 1 + 3 + 0 + 0 + 2)
D = 21 − 6 = 15
where
D: the number of distinct (different) non-empty substrings
n: the length of the string, 6 for banana
n(n + 1) / 2: the total number of substrings counted with repeats: n of length 1, n − 1 of length 2, and so on down to 1 of length n
lcp[k]: the LCP value at position k of the suffix array
k: a position in the suffix array, 0 to n − 1
Σ: the sum over every position k
In words: count every substring, then subtract the repeats, which are exactly the prefixes each sorted suffix shares with the one before it.
```

- **Longest common substring** of two strings: build over `a + "#" + b` with `#` absent from both inputs, and take the largest LCP between adjacent suffixes from different strings.

### Suffix arrays vs suffix trees

A **suffix tree** is a compressed trie of all suffixes. It can answer the same queries, and builds in O(n) with Ukkonen's algorithm for a constant-size alphabet and constant-time edge lookup. Space overhead depends on node representation; no universal bytes-per-character estimate is supplied without measurement. A suffix array is n integers. Together with the LCP array it can simulate most suffix-tree algorithms, which is why bioinformatics tools favour suffix arrays and the related **FM-index** (built on the Burrows–Wheeler transform, as in the BWA and Bowtie read aligners).

## Pitfalls

- Forgetting overlaps in KMP: after a match, set `k = pi[k - 1]`, not 0, or you miss overlapping occurrences.
- Trusting a hash match: without the final comparison, Rabin–Karp is a probabilistic algorithm that can report false positives.
- **Separators that occur in the input**: the `#` in `p + "#" + t` must be a character neither string contains.
- Quadratic suffix sorting: `sorted(range(n), key=lambda i: s[i:])` is fine for tests but builds O(n²) characters of slices.

## Key takeaways

- Adjacent longest-common-prefix values expose repeated substrings.
- Subtract those repeated prefixes from the total substring count to count distinct substrings.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
