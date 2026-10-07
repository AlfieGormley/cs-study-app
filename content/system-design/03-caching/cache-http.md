---
id: cache-http
title: HTTP caching
level: intermediate
minutes: 12
summary: How browsers, proxies and CDNs decide what to store and for how long — Cache-Control, validators (ETag, Last-Modified), Vary and stale-while-revalidate.
---

HTTP has caching built into the protocol. Browsers, corporate proxies, reverse proxies and CDNs all follow the same rules, defined in **RFC 9111**. If you set the headers correctly, a compliant cache may reuse eligible responses; actual cache enablement and optional feature support depend on the browser/provider. If you set them wrongly, you get stale pages, or worse, one user's private data served to another.

There are two separate questions a cache asks:

1. **Freshness**: may I serve my stored copy without asking the origin?
2. **Validation**: once it's stale, can I cheaply check whether it's still correct?

## Freshness: Cache-Control

The origin tells caches how to behave with the `Cache-Control` response header.

| Directive | Meaning |
|---|---|
| `max-age=N` | Fresh for N seconds |
| `s-maxage=N` | Like max-age, shared caches only |
| `public` | Any cache may store it |
| `private` | Only private caches (the browser) |
| `no-cache` | Store, but revalidate every use |
| `must-revalidate` | Once stale, never reuse unvalidated |
| `no-store` | Forbid intentional HTTP-cache storage |
| `immutable` | Won't change while fresh |

Most directives are defined in RFC 9111; `immutable` comes from RFC 8246, and the `stale-*` directives from RFC 5861 (covered below).

Two common points of confusion:

- **`no-cache` does not mean "don't cache".** It means "you may store it, but you must check with me before each use". Use no-store to prohibit intentional HTTP-cache storage. It is not a guarantee that data never reaches disk, browser history or a compromised cache, nor a complete privacy mechanism.
- **`private` matters for shared caches.** A response containing a user's name or basket must be `private` (or `no-store`), otherwise a CDN might hand it to the next visitor.

A response's **age** is the time since the origin generated or last validated it; shared caches pass it on in an `Age` header. A stored response is fresh while its age is less than its **freshness lifetime**, which comes from `s-maxage` (shared caches only), then `max-age`, then the older `Expires` header.

Why `must-revalidate`? HTTP normally lets a cache serve a stale response in some situations, such as when it is disconnected from the origin. `must-revalidate` forbids that: once stale, the cache must revalidate successfully or return an error (typically `504 Gateway Timeout`). Use it when serving stale data would be worse than serving an error.

If there is no explicit lifetime, caches may apply a **heuristic** to responses that are cacheable by default (such as a `200` to a `GET`). RFC 9111 suggests a fraction of the time since `Last-Modified`, with 10% as a typical setting: a file last changed 10 days ago may be treated as fresh for a day. This surprises people, so always set `Cache-Control` explicitly.

### Typical policies

```
# Fingerprinted assets (app.3f9a1c.js)
Cache-Control: public, max-age=31536000,
               immutable

# HTML pages
Cache-Control: no-cache

# Logged-in API response
Cache-Control: private, max-age=0

# Sensitive data
Cache-Control: no-store
```

HTML is set to `no-cache` so the browser always checks for a new page, which in turn references the latest fingerprinted assets.

## Validation: ETag and Last-Modified

When a cached response goes stale, the cache doesn't have to download it again. It can send a **conditional request** asking "has this changed?".

### ETag / If-None-Match

The origin labels each version of a resource with an **ETag**, an opaque identifier, often a hash of the content.

```
 First request
 GET /api/products/9
 <- 200 OK
    ETag: "a1b2c3"
    Cache-Control: max-age=60

 After 60 s (stale)
 GET /api/products/9
 If-None-Match: "a1b2c3"
 <- 304 Not Modified   (no body)
```

A `304 Not Modified` has no body, so it saves bandwidth and the cache resets the freshness clock on its stored copy. If the resource has changed, the origin replies `200` with the new body and a new ETag.

