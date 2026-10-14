---
id: cache-refresh-ahead
title: Refresh a hot entry before it expires
level: basic
minutes: 2
summary: Use an entry-age threshold to reload popular values in the background without refreshing every cold key.
sourceLesson: cache-strategies
---

Expiry makes the next reader wait for a reload. Refresh-ahead uses a read near the end of an entry’s lifetime to start that work while the current copy is still available.

## Refresh-ahead

A fifth pattern tackles the miss that happens when a popular key expires. With **refresh-ahead**, the cache reloads an entry *before* it expires, once it has been read close to the end of its life. You choose a **refresh factor**, the fraction of the TTL after which a read triggers a reload:

```formula
t_refresh = f × TTL
t_refresh = 0.8 × 60 s = 48 s
where
t_refresh: the entry's age, in seconds (s), after which a read starts a background reload
f: the refresh factor, a fraction between 0 and 1; here 0.8
TTL: time to live, how long the entry may be served before it expires; here 60 s
s: seconds
In words: with a 60-second TTL and a refresh factor of 0.8, any read after the entry is 48 seconds old triggers a reload.
```

So a read after 48 s returns the current value immediately and triggers a background reload. A lower factor refreshes earlier and more often; a factor close to 1 leaves little time for the reload to finish before expiry.

- Successful timely refreshes hide expiry for hot keys; slow or failed refreshes can still lead to a miss.
- Keys nobody reads near expiry are left to expire, so cold data is not refreshed for nothing.
- If the predictions are poor, you pay for reloads that nobody uses.

Caffeine's `refreshAfterWrite` is an example. The later early-refresh unit shows a probabilistic version that reduces stampede risk.

## Key takeaways
- The refresh factor sets the entry age at which a read starts background work.
- Earlier refreshes provide more time to finish but can perform work nobody uses.
- Only timely successful refreshes hide expiry; cold keys and failed refreshes can still miss.

## Further reading
- [Refresh — Caffeine documentation](https://github.com/ben-manes/caffeine/wiki/Refresh)
- [Caching best practices — AWS](https://aws.amazon.com/caching/best-practices/)
