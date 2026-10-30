---
id: hash-prob-hll-registers
title: HyperLogLog registers and standard error
level: advanced
minutes: 4
sourceLesson: hash-probabilistic
summary: HyperLogLog estimates distinct counts from the longest runs of leading zeros in hashes, with error that shrinks only as the square root of memory.
---

HyperLogLog counts distinct items without keeping them. A rare leading-zero pattern in a hash suggests scale, and many registers reduce the noise of relying on a single maximum.

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

Each bit of a good hash is 0 or 1 with equal chance, independently of the others, so each extra leading zero halves the chance: a hash starting with 20 zeros turns up about once in every 2²⁰ (about a million) distinct items. So if the longest run of leading zeros you have ever seen is 20, you have probably seen around a million distinct items. Duplicates hash identically, so they cannot change the maximum: only *distinct* items count.

> [!analogy] Real-world analogy: the longest run of heads
> Ask a crowd to toss coins and report their longest run of heads in a row. If the best anyone reports is 2, there were probably only a few tossers; if someone reports 20, there were probably about a million. One person getting very lucky can mislead you, so you split the crowd into groups and combine every group's best.
>
> **How it maps:** each distinct item's hash is one person's sequence of tosses, leading zeros are the run of heads, a register is one group's best run, and combining groups is HyperLogLog's averaging.
>
> **Where it stops:** a person who tosses twice gets a fresh run; a repeated item produces exactly the same hash, which is why duplicates cannot inflate the count.

One maximum is a very noisy estimate (one lucky hash doubles it). HyperLogLog fixes this by **stochastic averaging**:

1. Use the first few bits of the hash to pick one of the **registers** (small counters): 14 bits can pick any of 16,384 registers, since 2¹⁴ = 16,384.
2. In that register, keep the maximum leading-zero count (plus one) of the remaining bits.
3. Combine all the registers with a *harmonic mean* (the reciprocal of the average of reciprocals), scaled by the number of registers and a correction constant. A harmonic mean is barely moved by one register that got a lucky long run of zeros. Practical variants add corrections for very small and very large counts.

```formula reference
E = (α_m m^2) / (Σ 2^(−M_j))
where
E: the raw estimated number of distinct items, before small- or large-range corrections
m: the number of registers, a power of two (Redis uses 16,384)
j: the register index, from 1 to m
M_j: the value stored in register number j: zero initially, then the largest leading-zero count plus one seen there
Σ: "sum of", adding the term after it over all m registers
α_m: alpha-m, a correction constant that depends on m; about 0.7213 / (1 + 1.079 / m) for m of 128 or more
^: "to the power of"
In words: turn each register into 2 to the minus its value, add those up, and divide the square of the register count by the total, then scale by the correction constant. This is a scaled harmonic mean of the registers' individual guesses.
```

### Accuracy grows slowly with memory

The estimate's typical error shrinks as you add registers, but only with the square root of their number: it is about 1.04 divided by the square root of the register count.

```formula reference
σ ≈ 1.04 / √(m)
where
σ: sigma, the relative standard error: the typical size of the estimate's error as a fraction of the true count
m: the number of registers
√: square root
≈: approximately equal to
In words: 16,384 registers give a typical error of about 0.81%. Halving the error needs four times as many registers, and so about four times the memory.
```

This is a typical (standard) error, not a maximum. Treating the error as roughly normally distributed, about 1 estimate in 20 is off by more than twice the standard error, and about 1 in 370 by more than three times. Memory grows only with the number of registers, not with the count being estimated.

## Key takeaways
- Registers retain maximum leading-zero ranks after bucket selection.
- Harmonic aggregation reduces sensitivity to a lucky large rank.
- Standard error shrinks with the square root of register count and is not a maximum error.

## Further reading
- [HyperLogLog — Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog)
- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (Flajolet et al., 2007)](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [HyperLogLog — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [HyperLogLog in Practice (Heule, Nunkesser and Hall, Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
