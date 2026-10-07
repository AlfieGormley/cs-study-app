---
id: hash-probabilistic
title: Probabilistic structures
level: advanced
minutes: 14
summary: Bloom filters, Count-Min Sketch and HyperLogLog trade a small, controllable error for enormous memory savings; this lesson covers how they work, the false-positive maths, and where databases and Redis use them.
---

An exact hash set of a billion 20-byte keys needs tens of gigabytes. Often you do not need an exact answer. "Is this key *possibly* on disk?", "roughly how often has this IP appeared?" and "about how many unique visitors today?" can be answered in kilobytes or megabytes if you accept a small, known error.

All three structures in this lesson rely on the same idea: a good hash function makes its output look random, so you can reason about collisions with probability, and then size the structure to make errors as rare as you like.

| Structure | Answers | Error |
|---|---|---|
| Bloom filter | "is x in the set?" | false positives only |
| Count-Min Sketch | "how many times x?" | overestimates only |
| HyperLogLog | "how many distinct?" | ± a few % |

## Bloom filters

A **Bloom filter** (Burton Bloom, 1970) is a bit array of m bits, all 0, plus k hash functions that each map an item to one of the m positions.

- **Add x**: set the k bits h₁(x), …, hₖ(x) to 1.
- **Query x**: if *any* of those k bits is 0, x was definitely never added. If all are 1, x was *possibly* added. Its probability of membership also depends on how often queried items are actually members.

```
m = 16, k = 3
add "cat": bits 2, 7, 11
add "dog": bits 4, 7, 13

idx  0123456789012345
     0010100100010100

query "eel": bits 2, 4, 13 -> all 1
             -> "maybe" (false positive)
query "fox": bits 3, 7, 11 -> bit 3 is 0
             -> "definitely not"
```

"eel" was never added, but other items happened to set all of its bits. That is a **false positive**. There are never **false negatives**: an added item's bits stay set, because nothing ever clears a bit.

```python
from hashlib import sha256

class Bloom:
    def __init__(self, m, k):
        if type(m) is not int or m <= 0:
            raise ValueError("positive m")
        if type(k) is not int or k <= 0:
            raise ValueError("positive k")
        self.m, self.k = m, k
        # 1 bool per bit (real ones pack)
        self.bits = [False] * m

    def _idx(self, item):
        d = sha256(item.encode()).digest()
        h1 = int.from_bytes(d[:8])
        h2 = int.from_bytes(d[8:16]) | 1
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for j in self._idx(item):
            self.bits[j] = True

    def __contains__(self, item):
        return all(self.bits[j]
                   for j in self._idx(item))
```

Computing k separate hashes would be slow. The `h1 + i*h2` trick, due to Kirsch and Mitzenmacher, derives all k positions from two hashes with the same asymptotic false-positive probability under the paper's model; this does not promise identical finite-filter accuracy. The odd step is coprime to power-of-two m, but not to every composite m.

> [!note] Evidence gap
> The previously claimed measured 0.84% rate is omitted: no benchmark dataset, query sample or reproducible measurement accompanied it. The formulas below are modeled estimates, not measurements of this implementation.

### The false-positive maths

Under independent uniform hashes for n distinct items (duplicate insertion does not add new positions), the chance that a given bit is still 0 is

```
(1 - 1/m)^(kn)  ≈  e^(-kn/m)
```

A false positive needs all k of a new item's bits to be 1:

```
p ≈ (1 - e^(-kn/m))^k
```

Worked example: m = 1,000 bits, n = 100 items, k = 7.

1. kn/m = 700/1000 = 0.7.
2. e^(−0.7) ≈ 0.497, so a bit is set with probability 0.503.
3. p ≈ 0.503⁷ ≈ 0.0082, about 0.8%.

**Choosing k.** Too few hashes and each query checks too few bits; too many and the array fills with 1s. The optimum is

```
k = (m/n) * ln 2  ≈  0.69 * (m/n)
```

which leaves about half the bits set. For m/n = 10, k ≈ 6.9, so 7. With k = 1 the same filter gives about 9.5%; with k = 14, about 1.9%.

