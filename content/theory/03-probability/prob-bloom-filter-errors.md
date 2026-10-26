---
id: prob-bloom-filter-errors
title: Size Bloom filters and respect randomness limits
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: An insert-only Bloom filter trades space for false positives.
---

A **Bloom filter** can cheaply rule out membership, but a positive answer means “possibly present”. It is useful when a false positive merely triggers a more expensive exact lookup.

## Why the two answers differ

Insertion sets several hash-selected bits. Querying checks the same positions. If any required bit is unset, the key was not inserted. If all are set, other keys may have set them, so membership still needs confirmation.

No false negatives requires an insert-only filter, consistent hash mappings and no lost updates. Clearing a shared bit to delete one key can break that guarantee for other keys. An ordinary Bloom filter therefore cannot support deletion by simply clearing its bits.

## Balance memory and hash work

More bits per inserted key reduces crowding. More hash functions initially help distinguish queries, but too many set too many bits and increase false positives. The usual large-filter ideal-hashing approximation gives a useful sizing rule:

```formula reference
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

Under that approximation, ten bits per distinct key and seven hash functions give about a 0.82% false-positive rate. The query hash positions are independently sampled in this model, but the events that their selected bits are set are not generally independent after averaging over random insertions. Repeated positions can also test the same bit. The result is therefore not an exact finite-filter probability.

Check actual insertion count and query workload. Inserting beyond the planned count fills more bits and raises false positives. Memory, hash computation and the cost of unnecessary exact lookups all affect the useful design.

Security-sensitive randomness also needs an appropriate source. Python's pseudo-random `random` module is suitable for teaching simulations, not security tokens; use a cryptographic source such as its `secrets` module for those.

## Key takeaways
- Negative answers can rule out membership under stated implementation conditions.
- Positive answers need exact confirmation when correctness matters.
- More hashes help only up to a trade-off point.

## Further reading
- [On the false-positive rate of Bloom filters — Bose and colleagues](https://people.scs.carleton.ca/~michiel/bloomfilter.pdf)
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
