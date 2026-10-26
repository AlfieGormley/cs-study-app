---
id: nf-queue-utilisation
sourceLesson: nf-performance
title: Why busy queues become slow
level: basic
minutes: 3
summary: Explain why queues grow near capacity and why high throughput can hide bufferbloat.
---

A link with spare capacity on average can still build queues. Bursts temporarily arrive faster than the link can serve them; spare capacity between bursts is what lets that backlog drain.

## Why delay grows near full load

**Traffic intensity**, often called utilisation in the simple model, compares the average incoming work with the link's service capacity. Traffic asking for 90 Mbit/s on a 100 Mbit/s link represents 90% load.

With sustained offered work above service capacity, an ideal infinite queue has no stable finite backlog. A real finite buffer eventually fills and drops or rejects excess traffic. Below capacity, the average load alone still does not determine delay: burstiness, packet sizes, scheduling and competing traffic matter.

Near full load there is little spare service capacity to drain bursts. A small rise in average traffic can therefore produce a much larger rise in waiting time.

## An illustrative queue model

The **M/M/1 queue** makes this effect precise under particular assumptions: Poisson arrivals (independent random arrivals at a steady average rate), independent exponentially distributed service times, one server, infinite waiting space and offered load below capacity.

In that model the mean queueing wait is one mean packet-service time at 50% load, four at 80%, nine at 90% and 99 at 99%. Delay grows much faster than the offered load near capacity. The mean is finite below full load under these assumptions.

```formula reference
W_q = (ρ / (1 − ρ)) T_s
where
W_q: mean time spent waiting before transmission starts, in seconds
ρ: traffic intensity, the average arriving work divided by service capacity; a unitless fraction between zero and one, strictly below one for this model
T_s: mean service time, the average transmission time of a packet, in seconds
In words: in this particular random-arrival, random-service queue model, waiting grows sharply as offered work approaches service capacity because less spare capacity remains to clear bursts.
```

Fixed-size packets have fixed transmission times rather than exponential ones. Real arrival patterns and schedulers also differ. This model is neither a universal prediction nor a bound for routers.

## Bufferbloat

Very large buffers can keep throughput high while allowing hundreds of milliseconds of persistent queueing. This **bufferbloat** hurts calls and games during a bulk upload. Active queue management, including CoDel and FQ-CoDel, addresses persistent queues; FQ-CoDel also separates traffic into flow queues.

Measure latency under load as well as throughput. An impressive bulk-transfer rate does not establish that interactive traffic is responsive.

## Key takeaways
- Average spare capacity does not prevent transient queues.
- Near capacity, waiting can grow sharply; exact values depend on the queue model.
- Throughput and latency under load reveal different aspects of a link.

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
