---
id: hash-prob-bloom-sizing
title: Sizing Bloom filters and modelling error
level: advanced
minutes: 5
sourceLesson: hash-probabilistic
summary: A Bloom filter's false-positive rate depends on bits per item and the number of hashes, and climbs steeply once it holds more items than it was sized for.
---

A Bloom filter's error rate is not fixed by its design alone: it depends on how full the bit array has become. This lesson explains the standard estimate in words, then turns it into practical sizing rules.

## The false-positive trade-off

Assume the hashes behave like independent, uniformly random choices, and count only distinct items (adding the same item twice sets no new bits). Every item added sets k bits, so as items arrive the fraction of bits still 0 shrinks. A query for an item that was never added gives a false positive when all k of its bits happen to be 1 already. So the false-positive rate is roughly the fraction of bits already set, raised to the power k. That fraction grows with k times the number of items, divided by the number of bits:

```formula reference
p ≈ (1 − e^(−kn / m))^k
where
p: the false-positive rate, the probability that a query for an item never added answers "maybe present"
k: the number of hash functions (bits set and checked per item)
n: the number of distinct items added
m: the number of bits in the filter
e: Euler's number, about 2.718
^: "to the power of"
≈: approximately equal to; a model for large filters with good hashes
In words: a false positive needs all k of a query's bits to be set already, so the rate is the fraction of bits set, multiplied by itself k times. That fraction depends only on hashes per item times items per bit, so more bits per item lower it and more items raise it.
```

Three practical consequences follow.

- **Bits per item drive accuracy.** Only the ratio of bits to items matters, not the size of each item. A filter with 1,000 bits, 7 hashes and 100 items (10 bits per item) gives about 0.8%, roughly 1 query in 120.
- **There is a best number of hashes.** Too few and each query checks too few bits; too many and the array fills with 1s. The best number of hashes is about 0.69 times the bits per item, which leaves about half the bits set. With 10 bits per item that is 7 hashes; using 1 gives about 9.5% and using 14 about 1.9%.
- **Each tenfold improvement costs a fixed number of bits.** At the best number of hashes, a 1% filter needs about 9.6 bits per item, and every further tenfold reduction in the false-positive rate adds about 4.8 bits per item.

```formula reference
k = (m / n) ln(2)
m / n = −ln(p) / (ln(2))^2
where
k: the number of hash functions that gives the lowest false-positive rate, rounded to a whole number in practice
m: the number of bits in the filter
n: the number of distinct items you expect to add
m / n: bits per item
p: the target false-positive rate
ln: the natural logarithm, the logarithm to base e (about 2.718); ln(2) ≈ 0.693
^: "to the power of"
≈: approximately equal to
In words: use about 0.69 times as many hash functions as there are bits per item, and budget bits per item according to how small a false-positive rate you need: about 9.6 bits for 1%, 14.4 for 0.1% and 19.2 for 0.01%.
```

| Target p | Bits per item | k |
|---|---|---|
| 1% | 9.6 | 7 |
| 0.1% | 14.4 | 10 |
| 0.01% | 19.2 | 13 |

Notice what is *not* in any of this: the size of the items. A billion 100-byte URLs need about 1.2 GB for a 1% filter, versus over 100 GB to store them.

> [!warning] Overfilling
> The false-positive rate climbs fast past the design capacity. The one-thousand-bit, seven-hash filter above gives 0.8% at 100 items but about 14% at 200. Size for the largest number of items you expect, or use a scalable Bloom filter that adds layers as it grows.

## Key takeaways
- Sizing depends on distinct items, bits per item and hash count.
- The optimal hash count leaves about half the bits occupied.
- Overfilling sharply increases modelled false positives; estimates are not measurements.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Less hashing, same performance](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf)
