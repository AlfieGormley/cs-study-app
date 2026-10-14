---
id: net-tls-resumption-replay
title: "Resumption, setup cost and replay"
level: intermediate
minutes: 4
summary: "Count TLS setup trips, support tickets across a fleet and decide which requests tolerate early data."
sourceLesson: net-tls
---
Once certificate trust and termination are understood, count the setup rounds and choose what to reuse. All timings below exclude DNS and assume no handshake retry, loss or extra processing.

## The latency cost, and how to reduce it

In the simplified model with no DNS delay, TCP Fast Open, handshake retry, loss or processing delay, a new HTTPS connection over TCP costs **one TCP round trip and one TLS 1.3 round trip** before the request goes out. Setup time is a count of round trips multiplied by the round-trip time:

```formula
T_setup = (n_TCP + n_TLS) × RTT
T_setup = (1 + 1) × 100 ms = 200 ms
T_edge = (1 + 1) × 10 ms = 20 ms
where
T_setup: the time spent on handshakes before the first request byte can leave the client, in milliseconds (ms)
n_TCP: the round trips for the TCP handshake: 1 (QUIC folds it into its own handshake)
n_TLS: the round trips for the TLS handshake: 1 for TLS 1.3, 2 for a full TLS 1.2 handshake, 0 with 0-RTT early data
RTT: the round-trip time between the client and whichever server terminates TLS, in ms
T_edge: the same setup when TLS terminates at a CDN edge only 10 ms away
ms: millisecond, one thousandth of a second
In words: you can cut handshake cost in two ways, by doing fewer round trips or by making each round trip shorter.
```

At 100 ms RTT, that's 200 ms of pure setup. Ways to cut it:

1. **Use TLS 1.3.** Saves a full RTT over TLS 1.2.
2. **Session resumption.** The server hands the client a *session ticket*; next time, the handshake skips certificate exchange and verification (less CPU and fewer bytes).
3. **0-RTT (early data).** With a ticket, TLS 1.3 lets the client send its request *in the first flight*. Setup cost on resumption drops to just the TCP handshake (or nothing extra with QUIC).
4. **Terminate close to the user.** Handshakes at a CDN edge 10 ms away cost 20 ms, not 200 ms. The edge keeps warm, long-lived connections to the origin.
5. **Reuse connections.** The best handshake is the one you don't do.
6. **Keep certificate chains small.** For comparable certificate fields, ECDSA P-256 uses smaller keys and signatures than RSA-2048; actual certificate size and signing time depend on the chain and implementation. Oversized chains can overflow TCP's initial window and add an RTT.

Putting the round trips together, before the first request byte can leave the client:

| Setup | New | Resumed |
|---|---|---|
| TCP + TLS 1.2 | 3 RTT | 2 RTT |
| TCP + TLS 1.3 | 2 RTT | 2 (1 with 0-RTT) |
| QUIC | 1 RTT | 1 (0 with 0-RTT) |

Note that plain TLS 1.3 resumption *without* early data saves CPU and bytes, not round trips: it still takes a full round trip before the request goes out.

> [!warning] 0-RTT replay
> Early data has no protection against replay across connections: an attacker who captures the first flight can resend it. Servers must assess **replay safety**, not merely idempotency. RFC 8470 permits clients, absent other information, to send only safe HTTP methods in early data. Even a nominal `GET` requires care if its implementation has sensitive side effects. When Cloudflare launched 0-RTT in 2017, it answered only `GET` requests without query parameters in early data, and tagged them with a header so the origin could spot replays. RFC 8470 standardises this pattern: a proxy adds `Early-Data: 1`, and an origin that won't risk it replies `425 Too Early`, making the client retry after the handshake completes.

### CPU cost

TLS CPU cost includes bulk encryption, handshake signatures and key exchange. Their relative cost depends on hardware, cryptographic library, algorithms, record sizes and connection reuse. Benchmark representative traffic before sizing load balancers; resumption and connection reuse can reduce handshake work.

### Tickets across a fleet

In an encrypted stateless-ticket design, the receiving server needs a compatible ticket-encryption key to recover the resumable state. If each terminating node has a different key, a returning client routed to another node may need a full handshake. A securely distributed, rotated key set can support resumption across servers; other designs use opaque ticket identifiers and shared server-side state. NGINX documents explicit ticket keys for configurations that need the same key on several servers. Protect the keys: compromise can expose early data or PSK-only traffic, even though it does not automatically decrypt past traffic protected by fresh (EC)DHE.

## Key takeaways

- TLS 1.3 resumption without early data saves bytes and work but still requires a TLS round trip.
- Early data can save that trip only when the application can tolerate replay safely.
- Reused connections and nearby termination cut setup cost; ticket designs must work across the terminating fleet.

## Further reading

- [TLS 1.3 (RFC 8446)](https://www.rfc-editor.org/rfc/rfc8446)
- [Using early data in HTTP (RFC 8470)](https://www.rfc-editor.org/rfc/rfc8470)
- [Session ticket keys (NGINX)](https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_session_ticket_key)
