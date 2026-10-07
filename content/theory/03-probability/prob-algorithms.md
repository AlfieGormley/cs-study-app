---
id: prob-algorithms
title: Probability in algorithms
level: advanced
minutes: 15
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

Monte Carlo errors can be driven down by **repetition**. With independent rounds, k rounds of Miller–Rabin have error at most (1/4)ᵏ: 20 rounds gives less than 10⁻¹². This bounds acceptance of a fixed composite under the sampling model; it is not directly the posterior probability that a returned candidate is composite.

> [!note] Evidence gap
> The previous comparison with hardware-fault probability is omitted because no hardware error model or measured execution exposure supported it.

## Hash tables and collisions

Hash n keys into m buckets, each key independently to a uniformly random bucket (the **simple uniform hashing** assumption). The **load factor** is α = n/m.

By indicators and linearity:

- Expected keys per bucket is α.
- An unsuccessful search in a chained table inspects about α keys on average (plus the cost of hashing), so lookups are O(1 + α).
- Each of the C(n, 2) pairs collides with probability 1/m, so the **expected number of colliding pairs** is n(n − 1)/(2m).

That last result is surprising. With n = m (α = 1), you expect about n/2 colliding pairs. Collisions are not a rare failure; they are the normal state of a hash table, which is why every hash table needs a collision strategy.

> [!note] Real tables resize
> CPython's dictionary implementation uses a usable-entry fraction of about two-thirds; deletions and table layout complicate a simple occupancy trigger. Java `HashMap` has a configurable load factor, default 0.75. These are implementation/default details, not universal rules for all hash tables. Keeping α bounded keeps the expected cost constant. Open addressing degrades sharply as α approaches 1: in the classical large-table model with uniform independent home positions and no deletions, linear probing has expected unsuccessful-search cost about ½(1 + 1/(1 − α)²) probes, which is 50.5 at α = 0.9.

### Adversaries and hash flooding

The uniform-hashing assumption fails if an attacker chooses the keys. In 2011, researchers showed that web frameworks in PHP, Java, Python and others could be knocked over by POST requests whose parameter names all hashed to one bucket, turning each insert into O(n) work. Defences include input limits and secret keyed hashing. Python enables hash randomisation for str and bytes by default since 3.3; CPython commonly uses SipHash, with the active algorithm visible in sys.hash_info. Configuration can disable randomisation, and custom or non-string hashes need separate consideration. A random seed alone is not a guarantee against every adaptive attack.

## The birthday problem

How many people must be in a room before two probably share a birthday? Under independent uniform birthdays over 365 days, the first group size with a collision probability above 50% is **23**.

There are m = 365 days. The chance that n people all have different birthdays is:

```
P(no match) = (365/365)(364/365)...
              ((365 − n + 1)/365)
```

Each new person must avoid all the earlier ones. For n = 23 this is about 0.493, so P(match) ≈ 0.507.

The reason it is so low: what matters is the number of **pairs**, and 23 people form C(23, 2) = 253 pairs, each of which might match.

### The birthday bound

For n independent uniform draws from m slots, approximating the no-collision product gives (accurate in the birthday regime n on the order of √m for large m):

```
P(collision) ≈ 1 − e^(−n(n−1)/(2m))
```

Setting this to 1/2 gives the **birthday bound**:

```
n ≈ 1.18 √m   (50% chance)
```

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
- **Git abbreviations.** Seven hex characters give 28 bits, so a repository with tens of thousands of objects has a material probability of ambiguous fixed-length abbreviations under an ideal uniform-hash model. That is why Git automatically lengthens abbreviations as a repository grows.
- **UUIDs.** Version 4 UUIDs have 122 random bits. You would need about 2.7 quintillion of them for an even chance of a single collision, which is why systems generate them without coordination.
- **Cryptographic hashes.** For an ideal n-bit hash under a classical generic attack, finding *some* collision takes on the order of 2^(n/2) evaluations, a **birthday attack**. A 128-bit hash gives only 64-bit collision resistance. MD5 and SHA-1 also have cryptanalytic collision weaknesses beyond this generic bound; their history cannot be explained by output length alone. SHA-256 offers a generic 128-bit classical collision bound, assuming no better attack.

> [!tip] Quick estimate
> For small probabilities, P(collision) ≈ n²/(2m). Doubling the number of items quadruples the risk; adding 1 bit to the ID halves it.

## Randomised quicksort

Quicksort picks a pivot, partitions the array into smaller and larger elements, and recurses. With a fixed pivot (say the first element), a sorted input gives the worst case: every partition peels off one element, for n(n − 1)/2 comparisons. Sorted and nearly sorted inputs are common in practice, so this matters.

