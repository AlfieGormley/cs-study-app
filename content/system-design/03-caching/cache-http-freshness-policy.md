---
id: cache-http-freshness-policy
title: Decide whether an HTTP response is still fresh
level: intermediate
minutes: 4
summary: Interpret Cache-Control storage directives, current age and the requirement to validate stale responses.
sourceLesson: cache-http
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

Most directives are defined in RFC 9111; `immutable` comes from RFC 8246, and the `stale-*` directives from RFC 5861 (covered in the later stale-serving unit).

Two common points of confusion:

- **`no-cache` does not mean "don't cache".** It means "you may store it, but you must check with me before each use". Use no-store to prohibit intentional HTTP-cache storage. It is not a guarantee that data never reaches disk, browser history or a compromised cache, nor a complete privacy mechanism.
- **`private` matters for shared caches.** A response containing a user's name or basket must be `private` (or `no-store`), otherwise a CDN might hand it to the next visitor.

A response's **age** is the time since the origin generated or last validated it; shared caches pass it on in an `Age` header. A stored response is fresh while its age is less than its **freshness lifetime**, which comes from `s-maxage` (shared caches only), then `max-age`, then the older `Expires` header. RFC 9111 states the test like this:

```formula
a < L
r = L − a
where
a: the response's current age, in seconds (s): time since the origin generated or last validated it, including any time already spent in other caches (the Age header)
L: the freshness lifetime, in seconds; from s-maxage (shared caches only), else max-age, else Expires minus the response's Date
r: the freshness remaining, in seconds; once it reaches 0 the response is stale
<: is less than; while a < L holds, the response is fresh and the cache may reuse it without contacting the origin; once it fails, the response is stale
s: seconds
In words: a cached response is fresh while it is younger than its lifetime, and the time left is the lifetime minus its age.
```

For example, a browser that receives `max-age=300` from a CDN with `Age: 250` may treat it as fresh for only 300 − 250 = 50 more seconds, not 300. A response whose age reaches its lifetime is stale: the cache must revalidate it before reuse, unless a directive such as `stale-while-revalidate` allows otherwise.

Why `must-revalidate`? HTTP normally lets a cache serve a stale response in some situations, such as when it is disconnected from the origin. `must-revalidate` forbids that: once stale, the cache must revalidate successfully or return an error (typically `504 Gateway Timeout`). Use it when serving stale data would be worse than serving an error.

## Key takeaways
- A response is fresh only while its current age is less than its freshness lifetime; time upstream has already consumed part of it.
- No-cache allows storage but requires validation; no-store prohibits intentional HTTP-cache storage and is not a complete privacy mechanism.
- Must-revalidate prevents reuse of a stale response without successful validation; private keeps a response out of shared caches.

## Further reading
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [Cache-Control — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
- [RFC 8246: HTTP Immutable Responses](https://www.rfc-editor.org/rfc/rfc8246)
