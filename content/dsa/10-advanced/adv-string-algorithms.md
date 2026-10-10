---
id: adv-string-algorithms
title: String algorithms
level: advanced
minutes: 15
summary: Linear-time pattern matching with KMP, rolling hashes with Rabin–Karp, the Z-function, and an introduction to suffix arrays and LCP arrays for many-query string problems.
---

The naive way to find a pattern p (length m) in a text t (length n) tries every start position and compares character by character. In the worst case every start position compares the whole pattern:

```formula
C_naive ≤ (n − m + 1) × m = O(n × m)
C_naive ≈ (10^6 − 5 + 1) × 5 ≈ 5 × 10^6
where
C_naive: the number of character comparisons naive matching makes
n: the length of the text t, in characters
m: the length of the pattern p, in characters
n − m + 1: the number of places the pattern can start inside the text
O(f): "grows at most in proportion to f", ignoring constant factors
≤: is at most
≈: approximately equal to
In words: naive matching can compare up to m characters at each of about n start positions, so its cost grows with the product of the two lengths.
```

The second line is the classic bad case: searching for `aaaab` (m = 5) in a million `a`s matches four `a`s and fails on the `b` at every start, about five million comparisons, and finds nothing. When mismatches come early (typical English text), naive matching is much closer to n comparisons.

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

For a pattern p, `pi[i]` is the length of the longest **proper prefix** of `p[0..i]` that is also a **suffix** of it. ("Proper" means not the whole string.) A string that is both a proper prefix and a suffix is called a **border**, so `pi` is often called the failure function or border array. As a formula:

```formula
pi[i] = max L   such that   L ≤ i
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

## Rabin–Karp: compare hashes, not strings

Treat a window of m characters as a number in base B, modulo a large prime M:

```formula
h(s) = (s_0 × B^{m−1} + s_1 × B^{m−2}
  + … + s_{m−1} × B^0) mod M
h("123") = 1 × 10^2 + 2 × 10 + 3 = 123
where
s: the window of m characters being hashed
s_0, s_1, s_{m−1}: the character codes of the window's first, second and last characters (for example `ord('a')` = 97 in Python)
m: the window length, equal to the pattern length, in characters
B: the base, a whole number at least as big as the alphabet; 256 in the code below, 10 in the toy last line
B^0: B to the power 0, which is 1
M: the modulus, a large prime such as 10^9 + 7
mod: the remainder after dividing by M, so the hash is always 0 to M − 1
h(s): the hash value of the window
…: the terms in between, one per character
In words: read the window as a number written in base B, with the first character as the most significant digit, and keep only the remainder after dividing by M.
```

The last line is a toy example: with B = 10, digits as characters and M large enough to ignore, the window `123` hashes to the number 123.

Sliding the window one place removes the leading character and appends one. That is O(1) arithmetic, a **rolling hash**:

```formula
h_new = ((h_old − c_out × B^{m−1}) × B
  + c_in) mod M
