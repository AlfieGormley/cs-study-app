---
id: net-connection-handshakes
title: "TCP, TLS and the first HTTP request"
level: basic
minutes: 4
summary: "Understand connection setup, the distance floor and what HTTPS hides from an observer."
sourceLesson: net-request-lifecycle
---
After resolving the name, a browser needs a transport connection and, for HTTPS, a protected channel. This unit follows a new HTTPS-over-TCP connection; QUIC combines transport and TLS setup differently.

## The TCP handshake

With an IP address, the browser opens a TCP connection to port 443:

```
Client                     Server
  | ---- SYN -------------->  |
  | <--- SYN-ACK -----------  |
  | ---- ACK -------------->  |
  |    (connection open)      |
```

Without TCP Fast Open, the client waits **one round trip (RTT)** before sending application data. Use 80 ms as an illustrative London–Virginia RTT, not a guaranteed route measurement.

Most of that is physics. Light in optical fibre travels at roughly 200,000 km/s, about two-thirds of its speed in a vacuum, and a round trip covers the distance twice. So every 1,000 km of fibre path adds at least about 10 ms of round-trip time. London to Virginia is roughly 5,900 km in a straight line, which sets a **propagation floor** of about 59 ms before any equipment does anything.

```formula reference
RTT_min = 2d / v
where
RTT_min: the propagation floor: the shortest round-trip time (RTT) that distance alone allows, in milliseconds (ms)
d: the one-way length of the path between client and server, in kilometres (km)
v: the signal speed in the cable, in kilometres per millisecond (km/ms); about 200 km/ms (200,000 km per second) for light in fibre
In words: a round trip crosses the path twice at the speed of light in fibre, so each 1,000 km of path adds at least about 10 ms of round-trip time.
```

The result is a floor, not a prediction. Real cables don't follow the great-circle route (the shortest route over the Earth's surface), and routers add queueing, so measured RTTs are higher. Faster servers or a newer protocol can cut the *number* of round trips, but nothing in software makes each trip shorter than this. Only moving the endpoint (a nearer region or CDN edge) does that.

## The TLS handshake

For HTTPS, client and server now agree on encryption keys and the server proves its identity with a certificate. TLS 1.3 needs **one more round trip**; a full TLS 1.2 handshake needs two. (The TLS lesson covers how resumption and 0-RTT shrink this further.)

The browser checks that the certificate:

- covers the hostname (`shop.example.com` or `*.example.com`),
- hasn't expired, and
- chains up to a certificate authority it trusts.

The client also sends the hostname in the **SNI** extension, so a server hosting thousands of sites knows which certificate to present. SNI has traditionally been sent in the clear, so anyone on the path can see which site you're visiting even though they can't read the traffic. **Encrypted Client Hello (ECH)** is a newer extension that hides it, and support is spreading through browsers and CDNs.

## The HTTP request and response

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

The HTTP block above is an illustrative request message, not an executable program or a complete packet capture. On a network without a VPN or proxy, a passive observer can see destination IP addresses and traffic timing. With plain DNS and no ECH, it can also learn the queried name and SNI hostname. TLS encrypts the HTTP path, cookies and body.

## Key takeaways

- A new TCP connection normally pays one round trip before TLS begins.
- Distance sets a propagation floor; software can reduce trip counts but cannot remove the physical path.
- HTTPS protects the path, cookies and response body; plain DNS and unencrypted SNI can still reveal the hostname.

## Further reading

- [Building blocks of TCP (High Performance Browser Networking)](https://hpbn.co/building-blocks-of-tcp/)
- [TLS 1.3 (RFC 8446)](https://www.rfc-editor.org/rfc/rfc8446)
