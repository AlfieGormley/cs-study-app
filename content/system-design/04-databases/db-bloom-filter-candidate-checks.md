---
id: db-bloom-filter-candidate-checks
title: Bloom filters and candidate checks
level: advanced
minutes: 4
summary: Predict how bits per key trade memory for false positives, and distinguish candidate-file checks from disk reads and range scans.
sourceLesson: db-storage-internals
---

Before searching an SSTable, cheaply rule out files that cannot contain an exact key. Bloom filters trade a small amount of memory for fewer candidate checks, with a controlled chance of false positives.

## Bloom filters

A **bloom filter** answers "is this key *possibly* in this set?" using very little memory. It never gives a false negative, and gives false positives at a tunable rate.

How it works: an array of bits, all starting at 0, plus a few independent hash functions. To add a key, hash it with each function and set the bits it lands on to 1. To check a key, test the same bits: any zero means "definitely not present". If all are 1, the key is *possibly* present, because other keys may have set those bits.

```
add "cat": h1=2 h2=5 h3=9
bits: 0 0 1 0 0 1 0 0 0 1
check "dog": h1=2 h2=4 h3=9
bit 4 is 0 → definitely absent
```

With about **10 bits per key** and the best number of hash functions (about 7), the false-positive rate is about **1%**. A billion keys need ~1.2 GB of filter, a fraction of the data size.

The trade-off is memory for accuracy. Give each key more bits and fewer absent keys look present; each extra 4.8 or so bits per key cuts the false-positive rate about tenfold. More hash functions help only up to a point (about 0.7 per bit per key); beyond that they fill the array with ones and make things worse.

```formula reference
p ≈ (1 − e^(−k × n / m))^k
where
p: the false-positive rate: the chance a key that was never added is reported as possibly present (0.01 = 1%)
k: the number of hash functions, i.e. bits set per key
n: the number of keys added to the filter
m: the number of bits in the filter, so m / n is the bits per key
e: Euler's number, about 2.718, the base of natural logarithms
≈: approximately equal to; it assumes the hash functions behave like independent random choices
In words: the false-positive rate falls quickly as you give each key more bits, provided the number of hash functions suits the bits per key.
```

In an LSM tree, each SSTable has a filter. A read for a missing key consults filters for every level and skips almost all of them, so a lookup may need far fewer candidate-file checks. False positives still require checking metadata or cached/disk blocks; there is no guarantee of at most one file read. RocksDB, Cassandra (`bloom_filter_fp_chance`), HBase and Bigtable all do this.

Whole-key Bloom filters cannot exclude an arbitrary range using one membership test. A range iterator merges candidate sorted runs; key bounds and other metadata can still prune work. RocksDB's prefix bloom filters help when ranges share a prefix.

## Key takeaways
- A negative Bloom result excludes a key; a positive result only permits a follow-up check.
- Bits per key and hash count set the approximate false-positive rate.
- Exact-key filters do not solve arbitrary ranges; shared-prefix filtering serves a narrower use case.

## Further reading
- [github.com: RocksDB Bloom Filter](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)
- [RocksDB: Prefix seek](https://github.com/facebook/rocksdb/wiki/Prefix-Seek)
- [Wikipedia: Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter)
