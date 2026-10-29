---
id: net-cdn-dynamic-data-locality
title: "Dynamic acceleration and edge data locality"
level: advanced
minutes: 3
summary: "Explain how an edge speeds up uncacheable requests and decide whether edge compute keeps data access close enough."
sourceLesson: net-cdn
---
An edge can improve dynamic traffic without caching it. The key distinction is between moving the handshakes and moving the data.

## Dynamic content acceleration

Not everything is cacheable: checkout pages, API calls, search results. CDNs still help, through **dynamic site acceleration**:

1. **TLS and TCP terminate at the edge,** close to the user. Handshakes cost the short user→edge RTT.
2. **Warm, persistent connections** from edge to origin (or edge to shield to origin): no handshakes, already-open congestion windows.
3. **Optimised routing** over the CDN's private backbone or chosen paths, often faster and less lossy than default internet routing.
4. **Protocol upgrades** at the edge: HTTP/3 to the user even if your origin only speaks HTTP/1.1.

Illustrative example (assumed figures, not measurements): a user in Singapore, origin in Frankfurt with a 160 ms RTT, a Singapore edge 5 ms away that already holds a warm connection to the origin, and TLS 1.3 on a new user connection:

| Step | Direct | Via CDN edge |
|---|---|---|
| TCP handshake | 160 ms | 5 ms |
| TLS 1.3 handshake | 160 ms | 5 ms |
| Request and response | 160 ms | 5 + 160 ms |
| **Total** | **480 ms** | **175 ms** |

Even with nothing cached, the edge cuts the wait to roughly a third, because only the request itself crosses the long path; the handshakes happen on the short hop. What it cannot remove is that one remaining trip to the origin. Better routes over the CDN's backbone may shorten it somewhat, but only moving or caching the data nearer the user avoids it.

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
