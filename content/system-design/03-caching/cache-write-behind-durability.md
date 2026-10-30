---
id: cache-write-behind-durability
title: Bound the loss window of write-back caching
level: basic
minutes: 3
summary: Calculate unflushed acknowledged writes and handle durable baselines, batching and flush ordering.
sourceLesson: cache-strategies
---

Write-back acknowledges a cache write before the database has it. That lowers latency and combines updates, but temporarily makes the cache authoritative for the unflushed changes.

## Write-back (write-behind)

Writes go to the cache only, and are acknowledged immediately. The cache flushes them to the database **later**, asynchronously, often in batches.

```
 write --> Cache (ack)
             |  later, batched
             v
             DB
```

Many CPU caches, the operating system page cache and database buffer pools use write-back: dirty data is written to the next memory or storage level later. A database can first make a transaction durable in its write-ahead log, so delayed buffer-page writes do not imply the same loss window as an unlogged application cache.

**Strengths**

- Very low write latency.
- Absorbs bursts and **coalesces** repeated writes. A counter incremented 1,000 times a second can be flushed once a second as a single write.

**Weaknesses**

- **Data loss.** If the cache node dies before flushing, the acknowledged writes are gone, unless the cache itself is durable (replicated, with a write-ahead log).
- The database is behind the cache, so anything reading the database directly (reports, other services) sees old data.
- Ordering and failure handling of the flush are hard to get right.

How much can a crash lose? Everything acknowledged since the last *successful* flush. With steady writes and on-time flushes, that is about one flush interval's worth of writes: the counter above, flushed every second, risks about a second of increments; flushed every 5 s, about five seconds' worth. Longer intervals coalesce more writes but widen the loss window. A late or failed flush makes the real window longer than the planned interval, so measure the time since the last successful flush rather than trusting the schedule.

> [!analogy] Real-world analogy: the waiter's order pad
> A busy waiter jots orders on a pad, tells each table "got it", and takes the pad to the kitchen every few minutes rather than walking back after every order.
>
> **How it maps:** The pad is the write-back cache, "got it" is the acknowledgement, and the trip to the kitchen is the batched flush to the database. Fewer trips means less walking (fewer database writes), and repeated changes to one table's order collapse into one line (coalescing).
>
> **Where it stops:** If the waiter loses the pad, the customers were already told "got it" and those orders are simply gone, which is the write-back loss window. Unlike a waiter, the cache cannot ask customers to repeat themselves, and the kitchen (database) cannot see anything still on the pad.

> [!warning] Write-back changes your source of truth
> With write-back, the cache temporarily *is* the source of truth for recent writes. You need the durability guarantees of a database from it. Use it only where its measured loss window (including delayed or failed flushes) is tolerable (view counters, analytics) or where the cache is genuinely durable.

> [!example] A social feed counter
> Likes on a viral post may arrive at 20,000 per second. A single PostgreSQL row may become a contention bottleneck; benchmark the actual transaction path. Instead, `INCR post:123:likes` in Redis (write-back) and flush the total to Postgres every few seconds. Whether any lost likes are acceptable is a product decision. Restore the baseline from durable state after cache loss and handle flush ordering/idempotency; blindly persisting a reset or old total can lose previously saved counts.

## Key takeaways
- Acknowledged changes are vulnerable until a successful flush unless the cache has adequate durability.
- The loss estimate uses the actual time since the last successful flush; delays and failures enlarge it.
- Restore durable counter baselines after cache loss and make flush ordering and retries safe.

## Further reading
- [Cache writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
