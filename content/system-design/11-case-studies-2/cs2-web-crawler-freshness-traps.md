---
id: cs2-web-crawler-freshness-traps
title: Crawler traps and revisit policy
level: intermediate
minutes: 4
summary: Protect finite resources from infinite URL spaces and tune revisits to change rate.
sourceLesson: cs2-web-crawler
---

## Deep dive 4: traps and robustness

Spider traps generate infinite URL spaces: calendars with a "next month" link forever, `/a/b/a/b/a/...` paths, session ids in every URL. Defences:

- Choose explicit limits for URL length and path depth (2 KB is an illustrative policy, not a universal valid-URL limit).
- Set a **per-host page budget** per crawl cycle, scaled by host importance.
- Detect repeating path segments, and apply site-specific parameter policies only when their semantics are understood.
- Watch for hosts whose pages are all near-duplicates (high SimHash collision rate), then throttle them.

Other robustness rules:

- Bound connection time, total fetch time and body size; five seconds, thirty seconds and 10 MB are illustrative starting limits to test.
- Cap redirect chains at 5.
- Back off hosts with rising error rates.
- Run a dedicated DNS cache or resolver tier. Benchmark DNS cache misses, concurrency and resolver limits under the expected host mix; 1,000 fetches/s does not by itself establish a resolver bottleneck.

## Freshness and re-crawl

A finite crawl budget makes revisit priorities necessary. Estimate each page’s **change rate** from history. As an illustrative model, treat changes as a Poisson process and schedule more often the more often a page changes, weighted by importance. A news homepage might be fetched every few minutes, and a 2009 blog post every few months.

Use **conditional GETs** (`If-None-Match` with the stored ETag, or `If-Modified-Since`). A `304 Not Modified` has no response body, saving unchanged payload where validators are supported. Headers, request work and connection costs remain.

## Bottlenecks and trade-offs

- **Politeness caps throughput per host**. Large sites with millions of pages take weeks at one request every few seconds, and priority decides which of their pages you get.
- **Bloom filter false positives vs memory**: lower false-positive targets need more bits per inserted URL under the chosen hash and population assumptions. Check positives against exact state when silent coverage loss is unacceptable.
- **JavaScript rendering** adds browser CPU, memory and subresource work; the cost multiplier is workload-dependent. Render only hosts whose raw HTML lacks content, and keep it a separate, smaller pool.
- **Storage format**: large WARC files can reduce per-object request and listing overhead, while requiring offsets and range retrieval for individual records.

## Evolving at 10x

- **10 B pages/month (~4,000/s)**: add crawler nodes. Host partitioning distributes work, subject to skew, shared-IP limits and storage/network bottlenecks, and the frontier and seen-sets shard with it.
- If discovery grows proportionally in this scenario, the **seen-URL set** might reach 100 B URLs; measure it independently of fetched pages. Move to sharded Bloom filters plus an exact RocksDB store per partition.
- **Priority becomes the product**: learn from user and query signals what's worth fetching, and sitemaps or IndexNow-style push notifications from sites reduce blind re-crawl.
- **Multi-region**: crawl from regions near hosts, then ship compressed WARCs to central storage.

## A change-rate model

An illustrative Poisson model assumes independent changes at a steady average rate. A page that changes once every ten days is not certain to change during every ten-day interval.

```formula reference
P_c = 1 − e^{−λt}
where
P_c: probability of at least one change, a number between zero and one
λ: constant average change rate, in changes per day
t: elapsed time since the last fetch, in days
e: Euler's number, approximately 2.718
In words: under a steady independent-change model, a longer wait or faster change rate makes at least one change more likely.
```

Real pages change in bursts and can undo earlier edits. Treat this as a scheduling model, not a guarantee that a fresh fetch differs byte-for-byte.

> **Content gap:** no representative browser-rendering benchmark, current web-wide duplicate fraction or host capacity measurement is supplied. Page size, compression ratio, fetch latency and budgets are scenario inputs. URL equivalence and near-duplicate thresholds require validation on the actual crawl corpus.

## Key takeaways
- Cap host budgets, path depth, bodies, redirects and request time.
- Conditional requests reduce unchanged-response payload rather than eliminating fetch work.
- Model change rates and validate budgets on the real corpus before scaling.

## Further reading
- [RFC 9309: Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html)
- [Detecting near-duplicates for web crawling (Google Research)](https://research.google/pubs/detecting-near-duplicates-for-web-crawling/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Common Crawl](https://commoncrawl.org/)
- [HTTP conditional requests](https://www.rfc-editor.org/rfc/rfc9110.html)
