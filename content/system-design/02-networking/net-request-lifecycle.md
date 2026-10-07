---
id: net-request-lifecycle
title: What happens when you type a URL
level: basic
minutes: 11
summary: The full journey of a web request, from parsing the URL through DNS, TCP, TLS and HTTP to rendering, and where the time goes.
---

"What happens when you type `https://shop.example.com/cart` into a browser and press Enter?" is the classic opening question in networking interviews. It's popular because a good answer touches almost every layer a system designer works with: naming, transport, security, load balancing, caching and the application itself.

This lesson walks the whole path once, end to end. Each later lesson in this module zooms into one hop.

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

Roughly, the steps are:

1. **Parse the URL** and check local caches.
2. **Resolve the name** to an IP address with DNS.
3. **Open a transport connection** (TCP, or QUIC for HTTP/3).
4. **Negotiate encryption** with TLS.
5. **Send the HTTP request** and receive the response, possibly via a CDN, load balancer and reverse proxy.
6. **Render** the page, which triggers dozens more requests.

## Step 1: parse the URL and check caches

The browser splits the URL into parts:

| Part | Value |
|---|---|
| Scheme | `https` (so port 443) |
| Host | `shop.example.com` |
| Path | `/cart` |
| Query/fragment | none |

Before touching the network, it checks a few things:

