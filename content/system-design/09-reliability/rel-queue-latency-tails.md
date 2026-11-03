---
id: rel-queue-latency-tails
title: Queue utilisation and latency tails
level: intermediate
minutes: 4
summary: Use an M/M/1 model to explain why high utilisation inflates mean and tail latency.
sourceLesson: rel-overload-protection
---

Timeouts bound waiting, but a healthy service also needs spare capacity. This unit uses an explicitly simplified queueing model to explain the shape of overload, rather than predict every multi-worker production service.

## Why overload is a cliff, not a slope

With variable arrivals and service times, queueing delay can rise sharply near capacity. The simplest model that shows this is the **M/M/1 queue**: requests arrive at random (a Poisson process), each takes a random, exponentially distributed time to serve, there is one server, requests are served first in, first out (FIFO), and the waiting line has no size limit. For a stable M/M/1 queue, the average time a request spends in the system (waiting plus being served) is:

```formula reference
W = S / (1 − ρ)
where
W: the mean time in system (queueing plus service), in milliseconds (ms)
S: the mean service time, the time to process one request with no queue, here 10 ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 to just under 1; here 0.9 (90%)
ms: milliseconds
In words: at 90% busy, a request that takes 10 ms of work spends 100 ms in the system on average, ten times its service time, because most of that time is spent queueing.
```

The practical effect is lost latency headroom:

At 90% utilisation, this model’s mean time in system is ten times its mean service time.

The model only holds while utilisation is below 100%; at or above capacity the unbounded queue never settles.

| Utilisation | Latency multiplier |
|---|---|
| 50% | 2× |
| 80% | 5× |
| 90% | 10× |
| 99% | 100× |

The tail is worse than the mean. In an M/M/1 queue the time in system is exponentially distributed, and for an exponential distribution any percentile is a fixed multiple of the mean:

In this model, p99 is about 4.6 times the mean. A 100-millisecond mean therefore corresponds to about a 460-millisecond p99; this conversion is specific to the exponential response-time distribution.

Multi-worker systems and other arrival/service distributions have different delay curves; measure actual service behavior rather than treating M/M/1 as a universal bound.

## Key takeaways

- In the stable M/M/1 model, time in system rises sharply as utilisation approaches one.
- The exponentially distributed time in system places p99 at about 4.6 times the mean.
- The model assumes random independent arrivals, exponential service, one server and FIFO; measure other systems.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
