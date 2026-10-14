---
id: net-cdn-dynamic-data-locality
title: "Dynamic acceleration and edge data locality"
level: advanced
minutes: 3
summary: "Calculate warm-origin acceleration and decide whether edge compute keeps data access close enough."
sourceLesson: net-cdn
---
An edge can improve dynamic traffic without caching it. Keep the round-trip assumptions explicit, and distinguish moving the handshake from moving the data.

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

As a formula:

```formula
T_direct = 3 × RTT_origin
T_direct = 3 × 160 ms = 480 ms
T_cdn = 3 × RTT_edge + RTT_origin
T_cdn = 3 × 5 ms + 160 ms = 175 ms
T_direct / T_cdn = 480 / 175 ≈ 2.7
where
T_direct: the time to the first response byte when the user connects straight to the origin, in milliseconds (ms)
T_cdn: the same time through the CDN edge
RTT_origin: the round-trip time to the origin in Frankfurt, 160 ms from Singapore in this example
RTT_edge: the round-trip time from the user to the Singapore edge, 5 ms
3: the round trips on a new connection: TCP handshake, TLS 1.3 handshake and the request itself
ms: millisecond, one thousandth of a second
≈: approximately equal to
In words: going direct pays all three round trips over the long path; via the CDN, only the request itself crosses it, because the edge's connection to the origin is already open.
```

Even with zero caching, a cold request is ~2.7× faster. The remaining 160 ms is the assumed origin RTT, not a proven speed-of-light minimum. Better routes may reduce it; moving data or caching it nearby avoids the long origin round trip.

## Edge compute

Modern CDNs run code at the edge: Cloudflare Workers, Fastly Compute, CloudFront Functions and Lambda@Edge. Typical uses:

- A/B test assignment, redirects, header manipulation.
- Authentication checks (verifying a JWT) before hitting the origin.
- Personalising cached pages by stitching small dynamic pieces into cached shells.
- Serving from edge key-value stores for globally read-mostly data.

The constraint is data: edge code runs in hundreds of places, but your database usually lives in one or two regions.

Moving page code near a user does not automatically move its database. Three sequential edge-to-database queries cross the long path three times; rendering next to the database can perform those queries locally and return the whole page over one warm origin trip. Put chatty computation beside its data unless the needed data is cached or replicated at the edge.

## Key takeaways

- Uncacheable requests can still save remote setup trips through edge TLS and warm origin connections.
- A long origin request trip remains unless the data or response moves closer.
- Edge compute helps most when its data is local or unnecessary; sequential remote database calls can outweigh proximity to the user.

## Further reading

- [Cloud CDN overview (Google Cloud)](https://cloud.google.com/cdn/docs/overview)
- [Using Amazon CloudFront Origin Shield (AWS)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html)
