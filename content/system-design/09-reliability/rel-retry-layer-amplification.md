---
id: rel-retry-layer-amplification
title: Retry amplification across service layers
level: intermediate
minutes: 3
summary: Explain how nested retry loops amplify load and choose one retry layer.
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
- Up to 9 at the service
- Up to **27** at the database

Each retrying layer multiplies the attempts of the layer above it. Adding another retrying layer multiplies the database load again.

This is the worst case, when every attempt fails. The database, which was perhaps just overloaded, now receives 27 times its normal traffic and has no chance to recover. This is a **retry storm**.

Even one retrying layer adds traffic during partial failure: some original calls retry, and some retries fail and retry again. A per-request cap alone does not bound retries to a small fraction of original traffic.

The extra load arrives exactly as the dependency gets worse, which is a positive feedback loop: more failures cause more retries, which cause more failures.

### Fixes for amplification

1. **Retry at one layer only.** AWS's Well-Architected guidance is to implement retries at only one level of the stack. Usually that's the layer immediately above the failing dependency; every other layer fails fast and passes the error up.
2. **Retry budgets.** Cap retries as a fraction of total traffic.
3. **Propagate "don't retry" signals.** If a downstream is overloaded, return an error that tells upstream callers not to retry it. Google uses an explicit "overloaded; don't retry" response, so callers receiving that signal suppress retries.

## Key takeaways

- Worst-case attempts multiply across retrying layers.
- Even one retrying layer adds load during partial failure; a traffic budget limits that extra work.
- Choose one retrying layer, propagate overload signals and bound retry traffic; jitter alone changes timing.

## Further reading

- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Addressing cascading failures (Google SRE book)](https://sre.google/sre-book/addressing-cascading-failures/)
- [Limit retries (AWS Well-Architected)](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_limit_retries.html)
