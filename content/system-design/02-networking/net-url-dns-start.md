---
id: net-url-dns-start
title: "From a URL to a server address"
level: basic
minutes: 4
summary: "Trace the browser’s local checks and DNS lookup before it opens a connection."
sourceLesson: net-request-lifecycle
---
"What happens when you type `https://shop.example.com/cart` into a browser and press Enter?" is the classic opening question in networking interviews. It's popular because a good answer touches almost every layer a system designer works with: naming, transport, security, load balancing, caching and the application itself.

These short lessons walk the path end to end, then zoom into its naming, transport, security and routing decisions.

## The big picture

```
 Browser
   |  1. parse URL, check caches
   |  2. DNS: name -> IP
   v
 Resolver --> root -> .com -> example.com
   |
   |  3. TCP handshake (1 RTT)
   |  4. TLS handshake (1 RTT)
   |  5. HTTP request
   v
 CDN edge --(miss)--> Load balancer
                          |
                          v
                     App servers
                          |
                          v
                    DB / caches
```

The DNS arrow row names the hierarchy, rather than messages passed from root to TLD to authoritative servers: the recursive resolver queries each server itself. Roughly, the steps are:

1. **Parse the URL** and check local caches.
2. **Resolve the name** to an IP address with DNS.
3. **Open a transport connection** (TCP, or QUIC for HTTP/3).
4. **Negotiate encryption** with TLS.
5. **Send the HTTP request** and receive the response, possibly via a CDN, load balancer and reverse proxy.
6. **Render** the page, which triggers dozens more requests.

## Parse the URL and check caches

The browser splits the URL into parts:

| Part | Value |
|---|---|
| Scheme | `https` (so port 443) |
| Host | `shop.example.com` |
| Path | `/cart` |
| Query/fragment | none |

Before touching the network, it checks a few things:

- **HSTS list.** If the site has sent a `Strict-Transport-Security` header before (or is on the browser's preload list), the browser upgrades `http://` to `https://` itself, skipping an insecure redirect. HSTS is learnt over a valid HTTPS connection or from the preload list, so without a prior policy (or another browser HTTPS-first feature) an explicit first `http://` visit still travels unencrypted before being redirected.
- **HTTP cache.** If a fresh copy of the resource is stored, the browser can use it with zero network traffic. (Cache headers are covered in the caching module.)
- **Existing connections.** If there's already an open connection to this origin, it can be reused, skipping steps 2 to 4 entirely.

That last point matters enormously. The first request to a site is expensive; later ones are cheap because connections are kept alive.

## DNS resolution

Computers route IP packets by address. A browser may use the operating system resolver or its own resolver, including DNS over HTTPS. Cached answers may avoid a lookup; otherwise a **recursive resolver** resolves the name.

If the recursive resolver has no cached answer, it walks the hierarchy:

1. Ask a **root server**: "who handles `.com`?"
2. Ask the **`.com` TLD server**: "who handles `example.com`?"
3. Ask `example.com`'s **authoritative server**: "what is `shop.example.com`?"

The answer comes back with a **TTL**, telling every cache how long it may keep it. Latency depends on cache state, resolver placement and the authoritative path.

> [!note] DNS is also a routing tool
> The authoritative server doesn't have to give everyone the same answer. Large sites return different IPs depending on where you are, which is the basis of GeoDNS and CDN steering. More on that in the DNS and global traffic lessons.

Notice what the shortcuts have in common: each reuses state from an earlier visit (a cached response, a cached DNS answer, a remembered HSTS policy or an open connection). Header values that merely describe a message, such as `Content-Length` (the body size in bytes), remove no lookups, handshakes or redirects.

## Key takeaways

- Local HTTP caches and existing connections can avoid network work entirely.
- HSTS upgrades known HTTP names locally; an unprotected first HTTP visit may still need a redirect.
- A recursive resolver follows root, TLD and authoritative referrals when it lacks cached answers.

## Further reading

- [How browsers work (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work)
- [What happens when… (GitHub)](https://github.com/alex/what-happens-when)
- [HTTP Strict Transport Security (RFC 6797)](https://www.rfc-editor.org/rfc/rfc6797)
- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)
