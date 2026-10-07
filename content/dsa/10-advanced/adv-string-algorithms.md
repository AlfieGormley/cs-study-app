---
id: adv-string-algorithms
title: String algorithms
level: advanced
minutes: 15
summary: Linear-time pattern matching with KMP, rolling hashes with Rabin–Karp, the Z-function, and an introduction to suffix arrays and LCP arrays for many-query string problems.
---

The naive way to find a pattern p (length m) in a text t (length n) tries every start position and compares character by character. That is O(n·m) in the worst case: searching for `aaaab` in a million `a`s does about five million comparisons and finds nothing.

The algorithms in this lesson avoid that waste in different ways. **KMP** and the **Z-function** reuse previous matches instead of restarting the search at every position. **Rabin–Karp** compares hashes instead of strings. **Suffix arrays** pre-process the text once so that many later queries are fast.

## The waste in naive matching

Suppose we search for `abab` and have matched `aba` before a mismatch:

```
text:    a b a c ...
pattern: a b a b
               ^ mismatch
```

Naive matching slides the pattern one place and starts again from scratch. But we already know the last three text characters were `aba`. The end of what we matched (`a`) is also a start of the pattern, so the next possible match can begin there, with one character already matched. Nothing before it can work.

KMP precomputes, for every prefix of the pattern, exactly this "how much can I keep?" number.

## KMP: the prefix function

For a pattern p, `pi[i]` is the length of the longest **proper prefix** of `p[0..i]` that is also a **suffix** of it. ("Proper" means not the whole string.) This is often called the failure function or border array.

```
p:    a b a b a c a
i:    0 1 2 3 4 5 6
pi:   0 0 1 2 3 0 1
```

For example, `p[0..4] = ababa` ends with `aba`, which is also how it starts, so `pi[4] = 3`.

```python
def prefix_function(p):
    pi = [0] * len(p)
    k = 0  # length of current border
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:
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
            k = pi[k - 1]  # allow overlaps
    return hits
```

`kmp_search("abababab", "abab")` returns `[0, 2, 4]`, including overlapping matches.

### Why it is linear

The text index i only moves forward. Each step raises k by at most 1, and each fallback lowers it by at least 1. k can never go below 0, so over the whole search the total number of fallbacks is at most n. Search is O(n), building `pi` is O(m), and the total is **O(n + m)** with O(m) auxiliary memory, excluding the returned list of match positions. The empty pattern matches at every text boundary.

> [!tip] A concatenation trick
> Compute the prefix function of `p + "#" + t`, where `#` appears in neither string. Every position where `pi` equals m is the end of a match. The separator stops a border from running past the pattern.

## Rabin–Karp: compare hashes, not strings

Treat a window of m characters as a number in base B, modulo a large prime M:

```
h(s) = s[0]·B^(m-1) + ... + s[m-1]·B^0
       (mod M)
```

Sliding the window one place removes the leading character and appends one. That is O(1) arithmetic, a **rolling hash**:

```python
def rabin_karp(t, p, B=256, M=10**9 + 7):
    n, m = len(t), len(p)
    if not m:
        return list(range(n + 1))
    if m > n:
        return []
    # weight of the first character
    hi = pow(B, m - 1, M)
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        ht = (ht * B + ord(t[i])) % M
    hits = []
    for i in range(n - m + 1):
        if hp == ht and t[i:i + m] == p:
            hits.append(i)
        if i + m < n:
            out = ord(t[i])
            inc = ord(t[i + m])
            ht = (ht - out * hi) % M
            ht = (ht * B + inc) % M
    return hits
```

Equal strings always have equal hashes, but different strings can **collide**. So a hash match is only a candidate, confirmed by a direct comparison. For this implementation, time is **O(n + m + mC)**, where C is the number of equal-hash candidates, including genuine matches. Repeated text and pattern characters can require Θ(n·m) verification even without collisions. Linear expected time needs assumptions controlling false positives and genuine matches.

> [!note] Content gap: collision probabilities
> No numeric collision probability is provided for the fixed public B and M above: a prime modulus alone does not justify a 1/M probability for arbitrary inputs.

Rabin–Karp's real strengths are elsewhere:

- **Many patterns at once**: group k equal-length patterns by hash and look up each window in expected O(1), plus verification of candidate patterns.
- **Substring equality in O(1)**: with prefix hashes of a string, their fingerprints can be compared after O(n) set-up. This is probabilistic equality unless verified. Hashing and binary search can give an expected O(n log n) Monte Carlo longest-repeated-substring algorithm under an appropriate random-hash model; collision checks add costs.
- **Content-defined chunking**: backup tools such as restic use rolling fingerprints to choose boundaries. Rsync instead searches at every offset for matches to fixed-size blocks of the basis file.

> [!warning] Hash collisions can be attacked
> With a fixed, public B and M, an adversary can build inputs that collide on purpose. Randomised fingerprints can reduce collision risk under a stated model, but fixed double hashing is not an adversarial guarantee. Verify candidates; use KMP or Z when deterministic linear bounds matter.

