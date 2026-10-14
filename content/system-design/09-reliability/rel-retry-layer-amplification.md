---
id: rel-retry-layer-amplification
title: Retry amplification across service layers
level: intermediate
minutes: 3
summary: Calculate worst-case and expected retry load and choose one retry layer.
sourceLesson: rel-timeouts-retries
---

Backoff and jitter spread work over time. They do not remove the multiplication caused by nested retry loops. Keep total attempts distinct from retries: three attempts means one initial attempt and two retries.

## Retry amplification across layers

This is where retries cause outages. Suppose a request passes through three layers and each layer makes **up to 3 attempts** (1 try + 2 retries):

```
Client  ──3x──▶ API
API     ──3x──▶ Service
Service ──3x──▶ Database
```

If the database is completely down, one user request produces:

- 3 attempts at the API
- 3 × 3 = 9 at the service
- 3 × 3 × 3 = **27** at the database

Each retrying layer multiplies the attempts of the layer above it:

```formula
M = n^L
M = 3^3 = 3 × 3 × 3 = 27
M = 3^5 = 243
where
M: the attempts reaching the bottom dependency for one user request (the amplification factor)
n: the maximum attempts each layer makes (1 try + retries), here 3
L: the number of layers (hops) that retry, here 3 (or 5)
^: "to the power of"
In words: three retrying layers of three attempts turn one request into 27 at the database; five layers turn it into 243.
```

This is the worst case, when every attempt fails. The database, which was perhaps just overloaded, now receives 27 times its normal traffic and has no chance to recover. This is a **retry storm**.

Partial failure amplifies too, just less dramatically. Take a single retrying layer making up to 3 tries. The first try always happens; the second happens only if the first fails; the third only if the first two fail:

```formula
E = 1 + p + p^2
E = 1 + 0.5 + 0.5^2
E = 1 + 0.5 + 0.25 = 1.75
where
E: the expected (average) number of attempts per request
p: the probability that any one attempt fails, from 0 to 1, assumed independent and unchanged between attempts; here 0.5 (50%)
p^2: p squared, the chance the first two attempts both fail
In words: when half of attempts fail, each request makes 1.75 attempts on average, so the dependency sees 75% extra load.
```

The same formula gives the rest of the table:

| Failure rate p | Attempts per request |
|---|---|
| 10% | 1.11× |
| 50% | 1.75× |
| 90% | 2.71× |
| 100% | 3× |

The extra load arrives exactly as the dependency gets worse, which is a positive feedback loop: more failures cause more retries, which cause more failures.

### Fixes for amplification

1. **Retry at one layer only.** AWS's Well-Architected guidance is to implement retries at only one level of the stack. Usually that's the layer immediately above the failing dependency; every other layer fails fast and passes the error up.
2. **Retry budgets.** Cap retries as a fraction of total traffic.
3. **Propagate "don't retry" signals.** If a downstream is overloaded, return an error that tells upstream callers not to retry it. Google uses an explicit "overloaded; don't retry" response, so callers receiving that signal suppress retries.

## Key takeaways

- Worst-case attempts multiply across retrying layers.
- Expected attempts for three tries depend on the failure probability remaining independent and unchanged.
- Choose one retrying layer, propagate overload signals and bound retry traffic; jitter alone changes timing.

## Further reading

- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [Limit retries (AWS Well-Architected)](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_limit_retries.html)
