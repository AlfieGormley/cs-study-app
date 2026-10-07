---
id: cs2-web-crawler
title: Web crawler
level: intermediate
minutes: 16
summary: Design a distributed crawler for billions of pages, covering the URL frontier, politeness and robots.txt, dedup with Bloom filters and SimHash, spider traps, and partitioning by host.
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

```
1 B pages / month
  / (30 x 86,400 s) = ~400 pages/s
  peak/headroom: plan 1,000 pages/s

Avg HTML page ~100 KB (uncompressed)
  400 x 100 KB = 40 MB/s = ~320 Mbps
Storage: 1e9 x 100 KB = 100 TB/month
  (~25 TB compressed)
```

Bandwidth is modest. The hard numbers are about **URLs**. Each page has dozens of outlinks, so the set of *discovered* URLs grows far faster than the set of fetched pages. Plan for about 10 B known URLs.

```
Seen-URL set, exact:
  10e9 x ~100 B = ~1 TB (disk/KV)
Seen-URL Bloom filter, 1% false positives:
  ~9.6 bits/URL x 10e9 = ~12 GB, k=7
```

A 12 GB Bloom filter fits in RAM, split across a few nodes. An exact 1TB set usually motivates disk-backed or distributed storage; it is not inherently impossible to keep it in a large RAM cluster. This trade-off returns in the dedup section.

**Latency drives concurrency.** A fetch takes about 1 s on average (DNS + TCP + TLS + download), so 1,000 pages/s means about **1,000 requests in flight**. Use async I/O (epoll, an event loop) rather than a thread per request.

## API and interfaces

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

The frontier answers one question: **which URL should a fetcher take next?** It has to balance **priority** (fetch important pages first) and **politeness** (never hit one host too fast). The classic design comes from the Mercator crawler.

### Front queues: priority
- Score each URL by things like PageRank or host authority, how often the page changes, depth from the seed, and freshness need.
- Place it in one of F priority queues (say 10–20).
- A selector pulls from the queues with weighted randomness, so every nonempty class with nonzero weight has a chance of service. Random selection does not provide a deterministic maximum wait; add aging or explicit fairness if required.

### Back queues: politeness
- Keep B back queues, each holding URLs for **exactly one host**.
- Keep a **min-heap** keyed by `next_allowed_at` for each back queue.
- Atomically reserve the host so no other fetcher starts concurrently, then fetch. On completion, set `next_allowed_at = now + delay` and pushes the host back.
- When a back queue empties, refill it from the front queues with a URL for a new host.

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

A common heuristic, from the Mercator work, sets the delay to **about 10× the time the last fetch took**. If a page took 200 ms, wait 2 s before the next request to that host. A slow, struggling server automatically gets more breathing room.

### Persistence
The frontier holds billions of URLs, so it can't all live in memory. Keep the head of each queue in RAM and spill the rest to disk (RocksDB or append-only segment files). Persist accepted discoveries and queue transitions in a write-ahead log/transaction before acknowledging them; checkpoints alone lose discoveries since the last checkpoint. Reclaim abandoned fetch leases after crashes.

## Deep dive 2: politeness and robots.txt

- Fetch `/robots.txt` before crawling a host, and **cache it** by scheme and authority (including port), not hostname alone. RFC 9309 (the Robots Exclusion Protocol, standardised in 2022) says crawlers shouldn't use a cached copy for more than 24 hours unless the file is unreachable.
- Parse `User-agent`, `Allow` and `Disallow` rules. User-agent matching is case-insensitive. Under RFC 9309 the **most specific** rule wins, meaning the matching rule with the most octets, and if an `Allow` and a `Disallow` are equally long, `Allow` should win. `/robots.txt` itself is always allowed.
- Parse at least the first 500 KiB of the file. The RFC sets that as the minimum parsing limit, so crawlers agree on how much of a huge file counts.
- Follow at least five consecutive redirects when fetching it. Beyond that, you may treat the file as unavailable.
- Handle failure cases as the RFC specifies. A 4xx ("unavailable") means you may crawl everything. A 5xx or a network error ("unreachable") means you **must assume complete disallow**, since the server may be struggling. After a reasonably long undefined period (the RFC gives 30 days as an example), the RFC lets you either treat it as unavailable or keep using a cached copy.
- `Crawl-delay` isn't in the RFC, but many sites use it. Honour it as a minimum delay.
- Identify yourself with a clear `User-Agent` and a contact URL.

For example, with these rules:

```
User-agent: *
Disallow: /shop
Allow: /shop/help
```

`/shop/help/returns` matches both rules. `Allow: /shop/help` is longer (10 octets against 5), so it wins and the page may be fetched. `/shop/cart` matches only the `Disallow`, so it's skipped.

Politeness should be **per IP as well as per host**. Thousands of small sites can sit behind one shared-hosting IP, and hitting 500 of them at once still overloads one machine.

## Deep dive 3: dedup at three levels

### 1. URL normalisation
Before checking "seen", canonicalise URLs. Lower-case the scheme and host, drop default ports and fragments (`#...`), resolve `../`, and preserve query semantics. Reordering or stripping parameters is safe only when their equivalence is established for that site; `rel="canonical"` is a publisher hint, not proof that two URLs return identical content.

### 2. Seen-URL test
Ask for each discovered URL: "have we already queued or fetched this?"

