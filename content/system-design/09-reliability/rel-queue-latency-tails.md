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

```formula
W = S / (1 − ρ)
W = 10 ms / (1 − 0.9)
W = 10 ms / 0.1 = 100 ms
where
W: the mean time in system (queueing plus service), in milliseconds (ms)
S: the mean service time, the time to process one request with no queue, here 10 ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 to just under 1; here 0.9 (90%)
ms: milliseconds
In words: at 90% busy, a request that takes 10 ms of work spends 100 ms in the system on average, ten times its service time, because most of that time is spent queueing.
```

The response-time multiplier is the inverse idle fraction:

```formula
m = W / S = 1 / (1 − ρ)
m = 1 / (1 − 0.9) = 10
where
m: the mean-response-time multiplier, dimensionless
W: mean time in system, in milliseconds (ms)
S: mean service time, in milliseconds (ms)
ρ: utilisation, the fraction of time busy; here 0.9
ms: milliseconds
In words: At 90% utilisation this model’s mean response time is ten times mean service time.
```

The model only holds while utilisation is below 100%; at or above capacity the unbounded queue never settles.

| Utilisation | Latency multiplier |
|---|---|
| 50% | 2× |
| 80% | 5× |
| 90% | 10× |
| 99% | 100× |

The tail is worse than the mean. In an M/M/1 queue the time in system is exponentially distributed, and for an exponential distribution any percentile is a fixed multiple of the mean:

```formula
W_99 = W × ln(100)
W_99 ≈ 100 ms × 4.6 ≈ 460 ms
where
W_99: the 99th-percentile (p99) time in system: 99% of requests finish faster than this, in milliseconds (ms)
W: the mean time in system, here 100 ms (90% utilisation, 10 ms service time)
ln: the natural logarithm (log to base e ≈ 2.718); ln(100) ≈ 4.6
≈: approximately equal to (rounded)
ms: milliseconds
In words: in this model the slowest 1% of requests take more than about 4.6 times the average, so a 100 ms mean means a p99 of about 460 ms.
```

Where does ln(100) come from? For an exponential distribution, the fraction of requests slower than some multiple of the mean shrinks exponentially:

```formula
F = e^(−x)
F = e^(−ln(100)) = 1/100 = 1%
where
F: the fraction of requests slower than x times the mean
x: how many times the mean, here ln(100) ≈ 4.6
e: Euler's number, about 2.718, the base of natural logarithms
ln: the natural logarithm, the inverse of e^; e^(ln(100)) = 100
^: "to the power of"
≈: approximately equal to
%: per cent, one part in a hundred
In words: only 1% of requests are slower than about 4.6 times the mean, which is why p99 is about 4.6 times the mean in this model.
```

Multi-worker systems and other arrival/service distributions have different delay curves; measure actual service behavior rather than treating M/M/1 as a universal bound.

## Key takeaways

- In the stable M/M/1 model, time in system rises sharply as utilisation approaches one.
- The exponential time-in-system distribution places p99 at about 4.6 times the mean.
- The model assumes random independent arrivals, exponential service, one server and FIFO; measure other systems.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
