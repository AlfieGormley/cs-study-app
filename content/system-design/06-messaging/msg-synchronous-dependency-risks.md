---
id: msg-synchronous-dependency-risks
title: Synchronous dependencies: availability and tail latency
level: basic
minutes: 4
summary: Calculate the reliability and latency costs of waiting for several required services.
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

- **Availability multiplies.** If Checkout requires three services that are each 99.9% available and their failures are independent, all three must be up at once, so together they are only about 99.7% available (worked out below). Correlated failures change this calculation, and Checkout has its own failure modes. That is about 26 hours of downtime a year instead of 8.8.
- **Latency adds up.** Sequential dependent calls add their durations; parallel fan-out waits for the required critical path, and tail latency (p99) gets worse as you add hops, because the slowest dependency dominates. If a request touches 5 services with independent delays and each is slow 1% of the time, the request hits at least one slow call about 4.9% of the time (worked out below): tail slowness becomes more frequent at the request level; exact quantiles depend on the full latency distributions.
- **Load is coupled.** A spike at the front door hits every downstream service at the same instant. If Fraud can only handle 500 requests a second, Checkout can only handle 500 requests a second.

Both numbers come from one rule of probability: when events are independent, the chance that all of them happen is the product of their separate chances. For availability, a request that needs every dependency succeeds only when all of them are up:

```formula
A_chain = A_1 × A_2 × A_3
A_chain = 0.999 × 0.999 × 0.999
A_chain ≈ 0.997 = 99.7%
where
A_chain: the availability of the chain: the fraction of time all three dependencies are up together, so the request can succeed (ignoring Checkout's own failures)
A_1: the availability of the first dependency (Payments): the fraction of time it is up, here 0.999 (99.9%)
A_2: the availability of the second dependency (Inventory), here 0.999
A_3: the availability of the third dependency (Fraud), here 0.999
≈: approximately equal to (the result is rounded)
%: per cent; 0.997 is the same as 99.7%
In words: when every dependency is required, multiply their availabilities; three 99.9% services together are only about 99.7% available.
```

To turn an availability into downtime, multiply the fraction of time it is *not* up by the 8,760 hours in a 365-day year:

```formula
D = (1 − A) × 8760 h
D_one = (1 − 0.999) × 8760 h ≈ 8.8 h
D_chain = (1 − 0.997) × 8760 h ≈ 26 h
where
D: expected downtime per year, in hours (h)
A: an availability, as a fraction between 0 and 1
D_one: the yearly downtime of one 99.9% service
D_chain: the yearly downtime of the chain of three, which is about 99.7% available
h: hours
≈: approximately equal to
In words: each extra required dependency adds its own downtime, so three 99.9% services cost about three times the downtime of one.
```

For tail latency, it is easier to work out the chance that *every* call is fast and subtract that from 1:

```formula
P_slow = 1 − (1 − p)^k
P_slow = 1 − 0.99^5
P_slow ≈ 1 − 0.951 = 0.049
where
P_slow: the probability that a request hits at least one slow call, as a fraction (0.049 is 4.9%)
p: the probability that any one call is slow, here 0.01 (1%)
k: the number of independent calls the request must wait for, here 5
^: to the power of; 0.99^5 means 5 copies of 0.99 multiplied together
≈: approximately equal to
In words: if each of 5 calls is fast 99% of the time, all 5 are fast only about 95% of the time, so about 1 request in 20 is slow.
```

Both formulas assume independence. Shared causes (one database, one network link, one bad deploy) make failures and slow calls happen together, so real systems can be better or worse than these numbers, and you should measure.

## Key takeaways

- A synchronous request waits logically for a result; it need not block an operating-system thread.
- Independent required dependencies multiply availability, while parallel fan-out exposes the slowest required call.
- Shared failures break the independence assumption, so measure the actual critical path.

## Further reading

- [Queue-Based Load Leveling pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [Enterprise Integration Patterns: Messaging](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)
