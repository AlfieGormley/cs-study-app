---
id: fund-fanout-tail-latency
title: Control the tail amplified by fan-out
level: intermediate
minutes: 3
summary: Explain why more parallel backends increase exposure to slow responses, and choose remedies for variability.
sourceLesson: fund-latency-throughput
---

The previous unit introduced p99 and p99.9: thresholds near the slow end of a latency distribution. In a service that waits for many parallel backend calls, those rare slow responses can become the normal user experience.

## Why the tail matters more than you'd think

**Your heaviest users hit the tail most.** A user loading a page that makes 50 backend calls is much more likely to experience at least one slow call. Amazon's Dynamo paper describes service-level targets set at p99.9 rather than the mean or median, so that *every* customer gets a good experience, including those with the longest histories and so the most expensive requests.

**Fan-out amplifies the tail.** If a request fans out to several servers in parallel and must wait for all of them, it's as slow as the slowest. With independent 1%-slow backends, one call is rarely slow, but about 63% of requests waiting for 100 calls encounter at least one slow response. More calls create more opportunities for delay.

The reference relationship is useful when estimating that exposure:

```formula reference
P_slow = 1 − (1 − q)^n
where
P_slow: the probability that a user request is slow, i.e. at least one of its backend calls is slow, from 0 to 1
q: the probability that any one server exceeds the chosen slow-response threshold; here 0.01 (1%)
n: the number of servers the request fans out to in parallel
^: "to the power of": 0.99^10 means 10 copies of 0.99 multiplied together
In words: when a request needs every backend, more independent backend calls make it more likely to encounter at least one slow response.
```

The formula assumes each server is slow independently of the others. Correlated slowness (a shared overloaded database, say) changes the numbers.

At 100-way fan-out, most requests (63%) wait for at least one server's p99-or-worse response, so a single server's tail becomes your typical latency. This is the central point of Dean and Barroso's paper *The Tail at Scale*. Mitigations include **hedged requests** (send a second copy after the p95 time elapses and use whichever returns first), tied requests, and reducing variability at the source. Tied requests let a replica cancel its queued duplicate when another replica starts the work. Isolating or scheduling background work reduces interference; returning partial results after a deadline can cap latency when the application permits missing results.

## Key takeaways
- A request waiting for every shard inherits the slowest response.
- Independent 1%-slow shards make about 63% of 100-way requests slow; shared causes change that model.
- Hedging, partial results and reducing background-work interference address tail variability, with their own costs.

## Further reading
- [The Tail at Scale (Dean and Barroso)](https://www.barroso.org/publications/TheTailAtScale.pdf)
- [Dynamo: Amazon’s Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
