---
id: hash-prob-hll-merging
title: Merging HyperLogLogs and choosing a sketch
level: advanced
minutes: 3
sourceLesson: hash-probabilistic
summary: Compatible sketches merge by register maxima, so duplicates across servers are counted once in the union estimate.
---

Compatible sketches merge by register maxima, so duplicates across servers are counted once in the union estimate. Subtracting approximate counts to estimate a tiny overlap is much less reliable.

## HyperLogLog in practice

Redis's HyperLogLog (`PFADD`, `PFCOUNT`) uses sixteen thousand three hundred and eighty-four registers of 6 bits each: 12 KiB of dense register storage plus metadata per sketch, with a standard error of about 0.81%, using a sixty-four-bit hash space. Accuracy degrades near that hash-space limit because distinct inputs can share hashes; the usual error figure is not a guarantee across the entire range. Small sketches are stored sparsely and use far less.

HyperLogLogs with matching hash/seed and register configuration are **mergeable sketches**: the union of two sketches is the register-by-register maximum. That makes them ideal for distributed counting, since each server keeps its own sketch and you merge them for the total, or for rollups, where 30 daily sketches merge into a monthly unique count without double-counting repeat visitors. Intersections are another matter. The usual trick is **inclusion–exclusion**: add the two sets' counts and subtract the count of their union, because items in both sets were counted twice.

```formula reference
|A ∩ B| = |A| + |B| − |A ∪ B|
where
A: one set, such as the visitors on one day
B: another set, such as the visitors on another day
|A|: the number of distinct items in A (its cardinality)
|B|: the number of distinct items in B
∩: intersection, the items in both sets
∪: union, the items in either set; with HyperLogLog, its count comes from the merged sketch
In words: the overlap is the two counts added together minus the combined count.
```

The trouble is that every term is an estimate. Suppose two days each have about 1,000,000 visitors and the merged sketch estimates 1,995,000: the subtraction suggests an overlap of 5,000. But each of the three estimates carries a standard error of about 0.81%, roughly 8,000 to 16,000 visitors here, which is larger than the overlap itself. Inclusion–exclusion with HyperLogLog is unreliable when the overlap is small compared with the sets.

Google's **HyperLogLog++** improves the small-cardinality range with bias correction and a sparse representation; BigQuery's `APPROX_COUNT_DISTINCT` is built on it.

## Choosing a structure

| Question | Use | Memory |
|---|---|---|
| Have I seen x? | Bloom filter | ~10 bits per item (1%) |
| How often x? | Count-Min | rows times counters per row |
| How many distinct? | HyperLogLog | ~12 KiB register payload, ~1% standard error |

None of them store the items themselves. If you need the items back, or exact answers, you need a real hash set or map.

## Key takeaways
- Compatible HyperLogLogs merge by register-wise maxima.
- A small intersection derived by subtracting approximate large counts can be unreliable.
- Membership, frequency and distinct-count sketches answer different questions and cannot enumerate items.

## Further reading
- [HyperLogLog — Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog)
- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (Flajolet et al., 2007)](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [HyperLogLog — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [HyperLogLog in Practice (Heule, Nunkesser and Hall, Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