h_new = (123 − 1 × 10^2) × 10 + 4 = 234
where
h_old: the hash of the current window
h_new: the hash of the window one place to the right
c_out: the character code leaving on the left
c_in: the character code entering on the right
B: the base
m: the window length
B^{m−1}: the weight of the leading character, precomputed once (`hi` in the code)
M: the prime modulus
mod: the remainder after dividing by M
In words: subtract the leading character's contribution, shift everything up one place by multiplying by B, and add the new character as the lowest digit.
```

In the toy example, sliding from `123` to `234` removes 1 × 100, shifts 23 to 230 and adds 4. Real code does each step modulo M so the numbers never grow, and must keep the subtraction non-negative (see Pitfalls).

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

Equal strings always have equal hashes, but different strings can **collide**. So a hash match is only a candidate, confirmed by a direct comparison. For this implementation the time is:

```formula
T = O(n + m + m × C)
C_max = n − m + 1
T = Θ(n × m)   if C = C_max
m × C ≈ 3 × 10^6
where
T: the running time of `rabin_karp`
n: the length of the text, in characters
m: the length of the pattern, in characters
C: the number of windows whose hash equals the pattern's hash, including genuine matches; each costs an m-character comparison
C_max: the most candidates possible: one per window position
≈: approximately equal to
O(f): grows at most in proportion to f
Θ(f): grows exactly in proportion to f, up to constant factors
In words: hashing is linear, but every candidate costs a full m-character check, so many candidates make the algorithm as slow as naive matching.
```

The last line is a worked example: searching `aaa` (a 3-character pattern) in a million `a`s gives about a million genuine matches, so the checks alone cost about three million comparisons. Repeated text and pattern characters can require Θ(n·m) verification even without collisions. Linear expected time needs assumptions controlling false positives and genuine matches.

> [!note] Content gap: collision probabilities
> No numeric collision probability is provided for the fixed public B and M above: a prime modulus alone does not justify a 1/M probability for arbitrary inputs.

Rabin–Karp's real strengths are elsewhere:

- **Many patterns at once**: group k equal-length patterns by hash and look up each window in expected O(1), plus verification of candidate patterns.
- **Substring equality in O(1)**: with prefix hashes of a string of length n, any two substrings' fingerprints can be compared after O(n) set-up (formula below). This is probabilistic equality unless verified. Hashing and binary search can give an expected O(n log n) Monte Carlo longest-repeated-substring algorithm under an appropriate random-hash model; collision checks add costs.
- **Content-defined chunking**: backup tools such as restic use rolling fingerprints to choose boundaries. Rsync instead searches at every offset for matches to fixed-size blocks of the basis file.

The prefix-hash trick stores the hash of every prefix, then cuts any substring's hash out of two of them:

```formula
H[0] = 0
H[j + 1] = (H[j] × B + s_j) mod M
h(s[i..j)) = (H[j] − H[i] × B^{j−i}) mod M
h(s[1..4)) = 5123 − 5 × 10^3 = 123
where
s: the string, with characters numbered from 0
s_j: the character code at position j
H[j]: the hash of the first j characters of s
i, j: the start (included) and end (excluded) positions of a substring
s[i..j): the substring from position i up to but not including j
B: the base
B^{j−i}: j − i copies of B multiplied together (precomputed for every power)
M: the prime modulus
mod: the remainder after dividing by M, taken as 0 to M − 1
h: the hash of the substring
In words: a substring's hash is the longer prefix's hash minus the shorter prefix's hash shifted up by the substring's length.
```

The last line is a toy example with B = 10, digits as characters and M large enough to ignore: for the string `5123`, the prefix hashes are 5 (first character) and 5123 (all four), so the substring `123` hashes to 123, exactly what hashing it directly gives. Each comparison is O(1) once the H array and powers of B are precomputed in O(n).

> [!warning] Hash collisions can be attacked
> With a fixed, public B and M, an adversary can build inputs that collide on purpose. Randomised fingerprints can reduce collision risk under a stated model, but fixed double hashing is not an adversarial guarantee. Verify candidates; use KMP or Z when deterministic linear bounds matter.

## The Z-function

`z[i]` is the length of the longest substring starting at i that is also a **prefix** of the whole string. By convention `z[0] = 0`.

```formula
z[i] = max L   such that
  s[0..L−1] = s[i..i+L−1]
z[4] = 3   as s[0..2] = "aab" = s[4..6]
where
s: the string, with characters numbered from 0
n: the length of s
i: a position in s, from 1 to n − 1
z[i]: the Z-value at position i, a whole number of characters
L: a candidate match length
max: the largest value that satisfies the condition
s[a..b]: the characters of s from position a to position b, both included
In words: z[i] counts how many characters, starting at i, agree with the start of the string.
```

```
s:  a a b x a a b
z:  0 1 0 0 3 1 0
```

In the table, the value 3 at position 4 is because `aab` starting at 4 matches the prefix `aab`, then the suffix reaches the end of the string.

The algorithm keeps the rightmost window `[l, r)` known to match a prefix. For a new i inside that window, the character run from i mirrors the run from i − l, so it can reuse the earlier value, capped at the window's edge:

```formula
z[i] ≥ min(r − i, z[i − l])   if i < r
z[5] ≥ min(7 − 5, z[1]) = min(2, 1) = 1
where
i: the position being computed
l, r: the start (included) and end (excluded) of the rightmost known window, so s[l..r−1] equals s[0..r−l−1]
z[i]: the Z-value at position i
z[i − l]: the Z-value at the mirrored position inside the prefix, already computed
min: the smaller of the two values
≥: is at least
In words: inside a known matching window, position i agrees with the prefix at least as far as its mirror image did, but no further than the window's edge without checking.
```

The last line is the worked example for `aabxaab`: after position 4 the window runs from 4 up to 7, so position 5 mirrors position 1 and starts at 1. One more comparison (`a` against `b`) fails, so the value stays 1, with no wasted comparisons.

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

Each successful comparison in the inner loop pushes r to the right, and r never moves left, so the total work is O(n), where n is the length of s.

To search, compute z of `p + "$" + t`, choosing `$` absent from both strings: every position with `z[i] == m` is a match. The Z-function is often the simplest tool for "which suffixes match a prefix?" questions, such as finding a string's period.

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

Every occurrence of a pattern is a prefix of some suffix. Because the suffixes are sorted, all suffixes starting with p form one **contiguous block**, which two binary searches find in **O(m log n)**, where n is the text length and m the pattern length: each of about log_2(n) binary-search steps compares up to m characters. Searching `ana` finds the block `ana`, `anana`: occurrences at 3 and 1.

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
            new[b] = new[a] + diff
        rank = new
        # stop once all ranks are distinct
        if rank[sa[-1]] == n - 1:
            return sa
        k *= 2
```

