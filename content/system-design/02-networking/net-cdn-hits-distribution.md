---
id: net-cdn-hits-distribution
title: "CDN hits, misses and content placement"
level: advanced
minutes: 4
summary: "Trace edge routing, calculate origin misses and choose pull or pre-positioned content."
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

The key metric is the **cache hit ratio** (CHR): the fraction of requests served from the edge. In a simplified single-cache model where each miss causes one origin fetch and hits cause none, 95% CHR means 1 origin fetch per 20 user requests; 99% means 1 per 100. Shields, coalescing, background revalidation and bypass traffic change that relationship. The origin only sees the misses:

```formula
R_origin = (1 − CHR) × R_total
R_95 = (1 − 0.95) × 10,000 rps = 500 rps
R_99 = (1 − 0.99) × 10,000 rps = 100 rps
R_95 / R_99 = 500 / 100 = 5
where
R_origin: the request rate reaching the origin, in requests per second (rps)
CHR: the cache hit ratio as a fraction between 0 and 1; 0.95 means 95% of requests are served from the edge
R_total: the total request rate from users to the CDN; here 10,000 rps
R_95: the origin load at a 95% hit ratio
R_99: the origin load at a 99% hit ratio
rps: requests per second
In words: the origin's load is set by the miss rate, so going from 5% misses to 1% misses cuts it five times over.
```

Going from 95% to 99% cuts origin load by **5×**, so small CHR improvements matter a lot.

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
- In the one-fetch-per-miss model, origin load follows the miss rate rather than the hit rate.
- Pull fills on demand; push and pre-positioning suit large files with predictable launch demand.

## Further reading

- [Cloud CDN overview (Google Cloud)](https://cloud.google.com/cdn/docs/overview)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
