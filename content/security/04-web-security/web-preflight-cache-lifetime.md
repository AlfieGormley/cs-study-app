---
id: web-preflight-cache-lifetime
title: Preflight cache lifetime and matching
level: intermediate
minutes: 3
sourceLesson: web-sop-cors
summary: A cached permission has a bounded lifetime and specific matching conditions.
---

The previous unit's preflight approved a cross-origin `DELETE` carrying an `x-token` header. Sending an extra `OPTIONS` before every such request costs a round trip, so the browser can remember a successful preflight and reuse it. This **preflight cache** is separate from the ordinary HTTP cache that stores page and API responses.

## How long the permission lasts

The server suggests a lifetime with `Access-Control-Max-Age`, in seconds. The browser then applies its own rules:

- **It uses whichever is shorter:** the server's request or the browser's own cap.
- **Chromium's cap is two hours** (7,200 seconds) in its current source. Other browsers use their own caps, and they can change between versions.
- **A missing or invalid value means five seconds**, the default in the Fetch Standard.
- **The browser may forget sooner.** The standard allows early removal at any time, and a CORS failure on a later request to the same URL clears the matching entries. The requested lifetime is an upper limit, not a promise.

So the earlier `Access-Control-Max-Age: 600` lets the browser skip new preflights for at most ten minutes. A server sending 86,400 (one day) still gets at most two hours in Chromium. If you see `OPTIONS` requests reappearing in your logs, that is the browser's cap or eviction at work, not a server bug.

## When a cached permission can be reused

Reuse needs a close match with the original preflight:

- **Same requester and target:** the same requesting origin, the same URL, and the same top-level site (browsers keep a separate preflight cache for each site the user is visiting).
- **Covered method and headers:** a later request with a method or header that the cached answer did not allow needs a new preflight. One that the cached answer already covers does not.
- **Credentials:** an approval obtained for a request with credentials can cover a later request without them, but not the other way round.

The cache only saves the browser from asking again. It never weakens the server's own checks, which still run on every real request.

## Key takeaways
- The browser keeps a preflight approval for the shorter of the server's requested lifetime and its own cap, and may drop it sooner.
- A missing or invalid `Access-Control-Max-Age` gives only five seconds of reuse.
- Reuse needs the same origin, URL and top-level site, plus a cached answer that covers the method, headers and credentials mode.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [Chromium preflight result implementation](https://raw.githubusercontent.com/chromium/chromium/main/services/network/cors/preflight_result.cc)
