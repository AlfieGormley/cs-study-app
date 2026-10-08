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

- **Add x**: run x through all k hash functions and set each of the k bits they pick to 1.
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
> The previously claimed measured 0.84% rate is omitted: no benchmark dataset, query sample or reproducible measurement accompanied it. The formulas below are modelled estimates, not measurements of this implementation.

### The false-positive maths

Assume the hashes behave like independent, uniformly random choices, and count n distinct items (adding the same item twice sets no new bits). Each time a bit is set, a particular bit is missed with probability 1 − 1/m. Adding n items sets bits k × n times, so the chance that a given bit is still 0 is:

```formula
q = (1 − 1 / m)^(k × n) ≈ e^(−k × n / m)
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
p ≈ (1 − e^(−k × n / m))^k
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
In words: a bit is set with probability about 0.503, and a false positive needs all 7 of the query's bits set, so 0.503 multiplied by itself 7 times: about 0.8%, or 1 query in 120.
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

With k = 1 the same filter gives about 9.5%; with k = 14, about 1.9%.

**Sizing.** Turn the question round: given a target false-positive rate, how many bits does each item need? At the optimal k:

```formula
m / n = −ln(p) / (ln(2))^2
m / n ≈ 1.44 × log_2(1 / p)
m / n = −ln(0.01) / 0.4805
m / n = 4.605 / 0.4805 ≈ 9.6 bits
where
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

- **Add x**: in each row, increment the counter that row's hash function picks for x.
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

You size a Count-Min Sketch from two numbers: how big an error you accept, as a fraction of the whole stream, and how often you allow that limit to be broken. Assume independent rows using suitable universal hashes (lesson 2), nonnegative updates and counters that never overflow. Then choose:

```formula
w = ⌈e / ε⌉
d = ⌈ln(1 / δ)⌉
w = ⌈2.718 / 0.001⌉ = ⌈2718.3⌉ = 2719
d = ⌈ln(100)⌉ = ⌈4.61⌉ = 5
where
w: the width, the number of counters in each row
d: the depth, the number of rows (and of hash functions)
ε: epsilon, the allowed error as a fraction of the stream total, here 0.001 (0.1%)
δ: delta, the allowed probability of exceeding that error, here 0.01 (1%)
e: Euler's number, about 2.718
ln: the natural logarithm (base e); ln(100) ≈ 4.61
⌈ ⌉: ceiling, round up to the next whole number
In words: the width sets how big the error can be and the depth sets how rarely it is exceeded; for 0.1% error with 99% confidence you need 5 rows of 2,719 counters, about 13,600 counters in all.
```

With those sizes, the guarantee for any single item, fixed before the hash functions are chosen, is:

```formula
c_est ≤ c_true + ε × N
c_est ≤ c_true + 0.001 × 100,000,000
c_est ≤ c_true + 100,000
where
c_est: the count the sketch reports for the item
c_true: the item's real count in the stream
ε: epsilon, the error fraction the sketch was sized for, here 0.001
N: the total of all counts in the stream, here 100 million events
≤: "is at most"; the bound holds with probability at least 1 − δ (here 99%)
In words: the estimate never undercounts, and with 99% probability it overcounts by at most 0.1% of the whole stream: 100,000 for a 100-million-event stream, however many distinct items there are.
```

This is not a simultaneous guarantee for all items at once, nor for queries chosen after seeing the hash functions.

