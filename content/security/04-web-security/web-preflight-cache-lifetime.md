---
id: web-preflight-cache-lifetime
title: Preflight cache lifetime and matching
level: intermediate
minutes: 3
sourceLesson: web-sop-cors
summary: A cached permission has a bounded lifetime and specific matching conditions.
---

The preceding unit introduced the OPTIONS exchange for a CORS DELETE carrying x-token. A later matching request may reuse a successful permission instead of sending OPTIONS again. This cache is separate from ordinary HTTP response caching.

The actual `DELETE` needs successful preflight permission. Fetch specifies a five-second default when the Access-Control-Max-Age value is missing or invalid, with implementation caps and entries possibly dropped earlier. Chromium source currently uses a two-hour maximum; this is version-specific, not a guarantee that entries are kept that long or a cache shared with ordinary HTTP responses.

How long can the browser keep using a cached preflight before it must send another `OPTIONS`? The server asks for a lifetime, and the browser applies its own cap. The limit is whichever is smaller:

```formula
t_cache = min(t_req, t_cap)
t_cache = min(600 s, 7200 s)
t_cache = 600 s
where
t_cache: the longest time the browser may keep using this cached preflight permission, in seconds (s). It is a maximum: the browser may drop the entry sooner
t_req: the lifetime the server asked for in Access-Control-Max-Age, in seconds (s); here 600 s (ten minutes). The Fetch Standard uses 5 s when the header is missing or invalid
t_cap: the browser's own maximum, in seconds (s); 7200 s (two hours) in current Chromium source, and different in other browsers and versions
min: the minimum function, which returns the smaller of its two inputs
s: seconds, the unit of time
In words: the browser keeps the cached permission for the server's requested time or its own cap, whichever is shorter, and possibly less.
```

So the example above lets the browser skip new preflights for at most ten minutes. Had the server sent 86,400 s (one day), Chromium would still stop at its 7,200 s cap. Reuse requires a matching network partition key, serialized request origin and URL, plus the needed method/header permissions. A credentials-enabled entry can cover a later request without credentials mode include; an entry created without include cannot cover a later include request. A changed method or header needs another preflight only if the cached permissions do not already cover it.

## Key takeaways
- The smaller of the requested lifetime and implementation cap bounds reuse.
- A browser can evict permission earlier; max-age is not a retention promise.
- Reuse also requires matching cache-key and method/header conditions.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [Chromium preflight result implementation](https://raw.githubusercontent.com/chromium/chromium/main/services/network/cors/preflight_result.cc)
