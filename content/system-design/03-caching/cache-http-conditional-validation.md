---
id: cache-http-conditional-validation
title: Validate a retained response without its body
level: intermediate
minutes: 3
summary: Trace ETag and Last-Modified conditional requests and keep validators stable across origin servers.
sourceLesson: cache-http
---

Once freshness ends, a retained response can still save bandwidth. A conditional request asks whether its validator still identifies the current representation.

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

A `304 Not Modified` has no body, so it saves bandwidth and the cache updates the stored response headers and recomputes its age and freshness under RFC 9111. A 304 does not unconditionally grant a new fixed lifetime. If the resource has changed, the origin replies `200` with the new body and a new ETag.

ETags can be **strong** (`"a1b2c3"`, byte-for-byte identical) or **weak** (`W/"a1b2c3"`, semantically equivalent, for example the same article with a different timestamp in the footer). Some servers, including the Nginx 1.26.3 gzip filter, turn a strong ETag into a weak one when they compress a response on the fly, because the bytes are no longer the ones the ETag described. Weak ETags are fine for `If-None-Match` but not for byte-range requests.

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

If each server generates ETags from local details (Apache once used inode numbers), the same file has different ETags on different servers, and switching servers can cause unnecessary full responses even when the file is unchanged. Generate ETags from the **content** (a hash) or from a **version number** in the database.

## Key takeaways
- A matching conditional request gets a body-free 304; changed content gets a new body and validator.
- Validation still pays a network round trip, so freshness and validation save different costs.
- Use content or database revisions for consistent validators across servers; If-None-Match takes precedence over a modification-time condition.

## Further reading
- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
