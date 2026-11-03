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

For example, waits can grow from 0.1 to 0.2 to 0.4 to 0.8 seconds.

```
attempt 1: wait 0.1 s
attempt 2: wait 0.2 s
attempt 3: wait 0.4 s
attempt 4: wait 0.8 s
cap at, say, 20 s
```

Doubling grows quickly, so clients cap the wait at a maximum.

**Jitter** randomises the wait so clients don't retry in synchronised waves. AWS's "full jitter" picks a random wait anywhere between zero and the capped backoff:

```formula reference
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

With base 0.1 seconds and a 20-second cap:

At the fourth retry in this convention, full jitter chooses a delay between zero and 0.8 seconds.

Retry numbering differs between libraries. This code counts the first retry as 1:

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
- **Honour `Retry-After`** when the server sends one. Wait at least that long only if another attempt still fits the operation deadline and retry budget; otherwise stop or report that retrying is deferred.
- **Retry at one layer only.** If the app, the SDK and a sidecar each allow 3 total attempts, one failure can become 27 attempts on the struggling backend, because nested retries multiply:

Every outer retry can run a complete set of inner retries. Choose one retry owner rather than letting every layer multiply the work.

> [!analogy] Real-world analogy: Staggered return times
> **How it maps:** If a busy reception desk tells everyone to return at exactly the same moment, the queue returns together. Giving people different return times spreads the next wave, like jitter.
>
> **Where it stops:** Random delays cannot make an overloaded service healthy or make an unsafe operation retryable. Attempt limits, deadlines and retry budgets are separate controls.

## Key takeaways
- Exponential backoff doubles waits; a cap prevents unbounded delays.
- Full jitter chooses a uniform wait inside the capped interval; check attempt-number conventions.
- Honour Retry-After and bound attempts and total retry load.
- Nested retry layers multiply attempts, so choose one retry owner.

## Further reading
- [AWS Builders' Library: Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
