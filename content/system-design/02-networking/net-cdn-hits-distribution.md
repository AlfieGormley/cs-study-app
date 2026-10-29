---
id: net-cdn-hits-distribution
title: "CDN hits, misses and content placement"
level: advanced
minutes: 4
summary: "Trace edge routing, see why origin load follows the miss rate, and choose pull or pre-positioned content."
sourceLesson: net-cdn
---
A content delivery network (CDN) is a globally distributed fleet of reverse proxies, called **edge servers** or **PoPs** (points of presence), that sit between users and your **origin server** (usually just called the *origin*). Examples include Akamai, Cloudflare, Fastly, Amazon CloudFront and Google Cloud CDN; footprint and terminology vary by provider.

A CDN does three jobs:

1. **Serve cached content from near the user**, cutting latency.
2. **Absorb load**, so the origin sees a small fraction of requests.
3. **Protect the origin** from traffic spikes and DDoS attacks.

This lesson focuses on the network and architecture side. HTTP caching headers (`Cache-Control`, `ETag`, revalidation) are covered in the caching module.

## How a request reaches the edge

The user's request is steered to a nearby PoP in one of two ways:

- **DNS-based:** your `www` record is a CNAME to the CDN (`d111.cloudfront.net`), whose DNS returns the IP of a nearby PoP. Akamai and CloudFront are the classic examples.
- **Anycast:** every PoP advertises the *same* IP addresses; internet routing (BGP) chooses an available route according to routing policy, often reaching a nearby site but not necessarily the geographically closest one. Cloudflare is the classic example.

In practice the line is blurry: most large CDNs mix the two (for example anycast for their DNS servers and some edge addresses, DNS steering for the rest), so treat these as techniques rather than vendor labels.

Both are covered in the global traffic lesson.

## Cache hit, miss and the origin

```
User --> Edge (London)
          | hit?  serve (~10 ms)
          | miss
          v
        Origin (us-east-1)
          | response + headers
          v
        Edge stores it, serves user
```

The key metric is the **cache hit ratio** (CHR): the fraction of requests served from the edge. In a simplified single-cache model, each miss causes one origin fetch and hits cause none, so the origin sees only the misses:

```formula reference
R_origin = (1 − CHR) × R_total
where
R_origin: the request rate reaching the origin, in requests per second (rps)
CHR: the cache hit ratio, a fraction between 0 and 1; 0.95 means 95% of requests are served from the edge
R_total: the total request rate from users to the CDN, in rps
In words: origin load is set by the miss rate, not the hit rate, so a few points of hit ratio near the top make a large difference to the origin.
```

That is why a move from 95% to 99% hit ratio, which sounds like a 4% improvement, cuts origin load five-fold: misses fall from 1 in 20 requests to 1 in 100. The same logic warns that a small drop in hit ratio (a bad cache key, a purge) can multiply origin load. Shields, request coalescing, background revalidation and traffic that bypasses the cache all change the exact relationship.

> [!analogy] Real-world analogy: Local shops stocked from one warehouse
> A chain has one central warehouse and many local shops. Customers buy from the nearest shop; only when a shop has run out does it send an order back to the warehouse, which then restocks that shop.
>
> **How it maps:** the shops are CDN edge PoPs, the warehouse is the origin and a shopper finding the item on the shelf is a cache hit. The warehouse's workload depends on how often shops run out, which is the miss rate.
>
> **Where it stops:** a cached response is copied, not sold, so one stored copy can serve any number of requests until it expires or is evicted. A cache also follows freshness rules: it can serve out-of-date content if those rules are wrong, and it must never hand one user's personalised response to another.

## Pull vs push

| | Pull (origin pull) | Push |
|---|---|---|
| How content arrives | Edge fetches on first miss | You upload ahead of time |
| Effort | Just point at origin | Manage uploads, purges |
| First request | Slow (miss) | Fast |
| Storage | Filled on demand | Selected content placed ahead of demand |
| Fits | Most websites, APIs | Large, predictable files |

**Pull** is the default for almost everything: configure the origin, set cache headers and the CDN fills itself. Long-tail content that nobody requests never takes up edge storage.

**Push** (a *push CDN* setup) suits big, predictable content: game patches, software releases, video libraries, where you know exactly what will be requested and want no cold misses at launch. Netflix's Open Connect is an extreme version: it pre-positions content on appliances inside ISPs during off-peak hours, based on predicted demand.

## Key takeaways

- A CDN routes requests to distributed edge proxies using DNS, anycast or both.
- Origin load follows the miss rate: going from 95% to 99% hits cuts origin traffic about five-fold.
- Pull fills on demand; push and pre-positioning suit large files with predictable launch demand.

## Further reading

- [Cloud CDN overview (Google Cloud)](https://cloud.google.com/cdn/docs/overview)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
