---
id: prob-algorithms
title: Probability in algorithms
level: advanced
minutes: 22
summary: Hash collisions and load factors, the birthday bound behind ID lengths and hash security, randomised quicksort's expected comparisons, Bloom filter false positives, and Las Vegas versus Monte Carlo algorithms.
---

Randomness is one of the most useful tools in algorithm design. Independent uniform pivots give quicksort good expected performance on fixed distinct-key inputs. Secret keyed hashing makes precomputed collision attacks harder. Random sampling can reduce the data needed for an estimate, with accuracy and runtime depending on the task.

Using randomness well needs the probability from the earlier lessons: indicators and linearity, the complement trick and the union bound. This lesson applies them to the problems you will meet in interviews and in production.

## Two kinds of randomised algorithm

| Kind | Always correct? | Running time |
|---|---|---|
| Las Vegas | Yes | Random |
| Monte Carlo | Not always | Bounded |

- **Las Vegas** algorithms always give the right answer; only their running time is random. Randomised quicksort is the standard example: it always sorts, but how long it takes depends on the pivots.
- **Monte Carlo** algorithms run in bounded time but may be wrong with small probability. The Miller–Rabin primality test may call a composite number "probably prime", with probability at most 1/4 per round for an odd composite input when the base is sampled uniformly from the required range.

Monte Carlo errors can be driven down by **repetition** (amplification). With independent rounds, a composite number must fool every round to be accepted:

```formula
P(F) ≤ (1/4)^k
(1/4)^20 = 1 / 2^40 ≈ 9.1 × 10^{−13}
where
F: the event "a fixed odd composite input passes all k rounds"
k: the number of independent Miller–Rabin rounds, 20 in the second line
1/4: the most a single round can be fooled, when its base is chosen uniformly at random
P(F): the probability of F
≤: less than or equal to
≈: approximately equal to
10^{−13}: ten to the minus 13, 0.0000000000001
In words: each independent round at least quarters the chance of being fooled, so 20 rounds leave less than one chance in a trillion (10^{−12}).
```

This bounds acceptance of a fixed composite under the sampling model; it is not directly the posterior probability that a returned candidate is composite.

> [!note] Evidence gap
> The previous comparison with hardware-fault probability is omitted because no hardware error model or measured execution exposure supported it.

## Hash tables and collisions

Hash keys into buckets, each key independently to a uniformly random bucket (the **simple uniform hashing** assumption). By indicators and linearity, the expected number of keys in each bucket is the **load factor**, and the expected number of pairs of keys that land in the same bucket follows from counting pairs:

```formula
α = n / m
E[K_b] = n × (1/m) = α
E[N_c] = C(n, 2) × (1/m)
E[N_c] = n × (n − 1) / (2 × m)
where
n: the number of keys stored
m: the number of buckets
α: alpha, the load factor, the average number of keys per bucket
K_b: the number of keys in one particular bucket b
1/m: the chance a key lands in a given bucket, and the chance two keys land in the same bucket
N_c: the number of colliding pairs, pairs of keys in the same bucket
C(n, 2): "n choose 2", the number of pairs of keys, n × (n − 1) / 2
E[ ]: expected value
In words: each bucket gets α keys on average, and with n keys there are about n²/2 pairs, each colliding with chance 1/m.
```

An unsuccessful search in a **chained** table (each bucket holds a list of its keys) inspects about α keys on average, plus the cost of hashing, so lookups are O(1 + α), where O( ) is big-O notation, "grows at most as fast as".

The colliding-pairs result is surprising. With as many keys as buckets (α = 1), you expect about n/2 colliding pairs: 1,000 keys in 1,000 buckets give 1000 × 999 / 2000 ≈ 500. Collisions are not a rare failure; they are the normal state of a hash table, which is why every hash table needs a collision strategy.

> [!note] Real tables resize
> CPython's dictionary implementation uses a usable-entry fraction of about two-thirds; deletions and table layout complicate a simple occupancy trigger. Java `HashMap` has a configurable load factor, default 0.75. These are implementation/default details, not universal rules for all hash tables. Keeping the load factor bounded keeps the expected cost constant. **Open addressing** (storing every key in the array itself and probing other slots on a collision) degrades sharply as the load factor approaches 1.

In the classical large-table model with uniform independent home positions and no deletions, **linear probing** (trying the next slot, then the next) has this expected cost for an unsuccessful search:

```formula
U ≈ 1/2 × (1 + 1 / (1 − α)^2)
U ≈ 1/2 × (1 + 1 / 0.1^2) = 50.5
where
U: the expected number of probes (slots examined) in an unsuccessful search
α: alpha, the load factor, the fraction of slots in use; 0.9 in the second line
(1 − α)^2: the free fraction of slots, squared
≈: approximately equal to (valid for large tables)
In words: at 90% full, a failed lookup examines about 50 slots, versus 2.5 at 50% full.
```

