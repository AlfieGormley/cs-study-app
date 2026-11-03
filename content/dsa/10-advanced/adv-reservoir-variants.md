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


- **Algorithm L** draws how many items to skip before the next replacement. For a positive sample size k from a stream of length n at least k, its expected random-draw count is O(k(1 + log(n / k))). It avoids a draw for every input item. Reading a non-skippable stream still takes linear time, so fewer random draws do not imply skipping input I/O.

- **Weighted sampling** (Efraimidis–Spirakis): give each item a random key based on its weight and keep the k items with the largest keys, as below. This is sequential weighted sampling without replacement. It does not promise that each item's inclusion probability is k times its share of the total weight.

```formula reference
K = u^{1/w}
s = −ln(u) / w
where
w: the item's weight, a positive number; 2 in the example
u: a fresh uniform random number with 0 < u ≤ 1; 0.25 in the example
K: the item's key; keep the k items with the largest K
s: the equivalent score; keep the k smallest s
k: the sample size
ln: the natural logarithm, to base e ≈ 2.718
u^{1/w}: u raised to the power 1 / w (for w = 2, the square root of u)
≈: approximately equal to
In words: larger weights make an item more likely to win a place. Keeping the largest power-based keys is equivalent to keeping the smallest logarithmic scores, which avoids tiny power values that underflow.
```

- Distributed: assume disjoint shards, known shard sizes and independent uniform local samples. For a single-item sample, choose one shard's sample with probability proportional to its shard size. For a larger sample of k items, with k no greater than the total population, allocate counts as if drawing from the combined population without replacement: a hypergeometric allocation. Then uniformly subsample each local reservoir without replacement. Each local reservoir must contain k items, or every item in its shard if that shard is smaller. Repeating the singleton choice with unchanged shard probabilities is insufficient.

## Key takeaways

- Weighted sampling without replacement does not give simply proportional inclusion probabilities.
- Shard samples must be combined with their shard sizes, not by a fair shard coin.

## Further reading
- [Weighted Random Sampling — Efraimidis and Spirakis](https://utopia.duth.gr/pefraimi/research/data/2007EncOfAlg.pdf)
- [Algorithms for Generating Small Random Samples — Vincent Cicirello](https://reports.cicirello.org/24/008/ALG-24-008.pdf)
- [Communication-Optimal Parallel Reservoir Sampling — Winter and colleagues](https://dl.gi.de/bitstream/handle/20.500.12116/40332/B5-4.pdf)
