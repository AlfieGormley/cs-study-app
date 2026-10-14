---
id: cache-http-variants-and-shared-caches
title: Control HTTP variants and shared-cache privacy
level: intermediate
minutes: 3
summary: Use Vary and s-maxage without fragmenting a public cache or leaking personalised responses.
sourceLesson: cache-http
---

A shared cache may answer many users from one stored response. Its cache key and storage policy must describe when those users are entitled to the same representation.

## Vary: one URL, several responses

A cache keys stored responses by method and URL. But the same URL may return different content depending on request headers, such as compression or language. The `Vary` header tells caches which request headers must also match.

```
 Vary: Accept-Encoding
```

Reuse must match the nominated Accept-Encoding request header, allowing the cache to distinguish encoding variants. Header normalisation and the encodings a client accepts determine which variant is eligible.

Use `Vary` carefully:

- `Vary: Accept-Encoding` is common and usually necessary when encoding changes the representation; it still adds variants.
- `Vary: User-Agent` is almost always a mistake. There are thousands of distinct user-agent strings, so the cache fragments into thousands of copies and the hit ratio collapses.
- Vary: Cookie keys variants by the cookie header; user-specific cookies can fragment a shared cache, but identical cookie values can still hit. Often better: strip cookies at the CDN for anonymous pages, or mark personalised responses `private`.

CDNs often normalise headers before using them as a key (for example collapsing `Accept-Encoding` to `br`, `gzip` or none) to stop this fragmentation.

## Shared caches and purging

A CDN or reverse proxy is a **shared** cache. Use `s-maxage` to give it a different lifetime from browsers. A common pattern:

```
Cache-Control: public, max-age=0,
               s-maxage=300, must-revalidate
```

Browsers always revalidate; the CDN keeps it for 5 minutes. When content changes, you **purge** the CDN through its API, whereas browser clearing requires a later response such as supported Clear-Site-Data and is not a universal immediate remote purge. Many CDNs support tag-based purging (`Surrogate-Key` / `Cache-Tag` headers), so "purge everything tagged `product-9`" clears every page that shows that product.

> [!warning] Caching authenticated responses
> Shared caches won't store a response to a request with an `Authorization` header unless the response explicitly allows it with `public`, `s-maxage` or `must-revalidate`. Note that cookies get no such protection: a response to a request carrying a session cookie *can* be stored by a shared cache unless you mark it `private`. Adding `public` to an API that returns per-user data is a classic data leak.

## Key takeaways
- Vary includes selected request headers in variant matching; user-agent and cookie values can create many distinct copies.
- S-maxage gives a shared cache its own lifetime, and provider purge APIs remove shared responses after publication.
- Cookie-bearing requests have no automatic protection equivalent to Authorization; mark personalised responses private or no-store.

## Further reading
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [Vary — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Vary)