That error is relative to the *total* N, not to the item's own count, so the sketch is accurate for **heavy hitters** (frequent items) and nearly useless for rare ones: an item seen 10 times may be reported as tens of thousands. Tracking top items also requires a candidate-tracking algorithm, since the sketch cannot enumerate keys; a heap can form part of that design.

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
E = α_m × m^2 / Σ 2^(−M_j)
E = 0.673 × 16^2 / (16 × 2^(−3))
E = 0.673 × 256 / 2 ≈ 86
where
E: the estimated number of distinct items
m: the number of registers, a power of two; here 16 (Redis uses 16,384)
M_j: the value stored in register number j (its largest leading-zero count plus one); here every register holds 3
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
σ ≈ 0.0081 = 0.81%
where
σ: sigma, the relative standard error: the typical size of the estimate's error as a fraction of the true count
m: the number of registers, here 16,384
√: square root; √16384 = 128
≈: approximately equal to
%: per cent, parts per hundred
In words: the typical error is 1.04 divided by the square root of the number of registers, so 16,384 registers give about 0.81%; quadrupling the registers halves the error.
```

This is a typical (standard) error, not a maximum. Treating the error as roughly normally distributed, about 1 estimate in 20 is off by more than twice the standard error, and about 1 in 370 by more than three times. More registers, less error, and memory grows only with m, not with the count.

### In practice

Redis's HyperLogLog (`PFADD`, `PFCOUNT`) uses m = 16,384 registers of 6 bits each: 12 KiB of dense register storage plus metadata per sketch, with a standard error of about 0.81%, for cardinalities up to 2⁶⁴. Small counters are stored sparsely and use far less.

HyperLogLogs with matching hash/seed and register configuration are **mergeable**: the union of two sketches is the register-by-register maximum. That makes them ideal for distributed counting, since each server keeps its own sketch and you merge them for the total, or for rollups, where 30 daily sketches merge into a monthly unique count without double-counting repeat visitors. Intersections are another matter. The usual trick is **inclusion–exclusion**:

```formula
|A ∩ B| = |A| + |B| − |A ∪ B|
|A ∩ B| = 1000000 + 1000000 − 1995000
|A ∩ B| = 5000
where
A: the set of visitors on one day
B: the set of visitors on another day
|A|: the number of distinct items in A (its cardinality), here an estimate of 1,000,000
|B|: the number of distinct items in B, here an estimate of 1,000,000
∩: intersection, the items in both sets
∪: union, the items in either set; |A ∪ B| comes from the merged sketch, here 1,995,000
In words: the overlap is the two counts added together minus the combined count, because items in both sets were counted twice.
```

Each of the three estimates has a standard error of about 0.81%, roughly 8,000 to 16,000 here, which is larger than the 5,000 overlap itself. Inclusion–exclusion with HyperLogLog is unreliable when the overlap is small compared with the sets.

Google's **HyperLogLog++** improves the small-cardinality range with bias correction and a sparse representation; BigQuery's `APPROX_COUNT_DISTINCT` is built on it.

## Choosing a structure

| Question | Use | Memory |
|---|---|---|
| Have I seen x? | Bloom filter | ~10 bits per item (1%) |
| How often x? | Count-Min | w × d counters |
| How many distinct? | HyperLogLog | ~12 KiB register payload, ~1% standard error |

None of them store the items themselves. If you need the items back, or exact answers, you need a real hash set or map.

## Key takeaways
- Bloom filters answer membership with no false negatives and a false-positive rate you tune with the bits per item and the number of hash functions.
- The best number of hash functions is about 0.69 × bits per item; about 9.6 bits per item gives 1%, and each further factor of 10 costs about 4.8 bits, independent of item size.
- Count-Min Sketch takes the minimum of one hashed counter per row; it only overestimates, by at most a chosen fraction of the whole stream with a chosen probability, so it suits heavy hitters.
- HyperLogLog estimates distinct counts from the maximum leading zeros in hashes, split across many registers; the error is about 1.04 divided by the square root of the register count (about 0.81% standard error for 12 KiB of dense registers in Redis).
- All three are built on hashing that behaves randomly; LSM databases, CDNs, caches and analytics engines rely on them.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Count–min sketch — Wikipedia](https://en.wikipedia.org/wiki/Count%E2%80%93min_sketch)
- [HyperLogLog — Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog)
- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (Flajolet et al., 2007)](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [HyperLogLog — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [HyperLogLog in Practice (Heule, Nunkesser and Hall, Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
