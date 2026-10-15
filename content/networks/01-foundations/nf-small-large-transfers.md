---
id: nf-small-large-transfers
sourceLesson: nf-performance
title: Optimise small and large transfers
level: basic
minutes: 3
summary: Compare round-trip setup costs with sustained payload transmission for two workloads.
---

## Which one matters?

Small transfers are often sensitive to round trips, while sufficiently large transfers can be limited by sustained goodput. Server work, congestion and host performance can dominate either.

> [!example] A 20 KB API response versus a 1 GB download
> Hypothetical path: 100 Mbit/s payload rate, 40 ms RTT. Ignore DNS, server work, loss, slow start and additional overhead; use TCP plus a full TLS 1.3 handshake with no resumption, early data or retry.
> - 20 KB: in this model TCP setup and TLS setup consume two RTTs before the request, then one more RTT for the request and response: about 120 ms before adding 1.6 ms of response transmission. Round trips account for about 99% of that simplified total.
> - 1 GB: transmission alone takes 80 s. The handshakes are noise.

```formula
t ≈ 3 × RTT + L / R
t ≈ 3 × 40 ms + 160,000 bit / (10⁸ bit/s)
t ≈ 120 ms + 1.6 ms ≈ 121.6 ms
L / R = 8 × 10⁹ bit / (10⁸ bit/s) = 80 s
where
t: the time until the whole 20 KB response has arrived
RTT: the round-trip time, 40 ms; three are spent on TCP setup, TLS setup and the request itself
L: the response size in bits: 20 KB (20,000 bytes) is 160,000 bits; 1 GB (10⁹ bytes) is 8 × 10⁹ bits
R: the payload rate, 100 Mbit/s = 10⁸ bits per second
ms: milliseconds, thousandths of a second
bit: one binary digit; bit/s is bits per second
s: seconds
≈: approximately equal to
In words: for the small response, 120 of the 121.6 ms are round trips, so shorter RTT or fewer round trips dominate improvement in this model; for the 1 GB download, 80 s of transmission dwarfs the 120 ms of handshakes, so a higher sustained payload rate dominates improvement in this model.
```

For comparison, a conventional full TLS 1.2 handshake without resumption or False Start takes two TLS round trips before the client sends its request. With one TCP setup round trip and one request/response round trip, a fresh connection uses four round trips in the same simplified timing model. TLS 1.3 reduces that TLS portion to one round trip unless an additional retry is needed.

Connection reuse and closer servers can cut round-trip costs. TLS/QUIC handshake choices also matter: 0-RTT requires prior connection state and appropriate replay-safe application handling; it is not available for every first connection. Which improvement helps most requires a workload and path measurement. A universal bandwidth threshold beyond which pages stop benefiting is omitted because no such general threshold is established here.

## Key takeaways
- Small exchanges can be dominated by handshakes and round trips.
- Large transfers can be dominated by sustained goodput; the model explicitly omits other limits.

## Further reading
- [Primer on Latency and Bandwidth — High Performance Browser Networking](https://hpbn.co/primer-on-latency-and-bandwidth/)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)
- [Network delay — Wikipedia](https://en.wikipedia.org/wiki/Network_delay)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Bufferbloat — Wikipedia](https://en.wikipedia.org/wiki/Bufferbloat)
- [Goodput — Wikipedia](https://en.wikipedia.org/wiki/Goodput)

- [RFC 8290: FQ-CoDel](https://www.rfc-editor.org/rfc/rfc8290)
- [RFC 8446: TLS 1.3 and early-data replay considerations](https://www.rfc-editor.org/rfc/rfc8446)
- [MIT queueing lecture: M/M/1 assumptions](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-spring-2006/1a538356bf7a1f78408de525dd2d1032_lec21.pdf)
