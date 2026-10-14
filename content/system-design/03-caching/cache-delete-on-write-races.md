---
id: cache-delete-on-write-races
title: Prefer deletion when concurrent writers race
level: intermediate
minutes: 3
summary: Trace stale reads and out-of-order cache updates, then explain why delete-on-write is the safer default.
sourceLesson: cache-invalidation
---

> There are only two hard things in Computer Science: cache invalidation and naming things. — Phil Karlton

A cache holds a copy. The moment the original changes, the copy is wrong. **Cache invalidation** is how you bring the copy back in line, and it is hard because the cache and the database are two separate systems with no shared transaction. Any sequence of operations across them can be interleaved with other requests, or fail halfway.

These invalidation units concern the cache-aside world (app, Redis, database), which is where most of these bugs live.

## The options for keeping a cache fresh

1. **Expire it (TTL).** Bound the lifetime of a cached copy after insertion. Data can be older than one TTL if a delayed read or lagging replica refills the cache.
2. **Delete it on write.** The writer removes the key; the next read reloads.
3. **Update it on write.** The writer sets the new value in the cache.
4. **Let the database tell you.** Stream the database's change log and invalidate from that.

Nearly every production design is TTL plus one of the others. TTL limits the residence of one copy; repeated stale refills can extend the age of data served.

## Stale reads are the normal case

Even a perfect design has a short window where the cache is stale:

```
 t1  writer: UPDATE row (commit)
 t2  reader: GET key -> old value
 t3  writer: DEL key
```

Between t1 and t3 readers see the old value. The window depends on request timing, failures and invalidation delivery; whether it is tolerable is a product requirement. The real problems are races that leave stale data in the cache for a whole freshly started TTL, or longer if later refills are also stale.

## Race 1: update-on-write with concurrent writers

Two requests update the same user at almost the same time, and each writes the DB then sets the cache.

```
 A: UPDATE name='Ann'
 B: UPDATE name='Bea'      (DB = Bea)
 B: SET cache 'Bea'
 A: SET cache 'Ann'        (cache = Ann)
```

The database says `Bea`, the cache says `Ann`, and it stays wrong until the TTL. Network delays make A's cache write arrive after B's even though A's database write came first.

**This is why deleting is preferred over updating.** Deletes are idempotent and commutative: two deletes in either order leave the same result (an empty key), and the next reader loads the true value.

## Delete vs update: summary

| | Delete on write | Update on write |
|---|---|---|
| Concurrent writers | Deletes commute | Can leave old value |
| Next read | Miss | Hit |
| Expensive values | Recompute on read | Recompute on write |
| Hot keys | Herd risk on miss | No miss |

Delete is the safe default. Update (with versioning) is worth it for hot keys where a miss would cause a stampede.

## Key takeaways
- Database and cache operations can interleave or fail separately, leaving a stale copy.
- Two deletes commute; two independent cache updates can finish in the wrong order.
- Keep a TTL alongside explicit invalidation, while remembering stale refills can carry older source data.

## Further reading
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [TwoHardThings — Martin Fowler](https://martinfowler.com/bliki/TwoHardThings.html)
