---
id: dl-livelock-starvation-retry-storms
title: Retry storms and full jitter
level: intermediate
minutes: 2
sourceLesson: dl-livelock-starvation
summary: Synchronized retries amplify overload; exponential ceilings alone leave clients synchronized.
---

### Livelock at system scale

The same pattern appears wherever things retry:

- **Retry storms.** A service slows down; every client times out and retries at once, doubling the load; it slows further. The fix is exponential back-off with **jitter** (below).
- **Receive livelock.** Mogul and Ramakrishnan (1996) showed that an interrupt-driven kernel under a packet flood can spend all its time taking receive interrupts and none delivering packets to applications. Throughput collapses to near zero while the CPU is fully busy. Linux's NAPI uses interrupt-triggered, budgeted polling to mitigate receive livelock (module 7); it does not guarantee application progress under every overload or configuration.
- **Optimistic concurrency.** Two transactions that keep conflicting, aborting and restarting together can livelock. Back-off can reduce collisions; timestamp protocols need fair execution and finite transactions for eventual completion.

AWS's "full jitter" back-off picks each sleep at random between zero and an exponentially growing ceiling:

```formula
b = min(t_cap, t_base 2^a)
t_sleep = random(0, b)
b = min(2 s, 100 ms × 2^4) = 1.6 s
where
a: the attempt number, starting at 0
t_base: the base delay, 100 milliseconds (ms) in the example
t_cap: the largest ceiling allowed, 2 seconds (s) in the example
min(…): the smaller of the two values
b: the ceiling for this attempt
random(0, b): a number drawn uniformly at random between 0 and b
t_sleep: how long the client actually sleeps before retrying
ms: milliseconds
s: seconds
In words: the ceiling doubles with each attempt until it hits the cap, and the actual sleep is a random point below the ceiling, so clients that failed together spread out.
```

With these numbers the ceilings run 100, 200, 400, 800 and 1,600 ms, then stay at 2 s. In Python the same rule is `random.uniform(0, min(cap, base * 2**attempt))`. Doubling alone would keep synchronised clients synchronised; the randomness is what spreads them out.

## Key takeaways
- Synchronized retries amplify overload; exponential ceilings alone leave clients synchronized.
- Full jitter draws an independent delay below a capped exponential ceiling.
- Budgeted polling mitigates receive livelock without proving progress for every overload.

## Further reading
- [AWS: exponential back-off and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Linux: NAPI budgeted polling](https://docs.kernel.org/networking/napi.html)