**Sizing.** At the optimal k, the bits needed per item for a target rate p are

```
m/n = -ln(p) / (ln 2)^2  ≈  1.44 * log2(1/p)
```

| Target p | Bits per item | k |
|---|---|---|
| 1% | 9.6 | 7 |
| 0.1% | 14.4 | 10 |
| 0.01% | 19.2 | 13 |

Notice what is *not* in the formula: the size of the items. A billion 100-byte URLs need about 1.2 GB for a 1% filter, versus over 100 GB to store them. Each factor of 10 improvement in p costs about 4.8 more bits per item.

> [!warning] Overfilling
> The false-positive rate climbs fast past the design capacity. The 1,000-bit, k = 7 filter above gives 0.8% at 100 items but about 14% at 200. Size for the maximum n you expect, or use a scalable Bloom filter that adds layers as it grows.

### Limitations

- **No deletion.** Clearing a bit might also "remove" other items that share it, creating false negatives. **Counting Bloom filters** replace each bit with a small counter (often 4 bits) at about 4 times the memory; cuckoo filters also support deletion. Deletion requires knowing the item was inserted; deleting a false positive can damage other members, and counting filters must avoid counter overflow.
- **No listing.** You cannot get the items back out.
- **Fixed size.** You cannot simply grow the bit array and redistribute positions without the original items; scalable filters instead add compatible layers.

### Where they are used

- **LSM-tree databases** (RocksDB, LevelDB, Cassandra, HBase) can use per-SSTable Bloom filters, depending on configuration. A read for a key checks the filter first and skips any file that definitely does not contain it, avoiding a disk read. RocksDB's commonly used setting of 10 bits per key gives about 1% false positives; Cassandra exposes `bloom_filter_fp_chance` per table.
- **CDNs**: Akamai found that a large fraction of objects are requested only once. A Bloom filter can approximate second-request admission and reduce caching of one-hit objects; false positives can still admit some on their first request.
- **Redis** offers Bloom filters (`BF.ADD`, `BF.EXISTS`) through its probabilistic data types.

## Count-Min Sketch

A **Count-Min Sketch** (Cormode and Muthukrishnan, 2005) estimates how often each item appears in a stream. It is a grid of d rows by w counters, with one hash function per row.

- **Add x**: in each row i, increment counter `hᵢ(x)`.
- **Query x**: return the **minimum** of x's d counters.

```
w = 8, d = 3 (counts after a stream)

row 0: 0 5 0 2 0 9 0 1
row 1: 3 0 0 7 1 0 0 6
row 2: 0 0 4 0 8 0 2 3

x hashes to row0[5], row1[3], row2[4]
counters: 9, 7, 8  -> estimate 7
```

Every counter x touches includes x's true count plus whatever else collided there. Collisions can only *add*, so every counter is an overestimate (with non-negative updates), and the minimum is the least polluted one.

```python
class CountMin:
    def __init__(self, w, d):
        if type(w) is not int or w <= 0:
            raise ValueError("positive w")
        if type(d) is not int or d <= 0:
            raise ValueError("positive d")
        self.w, self.d = w, d
        self.t = [[0] * w for _ in range(d)]

    def _col(self, item, i):
        return hash((i, item)) % self.w

    def add(self, item, n=1):
        if type(n) is not int or n < 0:
            raise ValueError("negative n")
        for i in range(self.d):
            c = self._col(item, i)
            self.t[i][c] += n

    def count(self, item):
        return min(
            self.t[i][self._col(item, i)]
            for i in range(self.d))
```

This fragment demonstrates the counter/minimum mechanism. Python hash((i, item)) is not an independently sampled universal family, so the formal error bound below is not established for this sample. It still never undercounts under its enforced nonnegative updates, provided keys retain stable hashes.

### Error guarantee

For independent rows using suitable universal hashes, nonnegative updates and counters without overflow, if N is the total of all counts, choosing

```
w = ceil(e / eps)
d = ceil(ln(1 / delta))
```

