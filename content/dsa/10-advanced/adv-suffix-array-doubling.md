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

Direct pattern searches scan the text for each query, typically taking O(n) work under their stated assumptions, where n is the text length. If the text is fixed and queries are many (a genome, a corpus, a code base), we can do better by indexing the text.

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

The search finds a range of suffix positions; reporting all matches adds work proportional to the number of results. Index construction and storage are paid before queries begin.

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

Each round doubles the number of covered initial characters, so there are O(log n) rounds. A comparison sort of the rank pairs gives O(n log² n) total time, as in this code. Radix sorting bounded integer ranks reduces each round to O(n), giving O(n log n) total time.

Specialised algorithms (SA-IS, DC3) achieve O(n) with a suitable bounded integer alphabet. Arbitrary comparison-based alphabet ordering has its own cost.

## Key takeaways

- Sorting suffix positions groups all occurrences of one pattern together.
- Prefix doubling ranks increasingly long prefixes through pairs of shorter ranks.

## Further reading
- [Suffix arrays and LCP — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
