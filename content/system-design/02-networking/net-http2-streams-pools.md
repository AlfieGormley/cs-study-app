---
id: net-http2-streams-pools
title: "HTTP/2 streams and backend pools"
level: intermediate
minutes: 3
summary: "Explain multiplexing, shared TCP loss and why persistent gRPC connections can skew L4 balancing."
sourceLesson: net-transport-http
---
HTTP/2 solves HTTP/1.1’s response-order bottleneck by separating logical streams. It still shares TCP’s byte ordering and congestion window, and reused backend connections require appropriate balancing.

## HTTP/2: multiplexing over one connection

HTTP/2 (2015, now RFC 9113) keeps HTTP's semantics (methods, headers, status codes) but changes the wire format:

- **Binary framing.** Messages are split into frames.
- **Streams.** Each request/response is a stream with an ID; frames from many streams interleave on **one TCP connection**.
- **HPACK header compression.** Repeated headers (cookies, user agents) are sent as small table references.
- **Prioritisation** hints. The original dependency-tree scheme was complex and inconsistently implemented, and RFC 9113 deprecated it in favour of the simpler *Extensible Priorities* scheme (RFC 9218), which HTTP/3 also uses.

```
One TCP connection:
[A1][B1][C1][A2][C2][B2][A3]...
 A, B, C: streams, interleaved
```

A slow response no longer blocks fast ones, so the HTTP-level HOL problem is solved. The 6-connection limit, sharding and spriting become unnecessary, and often harmful (sharding defeats the single-connection design).

**Server push** was also part of HTTP/2, but it was hard to use well and browsers (Chrome in 2022) removed support. `103 Early Hints` is the replacement.

### The problem HTTP/2 can't fix

All those streams share one TCP byte stream. If one packet is lost, TCP holds back **every byte after it** until the retransmission arrives, even bytes belonging to unrelated streams:

```
Packets: [A1][B1][xx][A2][C2]
               lost ^
TCP delivers A1, B1, then WAITS.
A2 and C2 arrived but are stuck.
```

> [!analogy] Real-world analogy: One shared parcel conveyor
> Several shoppers' items travel to the packing bench on one conveyor belt, in the order they were scanned. If one item falls off and has to be fetched again, the belt stops, so every shopper waits, even those whose items are already sitting on the belt.
>
> **How it maps:** the shoppers are HTTP/2 streams and the single belt is the one TCP connection, which hands bytes to the application strictly in order. The fallen item is a lost packet, and stopping the belt until it is replaced is TCP head-of-line blocking across unrelated streams.
>
> **Where it stops:** TCP does not physically halt the network; later packets still arrive and wait in the receiver's buffer, and the sender also slows down because of congestion control. HTTP/2 does solve the separate problem of one slow *response* holding up others.

On a clean network this rarely matters. On lossy mobile or Wi-Fi links (a few per cent loss), HTTP/2 over one connection can perform *worse* than HTTP/1.1 over six, for two reasons:

- A single loss stalls every stream instead of one-sixth of the traffic.
- The one connection's congestion window shrinks on loss, cutting throughput for everything. With six connections, only one window shrinks at a time.

## Connection reuse in back-end systems

These lessons apply between your own services too:

- **Pool connections.** Opening a new TCP+TLS connection per request to a database or downstream API adds 2+ RTTs and slow start every time. Keep-alive pools are essential.
- **HTTP/2 between services** (gRPC uses it) gives multiplexing over few connections. But a few long-lived connections can **unbalance an L4 load balancer**, which balances connections, not requests. Use an L7 balancer or client-side balancing.
- **Set a max connection age** so pools pick up DNS changes and spread across new backends.

> [!example] A real migration
> Google’s 2017 QUIC deployment paper reports benefits for Search and YouTube in its measured environment. That historical Google QUIC implementation predates standard IETF QUIC; its results are not a guaranteed HTTP/3 speed-up.
>
> Evidence gap: no reproducible benchmark for this app or your network is provided. Exact performance gains and CPU comparisons are omitted; measure representative workloads.

## Key takeaways

- HTTP/2 interleaves request streams and compresses headers on one TCP connection.
- TCP still holds back later bytes after a loss, so unrelated HTTP/2 streams can stall together.
- Long-lived HTTP/2 connections can pin work behind L4 balancing; L7 or client-side balancing distributes requests.

## Further reading

- [HTTP/2 (RFC 9113)](https://www.rfc-editor.org/rfc/rfc9113)
- [HTTP/2 (High Performance Browser Networking)](https://hpbn.co/http2/)
- [Supported load balancers (Envoy)](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers)
