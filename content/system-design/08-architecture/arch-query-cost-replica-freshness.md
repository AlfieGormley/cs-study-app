---
id: arch-query-cost-replica-freshness
title: Cheap queries and fresh replica reads
level: intermediate
minutes: 5
summary: Reduce avoidable query work before spreading reads across replicas with an explicit freshness rule.
sourceLesson: arch-scaling-reads
---

Many read-heavy applications, such as feeds and catalogues, benefit from serving copies of data; measure the actual read/write mix instead of assuming a universal ratio. That's good news, because reads are easier to scale than writes: you can **copy data** and serve it from many places.

Every technique in this lesson is a form of the same trade:

> [!note] The core trade
> Do more work (or store more copies) at **write time** so that **read time** is cheap. The costs can include storage, maintenance work and either staleness or stronger coordination to keep copies current.

## Step 0: make each read cheaper

Before adding infrastructure, check the basics:

- **Indexes** that match your query patterns (compare execution plans and measured latency with representative data).
- **Avoid N+1 queries**: fetch 50 posts and their authors in 2 queries, not 51.
- **Return less**: paginate, select only needed columns.
- **Connection pooling**, so the database isn't spending its time on connection setup.

Measure their benefit before adding infrastructure; gains depend on the original bottleneck.

The N+1 pattern is worth spelling out, because ORMs produce it silently. This partial Python example assumes a database adapter that returns mutable post objects; the timings are hypothetical, not observed output:

```python
# Fetch the page before its related users.
posts = db.query("SELECT * FROM posts"
                 " LIMIT 50")
# Each lookup adds a serial database call.
for p in posts:          # 50 more
    p.author = db.get_user(p.author_id)
# Assume 1 ms per serial round trip:
# 51 round trips = 51 ms (network only)
# vs 2 queries (IN (...)) = ~2 ms
# Query execution time is additional.
```

The name comes from the count: one query for the list, then one more per item. When each query has to wait for its own network round trip, the time spent just on round trips is:

```formula
T = (N + 1) × t
T = (50 + 1) × 1 ms = 51 ms
where
T: total time spent on network round trips, in milliseconds (ms)
N: the number of items in the list, here 50 posts
t: the time for one round trip to the database, here an assumed 1 ms
ms: milliseconds, thousandths of a second
In words: the N+1 pattern costs one round trip per item, so 50 posts take 51 round trips instead of 2.
```

Fetching all the authors in one second query (`WHERE id IN (...)`) makes it 2 × 1 ms = about 2 ms, whatever N is. The 1 ms figure is an assumption; inside one data centre it is often less, across regions far more, and query execution time comes on top.

## Read replicas

A primary handles all writes and streams its change log to one or more **replicas**, which serve reads.

```
          writes
 app ------------> [ Primary ]
  |                  |  |
  |      replication |  | (async)
  |                  v  v
  +--reads-->  [Rep 1] [Rep 2]
```

- Adds read-serving capacity subject to replication overhead, workload balance and shared bottlenecks. Replica limits depend on the engine and service configuration; check current provider documentation.
- Replicas also give you failover candidates and a place for heavy analytics queries.
- Writes don't scale: every replica must still apply every write.

### Replication lag

With asynchronous replication, visibility can lag without a fixed upper bound; monitor replay progress and failure recovery. That causes anomalies:

- **Read-your-writes violation**: a user edits their profile, the page reloads from a replica and shows the old name.
- **Monotonic reads violation**: two refreshes hit different replicas and data appears to go backwards in time.

Common fixes:

1. Route a user's reads to the **primary for a short window** (say 10 s) after they write. This is a heuristic, not a guarantee when lag can exceed that window.
2. Track the write's log position (for example, Postgres's WAL LSN) and only read from replicas that have caught up to it.
3. **Pin each user to one advancing replica** to reduce backward jumps; carry a minimum observed version across failover or reassignment for a monotonic-read guarantee.

## Key takeaways
- Indexes, eager loading, smaller results and pooling address avoidable work before extra infrastructure.
- The N+1 pattern serialises one list query plus one query per item; batch related records or join appropriately.
- Full read replicas apply the same write stream and do not partition write ownership.
- Use committed positions or authoritative reads for required freshness; a fixed primary window is only a heuristic.

## Further reading
- [AWS: Working with read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
