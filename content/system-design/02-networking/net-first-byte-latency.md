---
id: net-first-byte-latency
title: "Count the trips before the first byte"
level: basic
minutes: 4
summary: "Calculate cold-request latency and explain how a nearby edge changes hits and misses."
sourceLesson: net-request-lifecycle
---
The handshake path gives us a useful first-byte budget. The following timings are hypothetical inputs, with no loss, retry or additional processing unless a row explicitly includes it.

## Where the time goes

Let's add up a cold first request from London to a single server in Virginia, with a round-trip time of 80 ms:

| Step | Cost |
|---|---|
| DNS (uncached) | ~100 ms |
| TCP handshake | 80 ms (1 RTT) |
| TLS 1.3 | 80 ms (1 RTT) |
| HTTP request/response | 80 ms + server time |
| **Total before first byte** | **~340 ms + server** |

The table follows a simple model: one DNS lookup, then a fixed number of round trips to the server, then the server's own work. Adding it up gives the **time to first byte**:

```formula
T = T_DNS + n × RTT + T_server
T = 100 ms + 3 × 80 ms + T_server
T = 340 ms + T_server
where
T: the time to first byte: from pressing Enter until the first byte of the response arrives, in milliseconds (ms)
T_DNS: the time to resolve the name with DNS; about 100 ms here, because nothing is cached
n: the number of round trips to the server before the first byte arrives: 1 for the TCP handshake, 1 for TLS 1.3 and 1 for the request and response, so 3
RTT: the round-trip time to the server, here 80 ms from London to Virginia
T_server: the time the server spends building the response, in ms
ms: millisecond, one thousandth of a second
In words: a cold first request pays for the DNS lookup and three full round trips before the server's own work even counts.
```

Only the last of those round trips actually carries the page; the rest are setup. (The DNS round trips go to resolvers, not to Virginia, which is why that row isn't exactly one RTT.) If the server used TLS 1.2, add another 80 ms.

Now put a CDN edge in London, with an RTT of 10 ms:

| Step | Cost |
|---|---|
| DNS (cached at resolver) | ~5 ms |
| TCP | 10 ms |
| TLS 1.3 | 10 ms |
| HTTP (cache hit) | 10 ms |
| **Total** | **~35 ms** |

The same model, with the shorter round trip to the edge and the edge's own trip to the origin on a miss:

```formula
T_hit = T_DNS + n × RTT_edge
T_hit = 5 ms + 3 × 10 ms = 35 ms
T_miss = T_hit + RTT_origin
T_miss = 35 ms + 80 ms = 115 ms
where
T_hit: the time to first byte when the London edge already has the response cached (a cache hit), in milliseconds (ms)
T_DNS: the DNS lookup time, about 5 ms when the recursive resolver already has the answer cached
n: the round trips to the edge before the first byte: TCP, TLS 1.3 and the request itself, so 3
RTT_edge: the round-trip time to the nearby edge, here 10 ms
T_miss: the time to first byte when the edge doesn't have the response (a cache miss) and must fetch it from the origin
RTT_origin: the round-trip time from the edge to the origin in Virginia, 80 ms, over a connection the edge already holds open
ms: millisecond
In words: a nearby edge makes every handshake cheap, and a miss adds just one long trip because the edge's connection to the origin is already open.
```

In these illustrative assumptions the total is about ten times lower (340 ms versus 35 ms, ignoring server time), combining a nearer endpoint, a faster DNS lookup and a cache hit. Note the hidden assumption: the edge had the response cached. On a miss, the edge must still fetch from Virginia, adding one 80 ms trip over a connection it keeps warm, so the total is closer to 115 ms. That's still about three times better than going direct.

Most of this module is about techniques that shrink, skip or move these round trips.

> [!tip] Interview framing
> Don't recite every step at equal depth. Walk the path briefly, then say "the expensive parts are the round trips: DNS, TCP and TLS. Here's how we cut them: caching, connection reuse, TLS 1.3/QUIC and edge termination." That shows you know what matters.

## Key takeaways

- A cold TCP/TLS 1.3 request pays DNS plus three server round trips and server work in the simplified model.
- A nearby CDN makes connection setup cheap; a miss still needs an origin trip.
- Reuse, caching and endpoint placement solve different parts of the latency budget.

## Further reading

- [Primer on latency and bandwidth (High Performance Browser Networking)](https://hpbn.co/primer-on-latency-and-bandwidth/)
- [An overview of HTTP (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
