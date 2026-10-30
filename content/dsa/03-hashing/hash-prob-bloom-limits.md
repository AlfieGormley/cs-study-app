---
id: hash-prob-bloom-limits
title: Bloom-filter deletion limits and database use
level: advanced
minutes: 3
sourceLesson: hash-probabilistic
summary: A shared bit does not identify which item set it.
---

A shared bit does not identify which item set it. That is why deletion and resizing need more information than an ordinary append-only Bloom filter stores.

## Limitations

- **No deletion.** Clearing a bit might also "remove" other items that share it, creating false negatives. **Counting Bloom filters** replace each bit with a small counter (often 4 bits) at about 4 times the memory; cuckoo filters also support deletion. Deletion requires knowing the item was inserted; deleting a false positive can damage other members, and counting filters must avoid counter overflow.
- **No listing.** You cannot get the items back out.
- **Fixed size.** You cannot simply grow the bit array and redistribute positions without the original items; scalable filters instead add compatible layers.

### Where they are used

- **LSM-tree databases** (RocksDB, LevelDB, Cassandra, HBase) can use per-SSTable Bloom filters, depending on configuration. A read for a key checks the filter first and skips any file that definitely does not contain it, avoiding a disk read. RocksDB's commonly used setting of 10 bits per key gives about 1% false positives; Cassandra exposes `bloom_filter_fp_chance` per table.
- **CDNs**: Akamai found that a large fraction of objects are requested only once. A Bloom filter can approximate second-request admission and reduce caching of one-hit objects; false positives can still admit some on their first request.
- **Redis** offers Bloom filters (`BF.ADD`, `BF.EXISTS`) through its probabilistic data types.

## Read a negative result against the right snapshot

An append-only filter can rule out an item only from the set represented by its current contents. If a username was created after the filter snapshot, a negative answer does not prove the live database lacks it. Publication and update ordering are part of the application’s correctness contract, separate from the filter’s mathematical no-false-negative property.

A positive answer likewise says maybe, so a service usually checks the authoritative store before rejecting a registration or skipping an operation. The false-positive rate is conditional on a queried item being absent; it is not automatically the probability that every positive answer is wrong. That latter probability also depends on how common real members are in the query workload.

For an absent-key LSM read, each candidate file’s false-positive indicator contributes to the expected number of extra reads. Add those expectations; independence is not required for that average. Independence does matter if you calculate the probability that no file is read or that several files are read together. Cached blocks, overlapping levels and range checks change the real I/O model.

## Union needs compatible filters

Two append-only filters can represent a union by OR-ing their bit arrays if they have the same bit count, position count and hash configuration. Every position set by either input then remains set, just as if both item sets had been added to one filter. The union usually contains more distinct items, so keeping the same bit array can increase false positives. Different hash seeds or sizes do not satisfy this compatibility rule.

## Key takeaways
- Shared bits prevent ordinary deletion without extra information.
- Negative answers concern the represented snapshot, not later database changes.
- Expected extra file reads add across candidate filters even without independent false positives.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Bloom filter — Redis docs](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Less hashing, same performance](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf)
