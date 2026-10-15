---
id: adv-reservoir-variants
title: Skipping, weighting and combining samples
level: advanced
minutes: 3
summary: Weighted sampling without replacement does not give simply proportional inclusion probabilities.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

## Reservoir variants



- **Algorithm L** computes how many items to skip before the next replacement, so it draws far fewer random numbers than one per item:

```formula
R = O(k(1 + log(n / k)))
G = k(1 + ln(n / k))
G ≈ 100 × (1 + ln(10^7)) ≈ 1,712
where
R: the expected number of random draws used by Algorithm L
G: a growth-model term used to illustrate the asymptotic scale; it is not a predicted draw count
k: a positive sample size no larger than the stream, 100 in the worked growth-term line
n: the stream length, at least k; one billion in the worked growth-term line
log: a logarithm; the base only changes a constant factor
ln: the natural logarithm, to base e ≈ 2.718; ln(10^7) ≈ 16.1
O(f): grows at most in proportion to f
≈: approximately equal to
In words: Algorithm L's random-number count grows with the logarithm of the stream length, not the length itself.
```

  For a 100-line sample from a billion lines, the displayed growth term is about 1,712. It illustrates scaling rather than predicting 1,712 actual draws: a common Algorithm L implementation uses three draws per selected replacement, as well as initialisation and termination work. Scanning a non-skippable input stream can still take linear time even when the random-draw count falls.

- **Weighted sampling** (Efraimidis–Spirakis): give each item a random key based on its weight and keep the k items with the largest keys, as below. This is sequential weighted sampling without replacement. It does not promise that each item's inclusion probability is k times its share of the total weight.

```formula
K = u^{1/w}
s = −ln(u) / w
K = 0.25^{1/2} = 0.5
s = −ln(0.25) / 2 ≈ 0.693
where
w: the item's weight, a positive number; 2 in the example
u: a fresh uniform random number with 0 < u ≤ 1; 0.25 in the example
K: the item's key; keep the k items with the largest K
s: the equivalent score; keep the k smallest s
k: the sample size
ln: the natural logarithm, to base e ≈ 2.718
u^{1/w}: u raised to the power 1 / w (for w = 2, the square root of u)
≈: approximately equal to
In words: heavier items get keys pushed towards 1, so they win more often; the logarithm form ranks items in exactly the same order and avoids tiny numbers that underflow.
```

- Distributed: for a single-item sample, choose one shard's sample with probability proportional to its shard size. For larger reservoirs, simple repetition is insufficient: allocate shard counts with a hypergeometric distribution and subsample each local uniform reservoir without replacement. Each local reservoir must hold up to k items, or the whole shard if it is smaller.

## Key takeaways

- Weighted sampling without replacement does not give simply proportional inclusion probabilities.
- Shard samples must be combined with their shard sizes, not by a fair shard coin.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
