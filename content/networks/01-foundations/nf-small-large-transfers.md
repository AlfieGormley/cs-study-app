---
id: nf-small-large-transfers
sourceLesson: nf-performance
title: Optimise small and large transfers
level: basic
minutes: 3
summary: Choose between reducing round trips and increasing sustained goodput for different workloads.
---

Small exchanges are often dominated by round trips; sufficiently large transfers can be dominated by sustained goodput. Server work, congestion and host performance can dominate either, so diagnose the workload first.

## Compare two workloads

Assume a hypothetical path with a 100 Mbit/s payload rate and a 40 ms round-trip time. Ignore DNS, server work, loss, slow start and additional overhead. Use fresh TCP plus a full TLS 1.3 handshake with no resumption, early data or retry.

- A **20 KB API response** waits through TCP setup, TLS setup and the request/response round trip. Those three round trips cost about 120 ms, while response transmission takes only about 1.6 ms.
- A **1 GB download** needs about 80 seconds of payload transmission. The same setup cost is small beside that.

Sending the small response at a higher payload rate removes little of its delay. Reducing RTT or avoiding repeated setup addresses the larger cost in this model. For the large download, improving sustained goodput can make a substantial difference.

## Avoid unnecessary round trips

Connection reuse avoids repeating setup for every request. A server location with a lower measured RTT shortens each required round trip.

A conventional full TLS 1.2 handshake without resumption or False Start takes two TLS round trips before the request. With one TCP setup round trip and one request/response round trip, that simplified fresh-connection model needs four RTTs. TLS 1.3 reduces the TLS part to one unless retry adds another exchange.

TLS/QUIC early data (**0-RTT**) requires prior connection state and replay-safe application handling. It is not available for every first connection, and replay risk matters when a request changes state.

These examples isolate mechanisms. Real workloads can involve parallel requests, caching, congestion, server computation and connection limits. There is no universal bandwidth threshold beyond which pages stop benefiting.

## Key takeaways
- Small exchanges can benefit most from fewer or shorter round trips.
- Large transfers can benefit most from higher sustained goodput.
- Reuse and handshake choices depend on protocol and application constraints.

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
