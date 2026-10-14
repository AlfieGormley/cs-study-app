---
id: hash-prob-bloom-sizing
title: Sizing Bloom filters and modelling error
level: advanced
minutes: 5
sourceLesson: hash-probabilistic
summary: Here n counts distinct inserted items, m is filter bits, and k is positions checked per item.
---

Here n counts distinct inserted items, m is filter bits, and k is positions checked per item. The equations model independent uniform hash choices; they are not measurements of the sample implementation.

## Bloom-filter false-positive estimates



Assume the hashes behave like independent, uniformly random choices, and count n distinct items (adding the same item twice sets no new bits). Each time a bit is set, a particular bit is missed with probability one minus the reciprocal of the bit count. Adding the items makes hash-count times item-count position choices, so the chance that a given bit is still 0 is:

```formula
q = (1 − 1 / m)^(k n) ≈ e^(−k n / m)
q ≈ e^(−7 × 100 / 1000) = e^(−0.7)
q ≈ 0.497
where
q: the probability that one particular bit is still 0 after all the insertions
m: the number of bits in the filter, here 1,000
k: the number of hash functions (bits set per item), here 7
n: the number of distinct items added, here 100
e: Euler's number, about 2.718; (1 − 1/m)^m is very close to 1/e when m is large, which gives the approximation
^: "to the power of"
≈: approximately equal to
In words: each of the 700 bit-settings misses a given bit with probability 999/1000, so the bit survives all of them about half the time (0.497).
```

A false positive happens when an item that was never added finds all k of its bits already set to 1. Treating the k bits as independent:

```formula
p ≈ (1 − e^(−k n / m))^k
p ≈ (1 − 0.497)^7 = 0.503^7
p ≈ 0.0082 ≈ 0.8%
where
p: the false-positive rate, the probability that a query for an item never added answers "maybe present"
k: the number of hash functions, here 7
n: the number of distinct items added, here 100
m: the number of bits, here 1,000
e: Euler's number, about 2.718
^: "to the power of"
≈: approximately equal to
%: per cent, parts per hundred; 0.0082 = 0.82%
In words: a bit is set with probability about 0.503, and a false positive needs all 7 of the query's bits set, so 7 copies of 0.503 multiplied together: about 0.8%, or 1 query in 120.
```

These are model estimates for large filters with good hashes; small filters and correlated hash positions can do slightly worse.

**Choosing k.** Too few hashes and each query checks too few bits; too many and the array fills with 1s. Minimising the false-positive formula above gives the best number of hash functions:

```formula
k = (m / n) × ln(2) ≈ 0.69 × (m / n)
k = 10 × 0.693 = 6.93 ≈ 7
where
k: the number of hash functions that gives the lowest false-positive rate (rounded to a whole number in practice)
m: the number of bits in the filter
n: the number of items you expect to add
m / n: bits per item, here 10
ln: the natural logarithm, the logarithm to base e (about 2.718); ln(2) ≈ 0.693
≈: approximately equal to
In words: use about 0.69 hash functions per bit per item; with 10 bits per item that is 7 hashes, which leaves about half the filter's bits set.
```

Using one hash in the same model gives about 9.5%; using fourteen gives about 1.9%.

**Sizing.** Turn the question round: given a target false-positive rate, how many bits does each item need? At the optimal k:

```formula
m / n = −ln(p) / (ln(2))^2
m / n ≈ 1.44 × log_2(1 / p)
m / n ≈ −ln(0.01) / 0.4805
m / n ≈ 4.605 / 0.4805 ≈ 9.6 bits
where
m: filter size in bits
n: expected distinct inserted-item count
m / n: bits per item: the filter's size in bits divided by the number of items
p: the target false-positive rate, here 1% = 0.01
ln: the natural logarithm (base e ≈ 2.718); ln(0.01) ≈ −4.605 and ln(2) ≈ 0.693, so (ln(2))^2 ≈ 0.4805
log_2: logarithm to base 2; log_2(100) ≈ 6.64
bits: binary digits, the 0s and 1s the filter is made of; 8 bits make a byte
^: "to the power of"
≈: approximately equal to
In words: a 1% filter needs about 9.6 bits per item; every time you make p ten times smaller you add 1.44 × log_2(10) ≈ 4.8 bits per item.
```

| Target p | Bits per item | k |
|---|---|---|
| 1% | 9.6 | 7 |
| 0.1% | 14.4 | 10 |
| 0.01% | 19.2 | 13 |

Notice what is *not* in the formula: the size of the items. A billion 100-byte URLs need about 1.2 GB for a 1% filter, versus over 100 GB to store them. Each factor of 10 improvement in p costs about 4.8 more bits per item.

> [!warning] Overfilling
> The false-positive rate climbs fast past the design capacity. The one-thousand-bit, seven-hash filter above gives 0.8% at 100 items but about 14% at 200. Size for the maximum n you expect, or use a scalable Bloom filter that adds layers as it grows.

## Key takeaways
- Sizing depends on distinct items, bits per item and hash count.
- The optimal hash count leaves about half the bits occupied.
- Overfilling sharply increases modelled false positives; estimates are not measurements.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Less hashing, same performance](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf)