For distinct keys, standard pivot partitioning that compares the pivot once with every other element, and fresh independent uniform pivots, the comparison-count distribution does not depend on the initial order. The expected number of comparisons is about 2n ln n ≈ 1.39 n log₂ n, i.e. O(n log n), for every fixed distinct-key input.

### The indicator proof

Let z₁ < z₂ < ... < zₙ be the elements in sorted order. Every comparison is between a pivot and another element, and each pair is compared at most once (after partitioning, the pivot is never touched again).

Let Xᵢⱼ = 1 if zᵢ and zⱼ are ever compared. Consider the block zᵢ, zᵢ₊₁, ..., zⱼ, which has j − i + 1 elements. They stay together in one subarray until one of them is chosen as a pivot:

- If the first pivot chosen from the block is zᵢ or zⱼ, they are compared.
- If it is anything in between, zᵢ and zⱼ are split into different sides and never compared.

Each element of the block is equally likely to be first, so:

```
P(zᵢ, zⱼ compared) = 2 / (j − i + 1)
```

By linearity, summing over all pairs:

```
E[comparisons] = Σ_{i<j} 2/(j − i + 1)
               = 2(n + 1)Hₙ − 4n
               ≈ 2n ln n
```

For n = 1,000 that is about 11,000 comparisons, versus 499,500 in the worst case. Simulating it confirms the figure.

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

The quadratic worst case remains possible. The expectation guarantee assumes the input is fixed independently of the random choices and comparisons obey a total order; an adaptive adversary or predictable pivots needs separate analysis. A naive two-way implementation can also be quadratic on equal keys. The same argument shows **quickselect** (finding the k-th smallest) runs in expected O(n).

> [!note] What libraries do
> Production sorts hedge further. C++'s `std::sort` is typically introsort, which falls back to heapsort if recursion gets too deep. Go's `sort` package switched to pattern-defeating quicksort (pdqsort) in Go 1.19, and Rust's documented current unstable sort uses ipnsort. Python's list sort and Java's object-array sort are stable; implementation details can change by version. These library algorithms have additional safeguards and are not identical to the teaching function above.

## Bloom filters: designed-in false positives

A **Bloom filter** answers "have I seen this key?" using m bits and k hash functions. Insert sets k bits; a query checks them. A correctly implemented, insert-only filter with consistent hashing and no lost updates gives no false negatives for inserted keys, but it can give false positives when other keys happened to set all k bits.

Under an ideal model with independent uniform hash positions for n distinct inserted keys, a given bit is still 0 with probability (1 − 1/m)^(kn) ≈ e^(−kn/m). A false positive needs all k bits set:

```
FPR ≈ (1 − e^(−kn/m))ᵏ
best real k ≈ (m/n) ln 2
```

With 10 bits per key and k = 7, the false positive rate is about 0.82%. Storage engines can use Bloom filters to skip files that cannot contain a key; RocksDB documents this use. Whether an absent-key read avoids physical I/O depends on filter configuration, cache state and the other files or metadata examined. Whether this memory/error trade is useful depends on key sizes and the cost of false positives.

## Pitfalls

- **Believing uniform hashing for adversarial input.** Use an appropriate secret keyed hash and bound untrusted input size; check which key types actually use that hash.
- **Underestimating collisions.** Think in pairs: risk grows with n², and collisions are likely at √m.
- **Confusing expected and worst case.** The stated randomised comparison bound assumes distinct keys, suitable partitioning and independent uniform pivots. Simple deterministic pivot rules can have quadratic inputs; deterministic algorithms with stronger pivot guarantees or fallback strategies can avoid that worst case.
- **Bad randomness.** a PRNG (`random` in Python) can serve non-adversarial pivot selection but not for security tokens; use `secrets`.

## Key takeaways
- Las Vegas algorithms are always correct with random running time; Monte Carlo algorithms permit error; independent repetition with an appropriate decision rule can amplify a suitable per-run bound.
- Hashing n keys into m buckets gives load α = n/m and about n²/(2m) colliding pairs; keep α bounded by resizing.
- Birthday bound: collisions become likely around 1.18√m items. 32-bit IDs collide at ~77,000; an ideal n-bit hash has a generic classical collision bound of about n/2 bits.
- Randomised quicksort makes about 2n ln n comparisons in expectation under the distinct-key pivot model; the proof uses P(zᵢ, zⱼ compared) = 2/(j − i + 1).
- Bloom filters trade a tunable false positive rate, (1 − e^(−kn/m))ᵏ, for large memory savings.

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
