---
id: cache-bloom-filter-sizing
title: Size and maintain a Bloom filter for valid keys
level: advanced
minutes: 3
summary: Relate memory to a false-positive target and preserve complete coverage before rejecting absent IDs.
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

Sizing comes from the standard Bloom filter analysis. With the best number of hash functions, the bits needed per stored id depend only on the false-positive rate you accept, not on how long the ids are:

```formula reference
b = −ln(p) / (ln 2)^2
where
b: the bits of filter needed per stored element
p: the false-positive rate, the chance that an id not in the set is wrongly answered "maybe", for example 0.01 (1%)
ln: the natural logarithm (logarithm to base e ≈ 2.718)
In words: about 9.6 bits per id buys a 1% false-positive rate; each tenfold cut in false positives costs about another 4.8 bits.
```

So the filter's size grows in step with the number of valid ids, and only slowly as you demand fewer false positives. At about 9.6 bits per id, 100 million ids need about 120 MB, small enough to keep in memory on each server or in Redis. Cutting false positives from 1% to 0.1% costs about 50% more memory, not ten times more.

A random invalid id is rejected 99% of the time without any database work. The other 1% fall through to the cache and database as before, so the filter cuts penetration traffic a hundredfold rather than to zero. The formula assumes a well-chosen number of hash functions (about 7 for 1%) and that every valid id has been added.

Caveats: standard Bloom filters can't delete entries (use a counting filter or Cuckoo filter, or rebuild periodically), and new ids must be included before they become visible, or a negative result must fall back to the source while coverage is uncertain. A stale filter can otherwise reject a valid new id.

Also: **validate input** (reject malformed ids at the edge) and **rate-limit** clients that generate many misses.

## Key takeaways
- A correctly populated Bloom filter rejects definite absence and permits some false positives.
- About 9.6 bits per valid ID gives an approximate one-percent false-positive rate with an appropriate hash count.
- Keep new IDs covered before relying on negative results; ordinary Bloom filters need a variant or rebuild strategy for deletion.

## Further reading
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Network applications of Bloom filters: a survey](https://www.eecs.harvard.edu/~michaelm/postscripts/im2005b.pdf)
