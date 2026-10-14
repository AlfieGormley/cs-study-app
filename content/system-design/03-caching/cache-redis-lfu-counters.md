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

The rule behind these figures comes from the Redis source. Below saturation, each access increments the counter only with this probability:

```formula
P = 1 / (max(C − 5, 0) × F + 1)
where
P: the probability (between 0 and 1) that this access adds 1 to the counter
C: the key's current LFU counter, from 0 to 255; new keys start at 5
5: the starting value Redis gives new keys (LFU_INIT_VAL)
max: the larger of its two inputs, so max(C − 5, 0) is never negative
F: the lfu-log-factor setting, default 10; a bigger F makes the counter climb more slowly
In words: at or below the starting value every access counts; above it, the higher the counter already is, the less likely each access is to raise it.
```

For example, with the default factor of 10:

```formula
P = 1 / (max(C − 5, 0) × F + 1)
C = 5:   P = 1 / (0 × 10 + 1) = 1
C = 15:  P = 1 / (10 × 10 + 1) ≈ 0.01
C = 105: P = 1 / (100 × 10 + 1) ≈ 0.001
where
P: the probability that one access increments the counter
C: the current counter value
max: the larger of its two inputs
F: the lfu-log-factor, here 10
≈: approximately equal to
In words: a new key counts every hit, a key at 15 counts about one hit in a hundred, and a key at 105 about one in a thousand.
```

So the counter climbs quickly at first and then ever more slowly, which is how 8 bits (0 to 255) can stand for about a million hits. It is a rough popularity score, not an exact count. A counter of 255 stays at 255.

Decay works the other way. For a positive decay-time setting, Redis computes a lower score for elapsed idle periods when considering a key. Ordinary accesses store the decayed-and-incremented score and a new timestamp; eviction sampling computes the score without updating that stored timestamp:

```formula
C_new = max(C − ⌊t_idle / D⌋, 0)
where
C_new: the counter after decay
C: the counter before decay
max: the larger of its two inputs, so the counter never goes below 0
⌊ ⌋: floor, rounding down to a whole number
t_idle: the whole minutes since Redis last stamped the key's decay clock, which it does on every access; in minutes (min)
D: the lfu-decay-time setting, in minutes; default 1
min: minutes
In words: with the default setting, a key loses one point of popularity for every minute nobody uses it.
```

For example, a key with counter 200 left idle for 3 hours (180 minutes) decays to 200 − 180 = 20. Setting `lfu-decay-time` to 0 turns decay off and is outside the division formula. The 16-bit minute clock wraps after about 45.5 days, so the simple idle-time model must not be extrapolated to arbitrarily long gaps.

## Key takeaways
- The probability of a counter increment falls as the counter rises, allowing eight bits to summarise many accesses.
- New keys start at five; the counter saturates at 255 and is an approximate popularity score.
- Idle time reduces the score when Redis examines it, allowing an old favourite to lose to a currently popular key.

## Further reading
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis eviction implementation (8.6)](https://raw.githubusercontent.com/redis/redis/8.6/src/evict.c)
