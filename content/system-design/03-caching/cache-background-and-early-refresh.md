---
id: cache-background-and-early-refresh
title: Refresh stale values or expire them probabilistically
level: advanced
minutes: 4
summary: Compare soft/hard expiry with XFetch’s random head start and calculate the early-refresh probability.
sourceLesson: cache-failure-modes
---

Readers need not all wait for a popular value to be rebuilt. A retained stale value can hide background work, and probabilistic refresh can begin that work before the nominal expiry.

### Fix B: serve stale while refreshing

Store the value with a **soft expiry** inside it and a longer **hard TTL** on the key. After the soft expiry, one request refreshes in the background while everyone else keeps getting the slightly stale value. This is `stale-while-revalidate` applied to your application cache, so readers with a retained eligible stale value can avoid waiting; after hard expiry, eviction or loss they still miss.

### Fix C: probabilistic early expiration (XFetch)

Instead of everyone noticing expiry at the same instant, each request independently decides to refresh **a little early**, with a probability that rises as expiry approaches. From Vattani, Chierichetti and Lowenstein (VLDB 2015), each request refreshes when:

```formula reference
t + δ × β × (−ln(U)) ≥ t_exp
where
t: the current time, in seconds (s)
δ: delta, how long one rebuild of this value takes, in seconds; measured when the value was last computed
β: beta, a tuning knob with no unit; 1 is the paper's default, above 1 refreshes earlier, below 1 later
ln: the natural logarithm (logarithm to base e ≈ 2.718)
U: a random number drawn uniformly above 0 and at most 1, fresh for every request
t_exp: the time at which the cached value expires, in seconds
≥: is greater than or equal to
s: seconds
In words: each request pretends the clock is a random amount later than it really is, and refreshes if that pretend time is past expiry. The random amount averages the rebuild time multiplied by a tuning factor (beta, normally 1), so slow-to-rebuild values refresh earlier.
```

The chance that any one request refreshes early is tiny far from expiry and climbs towards certainty as expiry nears. For example, with a 0.5 s rebuild and the default beta, a request arriving 2 s before expiry has under a 2% chance of triggering a refresh; one arriving 0.1 s before has over an 80% chance.

In code (using 1 − random() so the logarithm never sees zero):

```python
import math, random, time

def should_refresh(expiry, delta, beta=1.0):
    # delta is measured rebuild time (s).
    # -log(rand) is exponential, mean 1
    early = delta * beta * -math.log(
        1.0 - random.random())
    # True starts work; it is not an output.
    return time.time() + early >= expiry
```

With 5,000 requests a second, one of them almost certainly refreshes shortly before expiry, making expiry less likely under load; refresh failure or unlucky sampling can still let it expire. Rarely-read keys almost never refresh early, so you don't waste work on them. `beta > 1` refreshes earlier; `beta < 1` later. The refresh decision needs no lock or coordination, but overlapping refreshes are still possible; it does not guarantee exactly one rebuilder.

## Key takeaways
- Soft expiry permits stale reuse during refresh; hard expiry, eviction or cache loss still produces a miss.
- XFetch increases refresh probability as expiry approaches and as measured rebuild time grows.
- Probabilistic decisions reduce stampede risk without guaranteeing one refresh or preventing every eventual expiry.

## Further reading
- [Optimal Probabilistic Cache Stampede Prevention (VLDB 2015)](https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf)
- [RFC 5861: stale-while-revalidate and stale-if-error](https://www.rfc-editor.org/rfc/rfc5861)
- [Cache stampede — Wikipedia](https://en.wikipedia.org/wiki/Cache_stampede)
