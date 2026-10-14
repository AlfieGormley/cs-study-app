---
id: api-backoff-jitter-budgets
title: Backoff, jitter and retry budgets
level: intermediate
minutes: 5
summary: Spread safe retries over time and keep retry amplification inside deadline and load budgets.
sourceLesson: api-idempotency
---

## Retries need backoff and jitter

Idempotency makes retries *safe*. It doesn't make them *wise*. If a service is struggling and every client retries immediately, you've multiplied the load on something that's already failing.

**Exponential backoff** spaces retries out by doubling the wait each time:

```formula
T_n = base × 2^{n − 1}
T_4 = 0.1 s × 2^3 = 0.1 s × 8 = 0.8 s
where
T_n: the wait before retry number n, in seconds (s)
n: which retry this is: 1 for the first retry, 2 for the second, and so on
base: the first wait, here 0.1 s
T_4: the wait before the fourth retry
s: seconds
In words: each retry waits twice as long as the one before, so the waits grow 0.1, 0.2, 0.4, 0.8 s and so on.
```

```
attempt 1: wait 0.1 s
attempt 2: wait 0.2 s
attempt 3: wait 0.4 s
attempt 4: wait 0.8 s
cap at, say, 20 s
```

Doubling grows fast (the 12th retry would wait over 200 s), so real clients cap the wait at a maximum.

**Jitter** randomises the wait so clients don't retry in synchronised waves. AWS's "full jitter" picks a random wait anywhere between zero and the capped backoff:

```formula
T_max = min(cap, base × 2^{n − 1})
T_sleep = random(0, T_max)
where
T_max: the longest this retry may wait, in seconds (s)
cap: the largest wait ever allowed, here 20 s
base: the first backoff wait, here 0.1 s
n: which retry this is, starting at 1
min: the smaller of the two values
random: a number picked uniformly at random between the two values, so every wait in that range is equally likely
T_sleep: the wait actually used before this retry
s: seconds
In words: work out the doubled backoff, never let it exceed the cap, then wait a random time between zero and that.
```

Worked example for the fourth retry with base 0.1 s and cap 20 s:

```formula
T_max = min(20 s, 0.1 s × 2^3)
T_max = min(20 s, 0.8 s) = 0.8 s
T_sleep = random(0 s, 0.8 s)
where
T_max: the longest the fourth retry may wait
T_sleep: the wait actually used, on average 0.4 s
min: the smaller of the two values
random: a uniformly random value in the range
s: seconds
In words: the cap doesn't bite yet, so the client waits somewhere between 0 and 0.8 s, 0.4 s on average.
```

AWS's article uses the attempt number itself as the exponent and doesn't say whether counting starts at 0 or 1. Counted from 0 it is exactly the formula above; counted from 1 every wait is twice as long, so check which convention a library uses. In code:

```python
import random

def full_jitter(n, base=0.1, cap=20.0):
    # Retry 1 uses the base; cap later
    # waits.
    t_max = min(cap, base * 2 ** (n - 1))
    # Return a random delay, not a fixed
    # one.
    return random.uniform(0, t_max)
```

Without jitter, 10,000 clients that all failed at the same moment retry at the same moment, every time. That's a **thundering herd**.

Also:

- **Cap the number of attempts** according to the deadline and overload budget (for example, three total attempts).
- **Use a retry budget**: allow retries to add at most, say, 10% extra load, so a full outage doesn't triple your traffic. For 1,000 requests/s, a 10% budget allows at most 100 retries/s, however many requests fail.
- **Retry only retryable errors**: timeouts, connection resets, `429`, `502`, `503`, `504`, and an idempotency layer's `409` meaning "the original is still in progress". Never retry `400` or `422` unchanged.
- **Honour `Retry-After`** when the server sends one. It knows better than your backoff formula.
- **Retry at one layer only.** If the app, the SDK and a sidecar each allow 3 total attempts, one failure can become 27 attempts on the struggling backend, because nested retries multiply:

```formula
A = a^L
A = 3^3 = 3 × 3 × 3 = 27
where
A: the most attempts that reach the bottom service for one user action
a: the total attempts each layer allows, here 3
L: the number of nested layers that retry, here 3 (app, SDK, sidecar)
In words: every attempt at one layer can trigger a full set of attempts at the layer below, so the counts multiply rather than add.
```

## Key takeaways
- Exponential backoff doubles waits; a cap prevents unbounded delays.
- Full jitter chooses a uniform wait inside the capped interval; check attempt-number conventions.
- Honour Retry-After and bound attempts and total retry load.
- Nested retry layers multiply attempts, so choose one retry owner.

## Further reading
- [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