### Adversaries and hash flooding

The uniform-hashing assumption fails if an attacker chooses the keys. In 2011, researchers showed that web frameworks in PHP, Java, Python and others could be knocked over by POST requests whose parameter names all hashed to one bucket, making each insert cost O(n) work, where n is the number of keys already in that bucket. Defences include capping the number of request parameters and secret keyed hashing. Python enables hash randomisation for str and bytes by default since 3.3; CPython commonly uses SipHash, with the active algorithm visible in sys.hash_info. Configuration can disable randomisation, and custom or non-string hashes need separate consideration. A random seed alone is not a guarantee against every adaptive attack.

## The birthday problem

How many people must be in a room before two probably share a birthday? Under independent uniform birthdays over 365 days, the first group size with a collision probability above 50% is **23**.

Each new person must avoid the birthdays of all the earlier ones. Multiply those chances:

```formula
P(U) = 365/365 × 364/365 × …
  × (365 − n + 1)/365
P(U) ≈ 0.493   for n = 23
P(¬U) ≈ 1 − 0.493 = 0.507
where
U: the event "all n people have different birthdays"
¬U: "not U", at least two people share a birthday
n: the number of people in the room
365: the number of equally likely birthdays (ignoring 29 February)
(365 − n + 1)/365: the chance the n-th person avoids the n − 1 birthdays already taken
…: and so on, one factor per person
P: probability
≈: approximately equal to
In words: with 23 people, the chance everyone's birthday is different has already dropped below a half.
```

The reason it is so low: what matters is the number of **pairs**, and 23 people form 23 × 22 / 2 = 253 pairs, each of which might match.

### The birthday bound

For independent uniform draws from a large space, the no-collision product can be approximated with the exponential function. Setting the result to one half gives the **birthday bound**:

```formula
P(C) ≈ 1 − e^{−n × (n − 1) / (2 × m)}
n_{1/2} ≈ √(2 × ln(2) × m)
n_{1/2} ≈ 1.18 × √(m)
where
C: the event "at least two draws collide (are equal)"
n: the number of independent uniform draws (people, IDs, hashes)
m: the number of equally likely values (365 days, 2^32 IDs, …)
e: Euler's number, about 2.718; each factor 1 − i/m is close to e^{−i/m} when i is small next to m
n_{1/2}: the number of draws at which a collision becomes a 50% chance
ln(2): the natural logarithm of 2, about 0.693
1.18: √(2 × ln(2)) ≈ 1.1774
√: the square root
P: probability
≈: approximately equal to
In words: collisions become a coin flip at about 1.18 times the square root of the number of possible values.
```

The approximation is accurate when n is of the order of √m and m is large. For birthdays, 1.18 × √365 ≈ 22.5, close to the exact 23.

Collisions become likely at about the **square root** of the space size, not at the space size.

```python
def p_collision(n, m):
    if (not isinstance(n, int)
            or not isinstance(m, int)
            or n < 0 or m < 1):
        raise ValueError("invalid n or m")
    if n > m:
        return 1.0
    p_unique = 1.0
    for i in range(n):
        p_unique *= (m - i) / m
    return 1 - p_unique

print(round(p_collision(23, 365), 3))
# 0.507
```

### Why engineers care

| Space | Size | 50% collision at |
|---|---|---|
| Birthdays | 365 | ~23 |
| 7 hex chars (28 bits) | 2²⁸ | ~19,000 |
| 32-bit hash | 2³² | ~77,000 |
| 64-bit hash | 2⁶⁴ | ~5.1 billion |
| UUIDv4 (122 random bits) | 2¹²² | ~2.7 × 10¹⁸ |

- **Short IDs.** A 32-bit random ID looks huge (4 billion values), but collisions are a coin flip after about 77,000 IDs. Even at 10,000 IDs the chance is about 1.2%.
- **Git abbreviations.** Seven hex characters give 28 bits, so a repository with tens of thousands of objects has a material probability of ambiguous abbreviations of one set length under an ideal uniform-hash model. That is why Git automatically lengthens abbreviations as a repository grows.
- **UUIDs.** Version 4 UUIDs have 122 random bits. You would need about 2.7 quintillion of them for an even chance of a single collision, which is why systems generate them without coordination.
- **Cryptographic hashes.** For an ideal b-bit hash under a classical generic attack, finding *some* collision takes on the order of 2 to the power b/2 evaluations (the square root of the 2 to the power b possible outputs), a **birthday attack**. A 128-bit hash gives only 64-bit collision resistance. MD5 and SHA-1 also have cryptanalytic collision weaknesses beyond this generic bound; their history cannot be explained by output length alone. SHA-256 offers a generic 128-bit classical collision bound, assuming no better attack.

