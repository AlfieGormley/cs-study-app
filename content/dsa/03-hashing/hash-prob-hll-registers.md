---
id: hash-prob-hll-registers
title: HyperLogLog registers and standard error
level: advanced
minutes: 4
sourceLesson: hash-probabilistic
summary: HyperLogLog counts distinct hashes without keeping every item.
---

HyperLogLog counts distinct hashes without keeping every item. A rare leading-zero pattern suggests scale, while many registers reduce the noise of relying on a single maximum.

## HyperLogLog: counting distinct items

Counting distinct items exactly needs a set of everything seen. **HyperLogLog** (Flajolet, Fusy, Gandouet and Meunier, 2007) estimates it in a few kilobytes.

### The intuition

Hash each item to a uniformly random-looking bit string. Look at how many leading zeros it has:

```
1xxxxxxx   probability 1/2
01xxxxxx   probability 1/4
001xxxxx   probability 1/8
0000001x   probability 1/128
```

Each bit of a good hash is 0 or 1 with equal chance, independently of the others, so long runs of zeros at the start are rare in a predictable way:

```formula
P(r) = (1 / 2)^r = 1 / 2^r
P(20) = 1 / 2^20 ≈ 1 / 1,000,000
where
P(r): the probability that a hash starts with at least r zero bits
r: the number of leading zero bits, here 20
^: "to the power of"; 2^20 = 1,048,576
≈: approximately equal to
In words: each extra leading zero halves the chance, so a hash starting with 20 zeros turns up about once in every million distinct items.
```

So if the longest run of leading zeros you have ever seen is 20, you have probably seen around 2²⁰, about a million, distinct items. Duplicates hash identically, so they cannot change the maximum: only *distinct* items count.

One maximum is a very noisy estimate (one lucky hash doubles it). HyperLogLog fixes this by **stochastic averaging**:

1. Use the first few bits of the hash to pick one of the **registers** (small counters): 14 bits can pick any of 16,384 registers, since 2¹⁴ = 16,384.
2. In that register, keep the maximum leading-zero count (plus one) of the remaining bits.
3. Combine all the registers into one estimate, using the formula below. Practical variants add corrections for very small and very large counts.

```formula
E = (α_m m^2) / (Σ 2^{−M_j})
E = 0.673 × 16^2 / (16 × 2^(−3))
E = 0.673 × 256 / 2 ≈ 86
where
E: the raw estimated number of distinct items, before small- or large-range corrections
m: the number of registers, a power of two; here 16 (Redis uses 16,384)
j: the register index, from one through m
M_j: the value stored in register number j, initially zero and then its largest leading-zero count plus one; here every register holds 3
Σ: "sum of", adding the term after it over all m registers, j = 1 to m
α_m: alpha-m, a correction constant that depends on m; 0.673 for m = 16, about 0.7213 / (1 + 1.079 / m) for m of 128 or more
^: "to the power of"; 2^(−3) = 1/8
≈: approximately equal to
In words: turn each register into 2 to the minus its value, add those up, and divide m squared by the total; this is a harmonic mean of the registers' 2^M_j guesses, scaled up by the number of registers and corrected by α_m. Sixteen registers all holding 3 give an estimate of about 86 distinct items.
```

A harmonic mean (the reciprocal of the average of reciprocals) is used because it is barely moved by one register that got a lucky long run of zeros. The error of the estimate shrinks as you add registers:

```formula
σ ≈ 1.04 / √(m)
σ ≈ 1.04 / √(16384) = 1.04 / 128
σ ≈ 0.0081 ≈ 0.81%
where
σ: sigma, the relative standard error: the typical size of the estimate's error as a fraction of the true count
m: the number of registers, here 16,384
√: square root; √16384 = 128
≈: approximately equal to
%: per cent, parts per hundred
In words: the typical error is 1.04 divided by the square root of the number of registers, so 16,384 registers give about 0.81%; quadrupling the registers halves the error.
```

This is a typical (standard) error, not a maximum. Treating the error as roughly normally distributed, about 1 estimate in 20 is off by more than twice the standard error, and about 1 in 370 by more than three times. More registers, less error, and memory grows only with m, not with the count.

## Key takeaways
- Registers retain maximum leading-zero ranks after bucket selection.
- Harmonic aggregation reduces sensitivity to a lucky large rank.
- Standard error shrinks with the square root of register count and is not a maximum error.

## Further reading
- [HyperLogLog — Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog)
- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (Flajolet et al., 2007)](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [HyperLogLog — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [HyperLogLog in Practice (Heule, Nunkesser and Hall, Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
