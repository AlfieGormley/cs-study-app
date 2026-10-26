---
id: fund-queueing-headroom
title: Predict queueing and leave capacity headroom
level: intermediate
minutes: 4
summary: Explain why queueing grows near saturation and why spare capacity matters during peaks and failures.
sourceLesson: fund-latency-throughput
---

A server can have enough nominal throughput and still give poor latency because requests spend time waiting. Queueing models explain why capacity planning needs spare room.

## How they interact: queueing

Latency and throughput meet through **queueing**. When requests arrive faster than a server can process them, they wait. Waiting time is latency.

The **M/M/1 queue** assumes Poisson arrivals (independent random arrivals at a constant average rate), exponentially distributed service times, and one server serving one request at a time. The two M letters refer to the model’s memoryless arrival and service assumptions. For that model, queueing theory gives the average time a request spends in the system, waiting plus being served:

```formula reference
ρ = λ / μ
W = S / (1 − ρ)
where
W: the average time a request spends in the system (queueing plus being served), in milliseconds (ms); this is the response time within the modelled system
S: the average service time, the time the server spends actually working on one request when there is no queue, in ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 (idle) to just under 1 (always busy)
λ: lambda, the arrival rate, in requests per second (req/s)
μ: mu, the service rate (capacity), the most requests per second the server can complete, equal to 1 / S with S in seconds (a 10 ms service time gives 100 req/s)
ms: millisecond, one thousandth of a second
In words: in this single-server model, average response time rises sharply as spare capacity shrinks. Near full utilisation, a small extra load can cause a large increase in waiting.
```

For a modelled server with a 10 ms mean service time, 80% utilisation gives a 50 ms average response: most of that time is waiting. The table illustrates how quickly waiting grows:

| Utilisation | Latency vs service time |
|---|---|
| 50% | 2x |
| 80% | 5x |
| 90% | 10x |
| 99% | 100x |

This is why systems can appear to "fall off a cliff". As utilisation approaches 100% from below, the M/M/1 steady-state mean queue length diverges; at or above 100% the infinite-buffer model has no stable steady state. Capacity planning needs measured headroom rather than a goal of keeping every resource fully busy.

Real servers aren't exactly M/M/1 (they have many workers, and service times vary differently), and the exact curve depends on arrival/service variability, scheduling and queue limits. Many real systems develop large queues near saturation; a deterministic or admission-controlled system need not follow this curve.

## Little's law: how many requests are in flight

Little's law connects average throughput, time in the system and concurrency in a stable system, where work does not accumulate forever. If requests arrive at the same rate but each stays ten times longer, ten times as many are in flight on average. A slow dependency can therefore exhaust upstream threads or connections even without a traffic spike. The pool-sizing unit gives the reference relationship and discusses its limits.

Headroom must also cover failures. If three equally sized zones normally share the load, losing one pushes its work onto the two survivors. Test that case separately from healthy operation; acceptable normal utilisation alone does not prove the survivors will meet the latency target.

## Key takeaways
- The M/M/1 model’s mean latency grows sharply near saturation; real systems depend on their workload, admission rules and scheduling.
- Little’s law multiplies throughput by time in the system to give average concurrency.
- Check both normal load and survivor capacity during failures; headroom must satisfy each target.

## Further reading
- [Little’s Law (Marc Brooker)](https://brooker.co.za/blog/2018/06/20/littles-law.html)
- [Handling Overload (Google SRE)](https://sre.google/sre-book/handling-overload/)
- [MIT: basic queueing theory](https://ocw.mit.edu/courses/15-763j-manufacturing-system-and-supply-chain-design-spring-2005/22f4805864deb06eee85acc1601463ba_queueing_note.pdf)
