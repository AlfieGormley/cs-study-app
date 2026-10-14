---
id: fund-queueing-headroom
title: Predict queueing and leave capacity headroom
level: intermediate
minutes: 5
summary: Use the M/M/1 model and Little’s law to connect utilisation, latency and requests in flight.
sourceLesson: fund-latency-throughput
---

A server can have enough nominal throughput and still give poor latency because requests spend time waiting. Queueing models explain why capacity planning needs spare room.

## How they interact: queueing

Latency and throughput meet through **queueing**. When requests arrive faster than a server can process them, they wait. Waiting time is latency.

The simplest model of this is the **M/M/1 queue**: requests arrive at random (the first M), each takes a random amount of work to serve (the second M; "M" stands for Markovian, a particular kind of randomness), and there is 1 server handling one request at a time. For that model, queueing theory gives the average time a request spends in the system, waiting plus being served:

```formula
ρ = λ / μ
W = S / (1 − ρ)
where
W: the average time a request spends in the system (queueing plus being served), in milliseconds (ms); this is the latency the client sees
S: the average service time, the time the server spends actually working on one request when there is no queue, in ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 (idle) to just under 1 (always busy)
λ: lambda, the arrival rate, in requests per second (req/s)
μ: mu, the service rate (capacity), the most requests per second the server can complete, equal to 1 / S with S in seconds (a 10 ms service time gives 100 req/s)
ms: millisecond, one thousandth of a second
In words: latency is the service time divided by the fraction of time the server is idle. As the server gets busier, that idle fraction shrinks towards zero, so latency grows without limit.
```

Example: a server with a 10 ms service time at 80% utilisation has an average time in the system of 10 / (1 − 0.8) = 10 / 0.2 = 50 ms, five times the service time. The table shows the same ratio at other loads:

| Utilisation | Latency vs service time |
|---|---|
| 50% | 2x |
| 80% | 5x |
| 90% | 10x |
| 99% | 100x |

This is why systems "fall off a cliff". At 50% load everything looks fine; at 90% latency has quintupled compared with 50%; as utilisation approaches 100% from below, the M/M/1 steady-state mean queue length diverges; at or above 100% the infinite-buffer model has no stable steady state. It's also why capacity planning typically targets 50–70% peak utilisation, leaving headroom.

Real servers aren't exactly M/M/1 (they have many workers, and service times vary differently), and the exact curve depends on arrival/service variability, scheduling and queue limits. Many real systems develop large queues near saturation; a deterministic or admission-controlled system need not follow this curve.

## Little's law: how many requests are in flight

One more relationship ties the two metrics together. It holds for any stable system (one where requests don't pile up forever), averaged over time, whatever the pattern of arrivals:

```formula
L = λ × W
L = 2,000 /s × 0.05 s = 100
where
L: the average number of requests in flight (in the system at once), the concurrency; a plain count with no unit
λ: lambda, the throughput, the average rate at which requests arrive (and leave), in requests per second (/s)
W: the average time each request spends in the system, its latency, in seconds (s); here 50 ms = 0.05 s
s: second
ms: millisecond, one thousandth of a second
In words: requests in flight equal how fast they arrive multiplied by how long each one stays.
```

So a service doing 2,000 req/s at 50 ms average latency has **100 requests in flight on average**. Convert milliseconds to seconds first, or the answer is out by a factor of 1,000. If latency rises tenfold at the same throughput, so does the number in flight, which is why a slow dependency can exhaust every thread you have. The scalability lesson uses this law to size thread and connection pools.

## Key takeaways
- The M/M/1 model’s mean latency grows sharply near saturation; real systems depend on their workload, admission rules and scheduling.
- Little’s law multiplies throughput by time in the system to give average concurrency.
- Check both normal load and survivor capacity during failures; headroom must satisfy each target.

## Further reading
- [Little’s Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Handling Overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
- [MIT: basic queueing theory](https://ocw.mit.edu/courses/15-763j-manufacturing-system-and-supply-chain-design-spring-2005/22f4805864deb06eee85acc1601463ba_queueing_note.pdf)