## The Z-function

`z[i]` is the length of the longest substring starting at i that is also a **prefix** of the whole string. By convention `z[0] = 0`.

```
s:  a a b x a a b
z:  0 1 0 0 3 1 0
```

`z[4] = 3` because `aab` starting at 4 matches the prefix `aab`, then the suffix reaches the end of the string.

The algorithm keeps the rightmost window `[l, r)` known to match a prefix. For a new i inside that window, the character run from i mirrors the run from `i - l`, so it can reuse `z[i - l]`, capped at the window's edge:

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while (i + z[i] < n
               and s[z[i]] == s[i + z[i]]):
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z
```

Each successful comparison in the inner loop pushes r to the right, and r never moves left, so the total work is O(n).

To search, compute z of `p + "$" + t`, choosing `$` absent from both strings: every position with `z[i] == m` is a match. The Z-function is often the simplest tool for "which suffixes match a prefix?" questions, such as finding a string's period.

## KMP vs Rabin–Karp vs Z

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

## Suffix arrays: pre-process the text once

The algorithms above take O(n) per query. If the text is fixed and queries are many (a genome, a corpus, a code base), we can do better by indexing the text.

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

Every occurrence of a pattern is a prefix of some suffix. Because the suffixes are sorted, all suffixes starting with p form one **contiguous block**, which two binary searches find in **O(m log n)**. Searching `ana` finds the block `ana`, `anana`: occurrences at 3 and 1.

### Building it

Sorting the n suffixes directly costs O(n log n) comparisons of up to n characters each, O(n² log n) in the worst case. **Prefix doubling** sorts by the first 1, 2, 4, 8... characters. The rank of a suffix by its first 2k characters is the pair (rank of first k, rank of the k after that), so each round is a sort of integer pairs:

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
            new[b] = new[a] + diff
        rank = new
        # stop once all ranks are distinct
        if rank[sa[-1]] == n - 1:
            return sa
        k *= 2
```

There are at most about log2(n) rounds, each with an O(n log n) sort, so this is O(n log² n). Radix-sorting the pairs gives O(n log n), and specialised algorithms (SA-IS, DC3) achieve O(n) with a suitable bounded integer alphabet. Arbitrary comparison-based alphabet ordering has its own cost.

### The LCP array

The **LCP array** stores, for each adjacent pair in the suffix array, the length of their longest common prefix. For banana, with `lcp[0] = 0` by convention:

```
sa:  5    3     1      0       4   2
     a    ana   anana  banana  na  nana
lcp: 0    1     3      0       0   2
```

Kasai's algorithm builds it in O(n). The LCP array turns many problems into array scans:

- **Longest repeated substring**: the maximum LCP value. For banana that is 3 (`ana`).
- **Number of distinct substrings**: n(n+1)/2 minus the sum of the LCP array. For banana: 21 − 6 = 15.
- **Longest common substring** of two strings: build over `a + "#" + b` with `#` absent from both inputs, and take the largest LCP between adjacent suffixes from different strings.

### Suffix arrays vs suffix trees

A **suffix tree** is a compressed trie of all suffixes. It can answer the same queries, and builds in O(n) with Ukkonen's algorithm for a constant-size alphabet and constant-time edge lookup. Space overhead depends on node representation; no universal bytes-per-character estimate is supplied without measurement. A suffix array is n integers. Together with the LCP array it can simulate most suffix-tree algorithms, which is why bioinformatics tools favour suffix arrays and the related **FM-index** (built on the Burrows–Wheeler transform, as in the BWA and Bowtie read aligners).

## Pitfalls

- **Forgetting overlaps in KMP**: after a match, set `k = pi[k - 1]`, not 0, or you miss overlapping occurrences.
- **Negative modulo**: in C or Java, `(h - x) % M` can be negative. For positive M, Python's `%` returns a non-negative result, which hides this bug until you port the code.
- **Trusting a hash match**: without the final comparison, Rabin–Karp is a probabilistic algorithm that can report false positives.
- **Separators that occur in the input**: the `#` in `p + "#" + t` must be a character neither string contains.
- **Quadratic suffix sorting**: `sorted(range(n), key=lambda i: s[i:])` is fine for tests but builds O(n²) characters of slices.

## Key takeaways
- The prefix function stores, for each prefix, its longest proper border. KMP uses it to avoid re-reading text, giving O(n + m) worst case.
- Rabin–Karp's rolling hash updates in O(1) per window. Exact matching needs verification; all-occurrences cost includes O(m) for every candidate, even a genuine match.
- The Z-function gives, for each position, how far the string matches its own prefix, in O(n).
- A suffix array sorts all suffixes; pattern occurrences form one block found by binary search in O(m log n).
- The LCP array turns repeated-substring and distinct-substring questions into simple scans.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