guarantees that the estimate is at most the true count plus εN, with probability at least 1 − δ.

Example: ε = 0.001 and δ = 0.01 give w = 2,719 and d = 5, about 13,600 counters. For a stream of 100 million events, a fixed point query has error at most 100,000 with probability at least 99% over the random hash choices, independently of the number of distinct items. This is not a simultaneous guarantee for all or adaptively chosen queries.

That error is relative to the *total* N, so the sketch is accurate for **heavy hitters** (frequent items) and nearly useless for rare ones: an item seen 10 times may be reported as tens of thousands. Tracking top items also requires a candidate-tracking algorithm, since the sketch cannot enumerate keys; a heap can form part of that design.

Count-Min Sketches appear in network monitoring (top talkers by IP), trending-topic detection, and caches: the Caffeine library's W-TinyLFU policy keeps approximate access frequencies in a Count-Min-style sketch of 4-bit counters to decide which items deserve a place in the cache.

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

A hash starting with r zeros turns up about once every 2^r distinct items. So if the longest run of leading zeros you have ever seen is 20, you have probably seen around 2²⁰, about a million, distinct items. Duplicates hash identically, so they cannot change the maximum: only *distinct* items count.

One maximum is a very noisy estimate (one lucky hash doubles it). HyperLogLog fixes this by **stochastic averaging**:

1. Use the first p bits of the hash to pick one of m = 2^p **registers**.
2. In that register, keep the maximum leading-zero count (plus one) of the remaining bits.
3. If register values are M[j], the raw estimate is alpha_m * m**2 / sum(2**(-M[j])). Equivalently, take the harmonic mean of 2**M[j], then multiply by alpha_m * m. Practical variants add small/large-range corrections.

The relative standard error is about **1.04 / √m**, not a maximum-error bound for each estimate. More registers, less error, and memory grows only with m, not with the count.

### In practice

Redis's HyperLogLog (`PFADD`, `PFCOUNT`) uses m = 16,384 registers of 6 bits each: 12 KiB of dense register storage plus metadata per sketch, with a standard error of about 0.81%, for cardinalities up to 2⁶⁴. Small counters are stored sparsely and use far less.

HyperLogLogs with matching hash/seed and register configuration are **mergeable**: the union of two sketches is the register-by-register maximum. That makes them ideal for distributed counting, since each server keeps its own sketch and you merge them for the total, or for rollups, where 30 daily sketches merge into a monthly unique count without double-counting repeat visitors. Intersections are another matter: estimating |A ∩ B| by inclusion–exclusion compounds the errors and is unreliable when the overlap is small.

Google's **HyperLogLog++** improves the small-cardinality range with bias correction and a sparse representation; BigQuery's `APPROX_COUNT_DISTINCT` is built on it.

## Choosing a structure

| Question | Use | Memory |
|---|---|---|
| Have I seen x? | Bloom filter | ~10 bits per item (1%) |
| How often x? | Count-Min | w × d counters |
| How many distinct? | HyperLogLog | ~12 KiB register payload, ~1% standard error |

None of them store the items themselves. If you need the items back, or exact answers, you need a real hash set or map.

## Key takeaways
- Bloom filters answer membership with no false negatives and a tunable false-positive rate p ≈ (1 − e^(−kn/m))^k.
- Optimal k = (m/n) ln 2; about 9.6 bits per item gives 1%, and each further factor of 10 costs about 4.8 bits, independent of item size.
- Count-Min Sketch takes the minimum over d hashed counters; it only overestimates, by at most εN with probability 1 − δ, so it suits heavy hitters.
- HyperLogLog estimates distinct counts from the maximum leading zeros in hashes, split across m registers; error ≈ 1.04/√m (about 0.81% standard error for 12 KiB of dense registers in Redis).
- All three are built on hashing that behaves randomly; LSM databases, CDNs, caches and analytics engines rely on them.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Count–min sketch — Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
- [HyperLogLog — Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog)
- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (Flajolet et al., 2007)](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [HyperLogLog — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [HyperLogLog in Practice (Heule, Nunkesser and Hall, Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
