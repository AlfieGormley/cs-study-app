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

Another pattern tackles the miss that happens when a popular key expires. With **refresh-ahead**, the cache reloads an entry *before* it expires, once it has been read close to the end of its life. You choose a **refresh point**, often expressed as a **refresh factor**: a fraction of the TTL. With a 60-second TTL and a factor of 0.8, the refresh point is at 48 seconds.

A read before the refresh point is an ordinary hit. A read after it, but before expiry, still returns the current value immediately and also starts a background reload. Moving the refresh point earlier gives the reload more time to finish but refreshes more often; moving it close to expiry leaves little time for a slow reload.

> [!analogy] Real-world analogy: the office coffee jar
> When the office coffee jar is getting low, whoever makes a cup orders a new bag, but only if people are actually drinking it. Everyone keeps using the old jar until the delivery arrives, and a jar of decaf nobody touches is never reordered.
>
> **How it maps:** The jar is the cached entry, "getting low" is passing the refresh point, and making a cup is a read. That read triggers the reorder (background reload) but is still served from the existing jar. The untouched decaf is a cold key that is allowed to expire.
>
> **Where it stops:** A late delivery leaves an empty jar, just as a slow or failed reload can still let the entry expire and cause a miss. And old coffee is still the coffee you bought, whereas a cached copy can already be out of date compared with the database.

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
