---
id: net-cdn-purges-origin-shields
title: "Versioning, purges and origin shields"
level: advanced
minutes: 3
summary: "Refresh content without a miss storm and collapse edge demand before it reaches the origin."
sourceLesson: net-cdn
---
A release or viral object can turn many warm caches into simultaneous misses. Treat invalidation policy and origin protection as one capacity problem.

## Invalidation and versioning

There are two ways to change cached content:

1. **Purge:** tell the CDN to drop objects (by URL, prefix or tag). Propagation time and purge semantics depend on the provider and product; purging everything can cause a miss storm on the origin.
2. **Versioned URLs:** put a content hash in the filename (`app.3f9a1c.js`) and cache it for a year with `immutable`. A new deploy references a new URL, so there's nothing to purge.

> [!note] Measurement gap
> This lesson has no reproducible purge-latency or network-route measurements. Fixed purge and shield-route timings are omitted; numerical request examples use explicit hypothetical assumptions.

Use **versioned URLs for static assets** and short TTLs or tag-based purges for HTML and API responses. **Cache tags** (surrogate keys) let you purge "everything related to product 42" across many URLs in one call.

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

## CDN as a single point of failure

CDN outages have taken down large swathes of the web: Fastly in June 2021 (a valid customer config change triggered a latent bug, and about 85% of its network returned errors; most of it recovered within about 50 minutes), and Cloudflare in several incidents. Mitigations include **multi-CDN** setups with DNS-based traffic steering between providers, and being able to serve directly from origin in an emergency (if it can survive the load).

### Refresh without blocking every reader

When stale content is acceptable, `stale-while-revalidate` lets a cache serve the old response within its permitted stale window while it refreshes in the background. Combine that with request collapsing to avoid many simultaneous refreshes for the same key. It helps after TTL expiry; it cannot turn a never-cached object into a hit.

## Key takeaways

- Content-hashed static URLs separate releases without purging unchanged assets.
- A broad purge can suddenly make the origin handle the full request rate.
- A nearby origin shield, tiered caches and request collapsing reduce duplicate fetches; plan for CDN failure too.

## Further reading

- [Using Amazon CloudFront Origin Shield (AWS)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html)
- [HTTP caching (RFC 9111)](https://www.rfc-editor.org/rfc/rfc9111)
- [Fastly outage account](https://www.fastly.com/blog/summary-of-june-8-outage)
- [Stale-content cache extensions (RFC 5861)](https://www.rfc-editor.org/rfc/rfc5861)
