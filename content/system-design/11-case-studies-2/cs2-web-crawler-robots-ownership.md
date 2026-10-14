---
id: cs2-web-crawler-robots-ownership
title: Robots rules and crawl ownership
level: intermediate
minutes: 3
summary: Apply RFC 9309 alongside host and shared-IP scheduling limits.
sourceLesson: cs2-web-crawler
---

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

## Distributed crawling

Partition by **host** (consistent hash of the hostname, or the registered domain), so every URL for `example.com` lands on the same crawler node. This means:

- Politeness is enforced **locally**. One node owns a host's back queue and its `next_allowed_at`, without a distributed limiter for that host. Shared-IP limits across different host owners still require coordination or an IP-based scheduling owner. Ownership migration must drain or fence old fetchers, or both owners may fetch concurrently.
- The robots.txt and DNS caches for that host are local.
- Rebalancing is cheap with consistent hashing.

When a node extracts a link for a host it doesn't own, it forwards the URL to the owner. Batch these forwards (thousands of URLs per message, through Kafka or direct RPC), because a large share of extracted links point to other hosts, and with dozens of nodes almost all of those hosts are owned by a different node.

Geography can reduce latency when the actual serving infrastructure is nearby; hostname/domain geography alone does not locate a CDN-backed server.

## Key takeaways
- Cache robots rules by scheme and authority, including port.
- Handle unavailable and unreachable responses differently under RFC 9309.
- Host ownership simplifies local politeness, while shared-IP budgets still need coordination.

## Further reading
- [RFC 9309: Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html)
- [The anatomy of a large-scale hypertextual web search engine (Brin and Page)](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/)
- [Web crawler (Wikipedia)](https://en.wikipedia.org/wiki/Web_crawler)
