---
id: rel-backoff-jitter-distribution
title: Exponential backoff and jitter
level: intermediate
minutes: 3
summary: Spread retries over time without synchronising clients into repeated load spikes.
sourceLesson: rel-timeouts-retries
---

This unit assumes retries are safe and the operation still has time and budget. Backoff controls when to retry; it does not reduce the maximum number of attempts. The retry index in the formulas begins at zero for the first retry.

## Exponential backoff

Retrying immediately after a failure hits the dependency again while it's still struggling. **Exponential backoff** waits longer after each failure:

Double the delay after each failed attempt until it reaches the cap. The following schedule is illustrative; the first retry uses the base delay.

With base 100 ms and cap 10 s the waits go:

```
attempt 0: 100ms
attempt 1: 200ms
attempt 2: 400ms
attempt 3: 800ms
attempt 4: 1.6s ...
attempt 7: 10s (capped; 12.8s > cap)
```

Backoff gives the dependency time to recover and spreads load over time. But on its own it has a nasty property.

## Jitter: breaking the synchronisation

Suppose 1,000 clients all fail at the same instant (a dependency restarted). With pure exponential backoff, they all wait exactly 100 ms, then all retry together, then all wait 200 ms, then all retry together again. The retries arrive in **synchronised waves** that look like a series of load spikes.

```
No jitter:          Full jitter:
 ▲                   ▲
 █   █    █          ▄▄▄▄▄▄▄▄▄▄▄▄
 █   █    █          ████████████
 └────────────▶      └────────────▶
  spikes              spread out
```

**Jitter** adds randomness so retries spread out. Marc Brooker's analysis on the AWS Architecture Blog compared variants. **Full jitter**, the recommended default, picks a wait uniformly at random anywhere between zero and the exponential-backoff value:

```formula reference
w = random(0, min(c, b(2^a)))
where
w: the wait before the next attempt, in milliseconds (ms)
random(x, y): a number chosen uniformly at random between x and y, so every value in the range is equally likely
min: the smaller of the two values
c: the cap, the longest wait allowed, here 10 s
b: the base delay, here 100 ms
a: the retry number, counting from 0, here 2
2^a: 2 to the power a
ms: milliseconds; 1000 ms = 1 s
s: seconds
In words: before its third retry (a = 2) a client waits somewhere between 0 and 400 ms, so 1,000 clients spread their retries across that whole window instead of all retrying at exactly 400 ms.
```

> [!analogy] Real-world analogy: staggering departures after an event
> If everyone leaves a venue together, the exit crowds. Asking groups to leave at varied times spreads the demand.
>
> **How it maps:** Varied departure times map to random retry delays; identical schedules map to repeated synchronised waves.
>
> **Where it stops:** Spreading arrivals does not create capacity or limit the total number of attempts. Retries still require safety, deadlines and budgets.

## Key takeaways

- Backoff doubles delay until its cap, and the first retry has index zero.
- Full jitter spreads each retry across the entire current backoff interval.
- Backoff and jitter change timing; retry budgets and one retry layer still control work.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Exponential backoff and jitter (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [AWS SDK retry behaviour (2026 opt-in)](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)
