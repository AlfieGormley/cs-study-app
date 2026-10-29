---
id: net-first-byte-latency
title: "Count the trips before the first byte"
level: basic
minutes: 4
summary: "See why setup round trips dominate a small first request, and what a nearby edge does and does not remove."
sourceLesson: net-request-lifecycle
---
For a small page, the server's work and the bytes on the wire are usually not where the time goes. The time goes on **round trips**: each step that must wait for a reply before the next can start.

## Where the time goes

A cold first request over HTTPS on TCP with TLS 1.3 waits for a DNS answer, then for three round trips to the server: the TCP handshake, the TLS handshake, and finally the request and its response. Only the last of those carries the page; the rest are setup.

```formula essential
T ≈ T_DNS + n × RTT + T_server
where
T: the time to first byte: from starting the request until the first byte of the response arrives, in milliseconds (ms)
T_DNS: the time to resolve the name; near zero when cached, often tens of ms or more when not
n: the number of sequential round trips to the server before the first byte: 3 on a new TCP + TLS 1.3 connection (TCP, TLS, request), 4 with a full TLS 1.2 handshake, 1 on a reused connection
RTT: the round-trip time to whichever server terminates the connection, in ms
T_server: the time the server spends producing the response, in ms
≈: approximately equal to (loss, retries and queueing are ignored)
In words: a small request's wait is mostly the number of round trips times the length of each trip, plus DNS and the server's own work.
```

Two consequences follow directly:

- Bandwidth barely matters here. A faster link shortens the time to push bytes onto the wire, which for a small response is already a tiny fraction of one round trip. It does not shorten any round trip.
- There are only two levers. Make fewer trips (reuse connections, TLS 1.3, QUIC, caching) or make each trip shorter (put the endpoint nearer the user).

## What a nearby edge changes

Take an illustrative London user and a single origin in Virginia with an 80 ms RTT, compared with a CDN edge in London 10 ms away that already keeps a warm connection open to the origin. The direct path also pays an uncached DNS lookup (about 100 ms), while the edge path uses an answer already cached at the resolver (about 5 ms). These are assumed figures, not measurements.

| Path | Round trips that cross the Atlantic | Rough first byte |
|---|---|---|
| Direct, cold DNS | all three | ~340 ms + server |
| Edge, cache hit | none | ~35 ms |
| Edge, cache miss | only the request | ~115 ms + server |

On a **hit**, every trip is short, so the user sees roughly a tenth of the direct time (part of that gap is the assumed DNS difference; with equal DNS times the hit is still about seven times faster). On a **miss**, the handshakes still happen on the short hop, and the edge forwards just the request over its already-open origin connection: one long trip instead of three. The edge cannot remove that last trip, because the data lives in Virginia.

Most of this module is about techniques that shrink, skip or move these round trips.

> [!tip] Interview framing
> Don't recite every step at equal depth. Walk the path briefly, then say "the expensive parts are the round trips: DNS, TCP and TLS. Here's how we cut them: caching, connection reuse, TLS 1.3/QUIC and edge termination." That shows you know what matters.

## Key takeaways

- A small first request is dominated by the number of sequential round trips and the length of each, not by bandwidth.
- A nearby edge makes setup trips short; a cache miss still needs one trip to wherever the data lives.
- Reuse, caching and endpoint placement attack different parts of the same latency budget.

## Further reading

- [Primer on latency and bandwidth (High Performance Browser Networking)](https://hpbn.co/primer-on-latency-and-bandwidth/)
- [An overview of HTTP (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