> [!tip] Quick estimate
> For small probabilities, the collision chance is about the expected number of colliding pairs. Doubling the number of items quadruples the risk; adding 1 bit to the ID halves it.

```formula
P(C) ≈ n^2 / (2 × m)
P(C) ≈ 10,000^2 / (2 × 2^32) ≈ 0.012
where
C: the event "at least one collision"
n: the number of items (IDs); 10,000 in the second line
m: the number of possible values; 2^32 ≈ 4.29 billion for a 32-bit ID
n^2: n multiplied by itself
P: probability
≈: approximately equal to (good while the result is well below 1)
In words: 10,000 random 32-bit IDs collide with about a 1.2% chance.
```

## Randomised quicksort

Quicksort picks a pivot, partitions the array into smaller and larger elements, and recurses. With a fixed pivot (say the first element), a sorted input of n elements gives the worst case: every partition peels off one element, for n(n − 1)/2 comparisons (499,500 when n = 1,000). Sorted and nearly sorted inputs are common in practice, so this matters.

For distinct keys, standard pivot partitioning that compares the pivot once with every other element, and fresh independent uniform pivots, the comparison-count distribution does not depend on the initial order. The expected number of comparisons is about 2n ln n (ln is the natural logarithm), which is about 1.39 n log₂ n, i.e. O(n log n), for every fixed distinct-key input of n elements.

### The indicator proof

Name the elements in sorted order, smallest first. Every comparison is between a pivot and another element, and each pair is compared no more than once (after partitioning, the pivot is never touched again). So the number of comparisons is a sum of indicators, one per pair.

Take the i-th smallest and the j-th smallest elements, and the block of sorted elements from one to the other. They stay together in one subarray until one element of that block is chosen as a pivot:

- If the first pivot chosen from the block is one of the two ends, the pair is compared.
- If it is anything in between, the two are split into different sides and never compared.

Each element of the block is equally likely to be first, so:

```formula
P(X_ij = 1) = 2 / (j − i + 1)
where
z_1 < z_2 < … < z_n: the n elements in sorted order
i, j: the ranks of the two elements, with i < j
X_ij: the indicator that z_i and z_j are ever compared: 1 if so, 0 if not
j − i + 1: the number of elements in the block from z_i to z_j
2: the two "good" first pivots, z_i or z_j
P: probability
In words: two elements are compared only if one of them is the first pivot picked from the block between them, a chance of 2 divided by the number of elements in the block.
```

By linearity, summing over all pairs:

```formula
E[Q] = Σ_{i<j} 2 / (j − i + 1)
E[Q] = 2 × (n + 1) × H_n − 4 × n
E[Q] ≈ 2 × n × ln(n)
where
Q: the total number of comparisons
E[Q]: its expected value
n: the number of elements
i, j: the ranks of the two elements in a pair
Σ_{i<j}: sigma, "add up over every pair with i less than j"
H_n: the n-th harmonic number, 1 + 1/2 + … + 1/n
ln(n): the natural logarithm of n (base e ≈ 2.718)
≈: approximately equal to (for large n)
In words: close pairs are compared often and distant pairs rarely; adding up all pairs gives about 2 n ln(n) comparisons.
```

For n = 1,000:

```formula
E[Q] = 2 × 1001 × H_1000 − 4000
E[Q] ≈ 2002 × 7.485 − 4000 ≈ 10,986
where
E[Q]: the expected number of comparisons for 1,000 elements
H_1000: the 1,000th harmonic number, about 7.485
≈: approximately equal to
In words: randomised quicksort makes about 11,000 comparisons on 1,000 elements, against 499,500 in the worst case.
```

That is about 11,000 comparisons, versus 499,500 in the worst case. Simulating it confirms the figure.

```python
import random

def qs(a):
    # Distinct keys with a total order.
    # Count actual pivot comparisons.
    if len(a) <= 1:
        return 0
    i = random.randrange(len(a))
    p = a[i]
    lo, hi = [], []
    for j, x in enumerate(a):
        if j == i:
            continue
        if x < p:
            lo.append(x)
        else:
            hi.append(x)
    return (len(a) - 1) + qs(lo) + qs(hi)

print(qs(list(range(1000))))
# around 11,000 for any input order
```

The quadratic worst case remains possible. The expectation guarantee assumes the input is fixed independently of the random choices and comparisons obey a total order; an adaptive adversary or predictable pivots needs separate analysis. A naive two-way implementation can also be quadratic on equal keys. The same argument shows **quickselect** (finding the k-th smallest element of n) runs in expected O(n).

> [!note] What libraries do
> Production sorts hedge further. C++'s `std::sort` is typically introsort, which falls back to heapsort if recursion gets too deep. Go's `sort` package switched to pattern-defeating quicksort (pdqsort) in Go 1.19, and Rust's documented current unstable sort uses ipnsort. Python's list sort and Java's object-array sort are stable; implementation details can change by version. These library algorithms have additional safeguards and are not identical to the teaching function above.

