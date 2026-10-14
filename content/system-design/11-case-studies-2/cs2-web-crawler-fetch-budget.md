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
- **Politeness**: obey robots.txt, and never overload a host (at most about one request at a time per host, spaced out).
- **Scale**: 1 B pages per month at first, growing 10x.
- **Robustness**: survive malformed HTML, slow servers, spider traps and crashes, without losing frontier state.
- **Prioritisation**: important and fresh pages first. The web is effectively infinite, so you never finish.
- **Extensibility**: new content types and processors can be plugged in.

## Back-of-the-envelope

Start from the target of 1 B (one billion) pages a month and turn it into a rate per second. A 30-day month contains 2,592,000 seconds:

```formula
P = N / (30 × 86,400 s)
P = 1,000,000,000 / 2,592,000 s
P ≈ 386 ≈ 400 pages/s
where
P: average pages fetched per second
N: pages to fetch per month; here 1 billion
86,400 s: the number of seconds in one day
30: days in the month
s: seconds
pages: web pages fetched
≈: approximately equal to
In words: a billion pages a month works out at roughly 400 pages every second, around the clock.
```

Plan for **1,000 pages/s** to leave room for peaks, retries and growth.

Bandwidth is pages per second times page size. Assume an average HTML page of about 100 KB (kilobytes) uncompressed. Network speeds are quoted in bits, so multiply bytes by 8:

```formula
D = P × S
D = 400 pages/s × 100 KB = 40 MB/s
D = 40 MB/s × 8 = 320 Mbps
where
D: download bandwidth needed, in megabytes per second (MB/s) or megabits per second (Mbps)
P: pages fetched per second; here about 400
S: average page size; about 100 KB
pages: web pages fetched
s: seconds
KB: kilobytes, 1,000 bytes
MB: megabytes, 1,000,000 bytes
Mbps: megabits per second; one byte is 8 bits
In words: 400 pages a second at 100 KB each is 40 megabytes a second, or about 320 megabits a second on the network.
```

Storage for a month of pages is the page count times page size:

```formula
T = N × S
T = 1,000,000,000 × 100 KB = 100 TB
where
T: raw page storage per month
N: pages fetched per month; here 1 billion
S: average page size; about 100 KB
KB: kilobytes, 1,000 bytes
TB: terabytes, 10^12 bytes (a million million)
In words: a billion 100 KB pages is 100 terabytes a month, or roughly 25 TB if HTML compresses about four to one.
```

**Latency drives concurrency.** Little's law links three averages in any steady system: the number of things in progress equals the rate they arrive times how long each one stays.

```formula
L = λW
L = 1,000 pages/s × 1 s = 1,000
where
L: requests in flight at the same moment (concurrency)
λ: the arrival rate: pages started per second; here 1,000
W: average time one fetch takes, in seconds (s); about 1 s for DNS + TCP + TLS + download
s: seconds
pages: web page fetches
In words: starting 1,000 fetches a second, each taking a second, keeps about 1,000 requests open at once.
```

A fetch takes about 1 s on average (DNS + TCP + TLS + download), so 1,000 pages/s means about **1,000 requests in flight**. Little's law holds for long-run averages in a stable system; slow hosts raise W and so raise concurrency. Use async I/O (epoll, an event loop) rather than a thread per request.

## Key takeaways
- Page size and fetch rate determine raw network and storage volume.
- Stable-system concurrency is throughput times average fetch latency.
- Async fetchers need timeouts and capacity measured under the actual host mix.

## Further reading
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Common Crawl](https://commoncrawl.org/)
