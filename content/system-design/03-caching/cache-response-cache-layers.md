---
id: cache-response-cache-layers
title: Place response caches near the reader
level: basic
minutes: 3
summary: Compare browser, CDN and reverse-proxy caches, including privacy and fingerprinted asset names.
sourceLesson: cache-fundamentals
---

Response caches save a trip to the origin or application. Their location determines who shares a copy and how easily you can replace it.

## The layers where caches live

A single web request can pass through half a dozen caches before it reaches the disk.

```
 Browser cache     (per user, HTTP headers)
      |
 CDN edge          (shared, near the user)
      |
 Reverse proxy     (Varnish / Nginx)
      |
 App server        (in-process memory)
      |
 Distributed cache (Redis / Memcached)
      |
 Database          (buffer pool, page cache)
      |
 Disk
```

Each layer sits closer to the user than the one below it. Caching closer to the user saves more latency but gives you less control over invalidation.

| Layer | Main saving | Who controls it |
|---|---|---|
| Browser | Network request | Browser and response policy |
| CDN edge | Origin trip | Provider configuration |
| Reverse proxy | Application work | Service operator |
| In-process | Network and decoding work | Application |
| Redis / Memcached | Database work | Cache operator |
| DB buffer pool | Storage reads | Database |

### Browser cache

The browser stores responses keyed by URL and obeys `Cache-Control`, `ETag` and friends. It is local to a browser profile, not necessarily one application account. A long freshness lifetime permits reuse; it does not guarantee retention. Supporting browsers can honour a `Clear-Site-Data` header on a later response, but there is no universal, immediate way to remotely empty every browser's cache. That is why static assets use **fingerprinted file names** such as `app.3f9a1c.js`. A new version is a new URL, so the old cached copy simply stops being requested.

> [!analogy] Real-world analogy: notices pinned around town
> A club pins a timetable on its own door, in the library and on dozens of noticeboards. Changing the copy on its own door is easy; tracking down every other copy is not. So instead the club prints next season's timetable under a new title and updates the one index board everyone checks first.
>
> **How it maps:** The noticeboards are caches at different distances from the origin. The further out a copy sits (CDN, then browsers), the less direct control you have over removing it. The new title is the fingerprinted URL, and the index board is the HTML page, which is revalidated and points at the new asset.
>
> **Where it stops:** Old notices stay up until someone removes them, whereas cached responses also expire or get evicted on their own. And unlike a public noticeboard, a shared cache must never show one person's private page to someone else.

### CDN edge

Large CDNs can keep copies in hundreds of points of presence (PoPs) worldwide, allowing an Australian user to fetch from a nearby edge rather than a distant origin. Actual placement and routing depend on the provider and request. It is a **shared** cache, so it must never store one user's private response and hand it to another. CDNs are covered in the networking module; here, remember that they are just another HTTP cache with a purge API.

### Reverse proxy

Varnish, Nginx (`proxy_cache`) or a cloud load balancer can cache full HTTP responses in front of your app servers. This is very effective for pages that are the same for every anonymous visitor, such as a news homepage.

## Key takeaways
- Browser caches retain copies per browser profile; fingerprinted URLs select a new asset version without a universal browser purge.
- CDNs and reverse proxies share responses, so private user data needs an explicit caching policy.
- Moving a cache towards the reader saves more downstream work while making invalidation less direct.

## Further reading
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Historical latency estimates — not deployment measurements](https://gist.github.com/jboner/2841832)
