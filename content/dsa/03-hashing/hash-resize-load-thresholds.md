---
id: hash-resize-load-thresholds
title: Load-factor limits and space trade-offs
level: intermediate
minutes: 3
sourceLesson: hash-resizing
summary: The maximum load factor trades empty slots against collision work, and the right limit depends on how the table resolves collisions.
---

A hash table's speed depends on one ratio: its **load factor**, the number of stored keys divided by the number of buckets. Keep it low and buckets are mostly empty or hold a single key, so operations are fast. Let it creep up and chains lengthen or probe runs grow.

Many dynamically growing tables therefore watch the load factor and, when it passes a **maximum load factor**, allocate a bigger array and move everything across. This lesson is about choosing that limit; the following lessons cover the move itself. The key point: a useful limit depends on how the table resolves collisions, so a chaining table and a probing table need not share the same threshold.

## Choosing the maximum load factor

The threshold is a space–time trade-off. A low maximum wastes memory on empty slots; a high one makes operations slower.

| Table | Typical/default growth policy | Scheme |
|---|---|---|
| Java `HashMap` | 0.75 | chaining |
| CPython `dict` | about 2/3 | open addressing |
| Abseil Swiss table | 7/8 | open addressing + SIMD |
| Redis dict | normally grows near 1; policy can defer growth | chaining |

Chaining tolerates a higher load factor because a slightly longer chain is a mild slowdown: cost grows in a straight line with load. Open addressing is far more sensitive. In Knuth's model for linear probing (Linear probing and clustering), the expected cost of a miss depends on one over the *square* of the free fraction of slots. Going from 3/4 full to 7/8 full halves the free fraction, so it roughly quadruples the expected miss cost: from about 8.5 probes to about 32.5.

That model assumes random hashing, plain linear probing and no deletions; it is not the formula for every probing design. Swiss tables can run at 7/8 full because they probe whole groups of slots at once, comparing one-byte metadata entries first, so few probes ever touch the slots themselves.

In Java, the default maximum load factor of 0.75 with 16 buckets gives a threshold of 12 entries. Ordinary `put` grows the table only once the size goes *above* that threshold, so the 13th new key triggers the first doubling.

## Key takeaways
- Growth limits trade empty capacity against collision work.
- Chaining, linear probing and group probing need different cost models.
- Java’s ordinary size-triggered growth occurs after exceeding its threshold.

## Further reading
- [Hash table: dynamic resizing — Wikipedia](https://en.wikipedia.org/wiki/Hash_table#Dynamic_resizing)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
