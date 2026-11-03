---
id: cs2-web-crawler-fetch-budget
title: Crawler throughput and concurrency
level: intermediate
minutes: 4
summary: Size page storage and network work, then account for fetch latency.
sourceLesson: cs2-web-crawler
---

A web crawler sounds simple: fetch a page, extract the links, repeat. At a billion pages, the interesting problems are all about **restraint and memory**. Don't hammer anyone's server. Don't fetch the same thing twice. Don't fall into infinite URL spaces. Decide what to fetch *next* out of tens of billions of candidates.

## Requirements

### Functional
- Start from seed URLs and discover pages by following links.
- Fetch HTML (optionally render JavaScript for some sites), and store the content and metadata for downstream indexing.
- Re-crawl pages to keep them fresh.

### Non-functional
- **Politeness**: obey robots.txt, space out requests and coordinate host/IP budgets. One request at a time is a conservative starting policy, not proof that a fragile host cannot be overloaded.
- **Scale**: 1 B pages per month at first, growing 10x.
- **Robustness**: survive malformed HTML, slow servers, spider traps and crashes, without losing frontier state.
- **Prioritisation**: important and fresh pages first. The web is effectively infinite, so you never finish.
- **Extensibility**: new content types and processors can be plugged in.

## Latency consumes concurrency

An illustrative target of one billion pages in a 30-day month averages roughly 400 pages a second. A planning target of 1,000 fetches a second leaves some room for uneven demand, retries and growth; it is not a measured capacity guarantee.

Page size governs network and storage payload. Fetch duration governs how many requests remain open. If hosts become slower while you maintain the same completion rate, more fetches must be in flight. That consumes sockets, memory and connection slots even when CPU use is low.

Little's law is a useful reference for long-run averages in a stable system:

```formula reference
L = λW
where
L: average number of fetches in flight, a count
λ: average fetch completion rate, in fetches per second
W: average time a fetch remains in flight, in seconds
In words: sustaining the same fetch rate while requests take longer requires more requests in progress.
```

For example, at 1,000 fetches a second with an average one-second lifetime, about 1,000 fetches are open. This is an average, not a safe maximum. Allow for latency tails and bound concurrency, timeouts and response size. Slow hosts must not exhaust all slots and starve healthy ones.

## Keep capacity separate from permission

Asynchronous I/O lets a small number of threads handle many waiting sockets. Lightweight-thread designs are another option; measure their memory and scheduling cost. Neither makes it acceptable to exceed a host's request budget. Coordinate host and shared-IP politeness separately from fleet-wide concurrency.

For storage, distinguish raw fetched bodies from compression, indexes, copies and retention. A hypothetical 100 KB average HTML body excludes images and other resources; rendering JavaScript may create many additional requests and substantial CPU work. Measure the actual crawl mix before committing to a fleet size.

## Key takeaways
- Page size and fetch rate determine raw network and storage volume.
- Stable-system concurrency is throughput times average fetch latency.
- Async fetchers need timeouts and capacity measured under the actual host mix.

## Further reading
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Common Crawl](https://commoncrawl.org/)
