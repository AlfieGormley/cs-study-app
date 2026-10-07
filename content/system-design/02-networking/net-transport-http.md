---
id: net-transport-http
title: TCP vs UDP, and HTTP/1.1 vs HTTP/2 vs HTTP/3
level: intermediate
minutes: 14
summary: What TCP and UDP guarantee, how each HTTP version uses connections, and why head-of-line blocking drove the move to QUIC.
---

Every HTTP request rides on a transport protocol. The choice of transport, and how HTTP uses it, explains most of the performance differences between HTTP/1.1, HTTP/2 and HTTP/3. This lesson builds up from TCP and UDP to the problem each HTTP version was designed to fix.

## TCP: a reliable, ordered byte stream

TCP gives applications the illusion of a reliable pipe:

- **Connection-oriented:** a three-way handshake (SYN, SYN-ACK, ACK) costs 1 RTT before data flows.
- **Reliable:** lost segments are detected and retransmitted.
- **Ordered:** bytes are delivered to the app in the order they were sent.
- **Flow control:** the receiver advertises how much it can buffer.
- **Congestion control:** the sender probes for available bandwidth.

That last point matters for performance. A new TCP connection starts in **slow start**, with a small congestion window (typically 10 segments ≈ 14 KB, proposed by the Experimental RFC 6928; the actual initial window is implementation/configuration dependent). It roughly doubles each RTT until loss appears, after which the sender cuts its window (by half for classic Reno, by about 30% for CUBIC, the Linux default) and grows more cautiously. So a fresh connection can't use a fast link fully for several round trips:

| RTT # | Window | Cumulative sent |
|---|---|---|
| 1 | 14 KB | 14 KB |
| 2 | 28 KB | 42 KB |
| 3 | 56 KB | 98 KB |
| 4 | 112 KB | 210 KB |

In this idealised round-based model, a 200 KB response needs four transmission rounds, assuming a 14 KB starting window, doubling each round, no loss, immediate ACKs and negligible serialisation. This is not an exact packet-timing model or a bandwidth-independent guarantee. On a 1 Gbps link, 200 KB would take under 2 ms to clock out; at 50 ms RTT, slow start makes it take about 200 ms. **Warm, reused connections are fast; new ones are slow.**

> [!note] TCP Fast Open
> TCP Fast Open (RFC 7413) lets a returning client put data in the SYN, saving the handshake RTT. Deployment depends on both endpoints and middlebox compatibility.

## UDP: just datagrams

UDP is almost nothing on top of IP:

- No handshake, no connection state.
- No retransmission, no ordering, no congestion control.
- Each datagram is independent; it may be lost, duplicated or reordered.

That sounds worse, but it's exactly what some applications want:

| Use | Why UDP |
|---|---|
| DNS | One packet each way; retry is cheap |
| Voice/video calls | A late packet is useless; skip it |
| Games | Latest state matters, not old state |
| QUIC (HTTP/3) | Builds its own reliability in user space |

> [!note] Reliability isn't free
> TCP's ordering guarantee means one lost packet holds back everything after it, even data that arrived fine. That's **head-of-line (HOL) blocking** at the transport layer, and it's the thread that ties this whole lesson together.

## HTTP/1.1: one request at a time per connection

HTTP/1.1 (first specified in 1997, now RFC 9112) made **persistent connections** (`keep-alive`), so one TCP connection can carry many requests in sequence. But on each connection, a response must finish before the next request's response can start:

```
Conn 1: [req A ][resp A    ][req B][resp B]
Conn 2: [req C ][resp C][req D ][resp D   ]
...up to ~6 connections per origin
```

This is **HTTP-level head-of-line blocking**: a slow response blocks everything queued behind it on that connection. *Pipelining* (sending several requests without waiting) was specified but never worked reliably because responses still had to come back in order, and buggy proxies broke it. Browsers turned it off.

Workarounds from the HTTP/1.1 era:

- Browsers open **~6 parallel connections** per origin.
- Sites used **domain sharding** (`img1.`, `img2.`...) to get more connections.
- **Spriting and concatenation** bundled many small files into one.

All of these add handshakes, slow-start penalties or cache-busting problems.

## HTTP/2: multiplexing over one connection

HTTP/2 (2015, now RFC 9113) keeps HTTP's semantics (methods, headers, status codes) but changes the wire format:

- **Binary framing.** Messages are split into frames.
- **Streams.** Each request/response is a stream with an ID; frames from many streams interleave on **one TCP connection**.
- **HPACK header compression.** Repeated headers (cookies, user agents) are sent as small table references.
- **Prioritisation** hints. The original dependency-tree scheme was complex and inconsistently implemented, and RFC 9113 deprecated it in favour of the simpler *Extensible Priorities* scheme (RFC 9218), which HTTP/3 also uses.

