---
id: msg-consumer-lag-retry-storms
title: Diagnose consumer lag and retry storms
level: advanced
minutes: 5
summary: Turn lag into delay, inspect its trend and spread recovery retries with capped jitter.
sourceLesson: msg-ordering-backpressure
---

Lag tells you whether the whole pipeline is falling behind. Its shape and distribution help separate temporary buffering from persistent capacity problems or a failed record blocking one lane.

## Consumer lag

**Consumer lag** is how far a consumer group is behind the head of the log. In Kafka it is measured per partition, as a distance in offsets:

```formula
lag = LEO − C
lag = 1500 − 1200 = 300
where
lag: the consumer lag of one partition, in offsets (roughly, records not yet consumed)
LEO: the log end offset: the offset the next record appended to the partition will get
C: the group's committed offset for that partition: the next offset it will read
In words: lag is how many offsets lie between where the group will read next and the end of the log.
```

Offset-distance lag is easy to get but can include compacted gaps or transaction/control offsets; it is not always a count of application records. It is also hard to interpret: 50,000 records is nothing on a topic doing 100,000 per second and alarming on one doing 10 per second. Convert it to **time**, in one of two ways:

- Divide lag by the recent incoming rate (the formula below). This works when the arrival rate is reasonably steady; it is not a reliable instantaneous application of Little's Law during bursts.
- Subtract the timestamp of the record at the committed offset from the current time.

```formula
t_lag ≈ lag / λ
t_lag ≈ 180000 / (2000/s) = 90 s
where
t_lag: the approximate age of the backlog: how far behind real time the group is, in seconds (s)
lag: the consumer lag, here 180,000 records
λ: lambda, the recent rate at which records arrive, here 2,000 per second
≈: approximately equal to
s: seconds; "/s" means per second
In words: 180,000 records behind at 2,000 a second is about 90 seconds of traffic behind.
```

Also watch the **trend**. Lag that spikes and recovers is load levelling working. Lag that grows steadily means consumption is slower than production, and it will not recover by itself.

```
lag
 │      ╱╲            ╱
 │     ╱  ╲         ╱
 │ ___╱    ╲____  ╱   ← growing:
 └─────────────────▶     act now
   burst, recovers
```

Tools such as Burrow (from LinkedIn) evaluate lag trends per partition rather than using a fixed threshold. Autoscalers such as KEDA can add consumers based on lag, up to the partition count.

### Diagnosing growing lag

1. **Is it all partitions or one?** One hot partition suggests key skew or a poison message. All partitions suggests too little capacity.
2. **Is the consumer busy or waiting?** High CPU means scale out or optimise. Low CPU with high latency means a slow dependency (database, API).
3. **Is it rebalancing?** Frequent rebalances (check logs for revoked partitions) stall consumption. Common causes are processing exceeding `max.poll.interval.ms`, or deploys without static membership.
4. **Did production rate change?** A new producer or a backfill can double input.

## Retry storms and backoff

When a dependency fails, every consumer retrying immediately multiplies load on it exactly when it is weakest. Use **exponential backoff with jitter**: double the delay after each failed attempt, cap it, then randomise it so clients spread out instead of retrying in lockstep. The "full jitter" form that AWS describes is:

```formula
d_n = min(cap, b × 2^(n − 1))
d_3 = min(60 s, 1 s × 2^2) = 4 s
w_n = random(0, d_n)
where
d_n: the backoff limit before retry number n, in seconds (s)
n: the retry number: 1 for the first retry, 2 for the second, and so on
d_3: the backoff limit before the third retry
min: the smaller of the two values
cap: the largest delay you allow, here 60 s
b: the base delay, here 1 s
^: to the power of; 2^2 = 4
w_n: the time the client actually waits before retry n
random: a number drawn uniformly at random between the two values given
s: seconds
In words: the delays go 1 s, 2 s, 4 s and so on up to the cap, and each client waits a random time up to that delay, so retries spread out instead of arriving together.
```

AWS's article writes the exponent as the attempt count; here n counts retries from 1, so the exponent is n − 1 and the first retry waits up to one base delay. Either way the shape is the same. Then cap the number of attempts, and consider a **circuit breaker** that pauses consumption entirely while the dependency is unhealthy. Pausing is fine for a log; the data waits subject to broker capacity and retention; prolonged pauses can lose access to expired data.

## Key takeaways

- Offset lag is a distance, not always an application-record count; under steady arrivals it can estimate delay.
- Inspect per-partition trends, CPU, dependency waits and rebalances before choosing a scaling fix.
- Processing must leave enough time to poll; smaller batches or a bounded asynchronous worker design can prevent repeat rebalances.
- Capped exponential backoff with jitter spreads retries; long pauses remain bounded by broker retention.

## Further reading

- [Burrow: Kafka consumer lag checking (LinkedIn, GitHub)](https://github.com/linkedin/Burrow)
- [Kafka consumer (Confluent docs)](https://docs.confluent.io/platform/current/clients/consumer.html)
- [Timeouts, retries and backoff with jitter (Amazon Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
