---
id: cache-http-stale-serving
title: Bound stale serving during refreshes and outages
level: intermediate
minutes: 3
summary: Calculate stale-while-revalidate and stale-if-error windows and check optional provider support.
sourceLesson: cache-http
---

When slightly old content is acceptable, optional HTTP extensions can return it while refreshing or while the origin fails. Their windows begin when the ordinary freshness lifetime ends.

## stale-while-revalidate and stale-if-error

Defined in **RFC 5861**, these let a cache serve stale content in controlled ways.

```
Cache-Control: max-age=60,
  stale-while-revalidate=300,
  stale-if-error=86400
```

- For the first 60 s: fresh, served directly.
- From 60 s to 360 s: serve the stale copy **immediately**, and refresh it in the background.
- If the origin is unreachable or returns `500`, `502`, `503` or `504`: serve the stale copy for up to a day (86,400 s) after it went stale.

Each stale window starts when freshness ends, not when the response was stored. So with these headers background refresh is allowed up to an age of 360 s (60 + 300), and error fallback up to a day after the copy went stale.

```
 age 0      60          360
 |-fresh-|--SWR window--|-- must fetch
          ^ serve stale + refresh async
```

`stale-while-revalidate` hides origin latency from users: a supporting cache may serve stale within the window and refresh asynchronously. Coalescing can reduce background requests, but the directive does not itself guarantee exactly one refresh.

`stale-if-error` turns your cache into an availability tool: a crashed origin shows slightly old pages rather than an error.

> [!note] Support varies
> These directives are optional for caches: a cache that doesn't understand them simply ignores them. Browser versions and CDN products differ in which directives and failure cases they support. Use your deployed cache’s documentation and an integration check. Check your provider before relying on either.

## Key takeaways
- Stale windows begin when freshness ends, so each extends the permitted age beyond `max-age`.
- Stale-while-revalidate can hide refresh waits; stale-if-error can preserve availability during eligible origin failures.
- These extensions depend on cache support and do not themselves guarantee exactly one background refresh.

## Further reading
- [RFC 5861: stale-while-revalidate and stale-if-error](https://www.rfc-editor.org/rfc/rfc5861)
- [Keeping things fresh with stale-while-revalidate — web.dev](https://web.dev/articles/stale-while-revalidate)
