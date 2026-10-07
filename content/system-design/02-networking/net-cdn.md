---
id: net-cdn
title: "CDNs: edge caching, cache keys and origin shielding"
level: advanced
minutes: 14
summary: How CDNs work, push vs pull, designing cache keys, tiered caching and origin shields, and how CDNs speed up even uncacheable dynamic content.
---

A content delivery network (CDN) is a globally distributed fleet of reverse proxies, called **edge servers** or **PoPs** (points of presence), that sit between users and your **origin**. Examples include Akamai, Cloudflare, Fastly, Amazon CloudFront and Google Cloud CDN; footprint and terminology vary by provider.

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

The key metric is the **cache hit ratio** (CHR): the fraction of requests served from the edge. In a simplified single-cache model where each miss causes one origin fetch and hits cause none, 95% CHR means 1 origin fetch per 20 user requests; 99% means 1 per 100. Shields, coalescing, background revalidation and bypass traffic change that relationship. Going from 95% to 99% cuts origin load by **5×**, so small CHR improvements matter a lot.

## Pull vs push

| | Pull (origin pull) | Push |
|---|---|---|
| How content arrives | Edge fetches on first miss | You upload ahead of time |
| Effort | Just point at origin | Manage uploads, purges |
| First request | Slow (miss) | Fast |
| Storage | Filled on demand | Selected content placed ahead of demand |
| Fits | Most websites, APIs | Large, predictable files |

**Pull** is the default for almost everything: configure the origin, set cache headers and the CDN fills itself. Long-tail content that nobody requests never takes up edge storage.

**Push** suits big, predictable content: game patches, software releases, video libraries, where you know exactly what will be requested and want no cold misses at launch. Netflix's Open Connect is an extreme version: it pre-positions content on appliances inside ISPs during off-peak hours, based on predicted demand.

## Cache keys: the most important design decision

The **cache key** decides which requests share a cached object. A key can include host, path, selected query parameters, headers and cookies. Defaults vary: CloudFront's default key excludes query strings, cookies and headers unless configured.

Get it **too broad** and users get the wrong content. Get it **too narrow** and the hit ratio collapses.

### Fragmentation: keys too narrow

Consider `/product/42?utm_source=newsletter&utm_campaign=oct`. If the full query string is in the key, every combination of tracking parameters is a separate object: one hot page becomes thousands of cold ones.

Common culprits:

- Tracking parameters (`utm_*`, `fbclid`, `gclid`).
- Query parameters in random order (`?a=1&b=2` vs `?b=2&a=1`).
- `Vary: User-Agent`, which splits the cache by thousands of user-agent strings.
- Cookies in the key, when only one cookie matters.

Fixes: include only **allow-listed** query parameters and headers, sort parameters, and normalise headers into a few buckets (e.g. map `Accept-Encoding` to `br`, `gzip` or none; map user agents to `mobile` or `desktop`).

### Leakage: keys too broad

