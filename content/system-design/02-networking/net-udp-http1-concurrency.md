---
id: net-udp-http1-concurrency
title: "Datagrams and HTTP/1.1 concurrency"
level: intermediate
minutes: 3
summary: "Choose datagrams for disposable updates and explain HTTP/1.1’s parallel-connection workarounds."
sourceLesson: net-transport-http
---
Transport ordering is useful when every byte matters, but can hurt when a newer update replaces an old one. HTTP/1.1 has a separate concurrency problem: responses on each connection remain ordered.

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

## Key takeaways

- UDP supplies independent datagrams without TCP’s reliability or ordering.
- For frequent position updates, a newer state can be more useful than recovering a stale packet.
- HTTP/1.1 reuses connections but ordered responses limit concurrency on each connection.

## Further reading

- [User Datagram Protocol (RFC 768)](https://www.rfc-editor.org/rfc/rfc768)
- [HTTP/1.1 (RFC 9112)](https://www.rfc-editor.org/rfc/rfc9112)
- [HTTP/1.x (High Performance Browser Networking)](https://hpbn.co/http1x/)
