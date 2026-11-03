---
id: rel-jitter-variants-sdk-policy
title: Jitter variants and versioned SDK policy
level: intermediate
minutes: 4
summary: Compare jitter distributions and scope SDK defaults to the documented retry mode.
sourceLesson: rel-timeouts-retries
---

Full jitter, introduced immediately before this unit, chooses a delay from zero to the current capped backoff. The alternatives below change its minimum or how successive waits are related. Product defaults must be tied to an SDK mode and documented version.

## Equal and decorrelated jitter

The two other variants keep a floor under the wait:

```formula reference
t = min(c, b(2^a))
w_eq = t/2 + random(0, t/2)
w_dec = min(c, random(b, 3w_prev))
where
t: the plain exponential-backoff wait, in milliseconds (ms)
w_eq: the equal-jitter wait, in milliseconds (ms): half of t fixed plus a random amount up to the other half
w_dec: the decorrelated-jitter wait, in milliseconds (ms)
w_prev: the previous wait, in milliseconds (ms), starting at b
random(x, y): a number chosen uniformly at random between x and y
min: the smaller of the two values
c: the cap, the longest wait allowed, in milliseconds (ms)
b: the base delay, in milliseconds (ms)
a: the retry number, counting from 0
2^a: 2 to the power a
In words: equal jitter always waits at least half the backoff; decorrelated jitter chooses between the base delay and three times the previous wait, then applies the cap, so the wait may shrink as well as grow.
```

For a 400-millisecond backoff, equal jitter waits between 200 and 400 milliseconds. Full jitter can use the whole interval from zero to 400 milliseconds.

In his simulations, full jitter used the fewest calls; decorrelated jitter finished slightly sooner but did more work; equal jitter was the loser, doing slightly more work than full jitter and taking much longer. Equal jitter's one attraction is that it guarantees a minimum wait. All three are vastly better than no jitter.

The documented 2026 standard mode caps the backoff at 20 seconds and samples a random fraction of it. General base delays are 50 milliseconds for transient errors and one second for throttling; the first retry uses the base interval.

The SDK documentation gives DynamoDB and DynamoDB Streams clients a shorter 25-millisecond transient base and four attempts by default. Long-polling operations also have special backoff behaviour. Check the exact client and operation, rather than applying the general example unchanged.

> [!tip] Jitter everything periodic
> The same synchronisation problem hits cron jobs, cache expiry and health checks. Add jitter to TTLs and scheduled tasks too, or every client refreshes on the hour.

## Key takeaways

- Equal jitter keeps half of the current delay certain; decorrelated jitter chooses from the previous delay.
- The AWS simulation compares workload and completion time under its particular contention model.
- The quoted SDK values describe the 2026 opt-in standard retry behaviour; verify the SDK and mode actually in use.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Exponential backoff and jitter (AWS Architecture Blog)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [AWS SDK retry behaviour (2026 opt-in)](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)
