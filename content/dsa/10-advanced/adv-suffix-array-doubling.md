---
id: adv-suffix-array-doubling
title: Suffix arrays and prefix doubling
level: advanced
minutes: 4
summary: Sorting suffix positions groups all occurrences of one pattern together.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

## Suffix arrays: pre-process the text once

The algorithms above take O(n) per query, where n is the text length. If the text is fixed and queries are many (a genome, a corpus, a code base), we can do better by indexing the text.

The **suffix array** of s is the list of starting positions of all its suffixes, in sorted order:

```
s = "banana"
i  suffix        sorted:  sa  suffix
0  banana                 5   a
1  anana                  3   ana
2  nana                   1   anana
3  ana                    0   banana
4  na                     4   na
5  a                      2   nana

sa = [5, 3, 1, 0, 4, 2]
```

Every occurrence of a pattern is a prefix of some suffix. Because the suffixes are sorted, all suffixes starting with p form one contiguous range, which two binary searches find in **O(m log n)**, where n is the text length and m the pattern length: each binary-search comparison checks at most the pattern’s length. Searching `ana` finds the block `ana`, `anana`: occurrences at 3 and 1.

```formula
C ≤ 2m⌈log_2(n + 1)⌉
C ≤ 2 × 3 × 3 = 18
where
C: an upper bound on character comparisons in the two boundary searches, excluding reporting matches
n: the non-empty text length in characters, six for banana
m: the non-empty pattern length, three for ana
log_2(n + 1): the base-two logarithm of one more than the suffix count
⌈ ⌉: ceiling, rounding up to a whole number
≤: is at most
In words: each of two boundary searches takes at most three comparisons of three characters each in this small example; longer texts increase the number of binary-search rounds logarithmically.
```

### Building it

Sorting the n suffixes of an n-character string directly costs O(n log n) comparisons of up to n characters each, O(n² log n) in the worst case (for example, a string of all `a`s, where suffixes share long prefixes). **Prefix doubling** sorts by the first 1, 2, 4, 8... characters. The rank of a suffix by its first 2k characters is the pair (rank of first k, rank of the k after that), so each round is a sort of integer pairs:

```python
def suffix_array(s):
    n = len(s)
    if not n:
        return []
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        def key(i):
            j = i + k
            nxt = rank[j] if j < n else -1
            return (rank[i], nxt)
        sa.sort(key=key)
        new = [0] * n
        for j in range(1, n):
            a, b = sa[j - 1], sa[j]
            diff = key(a) != key(b)
            # Equal rank-pairs keep equal
            # new ranks.
            new[b] = new[a] + diff
        rank = new
        # stop once all ranks are distinct
        if rank[sa[-1]] == n - 1:
            return sa
        # The next round ranks twice the
        # prefix.
        k *= 2
```

Each round doubles the number of characters compared, so the rounds run out quickly:

```formula
R ≤ ⌈log_2(n)⌉
T_cmp = R O(n log(n)) = O(n log(n)^2)
T_radix = R O(n) = O(n log(n))
R ≤ ⌈log_2(10^6)⌉ = 20
where
R: the number of doubling rounds, for a string of at least 2 characters
n: the length of the string, in characters
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
log(n): the logarithm of n; the base only changes a constant factor
log(n)^2: log(n) multiplied by itself, often written log² n
⌈ ⌉: ceiling: round up to the nearest whole number
T_cmp: the total time when each round uses a comparison sort of the pairs
T_radix: the total time when each round uses a radix sort of the pairs
O(f): grows at most in proportion to f
≤: is at most
In words: after about log_2(n) doublings every suffix is ranked by at least n characters, so the cost is that many rounds times the cost of one sort.
```

For a million-character string that is at most 20 rounds. Specialised algorithms (SA-IS, DC3) achieve O(n) with a suitable bounded integer alphabet. Arbitrary comparison-based alphabet ordering has its own cost.

## Key takeaways

- Sorting suffix positions groups all occurrences of one pattern together.
- Prefix doubling ranks increasingly long prefixes through pairs of shorter ranks.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
