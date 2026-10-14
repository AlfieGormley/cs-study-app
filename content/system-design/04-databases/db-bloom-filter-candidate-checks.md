---
id: db-bloom-filter-candidate-checks
title: Bloom filters and candidate checks
level: advanced
minutes: 4
summary: Calculate false-positive probability and distinguish candidate-file checks from disk reads and range-scan work.
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

The standard approximation for a filter's false-positive rate, and the best number of hash functions, is:

```formula
p ≈ (1 − e^(−k × n / m))^k
k_best = (m / n) × ln(2)
where
p: the false-positive rate: the chance a key that was never added is reported as possibly present (0.01 = 1%)
k: the number of hash functions, i.e. bits set per key
n: the number of keys added to the filter
m: the number of bits in the filter
m / n: bits per key, the main tuning knob
e: Euler's number, about 2.718, the base of natural logarithms
ln: the natural logarithm (logarithm to base e); ln(2) ≈ 0.693
k_best: the number of hash functions that gives the lowest p for a given m / n
≈: approximately equal to
In words: the more bits you give each key, the lower the false-positive rate, and there's a best number of hash functions (about 0.7 per bit per key) beyond which more hashing makes it worse.
```

Worked example with 10 bits per key:

```formula
k_best = 10 × 0.693 ≈ 7
p ≈ (1 − e^(−7 / 10))^7
p ≈ (1 − 0.497)^7 ≈ 0.008
F = 1,000,000,000 × 10 bits
F = 10^10 bits = 1.25 GB
where
k_best: the best number of hash functions
p: the false-positive rate, about 0.8%, which is "about 1%"
e: Euler's number, about 2.718
F: the filter's total size for a billion keys
bits: binary digits; 8 bits make one byte
GB: gigabyte, 1,000,000,000 bytes
≈: approximately equal to
In words: 10 bits per key and 7 hash functions give a false-positive rate just under 1%, and a filter for a billion keys fits in about 1.25 GB.
```

The formula assumes the hash functions behave like independent random choices; real implementations come close. Each extra 4.8 or so bits per key cuts the rate about tenfold.

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
