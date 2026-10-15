---
id: prob-bloom-filter-errors
title: Size Bloom filters and respect randomness limits
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: An insert-only Bloom filter trades space for false positives.
---

## Bloom filters: designed-in false positives

A **Bloom filter** answers "have I seen this key?" using an array of bits and several hash functions. Inserting a key sets the bit chosen by each hash function; a query checks those same bits. A correctly implemented, insert-only filter with the same hash mappings on insertion and query and no lost updates gives no false negatives for inserted keys, but it can give false positives when other keys happened to set all of a query's bits.

Under an ideal model with independent uniform hash positions for distinct inserted keys, every bit-setting chooses uniformly, so it misses a specified bit unless it selects that one position. A false positive needs all k of the query's bits to be set:

```formula
P(B = 0) = (1 − 1/m)^{k × n}
P(B = 0) ≈ e^{−(kn) / m}
FPR ≈ (1 − e^{−(kn) / m})^k
k_opt ≈ (m / n) × ln(2)
where
P: probability of measurable events, dimensionless and between zero and one
m: the positive integer number of bits in an initially empty insert-only filter with independent uniform insertion and absent-query hash positions
n: the positive integer number of distinct keys inserted
k: the positive integer number of hash functions (positions selected per key)
B: the value of one particular bit after all inserts
P(B = 0): the probability that bit is still 0
e: Euler's number, about 2.718
FPR: the false positive rate, the chance an absent key's k bits are all set
k_opt: the optimal positive real hash count under the large-filter approximation; compare neighbouring positive integers for implementation
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

The false positive rate is about 0.82% under this approximation. Bit occupancies and repeated query positions introduce dependence in a finite filter, so multiplying marginal occupancy probabilities is not an exact finite-size error formula. Storage engines can use Bloom filters to skip files that cannot contain a key; RocksDB documents this use. Whether an absent-key read avoids physical I/O depends on filter configuration, cache state and the other files or metadata examined. Whether this memory/error trade is useful depends on key sizes and the cost of false positives.

## Pitfalls

- **Believing uniform hashing for adversarial input.** Use an appropriate secret keyed hash and bound untrusted input size; check which key types actually use that hash.
- **Underestimating collisions.** Think in pairs: risk grows with the square of the number of items, and collisions are likely at about the square root of the number of possible values.
- **Confusing expected and worst case.** The stated randomised comparison bound assumes distinct keys, suitable partitioning and independent uniform pivots. Simple deterministic pivot rules can have quadratic inputs; deterministic algorithms with stronger pivot guarantees or fallback strategies can avoid that worst case.
- **Bad randomness.** A **pseudo-random number generator** (PRNG; `random` in Python) can serve non-adversarial pivot selection but not for security tokens; use the `secrets` module.

## Key takeaways
- An insert-only Bloom filter trades space for false positives.
- The optimum hash count follows the large-filter ideal hashing approximation.
- Security tokens require a suitable cryptographic random source.

## Further reading
- [On the false-positive rate of Bloom filters — Bose and colleagues](https://people.scs.carleton.ca/~michiel/bloomfilter.pdf)
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
