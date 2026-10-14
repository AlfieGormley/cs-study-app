---
id: cache-stale-refills-and-double-delete
title: Trace stale refills after invalidation
level: intermediate
minutes: 3
summary: Explain the cache-aside reader/writer race and the timing limit of delayed double delete.
sourceLesson: cache-invalidation
---

Deleting after a database commit avoids racing cache updates, but a reader may already have fetched an old row. Its later refill can resurrect that row after the delete.

## Race 2: the cache-aside read/write race

Delete-on-write still has a race, involving a slow reader.

```
 Reader R                Writer W
 GET -> miss
 SELECT -> old value
                         UPDATE -> new
                         DEL key
 SET key = old value
```

R read the old row before W committed, but its `SET` lands after W's `DEL`. The cache now holds the old value with a fresh TTL, and nobody will delete it again.

This interleaving is possible even without an exceptional pause; its frequency depends on the workload. Pauses and network delays widen the opportunity. Facebook's memcache paper calls a write like R's a **stale set**: a value put into the cache that no longer reflects the latest data.

### Mitigations

- **Short TTLs** bound how long the bad value survives.
- **Delayed double delete**: delete, then delete again after a delay longer than nearly all miss-path reads take (say 500 ms). It narrows the window but is a heuristic, not a guarantee.
- **Leases** (covered in the following units) reject fills whose token was revoked by an invalidation, when the cache enforces that protocol.
- **Versioned writes** (covered in the following units) make stale sets lose.

For the delayed double delete, the second delete only helps if it lands after the slow reader's `SET`. So the delay has to be longer than the slowest read you want to cover:

```formula
d > t_read
where
d: the delay between the first and the second delete, in milliseconds (ms)
t_read: the time a reader takes from its database read to its cache SET, in ms; pick a high percentile such as p99.9, the time that 99.9% of reads finish within
ms: milliseconds; 1 ms = 0.001 seconds
In words: wait longer than nearly all slow readers take, then delete again to clean up any stale value they wrote.
```

For example, if 99.9% of miss-path reads finish within 400 ms, a 500 ms delay catches them. A reader stalled for 2 s (a long garbage-collection pause, say) still lands after both deletes, which is why this is only a heuristic.

## Key takeaways
- A miss-path reader can load old data, pause, and set it after a writer commits and invalidates.
- A second delete catches only refills that land before it; a delay based on a percentile remains a heuristic.
- Leases tied to invalidation and version checks with retained metadata can reject stale refills.

## Further reading
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
