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

```formula
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
In words: equal jitter always waits at least half the backoff; decorrelated jitter grows each wait randomly from the last one, up to three times it, without passing the cap.
```

For a 400-millisecond backoff, the equal-jitter calculation gives a wait between 200 and 400 milliseconds:

```formula
t = 400 ms
w_eq = t / 2 + random(0, t / 2)
w_eq = 200 ms + random(0, 200 ms)
where
t: the plain backoff delay, in milliseconds (ms)
w_eq: the equal-jitter delay, in milliseconds
random(x, y): a uniformly chosen delay from x to y
ms: milliseconds, one thousandth of a second
In words: Half the delay is certain and the other half is random, so the total lies between 200 and 400 milliseconds.
```

In his simulations, full jitter used the fewest calls; decorrelated jitter finished slightly sooner but did more work; equal jitter was the loser, doing slightly more work than full jitter and taking much longer. Equal jitter's one attraction is that it guarantees a minimum wait. All three are vastly better than no jitter.

The documented AWS SDK standard retry mode uses full jitter. In standard retry mode (as documented for the SDKs' updated 2026 retry behaviour, opt-in at first) the delay is written as a random fraction of the backoff, which is the same thing:

```formula
w = r × min(c, b(2^a))
w = 0.5 × min(20 s, 0.05 s × 2^1)
w = 0.5 × 0.1 s = 0.05 s
where
w: the wait before the next attempt, in seconds (s)
r: a uniformly random fraction between 0 and 1; here 0.5 for the illustrative draw
min: the smaller of the two values
c: the cap, 20 s in the SDKs' standard mode
b: the base delay, in seconds (s); documented 2026 general standard-mode values are 0.05 s (50 milliseconds) for transient errors and 1 s (1,000 milliseconds) for throttling
a: the retry number, counting from 0; here 1 for the second retry
2^a: 2 to the power a
s: seconds
In words: wait a random fraction of the exponential backoff, which never exceeds 20 seconds.
```

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
