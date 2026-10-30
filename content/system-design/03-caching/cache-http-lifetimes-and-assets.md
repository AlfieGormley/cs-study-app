---
id: cache-http-lifetimes-and-assets
title: Set explicit lifetimes for HTML and versioned assets
level: intermediate
minutes: 3
summary: Avoid heuristic freshness surprises and pair fingerprinted assets with HTML validation.
sourceLesson: cache-http
---

A missing freshness policy does not necessarily make a response uncacheable. Set explicit lifetimes so an unchanged-looking page does not remain silently fresh after you publish a new version.

If there is no explicit lifetime, caches may apply a **heuristic** to responses that are cacheable by default (such as a `200` to a `GET`). RFC 9111 encourages a lifetime of no more than some fraction of the time since `Last-Modified`, and says a typical setting of that fraction might be 10%:

```formula reference
L_h = k × (t_resp − t_mod)
where
L_h: the heuristic freshness lifetime the cache picks, in seconds or days
k: the fraction the cache uses; RFC 9111 only says "some fraction" and that 10% (0.1) might be typical, so each cache chooses its own
t_resp: when the response was generated (its Date header)
t_mod: when the resource last changed (its Last-Modified header)
In words: the longer a file has gone unchanged, the longer a cache may guess it will stay unchanged, typically about a tenth as long again. A file last changed 10 days ago may be treated as fresh for about a day.
```

So a page with no `Cache-Control` can be served from a cache for a day or more after you publish a new version, with no request to the origin. Each cache chooses its own heuristic, so the behaviour also varies between browsers and CDNs. This surprises people, so always set `Cache-Control` explicitly.

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

The number 31536000 is simply one (non-leap) year in seconds: an example of a "keep it as long as you like" lifetime for a fingerprinted asset, which is safe only because a new version gets a new URL.

## Key takeaways
- Heuristic freshness is provider-dependent; the RFC’s ten-percent example is guidance, not a universal rule.
- Fingerprinted asset names allow long fresh lifetimes because a new version has a new URL.
- HTML with no-cache checks for a new document, which can then reference the latest assets.

## Further reading
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [HTTP caching — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [RFC 8246: HTTP Immutable Responses](https://www.rfc-editor.org/rfc/rfc8246)
