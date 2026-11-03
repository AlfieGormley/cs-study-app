---
id: cs2-web-crawler-frontier-contracts
title: Crawler frontier contracts and persistence
level: intermediate
minutes: 4
summary: Combine priority queues and host timers with recoverable discovery state.
sourceLesson: cs2-web-crawler
---

## API and interfaces

The fields below describe an internal contract rather than a runnable client.

A crawler has few public APIs. What matters is the **internal contracts**.

```
POST /v1/seeds        {urls:[...], priority}
GET  /v1/status/{host}
  -> {queued, fetched, errors, last_fetch}

// fetcher -> storage, per page
{url, final_url, status, fetched_at,
 headers, content_hash, simhash,
 body_ref (WARC offset), outlinks:[...]}
```

Store raw responses in **WARC** files, the standard web-archive format used by Common Crawl and the Internet Archive. These are large append-only files in object storage, with an index of `url -> (file, offset)`.

## Data model

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

```
url_state(url_hash PK, url, host,
          last_fetch, next_fetch,
          etag, last_modified,
          content_hash, change_rate,
          priority)
host_state(host PK, robots_rules,
           robots_fetched_at, crawl_delay,
           next_allowed_at, ip, error_rate)
```

Both are partitioned by **host**, for reasons explained below.

## High-level architecture

Follow the arrows as data paths; the drawing is not a deployment specification.

```
          +--------+
 seeds -->|  URL   |<-----------------+
          |frontier|                  |
          +--------+                  |
              |                       |
              v                       |
          +--------+   +-------+      |
          |Fetcher |<->|DNS    |      |
          |(async) |   |cache  |      |
          +--------+   +-------+      |
              |  robots.txt cache     |
              v                       |
          +--------+   +-------+      |
          |Content |-->| WARC  |      |
          | dedup  |   | store |      |
          +--------+   +-------+      |
              |                       |
              v                       |
          +--------+   +--------+     |
          |  Link  |-->|URL seen|-----+
          |extract |   | filter |
          +--------+   +--------+
```

## Deep dive 1: the URL frontier

The frontier answers one question: **which URL should a fetcher take next?** It has to balance **priority** (fetch important pages first) and **politeness** (never hit one host too fast). The two-stage design below is an illustrative way to combine those requirements. The 1999 Mercator paper provides primary context for host-based FIFO subqueues and bounded memory; it does not establish this exact priority-front-queue/min-heap construction.

### Front queues: priority
- Score each URL by things like PageRank or host authority, how often the page changes, depth from the seed, and freshness need.
- Place it in one of F priority queues (say 10–20).
- A selector pulls from the queues with weighted randomness, so every nonempty class with nonzero weight has a chance of service. Random selection does not provide a deterministic maximum wait; add aging or explicit fairness if required.

### Back queues: politeness
- Keep B back queues, each holding URLs for **exactly one host**.
- Keep a **min-heap** keyed by `next_allowed_at` for each back queue.
- Atomically reserve the host so no other fetcher starts concurrently, then fetch. On completion, set the next-allowed timestamp to completion time plus the delay and push the host back.
- When a back queue empties, draw from front queues. Send a URL for an already-mapped host to its existing queue and continue until an unmapped host fills the empty queue. Maintain one back-queue mapping per host.

```
front queues (priority)
 [P1][P2]...[Pf]
       |  biased pick
       v
back queues (one host each)
 [a.com][b.org]...[z.net]
       |
 heap by next_allowed_at
       |
       v
    fetchers
```

For example, a policy might wait ten times the last fetch duration, so a 200 ms fetch leads to a two-second wait. This is an illustrative heuristic; also enforce configured minimum delays, robots policy and shared-IP budgets.

A slower response increases this heuristic delay, but response time alone cannot reveal the host’s safe capacity.

### Persistence
A frontier with billions of URLs can make an all-memory design expensive. Keep the head of each queue in RAM and spill the rest to disk (RocksDB or append-only segment files). Persist accepted discoveries and queue transitions in a write-ahead log/transaction before acknowledging them; checkpoints alone lose discoveries since the last checkpoint. Reclaim abandoned fetch leases after crashes.

> [!analogy] Real-world analogy: Appointments at separate desks
> A receptionist chooses important appointments, but each desk accepts visitors only when its next slot is free.
>
> **How it maps:** URL priority selects useful work; each host’s eligibility time and reservation enforce the configured request-spacing policy.
>
> **Where it stops:** Different hostnames may share one IP, and crashed or duplicated crawler owners need coordinated limits beyond one receptionist’s diary.

## Key takeaways
- Weighted priority service needs explicit fairness if a maximum wait is required.
- Reserve each host atomically and schedule its next eligible time after completion.
- Persist discoveries and queue transitions before acknowledgement; checkpoints alone lose recent work.

## Further reading
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Common Crawl](https://commoncrawl.org/)
- [Original Mercator paper (1999)](https://marc.najork.org/papers/wwwmerc.pdf)