ETags can be **strong** (`"a1b2c3"`, byte-for-byte identical) or **weak** (`W/"a1b2c3"`, semantically equivalent, for example the same article with a different timestamp in the footer). Some servers, Nginx among them, turn a strong ETag into a weak one when they compress a response on the fly, because the bytes are no longer the ones the ETag described. Weak ETags are fine for `If-None-Match` but not for byte-range requests.

### Last-Modified / If-Modified-Since

The older mechanism uses timestamps:

```
 <- Last-Modified:
      Tue, 01 Sep 2026 10:00:00 GMT
 -> If-Modified-Since:
      Tue, 01 Sep 2026 10:00:00 GMT
 <- 304 Not Modified
```

Its weakness is one-second resolution, and it relies on reliable modification times. When both are present, `If-None-Match` takes precedence.

> [!tip] A 304 still costs a round trip
> Validation saves bytes, not latency. For a 2 KB JSON response the round trip dominates, so a `max-age` that avoids the request entirely is worth far more than an ETag.

### ETags and multiple servers

If each server generates ETags from local details (Apache once used inode numbers), the same file has different ETags on different servers, and revalidation fails half the time behind a load balancer. Generate ETags from the **content** (a hash) or from a **version number** in the database.

## Vary: one URL, several responses

A cache keys stored responses by method and URL. But the same URL may return different content depending on request headers, such as compression or language. The `Vary` header tells caches which request headers must also match.

```
 Vary: Accept-Encoding
```

Now a gzip copy and a Brotli copy are stored separately, and a client asking for Brotli never gets the gzip body.

Use `Vary` carefully:

- `Vary: Accept-Encoding` is normal and harmless.
- `Vary: User-Agent` is almost always a mistake. There are thousands of distinct user-agent strings, so the cache fragments into thousands of copies and the hit ratio collapses.
- Vary: Cookie keys variants by the cookie header; user-specific cookies can fragment a shared cache, but identical cookie values can still hit. Often better: strip cookies at the CDN for anonymous pages, or mark personalised responses `private`.

CDNs often normalise headers before using them as a key (for example collapsing `Accept-Encoding` to `br`, `gzip` or none) to stop this fragmentation.

## stale-while-revalidate and stale-if-error

Defined in **RFC 5861**, these let a cache serve stale content in controlled ways.

```
Cache-Control: max-age=60,
  stale-while-revalidate=300,
  stale-if-error=86400
```

- For the first 60 s: fresh, served directly.
- From 60 s to 360 s: serve the stale copy **immediately**, and refresh it in the background.
- If the origin is unreachable or returns `500`, `502`, `503` or `504`: serve the stale copy for up to a day after it went stale.

```
 age 0      60          360
 |-fresh-|--SWR window--|-- must fetch
          ^ serve stale + refresh async
```

`stale-while-revalidate` hides origin latency from users: a supporting cache may serve stale within the window and refresh asynchronously. Coalescing can reduce background requests, but the directive does not itself guarantee exactly one refresh.

`stale-if-error` turns your cache into an availability tool: a crashed origin shows slightly old pages rather than an error.

> [!note] Support varies
> These directives are optional for caches: a cache that doesn't understand them simply ignores them. Major browsers support `stale-while-revalidate`, but `stale-if-error` is mainly honoured by CDNs and proxies, and each CDN documents its own behaviour. Check your provider before relying on either.

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
- Freshness (`max-age`, `s-maxage`) decides whether a cache can skip the origin; validation (ETag, Last-Modified) makes checking cheap.
- `no-cache` means revalidate before every use; `must-revalidate` means revalidate once stale; `no-store` means never store. `private` keeps responses out of shared caches.
- Fingerprinted assets: `max-age=31536000, immutable`. HTML: `no-cache`.
- `Vary` splits the cache key by request headers; `Vary: User-Agent` destroys hit ratio.
- `stale-while-revalidate` hides refresh latency; `stale-if-error` keeps serving when the origin fails.

## Further reading
- [HTTP caching — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Cache-Control — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [RFC 5861: stale-while-revalidate and stale-if-error](https://www.rfc-editor.org/rfc/rfc5861)
- [Keeping things fresh with stale-while-revalidate — web.dev](https://web.dev/articles/stale-while-revalidate)
- [Vary — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Vary)