- A **Bloom filter** answers in O(k) memory lookups with **no false negatives**. A false positive means you wrongly skip a new URL. At a 1% false-positive rate, approximately 1% of genuinely new membership probes may be skipped. Rediscovering the same URL does not fix a stable false positive: it hashes to the same already-set bits.
- If missing pages is unacceptable, treat the Bloom filter as a fast negative check. "Definitely not seen" proceeds to an atomic exact-store claim and durable enqueue; concurrent Bloom misses must not enqueue twice. "Maybe seen" is checked against the exact `url_state` store.
- Bloom filters can't delete entries. For re-crawl scheduling, use the exact store (or a counting or cuckoo filter).

### 3. Content dedup
Mirrors, printer-friendly pages and session variants can create many duplicates. The proportion depends on the crawl corpus and similarity definition.

- **Exact duplicates**: hash the normalised body with SHA-256 and check a fingerprint store. If using a short fingerprint, compare the candidate bodies before declaring an exact duplicate; collisions matter at billions of pages.
- **Near duplicates**: use **SimHash**. Hash each shingle (word n-gram) and, for each of 64 bit positions, add the shingle's weight if that bit is 1 and subtract it if 0. The sign of each total becomes the bit. Similar weighted feature vectors tend to produce fingerprints with small Hamming distance; small textual edits do not guarantee a fixed number of changed bits. Google's 2007 paper on near-duplicate detection (Manku, Jain and Das Sarma) found that, for a repository of 8 B pages, 64-bit SimHash fingerprints with a threshold of **3 differing bits** worked well. It found matches quickly by splitting the fingerprint into blocks and indexing permuted tables, so any fingerprint within 3 bits must match exactly on at least one block.

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

## Distributed crawling

Partition by **host** (consistent hash of the hostname, or the registered domain), so every URL for `example.com` lands on the same crawler node. This means:

- Politeness is enforced **locally**. One node owns a host's back queue and its `next_allowed_at`, without a distributed limiter for that host. Shared-IP limits across different host owners still require coordination or an IP-based scheduling owner. Ownership migration must drain or fence old fetchers, or both owners may fetch concurrently.
- The robots.txt and DNS caches for that host are local.
- Rebalancing is cheap with consistent hashing.

When a node extracts a link for a host it doesn't own, it forwards the URL to the owner. Batch these forwards (thousands of URLs per message, through Kafka or direct RPC), because a large share of extracted links point to other hosts, and with dozens of nodes almost all of those hosts are owned by a different node.

Geography can reduce latency when the actual serving infrastructure is nearby; hostname/domain geography alone does not locate a CDN-backed server.

## Freshness and re-crawl

You can't re-fetch 10 B URLs every day, so estimate each page's **change rate** from history. As an illustrative model, treat changes as a Poisson process and schedule more often the more often a page changes, weighted by importance. A news homepage might be fetched every few minutes, and a 2009 blog post every few months.

Use **conditional GETs** (`If-None-Match` with the stored ETag, or `If-Modified-Since`). A `304 Not Modified` costs a few hundred bytes instead of 100 KB.

## Bottlenecks and trade-offs

- **Politeness caps throughput per host**. Large sites with millions of pages take weeks at one request every few seconds, and priority decides which of their pages you get.
- **Bloom filter false positives vs memory**: 1% at 12 GB, 0.1% at about 18 GB.
- **JavaScript rendering** adds browser CPU, memory and subresource work; the cost multiplier is workload-dependent. Render only hosts whose raw HTML lacks content, and keep it a separate, smaller pool.
- **Storage format**: big WARC files beat billions of small objects (object-store cost per request, and listing overhead).

## Evolving at 10x

- **10 B pages/month (~4,000/s)**: add crawler nodes. Host partitioning distributes work, subject to skew, shared-IP limits and storage/network bottlenecks, and the frontier and seen-sets shard with it.
- The **seen-URL set** grows to around 100 B URLs. Move to sharded Bloom filters plus an exact RocksDB store per partition.
- **Priority becomes the product**: learn from user and query signals what's worth fetching, and sitemaps or IndexNow-style push notifications from sites reduce blind re-crawl.
- **Multi-region**: crawl from regions near hosts, then ship compressed WARCs to central storage.

## Key takeaways
- Bandwidth is modest. Concurrency (about 1 s per fetch means thousands in flight) and the URL space (billions discovered) are what's hard.
- The Mercator frontier pairs priority front queues with per-host back queues and a heap of next-allowed times, giving both importance ordering and politeness.
- Obey RFC 9309 robots.txt, normally avoid using a cached copy beyond 24h, with the RFC’s unreachable exception, and treat 5xx as disallow. Rate-limit per host *and* per IP.
- Dedup in three layers: URL normalisation, a seen-URL Bloom filter (no false negatives, tunable false positives), and content fingerprints with SimHash for near duplicates.
- Partition by host for local host scheduling; key robots caches by origin and coordinate shared-IP limits across owners. Batch-forward cross-host links.

> **Content gap:** no representative browser-rendering benchmark, current web-wide duplicate fraction or host capacity measurement is supplied. Page size, compression ratio, fetch latency and budgets are scenario inputs. URL equivalence and near-duplicate thresholds require validation on the actual crawl corpus.

## Further reading
- [RFC 9309: Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html)
- [Detecting near-duplicates for web crawling (Google Research)](https://research.google/pubs/detecting-near-duplicates-for-web-crawling/)
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
- [Bloom filter (Wikipedia)](https://en.wikipedia.org/wiki/Bloom_filter)
- [SimHash (Wikipedia)](https://en.wikipedia.org/wiki/SimHash)
- [Common Crawl](https://commoncrawl.org/)