## Bloom filters: designed-in false positives

A **Bloom filter** answers "have I seen this key?" using an array of bits and several hash functions. Inserting a key sets the bit chosen by each hash function; a query checks those same bits. A correctly implemented, insert-only filter with consistent hashing and no lost updates gives no false negatives for inserted keys, but it can give false positives when other keys happened to set all of a query's bits.

Under an ideal model with independent uniform hash positions for distinct inserted keys, each of the k × n bit-settings misses a given bit with probability 1 − 1/m. A false positive needs all k of the query's bits to be set:

```formula
P(B = 0) = (1 − 1/m)^{k × n}
P(B = 0) ≈ e^{−k × n / m}
FPR ≈ (1 − e^{−k × n / m})^k
k_opt ≈ (m / n) × ln(2)
where
m: the number of bits in the filter
n: the number of distinct keys inserted
k: the number of hash functions (bits set per key)
B: the value of one particular bit after all inserts
P(B = 0): the probability that bit is still 0
e: Euler's number, about 2.718
FPR: the false positive rate, the chance an absent key's k bits are all set
k_opt: the best real-valued number of hash functions for the given m and n; round it to a whole number
ln(2): the natural logarithm of 2, about 0.693
≈: approximately equal to
In words: the more bits per key, the fewer bits are set and the rarer false positives become; about 0.7 hash functions per bit-per-key is best.
```

With 10 bits per key and 7 hash functions:

```formula
FPR ≈ (1 − e^{−7/10})^7
FPR ≈ 0.5034^7 ≈ 0.0082
k_opt ≈ 10 × 0.693 ≈ 6.9
where
FPR: the false positive rate
7: the number of hash functions, k
10: bits per key, m / n
e: Euler's number, about 2.718
k_opt: the best number of hash functions, which rounds to 7
≈: approximately equal to
In words: 10 bits per key with 7 hash functions gives false positives about 0.82% of the time.
```

So the false positive rate is about 0.82%. Storage engines can use Bloom filters to skip files that cannot contain a key; RocksDB documents this use. Whether an absent-key read avoids physical I/O depends on filter configuration, cache state and the other files or metadata examined. Whether this memory/error trade is useful depends on key sizes and the cost of false positives.

## Pitfalls

- **Believing uniform hashing for adversarial input.** Use an appropriate secret keyed hash and bound untrusted input size; check which key types actually use that hash.
- **Underestimating collisions.** Think in pairs: risk grows with the square of the number of items, and collisions are likely at about the square root of the number of possible values.
- **Confusing expected and worst case.** The stated randomised comparison bound assumes distinct keys, suitable partitioning and independent uniform pivots. Simple deterministic pivot rules can have quadratic inputs; deterministic algorithms with stronger pivot guarantees or fallback strategies can avoid that worst case.
- **Bad randomness.** A **pseudo-random number generator** (PRNG; `random` in Python) can serve non-adversarial pivot selection but not for security tokens; use the `secrets` module.

## Key takeaways
- Las Vegas algorithms are always correct with random running time; Monte Carlo algorithms permit error; independent repetition with an appropriate decision rule can amplify a suitable per-run bound.
- Hashing keys into buckets gives a load factor of keys per bucket, and the expected colliding pairs are about the number of pairs divided by the number of buckets; keep the load factor bounded by resizing.
- Birthday bound: collisions become likely around 1.18 times the square root of the number of possible values. 32-bit IDs collide at ~77,000; an ideal hash has a generic classical collision bound of about half its output bits.
- Randomised quicksort makes about 2n ln n comparisons in expectation under the distinct-key pivot model; the proof uses the chance, 2 divided by the number of elements between them inclusive, that two elements are compared.
- Bloom filters trade a tunable false positive rate for large memory savings: about 0.82% at 10 bits per key.

## Further reading
- [Birthday problem — Wikipedia](https://en.wikipedia.org/wiki/Birthday_problem)
- [Birthday attack — Wikipedia](https://en.wikipedia.org/wiki/Birthday_attack)
- [Quicksort — Wikipedia](https://en.wikipedia.org/wiki/Quicksort)
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Las Vegas algorithm — Wikipedia](https://en.wikipedia.org/wiki/Las_Vegas_algorithm)
- [Hash flooding DoS (oCERT advisory 2011-003)](https://ocert.org/advisories/ocert-2011-003.html)

- [UUIDv4 random-bit layout — RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4)
- [Miller–Rabin — Handbook of Applied Cryptography, chapter 4](https://cacr.uwaterloo.ca/hac/about/chap4.pdf)
- [RocksDB Bloom filters](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)