- **HSTS list.** If the site has sent a `Strict-Transport-Security` header before (or is on the browser's preload list), the browser upgrades `http://` to `https://` itself, skipping an insecure redirect.
- **HTTP cache.** If a fresh copy of the resource is stored, the browser can use it with zero network traffic. (Cache headers are covered in the caching module.)
- **Existing connections.** If there's already an open connection to this origin, it can be reused, skipping steps 2 to 4 entirely.

That last point matters enormously. The first request to a site is expensive; later ones are cheap because connections are kept alive.

## Step 2: DNS resolution

Computers route IP packets by address. A browser may use the operating system resolver or its own resolver, including DNS over HTTPS. Cached answers may avoid a lookup; otherwise a **recursive resolver** resolves the name.

If the recursive resolver has no cached answer, it walks the hierarchy:

1. Ask a **root server**: "who handles `.com`?"
2. Ask the **`.com` TLD server**: "who handles `example.com`?"
3. Ask `example.com`'s **authoritative server**: "what is `shop.example.com`?"

The answer comes back with a **TTL**, telling every cache how long it may keep it. Latency depends on cache state, resolver placement and the authoritative path.

> [!note] Measurement gap
> No measured traces accompany this lesson. The timings below are illustrative assumptions, not measurements or universal latency bounds.

> [!note] DNS is also a routing tool
> The authoritative server doesn't have to give everyone the same answer. Large sites return different IPs depending on where you are, which is the basis of GeoDNS and CDN steering. More on that in the DNS and global traffic lessons.

## Step 3: the TCP handshake

With an IP address, the browser opens a TCP connection to port 443:

```
Client                     Server
  | ---- SYN -------------->  |
  | <--- SYN-ACK -----------  |
  | ---- ACK -------------->  |
  |    (connection open)      |
```

Without TCP Fast Open, the client waits **one round trip (RTT)** before sending application data. Use 80 ms as an illustrative London–Virginia RTT, not a guaranteed route measurement.

Most of that is physics. Light in fibre travels at roughly 200,000 km/s (about two-thirds of its speed in a vacuum), and London to Virginia is roughly 5,900 km in a straight line. That alone sets a floor of about 60 ms for the round trip; real cables don't follow the great-circle route, and routers add a little queueing. For this assumed fibre path, software cannot beat that propagation floor, which is why putting servers (or CDN edges) close to users matters so much.

## Step 4: the TLS handshake

For HTTPS, client and server now agree on encryption keys and the server proves its identity with a certificate. TLS 1.3 needs **one more round trip**; a full TLS 1.2 handshake needs two. (The TLS lesson covers how resumption and 0-RTT shrink this further.)

The browser checks that the certificate:

- covers the hostname (`shop.example.com` or `*.example.com`),
- hasn't expired, and
- chains up to a certificate authority it trusts.

The client also sends the hostname in the **SNI** extension, so a server hosting thousands of sites knows which certificate to present. SNI has traditionally been sent in the clear, so anyone on the path can see which site you're visiting even though they can't read the traffic. **Encrypted Client Hello (ECH)** is a newer extension that hides it, and support is spreading through browsers and CDNs.

## Step 5: the HTTP request and response

Only now does the browser send:

```
GET /cart HTTP/1.1
Host: shop.example.com
Cookie: session=abc123
Accept-Encoding: gzip, br
```

That's the HTTP/1.1 text format. HTTP/2 and HTTP/3 carry the same method, path and headers in binary frames (the `Host` header becomes the `:authority` pseudo-header), but the meaning is identical.

On the server side, the request might pass through several hops before reaching your code:

| Hop | What it does |
|---|---|
| CDN edge | Serves cached content, absorbs attacks |
| Load balancer | Picks a healthy backend |
| Reverse proxy | TLS, compression, routing |
| App server | Runs your code |
| Cache / DB | Supplies the data |

The app builds a response: a status line (`200 OK`), headers (`Content-Type`, `Cache-Control`, `Set-Cookie`) and a body, often compressed with gzip or Brotli.

## Step 6: rendering, and the requests it triggers

The browser parses the HTML and discovers more resources: CSS, JavaScript, images, fonts and API calls. A page may make many additional requests; the count depends on the page. Many go to the same origin and reuse the connection; others go to new origins (a CDN, an analytics domain), each paying its own DNS + TCP + TLS cost.

This is why front-end engineers use hints like `<link rel="preconnect">` and why consolidating origins can help.

## Where the time goes

Let's add up a cold first request from London to a single server in Virginia, with RTT = 80 ms:

| Step | Cost |
|---|---|
| DNS (uncached) | ~100 ms |
| TCP handshake | 80 ms (1 RTT) |
| TLS 1.3 | 80 ms (1 RTT) |
| HTTP request/response | 80 ms + server time |
| **Total before first byte** | **~340 ms + server** |

Only the last of those round trips actually carries the page; the rest are setup. (The DNS round trips go to resolvers, not to Virginia, which is why that row isn't exactly one RTT.) If the server used TLS 1.2, add another 80 ms.

Now put a CDN edge in London, with an RTT of 10 ms:

| Step | Cost |
|---|---|
| DNS (cached at resolver) | ~5 ms |
| TCP | 10 ms |
| TLS 1.3 | 10 ms |
| HTTP (cache hit) | 10 ms |
| **Total** | **~35 ms** |

In these illustrative assumptions the total is about ten times lower, combining a nearer endpoint, a faster DNS lookup and a cache hit. Note the hidden assumption: the edge had the response cached. On a miss, the edge must still fetch from Virginia, adding one 80 ms trip over a connection it keeps warm, so the total is closer to 115 ms. That's still three times better than going direct.

Most of this module is about techniques that shrink, skip or move these round trips.

> [!tip] Interview framing
> Don't recite every step at equal depth. Walk the path briefly, then say "the expensive parts are the round trips: DNS, TCP and TLS. Here's how we cut them: caching, connection reuse, TLS 1.3/QUIC and edge termination." That shows you know what matters.

## Failure modes along the path

Every hop can fail, and each failure looks different to the user:

- **DNS failure:** "server not found" (`NXDOMAIN` or timeout). The 2016 Dyn attack took down Twitter, GitHub and others this way.
- **TCP failure:** "connection refused" (the host answered with a reset because nothing is listening on that port) or a timeout (a firewall silently dropping packets, or a dead host). Refused is fast; a timeout can hang for many seconds, which is why client connect timeouts matter.
- **TLS failure:** certificate warnings, often from an expired certificate.
- **HTTP failure:** a `502 Bad Gateway` reports an invalid upstream response; a `504 Gateway Timeout` reports an upstream timeout. Inspect backend health, the network and proxy configuration; the status alone does not prove which component is faulty.

Knowing which layer produced an error is the first step in debugging production incidents.

## Key takeaways

- A request goes: URL parse → caches → DNS → TCP → TLS → HTTP → server stack → render.
- The fixed cost of a new connection is several round trips, and RTT is bounded by distance and the speed of light.
- Connection reuse, DNS caching, TLS 1.3 and serving from the edge each remove or shorten round trips.
- DNS answers can differ per client, which makes DNS a traffic-routing tool, not just a phone book.
- Error type (DNS, connection refused, TLS, 502/504) tells you which hop failed.

## Further reading

- [What happens when... (GitHub)](https://github.com/alex/what-happens-when)
- [How browsers work (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work)
- [An overview of HTTP (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [High Performance Browser Networking: Building blocks of TCP](https://hpbn.co/building-blocks-of-tcp/)