```
One TCP connection:
[A1][B1][C1][A2][C2][B2][A3]...
 A, B, C = streams, interleaved
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

On a clean network this rarely matters. On lossy mobile or Wi-Fi links (a few per cent loss), HTTP/2 over one connection can perform *worse* than HTTP/1.1 over six, for two reasons:

- A single loss stalls every stream instead of one-sixth of the traffic.
- The one connection's congestion window shrinks on loss, cutting throughput for everything. With six connections, only one window shrinks at a time.

## HTTP/3 and QUIC: fixing transport HOL blocking

HTTP/3 (RFC 9114, 2022) runs over **QUIC** (RFC 9000, 2021), a transport built on UDP. QUIC re-implements reliability and congestion control, and it tracks **ordering per stream**:

- A loss of application stream data does not create TCP-style ordering dependencies between otherwise independent streams.
- Other streams keep flowing.

```
QUIC packets: [A1][B1][xx][A2][C2]
                  lost ^ (B2)
A1, A2, C2 delivered at once.
Only stream B waits for B2.
```

Two subtleties. Ordering still holds *within* a stream, so a loss does stall that one stream. And congestion control is still per connection, so loss slows the whole connection's sending rate even though it no longer blocks delivery. HTTP/3 also replaced HPACK with **QPACK**, because HPACK assumes headers arrive in order, which would have reintroduced cross-stream blocking. QPACK bounds and manages header dependencies; it does not eliminate every possible cross-stream dependency.

QUIC brings several other wins:

1. **Combined handshake.** Transport and TLS 1.3 are negotiated together in the same packets: 1 RTT for a new connection instead of TCP's 1 plus TLS's 1, and **0-RTT** for resumption, where the request rides in the very first flight (with replay caveats; see the TLS lesson).
2. **Connection migration.** Nonzero *connection IDs* let endpoints identify connections across changes to the IP/port 4-tuple. A phone can keep its connection when changing networks if migration is supported and permitted; path validation and connection-ID handling still matter.
3. **Always encrypted.** Even most transport headers are encrypted, which stops middleboxes from ossifying the protocol.
4. **User-space implementation.** It can evolve with app releases, not OS kernel upgrades.

Costs and caveats:

- **CPU:** UDP processing in user space has historically cost more CPU than kernel TCP (improving with offloads like GSO).
- **Blocked UDP:** some corporate networks block UDP 443. Browsers fall back to HTTP/2 over TCP.
- **Discovery:** browsers usually learn about HTTP/3 from an `Alt-Svc` header on an HTTP/2 response, or from a DNS `HTTPS` record, so the first visit is often HTTP/2.
- **Load balancing:** L4 balancers must route by QUIC connection ID, not 4-tuple, or migration breaks.

## Side by side

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | QUIC/UDP |
| Concurrency | ~6 conns | Streams, 1 conn | Streams, 1 conn |
| HTTP HOL | Yes | No | No |
| TCP HOL | Per conn | Yes, all streams | No |
| New conn setup | 2 RTT | 2 RTT | 1 RTT |
| Resumed, 0-RTT | 1 RTT | 1 RTT | 0 RTT |

Setup figures assume TLS 1.3 and count round trips before the request can be sent. A full TLS 1.2 handshake adds one more RTT over TCP. With TLS 1.3 0-RTT over TCP, the TCP handshake still has to happen first, which is why it's 1 RTT rather than 0.

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

- TCP gives a reliable ordered stream at the cost of a handshake, slow start and transport-level HOL blocking.
- UDP gives raw datagrams; it suits DNS, real-time media and as a base for QUIC.
- HTTP/1.1 suffers HTTP-level HOL blocking, so browsers use ~6 connections per origin.
- HTTP/2 multiplexes streams over one TCP connection, but one lost packet stalls all streams.
- HTTP/3 on QUIC makes loss recovery per-stream, merges the TLS handshake, supports 0-RTT and survives network changes.
- Reuse connections everywhere; new connections are expensive.

## Further reading

- [High Performance Browser Networking: HTTP/1.x](https://hpbn.co/http1x/)
- [High Performance Browser Networking: HTTP/2](https://hpbn.co/http2/)
- [Head-of-line blocking (Wikipedia)](https://en.wikipedia.org/wiki/Head-of-line_blocking)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The road to QUIC (Cloudflare blog)](https://blog.cloudflare.com/the-road-to-quic/)