Each round doubles the number of characters compared, so the rounds run out quickly:

```formula
R ≤ ⌈log_2(n)⌉
T_cmp = R × O(n × log(n)) = O(n × log(n)^2)
T_radix = R × O(n) = O(n × log(n))
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
D = n × (n + 1) / 2 − Σ lcp[k]
D = 6 × 7 / 2 − (0 + 1 + 3 + 0 + 0 + 2)
D = 21 − 6 = 15
where
D: the number of distinct (different) non-empty substrings
n: the length of the string, 6 for banana
n × (n + 1) / 2: the total number of substrings counted with repeats: n of length 1, n − 1 of length 2, and so on down to 1 of length n
lcp[k]: the LCP value at position k of the suffix array
k: a position in the suffix array, 0 to n − 1
Σ: the sum over every position k
In words: count every substring, then subtract the repeats, which are exactly the prefixes each sorted suffix shares with the one before it.
```

- **Longest common substring** of two strings: build over `a + "#" + b` with `#` absent from both inputs, and take the largest LCP between adjacent suffixes from different strings.

### Suffix arrays vs suffix trees

A **suffix tree** is a compressed trie of all suffixes. It can answer the same queries, and builds in O(n) with Ukkonen's algorithm for a constant-size alphabet and constant-time edge lookup. Space overhead depends on node representation; no universal bytes-per-character estimate is supplied without measurement. A suffix array is n integers. Together with the LCP array it can simulate most suffix-tree algorithms, which is why bioinformatics tools favour suffix arrays and the related **FM-index** (built on the Burrows–Wheeler transform, as in the BWA and Bowtie read aligners).

## Pitfalls

- **Forgetting overlaps in KMP**: after a match, set `k = pi[k - 1]`, not 0, or you miss overlapping occurrences.
- **Negative modulo**: in C or Java, `(h - x) % M` can be negative. For positive M, Python's `%` returns a non-negative result, which hides this bug until you port the code. The portable fix adds M back:

```formula
r = ((a mod M) + M) mod M
r_C = (3 − 10) mod 11 = −7
r = (−7 + 11) mod 11 = 4
where
a: the number being reduced, possibly negative after a subtraction such as h − x
M: the positive modulus, 11 in the example
mod: the remainder after dividing by M; in C and Java it takes the sign of a, so it can be negative
r: the result, always between 0 and M − 1
r_C: the result C or Java's `%` gives for the example, which is negative
In words: if the remainder comes out negative, adding M once moves it into the range 0 to M − 1 without changing which remainder class it is in.
```

Both −7 and 4 leave the same remainder class (they differ by exactly 11), but only 4 equals a correctly computed hash.
- **Trusting a hash match**: without the final comparison, Rabin–Karp is a probabilistic algorithm that can report false positives.
- **Separators that occur in the input**: the `#` in `p + "#" + t` must be a character neither string contains.
- **Quadratic suffix sorting**: `sorted(range(n), key=lambda i: s[i:])` is fine for tests but builds O(n²) characters of slices.

## Key takeaways
- The prefix function stores, for each prefix, its longest proper border. KMP uses it to avoid re-reading text, giving O(n + m) worst case.
- Rabin–Karp's rolling hash updates in O(1) per window. Exact matching needs verification; all-occurrences cost includes O(m) for every candidate, even a genuine match.
- The Z-function gives, for each position, how far the string matches its own prefix, in O(n).
- A suffix array sorts all suffixes; pattern occurrences form one block found by binary search in O(m log n), for an n-character text and m-character pattern.
- The LCP array turns repeated-substring and distinct-substring questions into simple scans.

## Further reading
- [Prefix function and Knuth–Morris–Pratt — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Rabin–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
- [Suffix Array — cp-algorithms](https://cp-algorithms.com/string/suffix-array.html)
- [Suffix array — Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
