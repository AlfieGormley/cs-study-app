---
id: cache-redis-lfu-counters
title: Calculate Redis LFU increments and decay
level: intermediate
minutes: 4
summary: Use Redis’s sampled logarithmic counters to estimate popularity without interpreting them as exact hit counts.
sourceLesson: cache-eviction
---

Redis’s LFU mode keeps an 8-bit counter and a 16-bit decay timestamp in the 24-bit access field introduced in the preceding unit. It samples eviction candidates rather than ordering every key by exact frequency.

The **LFU** mode (since Redis 4.0) uses a probabilistic **logarithmic counter** in 8 bits. Each access increments it with a probability that falls as the counter grows, so 255 can represent around a million hits (tuned by `lfu-log-factor`, default 10). Elapsed decay is applied lazily when an object is accessed or considered for eviction (one per lfu-decay-time minute by default), rather than actively decrementing every idle key. New keys start at 5 rather than 0, giving them a chance to establish popularity; they can still be evicted immediately.

To get a feel for the log counter, the Redis config file gives these figures for the default factor of 10:

| Hits | Counter |
|---|---|
| 100 | ~10 |
| 1,000 | ~18 |
| 100,000 | ~142 |
| 1,000,000 | 255 |

The rule behind these figures comes from the Redis source. Each access adds 1 to the counter only with some probability, and that probability shrinks as the counter grows:

```formula reference
P = 1 / (max(C − 5, 0) × F + 1)
where
P: the probability (between 0 and 1) that this access adds 1 to the counter
C: the key's current LFU counter, from 0 to 255; new keys start at 5
5: the starting value Redis gives new keys (LFU_INIT_VAL)
max: the larger of its two inputs, so max(C − 5, 0) is never negative
F: the lfu-log-factor setting, default 10; a bigger F makes the counter climb more slowly
In words: at or below the starting value of 5 every access counts; above it, the higher the counter already is, the less likely each access is to raise it. With the default factor, a key at 15 counts about one access in a hundred, and a key at 105 about one in a thousand.
```

So the counter climbs quickly at first and then ever more slowly, which is how 8 bits (0 to 255) can stand for about a million hits. It is a rough popularity score, not an exact count. A counter of 255 stays at 255.

**Decay** works the other way. With the default `lfu-decay-time` of 1, a key loses one point for every whole minute since Redis last stamped its decay clock (it stamps it on every access), never going below zero. A key that reached 200 during a sale and then sat idle for three hours is scored at about 20 when Redis next looks at it, so a currently busy key with a counter of 30 now outranks it. A larger `lfu-decay-time` makes popularity fade more slowly; 0 turns decay off.

Decay is applied lazily, not by a background sweep. When a key is accessed, Redis stores the decayed-and-incremented score with a new timestamp. When a key is merely sampled as an eviction candidate, Redis computes the decayed score for the comparison without updating the stored timestamp. The decay clock is a 16-bit count of minutes, so it wraps after about 45.5 days; do not stretch the simple "one point per idle minute" model to arbitrarily long gaps.

## Key takeaways
- The probability of a counter increment falls as the counter rises, allowing eight bits to summarise many accesses.
- New keys start at five; the counter saturates at 255 and is an approximate popularity score.
- Idle time reduces the score when Redis examines it, allowing an old favourite to lose to a currently popular key.

## Further reading
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis eviction implementation (8.6)](https://raw.githubusercontent.com/redis/redis/8.6/src/evict.c)
