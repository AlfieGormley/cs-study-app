---
id: hash-resize-load-thresholds
title: Load-factor limits and space trade-offs
level: intermediate
minutes: 3
sourceLesson: hash-resizing
summary: Load factor describes fullness, but a useful growth limit depends on collision resolution.
---

Load factor describes fullness, but a useful growth limit depends on collision resolution. A chaining table and a group-probing table need not share the same threshold.

A hash table's speed depends on one ratio: how full it is. The **load factor** is

```formula
α = n / m
α = 12 / 16 = 0.75
where
α: alpha, the load factor: keys per bucket, a plain number with no unit
n: the number of keys stored, here 12
m: the number of buckets (slots) in the array, here 16
In words: divide the number of keys by the number of buckets; 12 keys in 16 buckets is a load factor of 0.75, the default maximum load ratio for Java's HashMap; ordinary put grows only after the threshold is exceeded.
```

Keep α low and buckets are mostly empty or hold a single key, so operations are fast. Let α creep up and chains lengthen or probe runs grow. Many dynamically growing tables therefore watch α and, when it passes a **maximum load factor**, allocate a bigger array and move everything across. This lesson is about that move: what it costs, why it is still cheap on average, and how two widely used implementations do it.



## Choosing the maximum load factor

The threshold is a space–time trade-off. A low maximum wastes memory on empty slots; a high one makes operations slower.

| Table | Typical/default growth policy | Scheme |
|---|---|---|
| Java `HashMap` | 0.75 | chaining |
| CPython `dict` | about 2/3 | open addressing |
| Abseil Swiss table | 7/8 | open addressing + SIMD |
| Redis dict | normally grows near 1; policy can defer growth | chaining |

Chaining tolerates a higher load factor because a slightly longer chain is a mild slowdown. Open addressing is far more sensitive. Knuth's classical estimate for a linear-probing miss (Collision resolution) shows why:

```formula
P_miss ≈ ½ × (1 + 1 / (1 − α)^2)
α = 0.75:  P_miss ≈ ½ × (1 + 16) = 8.5
α = 0.875: P_miss ≈ ½ × (1 + 64) = 32.5
where
P_miss: the expected number of slots examined by an unsuccessful lookup in a linear-probing table
α: alpha, the load factor, the fraction of slots occupied; 0.875 is 7/8
½: one half
^: "to the power of"; (1 − α)^2 means (1 − α) × (1 − α)
≈: approximately equal to
In words: as the free fraction 1 − α shrinks, a miss costs about one over its square; going from 3/4 full to 7/8 full nearly quadruples the expected miss cost.
```

The formula assumes random hashing, plain linear probing and no deletions; it is not the formula for every probing design. Swiss tables can run at 7/8 full because they probe whole groups of slots at once, comparing one-byte metadata entries first, so few probes ever touch the slots themselves.

## Key takeaways
- Growth limits trade empty capacity against collision work.
- Chaining, linear probing and group probing need different cost models.
- Java’s ordinary size-triggered growth occurs after exceeding its threshold.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
