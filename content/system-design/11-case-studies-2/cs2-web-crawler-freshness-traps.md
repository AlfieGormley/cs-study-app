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

- Cap URL length (around 2 KB) and path depth.
- Set a **per-host page budget** per crawl cycle, scaled by host importance.
- Detect repeating path segments, and apply site-specific parameter policies only when their semantics are understood.
- Watch for hosts whose pages are all near-duplicates (high SimHash collision rate), then throttle them.

Other robustness rules:

- Set timeouts on everything: connect at 5 s, total at 30 s, and a maximum body size (say 10 MB).
- Cap redirect chains at 5.
- Back off hosts with rising error rates.
- Run a dedicated DNS cache or resolver tier. Benchmark DNS cache misses, concurrency and resolver limits under the expected host mix; 1,000 fetches/s does not by itself establish a resolver bottleneck.

## Freshness and re-crawl

You can't re-fetch 10 B URLs every day, so estimate each page's **change rate** from history. As an illustrative model, treat changes as a Poisson process and schedule more often the more often a page changes, weighted by importance. A news homepage might be fetched every few minutes, and a 2009 blog post every few months.

Use **conditional GETs** (`If-None-Match` with the stored ETag, or `If-Modified-Since`). A `304 Not Modified` costs a few hundred bytes instead of 100 KB.

## Bottlenecks and trade-offs

- **Politeness caps throughput per host**. Large sites with millions of pages take weeks at one request every few seconds, and priority decides which of their pages you get.
- **Bloom filter false positives vs memory**: 1% at 12 GB, 0.1% at about 18 GB (the same sizing formula with a false-positive rate of 0.001 gives about 14.4 bits per URL).
- **JavaScript rendering** adds browser CPU, memory and subresource work; the cost multiplier is workload-dependent. Render only hosts whose raw HTML lacks content, and keep it a separate, smaller pool.
- **Storage format**: big WARC files beat billions of small objects (object-store cost per request, and listing overhead).

## Evolving at 10x

- **10 B pages/month (~4,000/s)**: add crawler nodes. Host partitioning distributes work, subject to skew, shared-IP limits and storage/network bottlenecks, and the frontier and seen-sets shard with it.
- The **seen-URL set** grows to around 100 B URLs. Move to sharded Bloom filters plus an exact RocksDB store per partition.
- **Priority becomes the product**: learn from user and query signals what's worth fetching, and sitemaps or IndexNow-style push notifications from sites reduce blind re-crawl.
- **Multi-region**: crawl from regions near hosts, then ship compressed WARCs to central storage.

## A change-rate model

An illustrative Poisson model assumes independent changes at a steady average rate. A page that changes once every ten days is not certain to change during every ten-day interval.

```formula
P_c = 1 − e^{−λt}
λ = 0.1/day
P_c = 1 − e^{−(0.1/day × 10 day)}
P_c ≈ 0.632
where
P_c: probability of at least one change, dimensionless
λ: average change rate, in changes per day; here 0.1
t: revisit interval, in days; here 10
e: Euler's number, about 2.718
day: a day
≈: approximately equal after rounding
In words: waiting ten days at this average rate finds at least one change about sixty-three per cent of the time.
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
