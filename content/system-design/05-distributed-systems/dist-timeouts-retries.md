---
id: dist-timeouts-retries
title: Timeouts, retries and unknown outcomes
level: basic
minutes: 5
summary: Design retries for partial failure without repeating side effects or amplifying load.
sourceLesson: dist-why-hard
---

A distributed system is a set of computers that cooperate over a network and, ideally, look like one machine to the user. You build one because a single machine can't give you enough capacity, availability or geographic reach.

The price is that you inherit a class of problems that simply do not exist inside one process. Almost every technique in this module (quorums, consensus, fencing tokens, sagas, CRDTs) exists to tame the failure modes introduced here and in the following units.

## Partial failure

A process crash or power loss can stop all work on one computer. Single machines can also suffer partial faults, such as a failed disk or a stuck thread; networking adds uncertainty about other machines whose state you cannot inspect directly.

In a distributed system, failure is **partial**. Some nodes work, some don't, and some are in an unknown state. Worse, failures are **non-deterministic**: the same request might succeed, fail, or hang.

Consider a client calling a remote service:

```
Client                  Server
  |---- request ------->|
  |                     |  (does work?)
  |       ...           |
  |   (no reply)        |
  |                     |
 timeout!
```

When the timeout fires, the client has no idea which of these happened:

1. The request was lost before reaching the server.
2. The server is down or paused (e.g. a long GC pause).
3. The server processed the request, but the reply was lost.
4. The server is just slow and will reply in 5 seconds.

All four look identical to the client. Cases 1 and 3 are the dangerous pair: in case 1 nothing happened, while in case 3 the side effect (charging a card, sending an email) **already happened**. This is why retries must be designed with idempotency in mind: an idempotency key lets the server recognise a duplicate and return its recorded result. This depends on the server's atomic deduplication and retention contract: a key forgotten after its retention window no longer protects a late retry.

> [!warning] The core uncertainty
> A remote node can't tell "dead" from "slow" from "network broken". All it ever has is "I haven't heard back yet". Every failure detector is a guess.

## Living with timeouts

Since a timeout is the only failure signal you get, its value is a real design decision.

- **Too short**: a slow but healthy node is declared dead. You fail over, retry or rebalance for nothing, and the extra work can make the overload that caused the slowness worse.
- **Too long**: a genuinely dead node stalls requests (and users) for the whole timeout before anything happens.

A common starting point is to set request timeouts a little above the latency percentile you're willing to give up on (say the p99.9 of healthy calls), rather than picking a round number. Failure detectors used for cluster membership go further and *adapt* to observed latency; the failure-detection unit later in this module covers the phi accrual detector.

### Retries need care too

Retrying after a timeout is natural, but naive retries cause their own outages:

- **Use the same idempotency key on every attempt.** A fresh key per attempt makes each retry look like a new request, which defeats the point.
- **Back off exponentially, with jitter.** If thousands of clients retry on the same schedule, they hit the recovering server in synchronised waves.
- **Retry at one layer only.** If three layers each make up to 3 attempts, one user request can become 3 × 3 × 3 = 27 calls at the bottom layer, just when it is least able to cope.

```
web (3 tries)
 -> api (3 tries each)  = 9
   -> db (3 tries each) = 27
```

The numbers multiply because every attempt at one layer starts a fresh set of attempts at the layer below. In general, when every layer in a stack retries independently:

```formula
C = a^L
C = 3^3
C = 27
where
C: the worst-case number of calls that reach the bottom layer for one user request (a count, no unit)
a: the maximum number of attempts each layer makes, counting the first try; here 3
L: the number of stacked layers that each retry; here 3 (web, API and database)
In words: the worst-case load on the bottom layer grows as a power of the number of retrying layers. Three layers of 3 attempts turn 1 request into 27 calls; a fourth layer would make it 81.
```

This is the worst case: it happens when every attempt fails, which is exactly what an overloaded database does. If only one layer retries (3 attempts), the bottom layer sees at most 3 calls per request.

## Key takeaways
- A timeout cannot tell whether a remote side effect happened; retry using the same idempotency key.
- Short timeouts can trigger needless failover and overload; long ones delay recovery.
- Back off with jitter and retry at one layer: independent retries multiply downstream load.

## Further reading
- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Making retries safe with idempotent APIs (AWS Builders' Library)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
