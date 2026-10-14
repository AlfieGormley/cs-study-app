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

The frontier answers one question: **which URL should a fetcher take next?** It has to balance **priority** (fetch important pages first) and **politeness** (never hit one host too fast). The two-stage design below is documented in the information-retrieval textbook. The 1999 Mercator paper describes host-based FIFO subqueues and an alternative dynamic host-to-thread mapping; it does not describe this exact priority-front-queue/min-heap construction.

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

The textbook describes a common heuristic that sets the delay to **about 10× the time the last fetch took**:

```formula
d = 10 × f
d = 10 × 200 ms = 2,000 ms = 2 s
where
d: the wait before the next request to the same host, in milliseconds (ms)
f: how long the last fetch from that host took, in milliseconds (ms)
ms: milliseconds, thousandths of a second
s: seconds
In words: wait ten times as long as the last fetch took; a 200 ms fetch means a 2 second pause.
```

So if a page took 200 ms, wait 2 s before the next request to that host. A slow, struggling server automatically gets more breathing room.

### Persistence
The frontier holds billions of URLs, so it can't all live in memory. Keep the head of each queue in RAM and spill the rest to disk (RocksDB or append-only segment files). Persist accepted discoveries and queue transitions in a write-ahead log/transaction before acknowledging them; checkpoints alone lose discoveries since the last checkpoint. Reclaim abandoned fetch leases after crashes.

## Key takeaways
- Weighted priority service needs explicit fairness if a maximum wait is required.
- Reserve each host atomically and schedule its next eligible time after completion.
- Persist discoveries and queue transitions before acknowledgement; checkpoints alone lose recent work.

## Further reading
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Common Crawl](https://commoncrawl.org/)
- [URL frontier priority and politeness (IR textbook)](https://nlp.stanford.edu/IR-book/html/htmledition/the-url-frontier-1.html)
- [Original Mercator paper (1999)](https://marc.najork.org/papers/wwwmerc.pdf)