The opposite failure is worse. If a personalised response (`/account` showing Alice's name) is cached under a key that doesn't include the user, Bob gets Alice's page. Real incidents of this kind have exposed users' personal data.

> [!warning] Defaults to protect you
> Mark personalised responses `Cache-Control: private` or `no-store`, and keep authenticated paths off the CDN cache unless the key includes the identity. Also beware *web cache deception*: tricking the cache into storing `/account/profile.css` because the extension looks static.

## Invalidation and versioning

There are two ways to change cached content:

1. **Purge:** tell the CDN to drop objects (by URL, prefix or tag). Propagation time and purge semantics depend on the provider and product; purging everything can cause a miss storm on the origin.

> [!note] Measurement gap
> This lesson has no reproducible purge-latency or network-route measurements. Fixed purge and shield-route timings are omitted; numerical request examples use explicit hypothetical assumptions.
2. **Versioned URLs:** put a content hash in the filename (`app.3f9a1c.js`) and cache it for a year with `immutable`. A new deploy references a new URL, so there's nothing to purge.

Use **versioned URLs for static assets** and short TTLs or tag-based purges for HTML and API responses. **Surrogate keys** (cache tags) let you purge "everything related to product 42" across many URLs in one call.

## Tiered caching and origin shielding

With 300 PoPs each missing independently, a newly popular object could trigger **300 origin fetches**. Tiered caching adds a middle layer:

```
 Edge PoPs (hundreds)
   |   |   |   |
   v   v   v   v
 Regional / shield tier
        |
        v (one fetch)
      Origin
```

An **origin shield** is a designated PoP (or small set) that all edges go through on a miss. CloudFront's Origin Shield, Fastly's shielding and Cloudflare's Tiered Cache all do this. Benefits:

- **Fewer origin requests:** many edge misses become one shield miss.
- **Higher effective hit ratio,** because the shield's cache aggregates demand from every edge.
- **Request collapsing:** when 1,000 users request the same cacheable key at once, a shield configured to coalesce those requests can send **one** request to the origin and fans the response out. This prevents a **thundering herd** after a purge or at a live-event start.

Pick a shield region close to the origin, so the shield→origin hop is short.

## Dynamic content acceleration

Not everything is cacheable: checkout pages, API calls, search results. CDNs still help, through **dynamic site acceleration**:

1. **TLS and TCP terminate at the edge,** close to the user. Handshakes cost the short user→edge RTT.
2. **Warm, persistent connections** from edge to origin (or edge to shield to origin): no handshakes, already-open congestion windows.
3. **Optimised routing** over the CDN's private backbone or chosen paths, often faster and less lossy than default internet routing.
4. **Protocol upgrades** at the edge: HTTP/3 to the user even if your origin only speaks HTTP/1.1.

Worked example: a user in Singapore, origin in Frankfurt (RTT 160 ms), edge in Singapore (RTT 5 ms), TLS 1.3, and an edge that already holds a warm connection to the origin:

| | Direct | Via CDN |
|---|---|---|
| TCP | 160 ms | 5 ms |
| TLS 1.3 | 160 ms | 5 ms |
| Request | 160 ms | 5 + 160 ms |
| **Total** | **480 ms** | **175 ms** |

Even with zero caching, a cold request is ~2.7× faster. The remaining 160 ms is the assumed origin RTT, not a proven speed-of-light minimum. Better routes may reduce it; moving data or caching it nearby avoids the long origin round trip.

## Edge compute

Modern CDNs run code at the edge: Cloudflare Workers, Fastly Compute, CloudFront Functions and Lambda@Edge. Typical uses:

- A/B test assignment, redirects, header manipulation.
- Authentication checks (verifying a JWT) before hitting the origin.
- Personalising cached pages by stitching small dynamic pieces into cached shells.
- Serving from edge key-value stores for globally read-mostly data.

The constraint is data: edge code runs in hundreds of places, but your database usually lives in one or two regions.

## CDN as a single point of failure

CDN outages have taken down large swathes of the web: Fastly in June 2021 (a valid customer config change triggered a latent bug, and about 85% of its network returned errors; most of it recovered within about 50 minutes), and Cloudflare in several incidents. Mitigations include **multi-CDN** setups with DNS-based traffic steering between providers, and being able to serve directly from origin in an emergency (if it can survive the load).

## Key takeaways

- CDNs serve from edges near users, cut origin load and absorb attacks; cache hit ratio is the key metric.
- Pull is the default; push suits large, predictable content.
- Cache keys must include everything that changes the response and nothing that doesn't; fragmentation kills hit ratio, leakage leaks data.
- Use versioned URLs for static assets; purge or tag-invalidate the rest.
- Origin shields and request collapsing turn many misses into one origin fetch.
- Even uncacheable traffic gets faster via edge TLS termination, warm origin connections and better routing.

## Further reading

- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
- [Using Amazon CloudFront Origin Shield (AWS)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html)
- [Understand the cache key (Amazon CloudFront)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [Cloud CDN overview (Google Cloud)](https://cloud.google.com/cdn/docs/overview)
- [Vary header (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary)
