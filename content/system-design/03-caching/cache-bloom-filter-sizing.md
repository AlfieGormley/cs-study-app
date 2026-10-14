---
id: cache-bloom-filter-sizing
title: Size and maintain a Bloom filter for valid keys
level: advanced
minutes: 3
summary: Calculate memory from a false-positive target and preserve complete coverage before rejecting absent IDs.
sourceLesson: cache-failure-modes
---

A stream of random invalid IDs has no repeated key for a negative cache to absorb. A compact membership filter can reject most of them before the cache or database lookup.

### Fix B: Bloom filter

A **Bloom filter** is a compact bit array that answers "is this key possibly in the set?" with **no false negatives** and a tunable false-positive rate. Put every valid id into it; check it before touching the cache or database.

```
 request id
     |
 Bloom: "definitely not"? --> 404
     | "maybe"
 cache --> DB
```

Sizing comes from the standard Bloom filter analysis. With the best number of hash functions, the bits needed per stored id depend only on the false-positive rate you accept:

```formula
b = −ln(p) / (ln 2)^2
b = −ln(0.01) / (ln 2)^2
b ≈ 4.605 / 0.4805 ≈ 9.6 bits
where
bits: binary digits; each is one 0-or-1 cell of the filter
b: the bits of filter needed per stored element
p: the false-positive rate, the chance that an id not in the set is wrongly answered "maybe"; here 0.01 (1%)
ln: the natural logarithm (logarithm to base e ≈ 2.718)
≈: approximately equal to
In words: about 9.6 bits per id buys a 1% false-positive rate; each tenfold cut in false positives costs about another 4.8 bits.
```

So **9.6 bits per element** for a 1% false-positive rate, and the whole filter is:

```formula
M = n × b / 8
M = 100,000,000 × 9.6 / 8
M = 120,000,000 B ≈ 120 MB
where
M: the filter's memory, in bytes (B)
n: the number of ids stored, here 100 million
b: the bits per element, here 9.6
8: bits per byte
B: bytes
MB: megabytes; 1 MB = 1,000,000 B
In words: 100 million ids at 9.6 bits each is 960 million bits, which is 120 MB.
```

A random invalid id is rejected 99% of the time without any database work. The formula assumes a well-chosen number of hash functions (about 7 for 1%) and that every valid id has been added.

Caveats: standard Bloom filters can't delete entries (use a counting filter or Cuckoo filter, or rebuild periodically), and new ids must be included before they become visible, or a negative result must fall back to the source while coverage is uncertain. A stale filter can otherwise reject a valid new id.

Also: **validate input** (reject malformed ids at the edge) and **rate-limit** clients that generate many misses.

## Key takeaways
- A correctly populated Bloom filter rejects definite absence and permits some false positives.
- About 9.6 bits per valid ID gives an approximate one-percent false-positive rate with an appropriate hash count.
- Keep new IDs covered before relying on negative results; ordinary Bloom filters need a variant or rebuild strategy for deletion.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Network applications of Bloom filters: a survey](https://www.eecs.harvard.edu/~michaelm/postscripts/im2005b.pdf)
