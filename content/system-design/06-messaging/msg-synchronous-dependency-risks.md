---
id: msg-synchronous-dependency-risks
title: Synchronous dependencies: availability and tail latency
level: basic
minutes: 4
summary: Predict how waiting on several required services erodes availability, tail latency and capacity.
sourceLesson: msg-sync-vs-async
---

When one service needs another to do something, it has two basic choices. It can **ask and wait** (synchronous), or it can **leave a note and move on** (asynchronous). Almost every messaging system you will meet in this module exists to make the second option reliable.

## Synchronous: request and wait

In a synchronous call, the caller sends a request (usually HTTP or gRPC) and logically waits for a response or timeout; a nonblocking client need not block an operating-system thread.

```
Checkout ──HTTP──▶ Payments ──▶ Fraud
   ▲                  │            │
   └──── waits ───────┴── waits ───┘
```

This is simple and gives you an immediate answer, which is exactly what you want when the user is waiting for that answer: "was my card accepted?"

But synchronous chains have three structural weaknesses:

- **Availability multiplies.** If Checkout requires three services that are each 99.9% available and their failures are independent, all three must be up at once, so together they are only about 99.7% available. Correlated failures change this calculation, and Checkout has its own failure modes. That is about 26 hours of downtime a year instead of 8.8.
- **Latency adds up.** Sequential dependent calls add their durations; parallel fan-out waits for the required critical path, and tail latency (p99) gets worse as you add hops, because the slowest dependency dominates. If a request touches 5 services with independent delays and each is slow 1% of the time, the request hits at least one slow call about 4.9% of the time: tail slowness becomes more frequent at the request level; exact quantiles depend on the full latency distributions.
- **Load is coupled.** A spike at the front door hits every downstream service at the same instant. If Fraud can only handle 500 requests a second, Checkout can only handle 500 requests a second.

Both numbers come from one rule of probability: when events are independent, the chance that all of them happen is the product of their separate chances. A request that needs every dependency succeeds only when all of them are up, and is fast only when every call is fast.

```formula reference
A_chain = A_1 × A_2 × A_3
P_slow = 1 − (1 − p)^k
where
A_chain: the availability of the chain: the fraction of time all three required dependencies are up together, ignoring Checkout's own failures
A_1: the availability of the first dependency (Payments), as a fraction; 99.9% is 0.999
A_2: the availability of the second dependency (Inventory), as a fraction
A_3: the availability of the third dependency (Fraud), as a fraction
P_slow: the probability that a request hits at least one slow call
p: the probability that any one call is slow, as a fraction; 1% is 0.01
k: the number of independent calls the request must wait for
^: to the power of; (1 − p)^k is the chance that all k calls are fast
In words: multiply the availabilities of required dependencies, so three 99.9% services give about 99.7%; and a request that waits for five calls, each slow 1% of the time, is slow about 5% of the time.
```

Both relationships assume independence. Shared causes (one database, one network link, one bad deploy) make failures and slow calls happen together, so real systems can be better or worse than these numbers, and you should measure. The practical lesson does not depend on the exact figure: every extra *required* hop on the synchronous path adds its own downtime and its own chance of a slow response.

> [!analogy] Real-world analogy: a journey with connecting trains
> A trip that needs three connecting trains only works if all three run. Each line might be reliable on its own, but the more connections you need, the more often something spoils the whole trip. If you wait on a platform for several friends arriving on different trains, you leave when the *last* one arrives.
>
> **How it maps:** Each train is a required dependency. Needing every connection is a series dependency, so the journey fails more often than any one line (availability multiplies). Waiting for every friend is parallel fan-out: the slowest arrival sets your departure time (tail latency).
>
> **Where it stops:** Trains on one network often fail together (one signal fault, one strike), which is exactly the shared-cause case that breaks the independence assumption. And a train timetable is fixed, whereas a service can time out, retry or degrade gracefully rather than simply waiting.

## Key takeaways

- A synchronous request waits logically for a result; it need not block an operating-system thread.
- Independent required dependencies multiply availability, while parallel fan-out exposes the slowest required call.
- Shared failures break the independence assumption, so measure the actual critical path.

## Further reading

- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [Enterprise Integration Patterns: Messaging](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)
